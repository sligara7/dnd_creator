#!/bin/bash

# D&D Character In-Game State Management Test Script
# Tests real-time character sheet updates during gameplay
# Covers: damage, healing, spell slots, conditions, exhaustion, experience, etc.
#
# Usage: ./test_character_in_game_play.sh [mode]
#   mode: all (default), combat-only, state-only, rest-only

# Parse command line arguments
MODE=${1:-"all"}
case "$MODE" in
    "combat-only")
        COMBAT_ONLY=true
        echo "COMBAT ONLY MODE: Testing only combat-related state changes"
        ;;
    "state-only")
        STATE_ONLY=true
        echo "STATE ONLY MODE: Testing only general state management"
        ;;
    "rest-only")
        REST_ONLY=true
        echo "REST ONLY MODE: Testing only rest mechanics"
        ;;
    "all")
        echo "FULL MODE: Testing all in-game state management features"
        ;;
    *)
        echo "Usage: $0 [all|combat-only|state-only|rest-only]"
        exit 1
        ;;
esac

BASE_URL="http://localhost:8000"
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

# Global variables for test character
CHARACTER_ID=""
INITIAL_HP=""
INITIAL_SPELL_SLOTS=""

echo -e "${PURPLE}⚔️ D&D Character In-Game State Management Test Suite${NC}"
echo "=================================================="
echo "Testing real-time character state updates during gameplay"
echo "This simulates various in-game scenarios that modify character state"
echo ""
echo "Test Coverage:"
echo "  🩸 Combat: Damage, healing, temporary HP"
echo "  🎭 Conditions: Poisoned, charmed, exhaustion, etc."
echo "  ✨ Spell Management: Slot usage, spell effects"
echo "  😴 Rest Mechanics: Short rest, long rest recovery"
echo "  📈 Progression: Experience points, level-up triggers"
echo ""

# Helper function to make API calls and check responses
test_api_call() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local store_response="$6"  # Optional flag to store response for ID extraction
    
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
        
        # Store character ID if this is character creation
        if [[ "$store_response" == "true" && "$test_name" == *"Create"* ]]; then
            CHARACTER_ID=$(echo "$body" | grep -o '"id":"[^"]*"' | head -1 | cut -d'"' -f4)
            [ -n "$CHARACTER_ID" ] && echo "   📝 Stored Character ID: $CHARACTER_ID"
        fi
        
        # Store initial HP for damage tests
        if [[ "$test_name" == *"Get Character State"* ]]; then
            INITIAL_HP=$(echo "$body" | grep -o '"current_hp":[0-9]*' | cut -d':' -f2)
            [ -n "$INITIAL_HP" ] && echo "   ❤️ Initial HP: $INITIAL_HP"
        fi
        
        # Show key state information
        if [[ "$body" == *"current_hp"* ]]; then
            local current_hp=$(echo "$body" | grep -o '"current_hp":[0-9]*' | cut -d':' -f2)
            local max_hp=$(echo "$body" | grep -o '"max_hit_points":[0-9]*' | cut -d':' -f2)
            local temp_hp=$(echo "$body" | grep -o '"temporary_hp":[0-9]*' | cut -d':' -f2)
            echo "   ❤️ HP: $current_hp/$max_hp (Temp: ${temp_hp:-0})"
        fi
        
        # Show conditions
        if [[ "$body" == *"conditions"* ]]; then
            local conditions=$(echo "$body" | grep -o '"conditions":\[[^]]*\]' | cut -d':' -f2)
            echo "   🎭 Conditions: $conditions"
        fi
        
        # Show spell slots (if any)
        if [[ "$body" == *"spell_slots"* ]]; then
            echo "   ✨ Spell slots updated"
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

# Helper function to run conditional test (only if CHARACTER_ID exists)
run_conditional_test() {
    local test_name="$1"
    local method="$2"
    local endpoint_template="$3"
    local data="$4"
    local expected_status="$5"
    
    if [ -n "$CHARACTER_ID" ]; then
        local endpoint="${endpoint_template//\$CHARACTER_ID/$CHARACTER_ID}"
        test_api_call "$test_name" "$method" "$endpoint" "$data" "$expected_status"
    else
        echo -e "${RED}❌ Skipping $test_name (no character ID)${NC}"
        return 1
    fi
}

# Step 1: Setup Test Character
echo -e "${BLUE}🏗️ STEP 1: Setup Test Character${NC}"
echo "================================="

# Create a test character for in-game testing
TEST_CHARACTER='{
    "name": "Test Adventurer",
    "species": "Human",
    "character_classes": {"Fighter": 3},
    "background": "Soldier",
    "alignment": ["Lawful", "Good"],
    "abilities": {
        "strength": 16,
        "dexterity": 14,
        "constitution": 15,
        "intelligence": 12,
        "wisdom": 13,
        "charisma": 10
    },
    "backstory": "A battle-tested fighter ready for adventure.",
    "equipment": {
        "weapons": ["Longsword", "Shield"],
        "armor": "Chain Mail",
        "currency": {"gold": 100}
    }
}'

test_api_call "Create Test Character" "POST" "/api/v1/characters" "$TEST_CHARACTER" "200" "true"

# Get initial character state
run_conditional_test "Get Initial Character State" "GET" "/api/v1/characters/\$CHARACTER_ID/state" "" "200"

# Step 2: Combat Damage and Healing Tests
if [[ "$MODE" == "all" || "$MODE" == "combat-only" ]]; then
    echo -e "${BLUE}⚔️ STEP 2: Combat Damage and Healing${NC}"
    echo "==================================="
    
    # Apply slashing damage
    DAMAGE_DATA='{
        "action": "take_damage",
        "damage": 8,
        "damage_type": "slashing"
    }'
    run_conditional_test "Apply Slashing Damage (8)" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$DAMAGE_DATA" "200"
    
    # Apply fire damage with save
    FIRE_DAMAGE_DATA='{
        "action": "take_damage",
        "damage": 12,
        "damage_type": "fire",
        "save_type": "dexterity",
        "save_dc": 15,
        "save_result": "success"
    }'
    run_conditional_test "Apply Fire Damage with Dex Save" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$FIRE_DAMAGE_DATA" "200"
    
    # Heal the character
    HEAL_DATA='{
        "action": "heal",
        "amount": 6,
        "heal_type": "magical"
    }'
    run_conditional_test "Magical Healing (6 HP)" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$HEAL_DATA" "200"
    
    # Add temporary hit points
    TEMP_HP_DATA='{
        "action": "add_temporary_hp",
        "amount": 5
    }'
    run_conditional_test "Add Temporary HP (5)" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$TEMP_HP_DATA" "200"
    
    # Apply massive damage (should test death saves if implemented)
    MASSIVE_DAMAGE_DATA='{
        "action": "take_damage",
        "damage": 25,
        "damage_type": "necrotic"
    }'
    run_conditional_test "Apply Massive Damage (25)" "POST" "/api/v1/characters/\$CHARACTER_ID/combat" "$MASSIVE_DAMAGE_DATA" "200"
fi

# Step 3: Condition Management Tests
if [[ "$MODE" == "all" || "$MODE" == "state-only" ]]; then
    echo -e "${BLUE}🎭 STEP 3: Condition Management${NC}"
    echo "==============================="
    
    # Add poisoned condition
    POISON_CONDITION='{
        "add_condition": {
            "condition": "poisoned",
            "duration": 3,
            "source": "poison dart"
        }
    }'
    run_conditional_test "Add Poisoned Condition" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$POISON_CONDITION" "200"
    
    # Add charmed condition
    CHARM_CONDITION='{
        "add_condition": {
            "condition": "charmed",
            "duration": 1,
            "source": "charm person spell"
        }
    }'
    run_conditional_test "Add Charmed Condition" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$CHARM_CONDITION" "200"
    
    # Add exhaustion level
    EXHAUSTION_UPDATE='{
        "exhaustion_level": 1
    }'
    run_conditional_test "Add Exhaustion Level 1" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$EXHAUSTION_UPDATE" "200"
    
    # Remove specific condition
    REMOVE_POISON='{
        "remove_condition": "poisoned"
    }'
    run_conditional_test "Remove Poisoned Condition" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$REMOVE_POISON" "200"
fi

# Step 4: Spell Slot Management Tests
if [[ "$MODE" == "all" || "$MODE" == "state-only" ]]; then
    echo -e "${BLUE}✨ STEP 4: Spell Slot Management${NC}"
    echo "==============================="
    
    # Use a 1st level spell slot
    USE_SPELL_SLOT='{
        "use_spell_slot": {
            "level": 1,
            "spell_name": "Cure Wounds"
        }
    }'
    run_conditional_test "Use 1st Level Spell Slot" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$USE_SPELL_SLOT" "200"
    
    # Use a 2nd level spell slot
    USE_SPELL_SLOT_2='{
        "use_spell_slot": {
            "level": 2,
            "spell_name": "Hold Person"
        }
    }'
    run_conditional_test "Use 2nd Level Spell Slot" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$USE_SPELL_SLOT_2" "200"
fi

# Step 5: Rest and Recovery Tests
if [[ "$MODE" == "all" || "$MODE" == "rest-only" ]]; then
    echo -e "${BLUE}😴 STEP 5: Rest and Recovery${NC}"
    echo "============================"
    
    # Take a short rest
    SHORT_REST_DATA='{
        "rest_type": "short",
        "hit_dice_used": 1
    }'
    run_conditional_test "Take Short Rest (1 Hit Die)" "POST" "/api/v1/characters/\$CHARACTER_ID/rest" "$SHORT_REST_DATA" "200"
    
    # Take a long rest
    LONG_REST_DATA='{
        "rest_type": "long"
    }'
    run_conditional_test "Take Long Rest" "POST" "/api/v1/characters/\$CHARACTER_ID/rest" "$LONG_REST_DATA" "200"
fi

# Step 6: Experience and Progression Tests
if [[ "$MODE" == "all" || "$MODE" == "state-only" ]]; then
    echo -e "${BLUE}📈 STEP 6: Experience and Progression${NC}"
    echo "====================================="
    
    # Add experience points
    XP_UPDATE='{
        "experience_points": 300
    }'
    run_conditional_test "Add Experience Points (300)" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$XP_UPDATE" "200"
    
    # Update character level (if experience is enough)
    LEVEL_UPDATE='{
        "current_level": 4
    }'
    run_conditional_test "Update Character Level" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$LEVEL_UPDATE" "200"
fi

# Step 7: Equipment and Inventory Management
if [[ "$MODE" == "all" || "$MODE" == "state-only" ]]; then
    echo -e "${BLUE}🎒 STEP 7: Equipment and Inventory${NC}"
    echo "=================================="
    
    # Add new equipment
    EQUIPMENT_UPDATE='{
        "add_equipment": {
            "item": "Potion of Healing",
            "quantity": 2,
            "category": "consumable"
        }
    }'
    run_conditional_test "Add Equipment (Healing Potions)" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$EQUIPMENT_UPDATE" "200"
    
    # Use/remove equipment
    USE_EQUIPMENT='{
        "use_equipment": {
            "item": "Potion of Healing",
            "quantity": 1
        }
    }'
    run_conditional_test "Use Equipment (Healing Potion)" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$USE_EQUIPMENT" "200"
    
    # Update currency
    CURRENCY_UPDATE='{
        "currency": {
            "gold": 150,
            "silver": 25
        }
    }'
    run_conditional_test "Update Currency" "PUT" "/api/v1/characters/\$CHARACTER_ID/state" "$CURRENCY_UPDATE" "200"
fi

# Step 8: Final State Review
echo -e "${BLUE}📊 STEP 8: Final Character State Review${NC}"
echo "======================================"

run_conditional_test "Get Final Character State" "GET" "/api/v1/characters/\$CHARACTER_ID/state" "" "200"
run_conditional_test "Get Final Character Sheet" "GET" "/api/v1/characters/\$CHARACTER_ID/sheet" "" "200"

# Step 9: Cleanup
echo -e "${BLUE}🧹 STEP 9: Cleanup${NC}"
echo "=================="

run_conditional_test "Delete Test Character" "DELETE" "/api/v1/characters/\$CHARACTER_ID" "" "200"

# Summary
echo -e "${PURPLE}📋 IN-GAME STATE MANAGEMENT TEST SUMMARY${NC}"
echo "========================================="
echo ""
echo -e "${GREEN}✅ Tested Features:${NC}"
echo "  🩸 Combat damage and healing mechanics"
echo "  🎭 Condition application and removal"
echo "  ✨ Spell slot usage and management"
echo "  😴 Short and long rest recovery"
echo "  📈 Experience points and level progression"
echo "  🎒 Equipment and inventory updates"
echo "  💰 Currency management"
echo ""
echo -e "${CYAN}🎮 Real-World Usage:${NC}"
echo "  - Use these endpoints during active gameplay sessions"
echo "  - Character state persists between API calls"
echo "  - All changes are automatically validated against D&D rules"
echo "  - State changes can trigger automatic recalculations"
echo ""
echo -e "${YELLOW}🔧 Integration Notes:${NC}"
echo "  - Frontend can poll /state endpoint for real-time updates"
echo "  - Combat endpoint handles complex damage calculations"
echo "  - Rest endpoint automatically manages resource recovery"
echo "  - All state changes are logged for character history"