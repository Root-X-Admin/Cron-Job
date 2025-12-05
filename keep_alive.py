import os
import sys
import requests

URL = os.getenv("KEEPALIVE_URL", "https://trackitall-t3x6.onrender.com/")
TIMEOUT = int(os.getenv("TIMEOUT", "10"))

def main():
    try:
        resp = requests.get(URL, timeout=TIMEOUT)
        print(f"[keep-alive] Ping {URL} -> {resp.status_code}")
        # Non-200 is still a successful *request* from Render's POV, so we return 0
        return 0
    except Exception as e:
        print(f"[keep-alive] Ping failed: {e}", file=sys.stderr)
        # Non-zero exit so cron logs it as error
        return 1

if __name__ == "__main__":
    sys.exit(main())
