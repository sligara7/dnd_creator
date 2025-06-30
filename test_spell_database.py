#!/usr/bin/env python3
"""
Test the D&D 5e spell database and spell selection system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from creation import (
    DND_SPELL_DATABASE, 
    CLASS_SPELL_LISTS, 
    get_appropriate_spells_for_character,
    get_spell_schools_for_class
)

def test_spell_database():
    """Test the spell database structure and content."""
    print("=" * 60)
    print("D&D 5E SPELL DATABASE TEST")
    print("=" * 60)
    
    # Count spells by level
    total_spells = 0
    for level_key, schools in DND_SPELL_DATABASE.items():
        level_count = 0
        level_name = "Cantrips" if level_key == "cantrips" else f"Level {level_key.split('_')[1]}"
        print(f"\n{level_name}:")
        
        for school, spells in schools.items():
            spell_count = len(spells)
            level_count += spell_count
            if spell_count > 0:
                print(f"  {school.title()}: {spell_count} spells")
                # Show first few spells as examples
                if spell_count <= 3:
                    print(f"    Examples: {', '.join(spells)}")
                else:
                    print(f"    Examples: {', '.join(spells[:3])}, ...")
        
        print(f"  Total: {level_count} spells")
        total_spells += level_count
    
    print(f"\nTotal spells in database: {total_spells}")

def test_class_spell_preferences():
    """Test spell preferences for different classes."""
    print("\n" + "=" * 60)
    print("CLASS SPELL PREFERENCES TEST")
    print("=" * 60)
    
    for class_name, info in CLASS_SPELL_LISTS.items():
        schools = info["schools"]
        restrictions = info.get("restrictions", "None")
        print(f"\n{class_name}:")
        print(f"  Preferred Schools: {', '.join(schools)}")
        print(f"  Restrictions: {restrictions}")

def test_spell_selection_for_classes():
    """Test spell selection for different character classes and levels."""
    print("\n" + "=" * 60)
    print("SPELL SELECTION TEST")
    print("=" * 60)
    
    test_cases = [
        {"classes": {"Wizard": 3}, "level": 3},
        {"classes": {"Sorcerer": 5}, "level": 5},
        {"classes": {"Cleric": 2}, "level": 2},
        {"classes": {"Warlock": 4}, "level": 4},
        {"classes": {"Druid": 6}, "level": 6},
        {"classes": {"Bard": 1}, "level": 1},
        {"classes": {"Paladin": 3}, "level": 3},
        {"classes": {"Ranger": 5}, "level": 5},
        {"classes": {"Fighter": 5}, "level": 5},  # Non-spellcaster
    ]
    
    for i, character_data in enumerate(test_cases):
        class_name = list(character_data["classes"].keys())[0]
        level = character_data["level"]
        
        print(f"\n--- Test {i+1}: {class_name} Level {level} ---")
        
        spells = get_appropriate_spells_for_character(character_data, max_spells=12)
        
        if not spells:
            print("  No spells (non-spellcaster or too low level)")
            continue
        
        # Organize spells by level
        spells_by_level = {}
        for spell in spells:
            spell_level = spell["level"]
            if spell_level not in spells_by_level:
                spells_by_level[spell_level] = []
            spells_by_level[spell_level].append(spell)
        
        for spell_level in sorted(spells_by_level.keys()):
            level_name = "Cantrips" if spell_level == 0 else f"Level {spell_level}"
            spells_at_level = spells_by_level[spell_level]
            print(f"  {level_name} ({len(spells_at_level)} spells):")
            
            for spell in spells_at_level:
                print(f"    - {spell['name']} ({spell['school'].title()})")

def test_spell_schools_for_classes():
    """Test getting spell schools for different classes."""
    print("\n" + "=" * 60)
    print("SPELL SCHOOLS FOR CLASSES TEST")
    print("=" * 60)
    
    for class_name in CLASS_SPELL_LISTS.keys():
        schools = get_spell_schools_for_class(class_name)
        print(f"{class_name}: {', '.join(schools)}")

def test_multiclass_spell_selection():
    """Test spell selection for multiclass characters."""
    print("\n" + "=" * 60)
    print("MULTICLASS SPELL SELECTION TEST")
    print("=" * 60)
    
    multiclass_cases = [
        {"classes": {"Wizard": 3, "Cleric": 2}, "level": 5},
        {"classes": {"Sorcerer": 4, "Warlock": 1}, "level": 5},
        {"classes": {"Druid": 2, "Ranger": 3}, "level": 5},
        {"classes": {"Fighter": 8, "Wizard": 2}, "level": 10},
    ]
    
    for i, character_data in enumerate(multiclass_cases):
        classes = character_data["classes"]
        level = character_data["level"]
        class_names = " / ".join([f"{name} {lvl}" for name, lvl in classes.items()])
        
        print(f"\n--- Test {i+1}: {class_names} (Total Level {level}) ---")
        
        spells = get_appropriate_spells_for_character(character_data, max_spells=15)
        
        if not spells:
            print("  No spells selected")
            continue
        
        print(f"  Selected {len(spells)} spells:")
        for spell in spells:
            level_name = "Cantrip" if spell["level"] == 0 else f"Level {spell['level']}"
            print(f"    - {spell['name']} ({level_name}, {spell['school'].title()})")

if __name__ == "__main__":
    test_spell_database()
    test_class_spell_preferences()
    test_spell_selection_for_classes()
    test_spell_schools_for_classes()
    test_multiclass_spell_selection()
    
    print("\n" + "=" * 60)
    print("SPELL DATABASE TESTING COMPLETE")
    print("=" * 60)
