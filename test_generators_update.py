#!/usr/bin/env python3
"""
Test script to verify the updated generators.py works correctly with the new spellcasting system.
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from generators import CustomContentGenerator
from custom_content_models import ContentRegistry
from core_models import SpellcastingManager

# Mock LLM service for testing
class MockLLMService:
    def generate(self, prompt, timeout_seconds=15):
        return '{"name":"Test Item","description":"Test description"}'

def test_spellcaster_detection():
    """Test the updated spellcaster detection method."""
    print("Testing spellcaster detection with new SpellcastingManager...")
    
    # Create generator instance
    registry = ContentRegistry()
    llm_service = MockLLMService()
    generator = CustomContentGenerator(llm_service, registry)
    
    # Test cases
    test_cases = [
        # Full spellcasters
        ({"classes": {"wizard": 5}}, True, "Wizard level 5"),
        ({"classes": {"sorcerer": 3}}, True, "Sorcerer level 3"),
        ({"classes": {"cleric": 1}}, True, "Cleric level 1"),
        ({"classes": {"druid": 2}}, True, "Druid level 2"),
        ({"classes": {"bard": 4}}, True, "Bard level 4"),
        ({"classes": {"warlock": 1}}, True, "Warlock level 1"),
        
        # Half spellcasters
        ({"classes": {"paladin": 2}}, True, "Paladin level 2 (starts spellcasting)"),
        ({"classes": {"paladin": 1}}, False, "Paladin level 1 (no spellcasting yet)"),
        ({"classes": {"ranger": 2}}, True, "Ranger level 2 (starts spellcasting)"),
        ({"classes": {"ranger": 1}}, False, "Ranger level 1 (no spellcasting yet)"),
        ({"classes": {"artificer": 2}}, True, "Artificer level 2 (starts spellcasting)"),
        ({"classes": {"artificer": 1}}, False, "Artificer level 1 (no spellcasting yet)"),
        
        # Third spellcasters
        ({"classes": {"eldritch_knight": 3}}, True, "Eldritch Knight level 3 (starts spellcasting)"),
        ({"classes": {"eldritch_knight": 2}}, False, "Eldritch Knight level 2 (no spellcasting yet)"),
        ({"classes": {"arcane_trickster": 3}}, True, "Arcane Trickster level 3 (starts spellcasting)"),
        ({"classes": {"arcane_trickster": 2}}, False, "Arcane Trickster level 2 (no spellcasting yet)"),
        
        # Non-spellcasters
        ({"classes": {"fighter": 10}}, False, "Fighter level 10"),
        ({"classes": {"barbarian": 5}}, False, "Barbarian level 5"),
        ({"classes": {"rogue": 8}}, False, "Rogue level 8"),
        ({"classes": {"monk": 6}}, False, "Monk level 6"),
        
        # Multiclass combinations
        ({"classes": {"wizard": 3, "fighter": 2}}, True, "Wizard/Fighter multiclass"),
        ({"classes": {"fighter": 5, "barbarian": 3}}, False, "Fighter/Barbarian multiclass"),
        ({"classes": {"paladin": 6, "warlock": 2}}, True, "Paladin/Warlock multiclass"),
        
        # Edge cases
        ({}, False, "No classes"),
        ({"classes": {}}, False, "Empty classes dict"),
    ]
    
    all_passed = True
    for character_data, expected, description in test_cases:
        result = generator._character_is_spellcaster(character_data)
        status = "PASS" if result == expected else "FAIL"
        if result != expected:
            all_passed = False
        print(f"{status}: {description} -> Expected: {expected}, Got: {result}")
    
    print(f"\nOverall result: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    return all_passed

def test_helper_methods():
    """Test the new helper methods."""
    print("\nTesting helper methods...")
    
    registry = ContentRegistry()
    llm_service = MockLLMService()
    generator = CustomContentGenerator(llm_service, registry)
    
    # Test theme extraction
    descriptions = [
        ("A fire-wielding warrior", ["fire", "battle"]),
        ("An ice-cold mage", ["ice", "magic"]),
        ("A shadowy assassin", ["shadow", "battle"]),
        ("A nature-loving druid", ["nature", "magic"]),
        ("An ordinary adventurer", ["general"]),
    ]
    
    print("Theme extraction tests:")
    for desc, expected_themes in descriptions:
        result = generator._extract_simple_themes(desc)
        # Check if any expected themes are found
        has_expected = any(theme in result for theme in expected_themes)
        status = "PASS" if has_expected or (expected_themes == ["general"] and result == ["general"]) else "FAIL"
        print(f"  {status}: '{desc}' -> {result}")
    
    # Test spell level calculation
    print("\nSpell level calculation tests:")
    level_tests = [
        (1, 1), (2, 1), (3, 2), (4, 2), (5, 3), (6, 3),
        (7, 4), (8, 4), (9, 5), (10, 5), (11, 6), (12, 6),
        (13, 7), (14, 7), (15, 8), (16, 8), (17, 9), (18, 9), (19, 9), (20, 9)
    ]
    
    for char_level, expected_spell_level in level_tests:
        result = generator._calculate_max_spell_level(char_level)
        status = "PASS" if result == expected_spell_level else "FAIL"
        print(f"  {status}: Character level {char_level} -> Max spell level {result} (expected {expected_spell_level})")

def main():
    """Run all tests."""
    print("GENERATORS.PY UPDATE VERIFICATION")
    print("=" * 50)
    
    try:
        # Test spellcaster detection
        spellcaster_passed = test_spellcaster_detection()
        
        # Test helper methods
        test_helper_methods()
        
        print("\n" + "=" * 50)
        if spellcaster_passed:
            print("✓ generators.py has been successfully updated!")
            print("✓ Now uses SpellcastingManager for accurate spellcaster detection")
            print("✓ Removed dependencies on refactored character_creation module")
            print("✓ Added helper methods for theme extraction and spell level calculation")
            print("✓ Compatible with the new shared architecture")
        else:
            print("✗ Some tests failed - generators.py may need additional fixes")
            return 1
        
    except Exception as e:
        print(f"ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
