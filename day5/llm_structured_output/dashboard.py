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
    <title>LLM Structured Output Dashboard</title>
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
            background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
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
            background-color: #2ecc71;
            color: white;
        }
        tr:hover {
            background-color: #f5f5f5;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LLM Structured Output Dashboard</h1>
        <div class="status active" id="status">Status: Active</div>
        <div class="auto-refresh">
            <button class="refresh-btn" onclick="loadMetrics()">Refresh Metrics</button>
            <label>
                <input type="checkbox" id="autoRefresh" checked onchange="toggleAutoRefresh()"> Auto-refresh (2s)
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
            // Add timestamp to prevent caching
            const timestamp = new Date().getTime();
            fetch('/api/metrics?t=' + timestamp, {
                cache: 'no-cache',
                headers: {
                    'Cache-Control': 'no-cache',
                    'Pragma': 'no-cache'
                }
            })
                .then(response => {
                    if (!response.ok) {
                        throw new Error('Network response was not ok');
                    }
                    return response.json();
                })
                .then(data => {
                    const metrics = data.metrics;
                    
                    document.getElementById('metricsGrid').innerHTML = `
                        <div class="metric-card">
                            <h3>Total Requests</h3>
                            <div class="metric-value">${formatNumber(metrics.total_requests)}</div>
                            <div class="metric-label">All Requests</div>
                        </div>
                        <div class="metric-card">
                            <h3>Successful Extractions</h3>
                            <div class="metric-value">${formatNumber(metrics.successful_extractions)}</div>
                            <div class="metric-label">Valid Products</div>
                        </div>
                        <div class="metric-card">
                            <h3>Failed Extractions</h3>
                            <div class="metric-value">${formatNumber(metrics.failed_extractions)}</div>
                            <div class="metric-label">Errors</div>
                        </div>
                        <div class="metric-card">
                            <h3>Validation Errors</h3>
                            <div class="metric-value">${formatNumber(metrics.validation_errors)}</div>
                            <div class="metric-label">Schema Mismatches</div>
                        </div>
                        <div class="metric-card">
                            <h3>Average Latency</h3>
                            <div class="metric-value">${formatNumber(metrics.average_latency_ms)}ms</div>
                            <div class="metric-label">Response Time</div>
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
                        requestsBody.innerHTML = '<tr><td colspan="3" style="text-align: center;">No requests yet</td></tr>';
                    } else {
                        requestsBody.innerHTML = recentRequests.map(req => `
                            <tr>
                                <td>${new Date(req.timestamp).toLocaleString()}</td>
                                <td>${req.latency_ms.toFixed(2)}</td>
                                <td>${req.success ? '✅ Success' : (req.validation_error ? '❌ Validation Error' : '❌ Error')}</td>
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
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                }
                // Refresh every 2 seconds for more real-time updates
                autoRefreshInterval = setInterval(loadMetrics, 2000);
            } else {
                if (autoRefreshInterval) {
                    clearInterval(autoRefreshInterval);
                    autoRefreshInterval = null;
                }
            }
        }
        
        // Load metrics on page load
        loadMetrics();
        // Start auto-refresh immediately
        document.addEventListener('DOMContentLoaded', function() {
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox && checkbox.checked) {
                toggleAutoRefresh();
            } else {
                // Force enable auto-refresh if checkbox exists
                if (checkbox) {
                    checkbox.checked = true;
                    toggleAutoRefresh();
                }
            }
        });
        
        // Also start auto-refresh if DOM is already loaded
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', function() {
                const checkbox = document.getElementById('autoRefresh');
                if (checkbox) {
                    checkbox.checked = true;
                    toggleAutoRefresh();
                }
            });
        } else {
            // DOM already loaded, start immediately
            const checkbox = document.getElementById('autoRefresh');
            if (checkbox) {
                checkbox.checked = true;
                toggleAutoRefresh();
            }
        }
    </script>
</body>
</html>
"""

def load_metrics():
    """Load metrics from JSON file. Always reads fresh from disk."""
    if os.path.exists(METRICS_FILE):
        try:
            # Force fresh read by closing and reopening
            with open(METRICS_FILE, 'r') as f:
                content = f.read()
                return json.loads(content)
        except (json.JSONDecodeError, IOError) as e:
            # If file is being written, return default
            pass
    return {
        "total_requests": 0,
        "successful_extractions": 0,
        "failed_extractions": 0,
        "validation_errors": 0,
        "total_latency_ms": 0,
        "average_latency_ms": 0.0,
        "last_request_time": None,
        "requests": []
    }

@app.route('/')
def dashboard():
    """Serve the dashboard HTML."""
    response = app.make_response(render_template_string(DASHBOARD_HTML))
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/api/metrics')
def get_metrics():
    """API endpoint to get metrics."""
    metrics = load_metrics()
    response = jsonify({"metrics": metrics})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/update')
def update_metrics():
    """API endpoint to trigger metrics refresh (for compatibility)."""
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting LLM Structured Output Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
