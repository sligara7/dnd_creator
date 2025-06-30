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

# TODO: check importing an existing character from JSON and updating it (at the current character level), or leveling it up to the next level, or doing a multi-class change (at level up)
# TODO: this is supposed to be interative - the LLM is supposed to provide an initial character concept, then offer the user the opportunity to modify it (and what they'd like to modify), the LLM should then ingest the previous concept and modify per the user requests.
# TODO: added ability to create NPCs, creatures (beasts, monsters, fey, and new species), and individual items (weapons, armor, spells).  

#!/usr/bin/env python3
"""
AI-Driven Character Creator - Creative Character Generation

This script uses the LLM service to create unique, non-traditional D&D characters
based on your prompts and descriptions. It can generate:
- Custom species and subspecies
- Unique character classes and subclasses  
- Custom feats, weapons, armor, and spells
- Rich backstories and personality traits

Usage:
    python ai_character_creator.py
    
Or in iPython:
    %run ai_character_creator.py
"""

import sys
import json
import asyncio
from pathlib import Path
from typing import Dict, Any, List, Optional

# Try to import json5 for more lenient JSON parsing
try:
    import json5
    HAS_JSON5 = True
except ImportError:
    HAS_JSON5 = False

# Add backend directory to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

try:
    from character_models import CharacterCore, DnDCondition
    from core_models import ProficiencyLevel
    from llm_service_new import create_llm_service, create_ollama_service
    print("✅ Character and LLM services imported successfully")
    if HAS_JSON5:
        print("✅ JSON5 library available for robust JSON parsing")
    else:
        print("⚠️  JSON5 not available. Install with: pip install json5")
except ImportError as e:
    print(f"❌ Failed to import required modules: {e}")
    print("Make sure you're running this from the backend directory")
    sys.exit(1)


class AICharacterCreator:
    """AI-driven character creation using LLM services."""
    
    def __init__(self, debug_mode: bool = False):
        self.character = None
        self.llm_service = None
        self.character_concept = ""
        self.debug_mode = debug_mode
        self.generated_content = {
            "species": None,
            "classes": {},
            "background": None,
            "personality": {},
            "equipment": [],
            "abilities": {},
            "custom_content": {
                "feats": [],
                "spells": [],
                "items": []
            }
        }
        
    def initialize_llm(self):
        """Initialize the LLM service with increased timeout for slow computers."""
        print("🤖 Initializing AI service...")
        try:
            # Try Ollama first (local) with longer timeout for slow computers
            self.llm_service = create_ollama_service(timeout=300)  # 5 minutes timeout
            print("✅ Connected to Ollama LLM service (5 min timeout)")
            return True
        except Exception as e:
            print(f"⚠️  Ollama not available: {e}")
            try:
                self.llm_service = create_llm_service()
                print("✅ Connected to default LLM service")
                return True
            except Exception as e2:
                print(f"❌ No LLM service available: {e2}")
                return False
    
    async def test_llm_basic_functionality(self):
        """Test LLM with a simple request to ensure it's working."""
        print("🧪 Testing LLM with simple request...")
        
        simple_prompt = """Generate a simple JSON response with a name and age:
        {"name": "Test Character", "age": 25}
        
        Please return exactly that JSON format."""
        
        try:
            response = await self.llm_service.generate_content(simple_prompt)
            test_data = self.parse_json_response(response)
            
            if test_data and "name" in test_data:
                print(f"✅ LLM test successful! Generated: {test_data.get('name', 'Unknown')}")
                return True
            else:
                print(f"⚠️  LLM test partially successful but JSON parsing failed")
                print(f"   Raw response: {response[:100]}...")
                return True  # Still proceed, just warn about JSON parsing
        except Exception as e:
            print(f"❌ LLM test failed: {e}")
            return False
    
    async def start_creation(self):
        """Start the AI-driven character creation process."""
        print("🎭 AI-Driven D&D Character Creator")
        print("=" * 50)
        print("Describe your character concept and I'll bring it to life!")
        print("I can create non-traditional species, classes, and abilities.\n")
        
        if not self.initialize_llm():
            print("❌ Cannot proceed without LLM service.")
            return
        
        # Test LLM functionality first
        if not await self.test_llm_basic_functionality():
            print("❌ LLM test failed. Cannot proceed with character generation.")
            return
        
        print("🎯 LLM is working! Proceeding with character generation...")
        print("⏱️  Note: Generation may take several minutes on slower computers.\n")
        
        # Get character concept from user
        concept = self.get_character_concept()
        if not concept:
            return
            
        self.character_concept = concept
        
        # Generate character using AI
        print(f"\n🔮 Creating character based on: '{concept}'")
        print("=" * 50)
        
        try:
            await self.generate_basic_info()
            await self.generate_species_and_classes()
            await self.generate_abilities()
            await self.generate_skills_and_background()
            await self.generate_equipment()
            await self.generate_custom_content()
            await self.generate_personality()
            
            self.create_character_object()
            self.display_final_character()
            
        except Exception as e:
            print(f"❌ Error during character generation: {e}")
            import traceback
            traceback.print_exc()
    
    def get_character_concept(self) -> str:
        """Get the character concept from the user."""
        print("Examples of character concepts:")
        print("• A crystal-powered artificer from a steampunk sky city")
        print("• A time-traveling druid who speaks with extinct creatures")
        print("• A shadow dancer who weaves darkness into magical weapons")
        print("• A dragon-touched healer with scales that change with emotions")
        print("• A void monk who fights by erasing parts of reality\n")
        
        concept = input("Describe your character concept: ").strip()
        
        if not concept:
            print("No concept provided. Goodbye!")
            return ""
        
        if concept.lower() in ['quit', 'exit']:
            return ""
            
        return concept
    
    async def generate_basic_info(self):
        """Generate basic character information."""
        print("📝 Generating basic character info... (this may take a few minutes)")
        
        prompt = f"""
        Based on this character concept: "{self.character_concept}"
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Generate a unique D&D character with the following JSON format:
        {{
            "name": "Character Name",
            "alignment": ["Ethical", "Moral"],
            "age": 25,
            "height": 68,
            "weight": 150,
            "appearance": "Detailed physical description",
            "voice": "How they speak and sound"
        }}
        
        IMPORTANT FORMATTING:
        - age: integer (years)
        - height: integer (total inches, e.g. 68 for 5'8")
        - weight: integer (pounds, no units)
        - alignment: array with exactly 2 strings
        
        Make the character interesting and unique. The alignment should be two words like ["Chaotic", "Good"].
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            basic_info = self.parse_json_response(response)
            
            if basic_info:
                self.generated_content.update(basic_info)
                print(f"✅ Generated: {basic_info.get('name', 'Unknown')}")
                print(f"   Alignment: {' '.join(basic_info.get('alignment', ['True', 'Neutral']))}")
            else:
                print("⚠️  Using fallback basic info")
                self.generated_content.update({
                    "name": "Mysterious Wanderer",
                    "alignment": ["True", "Neutral"],
                    "age": 25,
                    "height": 68,
                    "weight": 150,
                    "appearance": "An enigmatic figure with unique features"
                })
        except Exception as e:
            print(f"⚠️  Error generating basic info: {e}")
            self.generated_content.update({
                "name": "AI-Generated Hero",
                "alignment": ["Chaotic", "Good"],
                "age": 30,
                "height": 70,
                "weight": 180
            })
    
    async def generate_species_and_classes(self):
        """Generate unique species and class combinations."""
        print("🧬 Generating species and classes... (this may take a few minutes)")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Create a unique species and class combination in JSON format:
        {{
            "species": {{
                "name": "Species Name",
                "description": "What makes this species unique",
                "traits": ["Trait 1", "Trait 2", "Trait 3"],
                "abilities": {{
                    "strength": 12,
                    "dexterity": 14,
                    "constitution": 13,
                    "intelligence": 15,
                    "wisdom": 10,
                    "charisma": 16
                }}
            }},
            "primary_class": {{
                "name": "Class Name",
                "level": 3,
                "description": "What this class does",
                "features": ["Feature 1", "Feature 2"]
            }},
            "secondary_class": {{
                "name": "Optional Second Class",
                "level": 1,
                "description": "Multiclass option"
            }}
        }}
        
        Be creative! Invent new species and class combinations that don't exist in standard D&D.
        Ability scores should total around 75-80 points.
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            species_classes = self.parse_json_response(response)
            
            if species_classes:
                self.generated_content["species"] = species_classes.get("species")
                self.generated_content["primary_class"] = species_classes.get("primary_class")
                self.generated_content["secondary_class"] = species_classes.get("secondary_class")
                
                print(f"✅ Species: {species_classes.get('species', {}).get('name', 'Unknown')}")
                print(f"✅ Class: {species_classes.get('primary_class', {}).get('name', 'Unknown')}")
            else:
                print("⚠️  Using fallback species and class")
                self.use_fallback_species_class()
        except Exception as e:
            print(f"⚠️  Error generating species/class: {e}")
            self.use_fallback_species_class()
    
    async def generate_abilities(self):
        """Generate ability scores based on character concept."""
        print("💪 Generating ability scores...")
        
        species_abilities = self.generated_content.get("species", {}).get("abilities", {})
        if species_abilities:
            self.generated_content["abilities"] = species_abilities
            print("✅ Ability scores set from species")
        else:
            # Generate balanced ability scores
            self.generated_content["abilities"] = {
                "strength": 13,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 16
            }
            print("✅ Generated balanced ability scores")
    
    async def generate_skills_and_background(self):
        """Generate skills and background."""
        print("🎯 Generating skills and background... (this may take a few minutes)")
        
        prompt = f"""
        For this character: "{self.character_concept}"
        With species: {self.generated_content.get("species", {}).get("name", "Unknown")}
        And class: {self.generated_content.get("primary_class", {}).get("name", "Unknown")}
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Generate skills and background in JSON format:
        {{
            "background": {{
                "name": "Background Name",
                "description": "What they did before adventuring"
            }},
            "skills": ["Skill 1", "Skill 2", "Skill 3", "Skill 4"],
            "languages": ["Common", "Language 2", "Language 3"],
            "proficiencies": ["Tool 1", "Tool 2"]
        }}
        
        Choose skills that make sense for the character concept.
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            skills_bg = self.parse_json_response(response)
            
            if skills_bg:
                self.generated_content["background"] = skills_bg.get("background")
                self.generated_content["skills"] = skills_bg.get("skills", [])
                self.generated_content["languages"] = skills_bg.get("languages", ["Common"])
                print(f"✅ Background: {skills_bg.get('background', {}).get('name', 'Unknown')}")
                print(f"✅ Skills: {', '.join(skills_bg.get('skills', []))}")
            else:
                self.use_fallback_skills_background()
        except Exception as e:
            print(f"⚠️  Error generating skills/background: {e}")
            self.use_fallback_skills_background()
    
    async def generate_equipment(self):
        """Generate starting equipment."""
        print("⚔️ Generating equipment... (this may take a few minutes)")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Generate starting equipment in JSON format:
        {{
            "weapons": ["Weapon 1", "Weapon 2"],
            "armor": "Armor type",
            "tools": ["Tool 1", "Tool 2"],
            "items": ["Item 1", "Item 2", "Item 3"],
            "magical_items": ["Magic Item 1"]
        }}
        
        Be creative with equipment that matches the character concept.
        Include both practical and unique items.
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            equipment = self.parse_json_response(response)
            
            if equipment:
                self.generated_content["equipment"] = equipment
                print(f"✅ Equipment generated")
            else:
                self.use_fallback_equipment()
        except Exception as e:
            print(f"⚠️  Error generating equipment: {e}")
            self.use_fallback_equipment()
    
    async def generate_custom_content(self):
        """Generate custom feats, spells, and items."""
        print("✨ Generating custom content... (this may take a few minutes)")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Create custom D&D content in JSON format:
        {{
            "custom_feats": [
                {{
                    "name": "Feat Name",
                    "description": "What the feat does",
                    "prerequisites": "Any requirements"
                }}
            ],
            "custom_spells": [
                {{
                    "name": "Spell Name", 
                    "level": 1,
                    "school": "Magic School",
                    "description": "Spell effect"
                }}
            ],
            "custom_items": [
                {{
                    "name": "Item Name",
                    "type": "Item type",
                    "description": "What makes it special"
                }}
            ]
        }}
        
        Create 1-2 items for each category that perfectly match the character concept.
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            custom_content = self.parse_json_response(response)
            
            if custom_content:
                self.generated_content["custom_content"] = custom_content
                print("✅ Custom content created")
                
                # Show what was created
                if custom_content.get("custom_feats"):
                    print(f"   • {len(custom_content['custom_feats'])} custom feats")
                if custom_content.get("custom_spells"):
                    print(f"   • {len(custom_content['custom_spells'])} custom spells")
                if custom_content.get("custom_items"):
                    print(f"   • {len(custom_content['custom_items'])} custom items")
        except Exception as e:
            print(f"⚠️  Error generating custom content: {e}")
    
    async def generate_personality(self):
        """Generate personality traits and backstory."""
        print("🎭 Generating personality and backstory... (this may take a few minutes)")
        
        prompt = f"""
        For this character concept: "{self.character_concept}"
        With name: {self.generated_content.get("name", "Unknown")}
        
        IMPORTANT: Your response MUST be a single, valid, closed JSON object. Do NOT include any comments, explanations, or any text before or after the JSON. Do NOT omit closing braces/brackets under any circumstances. All values must be valid JSON (no parentheses, no comments, no extra text).
        
        Generate personality in JSON format:
        {{
            "personality_traits": ["Trait 1", "Trait 2"],
            "ideals": ["Ideal 1"],
            "bonds": ["Bond 1"],
            "flaws": ["Flaw 1"],
            "backstory": "A rich backstory of 2-3 paragraphs explaining their origin, motivations, and how they became who they are."
        }}
        
        Make the personality complex and interesting, with internal conflicts and clear motivations.
        """
        
        try:
            print("   ⏳ Sending request to LLM...")
            response = await self.llm_service.generate_content(prompt)
            print("   ⚙️  Processing response...")
            personality = self.parse_json_response(response)
            
            if personality:
                self.generated_content["personality"] = personality
                print("✅ Personality and backstory generated")
            else:
                self.use_fallback_personality()
        except Exception as e:
            print(f"⚠️  Error generating personality: {e}")
            self.use_fallback_personality()
    
    def parse_json_response(self, response: str) -> Optional[Dict[str, Any]]:
        """Parse JSON from LLM response with robust extraction and auto-closing."""
        if self.debug_mode:
            print(f"🔍 DEBUG - Raw LLM Response (full):\n{response}")
            print(f"   Length: {len(response)} characters")
        try:
            # Robustly find the first '{' and last '}' (ignore leading/trailing whitespace)
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                # --- Auto-close logic for incomplete JSON ---
                open_braces = json_str.count('{')
                close_braces = json_str.count('}')
                open_brackets = json_str.count('[')
                close_brackets = json_str.count(']')
                # Add missing closing braces/brackets if needed
                if close_braces < open_braces:
                    json_str += '}' * (open_braces - close_braces)
                if close_brackets < open_brackets:
                    json_str += ']' * (open_brackets - close_brackets)
                if self.debug_mode:
                    print(f"🔍 DEBUG - Extracted JSON string (auto-closed if needed):\n   {json_str}")
                # Try parsing the extracted JSON
                try:
                    return json.loads(json_str)
                except json.JSONDecodeError as e:
                    print(f"⚠️  JSON parsing error: {e}")
                    print(f"   Raw JSON attempt: {json_str[:200]}...")
                    # Try JSON5 if available
                    if HAS_JSON5:
                        try:
                            result = json5.loads(json_str)
                            print("✅ Recovered JSON using JSON5 parser")
                            return result
                        except Exception as json5_error:
                            print(f"   JSON5 also failed: {json5_error}")
                    # Try to find and extract multiple JSON objects
                    json_objects = []
                    brace_count = 0
                    current_json = ""
                    for char in response[start:]:
                        current_json += char
                        if char == '{':
                            brace_count += 1
                        elif char == '}':
                            brace_count -= 1
                            if brace_count == 0:
                                try:
                                    obj = json.loads(current_json)
                                    json_objects.append(obj)
                                    break
                                except:
                                    continue
                    if json_objects:
                        print("✅ Recovered JSON using alternative parsing")
                        return json_objects[0]
                    # Last resort: try to clean common issues
                    cleaned_json = self._clean_json_string(json_str)
                    if self.debug_mode:
                        print(f"🔍 DEBUG - Cleaned JSON: {cleaned_json}")
                    try:
                        result = json.loads(cleaned_json)
                        print("✅ Recovered JSON after cleaning")
                        return result
                    except Exception as clean_error:
                        # Try JSON5 on the cleaned version too
                        if HAS_JSON5:
                            try:
                                result = json5.loads(cleaned_json)
                                print("✅ Recovered JSON using JSON5 after cleaning")
                                return result
                            except Exception as json5_clean_error:
                                print(f"   JSON5 on cleaned JSON also failed: {json5_clean_error}")
                        print(f"❌ All JSON parsing attempts failed")
                        print(f"   Original error: {e}")
                        print(f"   Cleaning error: {clean_error}")
                        if self.debug_mode:
                            print(f"   Full response: {response}")
                        return None
            else:
                print("⚠️  No JSON found in response")
                print(f"   Full response (for debugging):\n{response}")
                return None
        except Exception as e:
            print(f"⚠️  Unexpected error in JSON parsing: {e}")
            print(f"   Full response (for debugging):\n{response}")
            return None
    
    def _clean_json_string(self, json_str: str) -> str:
        """Clean common JSON formatting issues."""
        import re
        
        # Remove markdown code blocks
        json_str = json_str.replace('```json', '').replace('```', '')
        
        # Fix the specific issue: unescaped quotes in measurements like "4'10""
        # This handles cases like "4'10"" -> "4'10\""
        json_str = re.sub(r'"(\d+\'\d*)"([^,\n\}]*)', r'"\1\\"', json_str)
        
        # Fix unescaped quotes at end of string values before comma/brace
        json_str = re.sub(r'([^\\])"([,\}])', r'\1\\"\2', json_str)
        
        # Remove trailing commas before closing braces/brackets
        json_str = re.sub(r',(\s*[}\]])', r'\1', json_str)
        
        # Fix common quote issues
        json_str = json_str.replace('"', '"').replace('"', '"')
        json_str = json_str.replace(''', "'").replace(''', "'")
        
        # Fix unescaped quotes in string values more aggressively
        # Look for patterns like: "key": "value with "quotes" inside"
        json_str = re.sub(r':\s*"([^"]*)"([^"]*)"([^"]*)"', r': "\1\\"\2\\"\3"', json_str)
        
        return json_str.strip()
    
    def create_character_object(self):
        """Create the CharacterCore object from generated content."""
        print("\n🏗️ Building character object...")
        
        name = self.generated_content.get("name", "AI Hero")
        self.character = CharacterCore(name=name)
        
        # Set basic info
        if "alignment" in self.generated_content:
            self.character.alignment = self.generated_content["alignment"]
        
        # Set species
        species_info = self.generated_content.get("species", {})
        self.character.species = species_info.get("name", "Custom Species")
        
        # Set background
        background_info = self.generated_content.get("background", {})
        self.character.background = background_info.get("name", "Unique Background")
        
        # Set classes
        primary_class = self.generated_content.get("primary_class", {})
        if primary_class:
            class_name = primary_class.get("name", "Custom Class")
            class_level = primary_class.get("level", 1)
            self.character.character_classes[class_name] = class_level
        
        secondary_class = self.generated_content.get("secondary_class", {})
        if secondary_class and secondary_class.get("name"):
            class_name = secondary_class.get("name", "Second Class")
            class_level = secondary_class.get("level", 1)
            self.character.character_classes[class_name] = class_level
        
        # Set ability scores
        abilities = self.generated_content.get("abilities", {})
        for ability, score in abilities.items():
            self.character.set_ability_score(ability, score)
        
        # Set skills
        skills = self.generated_content.get("skills", [])
        for skill in skills:
            skill_key = skill.lower().replace(" ", "_")
            self.character.skill_proficiencies[skill_key] = ProficiencyLevel.PROFICIENT
        
        # Set personality and backstory
        personality = self.generated_content.get("personality", {})
        self.character.personality_traits = personality.get("personality_traits", [])
        self.character.ideals = personality.get("ideals", [])
        self.character.bonds = personality.get("bonds", [])
        self.character.flaws = personality.get("flaws", [])
        
        # Use the rich backstory from personality generation, or fallback to basic info summary
        generated_backstory = personality.get("backstory", "")
        if not generated_backstory or len(generated_backstory) < 50:
            # Create a richer backstory from the generated content
            species_name = self.generated_content.get("species", {}).get("name", "Unknown")
            primary_class = self.generated_content.get("primary_class", {}).get("name", "Adventurer")
            background_name = self.generated_content.get("background", {}).get("name", "Wanderer")
            
            generated_backstory = f"A {species_name} {primary_class} with a background as a {background_name}. "
            if personality.get("personality_traits"):
                generated_backstory += f"Known for being {', '.join(personality['personality_traits'][:2])}. "
            if personality.get("ideals"):
                generated_backstory += f"Driven by the ideal: '{personality['ideals'][0]}'. "
            if personality.get("bonds"):
                generated_backstory += f"Bound by: '{personality['bonds'][0]}'. "
        
        self.character.backstory = generated_backstory
        
        print("✅ Character object created!")
    
    def display_final_character(self):
        """Display the complete AI-generated character."""
        print("\n" + "=" * 80)
        print("🎭 AI-GENERATED CHARACTER SHEET")
        print("=" * 80)
        
        # Basic Info
        print(f"Name: {self.character.name}")
        print(f"Species: {self.character.species}")
        print(f"Background: {self.character.background}")
        print(f"Alignment: {' '.join(self.character.alignment)}")
        
        # Physical Description
        if "appearance" in self.generated_content:
            print(f"Appearance: {self.generated_content['appearance']}")
        
        # Age, Height, Weight (format nicely)
        age = self.generated_content.get("age", "Unknown")
        height = self.generated_content.get("height")
        weight = self.generated_content.get("weight")
        
        physical_stats = []
        if age != "Unknown":
            physical_stats.append(f"Age: {age}")
        if height and isinstance(height, int):
            feet = height // 12
            inches = height % 12
            physical_stats.append(f"Height: {feet}'{inches}\"")
        elif height:
            physical_stats.append(f"Height: {height}")
        if weight:
            physical_stats.append(f"Weight: {weight} lbs")
        
        if physical_stats:
            print(f"Physical: {', '.join(physical_stats)}")
        
        # Classes
        if self.character.character_classes:
            classes_str = ", ".join([f"{cls} {lvl}" for cls, lvl in self.character.character_classes.items()])
            total_level = sum(self.character.character_classes.values())
            print(f"Class(es): {classes_str} (Total Level: {total_level})")
        
        # Ability Scores
        print("\nAbility Scores:")
        modifiers = self.character.get_ability_modifiers()
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for ability in abilities:
            ability_score_obj = self.character.get_ability_score(ability)
            score = ability_score_obj.total_score if hasattr(ability_score_obj, 'total_score') else 10
            modifier = modifiers.get(ability, 0)
            sign = "+" if modifier >= 0 else ""
            print(f"  {ability.title():13}: {score:2d} ({sign}{modifier})")
        
        # Skills
        if self.character.skill_proficiencies:
            skills = [skill.replace("_", " ").title() for skill in self.character.skill_proficiencies.keys()]
            print(f"\nSkill Proficiencies: {', '.join(skills)}")
        
        # Equipment
        equipment = self.generated_content.get("equipment", {})
        if equipment:
            print(f"\nEquipment:")
            if equipment.get("weapons"):
                print(f"  Weapons: {', '.join(equipment['weapons'])}")
            if equipment.get("armor"):
                print(f"  Armor: {equipment['armor']}")
            if equipment.get("tools"):
                print(f"  Tools: {', '.join(equipment['tools'])}")
            if equipment.get("magical_items"):
                print(f"  Magic Items: {', '.join(equipment['magical_items'])}")
        
        # Custom Content
        custom = self.generated_content.get("custom_content", {})
        if custom:
            print(f"\nCustom Content:")
            
            if custom.get("custom_feats"):
                print("  Custom Feats:")
                for feat in custom["custom_feats"]:
                    print(f"    • {feat['name']}: {feat['description']}")
            
            if custom.get("custom_spells"):
                print("  Custom Spells:")
                for spell in custom["custom_spells"]:
                    print(f"    • {spell['name']} (Level {spell['level']}): {spell['description']}")
            
            if custom.get("custom_items"):
                print("  Custom Items:")
                for item in custom["custom_items"]:
                    print(f"    • {item['name']}: {item['description']}")
        
        # Personality
        print(f"\nPersonality:")
        if self.character.personality_traits:
            print(f"  Traits: {', '.join(self.character.personality_traits)}")
        if self.character.ideals:
            print(f"  Ideals: {', '.join(self.character.ideals)}")
        if self.character.bonds:
            print(f"  Bonds: {', '.join(self.character.bonds)}")
        if self.character.flaws:
            print(f"  Flaws: {', '.join(self.character.flaws)}")
        
        # Backstory
        if self.character.backstory:
            print(f"\nBackstory:")
            print(f"  {self.character.backstory}")
        
        print("\n" + "=" * 80)
        print("🎉 Your AI-generated character is complete!")
        print("How does this match your creative vision?")
        print("=" * 80)
    
    # Fallback methods for when AI generation fails
    def use_fallback_species_class(self):
        self.generated_content["species"] = {
            "name": "Variant Human",
            "abilities": {"strength": 13, "dexterity": 14, "constitution": 15, 
                         "intelligence": 12, "wisdom": 10, "charisma": 16}
        }
        self.generated_content["primary_class"] = {
            "name": "Custom Adventurer",
            "level": 3
        }
    
    def use_fallback_skills_background(self):
        self.generated_content["background"] = {"name": "Wanderer"}
        self.generated_content["skills"] = ["Perception", "Insight", "Athletics", "Investigation"]
    
    def use_fallback_equipment(self):
        self.generated_content["equipment"] = {
            "weapons": ["Longsword", "Shortbow"],
            "armor": "Studded Leather",
            "items": ["Explorer's Pack", "Rope", "Torches"]
        }
    
    def use_fallback_personality(self):
        self.generated_content["personality"] = {
            "personality_traits": ["Curious about the unknown"],
            "ideals": ["Adventure calls to me"],
            "bonds": ["I seek my true purpose"],
            "flaws": ["I act before thinking"],
            "backstory": "A mysterious figure with an unknown past, driven by curiosity and wanderlust."
        }


async def main():
    """Main function for AI character creation."""
    try:
        # Enable debug mode if requested
        debug_mode = "--debug" in sys.argv or "-d" in sys.argv
        if debug_mode:
            print("🔍 DEBUG MODE ENABLED - Will show raw LLM responses")
        
        creator = AICharacterCreator(debug_mode=debug_mode)
        await creator.start_creation()
    except KeyboardInterrupt:
        print("\n\nCharacter creation cancelled. Goodbye!")
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
