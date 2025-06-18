#!/bin/bash

# D&D Character Creator - Backend Development Setup Script
# This script sets up only the backend services for development

set -e

echo "🎲 D&D Character Creator - Backend Development Setup"
echo "===================================================="

# Check if podman and podman-compose are installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install podman first."
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo "❌ podman-compose is not installed. Please install podman-compose first."
    exit 1
fi

# Navigate to backend directory
cd "$(dirname "$0")/../../backend"

# Set default environment variables
export DB_PASSWORD=${DB_PASSWORD:-"dnd_dev_password"}
export SECRET_KEY=${SECRET_KEY:-"dnd_dev_secret_key"}
export LLM_PROVIDER=${LLM_PROVIDER:-"ollama"}
export LLM_MODEL=${LLM_MODEL:-"llama3:8b"}
export DEBUG=${DEBUG:-"true"}
export LOG_LEVEL=${LOG_LEVEL:-"DEBUG"}

echo "📋 Development Configuration:"
echo "  - Database Password: [HIDDEN]"
echo "  - LLM Provider: $LLM_PROVIDER"
echo "  - LLM Model: $LLM_MODEL"
echo "  - Debug Mode: $DEBUG"
echo "  - Log Level: $LOG_LEVEL"
echo ""

# Create logs directory
mkdir -p logs

# Create development .env file if it doesn't exist
if [ ! -f .env.dev ]; then
    echo "📝 Creating development .env file..."
    cat > .env.dev << EOF
# Development Database Configuration
DB_PASSWORD=$DB_PASSWORD

# API Configuration
SECRET_KEY=$SECRET_KEY

# LLM Configuration
LLM_PROVIDER=$LLM_PROVIDER
LLM_MODEL=$LLM_MODEL

# Debug Configuration
DEBUG=$DEBUG
LOG_LEVEL=$LOG_LEVEL

# CORS Configuration (allow all for development)
CORS_ORIGINS=*

# External API Keys (optional)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
    echo "✅ Created development .env file"
else
    echo "📄 Using existing .env.dev file"
fi

# Load environment variables
set -a
source .env.dev
set +a

# Pull required images
echo "📦 Pulling required images..."
podman pull postgres:15-alpine

# Build and start backend services
echo "🚀 Starting backend development services..."
podman-compose -f ../deployment/compose/backend-dev.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 20

# Check service status
echo "🔍 Checking service status..."
podman-compose -f ../deployment/compose/backend-dev.yml ps

# Test connectivity
echo "🧪 Testing service connectivity..."

# Test database
if podman exec dnd_character_db_dev pg_isready -U dnd_user -d dnd_characters; then
    echo "✅ Database is ready"
else
    echo "❌ Database is not ready"
fi

# Test backend API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is ready"
else
    echo "❌ Backend API is not ready"
fi

# Test Ollama
if curl -f http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama LLM service is ready"
else
    echo "❌ Ollama LLM service is not ready"
fi

echo ""
echo "🎉 Backend development setup complete!"
echo ""
echo "📋 Service URLs:"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Ollama:    http://localhost:11434"
echo "  - Database:  localhost:5432"
echo ""
echo "🔧 Development commands:"
echo "  - View logs:     podman-compose -f ../deployment/compose/backend-dev.yml logs -f"
echo "  - Stop services: podman-compose -f ../deployment/compose/backend-dev.yml down"
echo "  - Restart:       podman-compose -f ../deployment/compose/backend-dev.yml restart"
echo "  - Shell access:  podman exec -it dnd_character_api_dev /bin/bash"
echo ""
echo "🧪 Testing commands:"
echo "  - Run tests:     podman exec dnd_character_api_dev python -m pytest"
echo "  - Check health:  curl http://localhost:8000/health"
echo ""
echo "📖 For more information, check the README.md file"
