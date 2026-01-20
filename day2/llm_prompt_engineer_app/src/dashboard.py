#!/usr/bin/env python3
"""
Dashboard server for LLM Prompt Engineering Demo
Tracks metrics and displays them in a web interface
"""
import os
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Metrics storage
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_tokens": 0,
    "zero_shot_requests": 0,
    "few_shot_requests": 0,
    "last_request_time": None,
    "requests": []
}

def update_metrics(response_data=None, success=True, tokens=0, request_type=None):
    """Update metrics with new request data"""
    metrics["total_requests"] += 1
    if success:
        metrics["successful_requests"] += 1
        metrics["total_tokens"] += tokens
    else:
        metrics["failed_requests"] += 1
    
    # Track request types regardless of success/failure
    if request_type == "zero_shot":
        metrics["zero_shot_requests"] += 1
    elif request_type == "few_shot":
        metrics["few_shot_requests"] += 1
    metrics["last_request_time"] = datetime.now().isoformat()
    if response_data:
        metrics["requests"].append({
            "time": datetime.now().isoformat(),
            "success": success,
            "tokens": tokens,
            "type": request_type or "unknown",
            "data": response_data
        })
    # Keep only last 50 requests
    if len(metrics["requests"]) > 50:
        metrics["requests"] = metrics["requests"][-50:]

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif parsed_path.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(metrics, indent=2).encode())
        elif parsed_path.path == '/update':
            # Update metrics endpoint
            query_params = parse_qs(parsed_path.query)
            success = query_params.get('success', ['true'])[0].lower() == 'true'
            tokens = int(query_params.get('tokens', ['0'])[0])
            request_type = query_params.get('type', [None])[0]
            update_metrics(success=success, tokens=tokens, request_type=request_type)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updated"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_dashboard_html(self):
        success_rate = 0
        if metrics["total_requests"] > 0:
            success_rate = (metrics["successful_requests"] / metrics["total_requests"]) * 100
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LLM Prompt Engineering Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        }}
        .metric-card.error {{
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .status {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .last-update {{
            text-align: right;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>LLM Prompt Engineering Dashboard</h1>
        <div class="status">
            <strong>Status:</strong> {"Active" if metrics["total_requests"] > 0 else "Waiting for requests"}
        </div>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{metrics['total_requests']}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Successful</div>
                <div class="metric-value">{metrics['successful_requests']}</div>
            </div>
            <div class="metric-card error">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{metrics['failed_requests']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{success_rate:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{metrics['total_tokens']}</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Zero-Shot Requests</div>
                <div class="metric-value">{metrics['zero_shot_requests']}</div>
            </div>
            <div class="metric-card warning">
                <div class="metric-label">Few-Shot Requests</div>
                <div class="metric-value">{metrics['few_shot_requests']}</div>
            </div>
        </div>
        <div class="last-update">
            Last Request: {metrics['last_request_time'] or 'Never'}
            <br>Auto-refresh: Every 5 seconds
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_dashboard_server(port=8080):
    """Start the dashboard server"""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Dashboard server starting on http://0.0.0.0:{port}")
    print(f"Metrics API: http://localhost:{port}/metrics")
    import signal
    import sys
    def signal_handler(sig, frame):
        print("\\nShutting down dashboard server...")
        server.shutdown()
        sys.exit(0)
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down dashboard server...")
        server.shutdown()

if __name__ == "__main__":
    import sys
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_dashboard_server(port)
