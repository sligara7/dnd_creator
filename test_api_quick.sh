#!/bin/bash

# D&D Character Creator API - QUICK TEST (Fast endpoints only)
# Tests only the fastest endpoints for rapid development iteration
# Usage: ./test_api_quick.sh [BASE_URL]

BASE_URL=${1:-"http://localhost:8000"}
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Global variables
CHARACTER_ID=""
REPOSITORY_ID=""

echo -e "${BLUE}⚡ D&D Character Creator - QUICK API Test${NC}"
echo -e "${BLUE}=======================================${NC}"
echo "Testing against: $BASE_URL"
echo ""

# Helper function
run_test() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    ((TOTAL_TESTS++))
    echo -ne "${YELLOW}⏳ $test_name ... ${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✅${NC}"
        ((PASSED_TESTS++))
        
        # Extract IDs
        if [[ "$test_name" == *"Create Character"* ]]; then
            CHARACTER_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        elif [[ "$test_name" == *"Create Repository"* ]]; then
            REPOSITORY_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
        fi
    else
        echo -e "${RED}❌ ($status)${NC}"
        ((FAILED_TESTS++))
    fi
}

# Quick tests - only the fastest ones
echo -e "${GREEN}🏃‍♂️ QUICK TESTS (Core Functionality)${NC}"

run_test "Health Check" "GET" "/health" "" "200"
run_test "List Characters" "GET" "/api/v1/characters" "" "200"

CHARACTER_DATA='{"name":"Quick Test","species":"Human","character_classes":{"Fighter":1},"background":"Folk Hero","alignment":["Neutral","Good"],"abilities":{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":12,"charisma":10}}'

run_test "Create Character" "POST" "/api/v1/characters" "$CHARACTER_DATA" "200"

if [ -n "$CHARACTER_ID" ]; then
    run_test "Get Character" "GET" "/api/v1/characters/$CHARACTER_ID" "" "200"
    run_test "Delete Character" "DELETE" "/api/v1/characters/$CHARACTER_ID" "" "200"
fi

REPO_DATA='{"name":"Quick Test Repo","character_data":{"name":"Test","species":"Human"}}'
run_test "Create Repository" "POST" "/api/v1/character-repositories" "$REPO_DATA" "200"

if [ -n "$REPOSITORY_ID" ]; then
    run_test "Get Repository" "GET" "/api/v1/character-repositories/$REPOSITORY_ID" "" "200"
fi

echo ""
echo -e "${BLUE}📊 QUICK TEST RESULTS${NC}"
echo "==================="
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC}/$TOTAL_TESTS"

if [ $PASSED_TESTS -eq $TOTAL_TESTS ]; then
    echo -e "${GREEN}🎉 All core functionality working!${NC}"
    exit 0
else
    echo -e "${RED}❌ Some core tests failed${NC}"
    exit 1
fi
