#!/bin/bash
# Cleanup script for multi-step LLM project
# Stops local services, Docker containers; removes unused Docker resources;
# removes node_modules, venv, .venv, .pytest_cache, .pyc, Istio files

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=============================================="
echo "  Multi-Step LLM Project Cleanup"
echo "=============================================="
echo ""

# Stop local services if running
echo "[1/4] Stopping local services..."
if [ -f "stop.sh" ]; then
    ./stop.sh
fi
pkill -f "dashboard.py" 2>/dev/null || true
pkill -f "background_demo.py" 2>/dev/null || true
echo "  Done."
echo ""

# Stop Docker containers and remove unused resources
echo "[2/4] Stopping containers and pruning unused Docker resources..."
if command -v docker &>/dev/null; then
    docker ps -aq 2>/dev/null | xargs -r docker stop 2>/dev/null || true
    docker ps -aq 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
    docker system prune -af --volumes 2>/dev/null || true
    echo "  Docker cleanup complete."
else
    echo "  Docker not found, skipping."
fi
echo ""

# Remove node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio
echo "[3/4] Removing node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio..."
find "$PROJECT_DIR" -maxdepth 3 -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 3 -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 3 -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 3 -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 4 -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 4 -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 3 -type d -name "istio" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -maxdepth 3 -type f \( -name "*.istio.yaml" -o -name "*.istio.yml" \) -delete 2>/dev/null || true
echo "  Done."
echo ""

# Remove logs and PIDs
echo "[4/4] Removing logs and PID files..."
rm -f "$PROJECT_DIR"/*.log "$PROJECT_DIR"/*.pid "$PROJECT_DIR"/metrics.json 2>/dev/null || true
echo "  Done."
echo ""

echo "=============================================="
echo "  Cleanup complete."
echo "=============================================="
