#!/bin/bash
# Cleanup script for RAG Imperative Day11 project.
# Stops project services, stops Docker containers, prunes Docker resources,
# and removes node_modules, venv, .pytest_cache, .pyc, and Istio files.

PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=============================================="
echo "RAG Imperative Day11 - Cleanup"
echo "=============================================="

# --- 1. Stop project services (dashboard, background_demo) ---
echo ""
echo "1. Stopping project services..."
if [ -f "$PROJECT_DIR/stop.sh" ]; then
    "$PROJECT_DIR/stop.sh"
else
    pkill -f "dashboard.py" 2>/dev/null || true
    pkill -f "background_demo.py" 2>/dev/null || true
    rm -f "$PROJECT_DIR"/dashboard.pid "$PROJECT_DIR"/background_demo.pid 2>/dev/null || true
fi
echo "   Services stopped."

# --- 2. Stop Docker containers and remove unused resources ---
echo ""
echo "2. Stopping Docker containers..."
if command -v docker >/dev/null 2>&1; then
    docker stop $(docker ps -q) 2>/dev/null || true
    echo "   Containers stopped."

    echo ""
    echo "3. Removing unused Docker resources (volumes, containers, images)..."
    docker system prune -af --volumes 2>/dev/null || true
    echo "   Unused Docker resources removed."
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
echo "5. Removing Python virtual environments (venv, .venv)..."
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
find "$PROJECT_DIR" -maxdepth 4 -type d -name "istio" 2>/dev/null | while read -r d; do rm -rf "$d"; done
find "$PROJECT_DIR" -maxdepth 4 -type d -name "istio-*" 2>/dev/null | while read -r d; do rm -rf "$d"; done
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
rm -f "$PROJECT_DIR/.env" "$PROJECT_DIR/.env.*" 2>/dev/null || true
echo "   .env removed."

echo ""
echo "=============================================="
echo "Cleanup complete."
echo "=============================================="
