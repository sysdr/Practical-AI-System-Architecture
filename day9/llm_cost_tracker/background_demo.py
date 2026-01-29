#!/usr/bin/env python3
"""Background demo that runs cost tracker prompts so the dashboard shows non-zero metrics."""
import os
import sys
import time
import random
import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from src.main import MockLLMAPI, TokenCostCalculator, LLMCostTracker, LLM_PRICING
    HAS_IMPORTS = True
except Exception as e:
    print(f"Import error: {e}")
    HAS_IMPORTS = False

running = True
def signal_handler(sig, frame):
    global running
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

DEMO_PROMPTS = [
    "Summarize the history of artificial intelligence.",
    "Explain the concept of quantum entanglement in simple terms.",
    "Write a short poem about a sunny day.",
    "What is the capital of France?",
    "Describe machine learning in one paragraph.",
]

def background_demo(interval=8):
    print("=" * 60)
    print("Background Demo - LLM Cost Tracker (dashboard updates)")
    print("=" * 60)
    print(f"Running prompts every {interval} seconds. Open http://localhost:5000")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    if not HAS_IMPORTS:
        print("Import failed. Exiting.")
        return
    mock_llm = MockLLMAPI(default_model="gpt-4-turbo-2024-04-09")
    cost_calculator = TokenCostCalculator(LLM_PRICING)
    tracker = LLMCostTracker(mock_llm, cost_calculator)
    count = 0
    try:
        while running:
            count += 1
            prompt = random.choice(DEMO_PROMPTS)
            model = random.choice(["gpt-4-turbo-2024-04-09", "gpt-3.5-turbo-0125"])
            print(f"[{time.strftime('%H:%M:%S')}] Request #{count}: {prompt[:50]}...")
            tracker.process_prompt(prompt, model=model)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    print("\n✅ Background demo stopped.")

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--interval", type=int, default=8)
    background_demo(p.parse_args().interval)
