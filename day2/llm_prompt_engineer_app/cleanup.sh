#!/bin/bash

# Cleanup script for Docker resources and project files
set -e

echo "=========================================="
echo "Docker and Project Cleanup Script"
echo "=========================================="

# Stop all running containers
echo "--- Stopping all Docker containers ---"
if [ $(docker ps -q | wc -l) -gt 0 ]; then
    docker stop $(docker ps -q)
    echo "Stopped all running containers"
else
    echo "No running containers to stop"
fi

# Remove all containers
echo "--- Removing all Docker containers ---"
if [ $(docker ps -aq | wc -l) -gt 0 ]; then
    docker rm $(docker ps -aq) 2>/dev/null || true
    echo "Removed all containers"
else
    echo "No containers to remove"
fi

# Remove unused Docker resources
echo "--- Removing unused Docker resources ---"
docker system prune -af --volumes

# Remove unused images
echo "--- Removing unused Docker images ---"
docker image prune -af

# Remove unused volumes
echo "--- Removing unused Docker volumes ---"
docker volume prune -af

# Remove unused networks
echo "--- Removing unused Docker networks ---"
docker network prune -f

echo ""
echo "=========================================="
echo "Cleanup completed successfully!"
echo "=========================================="
echo ""
echo "Docker resources cleaned:"
echo "  - Stopped and removed all containers"
echo "  - Removed unused images"
echo "  - Removed unused volumes"
echo "  - Removed unused networks"
echo "  - Pruned system resources"
