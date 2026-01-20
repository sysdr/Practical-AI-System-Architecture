#!/bin/bash
set -e

echo "=== Docker Cleanup Script ==="

# Stop all running containers
echo "Stopping all running Docker containers..."
docker ps -q | xargs -r docker stop 2>/dev/null || echo "No running containers to stop"

# Remove all containers
echo "Removing all Docker containers..."
docker ps -a -q | xargs -r docker rm 2>/dev/null || echo "No containers to remove"

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -a -f 2>/dev/null || echo "No unused images to remove"

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -f 2>/dev/null || echo "No unused volumes to remove"

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -f 2>/dev/null || echo "No unused networks to remove"

# Remove all unused resources (comprehensive cleanup)
echo "Performing comprehensive Docker cleanup..."
docker system prune -a --volumes -f 2>/dev/null || echo "Docker cleanup completed"

echo "=== Docker cleanup completed ==="
