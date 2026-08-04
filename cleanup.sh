#!/bin/bash
# Cleanup script for Practical-AI-System-Architecture project
# Stops all services, Docker containers; removes unused Docker resources;
# removes node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio files

set -e

PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_ROOT"

echo "=============================================="
echo "  Practical-AI-System-Architecture Cleanup"
echo "=============================================="
echo ""

# --- 1. Stop local services (dashboard, background_demo, etc.) ---
echo "[1/4] Stopping local services..."
for dir in day6/project_day6_multi_step_llm day5/llm_structured_output day4/llm_switching_project; do
    if [ -f "$PROJECT_ROOT/$dir/stop.sh" ]; then
        (cd "$PROJECT_ROOT/$dir" && bash stop.sh) 2>/dev/null || true
    fi
done
pkill -f "dashboard.py" 2>/dev/null || true
pkill -f "background_demo.py" 2>/dev/null || true
echo "  Done."
echo ""

# --- 2. Stop Docker containers and remove unused resources ---
echo "[2/4] Stopping Docker containers and pruning unused resources..."
if command -v docker &>/dev/null; then
    # Stop all running containers
    docker ps -aq 2>/dev/null | xargs -r docker stop 2>/dev/null || true
    # Remove all stopped containers
    docker ps -aq 2>/dev/null | xargs -r docker rm -f 2>/dev/null || true
    # Remove unused images, containers, networks; optional: --volumes to remove volumes
    docker system prune -af --volumes 2>/dev/null || true
    echo "  Docker cleanup complete."
else
    echo "  Docker not found, skipping."
fi
echo ""

# --- 3. Remove node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio files ---
echo "[3/4] Removing node_modules, venv, .venv, .pytest_cache, .pyc, __pycache__, Istio..."
find "$PROJECT_ROOT" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "venv" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".venv" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_ROOT" -type d -name "istio" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_ROOT" -type f \( -name "*.istio.yaml" -o -name "*.istio.yml" \) -delete 2>/dev/null || true
echo "  Done."
echo ""

# --- 4. Remove PID/log artifacts in subprojects ---
echo "[4/4] Removing logs and PID files in subprojects..."
find "$PROJECT_ROOT" -maxdepth 4 -type f \( -name "*.log" -o -name "*.pid" \) -delete 2>/dev/null || true
# Preserve meaningful logs if you prefer; here we clean common runtime artifacts
echo "  Done."
echo ""

echo "=============================================="
echo "  Cleanup complete."
echo "=============================================="
