import json
import os
from datetime import datetime as dt
from flask import Flask, jsonify, render_template_string
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

DEMO_QUESTIONS = [
    ("Who won the 2023 Nobel Prize in Physics?", "Attosecond physics: L'Huillier, Agostini, Krausz."),
    ("What is LLM hallucination?", "When the model generates plausible but incorrect or fabricated information."),
    ("Why does RAG help?", "RAG grounds the LLM in retrieved documents, reducing hallucination."),
]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>RAG Imperative - Hallucination Demo Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1000px; margin: 0 auto; background: #16213e; padding: 24px; border-radius: 12px; }
        h1 { color: #e94560; text-align: center; }
        h2 { color: #a2d2f0; font-size: 1.1em; margin: 24px 0 12px 0; border-bottom: 1px solid #0f3460; padding-bottom: 6px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; }
        .metric-card { background: #0f3460; color: #eee; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: bold; color: #e94560; }
        .refresh-btn { background: #e94560; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin: 10px 5px; }
        .op-btn { background: #0f766e; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; margin: 6px 6px 6px 0; font-size: 14px; }
        .status { text-align: center; padding: 8px; margin: 10px 0; border-radius: 4px; background: #0f3460; }
        .info-box { background: #0f3460; padding: 16px; border-radius: 8px; margin: 16px 0; font-size: 14px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>RAG Imperative - Hallucination Demo Dashboard</h1>
        <div class="info-box">
            <strong>Day 11</strong>: This demo shows LLM hallucination. Metrics: questions asked, responses, last activity. Run the demo or use buttons below to update metrics.
        </div>
        <h2>Live metrics</h2>
        <div class="status" id="status">Status: Active</div>
        <button class="refresh-btn" id="refreshBtn" onclick="loadMetrics()">Refresh Metrics</button>
        <span id="lastUpdated" style="margin-left: 15px; font-size: 12px;"></span>
        <div class="metrics-grid" id="metricsGrid"></div>
        <h2>Operations (update metrics)</h2>
        <button class="op-btn" onclick="runOp('simulate-question')">Simulate 1 question</button>
        <button class="op-btn" onclick="runOp('demo-batch')">Send 3 demo questions</button>
        <span id="opFeedback" style="font-size: 12px; color: #0d9488; margin-left: 10px;"></span>
    </div>
    <script>
        var refreshIntervalId = null;
        function loadMetrics() {
            var btn = document.getElementById('refreshBtn');
            if (btn) { btn.disabled = true; btn.textContent = 'Refreshing...'; }
            fetch('/api/metrics?t=' + new Date().getTime(), { cache: 'no-store' })
                .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
                .then(function(data) {
                    if (!data || !data.metrics) throw new Error('Invalid response');
                    if (refreshIntervalId) clearInterval(refreshIntervalId);
                    refreshIntervalId = setInterval(loadMetrics, 5000);
                    var m = data.metrics;
                    document.getElementById('metricsGrid').innerHTML =
                        '<div class="metric-card"><div>Questions Asked</div><div class="metric-value">' + (m.total_questions_asked || 0) + '</div></div>' +
                        '<div class="metric-card"><div>Responses</div><div class="metric-value">' + (m.total_responses || 0) + '</div></div>' +
                        '<div class="metric-card"><div>Last Activity</div><div class="metric-value" style="font-size:14px">' + (m.last_activity ? new Date(m.last_activity).toLocaleString() : 'Never') + '</div></div>';
                    document.getElementById('lastUpdated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
                    document.getElementById('status').textContent = 'Status: Active';
                })
                .catch(function(err) {
                    document.getElementById('status').textContent = 'Dashboard not running. Run: ./startup.sh or ./start_dashboard.sh';
                    document.getElementById('status').style.background = '#4a1515';
                    document.getElementById('metricsGrid').innerHTML = '<div class="metric-card" style="grid-column:1/-1">Start dashboard from project dir: ./start_dashboard.sh or ./startup.sh</div>';
                    if (refreshIntervalId) { clearInterval(refreshIntervalId); refreshIntervalId = null; }
                })
                .finally(function() { if (btn) { btn.disabled = false; btn.textContent = 'Refresh Metrics'; } });
        }
        function runOp(op) {
            var feedback = document.getElementById('opFeedback');
            feedback.textContent = 'Running...';
            fetch('/api/op/' + op, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
                .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
                .then(function(data) { feedback.textContent = data.message || 'Done.'; loadMetrics(); setTimeout(function() { feedback.textContent = ''; }, 3000); })
                .catch(function(err) { feedback.textContent = 'Error: ' + err.message; });
        }
        loadMetrics();
        refreshIntervalId = setInterval(loadMetrics, 5000);
    </script>
</body>
</html>
"""

def load_metrics():
    if os.path.exists(METRICS_FILE):
        try:
            with open(METRICS_FILE, "r") as f:
                return json.load(f)
        except Exception:
            pass
    return {"total_questions_asked": 0, "total_responses": 0, "last_activity": None, "questions": []}

def save_metrics(metrics):
    with open(METRICS_FILE, "w") as f:
        json.dump(metrics, f, indent=2)

@app.route("/")
def dashboard():
    return render_template_string(DASHBOARD_HTML)

@app.route("/api/metrics")
def get_metrics():
    m = load_metrics()
    r = jsonify({"metrics": m})
    r.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    return r

@app.route("/api/op/simulate-question", methods=["POST"])
def op_simulate_question():
    metrics = load_metrics()
    metrics["total_questions_asked"] = metrics.get("total_questions_asked", 0) + 1
    metrics["total_responses"] = metrics.get("total_responses", 0) + 1
    metrics["last_activity"] = dt.now().isoformat()
    metrics.setdefault("questions", []).append({"timestamp": metrics["last_activity"], "question_preview": "Simulated", "response_preview": "Demo"})
    if len(metrics["questions"]) > 100:
        metrics["questions"] = metrics["questions"][-100:]
    save_metrics(metrics)
    return jsonify({"ok": True, "message": "1 question simulated. Metrics updated."})

@app.route("/api/op/demo-batch", methods=["POST"])
def op_demo_batch():
    metrics = load_metrics()
    for q, a in DEMO_QUESTIONS:
        metrics["total_questions_asked"] = metrics.get("total_questions_asked", 0) + 1
        metrics["total_responses"] = metrics.get("total_responses", 0) + 1
        metrics["last_activity"] = dt.now().isoformat()
        metrics.setdefault("questions", []).append({"timestamp": metrics["last_activity"], "question_preview": q[:80], "response_preview": a[:80]})
    if len(metrics["questions"]) > 100:
        metrics["questions"] = metrics["questions"][-100:]
    save_metrics(metrics)
    return jsonify({"ok": True, "message": "3 demo questions sent. Metrics updated."})

if __name__ == "__main__":
    print("Dashboard: http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
