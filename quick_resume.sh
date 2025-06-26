#!/bin/bash

# Quick Resume Script for D&D Character Creator Development
# Run this script to quickly get back to development state

echo "🚀 D&D Character Creator - Quick Resume Script"
echo "=============================================="

# Check if we're in the right directory
if [ ! -f "test_api_endpoints_refactored.sh" ]; then
    echo "❌ Error: Not in the correct directory. Please cd to /home/ajs7/dnd_tools/dnd_char_creator"
    exit 1
fi

echo "✅ In correct directory"

# Check if Ollama is running
echo "🔍 Checking Ollama service..."
if curl -s http://localhost:11434/api/tags >/dev/null 2>&1; then
    echo "✅ Ollama is running"
    
    # Check if tinyllama model is available
    if curl -s http://localhost:11434/api/tags | grep -q "tinyllama"; then
        echo "✅ tinyllama model is available"
    else
        echo "⚠️  tinyllama model not found. You may need to run: ollama pull tinyllama:latest"
    fi
else
    echo "❌ Ollama is not running. Please start it with: ollama serve"
    exit 1
fi

# Start the backend
echo "🔄 Starting backend server..."
cd backend

# Check if uvicorn is available
if ! command -v uvicorn &> /dev/null; then
    echo "❌ uvicorn not found. Please install with: pip install uvicorn"
    exit 1
fi

echo "🚀 Starting uvicorn server..."
echo "📝 Backend will be available at http://localhost:8000"
echo "📊 Health check: http://localhost:8000/health"
echo "📖 API docs: http://localhost:8000/docs"
echo ""
echo "🔧 CURRENT ISSUES TO FIX:"
echo "1. Character data structure mismatches in shared_character_generation.py"
echo "2. JSON parsing errors in generators.py"
echo "3. Field name consistency between prompts and models"
echo ""
echo "📁 KEY FILES TO EDIT:"
echo "- backend/shared_character_generation.py (data structure fixes)"
echo "- backend/generators.py (JSON parsing improvements)"
echo ""
echo "🧪 QUICK TESTS TO RUN:"
echo "cd .. && ./test_llm_with_long_timeout.sh"
echo "cd .. && curl -X POST 'http://localhost:8000/api/v1/characters/generate?prompt=Create%20a%20wise%20wizard' --max-time 300"
echo ""
echo "📋 STATUS: Backend starts cleanly, LLM working, but character generation needs data structure fixes"
echo ""
echo "Press Ctrl+C to stop the server when done"

# Start the server
uvicorn app:app --host 0.0.0.0 --port 8000 --reload
