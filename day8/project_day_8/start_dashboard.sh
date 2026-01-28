#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if dashboard is already running
if pgrep -f "dashboard.py" > /dev/null; then
    echo "Dashboard is already running. Use 'pkill -f dashboard.py' to stop it."
    exit 1
fi

# Initialize metrics file if it doesn't exist
if [ ! -f "metrics.json" ]; then
    echo '{"total_requests": 0, "successful_parsing": 0, "failed_parsing": 0, "retry_attempts": 0, "validation_errors": 0, "total_latency_ms": 0, "average_latency_ms": 0.0, "last_request_time": null, "requests": []}' > metrics.json
fi

# Start dashboard
echo "Starting dashboard server on http://localhost:5000"
python "$SCRIPT_DIR/dashboard.py" &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"
echo "Access dashboard at: http://localhost:5000"
echo "To stop: kill $DASHBOARD_PID"
deactivate
