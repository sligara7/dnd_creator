#!/bin/bash
# Podman build and deployment script for D&D Character Creator Backend

set -e

# Configuration
IMAGE_NAME="dnd-character-creator-backend"
IMAGE_TAG="v2.0"
CONTAINER_NAME="dnd-backend-api"
HOST_PORT="8000"
CONTAINER_PORT="8000"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🏗️  Building D&D Character Creator Backend with Podman${NC}"
echo "=================================="

# Check if podman is installed
if ! command -v podman &> /dev/null; then
    echo -e "${RED}❌ Podman is not installed. Please install Podman first.${NC}"
    exit 1
fi

# Stop and remove existing container if it exists
if podman ps -a --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${YELLOW}🛑 Stopping existing container...${NC}"
    podman stop "${CONTAINER_NAME}" || true
    echo -e "${YELLOW}🗑️  Removing existing container...${NC}"
    podman rm "${CONTAINER_NAME}" || true
fi

# Remove existing image if it exists
if podman images --format "{{.Repository}}:{{.Tag}}" | grep -q "^${IMAGE_NAME}:${IMAGE_TAG}$"; then
    echo -e "${YELLOW}🗑️  Removing existing image...${NC}"
    podman rmi "${IMAGE_NAME}:${IMAGE_TAG}" || true
fi

# Build the image
echo -e "${GREEN}🔨 Building Docker image...${NC}"
podman build -t "${IMAGE_NAME}:${IMAGE_TAG}" .

# Create necessary directories for volumes
echo -e "${GREEN}📁 Creating host directories for volumes...${NC}"
mkdir -p "${PWD}/data"
mkdir -p "${PWD}/logs"
mkdir -p "${PWD}/characters"
mkdir -p "${PWD}/custom_content"

# Set proper permissions for rootless Podman
chmod 755 "${PWD}/data" "${PWD}/logs" "${PWD}/characters" "${PWD}/custom_content"

# Check for required environment variables
if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set in environment. LLM features may not work.${NC}"
    echo "   Set it with: export OPENAI_API_KEY=your-key-here"
fi

# Run the container with proper volume mounts and environment variables
echo -e "${GREEN}🚀 Running container...${NC}"
podman run -d \
    --name "${CONTAINER_NAME}" \
    --publish "${HOST_PORT}:${CONTAINER_PORT}" \
    --volume "${PWD}/data:/app/data:Z" \
    --volume "${PWD}/logs:/app/logs:Z" \
    --volume "${PWD}/characters:/app/characters:Z" \
    --volume "${PWD}/custom_content:/app/custom_content:Z" \
    --env OPENAI_API_KEY="${OPENAI_API_KEY:-}" \
    --env ANTHROPIC_API_KEY="${ANTHROPIC_API_KEY:-}" \
    --env DEBUG="${DEBUG:-false}" \
    --env LLM_MODEL="${LLM_MODEL:-gpt-3.5-turbo}" \
    --health-cmd "python -c 'import requests; requests.get(\"http://localhost:8000/health\")'" \
    --health-interval 30s \
    --health-timeout 10s \
    --health-retries 3 \
    "${IMAGE_NAME}:${IMAGE_TAG}"

# Wait a moment for the container to start
echo -e "${YELLOW}⏳ Waiting for container to start...${NC}"
sleep 5

# Check if container is running
if podman ps --format "{{.Names}}" | grep -q "^${CONTAINER_NAME}$"; then
    echo -e "${GREEN}✅ Container is running successfully!${NC}"
    echo "=================================="
    echo -e "${GREEN}🌐 API available at: http://localhost:${HOST_PORT}${NC}"
    echo -e "${GREEN}📊 Health check: http://localhost:${HOST_PORT}/health${NC}"
    echo -e "${GREEN}📚 API docs: http://localhost:${HOST_PORT}/docs${NC}"
    echo "=================================="
    
    # Show container status
    echo -e "${YELLOW}📋 Container Status:${NC}"
    podman ps --filter "name=${CONTAINER_NAME}" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    # Show logs
    echo -e "${YELLOW}📜 Recent logs:${NC}"
    podman logs --tail 10 "${CONTAINER_NAME}"
    
else
    echo -e "${RED}❌ Container failed to start. Checking logs...${NC}"
    podman logs "${CONTAINER_NAME}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Deployment complete!${NC}"
echo ""
echo "Useful commands:"
echo "  View logs:     podman logs -f ${CONTAINER_NAME}"
echo "  Stop:          podman stop ${CONTAINER_NAME}"
echo "  Remove:        podman rm ${CONTAINER_NAME}"
echo "  Shell access:  podman exec -it ${CONTAINER_NAME} bash"
