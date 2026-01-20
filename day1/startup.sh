#!/bin/bash

# Startup script for LLM Day 1 Demo
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

# Run the LLM client demo
echo "Starting LLM Demo..."
python src/llm_client.py "$@"
