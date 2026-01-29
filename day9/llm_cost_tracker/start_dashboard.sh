#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi
source .venv/bin/activate

if pgrep -f "dashboard.py" > /dev/null; then
    echo "Dashboard is already running. Use ./stop.sh or pkill -f dashboard.py to stop."
    exit 1
fi

if [ ! -f "metrics.json" ]; then
    echo '{"total_prompts": 0, "total_input_tokens": 0, "total_output_tokens": 0, "total_estimated_cost": 0.0, "last_request_time": null, "requests": []}' > metrics.json
fi

echo "Starting dashboard on http://localhost:5000"
nohup python "$SCRIPT_DIR/dashboard.py" >> "$SCRIPT_DIR/dashboard.log" 2>&1 &
DASH_PID=$!
echo $DASH_PID > "$SCRIPT_DIR/dashboard.pid"
sleep 1
if kill -0 $DASH_PID 2>/dev/null; then
    echo "Dashboard started (PID: $DASH_PID). Access at: http://localhost:5000"
    echo "Logs: $SCRIPT_DIR/dashboard.log. To stop: ./stop.sh or kill $DASH_PID"
else
    echo "Dashboard failed to start. Check $SCRIPT_DIR/dashboard.log"
    exit 1
fi
deactivate
