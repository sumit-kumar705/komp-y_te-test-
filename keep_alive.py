"""
Keep-Alive Service
This script pings your deployed application to prevent it from sleeping.
Run this on your local machine or use a cron job service.
"""

import requests
import time
from datetime import datetime

# Replace with your actual Railway deployment URL
# Find it in Railway Dashboard -> Your Service -> Settings -> Domains
DEPLOYMENT_URL = "https://your-app-name.up.railway.app"  # Railway format

# Ping interval in seconds (13 minutes = 780 seconds)
# Railway free tier sleeps after ~15 minutes of inactivity
PING_INTERVAL = 780


def ping_app():
    """Ping the application to keep it awake"""
    try:
        response = requests.get(f"{DEPLOYMENT_URL}/", timeout=30)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if response.status_code == 200:
            print(f"[{timestamp}] ✓ App is alive! Status: {response.status_code}")
        else:
            print(f"[{timestamp}] ⚠ App responded with status: {response.status_code}")

        return True
    except requests.exceptions.Timeout:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ⏱ Timeout - App is waking up...")
        return False
    except Exception as e:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] ✗ Error: {str(e)}")
        return False


if __name__ == "__main__":
    print("=" * 60)
    print("🔄 Keep-Alive Service Started")
    print(f"🎯 Target URL: {DEPLOYMENT_URL}")
    print(f"⏰ Ping interval: {PING_INTERVAL} seconds ({PING_INTERVAL//60} minutes)")
    print("=" * 60)

    # Initial ping
    ping_app()

    # Keep pinging
    while True:
        time.sleep(PING_INTERVAL)
        ping_app()
