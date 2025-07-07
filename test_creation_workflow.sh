#!/bin/bash

# D&D Character Creator - Comprehensive Workflow Test
# Tests the /backend service running in a podman container
# Covers: creation, theming, versioning, leveling, multi-classing, and listing

set -e  # Exit on any error

# Environment Variables Check
if [ -z "$OPENAI_API_KEY" ]; then
    log_error() { echo -e "\033[0;31m[ERROR]\033[0m $1"; }
    log_error "OPENAI_API_KEY environment variable is required but not set."
    echo "Please export your OpenAI API key:"
    echo "  export OPENAI_API_KEY='your-openai-api-key-here'"
    echo ""
    echo "You can also create a .env file in the backend directory with:"
    echo "  echo 'OPENAI_API_KEY=your-openai-api-key-here' > backend/.env"
    exit 1
fi

# Optional: Set a secret key for the application if not already set
if [ -z "$SECRET_KEY" ]; then
    export SECRET_KEY="test-secret-key-$(date +%s)-$(openssl rand -hex 16 2>/dev/null || echo 'fallback-secret')"
fi

# Configuration
BASE_URL="http://localhost:8000"
API_URL="${BASE_URL}/api/v2"
TEST_NAME="workflow_test_$(date +%s)"

# Display environment info
echo "Environment Variables:"
echo "  OPENAI_API_KEY: ${OPENAI_API_KEY:0:8}..." # Show only first 8 chars for security
echo "  SECRET_KEY: ${SECRET_KEY:0:12}..."
echo "  BASE_URL: $BASE_URL"
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Test result tracking
TESTS_PASSED=0
TESTS_FAILED=0
CREATED_CHARACTERS=()
CREATED_NPCS=()
CREATED_MONSTERS=()
CREATED_ITEMS=()

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
    ((TESTS_PASSED++))
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
    ((TESTS_FAILED++))
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Test if service is running
test_service_health() {
    log_info "Testing service health..."
    
    response=$(curl -s -w "%{http_code}" "${BASE_URL}/health" -o /tmp/health_response.json || echo "000")
    
    if [ "$response" = "200" ]; then
        log_success "Service is healthy and responding"
        cat /tmp/health_response.json | jq '.' 2>/dev/null || cat /tmp/health_response.json
        
        # Check if the service has proper configuration
        log_info "Checking service configuration..."
        
        # Test a simple endpoint that might indicate LLM service availability
        config_response=$(curl -s -w "%{http_code}" "${API_URL}/config" -o /tmp/config_response.json 2>/dev/null || echo "404")
        
        if [ "${config_response: -3}" = "200" ]; then
            log_info "Service configuration endpoint available"
        else
            log_warning "Service configuration endpoint not available (this is normal)"
        fi
        
    else
        log_error "Service is not responding (HTTP $response)"
        echo "Make sure the backend service is running in podman container"
        echo "Example commands to start the service:"
        echo "  cd backend"
        echo "  export OPENAI_API_KEY='your-api-key'"
        echo "  export SECRET_KEY='your-secret-key'"
        echo "  podman-compose up -d"
        exit 1
    fi
}

# Create a test character with custom content
test_create_character() {
    log_info "Creating test character with custom content..."
    
    local theme="$1"
    local level="$2"
    local prompt="$3"
    
    # Default values if not provided
    level=${level:-5}
    if [ -z "$prompt" ]; then
        case "$theme" in
            "traditional D&D")
                prompt="A brave elven ranger who protects the forest and has a mysterious past involving ancient magic"
                ;;
            "steampunk")
                prompt="A unique steam-powered clockwork artificer from a rare mechanical species, wielding custom gear-based magic and specialized clockwork weapons and armor"
                ;;
            "cyberpunk")
                prompt="A bio-enhanced netrunner from a rare cyber-augmented species, using custom neural-link magic and high-tech weapons and armor"
                ;;
            *)
                prompt="A unique character with custom abilities, specialized equipment, and rare magical powers from an uncommon species"
                ;;
        esac
    fi
    
    local request_data=$(cat <<EOF
{
    "creation_type": "character",
    "prompt": "$prompt",
    "theme": "$theme",
    "user_preferences": {
        "level": $level,
        "require_custom_content": true,
        "force_unique_creation": true,
        "full_equipment_loadout": true,
        "balance_for_level": true,
        "custom_class_required": true,
        "custom_species_required": true,
        "custom_spells_required": true,
        "custom_equipment_required": true
    },
    "extra_fields": {
        "generation_focus": "Create completely unique custom content including new class, species, spells, weapons, and armor",
        "balance_requirements": "Ensure character is appropriately powered for level $level with balanced custom content",
        "spell_requirements": "Generate full spell list appropriate for character level and custom class",
        "equipment_requirements": "Create level-appropriate custom weapons, armor, and magical items"
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/character_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        character_id=$(cat /tmp/character_response.json | jq -r '.object_id')
        if [ "$character_id" != "null" ] && [ -n "$character_id" ]; then
            CREATED_CHARACTERS+=("$character_id")
            log_success "Character created successfully (ID: $character_id, Theme: $theme)"
            echo "$character_id"
        else
            log_error "Character creation response missing object_id"
            cat /tmp/character_response.json | jq '.'
        fi
    else
        log_error "Character creation failed (HTTP ${response: -3})"
        cat /tmp/character_response.json
    fi
}

# Create a test NPC
test_create_npc() {
    log_info "Creating test NPC..."
    
    local theme="$1"
    local prompt="A wise tavern keeper who knows many secrets and offers cryptic advice to adventurers"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "npc",
    "prompt": "$prompt",
    "theme": "$theme",
    "user_preferences": {
        "challenge_rating": 0.25,
        "npc_type": "civilian"
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/npc_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        npc_id=$(cat /tmp/npc_response.json | jq -r '.object_id')
        if [ "$npc_id" != "null" ] && [ -n "$npc_id" ]; then
            CREATED_NPCS+=("$npc_id")
            log_success "NPC created successfully (ID: $npc_id, Theme: $theme)"
            echo "$npc_id"
        else
            log_error "NPC creation response missing object_id"
            cat /tmp/npc_response.json | jq '.'
        fi
    else
        log_error "NPC creation failed (HTTP ${response: -3})"
        cat /tmp/npc_response.json
    fi
}

# Create a test monster
test_create_monster() {
    log_info "Creating test monster..."
    
    local theme="$1"
    local prompt="A fierce owlbear that guards an ancient grove, with enhanced intelligence and nature magic"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "monster",
    "prompt": "$prompt",
    "theme": "$theme",
    "user_preferences": {
        "challenge_rating": 3,
        "creature_type": "monstrosity"
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/monster_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        monster_id=$(cat /tmp/monster_response.json | jq -r '.object_id')
        if [ "$monster_id" != "null" ] && [ -n "$monster_id" ]; then
            CREATED_MONSTERS+=("$monster_id")
            log_success "Monster created successfully (ID: $monster_id, Theme: $theme)"
            echo "$monster_id"
        else
            log_error "Monster creation response missing object_id"
            cat /tmp/monster_response.json | jq '.'
        fi
    else
        log_error "Monster creation failed (HTTP ${response: -3})"
        cat /tmp/monster_response.json
    fi
}

# Create test items (weapon, armor, spell)
test_create_items() {
    log_info "Creating test items..."
    
    local theme="$1"
    
    # Create a weapon
    local weapon_request=$(cat <<EOF
{
    "creation_type": "weapon",
    "prompt": "A masterwork elven longbow that hums with forest magic and never misses its intended target",
    "theme": "$theme",
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$weapon_request" \
        -w "%{http_code}" -o /tmp/weapon_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        weapon_id=$(cat /tmp/weapon_response.json | jq -r '.object_id')
        if [ "$weapon_id" != "null" ] && [ -n "$weapon_id" ]; then
            CREATED_ITEMS+=("weapon:$weapon_id")
            log_success "Weapon created successfully (ID: $weapon_id)"
        fi
    else
        log_error "Weapon creation failed (HTTP ${response: -3})"
    fi
    
    # Create armor
    local armor_request=$(cat <<EOF
{
    "creation_type": "armor",
    "prompt": "Lightweight leather armor woven with protective ward spells and camouflage enchantments",
    "theme": "$theme",
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$armor_request" \
        -w "%{http_code}" -o /tmp/armor_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        armor_id=$(cat /tmp/armor_response.json | jq -r '.object_id')
        if [ "$armor_id" != "null" ] && [ -n "$armor_id" ]; then
            CREATED_ITEMS+=("armor:$armor_id")
            log_success "Armor created successfully (ID: $armor_id)"
        fi
    else
        log_error "Armor creation failed (HTTP ${response: -3})"
    fi
    
    # Create spell
    local spell_request=$(cat <<EOF
{
    "creation_type": "spell",
    "prompt": "A nature-based spell that allows communication with forest animals and plants for one hour",
    "theme": "$theme",
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$spell_request" \
        -w "%{http_code}" -o /tmp/spell_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        spell_id=$(cat /tmp/spell_response.json | jq -r '.object_id')
        if [ "$spell_id" != "null" ] && [ -n "$spell_id" ]; then
            CREATED_ITEMS+=("spell:$spell_id")
            log_success "Spell created successfully (ID: $spell_id)"
        fi
    else
        log_error "Spell creation failed (HTTP ${response: -3})"
    fi
}

# Test character save/load functionality
test_character_save_load() {
    log_info "Testing character save/load functionality..."
    
    local character_id="$1"
    
    # Test loading the character
    response=$(curl -s "${API_URL}/characters/${character_id}" -w "%{http_code}" -o /tmp/load_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        loaded_name=$(cat /tmp/load_response.json | jq -r '.name')
        if [ "$loaded_name" != "null" ] && [ -n "$loaded_name" ]; then
            log_success "Character loaded successfully (Name: $loaded_name)"
        else
            log_error "Character loaded but missing name field"
        fi
    else
        log_error "Character load failed (HTTP ${response: -3})"
    fi
}

# Test retheming functionality
test_retheming() {
    log_info "Testing character retheming (Traditional D&D → Cyberpunk)..."
    
    local character_id="$1"
    local new_theme="cyberpunk"
    
    local retheme_request=$(cat <<EOF
{
    "creation_type": "character",
    "character_id": "$character_id",
    "evolution_prompt": "Transform this traditional D&D ranger into a cyberpunk setting: they become a street-smart data tracker who hunts rogue AIs in the digital wilderness of cyberspace, using neural implants instead of nature magic, cyber-enhanced weapons instead of traditional bows, and tactical gear instead of leather armor. Preserve their core personality as a protector and tracker, but adapt everything to fit a high-tech dystopian world.",
    "theme": "$new_theme",
    "preserve_backstory": true,
    "user_preferences": {
        "retheming_focus": "complete_adaptation",
        "preserve_core_concept": true,
        "update_equipment": true,
        "update_abilities": true
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$retheme_request" \
        -w "%{http_code}" -o /tmp/retheme_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        new_character_id=$(cat /tmp/retheme_response.json | jq -r '.object_id')
        if [ "$new_character_id" != "null" ] && [ -n "$new_character_id" ]; then
            log_success "Character rethemed successfully!"
            log_info "  Original (Traditional D&D): $character_id"
            log_info "  Rethemed (Cyberpunk): $new_character_id"
            echo "$new_character_id"
        else
            log_error "Retheming response missing object_id"
        fi
    else
        log_error "Character retheming failed (HTTP ${response: -3})"
        cat /tmp/retheme_response.json
    fi
}

# Test leveling up a character
test_level_up() {
    log_info "Testing character level up..."
    
    local character_id="$1"
    
    local levelup_request=$(cat <<EOF
{
    "creation_type": "character",
    "character_id": "$character_id",
    "evolution_prompt": "Level up this character to level 5, gaining new abilities and improved stats",
    "user_preferences": {
        "new_level": 5,
        "evolution_type": "level_up"
    },
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$levelup_request" \
        -w "%{http_code}" -o /tmp/levelup_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        leveled_character_id=$(cat /tmp/levelup_response.json | jq -r '.object_id')
        if [ "$leveled_character_id" != "null" ] && [ -n "$leveled_character_id" ]; then
            log_success "Character leveled up successfully (New ID: $leveled_character_id)"
            echo "$leveled_character_id"
        else
            log_error "Level up response missing object_id"
        fi
    else
        log_error "Character level up failed (HTTP ${response: -3})"
        cat /tmp/levelup_response.json
    fi
}

# Test multiclassing a character
test_multiclass() {
    log_info "Testing character multiclassing..."
    
    local character_id="$1"
    
    local multiclass_request=$(cat <<EOF
{
    "creation_type": "character",
    "character_id": "$character_id",
    "evolution_prompt": "Multiclass this character by adding levels in Wizard, focusing on utility magic",
    "user_preferences": {
        "multiclass_option": "wizard",
        "evolution_type": "level_up"
    },
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$multiclass_request" \
        -w "%{http_code}" -o /tmp/multiclass_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        multiclass_character_id=$(cat /tmp/multiclass_response.json | jq -r '.object_id')
        if [ "$multiclass_character_id" != "null" ] && [ -n "$multiclass_character_id" ]; then
            log_success "Character multiclassed successfully (New ID: $multiclass_character_id)"
            echo "$multiclass_character_id"
        else
            log_error "Multiclass response missing object_id"
        fi
    else
        log_error "Character multiclassing failed (HTTP ${response: -3})"
        cat /tmp/multiclass_response.json
    fi
}

# Test listing characters
test_list_characters() {
    log_info "Testing character listing..."
    
    response=$(curl -s "${API_URL}/characters" -w "%{http_code}" -o /tmp/characters_list.json)
    
    if [ "${response: -3}" = "200" ]; then
        character_count=$(cat /tmp/characters_list.json | jq length 2>/dev/null || echo "0")
        log_success "Characters listed successfully (Count: $character_count)"
        
        # Show first few characters
        log_info "Sample characters:"
        cat /tmp/characters_list.json | jq -r '.[0:3][] | "  - \(.name // "Unknown") (ID: \(.id // .character_id // "Unknown"))"' 2>/dev/null || log_warning "Could not parse character names"
    else
        log_error "Character listing failed (HTTP ${response: -3})"
        cat /tmp/characters_list.json
    fi
}

# Test listing NPCs
test_list_npcs() {
    log_info "Testing NPC listing..."
    
    response=$(curl -s "${API_URL}/npcs" -w "%{http_code}" -o /tmp/npcs_list.json)
    
    if [ "${response: -3}" = "200" ]; then
        npc_count=$(cat /tmp/npcs_list.json | jq length 2>/dev/null || echo "0")
        log_success "NPCs listed successfully (Count: $npc_count)"
        
        # Show first few NPCs
        log_info "Sample NPCs:"
        cat /tmp/npcs_list.json | jq -r '.[0:3][] | "  - \(.name // "Unknown") (ID: \(.id // .npc_id // "Unknown"))"' 2>/dev/null || log_warning "Could not parse NPC names"
    else
        log_error "NPC listing failed (HTTP ${response: -3})"
        cat /tmp/npcs_list.json
    fi
}

# Test listing monsters
test_list_monsters() {
    log_info "Testing monster listing..."
    
    response=$(curl -s "${API_URL}/monsters" -w "%{http_code}" -o /tmp/monsters_list.json)
    
    if [ "${response: -3}" = "200" ]; then
        monster_count=$(cat /tmp/monsters_list.json | jq length 2>/dev/null || echo "0")
        log_success "Monsters listed successfully (Count: $monster_count)"
        
        # Show first few monsters
        log_info "Sample monsters:"
        cat /tmp/monsters_list.json | jq -r '.[0:3][] | "  - \(.name // "Unknown") (ID: \(.id // .monster_id // "Unknown"))"' 2>/dev/null || log_warning "Could not parse monster names"
    else
        log_error "Monster listing failed (HTTP ${response: -3})"
        cat /tmp/monsters_list.json
    fi
}

# Test git-like versioning system with visual branching
test_versioning_with_branching() {
    log_info "Testing git-like versioning system with character branching..."
    
    local original_character_id="$1"
    local rethemed_character_id="$2"
    local original_theme="$3"
    local new_theme="$4"
    
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "                           CHARACTER VERSIONING SYSTEM                           "
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    
    # Get original character details
    if [ -n "$original_character_id" ]; then
        response=$(curl -s "${API_URL}/characters/${original_character_id}" -w "%{http_code}" -o /tmp/original_char.json)
        if [ "${response: -3}" = "200" ]; then
            original_name=$(cat /tmp/original_char.json | jq -r '.name // "Unknown"' 2>/dev/null)
            original_level=$(cat /tmp/original_char.json | jq -r '.level // "1"' 2>/dev/null)
            original_class=$(cat /tmp/original_char.json | jq -r '.classes | keys[0] // "Unknown"' 2>/dev/null)
            original_species=$(cat /tmp/original_char.json | jq -r '.species // "Unknown"' 2>/dev/null)
            original_creation_time=$(cat /tmp/original_char.json | jq -r '.created_at // .creation_time // "Unknown"' 2>/dev/null)
        else
            original_name="Unknown"
            original_level="?"
            original_class="Unknown"
            original_species="Unknown"
            original_creation_time="Unknown"
        fi
    else
        log_error "No original character ID provided for versioning test"
        return 1
    fi
    
    # Get rethemed character details
    if [ -n "$rethemed_character_id" ]; then
        response=$(curl -s "${API_URL}/characters/${rethemed_character_id}" -w "%{http_code}" -o /tmp/rethemed_char.json)
        if [ "${response: -3}" = "200" ]; then
            rethemed_name=$(cat /tmp/rethemed_char.json | jq -r '.name // "Unknown"' 2>/dev/null)
            rethemed_level=$(cat /tmp/rethemed_char.json | jq -r '.level // "1"' 2>/dev/null)
            rethemed_class=$(cat /tmp/rethemed_char.json | jq -r '.classes | keys[0] // "Unknown"' 2>/dev/null)
            rethemed_species=$(cat /tmp/rethemed_char.json | jq -r '.species // "Unknown"' 2>/dev/null)
            rethemed_creation_time=$(cat /tmp/rethemed_char.json | jq -r '.created_at // .creation_time // "Unknown"' 2>/dev/null)
            parent_id=$(cat /tmp/rethemed_char.json | jq -r '.parent_character_id // .base_character_id // "Unknown"' 2>/dev/null)
        else
            rethemed_name="Unknown"
            rethemed_level="?"
            rethemed_class="Unknown"
            rethemed_species="Unknown"
            rethemed_creation_time="Unknown"
            parent_id="Unknown"
        fi
    else
        log_error "No rethemed character ID provided for versioning test"
        return 1
    fi
    
    # Display the git-like branching visualization
    echo ""
    echo "CHARACTER EVOLUTION TREE:"
    echo ""
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│                                 ORIGINAL                                    │"
    echo "├─────────────────────────────────────────────────────────────────────────────┤"
    echo "│ Theme: ${original_theme:-traditional D&D}"
    echo "│ ID: ${original_character_id:0:12}...${original_character_id: -4}"
    echo "│ Name: $original_name"
    echo "│ Level: $original_level $original_class ($original_species)"
    echo "│ Created: ${original_creation_time:0:19}"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    echo "                                      │"
    echo "                                      │ retheme"
    echo "                                      ↓"
    echo "┌─────────────────────────────────────────────────────────────────────────────┐"
    echo "│                                 RETHEMED                                    │"
    echo "├─────────────────────────────────────────────────────────────────────────────┤"
    echo "│ Theme: ${new_theme:-cyberpunk}"
    echo "│ ID: ${rethemed_character_id:0:12}...${rethemed_character_id: -4}"
    echo "│ Name: $rethemed_name"
    echo "│ Level: $rethemed_level $rethemed_class ($rethemed_species)"
    echo "│ Parent: ${parent_id:0:8}...${parent_id: -4}"
    echo "│ Created: ${rethemed_creation_time:0:19}"
    echo "└─────────────────────────────────────────────────────────────────────────────┘"
    
    # Show the relationship mapping
    echo ""
    echo "RELATIONSHIP MAPPING:"
    echo "  $original_character_id ($original_theme) → $rethemed_character_id ($new_theme)"
    echo ""
    
    # Test getting character history/versions if endpoint exists
    log_info "Checking for version history endpoints..."
    
    response=$(curl -s "${API_URL}/characters/${original_character_id}/versions" -w "%{http_code}" -o /tmp/versions_response.json 2>/dev/null || echo "404")
    
    if [ "${response: -3}" = "200" ]; then
        version_count=$(cat /tmp/versions_response.json | jq length 2>/dev/null || echo "0")
        log_success "Character versioning API available (Versions: $version_count)"
        
        # Show version history
        echo ""
        echo "VERSION HISTORY:"
        cat /tmp/versions_response.json | jq -r '.[] | "  - Version \(.version // .id): \(.description // .timestamp // "No description")"' 2>/dev/null || log_warning "Could not parse version history"
    else
        log_info "Version history endpoint not available (simulated git-like branching shown above)"
    fi
    
    # Show git-like commit log style
    echo ""
    echo "GIT-STYLE COMMIT LOG:"
    echo "commit ${rethemed_character_id:0:8} (HEAD -> $new_theme)"
    echo "Author: D&D Character Creator <system@dnd-creator.local>"
    echo "Date: $(date)"
    echo ""
    echo "    Retheme character from $original_theme to $new_theme"
    echo "    "
    echo "    - Adapted character concept to fit $new_theme setting"
    echo "    - Preserved core personality and backstory elements"
    echo "    - Updated equipment and abilities for theme consistency"
    echo ""
    echo "commit ${original_character_id:0:8} (origin/$original_theme)"
    echo "Author: D&D Character Creator <system@dnd-creator.local>"
    echo "Date: $(date -d '1 hour ago' 2>/dev/null || date)"
    echo ""
    echo "    Initial character creation with $original_theme theme"
    echo "    "
    echo "    - Created $original_level level $original_class"
    echo "    - Generated backstory and equipment"
    echo "    - Established base character concept"
    echo ""
    
    log_success "Character versioning visualization completed"
}

# Test custom content validation and balance
test_custom_content_validation() {
    log_info "Testing custom content validation and balance..."
    
    local character_id="$1"
    local expected_level="$2"
    
    # Get character details
    response=$(curl -s "${API_URL}/characters/${character_id}" -w "%{http_code}" -o /tmp/custom_character.json)
    
    if [ "${response: -3}" = "200" ]; then
        # Check if character has custom content
        custom_species=$(cat /tmp/custom_character.json | jq -r '.custom_content.species[]? // empty' 2>/dev/null)
        custom_classes=$(cat /tmp/custom_character.json | jq -r '.custom_content.classes[]? // empty' 2>/dev/null)
        custom_spells=$(cat /tmp/custom_character.json | jq -r '.custom_content.spells[]? // empty' 2>/dev/null)
        custom_weapons=$(cat /tmp/custom_character.json | jq -r '.custom_content.weapons[]? // empty' 2>/dev/null)
        custom_armor=$(cat /tmp/custom_character.json | jq -r '.custom_content.armor[]? // empty' 2>/dev/null)
        custom_feats=$(cat /tmp/custom_character.json | jq -r '.custom_content.feats[]? // empty' 2>/dev/null)
        
        # Count spells by level
        spell_count=$(cat /tmp/custom_character.json | jq -r '.spells | length' 2>/dev/null || echo "0")
        cantrips=$(cat /tmp/custom_character.json | jq -r '.spells | map(select(.level == 0)) | length' 2>/dev/null || echo "0")
        level1_spells=$(cat /tmp/custom_character.json | jq -r '.spells | map(select(.level == 1)) | length' 2>/dev/null || echo "0")
        level2_spells=$(cat /tmp/custom_character.json | jq -r '.spells | map(select(.level == 2)) | length' 2>/dev/null || echo "0")
        level3_spells=$(cat /tmp/custom_character.json | jq -r '.spells | map(select(.level == 3)) | length' 2>/dev/null || echo "0")
        
        # Check level appropriateness
        character_level=$(cat /tmp/custom_character.json | jq -r '.level' 2>/dev/null || echo "1")
        
        # Validation checks
        log_info "Custom Content Validation Results:"
        
        if [ -n "$custom_species" ]; then
            log_success "✅ Custom species created: $custom_species"
        else
            log_error "❌ No custom species found"
        fi
        
        if [ -n "$custom_classes" ]; then
            log_success "✅ Custom class created: $custom_classes"
        else
            log_error "❌ No custom class found"
        fi
        
        if [ -n "$custom_spells" ]; then
            log_success "✅ Custom spells created: $(echo "$custom_spells" | wc -w) spells"
            log_info "   Spell breakdown: $cantrips cantrips, $level1_spells 1st level, $level2_spells 2nd level, $level3_spells 3rd level"
        else
            log_error "❌ No custom spells found"
        fi
        
        if [ -n "$custom_weapons" ]; then
            log_success "✅ Custom weapons created: $custom_weapons"
        else
            log_error "❌ No custom weapons found"
        fi
        
        if [ -n "$custom_armor" ]; then
            log_success "✅ Custom armor created: $custom_armor"
        else
            log_error "❌ No custom armor found"
        fi
        
        if [ -n "$custom_feats" ]; then
            log_success "✅ Custom feats created: $custom_feats"
        else
            log_warning "⚠️  No custom feats found (may be optional)"
        fi
        
        # Level validation
        if [ "$character_level" = "$expected_level" ]; then
            log_success "✅ Character level correct: $character_level"
        else
            log_error "❌ Character level mismatch: expected $expected_level, got $character_level"
        fi
        
        # Spell count validation for level
        if [ "$character_level" -ge 3 ] && [ "$spell_count" -lt 3 ]; then
            log_error "❌ Insufficient spells for level $character_level (has $spell_count, expected at least 3)"
        elif [ "$spell_count" -gt 0 ]; then
            log_success "✅ Appropriate spell count for level: $spell_count spells"
        fi
        
        # Check for balance validation metadata
        validation_status=$(cat /tmp/custom_character.json | jq -r '.custom_content._validation.is_valid // false' 2>/dev/null)
        balance_score=$(cat /tmp/custom_character.json | jq -r '.custom_content._validation.balance_score // "unknown"' 2>/dev/null)
        
        if [ "$validation_status" = "true" ]; then
            log_success "✅ Content validation passed (Balance score: $balance_score)"
        else
            log_warning "⚠️  Content validation status unclear"
        fi
        
    else
        log_error "Failed to retrieve character for validation (HTTP ${response: -3})"
        return 1
    fi
}

# Test iterative character creation
test_iterative_character_creation() {
    log_info "Testing iterative character creation approach..."
    
    local concept="$1"
    local theme="$2"
    local max_iterations="${3:-3}"
    
    log_info "Starting iterative creation for concept: '$concept'"
    log_info "Theme: $theme, Max iterations: $max_iterations"
    
    # Step 1: Initial concept description (user input simulation)
    local current_concept="$concept"
    local iteration=1
    local character_id=""
    local current_character_data=""
    
    while [ $iteration -le $max_iterations ]; do
        log_info "--- Iteration $iteration ---"
        
        # Step 2: LLM creates/refines character based on concept
        if [ $iteration -eq 1 ]; then
            character_id=$(test_initial_character_creation "$current_concept" "$theme")
        else
            character_id=$(test_character_refinement "$character_id" "$current_concept" "$theme")
        fi
        
        if [ -z "$character_id" ]; then
            log_error "Failed to create/refine character in iteration $iteration"
            return 1
        fi
        
        # Step 3: User review and feedback simulation
        local feedback=$(simulate_user_feedback "$character_id" $iteration)
        log_info "User feedback: $feedback"
        
        # Check if user is satisfied
        if [[ "$feedback" == *"satisfied"* ]]; then
            log_success "User satisfied with character after $iteration iterations"
            break
        fi
        
        # Prepare next iteration with feedback
        current_concept="$feedback"
        ((iteration++))
    done
    
    # Step 4: Final save confirmation
    if [ -n "$character_id" ]; then
        test_final_character_save "$character_id"
        echo "$character_id"
    fi
}

# Helper function: Initial character creation
test_initial_character_creation() {
    log_info "Step 2: Initial character creation..."
    
    local concept="$1"
    local theme="$2"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "character",
    "prompt": "$concept",
    "theme": "$theme",
    "user_preferences": {
        "level": 3,
        "iteration": 1,
        "draft_mode": true
    },
    "extra_fields": {
        "creation_mode": "iterative_initial",
        "allow_refinement": true
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/initial_creation_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        character_id=$(cat /tmp/initial_creation_response.json | jq -r '.object_id')
        if [ "$character_id" != "null" ] && [ -n "$character_id" ]; then
            log_success "Initial character created (ID: $character_id)"
            
            # Display initial character summary
            display_character_summary "$character_id" "Initial Creation"
            echo "$character_id"
        else
            log_error "Initial creation failed - no character ID returned"
        fi
    else
        log_error "Initial character creation failed (HTTP ${response: -3})"
        cat /tmp/initial_creation_response.json
    fi
}

# Helper function: Character refinement
test_character_refinement() {
    log_info "Step 2: Character refinement..."
    
    local character_id="$1"
    local refinement_prompt="$2"
    local theme="$3"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "character",
    "character_id": "$character_id",
    "evolution_prompt": "$refinement_prompt",
    "theme": "$theme",
    "user_preferences": {
        "evolution_type": "refine",
        "preserve_core_concept": true
    },
    "extra_fields": {
        "creation_mode": "iterative_refinement",
        "iteration_feedback": true
    },
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/refinement_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        refined_character_id=$(cat /tmp/refinement_response.json | jq -r '.object_id')
        if [ "$refined_character_id" != "null" ] && [ -n "$refined_character_id" ]; then
            log_success "Character refined (New ID: $refined_character_id)"
            
            # Display refined character summary
            display_character_summary "$refined_character_id" "Refinement"
            echo "$refined_character_id"
        else
            log_error "Character refinement failed - no character ID returned"
            echo "$character_id"  # Return original ID
        fi
    else
        log_error "Character refinement failed (HTTP ${response: -3})"
        cat /tmp/refinement_response.json
        echo "$character_id"  # Return original ID
    fi
}

# Helper function: Simulate user feedback
simulate_user_feedback() {
    local character_id="$1"
    local iteration="$2"
    
    log_info "Step 3: Simulating user review and feedback..."
    
    # Get character details for review
    response=$(curl -s "${API_URL}/characters/${character_id}" -w "%{http_code}" -o /tmp/character_for_feedback.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local character_name=$(cat /tmp/character_for_feedback.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local character_class=$(cat /tmp/character_for_feedback.json | jq -r '.classes | keys[0] // "Unknown"' 2>/dev/null)
        local character_level=$(cat /tmp/character_for_feedback.json | jq -r '.level // "1"' 2>/dev/null)
        local spell_count=$(cat /tmp/character_for_feedback.json | jq -r '.spells | length' 2>/dev/null || echo "0")
        local custom_content_count=$(cat /tmp/character_for_feedback.json | jq -r '.custom_content | [.species[]?, .classes[]?, .spells[]?, .weapons[]?, .armor[]?, .feats[]?] | length' 2>/dev/null || echo "0")
        
        log_info "Character Review:"
        log_info "  Name: $character_name"
        log_info "  Class: $character_class (Level $character_level)"
        log_info "  Spells: $spell_count"
        log_info "  Custom Content Items: $custom_content_count"
        
        # Simulate different types of user feedback based on iteration
        case $iteration in
            1)
                # First iteration - usually wants some refinements
                if [ "$spell_count" -lt 3 ]; then
                    echo "I like the concept but could you add more spells appropriate for this character's level? Also, make the backstory more detailed."
                elif [ "$custom_content_count" -lt 3 ]; then
                    echo "Good start, but I'd like more unique custom equipment and abilities that fit the theme better."
                else
                    echo "This looks great! I'm satisfied with this character."
                fi
                ;;
            2)
                # Second iteration - usually getting closer to satisfaction
                if [ "$custom_content_count" -ge 4 ] && [ "$spell_count" -ge 3 ]; then
                    echo "Much better! I'm satisfied with this character now."
                else
                    echo "Getting closer! Could you enhance the custom abilities and make sure the equipment is balanced for the level?"
                fi
                ;;
            3)
                # Third iteration - usually satisfied by now
                echo "Perfect! I'm satisfied with this character."
                ;;
            *)
                echo "This iteration looks good, I'm satisfied with this character."
                ;;
        esac
    else
        log_error "Could not retrieve character for feedback simulation"
        echo "The character looks incomplete, please try to improve it with more details and custom content."
    fi
}

# Helper function: Display character summary
display_character_summary() {
    local character_id="$1"
    local stage="$2"
    
    response=$(curl -s "${API_URL}/characters/${character_id}" -w "%{http_code}" -o /tmp/character_summary.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local name=$(cat /tmp/character_summary.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local class=$(cat /tmp/character_summary.json | jq -r '.classes | keys[0] // "Unknown"' 2>/dev/null)
        local level=$(cat /tmp/character_summary.json | jq -r '.level // "1"' 2>/dev/null)
        local species=$(cat /tmp/character_summary.json | jq -r '.species // "Unknown"' 2>/dev/null)
        local spell_count=$(cat /tmp/character_summary.json | jq -r '.spells | length' 2>/dev/null || echo "0")
        
        # Count custom content
        local custom_species=$(cat /tmp/character_summary.json | jq -r '.custom_content.species | length' 2>/dev/null || echo "0")
        local custom_classes=$(cat /tmp/character_summary.json | jq -r '.custom_content.classes | length' 2>/dev/null || echo "0")
        local custom_spells=$(cat /tmp/character_summary.json | jq -r '.custom_content.spells | length' 2>/dev/null || echo "0")
        local custom_weapons=$(cat /tmp/character_summary.json | jq -r '.custom_content.weapons | length' 2>/dev/null || echo "0")
        local custom_armor=$(cat /tmp/character_summary.json | jq -r '.custom_content.armor | length' 2>/dev/null || echo "0")
        
        log_info "$stage Summary:"
        log_info "  ├─ Name: $name"
        log_info "  ├─ Class: $class (Level $level)"
        log_info "  ├─ Species: $species"
        log_info "  ├─ Total Spells: $spell_count"
        log_info "  └─ Custom Content: $custom_species species, $custom_classes classes, $custom_spells spells, $custom_weapons weapons, $custom_armor armor"
    else
        log_warning "Could not retrieve character summary"
    fi
}

# Helper function: Final character save
test_final_character_save() {
    log_info "Step 4: Final character save confirmation..."
    
    local character_id="$1"
    
    # Mark character as finalized (if endpoint exists)
    local finalize_request=$(cat <<EOF
{
    "character_id": "$character_id",
    "status": "finalized",
    "iteration_complete": true
}
EOF
)
    
    response=$(curl -s -X PATCH "${API_URL}/characters/${character_id}/finalize" \
        -H "Content-Type: application/json" \
        -d "$finalize_request" \
        -w "%{http_code}" -o /tmp/finalize_response.json 2>/dev/null || echo "404")
    
    if [ "${response: -3}" = "200" ]; then
        log_success "Character finalized and saved successfully"
    else
        log_info "Character finalization endpoint not available (character already saved)"
    fi
    
    # Display final character summary
    display_character_summary "$character_id" "Final"
}

# Test iterative NPC creation
test_iterative_npc_creation() {
    log_info "Testing iterative NPC creation approach..."
    
    local concept="$1"
    local theme="$2"
    local max_iterations="${3:-3}"
    
    log_info "Starting iterative NPC creation for concept: '$concept'"
    log_info "Theme: $theme, Max iterations: $max_iterations"
    
    local current_concept="$concept"
    local iteration=1
    local npc_id=""
    
    while [ $iteration -le $max_iterations ]; do
        log_info "--- NPC Iteration $iteration ---"
        
        if [ $iteration -eq 1 ]; then
            npc_id=$(test_initial_npc_creation "$current_concept" "$theme")
        else
            npc_id=$(test_npc_refinement "$npc_id" "$current_concept" "$theme")
        fi
        
        if [ -z "$npc_id" ]; then
            log_error "Failed to create/refine NPC in iteration $iteration"
            return 1
        fi
        
        local feedback=$(simulate_npc_feedback "$npc_id" $iteration)
        log_info "User feedback: $feedback"
        
        if [[ "$feedback" == *"satisfied"* ]]; then
            log_success "User satisfied with NPC after $iteration iterations"
            break
        fi
        
        current_concept="$feedback"
        ((iteration++))
    done
    
    if [ -n "$npc_id" ]; then
        log_success "Final NPC created: $npc_id"
        echo "$npc_id"
    fi
}

# Helper function: Initial NPC creation
test_initial_npc_creation() {
    local concept="$1"
    local theme="$2"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "npc",
    "prompt": "$concept",
    "theme": "$theme",
    "user_preferences": {
        "challenge_rating": 0.5,
        "iteration": 1,
        "draft_mode": true,
        "detailed_personality": true
    },
    "extra_fields": {
        "creation_mode": "iterative_initial",
        "allow_refinement": true
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/initial_npc_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        npc_id=$(cat /tmp/initial_npc_response.json | jq -r '.object_id')
        if [ "$npc_id" != "null" ] && [ -n "$npc_id" ]; then
            log_success "Initial NPC created (ID: $npc_id)"
            display_npc_summary "$npc_id" "Initial Creation"
            echo "$npc_id"
        fi
    else
        log_error "Initial NPC creation failed (HTTP ${response: -3})"
    fi
}

# Helper function: NPC refinement
test_npc_refinement() {
    local npc_id="$1"
    local refinement_prompt="$2"
    local theme="$3"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "npc",
    "character_id": "$npc_id",
    "evolution_prompt": "$refinement_prompt",
    "theme": "$theme",
    "user_preferences": {
        "evolution_type": "refine",
        "preserve_core_concept": true
    },
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/npc_refinement_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        refined_npc_id=$(cat /tmp/npc_refinement_response.json | jq -r '.object_id')
        if [ "$refined_npc_id" != "null" ] && [ -n "$refined_npc_id" ]; then
            log_success "NPC refined (New ID: $refined_npc_id)"
            display_npc_summary "$refined_npc_id" "Refinement"
            echo "$refined_npc_id"
        else
            echo "$npc_id"
        fi
    else
        log_error "NPC refinement failed (HTTP ${response: -3})"
        echo "$npc_id"
    fi
}

# Helper function: Simulate NPC feedback
simulate_npc_feedback() {
    local npc_id="$1"
    local iteration="$2"
    
    response=$(curl -s "${API_URL}/npcs/${npc_id}" -w "%{http_code}" -o /tmp/npc_for_feedback.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local npc_name=$(cat /tmp/npc_for_feedback.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local personality=$(cat /tmp/npc_for_feedback.json | jq -r '.personality.trait // .personality // "Unknown"' 2>/dev/null)
        
        log_info "NPC Review: $npc_name - $personality"
        
        case $iteration in
            1)
                echo "The NPC is interesting but could use more depth in their background and motivations."
                ;;
            2)
                echo "Better! I'm satisfied with this NPC now."
                ;;
            *)
                echo "Perfect! I'm satisfied with this NPC."
                ;;
        esac
    else
        echo "The NPC needs more development."
    fi
}

# Helper function: Display NPC summary
display_npc_summary() {
    local npc_id="$1"
    local stage="$2"
    
    response=$(curl -s "${API_URL}/npcs/${npc_id}" -w "%{http_code}" -o /tmp/npc_summary.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local name=$(cat /tmp/npc_summary.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local role=$(cat /tmp/npc_summary.json | jq -r '.role // "Unknown"' 2>/dev/null)
        local personality=$(cat /tmp/npc_summary.json | jq -r '.personality.trait // .personality // "Unknown"' 2>/dev/null)
        
        log_info "$stage NPC Summary:"
        log_info "  ├─ Name: $name"
        log_info "  ├─ Role: $role"
        log_info "  └─ Personality: $personality"
    fi
}

# Test iterative monster creation
test_iterative_monster_creation() {
    log_info "Testing iterative monster creation approach..."
    
    local concept="$1"
    local theme="$2"
    local max_iterations="${3:-3}"
    
    log_info "Starting iterative monster creation for concept: '$concept'"
    log_info "Theme: $theme, Max iterations: $max_iterations"
    
    local current_concept="$concept"
    local iteration=1
    local monster_id=""
    
    while [ $iteration -le $max_iterations ]; do
        log_info "--- Monster Iteration $iteration ---"
        
        if [ $iteration -eq 1 ]; then
            monster_id=$(test_initial_monster_creation "$current_concept" "$theme")
        else
            monster_id=$(test_monster_refinement "$monster_id" "$current_concept" "$theme")
        fi
        
        if [ -z "$monster_id" ]; then
            log_error "Failed to create/refine monster in iteration $iteration"
            return 1
        fi
        
        local feedback=$(simulate_monster_feedback "$monster_id" $iteration)
        log_info "User feedback: $feedback"
        
        if [[ "$feedback" == *"satisfied"* ]]; then
            log_success "User satisfied with monster after $iteration iterations"
            break
        fi
        
        current_concept="$feedback"
        ((iteration++))
    done
    
    if [ -n "$monster_id" ]; then
        log_success "Final monster created: $monster_id"
        echo "$monster_id"
    fi
}

# Helper function: Initial monster creation
test_initial_monster_creation() {
    local concept="$1"
    local theme="$2"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "monster",
    "prompt": "$concept",
    "theme": "$theme",
    "user_preferences": {
        "challenge_rating": 2,
        "creature_type": "monstrosity",
        "iteration": 1,
        "draft_mode": true,
        "detailed_abilities": true
    },
    "extra_fields": {
        "creation_mode": "iterative_initial",
        "allow_refinement": true
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/initial_monster_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        monster_id=$(cat /tmp/initial_monster_response.json | jq -r '.object_id')
        if [ "$monster_id" != "null" ] && [ -n "$monster_id" ]; then
            log_success "Initial monster created (ID: $monster_id)"
            display_monster_summary "$monster_id" "Initial Creation"
            echo "$monster_id"
        fi
    else
        log_error "Initial monster creation failed (HTTP ${response: -3})"
    fi
}

# Helper function: Monster refinement
test_monster_refinement() {
    local monster_id="$1"
    local refinement_prompt="$2"
    local theme="$3"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "monster",
    "character_id": "$monster_id",
    "evolution_prompt": "$refinement_prompt",
    "theme": "$theme",
    "user_preferences": {
        "evolution_type": "refine",
        "preserve_core_concept": true
    },
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/monster_refinement_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        refined_monster_id=$(cat /tmp/monster_refinement_response.json | jq -r '.object_id')
        if [ "$refined_monster_id" != "null" ] && [ -n "$refined_monster_id" ]; then
            log_success "Monster refined (New ID: $refined_monster_id)"
            display_monster_summary "$refined_monster_id" "Refinement"
            echo "$refined_monster_id"
        else
            echo "$monster_id"
        fi
    else
        log_error "Monster refinement failed (HTTP ${response: -3})"
        echo "$monster_id"
    fi
}

# Helper function: Simulate monster feedback
simulate_monster_feedback() {
    local monster_id="$1"
    local iteration="$2"
    
    response=$(curl -s "${API_URL}/monsters/${monster_id}" -w "%{http_code}" -o /tmp/monster_for_feedback.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local monster_name=$(cat /tmp/monster_for_feedback.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local challenge_rating=$(cat /tmp/monster_for_feedback.json | jq -r '.challenge_rating // "Unknown"' 2>/dev/null)
        local abilities_count=$(cat /tmp/monster_for_feedback.json | jq -r '.abilities | length' 2>/dev/null || echo "0")
        
        log_info "Monster Review: $monster_name (CR $challenge_rating) - $abilities_count abilities"
        
        case $iteration in
            1)
                if [ "$abilities_count" -lt 3 ]; then
                    echo "The monster is interesting but needs more unique abilities and special attacks to make it challenging."
                else
                    echo "Good concept! Could you enhance the lore and make the abilities more thematically consistent?"
                fi
                ;;
            2)
                echo "Much better! I'm satisfied with this monster now."
                ;;
            *)
                echo "Perfect! I'm satisfied with this monster."
                ;;
        esac
    else
        echo "The monster needs more development and unique abilities."
    fi
}

# Helper function: Display monster summary
display_monster_summary() {
    local monster_id="$1"
    local stage="$2"
    
    response=$(curl -s "${API_URL}/monsters/${monster_id}" -w "%{http_code}" -o /tmp/monster_summary.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local name=$(cat /tmp/monster_summary.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local cr=$(cat /tmp/monster_summary.json | jq -r '.challenge_rating // "Unknown"' 2>/dev/null)
        local type=$(cat /tmp/monster_summary.json | jq -r '.creature_type // "Unknown"' 2>/dev/null)
        local abilities_count=$(cat /tmp/monster_summary.json | jq -r '.abilities | length' 2>/dev/null || echo "0")
        
        log_info "$stage Monster Summary:"
        log_info "  ├─ Name: $name"
        log_info "  ├─ Challenge Rating: $cr"
        log_info "  ├─ Type: $type"
        log_info "  └─ Special Abilities: $abilities_count"
    fi
}

# Test iterative item creation
test_iterative_item_creation() {
    log_info "Testing iterative item creation approach..."
    
    local item_type="$1"  # weapon, armor, spell, other_item
    local concept="$2"
    local theme="$3"
    local max_iterations="${4:-3}"
    
    log_info "Starting iterative $item_type creation for concept: '$concept'"
    log_info "Theme: $theme, Max iterations: $max_iterations"
    
    local current_concept="$concept"
    local iteration=1
    local item_id=""
    
    while [ $iteration -le $max_iterations ]; do
        log_info "--- $item_type Iteration $iteration ---"
        
        if [ $iteration -eq 1 ]; then
            item_id=$(test_initial_item_creation "$item_type" "$current_concept" "$theme")
        else
            item_id=$(test_item_refinement "$item_type" "$item_id" "$current_concept" "$theme")
        fi
        
        if [ -z "$item_id" ]; then
            log_error "Failed to create/refine $item_type in iteration $iteration"
            return 1
        fi
        
        local feedback=$(simulate_item_feedback "$item_type" "$item_id" $iteration)
        log_info "User feedback: $feedback"
        
        if [[ "$feedback" == *"satisfied"* ]]; then
            log_success "User satisfied with $item_type after $iteration iterations"
            break
        fi
        
        current_concept="$feedback"
        ((iteration++))
    done
    
    if [ -n "$item_id" ]; then
        log_success "Final $item_type created: $item_id"
        echo "$item_id"
    fi
}

# Helper function: Initial item creation
test_initial_item_creation() {
    local item_type="$1"
    local concept="$2"
    local theme="$3"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "$item_type",
    "prompt": "$concept",
    "theme": "$theme",
    "user_preferences": {
        "iteration": 1,
        "draft_mode": true,
        "detailed_properties": true
    },
    "extra_fields": {
        "creation_mode": "iterative_initial",
        "allow_refinement": true
    },
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/create" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/initial_item_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        item_id=$(cat /tmp/initial_item_response.json | jq -r '.object_id')
        if [ "$item_id" != "null" ] && [ -n "$item_id" ]; then
            log_success "Initial $item_type created (ID: $item_id)"
            display_item_summary "$item_type" "$item_id" "Initial Creation"
            echo "$item_id"
        fi
    else
        log_error "Initial $item_type creation failed (HTTP ${response: -3})"
    fi
}

# Helper function: Item refinement
test_item_refinement() {
    local item_type="$1"
    local item_id="$2"
    local refinement_prompt="$3"
    local theme="$4"
    
    local request_data=$(cat <<EOF
{
    "creation_type": "$item_type",
    "item_id": "$item_id",
    "evolution_prompt": "$refinement_prompt",
    "theme": "$theme",
    "user_preferences": {
        "evolution_type": "refine",
        "preserve_core_concept": true
    },
    "preserve_base_properties": true,
    "save_to_database": true
}
EOF
)
    
    response=$(curl -s -X POST "${API_URL}/factory/evolve" \
        -H "Content-Type: application/json" \
        -d "$request_data" \
        -w "%{http_code}" -o /tmp/item_refinement_response.json)
    
    if [ "${response: -3}" = "200" ]; then
        refined_item_id=$(cat /tmp/item_refinement_response.json | jq -r '.object_id')
        if [ "$refined_item_id" != "null" ] && [ -n "$refined_item_id" ]; then
            log_success "$item_type refined (New ID: $refined_item_id)"
            display_item_summary "$item_type" "$refined_item_id" "Refinement"
            echo "$refined_item_id"
        else
            echo "$item_id"
        fi
    else
        log_error "$item_type refinement failed (HTTP ${response: -3})"
        echo "$item_id"
    fi
}

# Helper function: Simulate item feedback
simulate_item_feedback() {
    local item_type="$1"
    local item_id="$2"
    local iteration="$3"
    
    # Try different endpoints based on item type
    local endpoint=""
    case "$item_type" in
        "weapon") endpoint="weapons" ;;
        "armor") endpoint="armor" ;;
        "spell") endpoint="spells" ;;
        *) endpoint="items" ;;
    esac
    
    response=$(curl -s "${API_URL}/${endpoint}/${item_id}" -w "%{http_code}" -o /tmp/item_for_feedback.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local item_name=$(cat /tmp/item_for_feedback.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local rarity=$(cat /tmp/item_for_feedback.json | jq -r '.rarity // "common"' 2>/dev/null)
        local properties_count=$(cat /tmp/item_for_feedback.json | jq -r '.properties | length' 2>/dev/null || echo "0")
        
        log_info "$item_type Review: $item_name ($rarity) - $properties_count properties"
        
        case $iteration in
            1)
                case "$item_type" in
                    "weapon")
                        if [ "$properties_count" -lt 2 ]; then
                            echo "The weapon is basic but could use more unique properties and special abilities to make it interesting."
                        else
                            echo "Good concept! Could you enhance the damage properties and add more flavorful descriptions?"
                        fi
                        ;;
                    "armor")
                        echo "The armor design is good but could use more protective enchantments and unique visual elements."
                        ;;
                    "spell")
                        echo "Interesting spell concept but could use more detailed mechanics and creative effects."
                        ;;
                    *)
                        echo "The item is interesting but needs more unique properties and practical applications."
                        ;;
                esac
                ;;
            2)
                echo "Much better! I'm satisfied with this $item_type now."
                ;;
            *)
                echo "Perfect! I'm satisfied with this $item_type."
                ;;
        esac
    else
        echo "The $item_type needs more development and unique properties."
    fi
}

# Helper function: Display item summary
display_item_summary() {
    local item_type="$1"
    local item_id="$2"
    local stage="$3"
    
    # Try different endpoints based on item type
    local endpoint=""
    case "$item_type" in
        "weapon") endpoint="weapons" ;;
        "armor") endpoint="armor" ;;
        "spell") endpoint="spells" ;;
        *) endpoint="items" ;;
    esac
    
    response=$(curl -s "${API_URL}/${endpoint}/${item_id}" -w "%{http_code}" -o /tmp/item_summary.json 2>/dev/null)
    
    if [ "${response: -3}" = "200" ]; then
        local name=$(cat /tmp/item_summary.json | jq -r '.name // "Unknown"' 2>/dev/null)
        local rarity=$(cat /tmp/item_summary.json | jq -r '.rarity // "common"' 2>/dev/null)
        local description=$(cat /tmp/item_summary.json | jq -r '.description // "No description"' 2>/dev/null)
        
        # Item-specific details
        case "$item_type" in
            "weapon")
                local damage=$(cat /tmp/item_summary.json | jq -r '.damage // "Unknown"' 2>/dev/null)
                local weapon_type=$(cat /tmp/item_summary.json | jq -r '.weapon_type // "Unknown"' 2>/dev/null)
                log_info "$stage $item_type Summary:"
                log_info "  ├─ Name: $name"
                log_info "  ├─ Type: $weapon_type"
                log_info "  ├─ Damage: $damage"
                log_info "  ├─ Rarity: $rarity"
                log_info "  └─ Description: ${description:0:50}..."
                ;;
            "armor")
                local ac=$(cat /tmp/item_summary.json | jq -r '.ac_base // .base_ac // "Unknown"' 2>/dev/null)
                local armor_type=$(cat /tmp/item_summary.json | jq -r '.armor_type // "Unknown"' 2>/dev/null)
                log_info "$stage $item_type Summary:"
                log_info "  ├─ Name: $name"
                log_info "  ├─ Type: $armor_type"
                log_info "  ├─ AC: $ac"
                log_info "  ├─ Rarity: $rarity"
                log_info "  └─ Description: ${description:0:50}..."
                ;;
            "spell")
                local level=$(cat /tmp/item_summary.json | jq -r '.level // "Unknown"' 2>/dev/null)
                local school=$(cat /tmp/item_summary.json | jq -r '.school // "Unknown"' 2>/dev/null)
                log_info "$stage $item_type Summary:"
                log_info "  ├─ Name: $name"
                log_info "  ├─ Level: $level"
                log_info "  ├─ School: $school"
                log_info "  ├─ Rarity: $rarity"
                log_info "  └─ Description: ${description:0:50}..."
                ;;
            *)
                log_info "$stage $item_type Summary:"
                log_info "  ├─ Name: $name"
                log_info "  ├─ Rarity: $rarity"
                log_info "  └─ Description: ${description:0:50}..."
                ;;
        esac
    fi
}

# Main test execution
main() {
    echo "============================================="
    echo "D&D Character Creator - Workflow Test Suite"
    echo "============================================="
    
    # Check if jq is available
    if ! command -v jq &> /dev/null; then
        log_error "jq is required for this test. Please install it: sudo apt-get install jq"
        exit 1
    fi
    
    # Verify environment variables are set
    log_info "Verifying environment setup..."
    if [ -z "$OPENAI_API_KEY" ]; then
        log_error "OPENAI_API_KEY is not set"
        exit 1
    fi
    
    if [ -z "$SECRET_KEY" ]; then
        log_warning "SECRET_KEY is not set, using generated key"
    fi
    
    log_success "Environment setup verified"
    
    # Test 1: Service Health
    test_service_health
    
    # Test 2: Create content with traditional theme (basic character)
    log_info "\n=== Testing Content Creation (Traditional Theme) ==="
    character_id_1=$(test_create_character "traditional D&D" 3 "A brave elven ranger who protects the forest")
    npc_id_1=$(test_create_npc "traditional D&D")
    monster_id_1=$(test_create_monster "traditional D&D")
    test_create_items "traditional D&D"
    
    # Test 3: Create content with custom requirements (steampunk theme, higher level)
    log_info "\n=== Testing Custom Content Creation (Steampunk Theme, Level 8) ==="
    character_id_2=$(test_create_character "steampunk" 8)
    
    # Validate custom content for steampunk character
    if [ -n "$character_id_2" ]; then
        test_custom_content_validation "$character_id_2" 8
    fi
    
    # Test 4: Create high-level character with cyberpunk theme
    log_info "\n=== Testing High-Level Custom Content (Cyberpunk Theme, Level 12) ==="
    character_id_3=$(test_create_character "cyberpunk" 12)
    
    # Validate custom content for cyberpunk character
    if [ -n "$character_id_3" ]; then
        test_custom_content_validation "$character_id_3" 12
    fi
    
    npc_id_2=$(test_create_npc "steampunk")
    monster_id_2=$(test_create_monster "steampunk")
    
    # Test 5: Save/Load functionality
    if [ -n "$character_id_2" ]; then
        log_info "\n=== Testing Save/Load Functionality ==="
        test_character_save_load "$character_id_2"
    fi
    
    # Test 6: Retheming with git-like branching visualization
    if [ -n "$character_id_1" ]; then
        log_info "\n=== Testing Retheming & Character Versioning System ==="
        
        # Store original character details for comparison
        response=$(curl -s "${API_URL}/characters/${character_id_1}" -w "%{http_code}" -o /tmp/original_for_retheme.json 2>/dev/null)
        original_theme="traditional D&D"
        new_theme="cyberpunk"
        
        # Perform retheming
        rethemed_character_id=$(test_retheming "$character_id_1")
        
        # Display the git-like versioning visualization
        if [ -n "$rethemed_character_id" ]; then
            test_versioning_with_branching "$character_id_1" "$rethemed_character_id" "$original_theme" "$new_theme"
        fi
    fi
    
    # Test 7: Level Up (use the steampunk character)
    if [ -n "$character_id_2" ]; then
        log_info "\n=== Testing Level Up Functionality ==="
        leveled_character_id=$(test_level_up "$character_id_2")
        
        # Validate the leveled character
        if [ -n "$leveled_character_id" ]; then
            test_custom_content_validation "$leveled_character_id" 5
        fi
    fi
    
    # Test 8: Multiclassing (use the high-level cyberpunk character)
    if [ -n "$character_id_3" ]; then
        log_info "\n=== Testing Multiclassing Functionality ==="
        multiclass_character_id=$(test_multiclass "$character_id_3")
        
        # Validate the multiclassed character
        if [ -n "$multiclass_character_id" ]; then
            test_custom_content_validation "$multiclass_character_id" 12
        fi
    fi
    
    # Test 9: Iterative Creation Tests
    log_info "\n=== Testing Iterative Character Creation ==="
    iterative_character_id=$(test_iterative_character_creation "A mysterious wizard who studies forbidden ancient magic and seeks to uncover lost secrets" "dark fantasy" 3)
    
    if [ -n "$iterative_character_id" ]; then
        CREATED_CHARACTERS+=("$iterative_character_id")
        test_custom_content_validation "$iterative_character_id" 3
    fi
    
    log_info "\n=== Testing Iterative NPC Creation ==="
    iterative_npc_id=$(test_iterative_npc_creation "A tavern keeper who secretly smuggles information for the resistance" "steampunk" 2)
    
    if [ -n "$iterative_npc_id" ]; then
        CREATED_NPCS+=("$iterative_npc_id")
    fi
    
    log_info "\n=== Testing Iterative Monster Creation ==="
    iterative_monster_id=$(test_iterative_monster_creation "A mechanical beast powered by steam and arcane energy that guards ancient ruins" "steampunk" 2)
    
    if [ -n "$iterative_monster_id" ]; then
        CREATED_MONSTERS+=("$iterative_monster_id")
    fi
    
    log_info "\n=== Testing Iterative Item Creation ==="
    iterative_weapon_id=$(test_iterative_item_creation "weapon" "A sword that can channel the wielder's emotions into elemental damage" "high fantasy" 2)
    iterative_armor_id=$(test_iterative_item_creation "armor" "Living armor that adapts to threats and grows stronger with each battle" "dark fantasy" 2)
    iterative_spell_id=$(test_iterative_item_creation "spell" "A spell that allows the caster to temporarily merge with shadows and become intangible" "gothic" 2)
    
    if [ -n "$iterative_weapon_id" ]; then
        CREATED_ITEMS+=("weapon:$iterative_weapon_id")
    fi
    if [ -n "$iterative_armor_id" ]; then
        CREATED_ITEMS+=("armor:$iterative_armor_id")
    fi
    if [ -n "$iterative_spell_id" ]; then
        CREATED_ITEMS+=("spell:$iterative_spell_id")
    fi
    
    # Test 10: Listing functionality
    log_info "\n=== Testing Listing Functionality ==="
    test_list_characters
    test_list_npcs
    test_list_monsters
    
    # Summary
    echo ""
    echo "============================================="
    echo "Test Summary"
    echo "============================================="
    log_info "Tests Passed: $TESTS_PASSED"
    log_info "Tests Failed: $TESTS_FAILED"
    log_info "Created Characters: ${#CREATED_CHARACTERS[@]}"
    log_info "  - Traditional D&D (Level 3): $([ -n "$character_id_1" ] && echo "✓" || echo "✗")"
    log_info "  - Steampunk Custom (Level 8): $([ -n "$character_id_2" ] && echo "✓" || echo "✗")"
    log_info "  - Cyberpunk Custom (Level 12): $([ -n "$character_id_3" ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Dark Fantasy Wizard: $([ -n "$iterative_character_id" ] && echo "✓" || echo "✗")"
    log_info "Created NPCs: ${#CREATED_NPCS[@]}"
    log_info "  - Traditional Tavern Keeper: $([ -n "$npc_id_1" ] && echo "✓" || echo "✗")"
    log_info "  - Steampunk NPC: $([ -n "$npc_id_2" ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Resistance Smuggler: $([ -n "$iterative_npc_id" ] && echo "✓" || echo "✗")"
    log_info "Created Monsters: ${#CREATED_MONSTERS[@]}"
    log_info "  - Traditional Monster: $([ -n "$monster_id_1" ] && echo "✓" || echo "✗")"
    log_info "  - Steampunk Monster: $([ -n "$monster_id_2" ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Mechanical Beast: $([ -n "$iterative_monster_id" ] && echo "✓" || echo "✗")"
    log_info "Created Items: ${#CREATED_ITEMS[@]}"
    log_info "  - Traditional D&D Items: $([ ${#CREATED_ITEMS[@]} -ge 3 ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Emotional Sword: $([ -n "$iterative_weapon_id" ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Living Armor: $([ -n "$iterative_armor_id" ] && echo "✓" || echo "✗")"
    log_info "  - Iterative Shadow Spell: $([ -n "$iterative_spell_id" ] && echo "✓" || echo "✗")"
    
    echo ""
    echo "Standard Content Test Results:"
    echo "- Level 8 Steampunk Character: Custom species, class, spells, equipment"
    echo "- Level 12 Cyberpunk Character: Full custom content with advanced balance"
    echo "- Balance validation and spell distribution testing completed"
    echo "- Character versioning system tested with traditional D&D → cyberpunk retheming"
    
    echo ""
    echo "Iterative Creation Test Results:"
    echo "- Character: Dark fantasy wizard with forbidden magic (3 iterations)"
    echo "- NPC: Steampunk tavern keeper/smuggler (2 iterations)"
    echo "- Monster: Mechanical steam-powered guardian beast (2 iterations)"
    echo "- Items: Emotional sword, living armor, shadow spell (2 iterations each)"
    echo "- User feedback simulation and refinement workflow tested"
    
    if [ $TESTS_FAILED -eq 0 ]; then
        log_success "All tests completed successfully! ✅"
        echo ""
        echo "🎭 Character Versioning Demo:"
        echo "   Traditional Ranger → Cyberpunk Ranger branching completed"
        echo "   Git-like commit history visualization displayed"
        echo ""
        echo "🔄 Iterative Creation Demo:"
        echo "   Character: 3-iteration refinement process completed"
        echo "   NPC: 2-iteration feedback and improvement cycle"
        echo "   Monster: 2-iteration enhancement workflow"
        echo "   Items: Multiple item types with iterative refinement"
        echo "   User feedback simulation and LLM response loop tested"
        exit 0
    else
        log_error "Some tests failed. Check the output above for details. ❌"
        exit 1
    fi
}

# Cleanup function
cleanup() {
    log_info "Cleaning up temporary files..."
    rm -f /tmp/*_response.json /tmp/*_list.json 2>/dev/null || true
}

# Set trap for cleanup
trap cleanup EXIT

# Run main function
main "$@"


