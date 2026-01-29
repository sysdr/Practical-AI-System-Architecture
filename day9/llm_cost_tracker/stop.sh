#!/bin/bash
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "Stopping LLM Cost Tracker services..."

for pidfile in dashboard.pid background_demo.pid; do
    if [ -f "$PROJECT_DIR/$pidfile" ]; then
        PID=$(cat "$PROJECT_DIR/$pidfile")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $pidfile (PID: $PID)..."
            kill $PID 2>/dev/null
        fi
        rm -f "$PROJECT_DIR/$pidfile"
    fi
done

pkill -f "dashboard.py" 2>/dev/null || true
pkill -f "background_demo.py" 2>/dev/null || true
sleep 1
echo "All services stopped."
