# Playground Game Maker

A lightweight web application that helps friends and kids play outside by generating creative outdoor games based on available items, play space, and duration. It enforces strict outdoor safety guidelines and features a screen-lock countdown timer to encourage players to "touch grass".

Built with **Antigravity** and **Google Stitch**.

## How to Run

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt # or: pip install flask python-dotenv requests tinker
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
   - `BASE_URL`
   - `MOCK_MODEL`

4. **Start the Server**:
   ```bash
   python app.py
   ```
   Open the displayed URL (e.g. `http://127.0.0.1:5000` or local Wi-Fi IP on mobile) in your browser.

## Safety & Local Privacy

This application is designed for trusted local networks with no external telemetry, logins, or trackers. All game histories and play logs are stored locally in SQLite.
