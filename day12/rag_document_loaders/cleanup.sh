#!/bin/bash
# Cleanup script for RAG Document Loader project
# This script stops all services and removes Docker resources

set -e

echo "=== RAG Document Loader Cleanup Script ==="
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# --- Stop Services ---
echo "[1/6] Stopping services..."
pkill -f "python dashboard.py" 2>/dev/null && echo "  - Stopped dashboard" || echo "  - Dashboard not running"
pkill -f "flask" 2>/dev/null && echo "  - Stopped Flask" || echo "  - Flask not running"

# --- Stop Docker Containers ---
echo ""
echo "[2/6] Stopping Docker containers..."
CONTAINERS=$(docker ps -a --filter "name=rag-loader" --format "{{.Names}}" 2>/dev/null || true)
if [ -n "$CONTAINERS" ]; then
    echo "$CONTAINERS" | xargs -r docker stop 2>/dev/null && echo "  - Stopped containers" || true
    echo "$CONTAINERS" | xargs -r docker rm 2>/dev/null && echo "  - Removed containers" || true
else
    echo "  - No rag-loader containers found"
fi

# --- Remove Docker Images ---
echo ""
echo "[3/6] Removing Docker images..."
IMAGES=$(docker images --filter "reference=rag-loader*" --format "{{.Repository}}:{{.Tag}}" 2>/dev/null || true)
if [ -n "$IMAGES" ]; then
    echo "$IMAGES" | xargs -r docker rmi 2>/dev/null && echo "  - Removed images" || echo "  - Could not remove some images (may be in use)"
else
    echo "  - No rag-loader images found"
fi

# --- Clean Docker System ---
echo ""
echo "[4/6] Cleaning unused Docker resources..."
docker system prune -f 2>/dev/null && echo "  - Pruned unused containers, networks, and dangling images" || echo "  - Docker prune skipped"

# --- Remove Dangling Volumes ---
echo ""
echo "[5/6] Removing dangling Docker volumes..."
DANGLING_VOLUMES=$(docker volume ls -qf dangling=true 2>/dev/null || true)
if [ -n "$DANGLING_VOLUMES" ]; then
    echo "$DANGLING_VOLUMES" | xargs -r docker volume rm 2>/dev/null && echo "  - Removed dangling volumes" || echo "  - Could not remove some volumes"
else
    echo "  - No dangling volumes found"
fi

# --- Clean Python Cache ---
echo ""
echo "[6/6] Cleaning Python cache files..."
find "$SCRIPT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyc" -delete 2>/dev/null || true
find "$SCRIPT_DIR" -type f -name "*.pyo" -delete 2>/dev/null || true
echo "  - Removed Python cache files"

echo ""
echo "=== Cleanup Complete ==="
echo ""
echo "Optional: To remove virtual environment, run:"
echo "  rm -rf $SCRIPT_DIR/.venv"
echo ""
echo "Optional: To remove all generated data, run:"
echo "  rm -rf $SCRIPT_DIR/data $SCRIPT_DIR/metrics.json"
