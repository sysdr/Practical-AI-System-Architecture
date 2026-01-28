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

export DASHBOARD_URL="http://localhost:5000"

# Check if dashboard is running, start if not
if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python "$SCRIPT_DIR/dashboard.py" > /dev/null 2>&1 &
    sleep 2
    echo "Dashboard started at http://localhost:5000"
fi

echo "Running Reliable Output Parsing demo with dashboard integration..."
python "$SCRIPT_DIR/src/main.py" "$@"
deactivate
