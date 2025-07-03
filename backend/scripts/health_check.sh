#!/bin/bash
# Health check script for D&D Character Creator Backend

set -e

echo "🏥 D&D Character Creator Backend - Health Check"
echo "================================================"

# Check if the backend structure is correct
echo "📁 Checking directory structure..."
if [ ! -d "src" ]; then
    echo "❌ src/ directory not found"
    exit 1
fi

if [ ! -d "src/core" ] || [ ! -d "src/models" ] || [ ! -d "src/services" ]; then
    echo "❌ Required source directories not found"
    exit 1
fi

echo "✅ Directory structure is correct"

# Check if required files exist
echo "📄 Checking required files..."
required_files=("app.py" "main.py" "requirements.txt" "Dockerfile" ".env.example")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Required file $file not found"
        exit 1
    fi
done

echo "✅ All required files present"

# Check if Python modules can be imported (if Python is available)
if command -v python3 &> /dev/null; then
    echo "🐍 Testing Python imports..."
    
    export PYTHONPATH="$PWD:$PWD/src"
    
    # Test basic imports
    python3 -c "
import sys
sys.path.insert(0, 'src')

try:
    from src.core.config import Settings
    from src.models.character_models import CharacterCore
    print('✅ Core imports successful')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"
else
    echo "⚠️  Python3 not available, skipping import tests"
fi

# Check if Podman/Docker is available
echo "🐳 Checking container runtime..."
if command -v podman &> /dev/null; then
    echo "✅ Podman is available"
    CONTAINER_CMD="podman"
elif command -v docker &> /dev/null; then
    echo "✅ Docker is available"
    CONTAINER_CMD="docker"
else
    echo "⚠️  No container runtime found (Podman/Docker)"
    CONTAINER_CMD=""
fi

# Test container build (if runtime available and user wants to)
if [ -n "$CONTAINER_CMD" ] && [ "$1" = "--build-test" ]; then
    echo "🔨 Testing container build..."
    $CONTAINER_CMD build -t dnd-backend-test .
    echo "✅ Container build successful"
    
    # Clean up test image
    $CONTAINER_CMD rmi dnd-backend-test
fi

echo ""
echo "🎉 Health check completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Copy .env.example to .env and configure your API keys"
echo "  2. Run: ./scripts/build_and_run.sh (with Podman)"
echo "  3. Or run: docker-compose -f docker-compose.dev.yml up --build"
echo "  4. Access API at: http://localhost:8000"
echo ""
