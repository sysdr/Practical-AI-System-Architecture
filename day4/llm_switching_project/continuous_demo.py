#!/usr/bin/env python3
"""
Continuous demo script to show real-time dashboard updates.
This script will add requests every few seconds to demonstrate live updates.
"""
import os
import sys
import time
import random

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import llm_switcher

def continuous_demo(num_requests=10, interval=4):
    """Run continuous demo to show real-time updates."""
    print("=" * 60)
    print("Continuous Demo - Real-time Dashboard Updates")
    print("=" * 60)
    print(f"Will add {num_requests} requests with {interval} second intervals")
    print("Open http://localhost:5000 in your browser to see live updates!")
    print("=" * 60)
    print()
    
    providers = ["openai", "anthropic"]
    
    for i in range(1, num_requests + 1):
        provider = random.choice(providers)
        # Simulate realistic latency (100-200ms)
        latency = random.uniform(100, 200)
        success = random.random() > 0.1  # 90% success rate
        
        print(f"[{i}/{num_requests}] Adding {provider.upper()} request (latency: {latency:.1f}ms, success: {success})")
        llm_switcher.update_metrics(provider, latency, success=success)
        
        if i < num_requests:
            print(f"  Waiting {interval} seconds before next request...")
            time.sleep(interval)
    
    metrics = llm_switcher.load_metrics()
    print()
    print("=" * 60)
    print("Demo Complete!")
    print("=" * 60)
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"OpenAI: {metrics['openai_requests']} requests")
    print(f"Anthropic: {metrics['anthropic_requests']} requests")
    print("=" * 60)
    print("\n✅ Dashboard should show all updated metrics in real-time!")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Continuous demo for real-time dashboard")
    parser.add_argument("--requests", type=int, default=10, help="Number of requests to add")
    parser.add_argument("--interval", type=int, default=4, help="Seconds between requests")
    args = parser.parse_args()
    
    continuous_demo(args.requests, args.interval)
