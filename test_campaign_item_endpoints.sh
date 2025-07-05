#!/bin/bash

# Test script for Campaign Service Item Endpoints (Task 3b)
# Sets minimal environment variables needed to run the campaign service

export SECRET_KEY="test-secret-key-for-development"
export LLM_PROVIDER="ollama"  # Use local Ollama to avoid API key requirements
export LLM_MODEL="llama3"
export DATABASE_URL="sqlite:///./test_campaign.db"

echo "Starting Campaign Service for Item Endpoints Testing..."
echo "Environment configured:"
echo "  SECRET_KEY: [REDACTED]"
echo "  LLM_PROVIDER: $LLM_PROVIDER"
echo "  LLM_MODEL: $LLM_MODEL"
echo "  DATABASE_URL: $DATABASE_URL"
echo ""

cd backend_campaign

# Start the campaign service
echo "Starting campaign service..."
python -m uvicorn app:app --host 0.0.0.0 --port 8001 --reload
