#!/bin/bash

# Dashboard startup script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:${SCRIPT_DIR}"

# Check if dashboard is already running
if pgrep -f "dashboard.py" > /dev/null; then
    echo "Dashboard is already running. Use 'pkill -f dashboard.py' to stop it."
    exit 1
fi

# Start dashboard
echo "Starting dashboard server on http://localhost:8080"
python src/dashboard.py 8080 &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"
echo "Access dashboard at: http://localhost:8080"
echo "To stop: kill $DASHBOARD_PID"
