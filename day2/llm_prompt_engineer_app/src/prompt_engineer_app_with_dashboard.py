import os
import sys
import requests
import json
from prompt_engineer_app import (
    CUSTOMER_FEEDBACK_TEXT,
    zero_shot_summarize,
    few_shot_structured_summarize,
    call_llm
)

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8080")

def update_dashboard(success=True, tokens=0, request_type=None):
    """Update dashboard metrics"""
    try:
        requests.get(f"{DASHBOARD_URL}/update", params={
            "success": "true" if success else "false",
            "tokens": str(tokens),
            "type": request_type or ""
        }, timeout=1)
    except:
        # Dashboard might not be running, that's okay
        pass

def zero_shot_summarize_with_dashboard(feedback_text, demo_mode=False):
    """Zero-shot summarization with dashboard integration"""
    try:
        if demo_mode:
            # Simulate successful API call for demo purposes
            print("\\n--- Zero-Shot Summarization (Demo Mode) ---")
            summary = "Customer feedback indicates issues with brush attachment durability and battery life not meeting advertised specifications. Positive note on mobile app usability."
            print("Zero-shot Summary:")
            print(summary)
            # Estimate tokens: input + output (rough approximation)
            tokens = len(feedback_text.split()) * 1.3 + len(summary.split()) * 1.3
            tokens = int(tokens) + 50  # Add overhead, typical range 150-250 tokens
            update_dashboard(success=True, tokens=tokens, request_type="zero_shot")
            return summary
        else:
            summary = zero_shot_summarize(feedback_text)
            # Estimate tokens (rough approximation)
            tokens = len(feedback_text.split()) + len(summary.split()) if summary else 0
            update_dashboard(success=True, tokens=tokens, request_type="zero_shot")
            return summary
    except Exception as e:
        print(f"Error in zero-shot summarization: {e}")
        update_dashboard(success=False, tokens=0, request_type="zero_shot")
        return None

def few_shot_structured_summarize_with_dashboard(feedback_text, demo_mode=False):
    """Few-shot structured summarization with dashboard integration"""
    try:
        if demo_mode:
            # Simulate successful API call for demo purposes
            print("\\n--- Few-Shot Structured Summarization (Demo Mode) ---")
            result_json = {
                "issue": "Brush attachment failure and battery life below advertised",
                "sentiment": "Negative",
                "product_area": "Hardware",
                "priority": "High"
            }
            print("Few-shot Structured Summary:")
            print(json.dumps(result_json, indent=2))
            # Few-shot uses more tokens due to examples in prompt
            tokens = len(feedback_text.split()) * 2.5 + 200  # Examples add ~200 tokens
            tokens = int(tokens) + 100  # Typical range 300-500 tokens
            update_dashboard(success=True, tokens=tokens, request_type="few_shot")
            return result_json
        else:
            result = few_shot_structured_summarize(feedback_text)
            # Estimate tokens (rough approximation)
            tokens = len(feedback_text.split()) * 3  # Few-shot uses more tokens
            update_dashboard(success=True, tokens=tokens, request_type="few_shot")
            return result
    except Exception as e:
        print(f"Error in few-shot summarization: {e}")
        update_dashboard(success=False, tokens=0, request_type="few_shot")
        return None

if __name__ == "__main__":
    import sys
    
    # Check for demo mode flag
    demo_mode = "--demo" in sys.argv or os.getenv("DEMO_MODE", "false").lower() == "true"
    
    print("=" * 60)
    print("LLM Prompt Engineering Demo with Dashboard")
    if demo_mode:
        print("(Running in DEMO MODE - simulating successful API calls)")
    print("=" * 60)
    
    # Check if dashboard is running
    try:
        response = requests.get(f"{DASHBOARD_URL}/metrics", timeout=1)
        print(f"✅ Dashboard is running at {DASHBOARD_URL}")
    except:
        print(f"⚠️  Dashboard not detected at {DASHBOARD_URL}")
        print("   Metrics will not be tracked. Start dashboard with: ./start_dashboard.sh")
    
    print("\\n" + "=" * 60)
    
    # Zero-shot summarization
    try:
        zero_shot_summarize_with_dashboard(CUSTOMER_FEEDBACK_TEXT, demo_mode=demo_mode)
    except Exception as e:
        print(f"Zero-shot summarization failed: {e}")
        # Dashboard already updated with failure
    
    print("\\n" + "=" * 60)
    
    # Few-shot structured summarization
    try:
        few_shot_structured_summarize_with_dashboard(CUSTOMER_FEEDBACK_TEXT, demo_mode=demo_mode)
    except Exception as e:
        print(f"Few-shot summarization failed: {e}")
        # Dashboard already updated with failure
    
    print("\\n" + "=" * 60)
    print("Demo completed! Check dashboard at:", DASHBOARD_URL)
