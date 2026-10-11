# Playground Game Maker

A lightweight web application that helps friends and kids play outside by generating creative outdoor games based on available items, play space, and duration. It enforces strict outdoor safety guidelines and features a screen-lock countdown timer to encourage players to "touch grass".

Built with **Antigravity** and **Google Stitch**.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**:
   Copy `.env.example` to `.env` and fill in your settings:
   ```bash
   cp .env.example .env
   ```

3. **Environment Variables**:
   The application uses the following environment variables (configured in `.env`):
   - `PROVIDER`
   - `MODEL`
   - `API_KEY`
   - `MOCK_MODEL`
   - `DEMO_MODE`
   - `DEMO_TOKEN`

4. **Start the Server**:
   ```bash
   python app.py
   ```
   Open the displayed URL (e.g. `http://127.0.0.1:5000` or local Wi-Fi IP on mobile) in your browser.

## Deploy

The application can be deployed as a public demo on Render using the included `render.yaml` (free web service tier with Gunicorn):

- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `gunicorn app:app --workers 1 --threads 4 --timeout 180 --bind 0.0.0.0:$PORT`
- **Demo Mode & Limits**: When `DEMO_MODE=1` is set, games are rate-limited to **5 games per IP per hour** and **100 games per day in total** to protect credits. Stats saving to database is disabled online.
- **Token Gate**: Setting `DEMO_TOKEN` requires visitors to access the demo via `?token=YOUR_TOKEN` (remembered via cookie after the first visit).

## Safety & Local Privacy

In local mode, all game histories and play logs are stored locally in SQLite with no external telemetry, logins, or trackers.
