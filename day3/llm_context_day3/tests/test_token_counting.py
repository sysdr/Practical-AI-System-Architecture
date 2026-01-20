import pytest
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_with_dashboard import count_tokens, truncate_text_to_fit_context, simulate_llm_interaction

def test_count_tokens_short_text():
    """Test token counting with short text"""
    text = "Hello, world!"
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)

def test_count_tokens_long_text():
    """Test token counting with long text"""
    text = "The quick brown fox jumps over the lazy dog. " * 10
    tokens = count_tokens(text)
    assert tokens > 0
    assert isinstance(tokens, int)

def test_count_tokens_empty():
    """Test token counting with empty text"""
    text = ""
    tokens = count_tokens(text)
    assert tokens == 0

def test_truncate_text_no_truncation_needed():
    """Test truncation when text fits within limit"""
    text = "Short text"
    max_tokens = 100
    result = truncate_text_to_fit_context(text, max_tokens)
    assert result == text

def test_truncate_text_truncation_needed():
    """Test truncation when text exceeds limit"""
    text = "The quick brown fox jumps over the lazy dog. " * 50
    max_tokens = 10
    result = truncate_text_to_fit_context(text, max_tokens)
    assert len(result) < len(text)
    tokens = count_tokens(result)
    assert tokens <= max_tokens

def test_simulate_llm_interaction_fits():
    """Test simulation when text fits in context window"""
    text = "Short text"
    # Should not raise exception
    simulate_llm_interaction(text, context_window_size=1024, expected_output_tokens=100)

def test_simulate_llm_interaction_overflow():
    """Test simulation when text exceeds context window"""
    text = "The quick brown fox jumps over the lazy dog. " * 100
    # Should not raise exception
    simulate_llm_interaction(text, context_window_size=50, expected_output_tokens=10)
