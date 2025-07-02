#!/bin/bash
# Helper script to run the D&D Character Creator backend container with OpenAI API key
# Usage: ./run_container_with_api_key.sh

echo "D&D Character Creator Backend - Container Startup"
echo "================================================="
echo ""

# Check if API key is provided as argument
if [ "$1" != "" ]; then
    OPENAI_API_KEY="$1"
else
    # Prompt for API key
    echo "Enter your OpenAI API key:"
    echo "(Get it from: https://platform.openai.com/account/api-keys)"
    read -s OPENAI_API_KEY
    echo ""
fi

# Validate API key format (should start with )
if [[ ! $OPENAI_API_KEY =~ ^ ]]; then
    echo "❌ Invalid API key format. OpenAI API keys should start with ''"
    echo "Please get your API key from: https://platform.openai.com/account/api-keys"
    exit 1
fi

# Stop and remove any existing container
echo "🛑 Stopping any existing container..."
podman stop dnd-backend-test 2>/dev/null || true
podman rm dnd-backend-test 2>/dev/null || true

# Start the container with the API key
echo "🚀 Starting D&D Character Creator backend container..."
podman run -d \
    --name dnd-backend-test \
    -p 8000:8000 \
    -e OPENAI_API_KEY="$OPENAI_API_KEY" \
    localhost/dnd-char-creator-backend:latest

if [ $? -eq 0 ]; then
    echo "✅ Container started successfully!"
    echo ""
    echo "🌐 API Documentation: http://localhost:8000/docs"
    echo "❤️  Health Check: http://localhost:8000/health"
    echo ""
    echo "Waiting for container to be ready..."
    sleep 5
    
    # Test the health endpoint
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ Backend is ready and responding!"
        echo ""
        echo "📝 Test character creation:"
        echo "curl -X POST http://localhost:8000/api/v2/factory/create \\"
        echo "  -H 'Content-Type: application/json' \\"
        echo "  -d '{\"creation_type\": \"character\", \"prompt\": \"Create a level 1 Human Fighter\"}'"
    else
        echo "⚠️  Backend is starting... check logs with: podman logs dnd-backend-test"
    fi
else
    echo "❌ Failed to start container"
    exit 1
fi
