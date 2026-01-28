import json
import time
import os
import sys
from datetime import datetime
from typing import Type, TypeVar, Dict, Any
from pydantic import ValidationError, BaseModel
import requests

# Add src directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from schema import Task, get_task_schema_json
from llm_service import call_llm, LLMServiceError

# Generic type for Pydantic models
T = TypeVar('T', bound=BaseModel)

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
        "successful_parsing": 0,
        "failed_parsing": 0,
        "retry_attempts": 0,
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

def update_metrics(latency_ms, success=True, retries=0, validation_error=False):
    """Update metrics with new request data."""
    metrics = load_metrics()
    metrics["total_requests"] += 1
    metrics["total_latency_ms"] += latency_ms
    metrics["average_latency_ms"] = metrics["total_latency_ms"] / metrics["total_requests"]
    metrics["last_request_time"] = datetime.now().isoformat()
    metrics["retry_attempts"] += retries
    
    if success:
        metrics["successful_parsing"] += 1
    else:
        metrics["failed_parsing"] += 1
    
    if validation_error:
        metrics["validation_errors"] += 1
    
    metrics["requests"].append({
        "latency_ms": latency_ms,
        "success": success,
        "retries": retries,
        "validation_error": validation_error,
        "timestamp": datetime.now().isoformat()
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    
    save_metrics(metrics)
    
    try:
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except:
        pass

class ReliableLLMParser:
    def __init__(self, max_retries: int = 3, initial_backoff_sec: int = 1):
        self.max_retries = max_retries
        self.initial_backoff_sec = initial_backoff_sec

    def call_llm_with_retry(
        self,
        original_prompt: str,
        output_schema_model: Type[T],
        use_real_llm: bool = False,
        malform_chance: float = 0.5
    ) -> T:
        
        output_schema_json = json.dumps(output_schema_model.model_json_schema(), indent=2)
        
        full_prompt = (
            f"{original_prompt}\n"
            f"Please respond strictly in JSON format according to the following schema:\n"
            f"{output_schema_json}\n"
            f"Return only valid JSON, no additional text."
        )
        
        retry_count = 0
        start_time = time.perf_counter()
        
        for attempt in range(self.max_retries + 1):
            try:
                raw_response = call_llm(full_prompt, malform_chance, use_real_llm)
                
                # Try to extract JSON from response
                json_str = raw_response.strip()
                
                # Remove any leading/trailing text that's not JSON
                if json_str.startswith("```json"):
                    json_str = json_str[7:]
                if json_str.startswith("```"):
                    json_str = json_str[3:]
                if json_str.endswith("```"):
                    json_str = json_str[:-3]
                json_str = json_str.strip()
                
                # Try to find JSON object in the string
                start_idx = json_str.find('{')
                end_idx = json_str.rfind('}')
                if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                    json_str = json_str[start_idx:end_idx+1]
                
                # Parse and validate
                parsed_data = json.loads(json_str)
                validated_obj = output_schema_model.model_validate(parsed_data)
                
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                update_metrics(latency_ms, success=True, retries=retry_count)
                
                return validated_obj
                
            except (json.JSONDecodeError, ValidationError) as e:
                retry_count += 1
                if attempt < self.max_retries:
                    backoff_time = self.initial_backoff_sec * (2 ** attempt)
                    print(f"[Parser] Validation/JSON error on attempt {attempt + 1}/{self.max_retries + 1}: {e}")
                    print(f"[Parser] Retrying in {backoff_time} seconds...")
                    
                    # Create correction prompt
                    correction_prompt = (
                        f"Your previous response was malformed or invalid. Please correct your response.\n"
                        f"Original prompt: {original_prompt}\n"
                        f"Your previous (invalid) response: {raw_response}\n"
                        f"Error: {str(e)}\n"
                        f"Please respond with valid JSON according to this schema:\n"
                        f"{output_schema_json}\n"
                        f"Return only valid JSON, no additional text."
                    )
                    full_prompt = correction_prompt
                    time.sleep(backoff_time)
                else:
                    end_time = time.perf_counter()
                    latency_ms = (end_time - start_time) * 1000
                    update_metrics(latency_ms, success=False, retries=retry_count, validation_error=True)
                    raise ValueError(f"Failed to parse LLM output after {self.max_retries + 1} attempts. Last error: {e}")
            except LLMServiceError as e:
                end_time = time.perf_counter()
                latency_ms = (end_time - start_time) * 1000
                update_metrics(latency_ms, success=False, retries=retry_count)
                raise
        
        end_time = time.perf_counter()
        latency_ms = (end_time - start_time) * 1000
        update_metrics(latency_ms, success=False, retries=retry_count)
        raise ValueError("Failed to parse LLM output after all retries.")

def extract_task_from_text(text: str, use_real_llm: bool = False) -> Task:
    """Extract a Task object from natural language text."""
    parser = ReliableLLMParser(max_retries=3, initial_backoff_sec=1)
    prompt = f"Extract task information from the following text: {text}"
    return parser.call_llm_with_retry(prompt, Task, use_real_llm=use_real_llm, malform_chance=0.5)

if __name__ == "__main__":
    # Check if dashboard is running
    try:
        response = requests.get(f"{DASHBOARD_URL}/metrics", timeout=1)
        print(f"✅ Dashboard is running at {DASHBOARD_URL}")
    except:
        print(f"⚠️  Dashboard not detected at {DASHBOARD_URL}")
        print("   Metrics will still be tracked locally. Start dashboard with: ./start_dashboard.sh")
    
    # Test cases
    test_prompts = [
        "I need to write a report by December 31, 2023. This is high priority.",
        "Review the code by January 15, 2024. Medium priority task.",
        "Prepare presentation for January 20, 2024. Low priority.",
        "Fix the bug by February 1, 2024. High priority.",
        "Update documentation by March 10, 2024. Medium priority."
    ]
    
    print("\n" + "="*60)
    print("Reliable Output Parsing Demo")
    print("="*60)
    
    for i, prompt in enumerate(test_prompts, 1):
        print(f"\n--- Test {i}/{len(test_prompts)} ---")
        print(f"Input: {prompt}")
        try:
            task = extract_task_from_text(prompt, use_real_llm=False)
            print(f"✅ Successfully parsed:")
            print(f"   Name: {task.name}")
            print(f"   Due Date: {task.due_date}")
            print(f"   Priority: {task.priority}")
        except Exception as e:
            print(f"❌ Failed to parse: {e}")
        time.sleep(1)
    
    print("\n" + "="*60)
    print("Demo completed!")
    print(f"Check dashboard at: {DASHBOARD_URL}")
    print("="*60)
