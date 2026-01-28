#!/usr/bin/env python3
"""
Background demo script that continuously runs parsing tasks.
This ensures the dashboard shows real-time changing data.
"""
import os
import sys
import time
import random
import signal

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

try:
    from src.main import extract_task_from_text
    HAS_IMPORTS = True
except Exception as e:
    print(f"⚠️  Import error: {e}")
    HAS_IMPORTS = False

running = True

def signal_handler(sig, frame):
    """Handle shutdown signals."""
    global running
    print("\n🛑 Stopping background demo...")
    running = False
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def background_demo(interval=10):
    """Run background demo that adds requests every N seconds."""
    print("=" * 60)
    print("Background Demo - Continuous Real-time Updates")
    print("=" * 60)
    print(f"Running parsing tasks every {interval} seconds")
    print("Open http://localhost:5000 to see live updates!")
    print("Press Ctrl+C to stop")
    print("=" * 60)
    print()
    
    test_prompts = [
        "I need to write a report by December 31, 2023. This is high priority.",
        "Review the code by January 15, 2024. Medium priority task.",
        "Prepare presentation for January 20, 2024. Low priority.",
        "Fix the bug by February 1, 2024. High priority.",
        "Update documentation by March 10, 2024. Medium priority.",
        "Test the application by April 5, 2024. Low priority.",
        "Deploy the system by May 1, 2024. High priority.",
    ]
    
    request_count = 0
    
    try:
        while running:
            request_count += 1
            prompt = random.choice(test_prompts)
            
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Request #{request_count}: Processing task extraction...")
            print(f"  Prompt: {prompt}")
            
            if HAS_IMPORTS:
                try:
                    task = extract_task_from_text(prompt, use_real_llm=False)
                    print(f"  ✅ Success: {task.name} - {task.due_date} - {task.priority}")
                except Exception as e:
                    print(f"  ❌ Error: {e}")
            else:
                print("  ⚠️  Skipping (import error)")
            
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
