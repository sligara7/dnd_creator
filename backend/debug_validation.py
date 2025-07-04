#!/usr/bin/env python3
"""
Debug script to test the validation function directly
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.creation_validation import validate_item_allocation

# Test data
character_data = {
    "character_classes": {"Fighter": 5},
    "weapon_proficiencies": ["simple weapons"],
    "armor_proficiencies": ["light armor", "medium armor", "heavy armor", "shields"],
    "tool_proficiencies": {},
    "level": 5
}

item_data = {
    "id": "test-spell-id",
    "name": "Fire Bolt",
    "item_type": "spell",
    "spell_level": 0,
    "spell_school": "Evocation",
    "class_restrictions": ["wizard", "sorcerer"],
    "content_data": {
        "name": "Fire Bolt",
        "level": 0,
        "school": "Evocation",
        "classes": ["wizard", "sorcerer"]
    }
}

print("Testing validation function directly...")
print(f"Character: {character_data}")
print(f"Item: {item_data['name']} (requires: {item_data['class_restrictions']})")

result = validate_item_allocation(character_data, item_data, "spells_known")

print(f"Validation result:")
print(f"  Success: {result.success}")
print(f"  Error: {result.error}")
print(f"  Warnings: {result.warnings}")

if result.success:
    print("❌ Fighter was allowed to learn wizard spell - validation logic is wrong!")
else:
    print("✅ Fighter correctly rejected from learning wizard spell")
