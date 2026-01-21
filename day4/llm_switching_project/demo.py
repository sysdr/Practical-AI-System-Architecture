#!/usr/bin/env python3
"""
Demo script to populate metrics for dashboard validation.
This script simulates LLM requests to update metrics.
"""
import os
import sys
import time
import json
from datetime import datetime

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

import llm_switcher

def simulate_request(provider, latency_ms, success=True):
    """Simulate a request and update metrics."""
    print(f"Simulating {provider.upper()} request (latency: {latency_ms}ms, success: {success})")
    llm_switcher.update_metrics(provider, latency_ms, success=success)
    time.sleep(0.1)  # Small delay for realism

def run_demo():
    """Run demo to populate metrics."""
    print("=" * 60)
    print("Running LLM Switcher Demo")
    print("=" * 60)
    
    # Simulate various requests
    print("\n--- Simulating OpenAI Requests ---")
    simulate_request("openai", 120.5, success=True)
    simulate_request("openai", 135.2, success=True)
    simulate_request("openai", 98.7, success=True)
    simulate_request("openai", 0, success=False)  # Simulate error
    
    print("\n--- Simulating Anthropic Requests ---")
    simulate_request("anthropic", 180.3, success=True)
    simulate_request("anthropic", 165.8, success=True)
    simulate_request("anthropic", 195.4, success=True)
    simulate_request("anthropic", 172.1, success=True)
    
    # Load and display final metrics
    metrics = llm_switcher.load_metrics()
    print("\n" + "=" * 60)
    print("Final Metrics Summary:")
    print("=" * 60)
    print(f"Total Requests: {metrics['total_requests']}")
    print(f"OpenAI Requests: {metrics['openai_requests']}")
    print(f"Anthropic Requests: {metrics['anthropic_requests']}")
    print(f"Total Errors: {metrics['errors']}")
    print(f"Average Latency: {metrics['total_latency_ms'] / metrics['total_requests']:.2f}ms" if metrics['total_requests'] > 0 else "Average Latency: 0ms")
    print(f"Last Request Time: {metrics['last_request_time']}")
    print("=" * 60)
    print("\n✅ Demo completed! Check the dashboard at http://localhost:5000")
    print("   All metrics should now show non-zero values.")

if __name__ == "__main__":
    run_demo()
