#!/bin/bash

# D&D Character Creator - Cleanup Script
# This script removes old Docker containers and images

set -e

echo "🧹 D&D Character Creator - Cleanup"
echo "=================================="

# Remove old docker-compose.yml
if [ -f "docker-compose.yml" ]; then
    echo "🗑️  Removing old docker-compose.yml..."
    rm -f docker-compose.yml
    echo "✅ Removed docker-compose.yml"
fi

# Stop and remove any running Docker containers
echo "🛑 Stopping any running Docker containers..."
if command -v docker &> /dev/null; then
    docker stop $(docker ps -aq --filter "name=dnd_character*") 2>/dev/null || true
    docker rm $(docker ps -aq --filter "name=dnd_character*") 2>/dev/null || true
    echo "✅ Stopped and removed Docker containers"
fi

# Stop and remove any running Podman containers
echo "🛑 Stopping any running Podman containers..."
if command -v podman &> /dev/null; then
    podman stop $(podman ps -aq --filter "name=dnd_character*") 2>/dev/null || true
    podman rm $(podman ps -aq --filter "name=dnd_character*") 2>/dev/null || true
    echo "✅ Stopped and removed Podman containers"
fi

# Clean up Docker images (optional)
read -p "🗑️  Do you want to remove Docker images as well? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v docker &> /dev/null; then
        docker rmi $(docker images --filter "reference=dnd_char_creator*" -q) 2>/dev/null || true
        echo "✅ Removed Docker images"
    fi
fi

# Clean up Podman images (optional)
read -p "🗑️  Do you want to remove Podman images as well? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v podman &> /dev/null; then
        podman rmi $(podman images --filter "reference=dnd_char_creator*" -q) 2>/dev/null || true
        echo "✅ Removed Podman images"
    fi
fi

# Clean up volumes (optional)
read -p "⚠️  Do you want to remove data volumes? This will DELETE ALL DATA! (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    if command -v docker &> /dev/null; then
        docker volume rm $(docker volume ls -q --filter "name=dnd_char_creator*") 2>/dev/null || true
    fi
    if command -v podman &> /dev/null; then
        podman volume rm $(podman volume ls -q --filter "name=dnd_char_creator*") 2>/dev/null || true
    fi
    echo "✅ Removed data volumes"
fi

echo ""
echo "🎉 Cleanup complete!"
echo ""
echo "📋 Next steps:"
echo "  - Run setup-full.sh for complete application"
echo "  - Run setup-backend-dev.sh for backend development"
