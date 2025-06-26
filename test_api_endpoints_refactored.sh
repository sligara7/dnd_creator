#!/bin/bash

# D&D Character Creator API Comprehensive Testing Script
# Tests ALL endpoints systematically from simple to complex
# Organized by speed: Fast → Medium → Slow → Very Slow (LLM)
# Usage: ./test_api_endpoints_refactored.sh [BASE_URL]

BASE_URL=${1:-"http://localhost:8000"}
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Global variables for storing created resource IDs
CHARACTER_ID=""
REPOSITORY_ID=""
BRANCH_NAME=""
COMMIT_HASH=""
TAG_NAME=""

echo -e "${PURPLE}🚀 D&D Character Creator - COMPREHENSIVE API Test Suite${NC}"
echo -e "${PURPLE}=====================================================${NC}"
echo "Testing against: $BASE_URL"
echo "Total endpoints to test: 34"
echo ""

# Helper function to run test
run_test() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local test_type="${6:-NORMAL}"
    
    ((TOTAL_TESTS++))
    
    # Color code by test type
    local color="${YELLOW}"
    case "$test_type" in
        "FAST") color="${GREEN}" ;;
        "MEDIUM") color="${CYAN}" ;;
        "SLOW") color="${YELLOW}" ;;
        "LLM") color="${RED}" ;;
    esac
    
    echo -ne "${color}⏳ Testing: $test_name ... ${NC}"
    
    if [ -n "$data" ]; then
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(curl -s -w "HTTPSTATUS:%{http_code}" -X $method "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
        ((PASSED_TESTS++))
        
        # Store important IDs for later tests
        extract_ids_from_response "$test_name" "$body"
        
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status)"
        ((FAILED_TESTS++))
        if [[ ${#body} -lt 150 ]]; then
            echo "   Response: $body"
        else
            echo "   Response: ${body:0:100}..."
        fi
    fi
}

# Helper function to extract IDs from responses
extract_ids_from_response() {
    local test_name="$1"
    local body="$2"
    
    case "$test_name" in
        *"Create Character"*)
            CHARACTER_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$CHARACTER_ID" ] && echo "   📝 Stored Character ID: $CHARACTER_ID"
            ;;
        *"Create Repository"*)
            REPOSITORY_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$REPOSITORY_ID" ] && echo "   📝 Stored Repository ID: $REPOSITORY_ID"
            ;;
        *"Create Branch"*)
            BRANCH_NAME=$(echo "$body" | grep -o '"branch_name":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$BRANCH_NAME" ] && echo "   📝 Stored Branch Name: $BRANCH_NAME"
            ;;
        *"Create Commit"*)
            COMMIT_HASH=$(echo "$body" | grep -o '"commit_hash":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$COMMIT_HASH" ] && echo "   📝 Stored Commit Hash: $COMMIT_HASH"
            ;;
        *"Create Tag"*)
            TAG_NAME=$(echo "$body" | grep -o '"tag_name":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$TAG_NAME" ] && echo "   📝 Stored Tag Name: $TAG_NAME"
            ;;
    esac
}

# Helper function to run conditional test
run_conditional_test() {
    local test_name="$1"
    local method="$2"
    local endpoint_template="$3"
    local data="$4"
    local expected_status="$5"
    local condition_var="$6"
    local condition_name="$7"
    local test_type="${8:-NORMAL}"
    
    if [ -n "${!condition_var}" ]; then
        # Replace the placeholder with actual ID
        local endpoint="${endpoint_template//\$CHARACTER_ID/$CHARACTER_ID}"
        endpoint="${endpoint//\$REPOSITORY_ID/$REPOSITORY_ID}"
        endpoint="${endpoint//\$COMMIT_HASH/$COMMIT_HASH}"
        run_test "$test_name" "$method" "$endpoint" "$data" "$expected_status" "$test_type"
    else
        echo -e "${RED}❌ Skipping $test_name (no $condition_name)${NC}"
        ((TOTAL_TESTS++))
        ((FAILED_TESTS++))
    fi
}

echo -e "${GREEN}🏃‍♂️ TIER 1: FASTEST TESTS (Basic Health & Info)${NC}"
echo "============================================="

# 1. Health Check - Fastest possible test
run_test "Health Check" "GET" "/health" "" "200" "FAST"

echo ""
echo -e "${CYAN}🏃‍♂️ TIER 2: FAST TESTS (Basic CRUD Operations)${NC}"
echo "==========================================="

# 2. List Characters (empty initially)
run_test "List Characters (Empty)" "GET" "/api/v1/characters" "" "200" "FAST"

# 3. Create Character - Core functionality
CHARACTER_DATA='{
    "name": "Test Wizard",
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

run_test "Create Character" "POST" "/api/v1/characters" "$CHARACTER_DATA" "200" "FAST"

# 4. List Characters (should have one now)
run_test "List Characters (With Data)" "GET" "/api/v1/characters" "" "200" "FAST"

# 5. Get Specific Character
run_conditional_test "Get Character by ID" "GET" "/api/v1/characters/\$CHARACTER_ID" "" "200" "CHARACTER_ID" "character ID" "FAST"

echo ""
echo -e "${CYAN}🚶‍♂️ TIER 3: MEDIUM TESTS (Character Management)${NC}"
echo "============================================"

# 6. Update Character
UPDATE_DATA='{
    "name": "Updated Test Wizard",
    "backstory": "An updated scholarly wizard seeking even more knowledge."
}'

run_conditional_test "Update Character" "PUT" "/api/v1/characters/\$CHARACTER_ID" "$UPDATE_DATA" "200" "CHARACTER_ID" "character ID" "MEDIUM"

# 7. Character Validation
VALIDATE_DATA='{
    "name": "Validation Test",
    "species": "Elf",
    "character_classes": {"Rogue": 1},
    "abilities": {
        "strength": 8,
        "dexterity": 16,
        "constitution": 14,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 10
    }
}'

run_test "Validate Character Data" "POST" "/api/v1/validate/character" "$VALIDATE_DATA" "200" "MEDIUM"

run_conditional_test "Validate Existing Character" "GET" "/api/v1/characters/\$CHARACTER_ID/validate" "" "200" "CHARACTER_ID" "character ID" "MEDIUM"

echo ""
echo -e "${CYAN}🚶‍♂️ TIER 4: MEDIUM TESTS (Character Versioning System)${NC}"
echo "===================================================="

# 8. Create Character Repository
REPO_DATA='{
    "name": "Test Character Evolution",
    "player_name": "Test Player",
    "description": "Test character repository for API testing",
    "character_data": {
        "name": "Test Wizard",
        "species": "Human",
        "character_classes": {"Wizard": 3},
        "background": "Scholar"
    }
}'

run_test "Create Repository" "POST" "/api/v1/character-repositories" "$REPO_DATA" "200" "MEDIUM"

# 9. Repository Operations
run_conditional_test "Get Repository Info" "GET" "/api/v1/character-repositories/\$REPOSITORY_ID" "" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

run_conditional_test "Get Repository Timeline" "GET" "/api/v1/character-repositories/\$REPOSITORY_ID/timeline" "" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

run_conditional_test "Get Repository Visualization" "GET" "/api/v1/character-repositories/\$REPOSITORY_ID/visualization" "" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

# 10. Branch Operations
BRANCH_DATA='{
    "branch_name": "test-branch",
    "source_commit_hash": "main",
    "description": "Test branch for API testing"
}'

run_conditional_test "Create Branch" "POST" "/api/v1/character-repositories/\$REPOSITORY_ID/branches" "$BRANCH_DATA" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

run_conditional_test "List Branches" "GET" "/api/v1/character-repositories/\$REPOSITORY_ID/branches" "" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

# 11. Commit Operations
COMMIT_DATA='{
    "commit_message": "Test commit",
    "branch_name": "main",
    "character_data": {
        "name": "Evolved Test Wizard",
        "level": 4
    }
}'

run_conditional_test "Create Commit" "POST" "/api/v1/character-repositories/\$REPOSITORY_ID/commits" "$COMMIT_DATA" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

run_conditional_test "List Commits" "GET" "/api/v1/character-repositories/\$REPOSITORY_ID/commits" "" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

# 12. Tag Operations
TAG_DATA='{
    "tag_name": "v1.0",
    "commit_hash": "main",
    "description": "First stable version"
}'

run_conditional_test "Create Tag" "POST" "/api/v1/character-repositories/\$REPOSITORY_ID/tags" "$TAG_DATA" "200" "REPOSITORY_ID" "repository ID" "MEDIUM"

echo ""
echo -e "${YELLOW}🚶‍♂️ TIER 5: SLOWER TESTS (Advanced Character Features)${NC}"
echo "====================================================="

# 13. Character Sheet & State
run_conditional_test "Get Character Sheet" "GET" "/api/v1/characters/\$CHARACTER_ID/sheet" "" "200" "CHARACTER_ID" "character ID" "SLOW"

run_conditional_test "Get Character State" "GET" "/api/v1/characters/\$CHARACTER_ID/state" "" "200" "CHARACTER_ID" "character ID" "SLOW"

# 14. Character State Updates
STATE_UPDATE='{
    "current_hp": 20,
    "add_condition": {"condition": "poisoned", "duration": 3}
}'

run_conditional_test "Update Character State" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$STATE_UPDATE" "200" "CHARACTER_ID" "character ID" "SLOW"

# 15. Combat Operations
COMBAT_DATA='{
    "action": "take_damage",
    "damage": 5,
    "damage_type": "slashing"
}'

run_conditional_test "Apply Combat Effect" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$COMBAT_DATA" "200" "CHARACTER_ID" "character ID" "SLOW"

# 16. Rest Operations
REST_DATA='{
    "rest_type": "short"
}'

run_conditional_test "Character Rest" "POST" "/api/v1/characters/\$CHARACTER_ID/rest" "$REST_DATA" "200" "CHARACTER_ID" "character ID" "SLOW"

# 17. Level Up Operations
LEVELUP_DATA='{
    "branch_name": "main",
    "new_character_data": {
        "name": "Evolved Test Wizard",
        "level": 4,
        "hit_points": 32,
        "abilities": {
            "strength": 10,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 16,
            "wisdom": 12,
            "charisma": 8
        }
    },
    "level_info": {
        "new_level": 4,
        "hit_points_gained": 8,
        "ability_score_improvement": {"intelligence": 1}
    }
}'

run_conditional_test "Character Level Up" "POST" "/api/v1/character-repositories/\$REPOSITORY_ID/level-up" "$LEVELUP_DATA" "200" "REPOSITORY_ID" "repository ID" "SLOW"

echo ""
echo -e "${YELLOW}🐌 TIER 6: SLOW TESTS (Content Creation)${NC}"
echo "======================================"

# 18. Create Item
ITEM_DATA='{
    "name": "Magic Sword",
    "item_type": "weapon",
    "rarity": "rare",
    "description": "A gleaming magical sword"
}'

run_test "Create Item" "POST" "/api/v1/items/create" "$ITEM_DATA" "200" "SLOW"

# 19. Create NPC
NPC_DATA='{
    "name": "Village Elder",
    "npc_type": "humanoid",
    "role": "quest_giver",
    "description": "A wise village elder"
}'

run_test "Create NPC" "POST" "/api/v1/npcs/create" "$NPC_DATA" "200" "SLOW"

# 20. Create Creature
CREATURE_DATA='{
    "name": "Forest Wolf",
    "creature_type": "beast",
    "size": "medium",
    "description": "A fierce forest predator"
}'

run_test "Create Creature" "POST" "/api/v1/creatures/create" "$CREATURE_DATA" "200" "SLOW"

echo ""
echo -e "${YELLOW}🐌 TIER 7: SLOW TESTS (Quick Generation - Non-LLM)${NC}"
echo "==============================================="

# 21. Quick Generation Tests
run_test "Quick Character Generation" "POST" "/api/v1/generate/quick-character?concept=A%20dwarf%20fighter%20from%20the%20mountains" "" "200" "SLOW"

run_test "Quick Item Generation" "POST" "/api/v1/generate/quick-item?concept=A%20magical%20sword%20glowing%20with%20inner%20fire&item_type=magic_item&level=1" "" "200" "SLOW"

run_test "Quick NPC Generation" "POST" "/api/v1/generate/quick-npc?concept=A%20mysterious%20tavern%20keeper&npc_type=humanoid" "" "200" "SLOW"

run_test "Quick Creature Generation" "POST" "/api/v1/generate/quick-creature?concept=A%20fierce%20dragon%20guarding%20treasure&creature_type=dragon" "" "200" "SLOW"

echo ""
echo -e "${RED}🐢 TIER 8: SLOWEST TESTS (LLM-Based Generation)${NC}"
echo "=============================================="
echo -e "${YELLOW}⚠️  LLM tests may fail if no LLM service is configured${NC}"
echo -e "${YELLOW}⚠️  These are the slowest tests and will be run last${NC}"

# 22. LLM Backstory Generation
BACKSTORY_DATA='{
    "character_concept": "A wise old wizard",
    "character_details": {
        "name": "Gandalf",
        "species": "Human",
        "character_class": "Wizard",
        "background": "Hermit"
    }
}'

run_test "Generate Backstory (LLM)" "POST" "/api/v1/generate/backstory" "$BACKSTORY_DATA" "200" "LLM"

# 23. LLM Equipment Generation
EQUIPMENT_DATA='{
    "character_concept": "A stealthy rogue",
    "character_level": 3,
    "character_class": "Rogue"
}'

run_test "Generate Equipment (LLM)" "POST" "/api/v1/generate/equipment" "$EQUIPMENT_DATA" "200" "LLM"

# 24. Full Character Generation (SLOWEST)
run_test "Generate Full Character (LLM)" "POST" "/api/v1/characters/generate?prompt=A%20noble%20paladin%20seeking%20redemption%20for%20past%20misdeeds" "" "200" "LLM"

echo ""
echo -e "${BLUE}🧹 CLEANUP PHASE${NC}"
echo "==============="

# 25. Get Character from Commit (if we have a commit hash)
run_conditional_test "Get Character from Commit" "GET" "/api/v1/character-commits/\$COMMIT_HASH/character" "" "200" "COMMIT_HASH" "commit hash" "FAST"

# 26. Delete Character (cleanup)
run_conditional_test "Delete Character" "DELETE" "/api/v1/characters/\$CHARACTER_ID" "" "200" "CHARACTER_ID" "character ID" "FAST"

echo ""
echo -e "${PURPLE}📊 COMPREHENSIVE TEST RESULTS SUMMARY${NC}"
echo "======================================"
echo -e "Total Endpoints Tested: ${BLUE}$TOTAL_TESTS${NC}"
echo -e "Passed: ${GREEN}$PASSED_TESTS${NC} ($(( PASSED_TESTS * 100 / TOTAL_TESTS ))%)"
echo -e "Failed: ${RED}$FAILED_TESTS${NC} ($(( FAILED_TESTS * 100 / TOTAL_TESTS ))%)"
echo ""

# Performance Analysis
if [ $PASSED_TESTS -ge 30 ]; then
    echo -e "${GREEN}🎉 Excellent! Most endpoints are working (30+ tests passed)${NC}"
elif [ $PASSED_TESTS -ge 20 ]; then
    echo -e "${YELLOW}👍 Good progress! Core functionality working (20+ tests passed)${NC}"
elif [ $PASSED_TESTS -ge 10 ]; then
    echo -e "${YELLOW}⚠️  Basic functionality working (10+ tests passed)${NC}"
else
    echo -e "${RED}❌ Major issues detected (less than 10 tests passed)${NC}"
fi

echo ""
echo -e "${CYAN}🔍 Analysis by Test Tier:${NC}"
echo "- Tier 1 (Health): Fastest basic connectivity tests"
echo "- Tier 2-3 (CRUD): Core character management" 
echo "- Tier 4 (Versioning): Git-like character evolution"
echo "- Tier 5 (Advanced): Character sheets, combat, state"
echo "- Tier 6-7 (Generation): Content creation"
echo "- Tier 8 (LLM): AI-powered generation (slowest)"

if [ $FAILED_TESTS -eq 0 ]; then
    echo -e "${GREEN}🏆 ALL TESTS PASSED! API is fully functional!${NC}"
    exit 0
else
    echo -e "${RED}🔧 Some tests failed. Check backend implementation.${NC}"
    exit 1
fi
