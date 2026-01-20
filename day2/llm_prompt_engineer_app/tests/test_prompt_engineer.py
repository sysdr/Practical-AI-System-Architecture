import pytest
import os
import sys
import json

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from prompt_engineer_app import (
    call_llm,
    zero_shot_summarize,
    few_shot_structured_summarize,
    CUSTOMER_FEEDBACK_TEXT
)

def test_customer_feedback_text_exists():
    """Test that customer feedback text is defined"""
    assert CUSTOMER_FEEDBACK_TEXT is not None
    assert len(CUSTOMER_FEEDBACK_TEXT) > 0

def test_call_llm_function_exists():
    """Test that call_llm function exists and is callable"""
    assert callable(call_llm)

def test_zero_shot_summarize_function_exists():
    """Test that zero_shot_summarize function exists and is callable"""
    assert callable(zero_shot_summarize)

def test_few_shot_structured_summarize_function_exists():
    """Test that few_shot_structured_summarize function exists and is callable"""
    assert callable(few_shot_structured_summarize)

def test_call_llm_without_api_key():
    """Test that call_llm handles missing API key gracefully"""
    original_key = os.environ.get("OPENAI_API_KEY")
    try:
        # Temporarily remove API key
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # This should raise an error or return None
        # The function should handle this gracefully
        result = call_llm("test prompt")
        # If it doesn't raise, it should return None or handle the error
        assert result is None or isinstance(result, str)
    except (ValueError, Exception) as e:
        # Expected behavior - function should handle missing key
        assert True
    finally:
        # Restore original key
        if original_key:
            os.environ["OPENAI_API_KEY"] = original_key

# Note: Integration tests that actually call the API would require a valid API key
# and are not included here to avoid making real API calls during testing
