#!/usr/bin/env python3
"""
Dashboard server for LLM Context Analysis Demo
"""
import json
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Lock
from urllib.parse import urlparse, parse_qs

# Global metrics storage
metrics = {
    "total_token_count_operations": 0,
    "total_tokens_counted": 0,
    "total_context_window_simulations": 0,
    "total_context_overflow_events": 0,
    "total_tokens_truncated": 0,
    "total_context_utilization": 0.0,
    "average_chars_per_token": 0.0,
    "last_update_time": time.time()
}

metrics_lock = Lock()

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif parsed_path.path == "/metrics":
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            with metrics_lock:
                self.wfile.write(json.dumps(metrics).encode())
        elif parsed_path.path == "/update":
            query_params = parse_qs(parsed_path.query)
            with metrics_lock:
                if "tokens" in query_params:
                    tokens = int(query_params["tokens"][0])
                    metrics["total_tokens_counted"] += tokens
                    metrics["total_token_count_operations"] += 1
                if "context_simulation" in query_params:
                    metrics["total_context_window_simulations"] += 1
                if "overflow" in query_params:
                    metrics["total_context_overflow_events"] += 1
                if "truncated_tokens" in query_params:
                    metrics["total_tokens_truncated"] += int(query_params["truncated_tokens"][0])
                if "context_used" in query_params and "context_size" in query_params:
                    context_used = int(query_params["context_used"][0])
                    context_size = int(query_params["context_size"][0])
                    utilization = (context_used / context_size) * 100 if context_size > 0 else 0
                    metrics["total_context_utilization"] = utilization
                if "chars" in query_params and "tokens" in query_params:
                    chars = int(query_params["chars"][0])
                    tokens = int(query_params["tokens"][0])
                    if tokens > 0:
                        metrics["average_chars_per_token"] = chars / tokens
                metrics["last_update_time"] = time.time()
            self.send_response(200)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"OK")
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress default logging

    def get_dashboard_html(self):
        with metrics_lock:
            m = metrics.copy()
        
        avg_tokens_per_op = (m["total_tokens_counted"] / m["total_token_count_operations"]) if m["total_token_count_operations"] > 0 else 0
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LLM Context Analysis Dashboard</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: #333;
            padding: 20px;
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
        h1 {{
            text-align: center;
            color: white;
            margin-bottom: 30px;
            font-size: 2.5em;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .metric-card {{
            background: white;
            border-radius: 10px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            transition: transform 0.2s;
        }}
        .metric-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0,0,0,0.15);
        }}
        .metric-label {{
            font-size: 0.9em;
            color: #666;
            margin-bottom: 10px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        .metric-value {{
            font-size: 2em;
            font-weight: bold;
            color: #667eea;
        }}
        .metric-unit {{
            font-size: 0.6em;
            color: #999;
            margin-left: 5px;
        }}
        .status {{
            text-align: center;
            color: white;
            padding: 10px;
            background: rgba(255,255,255,0.2);
            border-radius: 5px;
            margin-top: 20px;
        }}
        .refresh-info {{
            text-align: center;
            color: rgba(255,255,255,0.8);
            margin-top: 10px;
            font-size: 0.9em;
        }}
    </style>
    <script>
        function updateMetrics() {{
            fetch('/metrics')
                .then(response => {{
                    if (!response.ok) {{
                        throw new Error('Network response was not ok');
                    }}
                    return response.json();
                }})
                .then(data => {{
                    if (data) {{
                        document.getElementById('total-operations').textContent = data.total_token_count_operations || 0;
                        document.getElementById('total-tokens').textContent = data.total_tokens_counted || 0;
                        document.getElementById('total-simulations').textContent = data.total_context_window_simulations || 0;
                        document.getElementById('total-overflows').textContent = data.total_context_overflow_events || 0;
                        document.getElementById('total-truncated').textContent = data.total_tokens_truncated || 0;
                        document.getElementById('context-utilization').textContent = (data.total_context_utilization || 0).toFixed(2);
                        document.getElementById('avg-chars-token').textContent = (data.average_chars_per_token || 0).toFixed(2);
                        if (data.last_update_time) {{
                            const lastUpdate = new Date(data.last_update_time * 1000);
                            document.getElementById('last-update').textContent = lastUpdate.toLocaleTimeString();
                        }}
                    }}
                }})
                .catch(error => {{
                    console.error('Error fetching metrics:', error);
                }});
        }}
        // Update immediately on load
        updateMetrics();
        // Then update every second
        setInterval(updateMetrics, 1000);
    </script>
</head>
<body>
    <div class="container">
        <h1>LLM Context Analysis Dashboard</h1>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Token Count Operations</div>
                <div class="metric-value"><span id="total-operations">0</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens Counted</div>
                <div class="metric-value"><span id="total-tokens">0</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Context Simulations</div>
                <div class="metric-value"><span id="total-simulations">0</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Context Overflows</div>
                <div class="metric-value"><span id="total-overflows">0</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Tokens Truncated</div>
                <div class="metric-value"><span id="total-truncated">0</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Context Utilization</div>
                <div class="metric-value"><span id="context-utilization">0.00</span><span class="metric-unit">%</span></div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Avg Chars/Token</div>
                <div class="metric-value"><span id="avg-chars-token">0.00</span></div>
            </div>
        </div>
        <div class="status">
            <div>Last Update: <span id="last-update">--</span></div>
        </div>
        <div class="refresh-info">Dashboard auto-refreshes every second</div>
    </div>
</body>
</html>"""

def start_dashboard_server(port=8080):
    """Start the dashboard server"""
    server = HTTPServer(('0.0.0.0', port), DashboardHandler)
    print(f"Dashboard server starting on http://0.0.0.0:{port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\\nShutting down dashboard server...")
        server.shutdown()
    except Exception as e:
        print(f"Error: {e}")
        print("\\nShutting down dashboard server...")
        server.shutdown()

if __name__ == "__main__":
    import sys
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8080
    start_dashboard_server(port)
