#!/bin/bash

# Simple API endpoint testing for D&D Character Creator
set -e

API_BASE="http://localhost:8000"
echo "🧪 Testing Critical D&D Character Creator API v2 Endpoints"
echo ""

# Function to test endpoint simply
test_simple() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    local description="$4"
    
    echo -n "Testing: $description ... "
    
    if [ "$method" = "GET" ]; then
        if curl -s -f "$API_BASE$endpoint" > /dev/null; then
            echo "✅ PASS"
            return 0
        else
            echo "❌ FAIL"
            return 1
        fi
    else
        if curl -s -f -X "$method" -H "Content-Type: application/json" -d "$data" "$API_BASE$endpoint" > /dev/null; then
            echo "✅ PASS"
            return 0
        else
            echo "❌ FAIL"
            return 1
        fi
    fi
}

echo "🏥 Core Health Endpoints:"
test_simple "GET" "/health" "" "Health Check"
test_simple "POST" "/api/v2/test/mock" "" "Mock Test Endpoint"

echo ""
echo "🏭 Factory System:"
test_simple "GET" "/api/v2/factory/types" "" "Factory Creation Types"

echo ""
echo "👤 Character Management:"
test_simple "GET" "/api/v2/characters" "" "List Characters"

echo ""
echo "🧪 Creating Test Character..."
CREATE_RESPONSE=$(curl -s -X POST -H "Content-Type: application/json" -d '{
    "name": "Test Warrior",
    "species": "Human", 
    "background": "Soldier",
    "character_classes": {"Fighter": 1},
    "backstory": "A brave test character",
    "alignment": ["Lawful", "Good"],
    "abilities": {
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 12,
        "charisma": 13
    }
}' "$API_BASE/api/v2/characters")

if echo "$CREATE_RESPONSE" | grep -q '"id"'; then
    CHARACTER_ID=$(echo "$CREATE_RESPONSE" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo "✅ Character created with ID: $CHARACTER_ID"
    
    echo ""
    echo "📋 Character Operations:"
    test_simple "GET" "/api/v2/characters/$CHARACTER_ID" "" "Get Character"
    test_simple "GET" "/api/v2/characters/$CHARACTER_ID/validate" "" "Validate Character"
    
    echo ""
    echo "🎮 Gameplay Features:"
    test_simple "GET" "/api/v2/characters/$CHARACTER_ID/state" "" "Get Character State"
    test_simple "GET" "/api/v2/characters/$CHARACTER_ID/inventory" "" "Get Inventory"
    test_simple "GET" "/api/v2/characters/$CHARACTER_ID/versions" "" "List Versions"
    
    echo ""
    echo "🧹 Cleanup:"
    if curl -s -f -X DELETE "$API_BASE/api/v2/characters/$CHARACTER_ID" > /dev/null; then
        echo "✅ Test character deleted"
    else
        echo "❌ Failed to delete test character"
    fi
else
    echo "❌ Failed to create test character"
    echo "Response: $CREATE_RESPONSE"
fi

echo ""
echo "🎉 Basic endpoint testing complete!"
echo "📖 Full API docs: http://localhost:8000/docs"
