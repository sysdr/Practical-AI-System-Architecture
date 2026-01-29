import json
import os
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LLM Cost Tracker Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }
        .container { max-width: 1200px; margin: 0 auto; background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        h1 { color: #333; text-align: center; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 20px; margin: 20px 0; }
        .metric-card { background: linear-gradient(135deg, #0d9488 0%, #0f766e 50%, #134e4a 100%); color: white; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-card h3 { margin: 0 0 10px 0; font-size: 14px; opacity: 0.9; }
        .metric-value { font-size: 28px; font-weight: bold; margin: 10px 0; }
        .metric-label { font-size: 12px; opacity: 0.8; }
        .refresh-btn { background: #4CAF50; color: white; border: none; padding: 10px 20px; border-radius: 4px; cursor: pointer; font-size: 16px; margin: 10px 5px; }
        .refresh-btn:hover { background: #45a049; }
        .auto-refresh { margin: 20px 0; text-align: center; }
        .status { text-align: center; padding: 10px; margin: 10px 0; border-radius: 4px; }
        .status.active { background: #d4edda; color: #155724; }
        table { width: 100%; border-collapse: collapse; margin-top: 20px; }
        th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
        th { background-color: #0d9488; color: white; }
        tr:hover { background-color: #f5f5f5; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LLM Cost Tracker Dashboard</h1>
        <div class="status active" id="status">Status: Active</div>
        <div class="auto-refresh">
            <button class="refresh-btn" id="refreshBtn" onclick="loadMetrics()">Refresh Metrics</button>
            <span id="lastUpdated" class="metric-label" style="margin-left: 15px;"></span>
            <label style="margin-left: 20px;"><input type="checkbox" id="autoRefresh" checked> Auto-refresh every 5s</label>
        </div>
        <div class="metrics-grid" id="metricsGrid"></div>
        <h2>Recent Requests</h2>
        <table id="requestsTable">
            <thead>
                <tr>
                    <th>Timestamp</th>
                    <th>Model</th>
                    <th>Input Tokens</th>
                    <th>Output Tokens</th>
                    <th>Cost</th>
                </tr>
            </thead>
            <tbody id="requestsBody"></tbody>
        </table>
    </div>
    <script>
        let autoRefreshInterval = null;
        const REFRESH_INTERVAL_MS = 5000;

        function formatNumber(num) {
            if (num === null || num === undefined) return '0';
            return typeof num === 'number' ? num.toLocaleString('en-US', {maximumFractionDigits: 4}) : num;
        }

        function setLastUpdated() {
            var el = document.getElementById('lastUpdated');
            if (el) el.textContent = 'Last updated: ' + new Date().toLocaleTimeString();
        }

        function loadMetrics() {
            var btn = document.getElementById('refreshBtn');
            if (btn) { btn.disabled = true; btn.textContent = 'Refreshing...'; }
            fetch('/api/metrics?t=' + new Date().getTime(), { cache: 'no-store', headers: { 'Cache-Control': 'no-cache', 'Pragma': 'no-cache' } })
                .then(function(response) {
                    if (!response.ok) throw new Error('HTTP ' + response.status);
                    return response.json();
                })
                .then(function(data) {
                    if (!data || !data.metrics) throw new Error('Invalid metrics response');
                    var m = data.metrics;
                    document.getElementById('metricsGrid').innerHTML =
                        '<div class="metric-card"><h3>Total Prompts</h3><div class="metric-value">' + formatNumber(m.total_prompts) + '</div><div class="metric-label">Processed</div></div>' +
                        '<div class="metric-card"><h3>Total Input Tokens</h3><div class="metric-value">' + formatNumber(m.total_input_tokens) + '</div><div class="metric-label">Tokens</div></div>' +
                        '<div class="metric-card"><h3>Total Output Tokens</h3><div class="metric-value">' + formatNumber(m.total_output_tokens) + '</div><div class="metric-label">Tokens</div></div>' +
                        '<div class="metric-card"><h3>Total Estimated Cost</h3><div class="metric-value">$' + formatNumber(m.total_estimated_cost) + '</div><div class="metric-label">USD</div></div>' +
                        '<div class="metric-card"><h3>Last Request</h3><div class="metric-value" style="font-size: 14px;">' + (m.last_request_time ? new Date(m.last_request_time).toLocaleString() : 'Never') + '</div><div class="metric-label">Most Recent</div></div>';
                    var recent = (m.requests || []).slice(-20).reverse();
                    var tbody = document.getElementById('requestsBody');
                    if (recent.length === 0) {
                        tbody.innerHTML = '<tr><td colspan="5" style="text-align: center;">No requests yet. Run the demo to see data.</td></tr>';
                    } else {
                        tbody.innerHTML = recent.map(function(r) {
                            return '<tr><td>' + new Date(r.timestamp).toLocaleString() + '</td><td>' + (r.model_used || '-') + '</td><td>' + formatNumber(r.input_tokens) + '</td><td>' + formatNumber(r.output_tokens) + '</td><td>$' + formatNumber(r.estimated_cost) + '</td></tr>';
                        }).join('');
                    }
                    setLastUpdated();
                    document.getElementById('status').textContent = 'Status: Active';
                    document.getElementById('status').className = 'status active';
                })
                .catch(function(err) {
                    console.error('Error loading metrics:', err);
                    document.getElementById('status').textContent = 'Status: Error - ' + err.message;
                    document.getElementById('status').className = 'status';
                })
                .finally(function() {
                    if (btn) { btn.disabled = false; btn.textContent = 'Refresh Metrics'; }
                });
        }

        function toggleAutoRefresh() {
            if (autoRefreshInterval) { clearInterval(autoRefreshInterval); autoRefreshInterval = null; }
            if (document.getElementById('autoRefresh').checked) {
                autoRefreshInterval = setInterval(loadMetrics, REFRESH_INTERVAL_MS);
            }
        }

        loadMetrics();
        toggleAutoRefresh();
        document.getElementById('autoRefresh').addEventListener('change', toggleAutoRefresh);
    </script>
</body>
</html>
"""

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "total_prompts": 0,
        "total_input_tokens": 0,
        "total_output_tokens": 0,
        "total_estimated_cost": 0.0,
        "last_request_time": None,
        "requests": []
    }

@app.route('/')
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route('/api/metrics')
def get_metrics():
    metrics = load_metrics()
    response = jsonify({"metrics": metrics})
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/update')
def update_metrics():
    return jsonify({"status": "ok"})

if __name__ == '__main__':
    print("Starting LLM Cost Tracker Dashboard on http://localhost:5000")
    app.run(host='0.0.0.0', port=5000, debug=False)
