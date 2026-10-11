import os
import requests
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("API_KEY")
if not api_key:
    print("Please set your API_KEY in the .env file first.")
    exit(1)

headers = {"X-API-Key": api_key}
print("Fetching models from Backboard...")

try:
    models = requests.get(
        "https://app.backboard.io/api/models",
        headers=headers,
        params={"model_type": "llm", "limit": 200},
        timeout=10
    ).json()

    print("\n--- Available Open-Weight Models ---")
    
    found = False
    for m in models.get("models", []):
        name_lower = m['name'].lower()
        if any(kw in name_lower for kw in ["gemma", "qwen", "llama", "mistral", "mixtral"]):
            print(f"PROVIDER={m['provider']}")
            print(f"MODEL={m['name']}")
            print("-" * 40)
            found = True
            
    if not found:
        print("No open-weight models matching 'gemma', 'qwen', 'llama', or 'mistral' were found.")
        print("You can see all models on https://app.backboard.io/dashboard/model-library")

except Exception as e:
    print(f"Error fetching models: {e}")
