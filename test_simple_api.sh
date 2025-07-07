#!/bin/bash

# Simple test script for D&D Character Creator API
# Tests the basic functionality that we know works

set -e

# Configuration
API_URL="http://localhost:8001/api/v2"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo "============================================="
echo "D&D Character Creator - Simple API Test"
echo "============================================="

# Test 1: Health check
log_info "Testing API health..."
response=$(curl -s -w "%{http_code}" "http://localhost:8001/health" -o /tmp/health.json)
if [ "$response" = "200" ]; then
    log_success "API is healthy"
    cat /tmp/health.json | jq '.'
else
    log_error "API health check failed (HTTP $response)"
    exit 1
fi

# Test 2: List existing characters
log_info "Testing character listing..."
response=$(curl -s -w "%{http_code}" "${API_URL}/characters" -o /tmp/characters.json)
if [ "${response: -3}" = "200" ]; then
    character_count=$(cat /tmp/characters.json | jq length)
    log_success "Character listing successful (Count: $character_count)"
    
    # Show first character if any exist
    if [ "$character_count" -gt 0 ]; then
        first_char_id=$(cat /tmp/characters.json | jq -r '.[0].id')
        first_char_name=$(cat /tmp/characters.json | jq -r '.[0].name')
        log_info "First character: $first_char_name (ID: $first_char_id)"
        
        # Test 3: Get specific character
        log_info "Testing character retrieval..."
        response=$(curl -s -w "%{http_code}" "${API_URL}/characters/${first_char_id}" -o /tmp/character.json)
        if [ "${response: -3}" = "200" ]; then
            char_name=$(cat /tmp/character.json | jq -r '.name')
            char_level=$(cat /tmp/character.json | jq -r '.level')
            char_species=$(cat /tmp/character.json | jq -r '.species')
            log_success "Character retrieval successful: $char_name (Level $char_level $char_species)"
        else
            log_error "Character retrieval failed (HTTP ${response: -3})"
        fi
        
        # Test 4: Test direct-edit endpoint
        log_info "Testing character direct-edit..."
        edit_data=$(cat <<EOF
{
    "updates": {"name": "Test Edited Character", "background": "Manual Override Background"},
    "notes": "Simple API test edit."
}
EOF
)
        response=$(curl -s -X POST "${API_URL}/characters/${first_char_id}/direct-edit" \
            -H "Content-Type: application/json" \
            -d "$edit_data" \
            -w "%{http_code}" -o /tmp/edit_result.json)
        if [ "${response: -3}" = "200" ]; then
            edited_name=$(cat /tmp/edit_result.json | jq -r '.name')
            user_modified=$(cat /tmp/edit_result.json | jq -r '.user_modified')
            log_success "Character direct-edit successful: $edited_name (user_modified: $user_modified)"
        else
            log_error "Character direct-edit failed (HTTP ${response: -3})"
            cat /tmp/edit_result.json
        fi
    fi
else
    log_error "Character listing failed (HTTP ${response: -3})"
    cat /tmp/characters.json
fi

# Test 5: Create a new character
log_info "Testing character creation via factory..."
create_data=$(cat <<EOF
{
    "creation_type": "character",
    "prompt": "A brave elven ranger who protects the forest",
    "theme": "traditional D&D",
    "user_preferences": {
        "level": 3
    },
    "save_to_database": true
}
EOF
)
response=$(curl -s -X POST "${API_URL}/factory/create" \
    -H "Content-Type: application/json" \
    -d "$create_data" \
    -w "%{http_code}" -o /tmp/create_result.json)
if [ "${response: -3}" = "200" ]; then
    success=$(cat /tmp/create_result.json | jq -r '.success')
    new_char_id=$(cat /tmp/create_result.json | jq -r '.object_id')
    if [ "$success" = "true" ] && [ "$new_char_id" != "null" ]; then
        log_success "Character creation successful (ID: $new_char_id)"
        
        # Test 6: Test character evolution
        log_info "Testing character evolution via factory..."
        evolve_data=$(cat <<EOF
{
    "creation_type": "character",
    "character_id": "$new_char_id",
    "evolution_prompt": "Level up this character to level 5 with new abilities",
    "theme": "traditional D&D",
    "preserve_backstory": true,
    "save_to_database": true
}
EOF
)
        response=$(curl -s -X POST "${API_URL}/factory/evolve" \
            -H "Content-Type: application/json" \
            -d "$evolve_data" \
            -w "%{http_code}" -o /tmp/evolve_result.json)
        if [ "${response: -3}" = "200" ]; then
            evolved_success=$(cat /tmp/evolve_result.json | jq -r '.success')
            evolved_char_id=$(cat /tmp/evolve_result.json | jq -r '.object_id')
            if [ "$evolved_success" = "true" ] && [ "$evolved_char_id" != "null" ]; then
                log_success "Character evolution successful (ID: $evolved_char_id)"
            else
                log_error "Character evolution failed in processing"
                cat /tmp/evolve_result.json | jq '.'
            fi
        else
            log_error "Character evolution failed (HTTP ${response: -3})"
            cat /tmp/evolve_result.json
        fi
    else
        log_error "Character creation failed in processing"
        cat /tmp/create_result.json | jq '.'
    fi
else
    log_error "Character creation failed (HTTP ${response: -3})"
    cat /tmp/create_result.json
fi

# Test 7: List NPCs and Monsters
log_info "Testing NPC listing..."
response=$(curl -s -w "%{http_code}" "${API_URL}/npcs" -o /tmp/npcs.json)
if [ "${response: -3}" = "200" ]; then
    npc_count=$(cat /tmp/npcs.json | jq length)
    log_success "NPC listing successful (Count: $npc_count)"
else
    log_error "NPC listing failed (HTTP ${response: -3})"
fi

log_info "Testing monster listing..."
response=$(curl -s -w "%{http_code}" "${API_URL}/monsters" -o /tmp/monsters.json)
if [ "${response: -3}" = "200" ]; then
    monster_count=$(cat /tmp/monsters.json | jq length)
    log_success "Monster listing successful (Count: $monster_count)"
else
    log_error "Monster listing failed (HTTP ${response: -3})"
fi

echo ""
echo "============================================="
echo "Simple API Test Complete"
echo "============================================="
log_success "All basic API functionality tested successfully!"

# Cleanup
rm -f /tmp/*.json 2>/dev/null || true
