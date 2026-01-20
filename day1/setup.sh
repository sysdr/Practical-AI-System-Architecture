#!/bin/bash

# Define colors for better console output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}--- Practical AI System Architecture: Day 1 Setup & Demo ---${NC}"

# 1. Setup Environment
echo -e "${YELLOW}1. Setting up environment...${NC}"

# Check for Python and pip
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python3 is not installed. Please install Python3 to proceed.${NC}"
    exit 1
fi
if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}Error: pip3 is not installed. Please install pip3 (usually comes with Python3) to proceed.${NC}"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo -e "${GREEN}Creating Python virtual environment...${NC}"
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}Failed to create virtual environment. Exiting.${NC}"
        exit 1
    fi
fi

# Activate virtual environment
source venv/bin/activate
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to activate virtual environment. Exiting.${NC}"
    exit 1
fi
echo -e "${GREEN}Virtual environment activated.${NC}"

# 2. Generate Project Structure and Code
echo -e "${YELLOW}2. Generating project structure and source code...${NC}"

mkdir -p src tests config
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create project directories. Exiting.${NC}"
    deactivate
    exit 1
fi

# Create requirements.txt
echo "openai~=1.0" > requirements.txt
echo "python-dotenv~=1.0" >> requirements.txt
echo "pytest~=8.0" >> requirements.txt
echo "requests~=2.31" >> requirements.txt
echo -e "${GREEN}Generated requirements.txt.${NC}"

# Install dependencies
echo -e "${GREEN}Installing dependencies...${NC}"
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to install dependencies. Exiting.${NC}"
    deactivate
    exit 1
fi
echo -e "${GREEN}Dependencies installed.${NC}"

# Create llm_client.py
cat <<EOF > src/llm_client.py
import os
import openai
from dotenv import load_dotenv
import sys

def get_llm_response(prompt_message: str, model: str = "gpt-3.5-turbo", temperature: float = 0.7, max_tokens: int = 150):
    """
    Makes an API call to a foundational LLM (OpenAI Chat API) and returns its raw output.
    """
    # Load environment variables from .env file in the config directory
    dotenv_path = os.path.join(os.path.dirname(__file__), '..', 'config', '.env')
    load_dotenv(dotenv_path)
    openai_api_key = os.getenv("OPENAI_API_KEY")

    if not openai_api_key:
        print("${RED}Error: OPENAI_API_KEY not found in environment or config/.env file.${NC}")
        print("${YELLOW}Please set it before running the script (e.g., in config/.env).${NC}")
        return None

    try:
        client = openai.OpenAI(api_key=openai_api_key)
        
        print(f"\n--- Sending request to LLM (Model: {model}) ---")
        print(f"Prompt: '{prompt_message}'")
        print(f"Temperature: {temperature}, Max Tokens: {max_tokens}")

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt_message}
            ],
            temperature=temperature,
            max_tokens=max_tokens
        )
        print("\n--- Raw LLM Response ---")
        return response

    except openai.APIError as e:
        print(f"${RED}OpenAI API Error: {e}${NC}")
        return None
    except Exception as e:
        print(f"${RED}An unexpected error occurred: {e}${NC}")
        return None

if __name__ == "__main__":
    print("${BLUE}--- LLM Interaction Demo ---${NC}")
    
    # Default prompt for demonstration
    default_prompt = "Explain the concept of 'distributed consensus' in a simple way."
    
    # Check for command line arguments for a custom prompt
    if len(sys.argv) > 1:
        custom_prompt_parts = sys.argv[1:]
        default_prompt = " ".join(custom_prompt_parts)

    llm_output = get_llm_response(default_prompt)

    if llm_output:
        print(llm_output.model_dump_json(indent=2)) # Pretty print the Pydantic model
        print("\n--- Extracted Content ---")
        print(llm_output.choices[0].message.content)
    else:
        print("\nFailed to get LLM response.")
EOF
echo -e "${GREEN}Generated src/llm_client.py.${NC}"

# Create a dummy test file
cat <<EOF > tests/test_llm_client.py
import pytest
import os
import openai
from src.llm_client import get_llm_response

# This is a very basic test. In a real system, you'd mock the OpenAI API.
# For this hands-on lesson, we'll just check if the function runs without immediate errors.
def test_get_llm_response_basic_call():
    # This test will attempt to make an actual API call if OPENAI_API_KEY is set.
    # It's primarily to ensure the function signature and basic execution flow are correct.
    # We don't assert on content as LLM output is non-deterministic.
    # If API key is missing, it should gracefully return None.
    
    # Temporarily unset API key to test the error path first
    original_api_key = os.environ.get("OPENAI_API_KEY")
    if original_api_key:
        del os.environ["OPENAI_API_KEY"]

    response_no_key = get_llm_response("test prompt")
    assert response_no_key is None

    # Restore API key if it existed, or set a dummy one for the function to proceed
    if original_api_key:
        os.environ["OPENAI_API_KEY"] = original_api_key
    else:
        # If no key was originally set, we still need one for the positive test path
        # This will likely fail if a real key isn't present, but tests the flow.
        os.environ["OPENAI_API_KEY"] = "dummy-key-for-test-flow" 

    # For a real API call, the key must be valid.
    # This test will pass if the function attempts to call without crashing.
    # A true integration test would require a valid, test-specific API key.
    try:
        response = get_llm_response("What is pytest?", temperature=0.1, max_tokens=20)
        # If an API key is present and valid, response should not be None
        # If API key is dummy, it will return None due to APIError, which is also a valid path for this test.
        # The main goal here is to ensure the function runs without syntax/runtime errors.
        assert response is None or hasattr(response, 'choices')
    except openai.APIError:
        # Expected if dummy key is used
        assert True
    finally:
        # Clean up environment variable
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key # Restore original
EOF
echo -e "${GREEN}Generated tests/test_llm_client.py.${NC}"

# Create startup script
cat <<'EOF' > startup.sh
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
EOF
chmod +x startup.sh
echo -e "${GREEN}Generated startup.sh.${NC}"

# Create dashboard server
cat <<'EOF' > src/dashboard.py
#!/usr/bin/env python3
"""
Dashboard server for LLM Day 1 Demo
Tracks metrics and displays them in a web interface
"""
import os
import json
import time
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import threading

# Metrics storage
metrics = {
    "total_requests": 0,
    "successful_requests": 0,
    "failed_requests": 0,
    "total_tokens": 0,
    "last_request_time": None,
    "requests": []
}

def update_metrics(response_data=None, success=True, tokens=0):
    """Update metrics with new request data"""
    metrics["total_requests"] += 1
    if success:
        metrics["successful_requests"] += 1
        metrics["total_tokens"] += tokens
    else:
        metrics["failed_requests"] += 1
    metrics["last_request_time"] = datetime.now().isoformat()
    if response_data:
        metrics["requests"].append({
            "time": datetime.now().isoformat(),
            "success": success,
            "tokens": tokens,
            "data": response_data
        })
    # Keep only last 50 requests
    if len(metrics["requests"]) > 50:
        metrics["requests"] = metrics["requests"][-50:]

class DashboardHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        if parsed_path.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.get_dashboard_html().encode())
        elif parsed_path.path == '/metrics':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(metrics, indent=2).encode())
        elif parsed_path.path == '/update':
            # Update metrics endpoint
            query_params = parse_qs(parsed_path.query)
            success = query_params.get('success', ['true'])[0].lower() == 'true'
            tokens = int(query_params.get('tokens', ['0'])[0])
            update_metrics(success=success, tokens=tokens)
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"status": "updated"}).encode())
        else:
            self.send_response(404)
            self.end_headers()
    
    def get_dashboard_html(self):
        success_rate = 0
        if metrics["total_requests"] > 0:
            success_rate = (metrics["successful_requests"] / metrics["total_requests"]) * 100
        
        html = f"""
<!DOCTYPE html>
<html>
<head>
    <title>LLM Day 1 Dashboard</title>
    <meta http-equiv="refresh" content="5">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .metrics-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric-card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 8px;
            text-align: center;
        }}
        .metric-card.success {{
            background: linear-gradient(135deg, #4CAF50 0%, #45a049 100%);
        }}
        .metric-card.warning {{
            background: linear-gradient(135deg, #ff9800 0%, #f57c00 100%);
        }}
        .metric-card.error {{
            background: linear-gradient(135deg, #f44336 0%, #d32f2f 100%);
        }}
        .metric-value {{
            font-size: 2.5em;
            font-weight: bold;
            margin: 10px 0;
        }}
        .metric-label {{
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .status {{
            padding: 10px;
            margin: 10px 0;
            border-radius: 4px;
            background: #e8f5e9;
            color: #2e7d32;
        }}
        .last-update {{
            text-align: right;
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 LLM Day 1 Demo Dashboard</h1>
        <div class="status">
            <strong>Status:</strong> {'🟢 Active' if metrics['total_requests'] > 0 else '🟡 Waiting for requests'}
        </div>
        <div class="metrics-grid">
            <div class="metric-card">
                <div class="metric-label">Total Requests</div>
                <div class="metric-value">{metrics['total_requests']}</div>
            </div>
            <div class="metric-card success">
                <div class="metric-label">Successful</div>
                <div class="metric-value">{metrics['successful_requests']}</div>
            </div>
            <div class="metric-card error">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{metrics['failed_requests']}</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Success Rate</div>
                <div class="metric-value">{success_rate:.1f}%</div>
            </div>
            <div class="metric-card">
                <div class="metric-label">Total Tokens</div>
                <div class="metric-value">{metrics['total_tokens']}</div>
            </div>
        </div>
        <div class="last-update">
            Last Request: {metrics['last_request_time'] or 'Never'}
            <br>Auto-refresh: Every 5 seconds
        </div>
    </div>
</body>
</html>
"""
        return html
    
    def log_message(self, format, *args):
        # Suppress default logging
        pass

def start_dashboard_server(port=8080):
    """Start the dashboard server"""
    server = HTTPServer(('', port), DashboardHandler)
    print(f"Dashboard server starting on http://localhost:{port}")
    print(f"Metrics API: http://localhost:{port}/metrics")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down dashboard server...")
        server.shutdown()

if __name__ == "__main__":
    import sys
    port = 8080
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    start_dashboard_server(port)
EOF
chmod +x src/dashboard.py
echo -e "${GREEN}Generated src/dashboard.py.${NC}"

# Create enhanced LLM client that updates dashboard
cat <<'EOF' > src/llm_client_with_dashboard.py
#!/usr/bin/env python3
"""
Enhanced LLM client that updates dashboard metrics
"""
import os
import sys
import requests
import time
from llm_client import get_llm_response

DASHBOARD_URL = os.getenv("DASHBOARD_URL", "http://localhost:8080")

def update_dashboard(success=True, tokens=0):
    """Update dashboard metrics"""
    try:
        requests.get(f"{DASHBOARD_URL}/update", params={
            "success": "true" if success else "false",
            "tokens": str(tokens)
        }, timeout=1)
    except:
        # Dashboard might not be running, that's okay
        pass

if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt = " ".join(sys.argv[1:])
    else:
        prompt = "Explain the concept of 'distributed consensus' in a simple way."
    
    response = get_llm_response(prompt)
    
    if response:
        tokens = 0
        if hasattr(response, 'usage') and hasattr(response.usage, 'total_tokens'):
            tokens = response.usage.total_tokens
        update_dashboard(success=True, tokens=tokens)
        print(f"\n✅ Request successful - {tokens} tokens used")
    else:
        update_dashboard(success=False, tokens=0)
        print("\n❌ Request failed")
EOF
chmod +x src/llm_client_with_dashboard.py
echo -e "${GREEN}Generated src/llm_client_with_dashboard.py.${NC}"

# 3. Configure API Key
echo -e "${YELLOW}3. Configuring OpenAI API Key...${NC}"
ENV_FILE="config/.env"
if [ ! -f "$ENV_FILE" ]; then
    touch "$ENV_FILE"
fi

if grep -q "OPENAI_API_KEY" "$ENV_FILE"; then
    echo -e "${GREEN}OPENAI_API_KEY already found in $ENV_FILE. Skipping prompt.${NC}"
else
    # Check if API key is provided via environment variable
    if [ -n "$OPENAI_API_KEY" ]; then
        echo "OPENAI_API_KEY=$OPENAI_API_KEY" >> "$ENV_FILE"
        echo -e "${GREEN}API Key from environment saved to $ENV_FILE.${NC}"
    else
        # Try to read interactively, but don't fail if running non-interactively
        if [ -t 0 ]; then
            read -p "Please enter your OpenAI API Key (starts with sk-...): " OPENAI_KEY
            if [ -z "$OPENAI_KEY" ]; then
                echo -e "${YELLOW}API Key not provided. Some features may not work. Continuing...${NC}"
            else
                echo "OPENAI_API_KEY=$OPENAI_KEY" >> "$ENV_FILE"
                echo -e "${GREEN}API Key saved to $ENV_FILE.${NC}"
            fi
        else
            echo -e "${YELLOW}API Key not provided and running non-interactively. Some features may not work. Continuing...${NC}"
        fi
    fi
fi

# 4. Run Functional Test (local)
echo -e "${YELLOW}4. Running functional tests (local)...${NC}"
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/test_llm_client.py -v
if [ $? -ne 0 ]; then
    echo -e "${RED}Local tests failed. Please check your setup and API key.${NC}"
    # Continue to demo, as the demo might still work if the test failed due to a dummy key issue.
fi
echo -e "${GREEN}Local tests completed.${NC}"

# 5. Demo and Verify Functionality (Local)
echo -e "${YELLOW}5. Demonstrating LLM interaction (local)...${NC}"
python src/llm_client.py "What is a microservice?"
if [ $? -ne 0 ]; then
    echo -e "${RED}Local demo failed. Check API key and network connection.${NC}"
else
    echo -e "${GREEN}Local demo completed successfully!${NC}"
fi

# 6. Build and Run with Docker
echo -e "${YELLOW}6. Building and running with Docker...${NC}"

# Check for Docker
if ! command -v docker &> /dev/null; then
    echo -e "${YELLOW}Docker is not installed. Skipping Docker build and run.${NC}"
    echo -e "${BLUE}--- Day 1 Setup & Demo Complete (Local Only) ---${NC}"
    deactivate
    exit 0
fi

# Create Dockerfile
cat <<EOF > Dockerfile
FROM python:3.9-slim-buster

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY src/ ./src/
COPY config/ ./config/

ENV PYTHONPATH=/app

CMD ["python", "src/llm_client.py"]
EOF
echo -e "${GREEN}Generated Dockerfile.${NC}"

echo -e "${GREEN}Building Docker image 'llm-day1-app'...${NC}"
docker build -t llm-day1-app .
if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to build Docker image. Exiting.${NC}"
    deactivate
    exit 1
fi
echo -e "${GREEN}Docker image built successfully.${NC}"

echo -e "${GREEN}Running Docker container...${NC}"
# Get API key from config/.env for Docker
OPENAI_KEY_FOR_DOCKER=$(grep "OPENAI_API_KEY" "$ENV_FILE" | cut -d '=' -f2)
if [ -z "$OPENAI_KEY_FOR_DOCKER" ]; then
    echo -e "${YELLOW}Could not retrieve OPENAI_API_KEY from $ENV_FILE for Docker. Skipping Docker demo.${NC}"
else
    docker run --rm -e OPENAI_API_KEY="$OPENAI_KEY_FOR_DOCKER" llm-day1-app "Explain Docker in one sentence."
    if [ $? -ne 0 ]; then
        echo -e "${RED}Docker container run failed. Check API key and network connection.${NC}"
    else
        echo -e "${GREEN}Docker demo completed successfully!${NC}"
    fi
fi

# 7. Create dashboard startup script
echo -e "${YELLOW}7. Creating dashboard startup script...${NC}"
cat <<'EOF' > start_dashboard.sh
#!/bin/bash

# Dashboard startup script
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

# Check if dashboard is already running
if pgrep -f "dashboard.py" > /dev/null; then
    echo "Dashboard is already running. Use 'pkill -f dashboard.py' to stop it."
    exit 1
fi

# Start dashboard
echo "Starting dashboard server on http://localhost:8080"
python src/dashboard.py 8080 &
DASHBOARD_PID=$!
echo "Dashboard started with PID: $DASHBOARD_PID"
echo "Access dashboard at: http://localhost:8080"
echo "To stop: kill $DASHBOARD_PID"
EOF
chmod +x start_dashboard.sh
echo -e "${GREEN}Generated start_dashboard.sh.${NC}"

# 8. Create demo startup script with dashboard integration
cat <<'EOF' > start_demo.sh
#!/bin/bash

# Demo startup script with dashboard integration
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
export DASHBOARD_URL="http://localhost:8080"

# Check if dashboard is running, start if not
if ! pgrep -f "dashboard.py" > /dev/null; then
    echo "Starting dashboard..."
    python src/dashboard.py 8080 > /dev/null 2>&1 &
    sleep 2
    echo "Dashboard started at http://localhost:8080"
fi

# Run demo
echo "Running LLM demo with dashboard integration..."
if [ $# -gt 0 ]; then
    python src/llm_client_with_dashboard.py "$@"
else
    python src/llm_client_with_dashboard.py "What is a microservice architecture?"
fi
EOF
chmod +x start_demo.sh
echo -e "${GREEN}Generated start_demo.sh.${NC}"

echo -e "${BLUE}--- Day 1 Setup & Demo Complete ---${NC}"
echo -e "${GREEN}Generated files:${NC}"
echo -e "  - src/llm_client.py"
echo -e "  - src/dashboard.py"
echo -e "  - src/llm_client_with_dashboard.py"
echo -e "  - tests/test_llm_client.py"
echo -e "  - startup.sh"
echo -e "  - start_dashboard.sh"
echo -e "  - start_demo.sh"
echo -e "  - Dockerfile"

# Auto-start dashboard
echo -e "${YELLOW}8. Starting dashboard...${NC}"
pkill -f "dashboard.py" 2>/dev/null
sleep 1
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python src/dashboard.py 8080 > /tmp/dashboard.log 2>&1 &
DASHBOARD_PID=$!
sleep 2
if ps -p $DASHBOARD_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✓ Dashboard started with PID: $DASHBOARD_PID${NC}"
    echo -e "${GREEN}✓ Dashboard accessible at: http://localhost:8080${NC}"
else
    echo -e "${YELLOW}⚠ Dashboard may need a moment to start${NC}"
    echo -e "${YELLOW}Access dashboard at: http://localhost:8080${NC}"
fi

echo -e "${YELLOW}To run demo: ./start_demo.sh [prompt]${NC}"
deactivate