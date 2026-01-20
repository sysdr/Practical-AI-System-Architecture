#!/bin/bash

# Cleanup script for Docker resources and project files
# This script stops containers and removes unused Docker resources

set -e

echo "=== Docker Cleanup Script ==="

# Stop all running containers
echo "1. Stopping all running Docker containers..."
docker stop $(docker ps -q) 2>/dev/null || echo "   No running containers to stop"

# Remove all stopped containers
echo "2. Removing stopped containers..."
docker rm $(docker ps -aq) 2>/dev/null || echo "   No stopped containers to remove"

# Remove unused images
echo "3. Removing unused Docker images..."
docker image prune -af || echo "   No unused images to remove"

# Remove unused volumes
echo "4. Removing unused Docker volumes..."
docker volume prune -af || echo "   No unused volumes to remove"

# Remove unused networks
echo "5. Removing unused Docker networks..."
docker network prune -f || echo "   No unused networks to remove"

# Remove all unused resources (comprehensive cleanup)
echo "6. Performing comprehensive Docker cleanup..."
docker system prune -af --volumes || echo "   No additional resources to clean"

echo ""
echo "=== Docker Cleanup Complete ==="
echo "Removed:"
echo "  - Stopped containers"
echo "  - Unused images"
echo "  - Unused volumes"
echo "  - Unused networks"
echo "  - All unused Docker resources"
