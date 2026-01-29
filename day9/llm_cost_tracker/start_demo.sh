#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi
source .venv/bin/activate
export DASHBOARD_URL="http://localhost:5000"

if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python "$SCRIPT_DIR/dashboard.py" > /dev/null 2>&1 &
    sleep 2
fi

echo "Running LLM Cost Tracker demo (metrics update dashboard)..."
python "$SCRIPT_DIR/src/main.py" "$@"
deactivate
