# filename: test_llm_switcher.py
import unittest
import os
import json
import sys
from unittest.mock import patch, MagicMock
import llm_switcher

class TestLLMSwitcher(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures."""
        # Clear metrics before each test
        if os.path.exists("metrics.json"):
            os.remove("metrics.json")
    
    def test_load_metrics_empty(self):
        """Test loading metrics when file doesn't exist."""
        if os.path.exists("metrics.json"):
            os.remove("metrics.json")
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["total_requests"], 0)
        self.assertEqual(metrics["openai_requests"], 0)
        self.assertEqual(metrics["anthropic_requests"], 0)
    
    def test_save_and_load_metrics(self):
        """Test saving and loading metrics."""
        test_metrics = {
            "total_requests": 5,
            "openai_requests": 3,
            "anthropic_requests": 2,
            "total_latency_ms": 1000,
            "openai_latency_ms": 600,
            "anthropic_latency_ms": 400,
            "errors": 0,
            "last_request_time": None,
            "requests": []
        }
        llm_switcher.save_metrics(test_metrics)
        loaded = llm_switcher.load_metrics()
        self.assertEqual(loaded["total_requests"], 5)
        self.assertEqual(loaded["openai_requests"], 3)
        self.assertEqual(loaded["anthropic_requests"], 2)
    
    def test_update_metrics_openai(self):
        """Test updating metrics for OpenAI requests."""
        llm_switcher.update_metrics("openai", 150.5, success=True)
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["total_requests"], 1)
        self.assertEqual(metrics["openai_requests"], 1)
        self.assertEqual(metrics["openai_latency_ms"], 150.5)
        self.assertEqual(metrics["errors"], 0)
    
    def test_update_metrics_anthropic(self):
        """Test updating metrics for Anthropic requests."""
        llm_switcher.update_metrics("anthropic", 200.3, success=True)
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["total_requests"], 1)
        self.assertEqual(metrics["anthropic_requests"], 1)
        self.assertEqual(metrics["anthropic_latency_ms"], 200.3)
        self.assertEqual(metrics["errors"], 0)
    
    def test_update_metrics_error(self):
        """Test updating metrics for failed requests."""
        llm_switcher.update_metrics("openai", 0, success=False)
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["errors"], 1)
    
    @patch.dict(os.environ, {"OPENAI_API_KEY": "test-key"})
    @patch('llm_switcher.OpenAI')
    def test_generate_text_openai_success(self, mock_openai):
        """Test successful OpenAI text generation."""
        mock_client = MagicMock()
        mock_openai.return_value = mock_client
        mock_response = MagicMock()
        mock_response.choices = [MagicMock()]
        mock_response.choices[0].message.content = "Test response"
        mock_client.chat.completions.create.return_value = mock_response
        
        result = llm_switcher.generate_text_openai("test prompt", "test-key")
        self.assertEqual(result, "Test response")
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["openai_requests"], 1)
        self.assertGreater(metrics["openai_latency_ms"], 0)
    
    @patch.dict(os.environ, {"ANTHROPIC_API_KEY": "test-key"})
    @patch('llm_switcher.Anthropic')
    def test_generate_text_anthropic_success(self, mock_anthropic):
        """Test successful Anthropic text generation."""
        mock_client = MagicMock()
        mock_anthropic.return_value = mock_client
        mock_response = MagicMock()
        mock_response.content = [MagicMock()]
        mock_response.content[0].text = "Test response"
        mock_client.messages.create.return_value = mock_response
        
        result = llm_switcher.generate_text_anthropic("test prompt", "test-key")
        self.assertEqual(result, "Test response")
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["anthropic_requests"], 1)
        self.assertGreater(metrics["anthropic_latency_ms"], 0)
    
    def test_generate_text_openai_no_key(self):
        """Test OpenAI generation without API key."""
        result = llm_switcher.generate_text_openai("test prompt", None)
        self.assertIn("Error", result)
        metrics = llm_switcher.load_metrics()
        self.assertEqual(metrics["errors"], 1)

if __name__ == '__main__':
    unittest.main()
