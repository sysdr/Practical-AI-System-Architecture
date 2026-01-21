# filename: llm_switcher.py
import os
import argparse
import json
import time
from datetime import datetime
from openai import OpenAI
from anthropic import Anthropic

METRICS_FILE = "metrics.json"

def load_metrics():
    """Load metrics from JSON file."""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_requests": 0,
                "openai_requests": 0,
                "anthropic_requests": 0,
                "total_latency_ms": 0,
                "openai_latency_ms": 0,
                "anthropic_latency_ms": 0,
                "errors": 0,
                "last_request_time": None,
                "requests": []
            }
    return {
        "total_requests": 0,
        "openai_requests": 0,
        "anthropic_requests": 0,
        "total_latency_ms": 0,
        "openai_latency_ms": 0,
        "anthropic_latency_ms": 0,
        "errors": 0,
        "last_request_time": None,
        "requests": []
    }

def save_metrics(metrics):
    """Save metrics to JSON file."""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def update_metrics(provider, latency_ms, success=True):
    """Update metrics with new request data."""
    metrics = load_metrics()
    metrics["total_requests"] += 1
    metrics["total_latency_ms"] += latency_ms
    metrics["last_request_time"] = datetime.now().isoformat()
    
    if provider == "openai":
        metrics["openai_requests"] += 1
        metrics["openai_latency_ms"] += latency_ms
    elif provider == "anthropic":
        metrics["anthropic_requests"] += 1
        metrics["anthropic_latency_ms"] += latency_ms
    
    if not success:
        metrics["errors"] += 1
    
    # Keep last 100 requests
    metrics["requests"].append({
        "provider": provider,
        "latency_ms": latency_ms,
        "success": success,
        "timestamp": datetime.now().isoformat()
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    
    save_metrics(metrics)

def generate_text_openai(prompt: str, api_key: str, model: str = "gpt-3.5-turbo") -> str:
    """Generates text using OpenAI's API."""
    if not api_key:
        error_msg = "Error: OpenAI API key not set. Please set OPENAI_API_KEY environment variable."
        update_metrics("openai", 0, success=False)
        return error_msg
    try:
        client = OpenAI(api_key=api_key)
        start_time = time.perf_counter()
        response = client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0.7
        )
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000  # milliseconds
        content = response.choices[0].message.content.strip()
        print(f"  (OpenAI Latency: {duration:.2f}ms | Model: {model})")
        update_metrics("openai", duration, success=True)
        return content
    except Exception as e:
        error_msg = f"Error with OpenAI: {e}"
        update_metrics("openai", 0, success=False)
        return error_msg

def generate_text_anthropic(prompt: str, api_key: str, model: str = "claude-3-haiku-20240307") -> str:
    """Generates text using Anthropic's API."""
    if not api_key:
        error_msg = "Error: Anthropic API key not set. Please set ANTHROPIC_API_KEY environment variable."
        update_metrics("anthropic", 0, success=False)
        return error_msg
    try:
        client = Anthropic(api_key=api_key)
        start_time = time.perf_counter()
        response = client.messages.create(
            model=model,
            max_tokens=100,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.7
        )
        end_time = time.perf_counter()
        duration = (end_time - start_time) * 1000  # milliseconds
        content = response.content[0].text.strip()
        print(f"  (Anthropic Latency: {duration:.2f}ms | Model: {model})")
        update_metrics("anthropic", duration, success=True)
        return content
    except Exception as e:
        error_msg = f"Error with Anthropic: {e}"
        update_metrics("anthropic", 0, success=False)
        return error_msg

def main():
    parser = argparse.ArgumentParser(description="Generate text using different LLM providers.")
    parser.add_argument("--provider", type=str, choices=["openai", "anthropic"], required=True,
                        help="Choose LLM provider: 'openai' or 'anthropic'.")
    parser.add_argument("--prompt", type=str, required=True,
                        help="The text prompt for the LLM.")
    parser.add_argument("--openai_model", type=str, default="gpt-3.5-turbo",
                        help="Specify OpenAI model (e.g., gpt-4-turbo, gpt-3.5-turbo).")
    parser.add_argument("--anthropic_model", type=str, default="claude-3-haiku-20240307",
                        help="Specify Anthropic model (e.g., claude-3-opus-20240229, claude-3-sonnet-20240229, claude-3-haiku-20240307).")

    args = parser.parse_args()

    openai_key = os.getenv("OPENAI_API_KEY")
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")

    print(f"\n--- LLM SWITCHER: Generating with {args.provider.upper()} ---")
    if args.provider.lower() == "openai":
        response = generate_text_openai(args.prompt, openai_key, args.openai_model)
        print(f"Response:\n{response}")
    elif args.provider.lower() == "anthropic":
        response = generate_text_anthropic(args.prompt, anthropic_key, args.anthropic_model)
        print(f"Response:\n{response}")
    
    print("\n------------------------------------")

if __name__ == "__main__":
    main()
