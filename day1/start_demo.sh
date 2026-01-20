#!/bin/bash

# Demo startup script with dashboard integration
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
export DASHBOARD_URL="http://localhost:8080"

# Check if dashboard is running, start if not
if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python src/dashboard.py 8080 > /dev/null 2>&1 &
    sleep 2
    echo "Dashboard started at http://localhost:8080"
fi

# Run demo
echo "Running LLM demo with dashboard integration..."
if [ $# -gt 0 ]; then
    python src/llm_client_with_dashboard.py "$@"
else
    python src/llm_client_with_dashboard.py "What is a microservice architecture?"
fi
