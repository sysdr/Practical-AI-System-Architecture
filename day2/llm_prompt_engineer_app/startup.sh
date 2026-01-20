#!/bin/bash

# Startup script for LLM Prompt Engineering Demo
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Get the absolute path to the project root (parent of PROJECT_DIR)
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

# Run the prompt engineering demo
echo "Starting LLM Prompt Engineering Demo..."
python "$SCRIPT_DIR/src/prompt_engineer_app.py" "$@"
