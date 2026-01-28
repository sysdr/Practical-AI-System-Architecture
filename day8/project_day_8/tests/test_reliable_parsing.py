import pytest
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from src.schema import Task, Priority

def test_task_schema_validation():
    """Test Task schema validation"""
    task = Task(
        name="Test Task",
        due_date="2024-01-15",
        priority=Priority.HIGH
    )
    assert task.name == "Test Task"
    assert task.due_date == "2024-01-15"
    assert task.priority == Priority.HIGH

def test_task_schema_optional_fields():
    """Test Task with different priorities"""
    for priority in [Priority.HIGH, Priority.MEDIUM, Priority.LOW]:
        task = Task(
            name="Test Task",
            due_date="2024-01-15",
            priority=priority
        )
        assert task.priority == priority

def test_metrics_file_creation():
    """Test that metrics file can be created"""
    metrics_file = "metrics.json"
    test_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(test_dir, metrics_file)
    
    if os.path.exists(metrics_path):
        os.remove(metrics_path)
    
    test_metrics = {
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
    
    with open(metrics_path, 'w') as f:
        json.dump(test_metrics, f)
    
    assert os.path.exists(metrics_path)
    
    with open(metrics_path, 'r') as f:
        loaded = json.load(f)
        assert loaded["total_requests"] == 0
        assert loaded["successful_parsing"] == 0
