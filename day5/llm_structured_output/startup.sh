#!/bin/bash

# Get absolute path of project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# Check for duplicate services
check_duplicate_services() {
    DASHBOARD_PID=$(pgrep -f "dashboard.py" | grep -v "$$" | head -1)
    if [ ! -z "$DASHBOARD_PID" ]; then
        echo "Warning: Dashboard is already running (PID: $DASHBOARD_PID)"
        echo "Stopping existing dashboard..."
        kill $DASHBOARD_PID 2>/dev/null
        sleep 2
    fi
    
    DEMO_PID=$(pgrep -f "background_demo.py" | grep -v "$$" | head -1)
    if [ ! -z "$DEMO_PID" ]; then
        echo "Warning: Background demo is already running (PID: $DEMO_PID)"
        echo "Stopping existing demo..."
        kill $DEMO_PID 2>/dev/null
        sleep 1
    fi
}

# Check for virtual environment
if [ ! -d ".venv" ]; then
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check for duplicate services
check_duplicate_services

# Initialize metrics file if it doesn't exist
if [ ! -f "metrics.json" ]; then
    echo '{"total_requests": 0, "successful_extractions": 0, "failed_extractions": 0, "validation_errors": 0, "total_latency_ms": 0, "average_latency_ms": 0.0, "last_request_time": null, "requests": []}' > metrics.json
fi

# Start dashboard in background
echo "Starting LLM Structured Output Dashboard..."
nohup python dashboard.py > dashboard.log 2>&1 &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"
echo "Dashboard is available at: http://localhost:5000"
echo "Logs are written to: $PROJECT_DIR/dashboard.log"
echo ""
echo "To stop the services, run: ./stop.sh"
echo "Or manually: kill $DASHBOARD_PID"

# Save PID to file
echo $DASHBOARD_PID > dashboard.pid

# Start background demo to generate continuous updates
echo ""
echo "Starting background demo for real-time updates..."
nohup python background_demo.py --interval 10 > background_demo.log 2>&1 &
DEMO_PID=$!
echo "Background demo started with PID: $DEMO_PID"
echo "New requests will be added every 10 seconds"
echo "Demo logs: $PROJECT_DIR/background_demo.log"

# Save demo PID to file
echo $DEMO_PID > background_demo.pid

deactivate
