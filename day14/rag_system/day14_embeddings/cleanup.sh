#!/bin/bash

# =======================================================
# Day 14 Embeddings - Cleanup Script
# =======================================================
# This script stops containers, removes unused Docker resources,
# and cleans up project artifacts.

set -e

echo "======================================================="
echo "  Day 14 Embeddings - Cleanup Script"
echo "======================================================="

# --- Configuration ---
CONTAINER_NAME="day14-embeddings-container"
IMAGE_NAME="day14-embeddings-app"
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# --- Stop and Remove Containers ---
echo ""
echo "[1/6] Stopping and removing project containers..."
if docker ps -a --format '{{.Names}}' | grep -q "^${CONTAINER_NAME}$"; then
    docker stop "$CONTAINER_NAME" 2>/dev/null || true
    docker rm "$CONTAINER_NAME" 2>/dev/null || true
    echo "  - Container '$CONTAINER_NAME' stopped and removed."
else
    echo "  - Container '$CONTAINER_NAME' not found. Skipping."
fi

# --- Stop All Running Containers (Optional) ---
echo ""
echo "[2/6] Stopping all running containers..."
RUNNING_CONTAINERS=$(docker ps -q 2>/dev/null)
if [ -n "$RUNNING_CONTAINERS" ]; then
    docker stop $RUNNING_CONTAINERS 2>/dev/null || true
    echo "  - All running containers stopped."
else
    echo "  - No running containers found."
fi

# --- Remove Project Docker Image ---
echo ""
echo "[3/6] Removing project Docker image..."
if docker images --format '{{.Repository}}' | grep -q "^${IMAGE_NAME}$"; then
    docker rmi "$IMAGE_NAME" 2>/dev/null || true
    echo "  - Image '$IMAGE_NAME' removed."
else
    echo "  - Image '$IMAGE_NAME' not found. Skipping."
fi

# --- Remove Dangling Images ---
echo ""
echo "[4/6] Removing dangling Docker images..."
DANGLING_IMAGES=$(docker images -f "dangling=true" -q 2>/dev/null)
if [ -n "$DANGLING_IMAGES" ]; then
    docker rmi $DANGLING_IMAGES 2>/dev/null || true
    echo "  - Dangling images removed."
else
    echo "  - No dangling images found."
fi

# --- Remove Unused Volumes ---
echo ""
echo "[5/6] Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || true
echo "  - Unused volumes removed."

# --- Docker System Prune ---
echo ""
echo "[6/6] Running Docker system prune..."
docker system prune -f 2>/dev/null || true
echo "  - Docker system pruned."

# --- Clean Project Artifacts ---
echo ""
echo "======================================================="
echo "  Cleaning Project Artifacts"
echo "======================================================="

# Remove virtual environment
if [ -d "$PROJECT_DIR/venv" ]; then
    rm -rf "$PROJECT_DIR/venv"
    echo "  - Virtual environment removed."
fi

# Remove Python cache
find "$PROJECT_DIR" -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find "$PROJECT_DIR" -name "*.pyc" -delete 2>/dev/null || true
find "$PROJECT_DIR" -name "*.pyo" -delete 2>/dev/null || true
echo "  - Python cache files cleaned."

# Remove pytest cache
find "$PROJECT_DIR" -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
echo "  - Pytest cache cleaned."

# Remove node_modules (if any)
find "$PROJECT_DIR" -type d -name "node_modules" -exec rm -rf {} + 2>/dev/null || true
echo "  - Node modules cleaned."

# Remove Istio files (if any)
find "$PROJECT_DIR" -type f -name "*istio*" -delete 2>/dev/null || true
find "$PROJECT_DIR" -type d -name "*istio*" -exec rm -rf {} + 2>/dev/null || true
echo "  - Istio files cleaned."

# Remove .env files (potentially contain secrets)
# find "$PROJECT_DIR" -name ".env" -delete 2>/dev/null || true
# echo "  - Environment files cleaned."

echo ""
echo "======================================================="
echo "  Cleanup Complete!"
echo "======================================================="
echo ""
echo "Summary of Docker resources:"
docker system df 2>/dev/null || echo "Docker not available"
echo ""
