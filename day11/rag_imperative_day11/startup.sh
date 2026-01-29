#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

check_duplicate_services() {
    for name in "dashboard.py" "background_demo.py"; do
        PIDS=$(pgrep -f "$name" 2>/dev/null | grep -v "$$" || true)
        if [ -n "$PIDS" ]; then
            echo "Warning: $name already running (PIDs: $PIDS). Stopping..."
            echo "$PIDS" | xargs kill 2>/dev/null || true
            sleep 2
        fi
    done
}

[ -d "venv" ] && source "$SCRIPT_DIR/venv/bin/activate"
check_duplicate_services

[ ! -f "metrics.json" ] && echo '{"total_questions_asked": 0, "total_responses": 0, "last_activity": null, "questions": []}' > "$SCRIPT_DIR/metrics.json"

echo "Starting dashboard..."
nohup python "$SCRIPT_DIR/dashboard.py" >> "$SCRIPT_DIR/dashboard.log" 2>&1 &
echo $! > "$SCRIPT_DIR/dashboard.pid"
echo "Dashboard: http://localhost:5000 (PID: $(cat "$SCRIPT_DIR/dashboard.pid"))"

echo "Starting background demo (metrics updates)..."
nohup python "$SCRIPT_DIR/background_demo.py" --interval 5 >> "$SCRIPT_DIR/background_demo.log" 2>&1 &
echo $! > "$SCRIPT_DIR/background_demo.pid"
echo "Background demo PID: $(cat "$SCRIPT_DIR/background_demo.pid")"
echo "To stop: $SCRIPT_DIR/stop.sh or ./stop.sh"
[ -d "venv" ] && deactivate 2>/dev/null || true
