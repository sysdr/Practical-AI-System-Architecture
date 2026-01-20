#!/bin/bash

# Demo startup script with dashboard integration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get the absolute path to the project root
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Activate virtual environment
if [ -d "$PROJECT_ROOT/venv" ]; then
    source "$PROJECT_ROOT/venv/bin/activate"
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$SCRIPT_DIR/src"
export DASHBOARD_URL="http://localhost:8080"

# Check if dashboard is running, start if not
if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python "$SCRIPT_DIR/src/dashboard.py" 8080 > /dev/null 2>&1 &
    sleep 2
    echo "Dashboard started at http://localhost:8080"
fi

# Run demo (use --demo flag for simulated successful API calls)
echo "Running LLM Prompt Engineering demo with dashboard integration..."
if [ $# -eq 0 ]; then
    # Default to demo mode if no arguments provided
    python "$SCRIPT_DIR/src/prompt_engineer_app_with_dashboard.py" --demo
else
    python "$SCRIPT_DIR/src/prompt_engineer_app_with_dashboard.py" "$@"
fi
