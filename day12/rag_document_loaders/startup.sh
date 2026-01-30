#!/bin/bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== RAG Document Loader Startup Script ==="

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Run setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check for duplicate dashboard processes
EXISTING_PID=$(pgrep -f "python dashboard.py" || true)
if [ -n "$EXISTING_PID" ]; then
    echo "Warning: Dashboard already running with PID: $EXISTING_PID"
    echo "Stopping existing instance..."
    kill $EXISTING_PID 2>/dev/null || true
    sleep 2
fi

# Run the document loader demo first to generate initial metrics
echo ""
echo "--- Running initial document loader demo to populate metrics ---"
python app.py

echo ""
echo "--- Starting Dashboard Server ---"
export DASHBOARD_PORT=${DASHBOARD_PORT:-5000}
echo "Dashboard will be available at: http://localhost:$DASHBOARD_PORT"
echo "Press Ctrl+C to stop the dashboard"
echo ""

# Start dashboard
python dashboard.py
