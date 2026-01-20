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
    echo "Dashboard is already running."
else
    echo "Starting dashboard..."
    python "$SCRIPT_DIR/dashboard.py" 8080 > /dev/null 2>&1 &
    sleep 2
    echo "Dashboard started at http://localhost:8080"
fi

# Run demo
echo "Running LLM Context Analysis demo..."
python "$SCRIPT_DIR/main_with_dashboard.py"
