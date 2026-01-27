#!/usr/bin/env python3
"""
Background demo script that continuously runs article processing.
This ensures the dashboard shows real-time changing data.
"""
import os
import sys
import time
import random
import signal
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

# Try to import main, but handle if API key is not set
try:
    import main
    HAS_API_KEY = True
except ValueError as e:
    if "OPENAI_API_KEY" in str(e):
        HAS_API_KEY = False
        print("⚠️  OPENAI_API_KEY not set. Running in test mode with simulated metrics.")
    else:
        raise

running = True

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global running
    print("\n🛑 Stopping background demo...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def update_metrics_test_mode(latency_ms, success=True, step1=False, step2=False, step3=False):
    """Update metrics in test mode (when API key is not available)."""
    METRICS_FILE = "metrics.json"
    
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
        except:
            metrics = {
                "total_requests": 0,
                "successful_processing": 0,
                "failed_processing": 0,
                "step1_summaries": 0,
                "step2_rewrites": 0,
                "step3_keywords": 0,
                "total_latency_ms": 0,
                "average_latency_ms": 0.0,
                "last_request_time": None,
                "requests": []
            }
    else:
        metrics = {
            "total_requests": 0,
            "successful_processing": 0,
            "failed_processing": 0,
            "step1_summaries": 0,
            "step2_rewrites": 0,
            "step3_keywords": 0,
            "total_latency_ms": 0,
            "average_latency_ms": 0.0,
            "last_request_time": None,
            "requests": []
        }
    
    metrics["total_requests"] += 1
    metrics["total_latency_ms"] += latency_ms
    metrics["average_latency_ms"] = metrics["total_latency_ms"] / metrics["total_requests"]
    metrics["last_request_time"] = datetime.now().isoformat()
    
    if success:
        metrics["successful_processing"] += 1
    else:
        metrics["failed_processing"] += 1
    
    if step1:
        metrics["step1_summaries"] += 1
    if step2:
        metrics["step2_rewrites"] += 1
    if step3:
        metrics["step3_keywords"] += 1
    
    metrics["requests"].append({
        "latency_ms": latency_ms,
        "success": success,
        "step1": step1,
        "step2": step2,
        "step3": step3,
        "timestamp": datetime.now().isoformat()
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    # Update dashboard if available
    try:
        import requests
        DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except:
        pass

def background_demo(interval=15):
    """Run background demo that adds requests every N seconds."""
    print("=" * 60)
    print("Background Demo - Continuous Real-time Updates")
    if not HAS_API_KEY:
        print("⚠️  Running in TEST MODE (no API key)")
    print("=" * 60)
    print(f"Running article processing every {interval} seconds")
    print("Open http://localhost:5000 to see live updates!")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    # Load sample article
    article_content = None
    if os.path.exists("sample_article.txt"):
        with open("sample_article.txt", "r", encoding="utf-8") as f:
            article_content = f.read()
    
    request_count = 0
    
    try:
        while running:
            request_count += 1
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Request #{request_count}: Processing article...")
            
            if HAS_API_KEY and article_content:
                # Real mode: call actual API
                main.process_article(article_content)
            else:
                # Test mode: simulate metrics
                latency = random.uniform(2000, 5000)  # Simulate realistic latency for 3 steps
                success = random.random() > 0.1  # 90% success rate
                step1 = success and random.random() > 0.1
                step2 = step1 and random.random() > 0.1
                step3 = step2 and random.random() > 0.1
                update_metrics_test_mode(latency, success=success, step1=step1, step2=step2, step3=step3)
                status = "✅ Success" if success else "❌ Error"
                steps_completed = sum([step1, step2, step3])
                print(f"  Simulated: {latency:.1f}ms - {status} - {steps_completed}/3 steps completed")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n✅ Background demo stopped.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Background demo for continuous real-time updates")
    parser.add_argument("--interval", type=int, default=15, help="Seconds between requests (default: 15)")
    args = parser.parse_args()
    
    background_demo(args.interval)
