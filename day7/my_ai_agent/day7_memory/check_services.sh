#!/bin/bash
# Check for duplicate services script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "=== Checking for Running Services ==="
echo ""

# Check Flask processes
FLASK_PIDS=$(pgrep -f "flask run" || true)
if [ -n "$FLASK_PIDS" ]; then
    echo "Found Flask server processes:"
    ps -p $FLASK_PIDS -o pid,cmd
    echo ""
else
    echo "No Flask server processes found."
    echo ""
fi

# Check port 5000
PORT_USERS=$(lsof -ti:5000 2>/dev/null || true)
if [ -n "$PORT_USERS" ]; then
    echo "Processes using port 5000:"
    for PID in $PORT_USERS; do
        ps -p $PID -o pid,cmd
    done
    echo ""
    echo "Total processes on port 5000: $(echo $PORT_USERS | wc -w)"
else
    echo "Port 5000 is not in use."
    echo ""
fi

# Check Docker containers
if command -v docker >/dev/null 2>&1; then
    CONTAINERS=$(docker ps --filter "name=day7_memory" --format "{{.ID}} {{.Names}}" 2>/dev/null || true)
    if [ -n "$CONTAINERS" ]; then
        echo "Docker containers:"
        echo "$CONTAINERS"
        echo ""
    else
        echo "No day7_memory Docker containers running."
        echo ""
    fi
fi

echo "=== Service check complete ==="
