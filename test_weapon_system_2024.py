#!/usr/bin/env python3
"""
Test script for D&D 5e 2024 weapon prioritization system.
Verifies that character creation properly prioritizes official D&D weapons
and follows D&D 5e weapon rules and properties.
"""

import sys
import os
import asyncio

# Add the backend directory to the path
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend')

from creation import (
    DND_WEAPON_DATABASE, ALL_WEAPON_NAMES, CLASS_WEAPON_PROFICIENCIES,
    find_appropriate_weapons_for_character, is_existing_dnd_weapon,
    find_similar_weapons, _create_weapon_entry
)

def test_weapon_database_completeness():
    """Test that the weapon database includes all D&D 5e 2024 weapons."""
    print("=== Testing D&D 5e 2024 Weapon Database Completeness ===")
    
    # Expected weapon counts per category based on D&D 5e 2024
    expected_simple_melee = 10  # Club, Dagger, Greatclub, Handaxe, Javelin, Light Hammer, Mace, Quarterstaff, Sickle, Spear
    expected_simple_ranged = 4  # Dart, Light Crossbow, Shortbow, Sling
    expected_martial_melee = 18  # All martial melee weapons
    expected_martial_ranged = 6  # All martial ranged weapons
    
    actual_simple_melee = len(DND_WEAPON_DATABASE.get("simple_melee", {}))
    actual_simple_ranged = len(DND_WEAPON_DATABASE.get("simple_ranged", {}))
    actual_martial_melee = len(DND_WEAPON_DATABASE.get("martial_melee", {}))
    actual_martial_ranged = len(DND_WEAPON_DATABASE.get("martial_ranged", {}))
    
    print(f"Simple Melee: {actual_simple_melee}/{expected_simple_melee}")
    print(f"Simple Ranged: {actual_simple_ranged}/{expected_simple_ranged}")
    print(f"Martial Melee: {actual_martial_melee}/{expected_martial_melee}")
    print(f"Martial Ranged: {actual_martial_ranged}/{expected_martial_ranged}")
    
    # Test specific weapons exist
    required_weapons = [
        "Longsword", "Shortsword", "Rapier", "Dagger", "Greatsword", "Battleaxe",
        "Longbow", "Shortbow", "Light Crossbow", "Heavy Crossbow",
        "Club", "Mace", "Quarterstaff", "Spear", "Handaxe"
    ]
    
    missing_weapons = []
    for weapon in required_weapons:
        if not is_existing_dnd_weapon(weapon):
            missing_weapons.append(weapon)
    
    if missing_weapons:
        print(f"❌ Missing required weapons: {missing_weapons}")
        return False
    else:
        print("✅ All required weapons found in database")
        return True

def test_weapon_properties():
    """Test that weapons have correct properties according to D&D 5e 2024."""
    print("\n=== Testing Weapon Properties ===")
    
    # Test specific weapon properties
    test_cases = [
        ("Longsword", {"damage": "1d8", "damage_type": "slashing", "properties": ["Versatile (1d10)"], "mastery": "Sap"}),
        ("Rapier", {"damage": "1d8", "damage_type": "piercing", "properties": ["Finesse"], "mastery": "Vex"}),
        ("Dagger", {"damage": "1d4", "damage_type": "piercing", "properties": ["Finesse", "Light", "Thrown (20/60)"], "mastery": "Nick"}),
        ("Greatsword", {"damage": "2d6", "damage_type": "slashing", "properties": ["Heavy", "Two-Handed"], "mastery": "Graze"}),
        ("Longbow", {"damage": "1d8", "damage_type": "piercing", "properties": ["Ammunition (150/600; Arrow)", "Heavy", "Two-Handed"], "mastery": "Slow"}),
    ]
    
    errors = []
    for weapon_name, expected_props in test_cases:
        if is_existing_dnd_weapon(weapon_name):
            # Find the weapon in database
            weapon_found = False
            for category, weapons in DND_WEAPON_DATABASE.items():
                if weapon_name in weapons:
                    weapon_data = weapons[weapon_name]
                    weapon_found = True
                    
                    # Check each expected property
                    for prop, expected_value in expected_props.items():
                        if prop in weapon_data:
                            actual_value = weapon_data[prop]
                            if actual_value != expected_value:
                                errors.append(f"{weapon_name}.{prop}: expected {expected_value}, got {actual_value}")
                        else:
                            errors.append(f"{weapon_name} missing property: {prop}")
                    break
            
            if not weapon_found:
                errors.append(f"{weapon_name} not found in database")
        else:
            errors.append(f"{weapon_name} not recognized as existing D&D weapon")
    
    if errors:
        print(f"❌ Property errors found:")
        for error in errors:
            print(f"  - {error}")
        return False
    else:
        print("✅ All weapon properties correct")
        return True

def test_class_weapon_allocation():
    """Test that characters get appropriate weapons for their class."""
    print("\n=== Testing Class Weapon Allocation ===")
    
    test_characters = [
        {"classes": {"Fighter": 5}, "level": 5},
        {"classes": {"Wizard": 3}, "level": 3},
        {"classes": {"Rogue": 4}, "level": 4},
        {"classes": {"Cleric": 2}, "level": 2},
        {"classes": {"Barbarian": 6}, "level": 6},
        {"classes": {"Ranger": 3}, "level": 3},
    ]
    
    for character_data in test_characters:
        class_name = list(character_data["classes"].keys())[0]
        level = character_data["level"]
        
        weapons = find_appropriate_weapons_for_character(character_data, 3)
        
        print(f"{class_name} (Level {level}):")
        for weapon in weapons:
            print(f"  - {weapon['name']} ({weapon['damage']} {weapon['damage_type']})")
        
        # Verify all weapons are official D&D weapons
        non_dnd_weapons = [w for w in weapons if w.get('source') != 'D&D 5e Official']
        if non_dnd_weapons:
            print(f"❌ {class_name} has non-D&D weapons: {[w['name'] for w in non_dnd_weapons]}")
            return False
    
    print("✅ All classes receive appropriate D&D 5e weapons")
    return True

def test_weapon_lookup_functions():
    """Test weapon lookup and similarity functions."""
    print("\n=== Testing Weapon Lookup Functions ===")
    
    # Test exact matches
    exact_tests = ["Longsword", "Rapier", "DAGGER", "shortbow"]
    for weapon in exact_tests:
        if not is_existing_dnd_weapon(weapon):
            print(f"❌ Failed to find exact match for: {weapon}")
            return False
    
    # Test similarity search
    similarity_tests = [
        ("Long sword", ["Longsword"]),  # Should find close match
        ("short", ["Shortsword", "Shortbow"]),  # Should find multiple matches
        ("InvalidWeapon", []),  # Should find no matches
    ]
    
    for test_input, expected_results in similarity_tests:
        similar = find_similar_weapons(test_input, 5)
        if test_input == "InvalidWeapon":
            if similar:
                print(f"❌ Found unexpected matches for {test_input}: {similar}")
                return False
        else:
            if not similar:
                print(f"❌ No similar weapons found for: {test_input}")
                return False
            
            # Check if expected results are in the found results
            for expected in expected_results:
                if expected not in similar:
                    print(f"❌ Expected {expected} in results for {test_input}, got: {similar}")
                    return False
    
    print("✅ Weapon lookup functions working correctly")
    return True

def test_weapon_mastery_properties():
    """Test that weapons have correct mastery properties."""
    print("\n=== Testing Weapon Mastery Properties ===")
    
    # Test mastery property mappings according to D&D 5e 2024
    mastery_tests = [
        ("Cleave", ["Greataxe", "Halberd"]),
        ("Graze", ["Glaive", "Greatsword"]),
        ("Nick", ["Dagger", "Light Hammer", "Sickle", "Scimitar"]),
        ("Push", ["Greatclub", "Pike", "Warhammer", "Heavy Crossbow"]),
        ("Sap", ["Mace", "Spear", "Flail", "Longsword", "Morningstar", "War Pick"]),
        ("Slow", ["Club", "Javelin", "Light Crossbow", "Sling", "Whip", "Longbow", "Musket"]),
        ("Topple", ["Quarterstaff", "Battleaxe", "Lance", "Maul", "Trident"]),
        ("Vex", ["Handaxe", "Dart", "Rapier", "Shortsword", "Blowgun", "Hand Crossbow", "Shortbow", "Pistol"]),
    ]
    
    errors = []
    for mastery, expected_weapons in mastery_tests:
        for weapon_name in expected_weapons:
            if is_existing_dnd_weapon(weapon_name):
                # Find weapon in database and check mastery
                weapon_found = False
                for category, weapons in DND_WEAPON_DATABASE.items():
                    if weapon_name in weapons:
                        weapon_data = weapons[weapon_name]
                        actual_mastery = weapon_data.get("mastery", "")
                        if actual_mastery != mastery:
                            errors.append(f"{weapon_name}: expected mastery '{mastery}', got '{actual_mastery}'")
                        weapon_found = True
                        break
                
                if not weapon_found:
                    errors.append(f"{weapon_name} not found in database")
            else:
                errors.append(f"{weapon_name} not recognized as existing D&D weapon")
    
    if errors:
        print(f"❌ Mastery property errors:")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  - {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more errors")
        return False
    else:
        print("✅ All weapon mastery properties correct")
        return True

def main():
    """Run all weapon system tests."""
    print("D&D 5e 2024 Weapon System Test Suite")
    print("=" * 50)
    
    tests = [
        test_weapon_database_completeness,
        test_weapon_properties,
        test_class_weapon_allocation,
        test_weapon_lookup_functions,
        test_weapon_mastery_properties,
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
            else:
                print(f"❌ Test failed: {test.__name__}")
        except Exception as e:
            print(f"❌ Test error in {test.__name__}: {e}")
    
    print(f"\n=== Test Summary ===")
    print(f"Passed: {passed}/{total}")
    if passed == total:
        print("✅ All weapon system tests passed!")
        return True
    else:
        print("❌ Some weapon system tests failed!")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
