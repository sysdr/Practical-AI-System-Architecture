#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
if [ -d ".venv" ]; then source "$SCRIPT_DIR/.venv/bin/activate"; fi
export DASHBOARD_URL="http://localhost:5000"
if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python "$SCRIPT_DIR/dashboard.py" >> "$SCRIPT_DIR/dashboard.log" 2>&1 &
    sleep 2
fi
echo "Running background demo to update dashboard metrics..."
python "$SCRIPT_DIR/background_demo.py" --interval 3
[ -d ".venv" ] && deactivate 2>/dev/null || true
