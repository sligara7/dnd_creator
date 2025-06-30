#!/bin/bash

# Quick demo of verbose LLM output
# This demonstrates what you'll see when running the full workflow with LLM calls

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m'

echo -e "${PURPLE}🎭 LLM Verbose Mode Demo${NC}"
echo "This shows how the verbose workflow script displays LLM interactions"
echo ""

# Demo factory weapon creation (usually faster than character creation)
FACTORY_WEAPON_DATA='{
    "creation_type": "weapon",
    "prompt": "A simple +1 magical dagger",
    "save_to_database": false
}'

echo -e "${YELLOW}Testing Factory Weapon Creation with verbose output:${NC}"
echo ""

echo -e "${GRAY}📤 REQUEST DETAILS:${NC}"
echo -e "${GRAY}   Method: POST${NC}"
echo -e "${GRAY}   URL: $BASE_URL/api/v2/factory/create${NC}"
echo -e "${GRAY}   Headers: Content-Type: application/json${NC}"
echo -e "${GRAY}   Body:${NC}"
echo "$FACTORY_WEAPON_DATA" | jq .
echo -e "${GRAY}   Timeout: 60s${NC}"
echo ""

echo -e "${CYAN}⏳ Making request to LLM service...${NC}"

response=$(timeout 60 curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v2/factory/create" \
    -H "Content-Type: application/json" \
    -d "$FACTORY_WEAPON_DATA" 2>/dev/null)

if [ $? -eq 124 ]; then
    echo -e "${YELLOW}⏰ TIMEOUT (60s exceeded)${NC}"
    echo -e "${YELLOW}   This is normal for LLM-based endpoints which can take time to generate content${NC}"
    exit 0
fi

body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

if [[ "$status" == "200" ]]; then
    echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
    echo ""
    echo -e "${GRAY}📥 RESPONSE DETAILS:${NC}"
    echo -e "${GRAY}   Status: $status${NC}"
    echo -e "${GRAY}   Body:${NC}"
    echo "$body" | jq .
else
    echo -e "${RED}❌ FAIL${NC} (Expected: 200, Got: $status)"
    echo ""
    echo -e "${RED}📥 ERROR RESPONSE:${NC}"
    echo -e "${RED}   Status: $status${NC}"
    echo -e "${RED}   Body:${NC}"
    echo "$body" | jq . 2>/dev/null || echo "$body"
fi

echo ""
echo -e "${BLUE}💡 This is what you'll see for each LLM-powered endpoint in the full workflow!${NC}"
