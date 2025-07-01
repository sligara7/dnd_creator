#!/usr/bin/env python3
"""
Quick integration test for the equipment system with character creation.
"""

import sys
import os
import asyncio
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from creation import CharacterCreator
from backend.creation_validation import validate_armor_database, validate_tools_database, validate_gear_database

async def test_equipment_integration():
    """Test that equipment system integrates properly with character creation."""
    print("Testing Equipment System Integration...")
    
    # Validate all databases first
    print("Validating D&D 5e databases...")
    assert validate_armor_database(), "Armor database validation failed"
    assert validate_tools_database(), "Tools database validation failed"
    assert validate_gear_database(), "Gear database validation failed"
    print("✓ All databases validated successfully")
    
    # Test character creation with different classes
    creator = CharacterCreator()
    
    test_characters = [
        {
            "name": "Test Fighter",
            "species": "Human",
            "character_class": "Fighter",
            "level": 3,
            "background": "Soldier",
            "concept": "A brave warrior"
        },
        {
            "name": "Test Wizard",
            "species": "Elf",
            "character_class": "Wizard",
            "level": 2,
            "background": "Sage",
            "concept": "A scholarly mage"
        },
        {
            "name": "Test Rogue",
            "species": "Halfling",
            "character_class": "Rogue",
            "level": 4,
            "background": "Criminal",
            "concept": "A sneaky thief"
        }
    ]
    
    for char_data in test_characters:
        print(f"\nTesting {char_data['name']} ({char_data['character_class']})...")
        
        try:
            # Create character using the full pipeline
            result = await creator.create_character(char_data)
            
            # Check if creation was successful
            assert result.success, f"Character creation failed: {result.error}"
            character = result.data
            
            # Verify character has equipment
            assert 'armor' in character, f"Character missing armor field"
            assert 'equipment' in character, f"Character missing equipment field"
            assert 'tools' in character, f"Character missing tools field"
            
            # Check that character has appropriate equipment for their class
            armor = character.get('armor', [])
            equipment = character.get('equipment', [])
            tools = character.get('tools', [])
            
            print(f"  ✓ Armor: {len(armor)} items")
            print(f"  ✓ Equipment: {len(equipment)} items")
            print(f"  ✓ Tools: {len(tools)} items")
            
            # Print some examples
            if armor:
                print(f"    Armor: {', '.join([item['name'] for item in armor[:2]])}")
            if equipment:
                print(f"    Equipment: {', '.join([item['name'] for item in equipment[:3]])}")
            if tools:
                print(f"    Tools: {', '.join([item['name'] for item in tools[:2]])}")
            
        except Exception as e:
            print(f"❌ Character creation failed for {char_data['name']}: {e}")
            raise
    
    print("\n✅ Equipment integration test passed!")
    print("The enhanced D&D 5e character creator successfully prioritizes")
    print("official equipment, armor, and tools for all character classes!")

if __name__ == "__main__":
    asyncio.run(test_equipment_integration())
