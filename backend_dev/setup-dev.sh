#!/bin/bash

# Local Development Setup Script for D&D Character Creator
# This script helps set up the environment for local development while
# following the same patterns used in production with GitHub secrets

set -e

echo "🚀 Setting up D&D Character Creator for local development"
echo "=================================================="

# Check if we're in the backend directory
if [ ! -f "podman-compose.yml" ]; then
    echo "❌ Please run this script from the backend directory"
    exit 1
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "📄 Creating .env file from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo "⚠️  Please edit .env file and add your API keys"
else
    echo "✅ .env file already exists"
fi

# Check for required environment variables
echo ""
echo "🔍 Checking environment configuration..."

if ! grep -q "OPENAI_API_KEY=" .env || grep -q "OPENAI_API_KEY=$" .env; then
    echo "⚠️  OPENAI_API_KEY not set in .env file"
    echo "   Please add your OpenAI API key to .env file"
    echo "   Example: OPENAI_API_KEY=-..."
fi

if ! grep -q "LLM_MODEL=" .env || grep -q "LLM_MODEL=$" .env; then
    echo "⚠️  LLM_MODEL not set in .env file"
    echo "   Please set your preferred model in .env file"
    echo "   Example: LLM_MODEL=gpt-4.1-nano-2025-04-14"
fi

# Test Python dependencies
echo ""
echo "🐍 Checking Python dependencies..."
if python -c "import openai, dotenv" 2>/dev/null; then
    echo "✅ Required Python packages installed"
else
    echo "📦 Installing required Python packages..."
    pip install openai python-dotenv
fi

# Test OpenAI connection
echo ""
echo "🤖 Testing OpenAI connection..."
python -c "
from llm_services import create_llm_service
try:
    llm = create_llm_service(provider='openai')
    result = llm.generate('Hello, test!', timeout_seconds=10)
    print('✅ OpenAI connection successful')
except Exception as e:
    print(f'❌ OpenAI connection failed: {e}')
    print('   Please check your API key in .env file')
"

# Test character creation
echo ""
echo "🏗️  Testing character creation..."
python -c "
from character_creation import CharacterCreator, CreationConfig
from llm_services import create_llm_service
try:
    llm = create_llm_service(provider='openai')
    creator = CharacterCreator(llm, CreationConfig())
    result = creator.create_character('A brave human fighter', 1, False, False)
    if result.success:
        print('✅ Character creation working')
        print(f'   Created: {result.data.get(\"name\", \"Unknown\")}')
    else:
        print(f'❌ Character creation failed: {result.error}')
except Exception as e:
    print(f'❌ Character creation test failed: {e}')
"

echo ""
echo "🎯 Development environment setup complete!"
echo ""
echo "📋 Next steps:"
echo "   1. Edit .env file with your API keys"
echo "   2. Run tests: python test_llm_diagnostic.py"
echo "   3. Start development server: python main.py server"
echo "   4. Or use CLI: python main.py cli"
echo ""
echo "🔒 Security reminders:"
echo "   - Never commit .env file to Git"
echo "   - Use GitHub secrets for production"
echo "   - API keys in .env are for local development only"
echo ""
