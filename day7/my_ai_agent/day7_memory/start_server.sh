#!/bin/bash
# Start Flask server script
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check if virtual environment exists (try current dir first, then parent)
if [ -d "$SCRIPT_DIR/.venv_day7" ]; then
    VENV_PATH="$SCRIPT_DIR/.venv_day7"
elif [ -d "$SCRIPT_DIR/../.venv_day7" ]; then
    VENV_PATH="$SCRIPT_DIR/../.venv_day7"
else
    echo "Error: Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source "$VENV_PATH/bin/activate"

# Check if server is already running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Warning: Port 5000 is already in use. Checking for existing Flask server..."
    PID=$(lsof -ti:5000)
    echo "Found process with PID: $PID"
    read -p "Do you want to kill it and start a new server? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        kill $PID
        sleep 2
    else
        echo "Exiting. Please stop the existing server first."
        exit 1
    fi
fi

# Start Flask server (use python app.py so routes from this dir are loaded)
echo "Starting Flask server on port 5000..."
nohup python app.py > flask_server.log 2>&1 &
SERVER_PID=$!
echo "Flask server started with PID $SERVER_PID"
echo "Logs are available in flask_server.log"
echo "To stop the server, run: kill $SERVER_PID"
