#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

# --- Configuration ---
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$SCRIPT_DIR/.venv"
DATA_DIR="$SCRIPT_DIR/data"
MAIN_SCRIPT="$SCRIPT_DIR/main.py"
SAMPLE_PDF_URL="https://arxiv.org/pdf/2307.03172.pdf"

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

# Function to check if a command exists
command_exists () {
    type "$1" &> /dev/null ;
}

# Function to set up Python virtual environment
setup_venv() {
    if [ -d "$VENV_DIR" ]; then
        display_message INFO "Virtual environment already exists. Activating..."
    else
        display_message INFO "Setting up Python virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    source "$VENV_DIR/bin/activate"
    display_message SUCCESS "Virtual environment activated."
}

# Function to install dependencies
install_dependencies() {
    display_message INFO "Installing dependencies..."
    pip install --upgrade pip --quiet
    pip install langchain-text-splitters langchain-community pypdf requests rich --quiet
    display_message SUCCESS "Dependencies installed."
}

# Function to run the main application
run_application() {
    display_message INFO "Running the text splitting application..."
    cd "$SCRIPT_DIR"
    export SAMPLE_PDF_URL="$SAMPLE_PDF_URL"
    python "$MAIN_SCRIPT"
    display_message SUCCESS "Application finished."
}

# --- Main execution flow ---

# Check for required tools
if ! command_exists python3; then
    display_message ERROR "Python 3 is not installed. Please install Python 3.10+ to proceed."
    exit 1
fi

display_message INFO "Starting RAG Text Splitting Project..."

# Setup virtual environment
setup_venv

# Install dependencies
install_dependencies

# Run the application
run_application

display_message SUCCESS "Project execution complete."
display_message INFO "To clean up, run: ./stop.sh"
