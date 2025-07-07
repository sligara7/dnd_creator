#!/bin/bash
# Simple test for direct-edit endpoints

export SECRET_KEY="dev-secret-key-$(date +%s)"
export OPENAI_API_KEY="$OPENAI_API_KEY"
API_URL="http://localhost:8001/api/v2"

echo "Testing Direct-Edit Endpoints..."
echo "=================================="

# Test health endpoint
echo "1. Testing health endpoint..."
curl -s http://localhost:8001/health | jq .

# Test mock endpoint  
echo "2. Testing mock endpoint..."
curl -s -X POST http://localhost:8001/api/v2/test/mock | jq .

# Test factory creation endpoint
echo "3. Testing factory creation endpoint..."
curl -s -X POST "${API_URL}/factory/create" \
    -H "Content-Type: application/json" \
    -d '{
        "creation_type": "character",
        "prompt": "A brave human fighter",
        "theme": "traditional D&D",
        "save_to_database": true
    }' | jq .

echo "Direct-edit endpoints test complete."
