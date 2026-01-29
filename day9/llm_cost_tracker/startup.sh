#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

check_duplicate_services() {
    DASHBOARD_PID=$(pgrep -f "dashboard.py" | grep -v "$$" | head -1)
    if [ -n "$DASHBOARD_PID" ]; then
        echo "Warning: Dashboard already running (PID: $DASHBOARD_PID). Stopping..."
        kill $DASHBOARD_PID 2>/dev/null
        sleep 2
    fi
    DEMO_PID=$(pgrep -f "background_demo.py" | grep -v "$$" | head -1)
    if [ -n "$DEMO_PID" ]; then
        echo "Warning: Background demo already running (PID: $DEMO_PID). Stopping..."
        kill $DEMO_PID 2>/dev/null
        sleep 1
    fi
}

if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh from day9 first."
    exit 1
fi
source .venv/bin/activate
check_duplicate_services

if [ ! -f "metrics.json" ]; then
    echo '{"total_prompts": 0, "total_input_tokens": 0, "total_output_tokens": 0, "total_estimated_cost": 0.0, "last_request_time": null, "requests": []}' > metrics.json
fi

echo "Starting LLM Cost Tracker Dashboard..."
nohup python dashboard.py > dashboard.log 2>&1 &
echo $! > dashboard.pid
echo "Dashboard: http://localhost:5000 (PID: $(cat dashboard.pid))"

echo "Starting background demo for live metrics..."
nohup python background_demo.py --interval 8 > background_demo.log 2>&1 &
echo $! > background_demo.pid
echo "Background demo PID: $(cat background_demo.pid)"
echo "To stop: ./stop.sh (or $PROJECT_DIR/stop.sh from anywhere)"
deactivate
