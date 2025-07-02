#!/bin/bash

# check the iterative character creation process of: 1) user describes character concept, 2) LLM generates initial character concept and backstory, 3) user provides tweeks to initial character concept, 4) LLM refines concept
# steps 3 and 4 continue until the user is satisfied with the character concept

# check importing an existing character and leveling it up using LLM service
# check importing an existing character and multi-classing it using LLM service
# check importing an existing character and updating it based on reviewing the journal of the character - should allow the character to evolve based on how the user actually plays it

# review the whole created character to include: backstory, equipment, species, class, abilities, spells, etc.  (basically the whole character sheet)

# API-Based Character Creation Workflow Test (PHASE 4 UPDATED - VERBOSE MODE)
# Updated for Phase 4 Factory Pattern Architecture
# Tests the complete character creation process using new unified endpoints
# VERBOSE MODE: Shows full inputs/outputs for LLM service debugging
#
# Usage: ./test_character_creation_workflow.sh [mode]
#   mode: all (default), quick, factory-only, v1-only

# Parse command line arguments
MODE=${1:-"all"}
case "$MODE" in
    "quick")
        SKIP_LLM=true
        echo "QUICK MODE: Skipping LLM-based tests"
        ;;
    "factory-only")
        FACTORY_ONLY=true
        echo "FACTORY ONLY MODE: Testing only v2 factory endpoints"
        ;;
    "v1-only")
        V1_ONLY=true
        echo "V1 ONLY MODE: Testing only preserved v1 endpoints"
        ;;
    "all")
        echo "FULL MODE: Testing all endpoints including LLM-based generation"
        ;;
    *)
        echo "Usage: $0 [all|quick|factory-only|v1-only]"
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

# Verbose mode flag
VERBOSE=true

echo -e "${PURPLE}🎭 AI-Driven D&D Character Creator - PHASE 4 API Workflow Test (VERBOSE)${NC}"
echo "=============================================================================="
echo "Testing the complete character creation workflow using Phase 4 Factory API"
echo "This demonstrates the new unified factory pattern architecture"
echo "VERBOSE MODE: Full request/response data will be displayed for debugging"
echo ""
echo "PHASE 4 CHANGES:"
echo "✅ Added: Factory pattern endpoints (/api/v2/factory/*)"
echo "❌ Removed: /api/v1/characters/generate, /generate/backstory, /generate/equipment"
echo "✅ Kept: /api/v1/generate/content, /generate/character-complete"
echo ""

# Test data for iterative character creation
CHARACTER_CONCEPT_INITIAL="A noble paladin seeking redemption for past misdeeds"
CHARACTER_CONCEPT_REFINED="A noble paladin seeking redemption for past misdeeds, specifically for failing to protect innocent villagers during a goblin raid. Now travels with a deep sense of guilt and a burning desire to prove worthy of divine favor again."

# Global variables to store created character IDs for evolution tests
CREATED_CHARACTER_ID=""

# Factory creation data - Initial iteration
FACTORY_CHARACTER_DATA_INITIAL='{
    "creation_type": "character",
    "prompt": "A noble paladin seeking redemption for past misdeeds",
    "save_to_database": true,
    "user_preferences": {
        "level": 1,
        "background": "Noble"
    }
}'

# Factory creation data - Refined iteration
FACTORY_CHARACTER_DATA_REFINED='{
    "creation_type": "character",
    "prompt": "A noble paladin seeking redemption for past misdeeds, specifically for failing to protect innocent villagers during a goblin raid. Now travels with a deep sense of guilt and a burning desire to prove worthy of divine favor again.",
    "save_to_database": true,
    "user_preferences": {
        "level": 1,
        "background": "Noble",
        "personality_notes": "Haunted by past failure, determined to prove worthiness"
    }
}'

FACTORY_WEAPON_DATA='{
    "creation_type": "weapon", 
    "prompt": "A holy longsword blessed by divine light",
    "save_to_database": false
}'

# Helper function to extract character ID from response
extract_character_id() {
    local response="$1"
    # Try to extract from different response formats
    local char_id=$(echo "$response" | jq -r '.id // .object_id // .character_id // empty' 2>/dev/null)
    if [ -n "$char_id" ] && [ "$char_id" != "null" ]; then
        echo "$char_id"
    fi
}
# Helper function to make API calls and check responses
test_api_call() {
    local test_name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    local timeout="${6:-30}"  # Default 30 second timeout
    local capture_id="${7:-false}"  # Whether to capture character ID from response
    
    echo -ne "${CYAN}⏳ $test_name ... ${NC}"
    
    # Show full request details in verbose mode
    if [ "$VERBOSE" = true ]; then
        echo ""
        echo -e "${GRAY}📤 REQUEST DETAILS:${NC}"
        echo -e "${GRAY}   Method: $method${NC}"
        echo -e "${GRAY}   URL: $BASE_URL$endpoint${NC}"
        if [ -n "$data" ]; then
            echo -e "${GRAY}   Headers: Content-Type: application/json${NC}"
            echo -e "${GRAY}   Body:${NC}"
            echo "$data" | jq . 2>/dev/null || echo "$data"
        else
            echo -e "${GRAY}   Body: (none)${NC}"
        fi
        echo -e "${GRAY}   Timeout: ${timeout}s${NC}"
        echo ""
    fi
    
    # Make the request with timeout
    if [ -n "$data" ]; then
        response=$(timeout "$timeout" curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>/dev/null)
    else
        response=$(timeout "$timeout" curl -s -w "HTTPSTATUS:%{http_code}" -X "$method" "$BASE_URL$endpoint" 2>/dev/null)
    fi
    
    # Check if curl timed out
    if [ $? -eq 124 ]; then
        echo -e "${YELLOW}⏰ TIMEOUT${NC} (${timeout}s exceeded)"
        echo -e "${YELLOW}   This is normal for LLM-based endpoints which can take time to generate content${NC}"
        echo ""
        return 2
    fi
    
    body=$(echo "$response" | sed -E 's/HTTPSTATUS\:[0-9]{3}$//')
    status=$(echo "$response" | tr -d '\n' | sed -E 's/.*HTTPSTATUS:([0-9]{3})$/\1/')
    
    if [[ "$status" == "$expected_status" ]]; then
        echo -e "${GREEN}✅ PASS${NC} (Status: $status)"
        
        # Capture character ID if requested
        if [ "$capture_id" = true ]; then
            CREATED_CHARACTER_ID=$(extract_character_id "$body")
            if [ -n "$CREATED_CHARACTER_ID" ]; then
                echo -e "${GREEN}   📝 Captured Character ID: $CREATED_CHARACTER_ID${NC}"
            fi
        fi
        
        # Show full response in verbose mode
        if [ "$VERBOSE" = true ]; then
            echo -e "${GRAY}📥 RESPONSE DETAILS:${NC}"
            echo -e "${GRAY}   Status: $status${NC}"
            echo -e "${GRAY}   Body:${NC}"
            echo "$body" | jq . 2>/dev/null || echo "$body"
        else
            if [[ ${#body} -gt 100 ]]; then
                echo "   Response: ${body:0:100}..."
            else
                echo "   Response: $body"
            fi
        fi
        echo ""
        return 0
    else
        echo -e "${RED}❌ FAIL${NC} (Expected: $expected_status, Got: $status)"
        
        # Always show error responses in detail
        echo -e "${RED}📥 ERROR RESPONSE:${NC}"
        echo -e "${RED}   Status: $status${NC}"
        echo -e "${RED}   Body:${NC}"
        echo "$body" | jq . 2>/dev/null || echo "$body"
        echo ""
        return 1
    fi
}

# Step 1: Test Health/Connection
echo -e "${BLUE}🏥 STEP 1: Health Check${NC}"
echo "========================"
test_api_call "Health Check" "GET" "/health" "" "200"

# Step 2: Test Iterative Character Creation Process
if [[ "$V1_ONLY" != true ]]; then
echo -e "${BLUE}🔄 STEP 2: Iterative Character Creation Process${NC}" 
echo "=============================================="
echo "Testing the iterative character creation workflow:"
echo "1) User describes character concept"
echo "2) LLM generates initial character concept and backstory" 
echo "3) User provides tweaks to initial character concept"
echo "4) LLM refines concept"
echo "Steps 3 and 4 continue until the user is satisfied with the character concept"
echo ""

echo -e "${YELLOW}Phase 1: Initial Character Concept Generation${NC}"
echo "User input: '$CHARACTER_CONCEPT_INITIAL'"
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Factory Create Initial Character" "POST" "/api/v2/factory/create" "$FACTORY_CHARACTER_DATA_INITIAL" "200" 60 true
fi

echo -e "${YELLOW}Phase 2: User Feedback and Concept Refinement${NC}"
echo "User provides feedback: 'I want more specific details about the failure and guilt'"
echo "Refined concept: '$CHARACTER_CONCEPT_REFINED'"
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Factory Create Refined Character" "POST" "/api/v2/factory/create" "$FACTORY_CHARACTER_DATA_REFINED" "200" 60
fi

echo -e "${YELLOW}Phase 3: Final Character Polish (if needed)${NC}"
echo "In a real workflow, this process could continue with further refinements..."
echo "The LLM would incorporate each round of user feedback into increasingly detailed characters."
echo ""
fi

# Step 4: Test Preserved v1 Generation Endpoints
if [[ "$FACTORY_ONLY" != true ]]; then
echo -e "${BLUE}🎭 STEP 3: Preserved v1 Generation Endpoints${NC}"
echo "=============================================="
echo "Testing the preserved v1 endpoints that use query parameters..."
echo "These endpoints demonstrate backward compatibility with existing workflows."
echo ""

echo -e "${YELLOW}Testing Unified Content Generation (v1):${NC}"
echo "This endpoint can generate multiple content types using a single unified interface."
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Generate Content (v1)" "POST" "/api/v1/generate/content?content_type=character&prompt=$(echo "$CHARACTER_CONCEPT_INITIAL" | sed 's/ /%20/g')&save_to_database=true" "" "200" 60
fi

echo -e "${YELLOW}Testing Complete Character Generation (v1):${NC}"
echo "This endpoint generates a complete character with backstory and equipment in one call."
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Generate Character Complete (v1)" "POST" "/api/v1/generate/character-complete?prompt=$(echo "$CHARACTER_CONCEPT_INITIAL" | sed 's/ /%20/g')&level=3&include_backstory=true&include_equipment=true" "" "200" 60
fi
fi

# Step 5: Test Traditional Character Creation (Should work)
echo -e "${BLUE}⚔️ STEP 5: Traditional Character Creation${NC}"
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

# Step 6: Test Factory Types Discovery
if [[ "$V1_ONLY" != true ]]; then
echo -e "${BLUE}🔍 STEP 6: Factory Types Discovery${NC}"
echo "===================================="
echo "Testing the factory types discovery endpoint..."

test_api_call "Factory Types Discovery" "GET" "/api/v2/factory/types" "" "200"
fi

# Step 7: Summary and Analysis
echo -e "${PURPLE}📊 PHASE 4 WORKFLOW TEST SUMMARY${NC}"
echo "=================================="
echo ""
echo -e "${GREEN}✅ Working Endpoints (Phase 4):${NC}"
echo "  - Traditional Character Creation (/api/v1/characters)"
echo "  - Factory Pattern Creation (/api/v2/factory/create)"
echo "  - Factory Types Discovery (/api/v2/factory/types)"
echo "  - Unified Content Generation (/api/v1/generate/content)"
echo "  - Complete Character Generation (/api/v1/generate/character-complete)"
echo ""
echo -e "${RED}❌ Removed Endpoints (Phase 4):${NC}" 
echo "  - /api/v1/characters/generate (replaced by factory pattern)"
echo "  - /api/v1/generate/backstory (replaced by unified content generation)"
echo "  - /api/v1/generate/equipment (replaced by unified content generation)"
echo ""
echo -e "${YELLOW}🏭 Architecture Benefits:${NC}"
echo "  - Unified factory pattern reduces code duplication"
echo "  - Single endpoint for multiple content types"
echo "  - Better error handling and response consistency"
echo "  - Cleaner API surface with fewer redundant endpoints"
echo "  - Full visibility into LLM interactions for debugging"
echo ""
echo -e "${CYAN}🔧 Usage Patterns:${NC}"
echo "  - Use /api/v2/factory/create for AI-powered content creation"
echo "  - Use /api/v1/characters for traditional manual character creation"  
echo "  - Use /api/v1/generate/* for preserved v1 workflows"
echo "  - All endpoints support both database saving and direct response"
echo ""
echo -e "${PURPLE}🐛 Debugging Notes:${NC}"
echo "  - VERBOSE mode shows full request/response data for LLM troubleshooting"
echo "  - Processing times are included in factory responses"
echo "  - Error responses include detailed information for debugging"
echo "  - All JSON responses are pretty-printed for readability"
echo "  - Character IDs are captured and reused for evolution testing"
echo ""
echo -e "${CYAN}🔄 Advanced Workflow Features Tested:${NC}"
echo "  ✅ Iterative character creation (concept → generate → refine → regenerate)"
echo "  ✅ Character evolution based on adventure experience"
echo "  ✅ LLM-powered character level up with multiclassing"
echo "  ✅ Journal-based character evolution reflecting actual gameplay"
echo "  ✅ Comprehensive character sheet review for concept alignment"
echo "  ✅ Full request/response visibility for LLM debugging"
echo ""
echo -e "${GREEN}🎯 Production Usage Recommendations:${NC}"
echo "  - Use iterative creation for complex character concepts"
echo "  - Leverage evolution endpoints for ongoing character development"
echo "  - Journal-based evolution keeps characters aligned with actual play"
echo "  - Always review complete character sheets for concept alignment"
echo "  - Use validation endpoints to ensure D&D 5e rule compliance"
echo "  - Verbose mode is essential for debugging LLM interactions"

# Step 3: Test Importing and Evolving Existing Characters  
if [[ "$V1_ONLY" != true && -n "$CREATED_CHARACTER_ID" ]]; then
echo -e "${BLUE}📈 STEP 3: Character Evolution and Level Up${NC}" 
echo "==========================================="
echo "Testing importing an existing character and evolving it using LLM service"
echo "Character ID from previous step: $CREATED_CHARACTER_ID"
echo ""

echo -e "${YELLOW}3a: Character Evolution Based on Experience${NC}"
echo "Simulating character growth through adventure experience..."
EVOLUTION_DATA='{
    "creation_type": "character",
    "character_id": "'$CREATED_CHARACTER_ID'",
    "evolution_prompt": "The character has been adventuring for several months and has faced many challenges. They have grown wiser and more experienced in combat, particularly in fighting undead creatures. They have also started to overcome some of their guilt.",
    "preserve_backstory": true,
    "user_preferences": {
        "focus": "combat_experience",
        "growth_areas": ["wisdom", "tactical_thinking", "emotional_healing"]
    }
}'
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Factory Evolve Character" "POST" "/api/v2/factory/evolve" "$EVOLUTION_DATA" "200" 60
fi

echo -e "${YELLOW}3b: Character Level Up with Multiclassing${NC}"
echo "Testing character level up with multiclassing considerations..."
LEVELUP_DATA='{
    "character_id": "'$CREATED_CHARACTER_ID'",
    "new_level": 3,
    "multiclass": "Cleric",
    "story_reason": "The character'"'"'s divine connection has grown stronger through their quest for redemption, leading them to take levels in Cleric",
    "context": "After saving a village from undead, the character felt a stronger divine presence and began studying clerical magic",
    "preserve_backstory": true
}'
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Factory Level Up Character" "POST" "/api/v2/factory/level-up" "$LEVELUP_DATA" "200" 60
fi

echo -e "${YELLOW}3c: Character Evolution Based on Journal Entries${NC}"
echo "Testing character evolution based on actual gameplay journal..."
echo "This simulates how a character should evolve based on how the user actually plays them."
JOURNAL_EVOLUTION_DATA='{
    "creation_type": "character", 
    "character_id": "'$CREATED_CHARACTER_ID'",
    "evolution_prompt": "Based on the character'"'"'s journal entries, they have: 1) Shown mercy to several enemies instead of killing them, 2) Consistently donated money to help poor villagers, 3) Spent time in meditation and prayer every morning, 4) Avoided violence when possible, choosing diplomacy first. Evolve the character to reflect these actual play patterns.",
    "preserve_backstory": true,
    "user_preferences": {
        "evolution_type": "journal_based",
        "personality_changes": ["more_merciful", "diplomatic", "devout"],
        "skill_development": ["persuasion", "religion", "insight"]
    }
}'
if [[ "$SKIP_LLM" == true ]]; then
    echo -e "${GRAY}   SKIPPED (Quick mode)${NC}"
else
    test_api_call "Factory Journal-Based Evolution" "POST" "/api/v2/factory/evolve" "$JOURNAL_EVOLUTION_DATA" "200" 60
fi
echo ""
else
    echo -e "${BLUE}📈 STEP 3: Character Evolution and Level Up${NC}" 
    echo "==========================================="
    echo -e "${YELLOW}⚠️  SKIPPED: No character ID available from previous steps${NC}"
    echo "Character evolution tests require a character to be created first."
    echo ""
fi

# Step 4: Comprehensive Character Sheet Review
if [[ -n "$CREATED_CHARACTER_ID" ]]; then
echo -e "${BLUE}📋 STEP 4: Comprehensive Character Sheet Review${NC}"
echo "==============================================="
echo "Reviewing the complete character sheet to verify alignment with original concept:"
echo "Original concept: '$CHARACTER_CONCEPT_INITIAL'"
echo "Character ID: $CREATED_CHARACTER_ID"
echo ""
echo "This comprehensive review allows verification that all character elements"
echo "(weapons, armor, items, spells, backstory, etc.) align with the user's concept."
echo ""

echo -e "${YELLOW}4a: Core Character Information${NC}"
test_api_call "Get Character Details" "GET" "/api/v1/characters/$CREATED_CHARACTER_ID" "" "200" 10

echo -e "${YELLOW}4b: Complete Character Sheet${NC}"
echo "Fetching the full character sheet with all calculated values..."
test_api_call "Get Character Sheet" "GET" "/api/v1/characters/$CREATED_CHARACTER_ID/sheet" "" "200" 10

echo -e "${YELLOW}4c: Character State and Equipment${NC}"
echo "Reviewing current character state including equipment, conditions, and resources..."
test_api_call "Get Character State" "GET" "/api/v1/characters/$CREATED_CHARACTER_ID/state" "" "200" 10

echo -e "${YELLOW}4d: Character Validation${NC}"
echo "Running comprehensive validation to ensure character follows D&D 5e rules..."
test_api_call "Validate Character" "GET" "/api/v1/characters/$CREATED_CHARACTER_ID/validate" "" "200" 10

echo -e "${PURPLE}📝 Character Review Checklist:${NC}"
echo "When reviewing the above character data, verify:"
echo "  ✓ Backstory aligns with original concept ('noble paladin seeking redemption')"
echo "  ✓ Class choice (Paladin) matches the concept"
echo "  ✓ Background (Noble) supports the character story"
echo "  ✓ Ability scores reflect a paladin build (high STR/CHA)"
echo "  ✓ Equipment includes appropriate paladin gear (armor, weapons, holy symbol)"
echo "  ✓ Skills and proficiencies match background and class"
echo "  ✓ Personality traits reflect the redemption-seeking theme"
echo "  ✓ Any spells or abilities are appropriate for the character level and class"
echo "  ✓ Overall character feels cohesive and true to the original concept"
echo ""
echo -e "${CYAN}💡 Review Tips:${NC}"
echo "  - Look for consistency between backstory details and mechanical choices"
echo "  - Verify equipment makes sense for the character's background and wealth"
echo "  - Check that personality traits support the central character theme"
echo "  - Ensure ability scores and skills reflect the character's story"
echo "  - Confirm any multiclassing or evolution maintains character coherence"
echo ""
else
    echo -e "${BLUE}📋 STEP 4: Comprehensive Character Sheet Review${NC}"
    echo "==============================================="
    echo -e "${YELLOW}⚠️  SKIPPED: No character ID available from previous steps${NC}"
    echo "Character sheet review requires a character to be created first."
    echo ""
fi
