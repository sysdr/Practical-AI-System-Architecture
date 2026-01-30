#!/bin/bash
echo "=== RAG Document Loader Cleanup Script ==="

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Stop dashboard process
echo "Stopping dashboard process..."
pkill -f "python dashboard.py" 2>/dev/null || echo "Dashboard not running"

# Stop any running containers
CONTAINER_NAME="rag-loader-container"
IMAGE_NAME="rag-loader-app"

echo "Stopping Docker container '$CONTAINER_NAME'..."
docker stop "$CONTAINER_NAME" 2>/dev/null || echo "Container not running"
docker rm "$CONTAINER_NAME" 2>/dev/null || echo "Container not found"

echo "Removing Docker image '$IMAGE_NAME'..."
docker rmi "$IMAGE_NAME" 2>/dev/null || echo "Image not found"

echo "Cleanup complete!"
