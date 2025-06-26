#!/bin/bash

# API-Based Character Creation Workflow Test
# Similar to backend_dev/ai_character_creator.py but using API endpoints
# This tests the complete character creation process step by step

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

echo -e "${PURPLE}🎭 AI-Driven D&D Character Creator - API Workflow Test${NC}"
echo "================================================================="
echo "Testing the complete character creation workflow using API endpoints"
echo "This simulates what backend_dev/ai_character_creator.py did, but via API"
echo ""

# Test data
CHARACTER_CONCEPT="A noble paladin seeking redemption for past misdeeds"
BACKSTORY_DATA='{
    "character_concept": "A noble paladin seeking redemption",
    "character_details": {
        "name": "Sir Galahad",
        "species": "Human",
        "character_class": "Paladin", 
        "background": "Noble",
        "level": 3
    }
}'

EQUIPMENT_DATA='{
    "character_concept": "A noble paladin with heavy armor and holy weapons",
    "character_level": 3,
    "character_class": "Paladin",
    "background": "Noble"
}'

# Helper function to make API calls and check responses
test_api_call() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -ne "${CYAN}⏳ $test_name ... ${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
        if [[ ${#body} -gt 100 ]]; then
            echo "   Response: ${body:0:100}..."
        else
            echo "   Response: $body"
        fi
        echo ""
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status)"
        if [[ ${#body} -lt 200 ]]; then
            echo "   Response: $body"
        else
            echo "   Response: ${body:0:150}..."
        fi
        echo ""
        return 1
    fi
}

# Step 1: Test Health/Connection
echo -e "${BLUE}🏥 STEP 1: Health Check${NC}"
echo "========================"
test_api_call "Health Check" "GET" "/health" "" "200"

# Step 2: Test Basic LLM Generation (Full Character)
echo -e "${BLUE}🧙 STEP 2: Full Character Generation (LLM)${NC}" 
echo "==========================================="
echo "This should work based on our test results..."
test_api_call "Generate Full Character" "POST" "/api/v1/characters/generate?prompt=$(echo "$CHARACTER_CONCEPT" | sed 's/ /%20/g')" "" "200"

# Step 3: Test Individual LLM Components (These are failing)
echo -e "${BLUE}🎭 STEP 3: Individual LLM Components${NC}"
echo "===================================="
echo "These are the endpoints that are currently failing..."

echo -e "${YELLOW}Testing Backstory Generation:${NC}"
test_api_call "Generate Backstory" "POST" "/api/v1/generate/backstory" "$BACKSTORY_DATA" "200"

echo -e "${YELLOW}Testing Equipment Generation:${NC}"
test_api_call "Generate Equipment" "POST" "/api/v1/generate/equipment" "$EQUIPMENT_DATA" "200"

# Step 4: Test Non-LLM Character Creation (Should work)
echo -e "${BLUE}⚔️ STEP 4: Traditional Character Creation${NC}"
echo "========================================"
echo "Creating a character using traditional data input..."

TRADITIONAL_CHARACTER='{
    "name": "Traditional Test Paladin",
    "species": "Human",
    "character_classes": {"Paladin": 3},
    "background": "Noble",
    "alignment": ["Lawful", "Good"],
    "abilities": {
        "strength": 16,
        "dexterity": 10,
        "constitution": 14,
        "intelligence": 11,
        "wisdom": 13,
        "charisma": 15
    },
    "backstory": "A noble-born paladin seeking to right the wrongs of his past.",
    "equipment": {
        "weapons": ["Longsword", "Shield"],
        "armor": "Chain Mail",
        "tools": ["Gaming Set"],
        "currency": {"gold": 150}
    }
}'

test_api_call "Create Traditional Character" "POST" "/api/v1/characters" "$TRADITIONAL_CHARACTER" "200"

# Step 5: Test Quick Generation (Should work)
echo -e "${BLUE}⚡ STEP 5: Quick Generation Endpoints${NC}"
echo "===================================="
echo "Testing the quick generation endpoints that should work..."

test_api_call "Quick Character Generation" "POST" "/api/v1/generate/quick-character?concept=A%20wise%20elven%20wizard" "" "200"

test_api_call "Quick Item Generation" "POST" "/api/v1/generate/quick-item?concept=A%20magical%20healing%20potion&item_type=potion&level=1" "" "200"

test_api_call "Quick NPC Generation" "POST" "/api/v1/generate/quick-npc?concept=A%20friendly%20tavern%20keeper&role=merchant" "" "200"

test_api_call "Quick Creature Generation" "POST" "/api/v1/generate/quick-creature?concept=A%20small%20forest%20sprite&cr=0.25&creature_type=fey" "" "200"

# Step 6: Summary and Analysis
echo -e "${PURPLE}📊 WORKFLOW TEST SUMMARY${NC}"
echo "=========================="
echo ""
echo -e "${GREEN}✅ Expected to work:${NC}"
echo "  - Full Character Generation (works because it uses create_llm_service() internally)"
echo "  - Traditional Character Creation (doesn't use LLM)"
echo "  - Quick Generation endpoints (use create_llm_service() internally)"
echo ""
echo -e "${RED}❌ Expected to fail:${NC}" 
echo "  - Generate Backstory (uses app.state.llm_service which isn't initialized)"
echo "  - Generate Equipment (uses app.state.llm_service which isn't initialized)"
echo ""
echo -e "${YELLOW}🔍 DIAGNOSIS:${NC}"
echo "The issue is that the failing endpoints expect app.state.llm_service to be"
echo "initialized, but it never gets set during app startup. The working endpoints"
echo "create their own LLM service instances using create_llm_service()."
echo ""
echo -e "${CYAN}🔧 SOLUTION:${NC}"
echo "We need to initialize app.state.llm_service in the FastAPI startup event."
