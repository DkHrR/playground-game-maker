import os
import json
import sqlite3
import shutil
import socket
from flask import Flask, render_template, request, jsonify, Response
from dotenv import load_dotenv
import requests

import tinker
from tinker.types import SamplingParams
from tinker_cookbook import renderers, tokenizer_utils

_tinker_service = None
_tinker_sampling_client = None
_tinker_renderer = None

def get_tinker_clients(model_name, api_key):
    global _tinker_service, _tinker_sampling_client, _tinker_renderer
    if _tinker_sampling_client is None:
        import os
        os.environ["TINKER_API_KEY"] = api_key
        _tinker_service = tinker.ServiceClient()
        _tinker_sampling_client = _tinker_service.create_sampling_client(base_model=model_name)
        _tokenizer = tokenizer_utils.get_tokenizer(model_name)
        _tinker_renderer = renderers.get_renderer("qwen3_5", _tokenizer)
    return _tinker_sampling_client, _tinker_renderer

load_dotenv()
app = Flask(__name__)
DB_FILE = 'data.sqlite'

def get_db():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    migration_needed = False
    
    if os.path.exists(DB_FILE):
        conn = sqlite3.connect(DB_FILE)
        c = conn.cursor()
        c.execute("PRAGMA table_info(games)")
        columns = [row[1] for row in c.fetchall()]
        if len(columns) > 0 and "source" not in columns:
            migration_needed = True
        conn.close()

    if migration_needed and os.path.exists(DB_FILE):
        backup_file = DB_FILE + ".backup"
        if not os.path.exists(backup_file):
            shutil.copy2(DB_FILE, backup_file)
            print(f"Backed up {DB_FILE} to {backup_file}")
            
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            screen_seconds INTEGER,
            outside_minutes INTEGER,
            rating INTEGER,
            notes TEXT
        )
    """)
    if migration_needed:
        c.execute("ALTER TABLE games ADD COLUMN source TEXT")
    
    # Just in case table was created for first time above, or we didn't migrate
    c.execute("PRAGMA table_info(games)")
    columns = [row[1] for row in c.fetchall()]
    if len(columns) > 0 and "source" not in columns:
        c.execute("ALTER TABLE games ADD COLUMN source TEXT")

    conn.commit()
    conn.close()

MOCK_RESPONSE = {
    "name": "Ghost Tag",
    "setup": "One person is the ghost, everyone else hides.",
    "rules": [
        "The ghost counts to 30 with eyes closed.",
        "Players hide within the chosen space.",
        "The ghost tries to tag the players.",
        "Tagged players become ghosts too."
    ],
    "how_to_win": "Last person who isn't a ghost wins.",
    "safety_note": "Stay within the boundaries, no running on roads. Tell an adult where you are playing.",
    "minutes": 15
}

def extract_json(content):
    start = content.find('{')
    end = content.rfind('}')
    if start != -1 and end != -1 and end > start:
        return json.loads(content[start:end+1])
    raise ValueError("No JSON object found in response")

def call_ai_provider(prompt, retries=1):
    mock = os.getenv("MOCK_MODEL", "0")
    if mock == "1" or not os.getenv("MODEL"):
        return MOCK_RESPONSE, "mock"

    base_url = os.getenv("BASE_URL", "https://app.backboard.io/api")
    api_key = os.getenv("API_KEY", "")
    provider = os.getenv("PROVIDER", "")
    model = os.getenv("MODEL", "")

    if not api_key or not provider or not model:
        raise ValueError("Missing API_KEY, PROVIDER, or MODEL in .env for real AI generation.")

    headers = {
        "X-API-Key": api_key,
        "Content-Type": "application/json"
    }

    system_message = """You are a playground game inventor. Create a new game.
Reply ONLY with valid JSON in this exact format, with no extra text or markdown:
{"name": "str", "setup": "str", "rules": ["str" (max 6)], "how_to_win": "str", "safety_note": "str", "minutes": 15}

Safety rules: no roads or traffic, no heights, no water, no fire, nothing sharp, no rough contact. Use EXCLUSIVELY the items the players listed. DO NOT INVENT any items (no buckets, no flags, no leaves, etc). If no items are listed, use NO items at all. Remind them to tell a parent or adult where they are. If an item is unsafe, swap it for a safe one and explain the swap in the safety_note."""

    payload = {
        "content": system_message + "\n\nUser request: " + prompt,
        "llm_provider": provider,
        "model_name": model,
        "stream": False
    }

    

    
    if provider.lower() == "tinker":
        try:
            sampling_client, renderer = get_tinker_clients(model, api_key)
            messages = [{"role": "system", "content": system_message}, {"role": "user", "content": prompt}]
            prompt_tokens = renderer.build_generation_prompt(messages)
            stop_sequences = renderer.get_stop_sequences()
            sampling_params = SamplingParams(max_tokens=1000, temperature=0.5, stop=stop_sequences)
            
            for attempt in range(retries + 1):
                try:
                    output = sampling_client.sample(prompt_tokens, sampling_params=sampling_params, num_samples=1).result()
                    sampled_message, _ = renderer.parse_response(output.sequences[0].tokens)
                    if isinstance(sampled_message, dict):
                        c = sampled_message.get("content")
                        if isinstance(c, list):
                            # It's a thinking model output
                            text_parts = [p.get("text", "") for p in c if p.get("type") == "text"]
                            content = "".join(text_parts)
                        else:
                            content = str(c)
                    else:
                        content = str(sampled_message)
                    
                    parsed = extract_json(content)
                    required_keys = {"name", "setup", "rules", "how_to_win", "safety_note", "minutes"}
                    if not required_keys.issubset(parsed.keys()):
                        raise ValueError("Missing required keys in JSON")
                    return parsed, model
                except Exception as e:
                    print(f"Attempt {attempt+1} failed: {e}")
                    if attempt == retries:
                        raise RuntimeError(f"Provider error: {e}")
        except Exception as e:
            raise RuntimeError(f"Provider error: {e}")

    for attempt in range(retries + 1):
        try:
            resp = requests.post(
                base_url.rstrip("/") + "/threads/messages", 
                headers=headers, 
                json=payload, 
                timeout=120
            )
            resp.raise_for_status()
            data = resp.json()
            
            # The API might wrap the text in 'content' or 'message.content'
            content = data.get("content")
            if not content and "message" in data:
                content = data["message"].get("content")
            if not content:
                content = str(data)

            parsed = extract_json(content)
            
            required_keys = {"name", "setup", "rules", "how_to_win", "safety_note", "minutes"}
            if not required_keys.issubset(parsed.keys()):
                raise ValueError("Missing required keys in JSON")
            
            return parsed, model
        except Exception as e:
            print(f"Attempt {attempt+1} failed: {e}")
            if attempt == retries:
                raise RuntimeError(f"Failed to generate game: {e}")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/generate', methods=['POST'])
def generate():
    data = request.json
    from shared_lists import UNSAFE_ITEMS, UNSAFE_OUTPUT, COMMON_ITEMS
    import re
    
    raw_items = data.get('items', '')
    safe_items = []
    removed_items = []
    
    # Split only on commas and newlines
    split_items = [x.strip() for x in re.split(r'[,\n]+', raw_items) if x.strip()]
    
    for item in split_items:
        is_unsafe = False
        for bad in UNSAFE_ITEMS:
            if re.search(r'\b' + re.escape(bad) + r's?\b', item.lower()):
                is_unsafe = True
                break
        if is_unsafe:
            removed_items.append(item)
        else:
            safe_items.append(item)
            
    safe_items_str = ", ".join(safe_items) if safe_items else "none"
    
    prompt = f"Players: {data.get('players')}, Age range: {data.get('age')}, Items: {safe_items_str}, Space: {data.get('space')}, Minutes: {data.get('minutes')}."
    
    try:
        import time
        start_time = time.time()
        print('generate started')
        final_game = None
        final_source = None
        has_unsafe = False
        invented_item_found = None
        
        for attempt in range(2):
            print(f'generate attempt {attempt+1}')
            game, source = call_ai_provider(prompt)
            game_text = (game.get("setup", "") + " " + " ".join(game.get("rules", []))).lower()
            
            has_unsafe = False
            for bad in UNSAFE_OUTPUT:
                if re.search(r'\b' + re.escape(bad) + r's?\b', game_text):
                    has_unsafe = True
                    break
                    
            invented_item_found = None
            for ci in COMMON_ITEMS:
                # check if common item is in game_text
                if re.search(r'\b' + re.escape(ci) + r's?\b', game_text):
                    # Check if it was in the safe listed items
                    if not re.search(r'\b' + re.escape(ci) + r's?\b', safe_items_str.lower()):
                        invented_item_found = ci
                        break
                        
            final_game = game
            final_source = source
            
            if not has_unsafe and not invented_item_found:
                break
                
        if has_unsafe:
            return jsonify({"success": False, "error": "Model failed to follow safety constraints after 2 attempts."})
            
        if invented_item_found:
            invented_str = f"Uses an item you didn't list: {invented_item_found}. "
            final_game["safety_note"] = invented_str + final_game.get("safety_note", "")
            
        if removed_items:
            removed_str = "Removed unsafe item: " + ", ".join(removed_items) + ". "
            final_game["safety_note"] = removed_str + final_game.get("safety_note", "")
            
        if "Tell a parent or adult where you are playing." not in final_game.get("safety_note", ""):
            final_game["safety_note"] = (final_game.get("safety_note", "") + " Tell a parent or adult where you are playing.").strip()
            
        game = final_game
        source = final_source


        print(f"generate done in {int(time.time() - start_time)}s")
        return jsonify({"success": True, "game": game, "source": source})
    except Exception as e:
        print(f"generate error: {str(e)}")
        return jsonify({"success": False, "error": str(e)})

@app.route('/api/save_stats', methods=['POST'])
def save_stats():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute('''
        INSERT INTO games (name, screen_seconds, outside_minutes, rating, notes, source)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (data.get('name'), data.get('screen_seconds'), data.get('outside_minutes'), data.get('rating'), data.get('notes'), data.get('source')))
    conn.commit()
    conn.close()
    return jsonify({"success": True})

@app.route('/stats')
def stats():
    conn = get_db()
    games = conn.execute("SELECT * FROM games ORDER BY id DESC").fetchall()
    conn.close()
    
    real_games = [g for g in games if g['source'] != 'mock']
    total_real = len(real_games)
    total_screen = sum(g['screen_seconds'] for g in real_games) if real_games else 0
    total_outside = sum(g['outside_minutes'] for g in real_games) if real_games else 0
    avg_rating = sum(g['rating'] for g in real_games) / total_real if total_real > 0 else 0
    
    return render_template('stats.html', real_games=real_games, sample_games=[g for g in games if g['source'] == 'mock'], games=games, 
                           games_count=total_real, 
                           total_screen=total_screen, 
                           total_outside=total_outside, 
                           avg_rating=round(avg_rating, 1))

@app.route('/stats/csv')
def stats_csv():
    conn = get_db()
    games = conn.execute("SELECT * FROM games ORDER BY id ASC").fetchall()
    conn.close()
    
    def generate():
        yield 'id,name,screen_seconds,outside_minutes,rating,notes,source\n'
        for g in games:
            notes = str(g['notes']).replace('"', '""') if g['notes'] else ''
            source = str(g['source']) if g['source'] else 'unknown'
            yield f"{g['id']},\"{g['name']}\",{g['screen_seconds']},{g['outside_minutes']},{g['rating']},\"{notes}\",\"{source}\"\n"
            
    return Response(generate(), mimetype='text/csv', headers={"Content-Disposition": "attachment; filename=stats.csv"})

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

if __name__ == '__main__':
    # Warm up Tinker client on startup
    if os.getenv("PROVIDER", "").lower() == "tinker":
        try:
            get_tinker_clients(os.getenv("MODEL", ""), os.getenv("API_KEY", ""))
            print("Tinker client warmed up.")
        except Exception as e:
            print("Failed to warm up Tinker client:", e)

    init_db()
    ip = get_ip()
    print("=========================================")
    print(f"PLAYGROUND GAME MAKER is starting!")
    print(f"Open this address on your phone (same Wi-Fi): http://{ip}:5000")
    print("=========================================")
    app.run(host="0.0.0.0", port=5000, debug=True)




