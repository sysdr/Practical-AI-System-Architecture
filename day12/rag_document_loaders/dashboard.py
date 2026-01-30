import os
import json
import subprocess
import signal
import sys
from flask import Flask, render_template, jsonify, request
from datetime import datetime

app = Flask(__name__)
METRICS_FILE = "metrics.json"

def load_metrics():
    """Load metrics from JSON file"""
    if os.path.exists(METRICS_FILE):
        with open(METRICS_FILE, 'r') as f:
            return json.load(f)
    return {
        "text_documents_loaded": 0,
        "pdf_documents_loaded": 0,
        "web_documents_loaded": 0,
        "total_documents_loaded": 0,
        "total_characters_processed": 0,
        "load_time_text_ms": 0,
        "load_time_pdf_ms": 0,
        "load_time_web_ms": 0,
        "total_load_time_ms": 0,
        "last_update": None,
        "errors": 0,
        "success_rate": 0.0,
        "documents_per_type": {"text": 0, "pdf": 0, "web": 0}
    }

@app.route('/')
def dashboard():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get current metrics"""
    metrics = load_metrics()
    return jsonify(metrics)

@app.route('/api/run-demo', methods=['POST'])
def run_demo():
    """API endpoint to run the document loader demo"""
    try:
        result = subprocess.run(
            ['python', 'app.py'],
            capture_output=True,
            text=True,
            timeout=120
        )
        metrics = load_metrics()
        return jsonify({
            "success": True,
            "output": result.stdout,
            "errors": result.stderr,
            "metrics": metrics
        })
    except subprocess.TimeoutExpired:
        return jsonify({"success": False, "error": "Demo timed out"}), 500
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "rag-document-loader-dashboard"
    })

def signal_handler(sig, frame):
    """Handle shutdown signals gracefully"""
    print("\nShutting down dashboard...")
    sys.exit(0)

if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    port = int(os.getenv('DASHBOARD_PORT', 5000))
    print(f"Starting RAG Document Loader Dashboard on http://localhost:{port}")
    app.run(host='0.0.0.0', port=port, debug=False)
