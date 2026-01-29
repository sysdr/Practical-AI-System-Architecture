import tiktoken
import os
import sys
import json
import datetime
import requests
from datetime import datetime as dt

# Ensure we use project dir for metrics (cwd when run as python src/main.py from project root)
PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")
DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:5000")

# --- Configuration ---
LLM_PRICING = {
    "gpt-4-turbo-2024-04-09": {
        "input_cost_per_1k_tokens": 0.01,
        "output_cost_per_1k_tokens": 0.03
    },
    "gpt-3.5-turbo-0125": {
        "input_cost_per_1k_tokens": 0.0005,
        "output_cost_per_1k_tokens": 0.0015
    }
}

DEFAULT_ENCODING_MODEL = "cl100k_base"

# --- Metrics ---
def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_prompts": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_estimated_cost": 0.0,
        "last_request_time": None,
        "requests": []
    }

def save_metrics(metrics):
    with open(METRICS_FILE, 'w') as f:
        json.dump(metrics, f, indent=2)

def update_metrics(model_used, input_tokens, output_tokens, estimated_cost, prompt_preview=""):
    metrics = load_metrics()
    metrics["total_prompts"] += 1
    metrics["total_input_tokens"] += input_tokens
    metrics["total_output_tokens"] += output_tokens
    metrics["total_estimated_cost"] = round(metrics["total_estimated_cost"] + estimated_cost, 6)
    metrics["last_request_time"] = dt.now().isoformat()
    metrics["requests"].append({
        "timestamp": dt.now().isoformat(),
        "model_used": model_used,
        "input_tokens": input_tokens,
        "output_tokens": output_tokens,
        "estimated_cost": estimated_cost,
        "prompt_preview": (prompt_preview or "")[:80]
    })
    if len(metrics["requests"]) > 100:
        metrics["requests"] = metrics["requests"][-100:]
    save_metrics(metrics)
    try:
        requests.get(f"{DASHBOARD_URL}/update", timeout=0.1)
    except Exception:
        pass

# --- Core Components ---
class TokenCostCalculator:
    def __init__(self, pricing_model: dict):
        self.pricing_model = pricing_model

    def calculate_cost(self, model_name: str, input_tokens: int, output_tokens: int) -> float:
        if model_name not in self.pricing_model:
            raise ValueError(f"Pricing model for '{model_name}' not found.")
        model_pricing = self.pricing_model[model_name]
        input_cost = (input_tokens / 1000) * model_pricing["input_cost_per_1k_tokens"]
        output_cost = (output_tokens / 1000) * model_pricing["output_cost_per_1k_tokens"]
        return input_cost + output_cost

class MockLLMAPI:
    def __init__(self, default_model: str = "gpt-4-turbo-2024-04-09"):
        self.default_model = default_model
        self.encoder = tiktoken.get_encoding(DEFAULT_ENCODING_MODEL)

    def _count_tokens(self, text: str) -> int:
        return len(self.encoder.encode(text))

    def generate_response(self, prompt: str, model: str = None) -> tuple:
        actual_model = model if model else self.default_model
        input_tokens = self._count_tokens(prompt)
        if "summarize" in prompt.lower():
            mock_response = "The provided text discusses key concepts related to AI, including its history, current applications, and future challenges. It emphasizes the importance of ethical considerations and continuous learning in the field."
        elif "explain quantum entanglement" in prompt.lower():
            mock_response = "Quantum entanglement is a phenomenon where two or more particles become linked in such a way that they share the same fate, no matter how far apart they are."
        elif "write a short poem" in prompt.lower():
            mock_response = "In lines of code, a thought takes flight,\nAI dreams in silicon light.\nFrom data's depths, new wisdom springs,\nOn digital wings, the future sings."
        else:
            mock_response = f"Hello! You asked about '{prompt}'. This is a simulated response from {actual_model}."
        output_tokens = self._count_tokens(mock_response)
        return mock_response, input_tokens, output_tokens

class LLMCostTracker:
    def __init__(self, llm_api: MockLLMAPI, cost_calculator: TokenCostCalculator):
        self.llm_api = llm_api
        self.cost_calculator = cost_calculator
        self.log_entries = []

    def process_prompt(self, prompt: str, model: str = None):
        print("\n--- Processing Prompt ---")
        print(f"Prompt: '{prompt}'")
        actual_model = model if model else self.llm_api.default_model
        print(f"Model: {actual_model}")

        response, input_tokens, output_tokens = self.llm_api.generate_response(prompt, model)
        estimated_cost = self.cost_calculator.calculate_cost(actual_model, input_tokens, output_tokens)

        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "model_used": actual_model,
            "prompt": prompt,
            "response": response,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "estimated_cost": estimated_cost
        }
        self.log_entries.append(log_entry)

        # Update dashboard metrics
        update_metrics(actual_model, input_tokens, output_tokens, estimated_cost, prompt)

        print(f"Input Tokens: {input_tokens}")
        print(f"Output Tokens: {output_tokens}")
        print(f"Estimated Cost: ${estimated_cost:.6f}")
        print(f"Response: {response[:150]}...")
        print("------------------------")
        return log_entry

    def generate_summary_report(self):
        total_input_tokens = sum(entry["input_tokens"] for entry in self.log_entries)
        total_output_tokens = sum(entry["output_tokens"] for entry in self.log_entries)
        total_estimated_cost = sum(entry["estimated_cost"] for entry in self.log_entries)
        print("\n==============================================")
        print("         LLM Cost Tracker Summary Report      ")
        print("==============================================")
        print(f"Total Prompts Processed: {len(self.log_entries)}")
        print(f"Total Input Tokens: {total_input_tokens}")
        print(f"Total Output Tokens: {total_output_tokens}")
        print(f"Total Estimated Cost: ${total_estimated_cost:.6f}")
        print("==============================================")

# --- Main Execution ---
if __name__ == "__main__":
    print("🚀 Starting LLM Cost Tracker Demo...")
    if os.getenv("DASHBOARD_URL"):
        print(f"Dashboard URL: {DASHBOARD_URL}")
        print("Metrics will update the dashboard in real time.")
    else:
        print("Tip: Set DASHBOARD_URL and run dashboard for live metrics.")

    mock_llm = MockLLMAPI(default_model="gpt-4-turbo-2024-04-09")
    cost_calculator = TokenCostCalculator(LLM_PRICING)
    tracker = LLMCostTracker(mock_llm, cost_calculator)

    tracker.process_prompt("Summarize the history of artificial intelligence.", model="gpt-4-turbo-2024-04-09")
    tracker.process_prompt("Explain the concept of quantum entanglement in simple terms.", model="gpt-4-turbo-2024-04-09")
    tracker.process_prompt("Write a short poem about a sunny day.", model="gpt-3.5-turbo-0125")
    tracker.process_prompt("What is the capital of France?", model="gpt-3.5-turbo-0125")

    tracker.generate_summary_report()
    print("\n✅ LLM Cost Tracker Demo Finished.")
    print(f"Check dashboard at: {DASHBOARD_URL}")
