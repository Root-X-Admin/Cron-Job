import os
import threading
import time
import requests
from flask import Flask, jsonify

# Target URL to keep alive
TARGET_URL = os.getenv(
    "KEEPALIVE_URL",
    "https://trackitall-t3x6.onrender.com/",
)

# How often to ping (in seconds)
PING_INTERVAL_SECONDS = int(os.getenv("PING_INTERVAL_SECONDS", "600"))  # 10 minutes
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

app = Flask(__name__)


def ping_loop():
    """Background loop that pings TARGET_URL forever."""
    while True:
        try:
            resp = requests.get(TARGET_URL, timeout=TIMEOUT)
            print(f"[keep-alive] Ping {TARGET_URL} -> {resp.status_code}", flush=True)
        except Exception as e:
            print(f"[keep-alive] Error pinging {TARGET_URL}: {e}", flush=True)

        time.sleep(PING_INTERVAL_SECONDS)


@app.route("/")
def index():
    """Simple health endpoint so Render sees this as a web service."""
    return jsonify(
        {
            "status": "ok",
            "target": TARGET_URL,
            "interval_seconds": PING_INTERVAL_SECONDS,
        }
    )


def start_background_thread():
    t = threading.Thread(target=ping_loop, daemon=True)
    t.start()


# Start background thread as soon as app is imported
start_background_thread()

if __name__ == "__main__":
    # For local testing only: python app.py
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
