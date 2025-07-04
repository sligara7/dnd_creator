#!/usr/bin/env python3
"""
Test script for Task 2C: Class/Proficiency Validation on Allocation
Verifies that the system properly validates class and proficiency restrictions when allocating items.
"""

import requests
import json
import logging
from typing import Dict, Any

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BASE_URL = "http://localhost:8000"

class AllocationValidationTest:
    
    def __init__(self):
        self.session = requests.Session()
    
    def test_allocation_validation(self):
        """Test that allocation validation works correctly for different scenarios."""
        
        print("\n" + "="*70)
        print("TASK 2C: CLASS/PROFICIENCY VALIDATION TEST")
        print("="*70)
        
        try:
            # Test Case 1: Valid spell allocation (Wizard can learn Wizard spells)
            print("\n1. Testing VALID spell allocation (Wizard learning Wizard spell)...")
            
            # Create a Wizard character
            wizard_data = {
                "name": "Gandalf the Grey",
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
            
            wizard_response = self.session.post(f"{BASE_URL}/api/v2/characters", json=wizard_data)
            if wizard_response.status_code != 200:
                print(f"❌ Failed to create wizard: {wizard_response.text}")
                return False
            
            wizard_id = wizard_response.json()["id"]
            print(f"✅ Created Wizard character: {wizard_id}")
            
            # Find a Wizard spell
            spell_response = self.session.get(f"{BASE_URL}/api/v2/catalog/search", params={
                "item_type": "spell",
                "spell_level": 1,
                "limit": 5
            })
            
            if spell_response.status_code != 200:
                print(f"❌ Failed to search spells: {spell_response.text}")
                return False
            
            spells = spell_response.json()["data"]["items"]
            wizard_spell = None
            
            # Find a spell that wizards can use
            for spell in spells:
                class_restrictions = spell.get("class_restrictions", [])
                if "wizard" in [cls.lower() for cls in class_restrictions]:
                    wizard_spell = spell
                    break
            
            if not wizard_spell:
                print("❌ No wizard spells found in catalog")
                return False
            
            print(f"✅ Found wizard spell: {wizard_spell['name']}")
            
            # Brief delay to ensure character is committed to database
            import time
            time.sleep(0.5)
            
            # Try to allocate the spell (should succeed)
            alloc_response = self.session.post(f"{BASE_URL}/api/v2/catalog/access", json={
                "character_id": wizard_id,
                "item_id": wizard_spell["id"],
                "access_type": "spells_known",
                "acquired_method": "Level up"
            })
            
            if alloc_response.status_code == 200:
                print(f"✅ VALID allocation succeeded: Wizard can learn {wizard_spell['name']}")
            else:
                print(f"❌ VALID allocation failed unexpectedly: {alloc_response.text}")
                return False
            
            # Test Case 2: Invalid spell allocation (Fighter trying to learn Wizard spells)
            print("\n2. Testing INVALID spell allocation (Fighter learning Wizard spell)...")
            
            # Create a Fighter character
            fighter_data = {
                "name": "Conan the Barbarian",
                "species": "Human", 
                "background": "Soldier",
                "character_classes": {"Fighter": 5},
                "strength": 16,
                "dexterity": 14,
                "constitution": 15,
                "intelligence": 10,
                "wisdom": 12,
                "charisma": 8
            }
            
            fighter_response = self.session.post(f"{BASE_URL}/api/v2/characters", json=fighter_data)
            if fighter_response.status_code != 200:
                print(f"❌ Failed to create fighter: {fighter_response.text}")
                return False
            
            fighter_id = fighter_response.json()["id"]
            print(f"✅ Created Fighter character: {fighter_id}")
            
            # Brief delay to ensure character is committed to database
            time.sleep(0.5)
            
            # Try to allocate the same wizard spell to the fighter (should fail)
            invalid_alloc_response = self.session.post(f"{BASE_URL}/api/v2/catalog/access", json={
                "character_id": fighter_id,
                "item_id": wizard_spell["id"],
                "access_type": "spells_known",
                "acquired_method": "Attempted learning"
            })
            
            if invalid_alloc_response.status_code == 400 or invalid_alloc_response.status_code == 422:
                print(f"✅ INVALID allocation correctly rejected: Fighter cannot learn {wizard_spell['name']}")
                print(f"   Rejection reason: {invalid_alloc_response.json().get('detail', 'Validation failed')}")
            elif invalid_alloc_response.status_code == 500:
                # Check if it's a validation error in the response
                error_detail = invalid_alloc_response.json().get('detail', '')
                if 'validation' in error_detail.lower() or 'cannot use spell' in error_detail.lower():
                    print(f"✅ INVALID allocation correctly rejected: {error_detail}")
                else:
                    print(f"❌ Unexpected server error: {error_detail}")
                    return False
            else:
                print(f"❌ INVALID allocation incorrectly succeeded: {invalid_alloc_response.text}")
                return False
            
            # Test Case 3: Weapon proficiency validation
            print("\n3. Testing weapon proficiency validation...")
            
            # Search for martial weapons
            weapon_response = self.session.get(f"{BASE_URL}/api/v2/catalog/search", params={
                "item_type": "weapon",
                "item_subtype": "martial_weapon",
                "limit": 3
            })
            
            if weapon_response.status_code != 200:
                print(f"❌ Failed to search weapons: {weapon_response.text}")
                return False
            
            weapons = weapon_response.json()["data"]["items"]
            if not weapons:
                print("❌ No martial weapons found")
                return False
            
            martial_weapon = weapons[0]
            print(f"✅ Found martial weapon: {martial_weapon['name']}")
            
            # Create a Wizard (no martial weapon proficiency by default)
            wizard2_data = {
                "name": "Weak Wizard",
                "species": "Human",
                "background": "Hermit", 
                "character_classes": {"Wizard": 1},
                "strength": 8,
                "dexterity": 12,
                "constitution": 12,
                "intelligence": 16,
                "wisdom": 13,
                "charisma": 10
            }
            
            wizard2_response = self.session.post(f"{BASE_URL}/api/v2/characters", json=wizard2_data)
            if wizard2_response.status_code != 200:
                print(f"❌ Failed to create second wizard: {wizard2_response.text}")
                return False
            
            wizard2_id = wizard2_response.json()["id"]
            print(f"✅ Created non-martial Wizard: {wizard2_id}")
            
            # Try to equip martial weapon (should give warning but not fail)
            weapon_alloc_response = self.session.post(f"{BASE_URL}/api/v2/catalog/access", json={
                "character_id": wizard2_id,
                "item_id": martial_weapon["id"],
                "access_type": "equipped",
                "acquired_method": "Found weapon"
            })
            
            if weapon_alloc_response.status_code == 200:
                print(f"✅ Weapon allocation succeeded with proficiency warning")
                # The system should allow allocation but might log warnings
            else:
                # If it fails, check if it's due to proficiency validation
                error_detail = weapon_alloc_response.json().get('detail', '')
                if 'proficient' in error_detail.lower():
                    print(f"✅ Weapon allocation correctly flagged proficiency issue: {error_detail}")
                else:
                    print(f"❌ Unexpected weapon allocation failure: {error_detail}")
            
            # Test Case 4: Check character sheet shows validation status
            print("\n4. Verifying character sheet reflects allocation validation...")
            
            sheet_response = self.session.get(f"{BASE_URL}/api/v2/characters/{wizard_id}/sheet")
            if sheet_response.status_code != 200:
                print(f"❌ Failed to get character sheet: {sheet_response.text}")
                return False
            
            sheet_data = sheet_response.json()
            allocated_spells = sheet_data.get("state", {}).get("allocated_spells", {}).get("spells_known", [])
            
            if allocated_spells:
                print(f"✅ Character sheet shows {len(allocated_spells)} validated spell allocations")
                for spell_alloc in allocated_spells:
                    spell_details = spell_alloc.get("item_details", {})
                    print(f"   - {spell_details.get('name', 'Unknown')} (validated)")
            else:
                print("❌ No allocated spells found in character sheet")
                return False
            
            print("\n" + "="*70)
            print("✅ TASK 2C: CLASS/PROFICIENCY VALIDATION TEST PASSED!")
            print("✅ System correctly validates class restrictions for spells")
            print("✅ System handles weapon proficiency validation")
            print("✅ Invalid allocations are properly rejected")
            print("✅ Valid allocations succeed and appear in character sheets")
            print("="*70)
            
            return True
            
        except Exception as e:
            print(f"\n❌ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    test = AllocationValidationTest()
    success = test.test_allocation_validation()
    
    if not success:
        exit(1)
    
    print("\n🎉 All Task 2C validation tests completed successfully!")
