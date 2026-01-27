#!/usr/bin/env python3
"""
Background demo script that continuously runs product extractions.
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

def update_metrics_test_mode(latency_ms, success=True, validation_error=False):
    """Update metrics in test mode (when API key is not available)."""
    METRICS_FILE = "metrics.json"
    
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                metrics = json.load(f)
        except:
            metrics = {
                "total_requests": 0,
                "successful_extractions": 0,
                "failed_extractions": 0,
                "validation_errors": 0,
                "total_latency_ms": 0,
                "average_latency_ms": 0.0,
                "last_request_time": None,
                "requests": []
            }
    else:
        metrics = {
            "total_requests": 0,
            "successful_extractions": 0,
            "failed_extractions": 0,
            "validation_errors": 0,
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
        metrics["successful_extractions"] += 1
    else:
        metrics["failed_extractions"] += 1
    
    if validation_error:
        metrics["validation_errors"] += 1
    
    metrics["requests"].append({
        "latency_ms": latency_ms,
        "success": success,
        "validation_error": validation_error,
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

def background_demo(interval=10):
    """Run background demo that adds requests every N seconds."""
    print("=" * 60)
    print("Background Demo - Continuous Real-time Updates")
    if not HAS_API_KEY:
        print("⚠️  Running in TEST MODE (no API key)")
    print("=" * 60)
    print(f"Running product extractions every {interval} seconds")
    print("Open http://localhost:5000 to see live updates!")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    descriptions = [
        "The new 'Quantum Leap' smartwatch by Chronos. Costs $299.99. Key features include heart rate monitoring, GPS, and 5-day battery life. It has a stellar 4.7 rating.",
        "Just bought the 'EcoClean' all-purpose cleaner. It's 15 EUR. Features: plant-based, non-toxic. No brand mentioned, no rating yet.",
        "Amazing 'Sonic Toothbrush' - cost me 50 bucks. Super powerful, comes with 3 brush heads. Brand is 'BrightSmile'.",
        "A fantastic 'Ergonomic Keyboard' from KeyPro, priced at 120 USD. Features include mechanical switches and RGB lighting. Average rating 4.2 out of 5.",
        "The 'Ultra-Portable Charger' is amazing. It's twenty-five dollars. Charges fast. No specific brand or rating mentioned.",
        "Premium 'Wireless Earbuds' by SoundMax, $89.99. Features: noise cancellation, 30-hour battery, water resistant. Rating: 4.5 stars.",
        "Budget 'Laptop Stand' for $24.99. Adjustable height, aluminum construction. No brand specified.",
    ]
    
    request_count = 0
    
    try:
        while running:
            request_count += 1
            description = random.choice(descriptions)
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Request #{request_count}: Processing product extraction...")
            
            if HAS_API_KEY:
                # Real mode: call actual API
                main.extract_and_validate_product_details(description)
            else:
                # Test mode: simulate metrics
                latency = random.uniform(800, 2500)  # Simulate realistic latency
                success = random.random() > 0.1  # 90% success rate
                validation_error = False if success else (random.random() > 0.5)
                update_metrics_test_mode(latency, success=success, validation_error=validation_error)
                status = "✅ Success" if success else ("❌ Validation Error" if validation_error else "❌ Error")
                print(f"  Simulated: {latency:.1f}ms - {status}")
            
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n✅ Background demo stopped.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Background demo for continuous real-time updates")
    parser.add_argument("--interval", type=int, default=10, help="Seconds between requests (default: 10)")
    args = parser.parse_args()
    
    background_demo(args.interval)
