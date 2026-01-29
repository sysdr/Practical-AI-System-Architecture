#!/usr/bin/env python3
"""Updates metrics so the dashboard shows non-zero values (no real API required)."""
import os
import json
import time
import signal

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_messages_sent": 0, "total_messages_received": 0, "total_conversations": 0, "last_activity": None, "messages": []}

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

running = True
def handler(sig, frame):
    global running
    running = False
signal.signal(signal.SIGINT, handler)
signal.signal(signal.SIGTERM, handler)

def main(interval=5):
    from datetime import datetime as dt
    print("Background demo: updating metrics for dashboard (no API required). Open http://localhost:5000")
    print("Press Ctrl+C to stop")
    count = 0
    while running:
        count += 1
        metrics = load_metrics()
        metrics["total_messages_sent"] = metrics.get("total_messages_sent", 0) + 1
        metrics["total_messages_received"] = metrics.get("total_messages_received", 0) + 1
        metrics["last_activity"] = dt.now().isoformat()
        metrics.setdefault("messages", []).append({"timestamp": metrics["last_activity"], "user": "demo", "bot_preview": "demo reply"})
        if len(metrics["messages"]) > 100:
            metrics["messages"] = metrics["messages"][-100:]
        save_metrics(metrics)
        print(f"[{time.strftime('%H:%M:%S')}] Updated metrics (#{count})")
        time.sleep(interval)
    print("Demo stopped.")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=5)
    main(p.parse_args().interval)
