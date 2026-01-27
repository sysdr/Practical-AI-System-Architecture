#!/bin/bash

# Get absolute path of project directory (where this script is located)
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

echo "=========================================="
echo "Docker Cleanup Script"
echo "=========================================="

# Stop all running containers
echo "Stopping all running Docker containers..."
docker ps -q | xargs -r docker stop 2>/dev/null || true

# Remove all stopped containers
echo "Removing all stopped containers..."
docker ps -aq | xargs -r docker rm 2>/dev/null || true

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -af 2>/dev/null || true

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -af 2>/dev/null || true

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -af 2>/dev/null || true

# Remove all unused Docker resources (containers, networks, images, build cache)
echo "Removing all unused Docker resources..."
docker system prune -af --volumes 2>/dev/null || true

echo ""
echo "=========================================="
echo "Docker cleanup completed!"
echo "=========================================="
