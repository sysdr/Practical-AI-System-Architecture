import pytest
import os
import json
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_metrics_file_structure():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    metrics_path = os.path.join(project_dir, "metrics.json")
    assert os.path.exists(metrics_path), "metrics.json should exist"
    with open(metrics_path) as f:
        data = json.load(f)
    assert "total_messages_sent" in data
    assert "total_messages_received" in data
    assert "total_conversations" in data
    assert "last_activity" in data

def test_dashboard_load_metrics():
    project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    sys.path.insert(0, project_dir)
    import dashboard
    m = dashboard.load_metrics()
    assert isinstance(m, dict)
    assert "total_messages_sent" in m
    assert "total_messages_received" in m
