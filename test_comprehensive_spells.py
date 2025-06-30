#!/usr/bin/env python3
"""
Test the enhanced spell prioritization system with comprehensive D&D 5e spell database.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from creation import (
    COMPLETE_SPELL_LIST, SPELL_LOOKUP, is_existing_dnd_spell, find_similar_spells,
    get_appropriate_spells_for_character, DND_SPELL_DATABASE
)

def test_spell_lookup():
    """Test the spell lookup functionality."""
    print("=" * 60)
    print("SPELL LOOKUP SYSTEM TEST")
    print("=" * 60)
    
    print(f"Total spells in lookup database: {len(COMPLETE_SPELL_LIST)}")
    print(f"Lookup set size: {len(SPELL_LOOKUP)}")
    
    # Test exact matches
    test_spells = ["Fireball", "Magic Missile", "Cure Wounds", "fireball", "MAGIC MISSILE"]
    print("\n--- EXACT MATCH TESTS ---")
    for spell in test_spells:
        result = is_existing_dnd_spell(spell)
        print(f"'{spell}': {result}")
    
    # Test non-existent spells
    fake_spells = ["Super Fireball", "Mega Healing", "Lightning Storm of Doom"]
    print("\n--- NON-EXISTENT SPELL TESTS ---")
    for spell in fake_spells:
        result = is_existing_dnd_spell(spell)
        print(f"'{spell}': {result}")
    
    # Test similar spell finding
    print("\n--- SIMILAR SPELL TESTS ---")
    test_similar = ["Fire", "Heal", "Light", "Magic", "Lightning"]
    for partial in test_similar:
        similar = find_similar_spells(partial, 3)
        print(f"'{partial}' -> {similar}")

def test_comprehensive_spell_selection():
    """Test spell selection with comprehensive spell database."""
    print("\n" + "=" * 60)
    print("COMPREHENSIVE SPELL SELECTION TEST")
    print("=" * 60)
    
    test_characters = [
        {"name": "Gandalf", "classes": {"Wizard": 5}, "level": 5},
        {"name": "Merlin", "classes": {"Wizard": 10}, "level": 10},
        {"name": "Elara", "classes": {"Cleric": 3}, "level": 3},
        {"name": "Thorn", "classes": {"Druid": 6}, "level": 6},
        {"name": "Seraphina", "classes": {"Sorcerer": 8}, "level": 8},
        {"name": "Nyx", "classes": {"Warlock": 4}, "level": 4},
        {"name": "Lyra", "classes": {"Bard": 7}, "level": 7},
        {"name": "Paladinn", "classes": {"Paladin": 5}, "level": 5},
        {"name": "Hunter", "classes": {"Ranger": 9}, "level": 9}
    ]
    
    for character in test_characters:
        print(f"\n--- {character['name']} ({list(character['classes'].keys())[0]} {character['level']}) ---")
        spells = get_appropriate_spells_for_character(character, 12)
        
        # Group by level
        by_level = {}
        for spell in spells:
            level = spell["level"]
            if level not in by_level:
                by_level[level] = []
            by_level[level].append(spell)
        
        for spell_level in sorted(by_level.keys()):
            level_name = "Cantrips" if spell_level == 0 else f"Level {spell_level}"
            print(f"  {level_name} ({len(by_level[spell_level])} spells):")
            for spell in by_level[spell_level][:3]:  # Show first 3
                print(f"    - {spell['name']} ({spell['school'].title()})")
            if len(by_level[spell_level]) > 3:
                print(f"    ... and {len(by_level[spell_level]) - 3} more")

def test_spell_database_coverage():
    """Test how well our organized database covers the complete spell list."""
    print("\n" + "=" * 60)
    print("SPELL DATABASE COVERAGE TEST")
    print("=" * 60)
    
    # Count spells in organized database
    organized_spells = set()
    for level_data in DND_SPELL_DATABASE.values():
        for school_spells in level_data.values():
            organized_spells.update(school_spells)
    
    print(f"Spells in organized database: {len(organized_spells)}")
    print(f"Spells in complete list: {len(COMPLETE_SPELL_LIST)}")
    print(f"Coverage: {len(organized_spells)/len(COMPLETE_SPELL_LIST)*100:.1f}%")
    
    # Find missing spells
    complete_set = set(COMPLETE_SPELL_LIST)
    missing = complete_set - organized_spells
    
    if missing:
        print(f"\n--- MISSING FROM ORGANIZED DB ({len(missing)} spells) ---")
        for spell in sorted(missing)[:10]:  # Show first 10
            print(f"  - {spell}")
        if len(missing) > 10:
            print(f"  ... and {len(missing) - 10} more")
    
    # Find extra spells in organized DB
    extra = organized_spells - complete_set
    if extra:
        print(f"\n--- EXTRA IN ORGANIZED DB ({len(extra)} spells) ---")
        for spell in sorted(extra):
            print(f"  - {spell}")

if __name__ == "__main__":
    print("COMPREHENSIVE D&D 5E SPELL SYSTEM TEST")
    print("Testing enhanced spell prioritization and lookup...")
    print()
    
    test_spell_lookup()
    test_comprehensive_spell_selection()
    test_spell_database_coverage()
    
    print("\n" + "=" * 60)
    print("SPELL SYSTEM TESTING COMPLETE")
    print("=" * 60)
