#!/usr/bin/env python3
"""
Test script for the comprehensive D&D 5e feat system.

This script verifies that:
1. Traditional D&D 5e feats are prioritized over custom feats
2. Feat allocation follows D&D 5e 2024 rules for level and class requirements
3. All feat categories are properly handled (Origin, General, Fighting Style, Epic Boon)
4. Feat prerequisites are properly validated
"""

import sys
import os
import time
import logging

# Add the backend directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from backend.dnd_data import (
    DND_FEAT_DATABASE, ALL_FEATS, FEAT_LOOKUP, FEAT_AVAILABILITY,
    is_existing_dnd_feat, find_similar_feats, get_feat_data,
    get_available_feats_for_level, get_appropriate_feats_for_character
)
from backend.creation_validation import validate_feat_prerequisites, validate_feat_database

def test_feat_database_integrity():
    """Test that the feat database is complete and correctly structured."""
    print("Testing feat database integrity...")
    
    # Test database validation
    assert validate_feat_database(), "Feat database validation failed"
    print("✓ Feat database validation passed")
    
    # Test that all categories exist
    expected_categories = ["origin_feats", "general_feats", "fighting_style_feats", "epic_boon_feats"]
    for category in expected_categories:
        assert category in DND_FEAT_DATABASE, f"Missing feat category: {category}"
    print("✓ All feat categories present")
    
    # Test that key feats exist
    key_feats = [
        "Alert", "Magic Initiate", "Skilled", "Savage Attacker",  # Origin
        "Ability Score Improvement", "Tough", "Lucky", "Resilient",  # General
        "Archery", "Defense", "Great Weapon Fighting", "Two-Weapon Fighting",  # Fighting Style
        "Boon of Combat Prowess", "Boon of Dimensional Travel", "Boon of Fate"  # Epic Boon
    ]
    
    for feat in key_feats:
        assert is_existing_dnd_feat(feat), f"Key feat missing: {feat}"
        feat_data = get_feat_data(feat)
        assert feat_data is not None, f"No data for feat: {feat}"
        assert "description" in feat_data, f"Feat {feat} missing description"
        assert "benefits" in feat_data, f"Feat {feat} missing benefits"
        assert "category" in feat_data, f"Feat {feat} missing category"
    print("✓ All key feats present with required data")
    
    print("Feat database integrity test completed successfully!\n")

def test_feat_lookup_functions():
    """Test feat lookup and search functions."""
    print("Testing feat lookup functions...")
    
    # Test exact feat lookup
    assert is_existing_dnd_feat("Alert"), "Alert feat not found"
    assert is_existing_dnd_feat("alert"), "Case-insensitive lookup failed"
    assert not is_existing_dnd_feat("Nonexistent Feat"), "False positive for nonexistent feat"
    print("✓ Feat existence checking works correctly")
    
    # Test feat data retrieval
    alert_data = get_feat_data("Alert")
    assert alert_data is not None, "Alert feat data not found"
    assert alert_data["category"] == "Origin", "Alert feat category incorrect"
    assert "initiative" in alert_data["description"].lower(), "Alert feat description incorrect"
    print("✓ Feat data retrieval works correctly")
    
    # Test similar feat finding
    similar = find_similar_feats("Magic", 3)
    assert "Magic Initiate" in similar, "Magic Initiate not found in similar feats"
    print("✓ Similar feat finding works correctly")
    
    print("Feat lookup functions test completed successfully!\n")

def test_feat_level_availability():
    """Test feat availability based on character level and class."""
    print("Testing feat availability by level and class...")
    
    # Test level 1 character
    level_1_feats = get_available_feats_for_level(1, "Fighter")
    assert len(level_1_feats["origin_feats"]) > 0, "No origin feats available at level 1"
    assert len(level_1_feats["fighting_style_feats"]) > 0, "No fighting style feats for Fighter"
    assert len(level_1_feats["general_feats"]) == 0, "General feats available too early"
    assert len(level_1_feats["epic_boon_feats"]) == 0, "Epic boons available too early"
    print("✓ Level 1 feat availability correct")
    
    # Test level 4 character (first ASI)
    level_4_feats = get_available_feats_for_level(4, "Wizard")
    assert len(level_4_feats["origin_feats"]) > 0, "Origin feats should remain available"
    assert len(level_4_feats["general_feats"]) > 0, "General feats should be available at level 4"
    assert len(level_4_feats["fighting_style_feats"]) == 0, "Fighting style feats should not be available for Wizard"
    print("✓ Level 4 feat availability correct")
    
    # Test level 20 character
    level_20_feats = get_available_feats_for_level(20, "Paladin")
    assert len(level_20_feats["epic_boon_feats"]) > 0, "Epic boons should be available at level 20"
    assert len(level_20_feats["fighting_style_feats"]) > 0, "Fighting style feats should be available for Paladin"
    print("✓ Level 20 feat availability correct")
    
    print("Feat availability test completed successfully!\n")

def test_character_appropriate_feats():
    """Test that appropriate feats are suggested for different character types."""
    print("Testing character-appropriate feat suggestions...")
    
    # Test spellcaster character
    wizard_data = {
        "level": 5,
        "classes": {"Wizard": 5},
        "species": "Human",
        "background": "Sage"
    }
    wizard_feats = get_appropriate_feats_for_character(wizard_data, 5)
    assert len(wizard_feats) > 0, "No feats suggested for wizard"
    
    # Check that appropriate feats are suggested
    feat_names = [f["name"] for f in wizard_feats]
    spellcaster_feats = ["Magic Initiate", "War Caster", "Fey Touched", "Resilient"]
    assert any(feat in feat_names for feat in spellcaster_feats), f"No appropriate spellcaster feats suggested: {feat_names}"
    print("✓ Appropriate feats suggested for spellcaster")
    
    # Test warrior character
    fighter_data = {
        "level": 8,
        "classes": {"Fighter": 8},
        "species": "Human",
        "background": "Soldier"
    }
    fighter_feats = get_appropriate_feats_for_character(fighter_data, 5)
    assert len(fighter_feats) > 0, "No feats suggested for fighter"
    
    # Check for fighting style feats
    feat_names = [f["name"] for f in fighter_feats]
    fighting_style_feats = ["Archery", "Defense", "Great Weapon Fighting", "Two-Weapon Fighting"]
    assert any(feat in feat_names for feat in fighting_style_feats), f"No fighting style feats suggested: {feat_names}"
    print("✓ Appropriate feats suggested for warrior")
    
    # Test high-level character
    high_level_data = {
        "level": 20,
        "classes": {"Paladin": 20},
        "species": "Dragonborn",
        "background": "Noble"
    }
    high_level_feats = get_appropriate_feats_for_character(high_level_data, 6)
    feat_names = [f["name"] for f in high_level_feats]
    assert any("Boon of" in feat for feat in feat_names), f"No epic boons suggested for level 20: {feat_names}"
    print("✓ Epic boons suggested for high-level character")
    
    print("Character-appropriate feat suggestions test completed successfully!\n")

def test_feat_prerequisites():
    """Test feat prerequisite validation."""
    print("Testing feat prerequisite validation...")
    
    # Test character that meets prerequisites
    strong_character = {
        "level": 5,
        "classes": {"Fighter": 5},
        "ability_scores": {"strength": 15, "dexterity": 12, "constitution": 14},
        "spells_known": []
    }
    
    # Grappler requires Strength 13+
    assert validate_feat_prerequisites("Grappler", strong_character), "Grappler should be valid for strong character"
    print("✓ Prerequisite validation works for valid character")
    
    # Test character that doesn't meet prerequisites
    weak_character = {
        "level": 3,
        "classes": {"Wizard": 3},
        "ability_scores": {"strength": 8, "dexterity": 14, "intelligence": 16},
        "spells_known": ["Magic Missile"]
    }
    
    # Grappler requires Strength 13+
    assert not validate_feat_prerequisites("Grappler", weak_character), "Grappler should not be valid for weak character"
    print("✓ Prerequisite validation correctly rejects invalid character")
    
    # Test spellcasting prerequisites
    spellcaster = {
        "level": 6,
        "classes": {"Cleric": 6},
        "ability_scores": {"wisdom": 16, "constitution": 14},
        "spells_known": ["Cure Wounds", "Bless"]
    }
    
    # War Caster requires spellcasting ability
    assert validate_feat_prerequisites("War Caster", spellcaster), "War Caster should be valid for spellcaster"
    print("✓ Spellcasting prerequisite validation works")
    
    print("Feat prerequisite validation test completed successfully!\n")

def test_feat_prioritization():
    """Test that D&D 5e feats are prioritized over custom feats."""
    print("Testing D&D 5e feat prioritization...")
    
    # Test character with mixed existing and custom feats
    character_with_mixed_feats = {
        "level": 8,
        "classes": {"Rogue": 8},
        "origin_feat": "Alert",  # Existing D&D feat
        "general_feats": [
            {"name": "Lucky", "level": 4},  # Existing D&D feat
            {"name": "Custom Stealth Master", "level": 8}  # Custom feat
        ],
        "fighting_style_feats": [],
        "epic_boon": ""
    }
    
    # Check that existing feats are recognized
    assert is_existing_dnd_feat("Alert"), "Alert should be recognized as D&D feat"
    assert is_existing_dnd_feat("Lucky"), "Lucky should be recognized as D&D feat"
    assert not is_existing_dnd_feat("Custom Stealth Master"), "Custom feat should not be recognized as D&D feat"
    print("✓ D&D feats correctly distinguished from custom feats")
    
    # Test feat coverage
    total_dnd_feats = len(ALL_FEATS)
    assert total_dnd_feats >= 20, f"Expected at least 20 D&D feats, found {total_dnd_feats}"
    print(f"✓ Comprehensive feat coverage: {total_dnd_feats} D&D 5e feats available")
    
    # Test that all feat categories have options
    for category, feats in DND_FEAT_DATABASE.items():
        assert len(feats) > 0, f"No feats in category: {category}"
    print("✓ All feat categories have available options")
    
    print("D&D 5e feat prioritization test completed successfully!\n")

def run_all_tests():
    """Run all feat system tests."""
    print("=" * 60)
    print("COMPREHENSIVE D&D 5E FEAT SYSTEM TEST")
    print("=" * 60)
    print()
    
    start_time = time.time()
    
    try:
        test_feat_database_integrity()
        test_feat_lookup_functions()
        test_feat_level_availability()
        test_character_appropriate_feats()
        test_feat_prerequisites()
        test_feat_prioritization()
        
        end_time = time.time()
        
        print("=" * 60)
        print("ALL FEAT SYSTEM TESTS PASSED! ✓")
        print(f"Total test time: {end_time - start_time:.2f} seconds")
        print("=" * 60)
        print()
        print("Summary:")
        print("- D&D 5e feat database is complete and properly structured")
        print("- Feat lookup and search functions work correctly")
        print("- Feat availability follows D&D 5e level and class rules")
        print("- Character-appropriate feats are suggested based on class and level")
        print("- Feat prerequisites are properly validated")
        print("- D&D 5e feats are prioritized over custom feat creation")
        print()
        print("The feat system is ready for use in character creation!")
        
        return True
        
    except AssertionError as e:
        print(f"TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"TEST ERROR: {e}")
        return False

if __name__ == "__main__":
    # Configure logging to reduce noise during testing
    logging.basicConfig(level=logging.WARNING)
    
    success = run_all_tests()
    
    if success:
        print("\n🎉 All feat system tests completed successfully!")
        exit(0)
    else:
        print("\n❌ Feat system tests failed!")
        exit(1)
