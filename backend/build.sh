#!/bin/bash
# Production Build and Run Script for D&D Character Creator Backend

set -e

echo "🏗️  Building D&D Character Creator Backend..."

# Check if .env exists, if not copy from example
if [ ! -f .env ]; then
    echo "📋 Creating .env from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env file with your configuration before running in production!"
fi

# Build the container
echo "🔨 Building container with Podman..."
podman build -t dnd-character-creator-backend:latest .

echo "✅ Build complete!"
echo ""
echo "🚀 To run the container:"
echo "   podman run -d --name dnd-backend \\"
echo "     -p 8000:8000 \\"
echo "     -v \$(pwd)/data:/app/data \\"
echo "     dnd-character-creator-backend:latest"
echo ""
echo "🔍 To view logs:"
echo "   podman logs -f dnd-backend"
echo ""
echo "🛑 To stop:"
echo "   podman stop dnd-backend && podman rm dnd-backend"
echo ""
echo "📡 API will be available at: http://localhost:8000"
echo "📚 API docs will be available at: http://localhost:8000/docs"
