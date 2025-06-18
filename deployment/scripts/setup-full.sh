#!/bin/bash

# D&D Character Creator - Full Stack Setup Script
# This script sets up the complete application stack using Podman

set -e

echo "🎲 D&D Character Creator - Full Stack Setup"
echo "============================================="

# Check if podman and podman-compose are installed
if ! command -v podman &> /dev/null; then
    echo "❌ Podman is not installed. Please install podman first."
    exit 1
fi

if ! command -v podman-compose &> /dev/null; then
    echo "❌ podman-compose is not installed. Please install podman-compose first."
    exit 1
fi

# Set default environment variables
export DB_PASSWORD=${DB_PASSWORD:-"dnd_secure_password_$(date +%s)"}
export SECRET_KEY=${SECRET_KEY:-"dnd_secret_key_$(openssl rand -hex 32)"}
export LLM_PROVIDER=${LLM_PROVIDER:-"ollama"}
export LLM_MODEL=${LLM_MODEL:-"llama3:8b"}
export DEBUG=${DEBUG:-"false"}
export LOG_LEVEL=${LOG_LEVEL:-"INFO"}

echo "📋 Configuration:"
echo "  - Database Password: [HIDDEN]"
echo "  - LLM Provider: $LLM_PROVIDER"
echo "  - LLM Model: $LLM_MODEL"
echo "  - Debug Mode: $DEBUG"
echo ""

# Create logs directory
mkdir -p backend/logs
mkdir -p ai_services/ollama/logs
mkdir -p ai_services/stable_diffusion/logs

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cat > .env << EOF
# Database Configuration
DB_PASSWORD=$DB_PASSWORD

# API Configuration
SECRET_KEY=$SECRET_KEY

# LLM Configuration
LLM_PROVIDER=$LLM_PROVIDER
LLM_MODEL=$LLM_MODEL

# Debug Configuration
DEBUG=$DEBUG
LOG_LEVEL=$LOG_LEVEL

# CORS Configuration
CORS_ORIGINS=http://localhost:3000

# External API Keys (optional)
# OPENAI_API_KEY=your_openai_key_here
# ANTHROPIC_API_KEY=your_anthropic_key_here
EOF
    echo "✅ Created .env file"
else
    echo "📄 Using existing .env file"
fi

# Pull required images
echo "📦 Pulling required images..."
podman pull postgres:15-alpine
podman pull nvidia/cuda:11.8-runtime-ubuntu20.04 || echo "⚠️  CUDA image not available, GPU features may not work"

# Build and start services
echo "🚀 Starting D&D Character Creator services..."
podman-compose -f podman-compose.yml up -d --build

# Wait for services to be healthy
echo "⏳ Waiting for services to start..."
sleep 30

# Check service status
echo "🔍 Checking service status..."
podman-compose -f podman-compose.yml ps

# Test connectivity
echo "🧪 Testing service connectivity..."

# Test database
if podman exec dnd_character_db pg_isready -U dnd_user -d dnd_characters; then
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

# Test frontend
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Frontend is ready"
else
    echo "❌ Frontend is not ready"
fi

# Test Ollama
if curl -f http://localhost:11434/api/version > /dev/null 2>&1; then
    echo "✅ Ollama LLM service is ready"
else
    echo "❌ Ollama LLM service is not ready"
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "📋 Service URLs:"
echo "  - Frontend:  http://localhost:3000"
echo "  - Backend:   http://localhost:8000"
echo "  - API Docs:  http://localhost:8000/docs"
echo "  - Ollama:    http://localhost:11434"
echo "  - Database:  localhost:5432"
echo ""
echo "🔧 Management commands:"
echo "  - View logs:     podman-compose -f podman-compose.yml logs -f"
echo "  - Stop services: podman-compose -f podman-compose.yml down"
echo "  - Restart:       podman-compose -f podman-compose.yml restart"
echo ""
echo "📖 For more information, check the README.md file"
