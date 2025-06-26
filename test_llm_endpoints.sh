#!/bin/bash

# Simple LLM endpoint test to verify Ollama integration
# Usage: ./test_llm_endpoints.sh

BASE_URL="http://localhost:8000"

echo "🧪 Testing LLM Endpoints with Ollama/llama3"
echo "============================================="

# Test 1: Generate Backstory
echo "⏳ Testing Generate Backstory..."
BACKSTORY_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/generate/backstory" \
  -H "Content-Type: application/json" \
  -d '{
    "character_concept": "A wise old wizard",
    "character_details": {
      "name": "Gandalf",
      "species": "Human", 
      "character_class": "Wizard",
      "background": "Hermit"
    }
  }')

BACKSTORY_BODY=$(echo "$BACKSTORY_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
BACKSTORY_STATUS=$(echo "$BACKSTORY_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

if [[ "$BACKSTORY_STATUS" == "200" ]]; then
    echo "✅ Backstory generation: PASS (Status: $BACKSTORY_STATUS)"
    echo "   Response sample: ${BACKSTORY_BODY:0:100}..."
else
    echo "❌ Backstory generation: FAIL (Status: $BACKSTORY_STATUS)"
    echo "   Error: $BACKSTORY_BODY"
fi

echo ""

# Test 2: Generate Equipment  
echo "⏳ Testing Generate Equipment..."
EQUIPMENT_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/generate/equipment" \
  -H "Content-Type: application/json" \
  -d '{
    "character_concept": "A stealthy rogue",
    "character_level": 3,
    "character_class": "Rogue"
  }')

EQUIPMENT_BODY=$(echo "$EQUIPMENT_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
EQUIPMENT_STATUS=$(echo "$EQUIPMENT_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

if [[ "$EQUIPMENT_STATUS" == "200" ]]; then
    echo "✅ Equipment generation: PASS (Status: $EQUIPMENT_STATUS)"
    echo "   Response sample: ${EQUIPMENT_BODY:0:100}..."
else
    echo "❌ Equipment generation: FAIL (Status: $EQUIPMENT_STATUS)"
    echo "   Error: $EQUIPMENT_BODY"
fi

echo ""

# Test 3: Generate Full Character (should still work with fallback or LLM)
echo "⏳ Testing Generate Full Character..."
FULL_CHAR_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/characters/generate?prompt=A%20noble%20paladin%20seeking%20redemption")

FULL_CHAR_BODY=$(echo "$FULL_CHAR_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
FULL_CHAR_STATUS=$(echo "$FULL_CHAR_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

if [[ "$FULL_CHAR_STATUS" == "200" ]]; then
    echo "✅ Full character generation: PASS (Status: $FULL_CHAR_STATUS)"
    echo "   Response sample: ${FULL_CHAR_BODY:0:100}..."
else
    echo "❌ Full character generation: FAIL (Status: $FULL_CHAR_STATUS)"
    echo "   Error: $FULL_CHAR_BODY"
fi

echo ""
echo "🏁 LLM Test Complete"
