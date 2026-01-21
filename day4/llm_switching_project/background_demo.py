#!/usr/bin/env python3
"""
Background demo script that continuously adds requests every 5 seconds.
This ensures the dashboard shows real-time changing data.
"""
import os
import sys
import time
import random
import signal

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import llm_switcher

running = True

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global running
    print("\n🛑 Stopping background demo...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def background_demo(interval=5):
    """Run background demo that adds requests every N seconds."""
    print("=" * 60)
    print("Background Demo - Continuous Real-time Updates")
    print("=" * 60)
    print(f"Adding new requests every {interval} seconds")
    print("Open http://localhost:5000 to see live updates!")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    providers = ["openai", "anthropic"]
    request_count = 0
    
    try:
        while running:
            request_count += 1
            provider = random.choice(providers)
            # Simulate realistic latency (80-250ms)
            latency = random.uniform(80, 250)
            success = random.random() > 0.15  # 85% success rate
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Request #{request_count}: {provider.upper()} - {latency:.1f}ms - {'✅' if success else '❌'}")
            
            llm_switcher.update_metrics(provider, latency, success=success)
            
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    finally:
        print("\n✅ Background demo stopped.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Background demo for continuous real-time updates")
    parser.add_argument("--interval", type=int, default=5, help="Seconds between requests (default: 5)")
    args = parser.parse_args()
    
    background_demo(args.interval)
