#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [ -d ".venv" ]; then source "$SCRIPT_DIR/.venv/bin/activate"; fi
if pgrep -f "dashboard.py" > /dev/null; then
    echo "Dashboard already running. Use ./stop.sh to stop."
    exit 1
fi
[ ! -f "metrics.json" ] && echo '{"total_messages_sent": 0, "total_messages_received": 0, "total_conversations": 0, "last_activity": null, "messages": []}' > "$SCRIPT_DIR/metrics.json"
echo "Starting dashboard on http://localhost:5000"
nohup python "$SCRIPT_DIR/dashboard.py" >> "$SCRIPT_DIR/dashboard.log" 2>&1 &
echo $! > "$SCRIPT_DIR/dashboard.pid"
sleep 1
echo "Dashboard started (PID: $(cat "$SCRIPT_DIR/dashboard.pid")). Access: http://localhost:5000"
[ -d ".venv" ] && deactivate 2>/dev/null || true
