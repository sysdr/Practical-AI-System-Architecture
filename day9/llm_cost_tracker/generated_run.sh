#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if [ ! -d ".venv" ]; then
    echo "Error: .venv not found. Run setup.sh from day9 first."
    exit 1
fi
source .venv/bin/activate

if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python dashboard.py > dashboard.log 2>&1 &
    sleep 2
fi

echo "Running LLM Cost Tracker demo. Dashboard: http://localhost:5000"
export DASHBOARD_URL="http://localhost:5000"
python src/main.py
echo "To stop dashboard: ./stop.sh"
deactivate
