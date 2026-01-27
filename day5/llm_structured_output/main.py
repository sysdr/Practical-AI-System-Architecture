import os
import json
import time
from datetime import datetime
from openai import OpenAI
from pydantic import ValidationError
from product_schema import ProductDetails
import requests

# --- Configuration ---
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it to your OpenAI API key.")

client = OpenAI(api_key=OPENAI_API_KEY)
LLM_MODEL = "gpt-4o"
METRICS_FILE = "metrics.json"
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")

# --- Metrics Functions ---
def load_metrics():
    """Load metrics from JSON file."""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            pass
    return {
        "total_requests": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "validation_errors": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0.0,
        "last_request_time": None,
        "requests": []
    }

def save_metrics(metrics):
    """Save metrics to JSON file."""
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def update_metrics(latency_ms, success=True, validation_error=False):
    """Update metrics with new request data."""
    metrics = load_metrics()
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
    
    # Keep last 100 requests
    metrics["requests"].append({
        "latency_ms": latency_ms,
        "success": success,
        "validation_error": validation_error,
        "timestamp": datetime.now().isoformat()
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    
    save_metrics(metrics)
    
    # Update dashboard if available
    try:
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except:
        pass  # Dashboard might not be running

# --- System Prompt with Schema Injection ---
SYSTEM_PROMPT_CONTENT = f"""
You are an expert data extraction assistant. Your task is to extract product details from user input and return them as a JSON object.
The JSON object MUST conform precisely to the following JSON schema. Do not include any additional text or formatting outside the JSON object.
{json.dumps(ProductDetails.model_json_schema(), indent=2)}

Ensure all fields are correctly identified and formatted according to the schema.
If a piece of information is not explicitly mentioned, omit it if optional, or use a reasonable default/empty value if required and no information is available.
Be concise and accurate.
"""

def extract_and_validate_product_details(description: str) -> ProductDetails:
    """
    Extracts product details from a description using an LLM and validates against Pydantic schema.
    """
    print(f"\n--- Processing Description ---\nInput: {description}")
    start_time = time.perf_counter()
    
    try:
        response = client.chat.completions.create(
            model=LLM_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT_CONTENT},
                {"role": "user", "content": description}
            ],
            response_format={"type": "json_object"}
        )
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        
        raw_json_output = response.choices[0].message.content
        print(f"\nRaw LLM Output:\n{raw_json_output}")

        # Validate with Pydantic
        validated_data = ProductDetails.model_validate_json(raw_json_output)
        print("\n--- Validation SUCCESS ---")
        print(f"Validated ProductDetails object:\n{validated_data.model_dump_json(indent=2)}")
        update_metrics(latency_ms, success=True, validation_error=False)
        return validated_data
    except ValidationError as e:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        print(f"\n--- Validation FAILED ---")
        print(f"Error: {e}")
        print(f"LLM output could not be validated against the schema. Raw output was:\n{raw_json_output}")
        update_metrics(latency_ms, success=False, validation_error=True)
        return None
    except Exception as e:
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        print(f"\n--- An unexpected error occurred ---")
        print(f"Error: {e}")
        update_metrics(latency_ms, success=False, validation_error=False)
        return None

if __name__ == "__main__":
    # Check if dashboard is running
    try:
        response = requests.get(f"{DASHBOARD_URL}/metrics", timeout=1)
        print(f"✅ Dashboard is running at {DASHBOARD_URL}")
    except:
        print(f"⚠️  Dashboard not detected at {DASHBOARD_URL}")
        print("   Metrics will still be tracked locally. Start dashboard with: ./start_dashboard.sh")
    
    # Test Cases
    descriptions = [
        "The new 'Quantum Leap' smartwatch by Chronos. Costs $299.99. Key features include heart rate monitoring, GPS, and 5-day battery life. It has a stellar 4.7 rating.",
        "Just bought the 'EcoClean' all-purpose cleaner. It's 15 EUR. Features: plant-based, non-toxic. No brand mentioned, no rating yet.",
        "Amazing 'Sonic Toothbrush' - cost me 50 bucks. Super powerful, comes with 3 brush heads. Brand is 'BrightSmile'.",
        "This 'Mystery Gadget' is just 10.50. No other details given.",
        "A fantastic 'Ergonomic Keyboard' from KeyPro, priced at 120 USD. Features include mechanical switches and RGB lighting. Average rating 4.2 out of 5.",
        "The 'Ultra-Portable Charger' is amazing. It's twenty-five dollars. Charges fast. No specific brand or rating mentioned."
    ]

    for desc in descriptions:
        extract_and_validate_product_details(desc)
        time.sleep(1)  # Small delay between requests

    print("\n--- Demonstration Complete ---")
    print(f"Check dashboard at: {DASHBOARD_URL}")
