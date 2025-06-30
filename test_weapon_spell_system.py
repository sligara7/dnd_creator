#!/usr/bin/env python3
"""
Test the enhanced weapon and spell selection system for D&D 5e character creation.

This script tests:
- Weapon database completeness and lookup functions
- Spell database completeness and lookup functions  
- Character-specific weapon selection
- Weapon and spell prioritization over custom content
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

try:
    from creation import (
        DND_WEAPON_DATABASE, ALL_DND_WEAPONS, WEAPON_LOOKUP,
        COMPLETE_SPELL_LIST, SPELL_LOOKUP,
        is_existing_dnd_weapon, find_weapon_by_name, get_weapons_for_class,
        get_appropriate_weapons_for_character, find_similar_weapons,
        is_existing_dnd_spell, find_similar_spells
    )
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure all required modules are available.")
    sys.exit(1)

def test_weapon_database():
    """Test the weapon database completeness and lookup functions."""
    print("=" * 80)
    print("D&D 5E WEAPON DATABASE TEST")
    print("=" * 80)
    
    total_weapons = 0
    for category_name, category in DND_WEAPON_DATABASE.items():
        print(f"\n{category_name.replace('_', ' ').title()}:")
        print(f"  {len(category)} weapons")
        for weapon_name, weapon_data in list(category.items())[:3]:  # Show first 3
            print(f"    {weapon_name}: {weapon_data['damage']} {weapon_data['damage_type']}")
        if len(category) > 3:
            print(f"    ... and {len(category) - 3} more")
        total_weapons += len(category)
    
    print(f"\nTotal weapons in database: {total_weapons}")
    print(f"Total weapons in lookup list: {len(ALL_DND_WEAPONS)}")
    print(f"Total weapons in lookup set: {len(WEAPON_LOOKUP)}")

def test_weapon_lookup():
    """Test weapon lookup and search functions."""
    print("\n" + "=" * 80)
    print("WEAPON LOOKUP TEST")
    print("=" * 80)
    
    # Test exact matches
    test_weapons = ["Longsword", "Shortbow", "Dagger", "Fireball"]  # Fireball should fail
    
    print("\n--- Exact Weapon Lookup ---")
    for weapon in test_weapons:
        exists = is_existing_dnd_weapon(weapon)
        print(f"  {weapon}: {'✓' if exists else '✗'}")
        
        if exists:
            weapon_data = find_weapon_by_name(weapon)
            if weapon_data:
                print(f"    {weapon_data['damage']} {weapon_data['damage_type']}, {weapon_data['category']} {weapon_data['type']}")
    
    # Test similar weapon searches
    print("\n--- Similar Weapon Search ---")
    test_searches = ["sword", "bow", "axe", "magical staff"]
    
    for search in test_searches:
        similar = find_similar_weapons(search, 3)
        print(f"  '{search}' → {similar}")

def test_class_weapons():
    """Test class-specific weapon selection."""
    print("\n" + "=" * 80)
    print("CLASS WEAPON SELECTION TEST")
    print("=" * 80)
    
    test_classes = ["Fighter", "Wizard", "Rogue", "Cleric", "Ranger", "Barbarian"]
    
    for class_name in test_classes:
        weapons = get_weapons_for_class(class_name, 5)
        print(f"\n--- {class_name} Weapons (Level 5) ---")
        print(f"  Found {len(weapons)} appropriate weapons:")
        for weapon in weapons[:4]:  # Show first 4
            print(f"    {weapon['name']}: {weapon['damage']} {weapon['damage_type']} ({weapon['category']} {weapon['type']})")
        if len(weapons) > 4:
            print(f"    ... and {len(weapons) - 4} more")

def test_character_weapon_selection():
    """Test character-specific weapon selection."""
    print("\n" + "=" * 80)
    print("CHARACTER WEAPON SELECTION TEST")
    print("=" * 80)
    
    test_characters = [
        {"classes": {"Fighter": 5}, "level": 5},
        {"classes": {"Wizard": 3}, "level": 3},
        {"classes": {"Rogue": 4}, "level": 4},
        {"classes": {"Cleric": 2}, "level": 2},
        {"classes": {"Ranger": 6}, "level": 6},
        {"classes": {"Fighter": 3, "Wizard": 2}, "level": 5}  # Multiclass
    ]
    
    for i, character in enumerate(test_characters, 1):
        class_names = list(character["classes"].keys())
        level = character["level"]
        
        weapons = get_appropriate_weapons_for_character(character, 3)
        
        print(f"\n--- Test {i}: {'/'.join(class_names)} Level {level} ---")
        print(f"  Selected {len(weapons)} weapons:")
        for weapon in weapons:
            print(f"    {weapon['name']}: {weapon['damage']} {weapon['damage_type']} ({weapon['type']})")

def test_spell_database():
    """Test the spell database completeness and lookup functions."""
    print("\n" + "=" * 80)
    print("D&D 5E SPELL DATABASE TEST")
    print("=" * 80)
    
    print(f"Total spells in database: {len(COMPLETE_SPELL_LIST)}")
    print(f"Total spells in lookup set: {len(SPELL_LOOKUP)}")
    
    # Show some examples by level
    cantrips = [s for s in COMPLETE_SPELL_LIST if any(s in ["Fire Bolt", "Mage Hand", "Guidance"])]
    level1 = [s for s in COMPLETE_SPELL_LIST if any(s in ["Magic Missile", "Cure Wounds", "Shield"])]
    level3 = [s for s in COMPLETE_SPELL_LIST if any(s in ["Fireball", "Lightning Bolt", "Counterspell"])]
    
    print(f"\nExample Cantrips: {', '.join(cantrips)}")
    print(f"Example Level 1: {', '.join(level1)}")
    print(f"Example Level 3: {', '.join(level3)}")

def test_spell_lookup():
    """Test spell lookup and search functions."""
    print("\n" + "=" * 80)
    print("SPELL LOOKUP TEST")
    print("=" * 80)
    
    # Test exact matches
    test_spells = ["Fireball", "Magic Missile", "Cure Wounds", "Longsword"]  # Longsword should fail
    
    print("\n--- Exact Spell Lookup ---")
    for spell in test_spells:
        exists = is_existing_dnd_spell(spell)
        print(f"  {spell}: {'✓' if exists else '✗'}")
    
    # Test similar spell searches
    print("\n--- Similar Spell Search ---")
    test_searches = ["fire", "heal", "missile", "magic sword"]
    
    for search in test_searches:
        similar = find_similar_spells(search, 3)
        print(f"  '{search}' → {similar}")

def main():
    """Run all tests."""
    print("D&D 5E WEAPON & SPELL SYSTEM TEST")
    print("Testing enhanced weapon and spell selection system...")
    
    try:
        test_weapon_database()
        test_weapon_lookup()
        test_class_weapons()
        test_character_weapon_selection()
        test_spell_database()
        test_spell_lookup()
        
        print("\n" + "=" * 80)
        print("WEAPON & SPELL SYSTEM TESTING COMPLETE")
        print("=" * 80)
        
    except Exception as e:
        print(f"\nTest failed with error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
