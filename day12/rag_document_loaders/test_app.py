import os
import sys
import json
import pytest

# Add project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import init_metrics, save_metrics, load_metrics, run_document_loader_demo

class TestMetrics:
    """Test metrics functionality"""
    
    def test_init_metrics(self):
        """Test that init_metrics returns correct structure"""
        metrics = init_metrics()
        assert "text_documents_loaded" in metrics
        assert "pdf_documents_loaded" in metrics
        assert "web_documents_loaded" in metrics
        assert "total_documents_loaded" in metrics
        assert metrics["total_documents_loaded"] == 0
    
    def test_save_and_load_metrics(self, tmp_path):
        """Test saving and loading metrics"""
        # Change to temp directory
        original_dir = os.getcwd()
        os.chdir(tmp_path)
        
        try:
            metrics = init_metrics()
            metrics["text_documents_loaded"] = 5
            metrics["total_documents_loaded"] = 10
            
            saved = save_metrics(metrics)
            assert saved["last_update"] is not None
            
            loaded = load_metrics()
            assert loaded["text_documents_loaded"] == 5
            assert loaded["total_documents_loaded"] == 10
        finally:
            os.chdir(original_dir)

class TestDocumentLoader:
    """Test document loader functionality"""
    
    def test_demo_runs_successfully(self):
        """Test that the demo runs and returns metrics"""
        metrics = run_document_loader_demo()
        
        assert metrics is not None
        assert "total_documents_loaded" in metrics
        assert "success_rate" in metrics
        # Should load at least some documents
        assert metrics["total_documents_loaded"] > 0
        
    def test_text_files_loaded(self):
        """Test that text files are loaded"""
        metrics = run_document_loader_demo()
        # We created 2 text files
        assert metrics["text_documents_loaded"] >= 1
        
    def test_pdf_files_loaded(self):
        """Test that PDF files are loaded"""
        metrics = run_document_loader_demo()
        # We created 1 PDF file
        assert metrics["pdf_documents_loaded"] >= 1
        
    def test_metrics_file_created(self):
        """Test that metrics file is created after demo"""
        run_document_loader_demo()
        assert os.path.exists("metrics.json")
        
        with open("metrics.json", 'r') as f:
            data = json.load(f)
        assert "last_update" in data

class TestDashboard:
    """Test dashboard functionality"""
    
    def test_dashboard_imports(self):
        """Test that dashboard can be imported"""
        import dashboard
        assert hasattr(dashboard, 'app')
        assert hasattr(dashboard, 'load_metrics')
    
    def test_health_endpoint(self):
        """Test health check endpoint"""
        import dashboard
        with dashboard.app.test_client() as client:
            response = client.get('/api/health')
            assert response.status_code == 200
            data = response.get_json()
            assert data['status'] == 'healthy'
    
    def test_metrics_endpoint(self):
        """Test metrics API endpoint"""
        import dashboard
        with dashboard.app.test_client() as client:
            response = client.get('/api/metrics')
            assert response.status_code == 200
            data = response.get_json()
            assert 'total_documents_loaded' in data

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
