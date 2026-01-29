import json
import os
from datetime import datetime as dt
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
PROJECT_DIR = os.path.dirname(os.path.abspath(__file__))
METRICS_FILE = os.path.join(PROJECT_DIR, "metrics.json")

DEMO_MESSAGES = [
    ("What is LangChain?", "LangChain is a framework for building LLM-powered applications."),
    ("Explain conversation memory.", "ConversationBufferMemory stores the chat history for context."),
    ("How do I run the chatbot?", "Set OPENAI_API_KEY and run: python app.py"),
    ("What metrics are tracked?", "Messages sent/received, conversations, and last activity."),
    ("Tell me a short joke.", "Why did the chatbot go to school? To improve its learning!"),
]

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>LangChain Chatbot Dashboard</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 20px; background: #1a1a2e; color: #eee; }
        .container { max-width: 1000px; margin: 0 auto; background: #16213e; padding: 24px; border-radius: 12px; }
        h1 { color: #e94560; text-align: center; }
        h2 { color: #a2d2f0; font-size: 1.1em; margin: 24px 0 12px 0; border-bottom: 1px solid #0f3460; padding-bottom: 6px; }
        .metrics-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin: 20px 0; }
        .metric-card { background: #0f3460; color: #eee; padding: 20px; border-radius: 8px; text-align: center; }
        .metric-value { font-size: 28px; font-weight: bold; color: #e94560; }
        .refresh-btn { background: #e94560; color: white; border: none; padding: 10px 20px; border-radius: 6px; cursor: pointer; margin: 10px 5px; }
        .refresh-btn:hover { background: #c73e54; }
        .op-btn { background: #0f766e; color: white; border: none; padding: 10px 16px; border-radius: 6px; cursor: pointer; margin: 6px 6px 6px 0; font-size: 14px; }
        .op-btn:hover { background: #0d9488; }
        .op-btn:disabled { opacity: 0.6; cursor: not-allowed; }
        .status { text-align: center; padding: 8px; margin: 10px 0; border-radius: 4px; background: #0f3460; }
        .info-box { background: #0f3460; padding: 16px; border-radius: 8px; margin: 16px 0; font-size: 14px; line-height: 1.5; }
        .info-box strong { color: #e94560; }
        .ops-box { margin: 16px 0; }
        .op-feedback { font-size: 12px; color: #0d9488; margin-top: 8px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>LangChain Chatbot Dashboard</h1>

        <h2>About this project</h2>
        <div class="info-box">
            <strong>LangChain Chatbot</strong> is a conversational app built with LangChain and OpenAI. 
            The chatbot uses <strong>ConversationBufferMemory</strong> to keep context across turns. 
            This dashboard shows <strong>live metrics</strong>: messages sent/received, number of conversations, and last activity. 
            Use the operations below to simulate chat activity and watch the metrics update in real time.
        </div>

        <h2>Live metrics</h2>
        <div class="status" id="status">Status: Active</div>
        <button class="refresh-btn" id="refreshBtn" onclick="loadMetrics()">Refresh Metrics</button>
        <span id="lastUpdated" style="margin-left: 15px; font-size: 12px;"></span>
        <div class="metrics-grid" id="metricsGrid"></div>

        <h2>Operations (try these to update metrics)</h2>
        <div class="ops-box">
            <button class="op-btn" id="opMsg" onclick="runOp('simulate-message')">Simulate 1 message</button>
            <button class="op-btn" id="opConv" onclick="runOp('new-conversation')">Start new conversation</button>
            <button class="op-btn" id="opBatch" onclick="runOp('demo-batch')">Send 5 demo messages</button>
            <span class="op-feedback" id="opFeedback"></span>
        </div>
    </div>
    <script>
        var refreshIntervalId = null;
        var consecutiveFailures = 0;

        function loadMetrics() {
            var btn = document.getElementById('refreshBtn');
            if (btn) { btn.disabled = true; btn.textContent = 'Refreshing...'; }
            fetch('/api/metrics?t=' + new Date().getTime(), { cache: 'no-store' })
                .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
                .then(function(data) {
                    if (!data || !data.metrics) throw new Error('Invalid response');
                    consecutiveFailures = 0;
                    if (refreshIntervalId) { clearInterval(refreshIntervalId); }
                    refreshIntervalId = setInterval(loadMetrics, 5000);
                    var m = data.metrics;
                    document.getElementById('metricsGrid').innerHTML =
                        '<div class="metric-card"><div>Messages Sent</div><div class="metric-value">' + (m.total_messages_sent || 0) + '</div></div>' +
                        '<div class="metric-card"><div>Messages Received</div><div class="metric-value">' + (m.total_messages_received || 0) + '</div></div>' +
                        '<div class="metric-card"><div>Conversations</div><div class="metric-value">' + (m.total_conversations || 0) + '</div></div>' +
                        '<div class="metric-card"><div>Last Activity</div><div class="metric-value" style="font-size:14px">' + (m.last_activity ? new Date(m.last_activity).toLocaleString() : 'Never') + '</div></div>';
                    document.getElementById('lastUpdated').textContent = 'Updated: ' + new Date().toLocaleTimeString();
                    document.getElementById('status').textContent = 'Status: Active';
                })
                .catch(function(err) {
                    consecutiveFailures++;
                    document.getElementById('status').textContent = 'Cannot connect to server (ERR_CONNECTION_REFUSED). Start the dashboard: run ./startup.sh or ./start_dashboard.sh from the project directory.';
                    document.getElementById('status').style.background = '#4a1515';
                    document.getElementById('metricsGrid').innerHTML = '<div class="metric-card" style="grid-column:1/-1">Dashboard server not running. From terminal: <code>./start_dashboard.sh</code> or <code>./startup.sh</code></div>';
                    if (refreshIntervalId) { clearInterval(refreshIntervalId); refreshIntervalId = null; }
                    if (consecutiveFailures >= 2) {
                        refreshIntervalId = setInterval(loadMetrics, 15000);
                    }
                })
                .finally(function() { if (btn) { btn.disabled = false; btn.textContent = 'Refresh Metrics'; } });
        }
        function runOp(op) {
            var feedback = document.getElementById('opFeedback');
            var btn = document.getElementById('op' + (op === 'simulate-message' ? 'Msg' : op === 'new-conversation' ? 'Conv' : 'Batch'));
            if (btn) btn.disabled = true;
            feedback.textContent = 'Running...';
            fetch('/api/op/' + op, { method: 'POST', headers: { 'Content-Type': 'application/json' } })
                .then(function(r) { if (!r.ok) throw new Error('HTTP ' + r.status); return r.json(); })
                .then(function(data) {
                    feedback.textContent = data.message || 'Done. Metrics updated.';
                    loadMetrics();
                    setTimeout(function() { feedback.textContent = ''; }, 3000);
                })
                .catch(function(err) {
                    feedback.textContent = 'Error: ' + err.message;
                })
                .finally(function() { if (btn) btn.disabled = false; });
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
    return {
        "total_messages_sent": 0,
        "total_messages_received": 0,
        "total_conversations": 0,
        "last_activity": None,
        "messages": []
    }

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

@app.route("/update")
def update_metrics():
    return jsonify({"status": "ok"})

@app.route("/api/op/simulate-message", methods=["POST"])
def op_simulate_message():
    metrics = load_metrics()
    metrics["total_messages_sent"] = metrics.get("total_messages_sent", 0) + 1
    metrics["total_messages_received"] = metrics.get("total_messages_received", 0) + 1
    metrics["last_activity"] = dt.now().isoformat()
    metrics.setdefault("messages", []).append({
        "timestamp": metrics["last_activity"],
        "user": "Dashboard simulated",
        "bot_preview": "Metrics updated from dashboard."
    })
    if len(metrics["messages"]) > 100:
        metrics["messages"] = metrics["messages"][-100:]
    save_metrics(metrics)
    return jsonify({"ok": True, "message": "1 message simulated. Metrics updated."})

@app.route("/api/op/new-conversation", methods=["POST"])
def op_new_conversation():
    metrics = load_metrics()
    metrics["total_conversations"] = metrics.get("total_conversations", 0) + 1
    metrics["last_activity"] = dt.now().isoformat()
    save_metrics(metrics)
    return jsonify({"ok": True, "message": "New conversation started. Total conversations incremented."})

@app.route("/api/op/demo-batch", methods=["POST"])
def op_demo_batch():
    metrics = load_metrics()
    for user_msg, bot_preview in DEMO_MESSAGES:
        metrics["total_messages_sent"] = metrics.get("total_messages_sent", 0) + 1
        metrics["total_messages_received"] = metrics.get("total_messages_received", 0) + 1
        metrics["last_activity"] = dt.now().isoformat()
        metrics.setdefault("messages", []).append({
            "timestamp": metrics["last_activity"],
            "user": user_msg,
            "bot_preview": bot_preview[:80]
        })
    if len(metrics["messages"]) > 100:
        metrics["messages"] = metrics["messages"][-100:]
    save_metrics(metrics)
    return jsonify({"ok": True, "message": "5 demo messages sent. Metrics updated."})

if __name__ == "__main__":
    print("Starting LangChain Chatbot Dashboard on http://localhost:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)
