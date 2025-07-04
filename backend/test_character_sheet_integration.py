#!/usr/bin/env python3
"""
Test script for Task 2B: Character Sheet Integration
Verifies that character sheet endpoints now display allocated spells/items via UUID.
"""

import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class CharacterSheetIntegrationTest:
    
    def __init__(self):
        self.session = requests.Session()
    
    def test_character_sheet_integration(self):
        """Test the character sheet integration with unified catalog."""
        
        print("\n" + "="*60)
        print("CHARACTER SHEET INTEGRATION TEST")
        print("="*60)
        
        try:
            # Step 1: Create a test character
            print("\n1. Creating a test character...")
            character_data = {
                "name": "Elara the Wizard",
                "species": "Human",
                "background": "Scholar",
                "character_classes": {"Wizard": 3},
                "strength": 10,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 16,
                "wisdom": 12,
                "charisma": 8
            }
            
            response = self.session.post(f"{BASE_URL}/api/v2/characters", json=character_data)
            if response.status_code != 200:
                print(f"❌ Failed to create character: {response.text}")
                return False
            
            character_id = response.json()["id"]
            print(f"✅ Created character: {character_id}")
            
            # Step 2: Allocate some spells to the character
            print("\n2. Allocating spells to character...")
            
            # First, search for some spells
            spell_response = self.session.get(f"{BASE_URL}/api/v2/catalog/search", params={
                "item_type": "spell",
                "spell_level": 0,
                "limit": 3
            })
            
            if spell_response.status_code != 200:
                print(f"❌ Failed to search spells: {spell_response.text}")
                return False
            
            spells = spell_response.json()["data"]["items"]
            print(f"✅ Found {len(spells)} cantrips")
            
            # Allocate the first 2 spells as "spells_known"
            for i, spell in enumerate(spells[:2]):
                alloc_response = self.session.post(f"{BASE_URL}/api/v2/catalog/access", json={
                    "character_id": character_id,
                    "item_id": spell["id"],
                    "access_type": "spells_known",
                    "acquired_method": f"Starting spell {i+1}"
                })
                
                if alloc_response.status_code != 200:
                    print(f"❌ Failed to allocate spell {spell['name']}: {alloc_response.text}")
                    return False
                
                print(f"✅ Allocated spell: {spell['name']}")
            
            # Step 3: Allocate some equipment
            print("\n3. Allocating equipment to character...")
            
            # Search for weapons
            weapon_response = self.session.get(f"{BASE_URL}/api/v2/catalog/search", params={
                "item_type": "weapon",
                "limit": 2
            })
            
            if weapon_response.status_code != 200:
                print(f"❌ Failed to search weapons: {weapon_response.text}")
                return False
            
            weapons = weapon_response.json()["data"]["items"]
            print(f"✅ Found {len(weapons)} weapons")
            
            # Allocate first weapon to inventory
            if weapons:
                weapon = weapons[0]
                alloc_response = self.session.post(f"{BASE_URL}/api/v2/catalog/access", json={
                    "character_id": character_id,
                    "item_id": weapon["id"],
                    "access_type": "inventory",
                    "acquired_method": "Starting equipment"
                })
                
                if alloc_response.status_code != 200:
                    print(f"❌ Failed to allocate weapon {weapon['name']}: {alloc_response.text}")
                    return False
                
                print(f"✅ Allocated weapon: {weapon['name']}")
            
            # Step 4: Get character sheet and verify allocated items are included
            print("\n4. Testing character sheet retrieval...")
            
            sheet_response = self.session.get(f"{BASE_URL}/api/v2/characters/{character_id}/sheet")
            
            if sheet_response.status_code != 200:
                print(f"❌ Failed to get character sheet: {sheet_response.text}")
                return False
            
            sheet_data = sheet_response.json()
            print(f"✅ Retrieved character sheet successfully")
            
            # Step 5: Verify the allocated items are present
            print("\n5. Verifying allocated items in character sheet...")
            
            # Check if state section exists
            if "state" not in sheet_data:
                print("❌ 'state' section missing from character sheet")
                return False
            
            state = sheet_data["state"]
            
            # Check for allocated spells
            if "allocated_spells" in state:
                allocated_spells = state["allocated_spells"]
                spells_known = allocated_spells.get("spells_known", [])
                print(f"✅ Found {len(spells_known)} allocated spells in spells_known")
                
                # Print details of allocated spells
                for spell_alloc in spells_known:
                    spell_details = spell_alloc.get("item_details", {})
                    print(f"   - {spell_details.get('name', 'Unknown')} (Level {spell_details.get('spell_level', '?')})")
            else:
                print("❌ allocated_spells not found in character sheet state")
                return False
            
            # Check for allocated equipment
            if "allocated_equipment" in state:
                allocated_equipment = state["allocated_equipment"]
                inventory = allocated_equipment.get("inventory", [])
                print(f"✅ Found {len(inventory)} allocated items in inventory")
                
                # Print details of allocated equipment
                for item_alloc in inventory:
                    item_details = item_alloc.get("item_details", {})
                    print(f"   - {item_details.get('name', 'Unknown')} ({item_details.get('item_type', '?')})")
            else:
                print("❌ allocated_equipment not found in character sheet state")
                return False
            
            # Check for all allocated items
            if "all_allocated_items" in state:
                all_items = state["all_allocated_items"]
                print(f"✅ Found {len(all_items)} total allocated items")
            else:
                print("❌ all_allocated_items not found in character sheet state")
                return False
            
            # Step 6: Verify backward compatibility - old equipment fields still exist
            print("\n6. Verifying backward compatibility...")
            
            if "equipment" in state:
                old_equipment = state["equipment"]
                print("✅ Old equipment fields still present for backward compatibility")
                print(f"   - armor: {old_equipment.get('armor')}")
                print(f"   - weapons: {len(old_equipment.get('weapons', []))} items")
                print(f"   - items: {len(old_equipment.get('items', []))} items")
            else:
                print("❌ Old equipment fields missing - backward compatibility broken")
                return False
            
            print("\n" + "="*60)
            print("✅ CHARACTER SHEET INTEGRATION TEST PASSED!")
            print("✅ Character sheets now include UUID-based allocated items")
            print("✅ Both traditional and unified catalog data are available")
            print("✅ Backward compatibility maintained")
            print("="*60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def print_json_section(self, data: Dict[str, Any], section_name: str, max_depth: int = 2):
        """Helper to print a section of JSON data with limited depth."""
        if section_name in data:
            print(f"\n{section_name.upper()}:")
            section_data = data[section_name]
            print(json.dumps(section_data, indent=2, default=str)[:1000] + "..." if len(json.dumps(section_data, default=str)) > 1000 else json.dumps(section_data, indent=2, default=str))


if __name__ == "__main__":
    test = CharacterSheetIntegrationTest()
    success = test.test_character_sheet_integration()
    
    if not success:
        exit(1)
    
    print("\n🎉 All tests completed successfully!")
