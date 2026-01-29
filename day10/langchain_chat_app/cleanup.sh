#!/bin/bash
# Cleanup script for LangChain Chatbot project.
# Stops services, stops/removes Docker containers, prunes Docker resources,
# and removes build/cache artifacts (node_modules, venv, .pytest_cache, .pyc, Istio).

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=============================================="
echo "LangChain Chatbot - Cleanup"
echo "=============================================="

# --- 1. Stop project services (dashboard, background_demo) ---
echo ""
echo "1. Stopping project services..."
if [ -f "$PROJECT_DIR/stop.sh" ]; then
    "$PROJECT_DIR/stop.sh"
else
    pkill -f "dashboard.py" 2>/dev/null || true
    pkill -f "background_demo.py" 2>/dev/null || true
    rm -f "$PROJECT_DIR"/dashboard.pid "$PROJECT_DIR"/background_demo.pid
fi
echo "   Services stopped."

# --- 2. Stop and remove Docker containers (project image) ---
echo ""
echo "2. Stopping and removing Docker containers..."
if command -v docker >/dev/null 2>&1; then
    docker ps -a --filter "ancestor=langchain-chat-app:latest" -q 2>/dev/null | xargs -r docker stop 2>/dev/null || true
    docker ps -a --filter "ancestor=langchain-chat-app:latest" -q 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
    docker ps -a -q 2>/dev/null | while read -r cid; do
        if docker inspect "$cid" 2>/dev/null | grep -q "langchain-chat-app"; then
            docker stop "$cid" 2>/dev/null || true
            docker rm -f "$cid" 2>/dev/null || true
        fi
    done
    echo "   Project containers stopped/removed."
else
    echo "   Docker not found, skipping."
fi

# --- 3. Remove unused Docker resources (images, volumes, build cache) ---
echo ""
echo "3. Removing unused Docker resources..."
if command -v docker >/dev/null 2>&1; then
    docker image rm langchain-chat-app:latest 2>/dev/null || true
    docker system prune -af --volumes 2>/dev/null || true
    echo "   Unused Docker resources (images, volumes, build cache) removed."
else
    echo "   Docker not found, skipping."
fi

# --- 4. Remove node_modules ---
echo ""
echo "4. Removing node_modules..."
find "$PROJECT_DIR" -type d -name "node_modules" 2>/dev/null | while read -r d; do rm -rf "$d"; done
echo "   node_modules removed."

# --- 5. Remove Python virtual environments ---
echo ""
echo "5. Removing Python virtual environments..."
for venv_name in .venv venv ENV env; do
    if [ -d "$PROJECT_DIR/$venv_name" ]; then
        echo "   Removing $PROJECT_DIR/$venv_name"
        rm -rf "$PROJECT_DIR/$venv_name"
    fi
done
echo "   Virtual environments removed."

# --- 6. Remove .pytest_cache and __pycache__ ---
echo ""
echo "6. Removing .pytest_cache and __pycache__..."
find "$PROJECT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
echo "   Cache directories removed."

# --- 7. Remove .pyc, .pyo files ---
echo ""
echo "7. Removing .pyc and .pyo files..."
find "$PROJECT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type f -name "*\$py.class" -delete 2>/dev/null || true
echo "   Bytecode files removed."

# --- 8. Remove Istio-related files ---
echo ""
echo "8. Removing Istio files..."
rm -rf "$PROJECT_DIR/istio" 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 4 -type d -name "istio" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 4 -type d -name "istio-*" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 4 -type f \( -name "*.istio.yaml" -o -name "*.istio.yml" -o -name "*.istio" \) -delete 2>/dev/null || true
echo "   Istio files removed."

# --- 9. Remove logs, PIDs, and metrics ---
echo ""
echo "9. Removing logs, PIDs, and metrics..."
rm -f "$PROJECT_DIR"/*.log "$PROJECT_DIR"/*.pid "$PROJECT_DIR"/metrics.json 2>/dev/null || true
echo "   Logs and runtime files removed."

# --- 10. Remove .env (API keys / secrets) ---
echo ""
echo "10. Removing .env (API keys / secrets)..."
rm -f "$PROJECT_DIR/.env" 2>/dev/null || true
echo "   .env removed."

echo ""
echo "=============================================="
echo "Cleanup complete."
echo "=============================================="
