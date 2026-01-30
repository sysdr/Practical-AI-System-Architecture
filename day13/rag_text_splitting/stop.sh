#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
DATA_DIR="$SCRIPT_DIR/data"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"

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

# Function to clean up
cleanup() {
    display_message INFO "Cleaning up project artifacts..."
    
    # Deactivate virtual environment if active
    if [ -n "$VIRTUAL_ENV" ]; then
        deactivate 2>/dev/null || true
        display_message INFO "Deactivated virtual environment."
    fi

    if [ -d "$VENV_DIR" ]; then
        display_message INFO "Removing virtual environment: $VENV_DIR"
        rm -rf "$VENV_DIR"
    fi
    if [ -d "$DATA_DIR" ]; then
        display_message INFO "Removing data directory: $DATA_DIR"
        rm -rf "$DATA_DIR"
    fi

    display_message SUCCESS "Cleanup complete."
}

# --- Main execution flow ---
display_message INFO "Stopping and cleaning up RAG Text Splitting Project..."
cleanup
