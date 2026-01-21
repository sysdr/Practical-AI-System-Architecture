# LLM Switcher Project

A Python application that allows switching between different LLM providers (OpenAI and Anthropic) with real-time metrics dashboard.

## Quick Start

### 1. Setup
From the `day4` directory, run:
```bash
./setup.sh
```

This will:
- Create the project structure
- Install Python dependencies
- Set up virtual environment

### 2. Start the Application
Navigate to the project directory and start the services:
```bash
cd llm_switching_project
./start.sh
```

This will start:
- **Dashboard** at http://localhost:5000 (auto-refreshes every 3 seconds)
- **Background Demo** that adds new requests every 5 seconds for real-time updates

### 3. Stop the Application
```bash
./stop.sh
```

### 4. Cleanup Docker Resources
```bash
./cleanup.sh
```

## Project Structure

```
llm_switching_project/
├── start.sh              # Start dashboard and background demo
├── stop.sh               # Stop all services
├── cleanup.sh            # Cleanup Docker resources
├── llm_switcher.py       # Main LLM switching logic
├── dashboard.py          # Web dashboard (Flask)
├── background_demo.py    # Continuous demo for real-time updates
├── demo.py               # One-time demo script
├── test_llm_switcher.py  # Unit tests
├── requirements.txt      # Python dependencies
├── Dockerfile           # Docker configuration
└── metrics.json         # Metrics storage (auto-generated)
```

## Usage

### Running Tests
```bash
cd llm_switching_project
source venv/bin/activate
python -m pytest test_llm_switcher.py -v
```

### Using the LLM Switcher
```bash
cd llm_switching_project
source venv/bin/activate

# OpenAI
python llm_switcher.py --provider openai --prompt "Your prompt here"

# Anthropic
python llm_switcher.py --provider anthropic --prompt "Your prompt here"
```

### Environment Variables
Set these before running:
```bash
export OPENAI_API_KEY='your-openai-key'
export ANTHROPIC_API_KEY='your-anthropic-key'
```

## Dashboard Features

- **Real-time Metrics**: Auto-updates every 3 seconds
- **Request Tracking**: See all recent requests with timestamps
- **Provider Statistics**: Separate metrics for OpenAI and Anthropic
- **Error Tracking**: Monitor failed requests
- **Latency Monitoring**: Average latency per provider

## Scripts

### start.sh
- Starts the dashboard on port 5000
- Starts background demo for continuous updates
- Checks for duplicate services and stops them
- Initializes metrics.json if needed

### stop.sh
- Stops dashboard and background demo
- Cleans up PID files
- Kills any remaining processes

### cleanup.sh
- Stops all Docker containers
- Removes unused Docker images, volumes, and networks
- Performs comprehensive Docker system cleanup

## Notes

- All scripts are designed to run from the `llm_switching_project` directory
- The dashboard requires the virtual environment to be activated
- Metrics are stored in `metrics.json` and persist between restarts
- Logs are written to `dashboard.log` and `background_demo.log`
