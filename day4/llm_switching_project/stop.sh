#!/bin/bash

# Get absolute path of project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

stop_services() {
    echo "Stopping LLM Switcher services..."
    
    # Stop dashboard
    if [ -f "$PROJECT_DIR/dashboard.pid" ]; then
        DASHBOARD_PID=$(cat "$PROJECT_DIR/dashboard.pid")
        if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
            echo "Stopping dashboard (PID: $DASHBOARD_PID)..."
            kill $DASHBOARD_PID 2>/dev/null
            rm "$PROJECT_DIR/dashboard.pid"
            echo "Dashboard stopped."
        else
            echo "Dashboard process not found."
            rm "$PROJECT_DIR/dashboard.pid"
        fi
    fi
    
    # Kill any remaining dashboard processes
    DASHBOARD_PIDS=$(pgrep -f "dashboard.py" 2>/dev/null)
    if [ ! -z "$DASHBOARD_PIDS" ]; then
        echo "Stopping remaining dashboard processes..."
        pkill -f "dashboard.py"
        sleep 1
    fi
    
    # Stop background demo
    if [ -f "$PROJECT_DIR/background_demo.pid" ]; then
        DEMO_PID=$(cat "$PROJECT_DIR/background_demo.pid")
        if ps -p $DEMO_PID > /dev/null 2>&1; then
            echo "Stopping background demo (PID: $DEMO_PID)..."
            kill $DEMO_PID 2>/dev/null
            rm "$PROJECT_DIR/background_demo.pid"
            echo "Background demo stopped."
        else
            echo "Background demo process not found."
            rm "$PROJECT_DIR/background_demo.pid"
        fi
    fi
    
    # Kill any remaining demo processes
    DEMO_PIDS=$(pgrep -f "background_demo.py" 2>/dev/null)
    if [ ! -z "$DEMO_PIDS" ]; then
        echo "Stopping remaining demo processes..."
        pkill -f "background_demo.py"
        sleep 1
    fi
    
    echo "All services stopped."
}

stop_services
