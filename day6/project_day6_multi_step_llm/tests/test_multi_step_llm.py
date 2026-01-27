import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_metrics_file_creation():
    """Test that metrics file can be created"""
    metrics_file = "metrics.json"
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(test_dir, metrics_file)
    
    # Remove if exists
    if os.path.exists(metrics_path):
        os.remove(metrics_path)
    
    test_metrics = {
        "total_requests": 0,
        "successful_processing": 0,
        "failed_processing": 0,
        "step1_summaries": 0,
        "step2_rewrites": 0,
        "step3_keywords": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0.0,
        "last_request_time": None,
        "requests": []
    }
    
    with open(metrics_path, 'w') as f:
        json.dump(test_metrics, f)
    
    assert os.path.exists(metrics_path)
    
    with open(metrics_path, 'r') as f:
        loaded = json.load(f)
        assert loaded["total_requests"] == 0
        assert loaded["step1_summaries"] == 0
        assert loaded["step2_rewrites"] == 0
        assert loaded["step3_keywords"] == 0

def test_sample_article_exists():
    """Test that sample article file exists"""
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    article_path = os.path.join(test_dir, "sample_article.txt")
    assert os.path.exists(article_path), "sample_article.txt should exist"
    
    with open(article_path, 'r') as f:
        content = f.read()
        assert len(content) > 0, "sample_article.txt should not be empty"

def test_metrics_structure():
    """Test that metrics structure is correct"""
    metrics_file = "metrics.json"
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(test_dir, metrics_file)
    
    if os.path.exists(metrics_path):
        with open(metrics_path, 'r') as f:
            metrics = json.load(f)
            assert "total_requests" in metrics
            assert "successful_processing" in metrics
            assert "failed_processing" in metrics
            assert "step1_summaries" in metrics
            assert "step2_rewrites" in metrics
            assert "step3_keywords" in metrics
            assert "average_latency_ms" in metrics
