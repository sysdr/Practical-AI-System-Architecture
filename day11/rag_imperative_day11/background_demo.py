#!/usr/bin/env python3
"""Updates metrics so the dashboard shows non-zero values."""
import os
import json
import time
import signal
from datetime import datetime as dt

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_questions_asked": 0, "total_responses": 0, "last_activity": None, "questions": []}

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
    print("Background demo: updating metrics. Open http://localhost:5000")
    print("Press Ctrl+C to stop")
    count = 0
    while running:
        count += 1
        metrics = load_metrics()
        metrics["total_questions_asked"] = metrics.get("total_questions_asked", 0) + 1
        metrics["total_responses"] = metrics.get("total_responses", 0) + 1
        metrics["last_activity"] = dt.now().isoformat()
        metrics.setdefault("questions", []).append({"timestamp": metrics["last_activity"], "question_preview": "demo", "response_preview": "demo reply"})
        if len(metrics["questions"]) > 100:
            metrics["questions"] = metrics["questions"][-100:]
        save_metrics(metrics)
        print(f"[{time.strftime('%H:%M:%S')}] Updated metrics (#{count})")
        time.sleep(interval)
    print("Demo stopped.")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=5)
    main(p.parse_args().interval)
