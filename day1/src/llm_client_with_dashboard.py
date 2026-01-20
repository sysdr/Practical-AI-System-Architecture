#!/usr/bin/env python3
"""
Enhanced LLM client that updates dashboard metrics
"""
import os
import sys
import requests
import time
from llm_client import get_llm_response

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8080")

def update_dashboard(success=True, tokens=0):
    """Update dashboard metrics"""
    try:
        requests.get(f"{DASHBOARD_URL}/update", params={
            "success": "true" if success else "false",
            "tokens": str(tokens)
        }, timeout=1)
    except:
        # Dashboard might not be running, that's okay
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Explain the concept of 'distributed consensus' in a simple way."
    
    response = get_llm_response(prompt)
    
    if response:
        tokens = 0
        if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
            tokens = response.usage.total_tokens
        update_dashboard(success=True, tokens=tokens)
        print(f"\n✅ Request successful - {tokens} tokens used")
    else:
        update_dashboard(success=False, tokens=0)
        print("\n❌ Request failed")
