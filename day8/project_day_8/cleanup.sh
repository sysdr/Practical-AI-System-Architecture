#!/bin/bash
# Cleanup script for reliable output parsing project
# Stops containers, removes unused Docker resources, and cleans project artifacts

set -e

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "Cleanup: Reliable Output Parsing Project"
echo "=========================================="
echo ""

# 1. Stop application services
echo "[1/4] Stopping application services..."
if [ -f "$PROJECT_DIR/stop.sh" ]; then
    ./stop.sh
else
    pkill -f "dashboard.py" 2>/dev/null || true
    pkill -f "background_demo.py" 2>/dev/null || true
    echo "  App services stopped."
fi
echo ""

# 2. Stop Docker containers and remove unused resources
echo "[2/4] Stopping Docker containers and removing unused resources..."
if command -v docker &>/dev/null; then
    # Stop all running containers
    if [ -n "$(docker ps -aq 2>/dev/null)" ]; then
        docker stop $(docker ps -aq) 2>/dev/null || true
        echo "  Containers stopped."
    fi
    # Remove unused containers, networks, images, and volumes
    docker system prune -af --volumes 2>/dev/null || true
    echo "  Docker cleanup complete (containers, images, volumes, networks pruned)."
else
    echo "  Docker not found. Skipping Docker cleanup."
fi
echo ""

# 3. Remove project artifacts: node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio files
echo "[3/4] Removing node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio files..."
rm -rf node_modules 2>/dev/null || true
rm -rf venv 2>/dev/null || true
rm -rf .venv 2>/dev/null || true
rm -rf .pytest_cache 2>/dev/null || true
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
rm -rf istio 2>/dev/null || true
find . -maxdepth 3 -type f \( -name "*.istio.yaml" -o -name "*.istio.yml" \) -delete 2>/dev/null || true
echo "  Project artifacts removed."
echo ""

# 4. Remove logs, PIDs, and generated metrics
echo "[4/4] Removing logs, PIDs, and metrics..."
rm -f *.log *.pid metrics.json 2>/dev/null || true
echo "  Logs and runtime files removed."
echo ""

echo "=========================================="
echo "Cleanup complete."
echo "=========================================="
