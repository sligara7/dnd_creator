#!/bin/bash

# Development startup script for D&D Character Creator
# This script safely passes your local API key to the container

set -e

echo "🧙‍♂️ Starting D&D Character Creator with secure API key handling..."

# Check if OPENAI_API_KEY is set
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY environment variable is not set!"
    echo "Please set it with: export OPENAI_API_KEY='your_key_here'"
    echo "Or load from .env.local: set -a; source .env.local; set +a"
    exit 1
fi

# Clean up any existing container
echo "🧹 Cleaning up existing containers..."
podman stop dnd-char-creator 2>/dev/null || true
podman rm dnd-char-creator 2>/dev/null || true

# Build the container
echo "🔨 Building container..."
podman build -t dnd-char-creator -f backend/Dockerfile .

# Start with secure environment variable passing
echo "🚀 Starting container with secure API key..."
podman run -d \
    --name dnd-char-creator \
    -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    -e OLLAMA_HOST="${OLLAMA_HOST:-http://host.containers.internal:11434}" \
    -e ENV="${ENV:-development}" \
    -e PYTHONPATH=/app \
    dnd-char-creator

# Wait for startup
echo "⏳ Waiting for API to start..."
sleep 5

# Test the API
echo "🧪 Testing API health..."
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ D&D Character Creator API is running!"
    echo "📖 API Documentation: http://localhost:8000/docs"
    echo "🔍 API Health: http://localhost:8000/health"
    echo ""
    echo "🛑 To stop: podman stop dnd-char-creator"
    echo "📋 To view logs: podman logs dnd-char-creator"
else
    echo "❌ API failed to start. Check logs with: podman logs dnd-char-creator"
    exit 1
fi
