#!/bin/bash
# Start client script
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

# Check if server is running
if ! lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "Error: Flask server is not running on port 5000."
    echo "Please start the server first using: ./start_server.sh"
    exit 1
fi

echo "Starting client..."
python client.py
