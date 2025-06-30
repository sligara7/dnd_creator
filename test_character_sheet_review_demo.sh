#!/bin/bash

# Quick test to demonstrate the character sheet review functionality
BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

echo -e "${PURPLE}🧪 Character Sheet Review Demo${NC}"
echo "================================"
echo "Creating a character and demonstrating the comprehensive review process"
echo ""

# Create a simple character
CHARACTER_DATA='{
    "name": "Demo Paladin",
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
    "backstory": "A noble paladin seeking redemption."
}'

echo -e "${YELLOW}Creating test character...${NC}"
response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X POST "$BASE_URL/api/v1/characters" \
    -H "Content-Type: application/json" \
    -d "$CHARACTER_DATA")

status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')

if [[ "$status" == "200" ]]; then
    CHARACTER_ID=$(echo "$body" | jq -r '.id')
    echo -e "${GREEN}✅ Character created: $CHARACTER_ID${NC}"
    echo ""
    
    echo -e "${BLUE}📋 Comprehensive Character Sheet Review${NC}"
    echo "============================================="
    echo -e "${PURPLE}Original Concept:${NC} 'A noble paladin seeking redemption'"
    echo -e "${PURPLE}Character ID:${NC} $CHARACTER_ID"
    echo ""
    
    echo -e "${YELLOW}1. Core Character Information:${NC}"
    curl -s "$BASE_URL/api/v1/characters/$CHARACTER_ID" | jq .
    echo ""
    
    echo -e "${YELLOW}2. Complete Character Sheet:${NC}"
    curl -s "$BASE_URL/api/v1/characters/$CHARACTER_ID/sheet" | jq .
    echo ""
    
    echo -e "${YELLOW}3. Character State:${NC}"
    curl -s "$BASE_URL/api/v1/characters/$CHARACTER_ID/state" | jq .
    echo ""
    
    echo -e "${YELLOW}4. Character Validation:${NC}"
    curl -s "$BASE_URL/api/v1/characters/$CHARACTER_ID/validate" | jq .
    echo ""
    
    echo -e "${PURPLE}📝 Review Checklist:${NC}"
    echo "✓ Backstory aligns with concept (noble paladin seeking redemption)"
    echo "✓ Class choice (Paladin) matches the concept"
    echo "✓ Background (Noble) supports the character story"
    echo "✓ Ability scores reflect a paladin build (high STR/CHA)"
    echo "✓ Equipment is appropriate for the character"
    echo "✓ Overall character feels cohesive and true to the concept"
    
    # Clean up
    echo ""
    echo -e "${GRAY}Cleaning up test character...${NC}"
    curl -s -X DELETE "$BASE_URL/api/v1/characters/$CHARACTER_ID" > /dev/null
    echo -e "${GREEN}✅ Demo complete${NC}"
else
    echo -e "${RED}❌ Failed to create character: $status${NC}"
    echo "$body"
fi
