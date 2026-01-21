# filename: dashboard.py
import json
import os
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

METRICS_FILE = "metrics.json"

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM Switcher Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .metrics-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }
        .metric-card {
            background: linear-gradient(135deg, #be75ff 0%, #be75ff 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }
        .metric-card h3 {
            margin: 0 0 10px 0;
            font-size: 14px;
            opacity: 0.9;
        }
        .metric-value {
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }
        .metric-label {
            font-size: 12px;
            opacity: 0.8;
        }
        .refresh-btn {
            background: #4CAF50;
            color: white;
            border: none;
            padding: 10px 20px;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px;
        }
        .refresh-btn:hover {
            background: #45a049;
        }
        .auto-refresh {
            margin: 20px 0;
            text-align: center;
        }
        .status {
            text-align: center;
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
        }
        .status.active {
            background: #d4edda;
            color: #155724;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        th {
            background-color: #667eea;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LLM Switcher Dashboard</h1>
        <div class="status active" id="status">Status: Active</div>
        <div class="auto-refresh">
            <button class="refresh-btn" onclick="loadMetrics()">Refresh Metrics</button>
            <label>
                <input type="checkbox" id="autoRefresh" checked onchange="toggleAutoRefresh()"> Auto-refresh (3s)
            </label>
        </div>
        <div class="metrics-grid" id="metricsGrid">
            <!-- Metrics will be loaded here -->
        </div>
        <h2>Recent Requests</h2>
        <table id="requestsTable">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Provider</th>
                    <th>Latency (ms)</th>
                    <th>Status</th>
                </tr>
            </thead>
            <tbody id="requestsBody">
                <!-- Requests will be loaded here -->
            </tbody>
        </table>
    </div>
    <script>
        let autoRefreshInterval = null;
        
        function formatNumber(num) {
            if (num === null || num === undefined) return '0';
            return typeof num === 'number' ? num.toLocaleString('en-US', {maximumFractionDigits: 2}) : num;
        }
        
        function loadMetrics() {
            // Add cache-busting parameter to ensure fresh data
            fetch('/api/metrics?t=' + new Date().getTime())
                .then(response => response.json())
                .then(data => {
                    const metrics = data.metrics;
                    const avgLatency = metrics.total_requests > 0 
                        ? (metrics.total_latency_ms / metrics.total_requests).toFixed(2) 
                        : '0.00';
                    const avgOpenAILatency = metrics.openai_requests > 0 
                        ? (metrics.openai_latency_ms / metrics.openai_requests).toFixed(2) 
                        : '0.00';
                    const avgAnthropicLatency = metrics.anthropic_requests > 0 
                        ? (metrics.anthropic_latency_ms / metrics.anthropic_requests).toFixed(2) 
                        : '0.00';
                    
                    document.getElementById('metricsGrid').innerHTML = `
                        <div class="metric-card">
                            <h3>Total Requests</h3>
                            <div class="metric-value">${formatNumber(metrics.total_requests)}</div>
                            <div class="metric-label">All Providers</div>
                        </div>
                        <div class="metric-card">
                            <h3>OpenAI Requests</h3>
                            <div class="metric-value">${formatNumber(metrics.openai_requests)}</div>
                            <div class="metric-label">Avg Latency: ${avgOpenAILatency}ms</div>
                        </div>
                        <div class="metric-card">
                            <h3>Anthropic Requests</h3>
                            <div class="metric-value">${formatNumber(metrics.anthropic_requests)}</div>
                            <div class="metric-label">Avg Latency: ${avgAnthropicLatency}ms</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Latency</h3>
                            <div class="metric-value">${avgLatency}ms</div>
                            <div class="metric-label">All Requests</div>
                        </div>
                        <div class="metric-card">
                            <h3>Total Errors</h3>
                            <div class="metric-value">${formatNumber(metrics.errors)}</div>
                            <div class="metric-label">Failed Requests</div>
                        </div>
                        <div class="metric-card">
                            <h3>Last Request</h3>
                            <div class="metric-value" style="font-size: 16px;">${metrics.last_request_time ? new Date(metrics.last_request_time).toLocaleString() : 'Never'}</div>
                            <div class="metric-label">Most Recent</div>
                        </div>
                    `;
                    
                    // Update requests table
                    const requestsBody = document.getElementById('requestsBody');
                    const recentRequests = metrics.requests.slice(-20).reverse();
                    if (recentRequests.length === 0) {
                        requestsBody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No requests yet</td></tr>';
                    } else {
                        requestsBody.innerHTML = recentRequests.map(req => `
                            <tr>
                                <td>${new Date(req.timestamp).toLocaleString()}</td>
                                <td>${req.provider.toUpperCase()}</td>
                                <td>${req.latency_ms.toFixed(2)}</td>
                                <td>${req.success ? '✅ Success' : '❌ Error'}</td>
                            </tr>
                        `).join('');
                    }
                })
                .catch(error => {
                    console.error('Error loading metrics:', error);
                    document.getElementById('status').textContent = 'Status: Error loading metrics';
                    document.getElementById('status').className = 'status';
                });
        }
        
        function toggleAutoRefresh() {
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox.checked) {
                // Clear any existing interval
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                }
                // Start auto-refresh every 3 seconds
                autoRefreshInterval = setInterval(loadMetrics, 3000);
            } else {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }
        }
        
        // Load metrics on page load
        loadMetrics();
        // Enable auto-refresh by default
        document.addEventListener('DOMContentLoaded', function() {
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox && checkbox.checked) {
                toggleAutoRefresh();
            }
        });
    </script>
</body>
</html>
"""

def load_metrics():
    """Load metrics from JSON file."""
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {
                "total_requests": 0,
                "openai_requests": 0,
                "anthropic_requests": 0,
                "total_latency_ms": 0,
                "openai_latency_ms": 0,
                "anthropic_latency_ms": 0,
                "errors": 0,
                "last_request_time": None,
                "requests": []
            }
    return {
        "total_requests": 0,
        "openai_requests": 0,
        "anthropic_requests": 0,
        "total_latency_ms": 0,
        "openai_latency_ms": 0,
        "anthropic_latency_ms": 0,
        "errors": 0,
        "last_request_time": None,
        "requests": []
    }

@app.route('/')
def dashboard():
    """Serve the dashboard HTML."""
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get metrics."""
    # Disable caching to ensure fresh data
    metrics = load_metrics()
    response = jsonify({"metrics": metrics})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

if __name__ == '__main__':
    print("Starting LLM Switcher Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
