#!/bin/bash

# Cleanup script for Docker resources and project files

echo "=========================================="
echo "Docker Cleanup Script"
echo "=========================================="

# Stop all running containers
echo "Stopping all running containers..."
docker stop $(docker ps -aq) 2>/dev/null || echo "No containers to stop"

# Remove all containers
echo "Removing all containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "No containers to remove"

# Remove unused images
echo "Removing unused Docker images..."
docker image prune -af 2>/dev/null || echo "No unused images to remove"

# Remove unused volumes
echo "Removing unused Docker volumes..."
docker volume prune -af 2>/dev/null || echo "No unused volumes to remove"

# Remove unused networks
echo "Removing unused Docker networks..."
docker network prune -af 2>/dev/null || echo "No unused networks to remove"

# Remove all unused resources (comprehensive cleanup)
echo "Performing comprehensive Docker cleanup..."
docker system prune -af --volumes 2>/dev/null || echo "Docker system cleanup completed"

echo ""
echo "=========================================="
echo "Docker cleanup completed!"
echo "=========================================="
