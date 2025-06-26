#!/bin/bash

# Test LLM endpoints with proper timeouts for tinyllama model
# This script tests the LLM endpoints with 5-minute timeouts

BASE_URL=${1:-"http://localhost:8000"}

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Testing LLM Endpoints with tinyllama (5-minute timeout)${NC}"
echo "=========================================================="
echo "Backend URL: $BASE_URL"
echo ""

# Helper function to test LLM endpoint with long timeout
test_llm_endpoint() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    
    echo -ne "${YELLOW}⏳ Testing $test_name (up to 5 min)... ${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" \
            --connect-timeout 30 \
            --max-time 300 2>/dev/null)  # 5 minute timeout
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" \
            --connect-timeout 30 \
            --max-time 300 2>/dev/null)  # 5 minute timeout
    fi
    
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [[ "$status" == "200" ]]; then
        echo -e "${GREEN}✅ SUCCESS${NC} (Status: $status)"
        response_length=${#body}
        echo "   Response length: $response_length characters"
        if [ $response_length -gt 50 ]; then
            echo "   Response preview: ${body:0:100}..."
        else
            echo "   Response: $body"
        fi
    else
        echo -e "${RED}❌ FAIL${NC} (Status: $status)"
        if [[ ${#body} -lt 200 ]]; then
            echo "   Error: $body"
        else
            echo "   Error: ${body:0:150}..."
        fi
    fi
    echo ""
}

# Test 1: Generate Backstory
BACKSTORY_DATA='{
    "character_concept": "A wise old wizard",
    "character_details": {
        "name": "Gandalf",
        "species": "Human",
        "character_class": "Wizard",
        "background": "Hermit"
    }
}'

test_llm_endpoint "Generate Backstory" "POST" "/api/v1/generate/backstory" "$BACKSTORY_DATA"

# Test 2: Generate Equipment
EQUIPMENT_DATA='{
    "character_concept": "A stealthy rogue",
    "character_level": 3,
    "character_class": "Rogue"
}'

test_llm_endpoint "Generate Equipment" "POST" "/api/v1/generate/equipment" "$EQUIPMENT_DATA"

# Test 3: Generate Full Character
test_llm_endpoint "Generate Full Character" "POST" "/api/v1/characters/generate?prompt=A%20noble%20paladin%20seeking%20redemption" ""

echo -e "${BLUE}📊 LLM Testing Complete${NC}"
echo "All tests run with 5-minute timeout to accommodate tinyllama model speed"
