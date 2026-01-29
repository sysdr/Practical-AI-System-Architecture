#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
echo "Stopping LangChain Chatbot services..."
for pidfile in dashboard.pid background_demo.pid; do
    if [ -f "$SCRIPT_DIR/$pidfile" ]; then
        PID=$(cat "$SCRIPT_DIR/$pidfile")
        if ps -p $PID > /dev/null 2>&1; then
            echo "Stopping $pidfile (PID: $PID)..."
            kill $PID 2>/dev/null
        fi
        rm -f "$SCRIPT_DIR/$pidfile"
    fi
done
pkill -f "dashboard.py" 2>/dev/null || true
pkill -f "background_demo.py" 2>/dev/null || true
sleep 1
echo "All services stopped."
