#!/bin/bash

# Test LLM endpoints with 5-minute timeout for slower laptops
# Usage: ./test_llm_with_timeout.sh

BASE_URL="http://localhost:8000"
TIMEOUT=300  # 5 minutes

echo "🧪 Testing LLM Endpoints with 5-minute timeout on laptop"
echo "======================================================="

test_with_timeout() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    
    echo -n "⏳ Testing $test_name (up to 5 min)... "
    
    if [ -n "$data" ]; then
        response=$(timeout $TIMEOUT curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(timeout $TIMEOUT curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    if [ $? -eq 124 ]; then
        echo "❌ TIMEOUT (exceeded 5 minutes)"
        return 1
    fi
    
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [[ "$status" == "200" ]]; then
        echo "✅ SUCCESS (Status: $status)"
        echo "   Response length: ${#body} characters"
        if [[ ${#body} -lt 200 ]]; then
            echo "   Response: $body"
        else
            echo "   Response preview: ${body:0:100}..."
        fi
        return 0
    else
        echo "❌ FAIL (Status: $status)"
        echo "   Response: $body"
        return 1
    fi
}

# Test 1: Generate Backstory
echo ""
echo "TEST 1: Generate Backstory"
echo "=========================="
BACKSTORY_DATA='{
    "character_concept": "A wise old wizard",
    "character_details": {
        "name": "Gandalf",
        "species": "Human",
        "character_class": "Wizard",
        "background": "Hermit"
    }
}'

test_with_timeout "Generate Backstory" "POST" "/api/v1/generate/backstory" "$BACKSTORY_DATA"

# Test 2: Generate Equipment  
echo ""
echo "TEST 2: Generate Equipment"
echo "=========================="
EQUIPMENT_DATA='{
    "character_concept": "A stealthy rogue",
    "character_level": 3,
    "character_class": "Rogue"
}'

test_with_timeout "Generate Equipment" "POST" "/api/v1/generate/equipment" "$EQUIPMENT_DATA"

# Test 3: Generate Full Character
echo ""
echo "TEST 3: Generate Full Character"
echo "==============================="

test_with_timeout "Generate Full Character" "POST" "/api/v1/characters/generate?prompt=A%20noble%20paladin%20seeking%20redemption" ""

echo ""
echo "📊 LLM Testing Complete"
echo "======================="
echo "Note: If tests timeout, the laptop may need more processing power"
echo "or consider using a lighter model like llama3:8b-instruct-q4_0"
