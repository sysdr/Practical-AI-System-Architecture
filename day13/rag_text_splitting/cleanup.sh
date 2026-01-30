#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Functions ---

# Function to display messages in a professional console style
display_message() {
    local type=$1
    local message=$2
    local color=""
    case "$type" in
        "INFO") color="\033[0;34m" ;; # Blue
        "SUCCESS") color="\033[0;32m" ;; # Green
        "WARNING") color="\033[0;33m" ;; # Yellow
        "ERROR") color="\033[0;31m" ;; # Red
        *) color="\033[0m" ;; # Reset
    esac
    echo -e "${color}[$type] $message\033[0m"
}

# --- Main Cleanup ---

display_message INFO "========================================"
display_message INFO "RAG Text Splitting - Full Cleanup Script"
display_message INFO "========================================"

# Stop any running Python processes from this project
display_message INFO "Stopping any running Python processes..."
# Note: Using pgrep to find and selectively kill only main.py processes
pids=$(pgrep -f "python.*main.py" 2>/dev/null | grep -v $$ || true)
if [ -n "$pids" ]; then
    echo "$pids" | xargs kill 2>/dev/null || true
    display_message SUCCESS "Stopped Python processes."
else
    display_message INFO "No Python processes to stop."
fi

# Stop Docker containers (if any related to this project)
display_message INFO "Checking for Docker containers..."
if command -v docker &> /dev/null; then
    # Stop all running containers
    RUNNING_CONTAINERS=$(docker ps -q 2>/dev/null)
    if [ -n "$RUNNING_CONTAINERS" ]; then
        display_message INFO "Stopping running Docker containers..."
        docker stop $RUNNING_CONTAINERS 2>/dev/null || true
    else
        display_message INFO "No running Docker containers found."
    fi

    # Remove stopped containers
    display_message INFO "Removing stopped Docker containers..."
    docker container prune -f 2>/dev/null || true

    # Remove unused Docker images
    display_message INFO "Removing unused Docker images..."
    docker image prune -f 2>/dev/null || true

    # Remove unused Docker volumes
    display_message INFO "Removing unused Docker volumes..."
    docker volume prune -f 2>/dev/null || true

    # Remove unused Docker networks
    display_message INFO "Removing unused Docker networks..."
    docker network prune -f 2>/dev/null || true

    # Full system prune (dangling resources)
    display_message INFO "Running Docker system prune..."
    docker system prune -f 2>/dev/null || true

    display_message SUCCESS "Docker cleanup complete."
else
    display_message WARNING "Docker is not installed or not running."
fi

# Remove virtual environment
display_message INFO "Removing Python virtual environment..."
if [ -d "$SCRIPT_DIR/.venv" ]; then
    rm -rf "$SCRIPT_DIR/.venv"
    display_message SUCCESS "Removed .venv directory."
else
    display_message INFO "No .venv directory found."
fi

if [ -d "$SCRIPT_DIR/venv" ]; then
    rm -rf "$SCRIPT_DIR/venv"
    display_message SUCCESS "Removed venv directory."
fi

# Remove data directory
display_message INFO "Removing data directory..."
if [ -d "$SCRIPT_DIR/data" ]; then
    rm -rf "$SCRIPT_DIR/data"
    display_message SUCCESS "Removed data directory."
else
    display_message INFO "No data directory found."
fi

# Remove Python cache files
display_message INFO "Removing Python cache files..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name ".coverage" -delete 2>/dev/null || true
display_message SUCCESS "Removed Python cache files."

# Remove node_modules if exists
display_message INFO "Checking for node_modules..."
if [ -d "$SCRIPT_DIR/node_modules" ]; then
    rm -rf "$SCRIPT_DIR/node_modules"
    display_message SUCCESS "Removed node_modules directory."
else
    display_message INFO "No node_modules directory found."
fi

# Remove Istio files if any
display_message INFO "Checking for Istio files..."
find "$SCRIPT_DIR" -type f -name "*istio*" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name "*istio*" -exec rm -rf {} + 2>/dev/null || true
display_message SUCCESS "Istio cleanup complete."

# Remove .env files (may contain API keys)
display_message INFO "Removing .env files (may contain sensitive data)..."
find "$SCRIPT_DIR" -type f -name ".env" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name ".env.*" -delete 2>/dev/null || true
display_message SUCCESS "Removed .env files."

# Remove log files
display_message INFO "Removing log files..."
find "$SCRIPT_DIR" -type f -name "*.log" -delete 2>/dev/null || true
display_message SUCCESS "Removed log files."

display_message SUCCESS "========================================"
display_message SUCCESS "Cleanup complete!"
display_message SUCCESS "========================================"

# Show remaining files
display_message INFO "Remaining files in project:"
ls -la "$SCRIPT_DIR"
