#!/bin/bash

# D&D Character Creator Single Character Test
# Tests a complete character lifecycle without cleanup

BASE_URL=${1:-"http://localhost:8000"}

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 D&D Character Creator - Single Character Test${NC}"
echo -e "${BLUE}============================================${NC}"
echo "Testing against: $BASE_URL"
echo ""

# Create a character
echo -e "${YELLOW}Creating character...${NC}"
CHARACTER_DATA='{
    "name": "Persistent Test Wizard",
    "species": "Human",
    "character_classes": {"Wizard": 3},
    "background": "Scholar",
    "alignment": ["Lawful", "Good"],
    "abilities": {
        "strength": 10,
        "dexterity": 14,
        "constitution": 12,
        "intelligence": 18,
        "wisdom": 16,
        "charisma": 13
    },
    "backstory": "A scholarly wizard seeking knowledge."
}'

CREATE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/characters" \
    -H "Content-Type: application/json" \
    -d "$CHARACTER_DATA" 2>/dev/null)

CREATE_BODY=$(echo "$CREATE_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
CREATE_STATUS=$(echo "$CREATE_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

if [[ "$CREATE_STATUS" == "200" ]]; then
    CHARACTER_ID=$(echo "$CREATE_BODY" | grep -o '"id":"[^"]*"' | cut -d'"' -f4)
    echo -e "${GREEN}✅ Character Created${NC}"
    echo "Character ID: $CHARACTER_ID"
    echo ""
else
    echo -e "${RED}❌ Failed to create character${NC}"
    echo "Status: $CREATE_STATUS"
    echo "Response: $CREATE_BODY"
    exit 1
fi

# Test character sheet endpoint
echo -e "${YELLOW}Testing character sheet...${NC}"
SHEET_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X GET "$BASE_URL/api/v1/characters/$CHARACTER_ID/sheet" 2>/dev/null)
SHEET_BODY=$(echo "$SHEET_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
SHEET_STATUS=$(echo "$SHEET_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Sheet Status: $SHEET_STATUS"
if [[ "$SHEET_STATUS" == "200" ]]; then
    echo -e "${GREEN}✅ Character Sheet Retrieved${NC}"
    echo "Sheet data: ${SHEET_BODY:0:100}..."
else
    echo -e "${RED}❌ Character Sheet Failed${NC}"
    echo "Response: $SHEET_BODY"
fi
echo ""

# Test character state endpoint
echo -e "${YELLOW}Testing character state...${NC}"
STATE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X GET "$BASE_URL/api/v1/characters/$CHARACTER_ID/state" 2>/dev/null)
STATE_BODY=$(echo "$STATE_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
STATE_STATUS=$(echo "$STATE_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "State Status: $STATE_STATUS"
if [[ "$STATE_STATUS" == "200" ]]; then
    echo -e "${GREEN}✅ Character State Retrieved${NC}"
    echo "State data: ${STATE_BODY:0:100}..."
else
    echo -e "${RED}❌ Character State Failed${NC}"
    echo "Response: $STATE_BODY"
fi
echo ""

# Test character validation
echo -e "${YELLOW}Testing character validation...${NC}"
VALIDATE_RESPONSE=$(curl -s -w "HTTPSTATUS:%{http_code}" -X GET "$BASE_URL/api/v1/characters/$CHARACTER_ID/validate" 2>/dev/null)
VALIDATE_BODY=$(echo "$VALIDATE_RESPONSE" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
VALIDATE_STATUS=$(echo "$VALIDATE_RESPONSE" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')

echo "Validation Status: $VALIDATE_STATUS"
if [[ "$VALIDATE_STATUS" == "200" ]]; then
    echo -e "${GREEN}✅ Character Validation Passed${NC}"
    echo "Validation data: ${VALIDATE_BODY:0:100}..."
else
    echo -e "${RED}❌ Character Validation Failed${NC}"
    echo "Response: $VALIDATE_BODY"
fi
echo ""

echo -e "${BLUE}Character ID for further testing: $CHARACTER_ID${NC}"
echo -e "${YELLOW}Use this ID to test other endpoints manually${NC}"
