import pytest
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.main import TokenCostCalculator, MockLLMAPI, LLMCostTracker, LLM_PRICING

def test_cost_calculator():
    calc = TokenCostCalculator(LLM_PRICING)
    cost = calc.calculate_cost("gpt-4-turbo-2024-04-09", 1000, 500)
    assert cost > 0
    assert cost == pytest.approx(0.01 * 1 + 0.03 * 0.5, rel=1e-5)

def test_mock_llm_returns_tokens():
    api = MockLLMAPI()
    response, inp, out = api.generate_response("Hello")
    assert isinstance(response, str)
    assert inp >= 0
    assert out >= 0

def test_tracker_process_prompt():
    api = MockLLMAPI(default_model="gpt-3.5-turbo-0125")
    calc = TokenCostCalculator(LLM_PRICING)
    tracker = LLMCostTracker(api, calc)
    entry = tracker.process_prompt("What is 2+2?")
    assert "input_tokens" in entry
    assert "output_tokens" in entry
    assert "estimated_cost" in entry
    assert entry["estimated_cost"] >= 0
    assert len(tracker.log_entries) == 1

def test_metrics_file_structure():
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(test_dir, "metrics.json")
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            data = json.load(f)
        assert "total_prompts" in data or "requests" in data
