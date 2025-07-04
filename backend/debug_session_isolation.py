#!/usr/bin/env python3
"""
Debug script to test the session isolation issue directly.
"""

import sys
import os
sys.path.append('.')

import requests
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

def test_character_creation_and_retrieval():
    """Test if character creation and immediate retrieval work."""
    
    print("\n" + "="*70)
    print("DEBUG: CHARACTER CREATION AND RETRIEVAL TEST")
    print("="*70)
    
    session = requests.Session()
    
    # Create a character
    wizard_data = {
        "name": "Debug Wizard",
        "species": "Human",
        "background": "Scholar",
        "character_classes": {"Wizard": 5},
        "strength": 10,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 16,
        "wisdom": 12,
        "charisma": 8
    }
    
    print("1. Creating character...")
    create_response = session.post(f"{BASE_URL}/api/v2/characters", json=wizard_data)
    if create_response.status_code != 200:
        print(f"❌ Failed to create character: {create_response.text}")
        return False
    
    character_id = create_response.json()["id"]
    print(f"✅ Created character: {character_id}")
    
    # Immediately try to retrieve the character through different endpoints
    print("\n2. Testing retrieval through different endpoints...")
    
    # Test 1: Get character directly
    print("   2a. Getting character directly...")
    get_response = session.get(f"{BASE_URL}/api/v2/characters/{character_id}")
    if get_response.status_code == 200:
        print(f"   ✅ Direct character retrieval successful")
    else:
        print(f"   ❌ Direct character retrieval failed: {get_response.text}")
    
    # Test 2: List all characters
    print("   2b. Listing all characters...")
    list_response = session.get(f"{BASE_URL}/api/v2/characters")
    if list_response.status_code == 200:
        characters = list_response.json()
        character_ids = [char["id"] for char in characters]
        if character_id in character_ids:
            print(f"   ✅ Character found in list (total: {len(characters)})")
        else:
            print(f"   ❌ Character NOT found in list (total: {len(characters)})")
            print(f"   Available IDs: {character_ids}")
    else:
        print(f"   ❌ Character list failed: {list_response.text}")
    
    # Test 3: Try allocation service character lookup
    print("   2c. Testing allocation service character lookup...")
    try:
        # Try to get character items (this uses AllocationService internally)
        items_response = session.get(f"{BASE_URL}/api/v2/catalog/character/{character_id}/items")
        if items_response.status_code == 200:
            print(f"   ✅ AllocationService character lookup successful")
        elif items_response.status_code == 400 and "Character not found" in items_response.text:
            print(f"   ❌ AllocationService character lookup failed: {items_response.text}")
        else:
            print(f"   ⚠️  AllocationService returned unexpected response: {items_response.status_code} - {items_response.text}")
    except Exception as e:
        print(f"   ❌ AllocationService test failed with exception: {e}")
    
    print("\n3. Summary:")
    print(f"   Character ID: {character_id}")
    return True

if __name__ == "__main__":
    test_character_creation_and_retrieval()
