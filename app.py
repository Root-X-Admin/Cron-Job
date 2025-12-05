import os
import threading
import time
import requests
from datetime import datetime, timedelta, timezone
from flask import Flask, jsonify

# Timezone: India Standard Time (UTC+05:30)
IST = timezone(timedelta(hours=5, minutes=30))

# Load URLs from environment variables
WEBSITE1 = os.getenv("WEBSITE1")  # active only 6:00–24:00 IST
WEBSITE2 = os.getenv("WEBSITE2")  # active 24x7

# How often to ping (seconds)
PING_INTERVAL_SECONDS = int(os.getenv("PING_INTERVAL_SECONDS", "600"))  # default: 10 mins
TIMEOUT = int(os.getenv("TIMEOUT", "10"))  # request timeout in seconds

app = Flask(__name__)


def is_website1_active(now_ist: datetime | None = None) -> bool:
    """
    WEBSITE1 should be pinged only between 06:00 and 24:00 IST.

    - Active window: 06:00:00 <= time < 24:00:00 (midnight)
    """
    if now_ist is None:
        now_ist = datetime.now(IST)

    hour = now_ist.hour
    # From 6:00 (hour=6) up to 23:59 (hour=23)
    return 6 <= hour < 24


def ping(url: str):
    """Ping a single URL and log the result."""
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        print(f"[keep-alive] Ping {url} -> {resp.status_code}", flush=True)
    except Exception as e:
        print(f"[keep-alive] Error pinging {url}: {e}", flush=True)


def ping_loop():
    """Background loop that pings WEBSITE1 (time-limited) and WEBSITE2 (24x7)."""
    while True:
        now_ist = datetime.now(IST)

        # WEBSITE1: only between 06:00 and 24:00 IST
        if WEBSITE1:
            if is_website1_active(now_ist):
                ping(WEBSITE1)
            else:
                print(
                    f"[keep-alive] Skipping WEBSITE1 (outside 06:00–24:00 IST). "
                    f"Current IST time: {now_ist.isoformat()}",
                    flush=True,
                )

        # WEBSITE2: always ping if set
        if WEBSITE2:
            ping(WEBSITE2)

        time.sleep(PING_INTERVAL_SECONDS)


@app.route("/")
def index():
    """Health endpoint for Render."""
    now_ist = datetime.now(IST)

    return jsonify(
        {
            "status": "ok",
            "targets": {
                "website1": WEBSITE1,
                "website2": WEBSITE2,
            },
            "website1_active_now": is_website1_active(now_ist),
            "interval_seconds": PING_INTERVAL_SECONDS,
            "current_time_ist": now_ist.isoformat(),
            "note": "website1: 06:00–24:00 IST, website2: 24x7",
        }
    )


def start_background_thread():
    t = threading.Thread(target=ping_loop, daemon=True)
    t.start()


# Start thread when Flask app loads
start_background_thread()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))
