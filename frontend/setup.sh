#!/bin/bash
# Frontend Development Setup Script

echo "🎲 D&D Character Creator - Frontend Setup 🎲"
echo "================================================"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is not installed. Please install npm first."
    exit 1
fi

echo "📋 Node.js version: $(node --version)"
echo "📋 npm version: $(npm --version)"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
npm install

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo ""
echo "🚀 Setup complete! You can now:"
echo "   • npm run dev    - Start development server"
echo "   • npm run build  - Build for production"
echo "   • npm run preview - Preview production build"
echo ""
echo "📡 Make sure your backend is running at http://localhost:8000"
