#!/usr/bin/env python3
"""
Test script for the new CharacterCore setter methods.
This demonstrates the comprehensive setter functionality added to address
the missing setter methods issue.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from character_models import CharacterCore

def test_character_setters():
    """Test all the new setter methods."""
    print("🎲 Testing CharacterCore Setter Methods")
    print("=" * 50)
    
    # Create a new character
    character = CharacterCore()
    
    # Test basic identity setters
    print("\n📋 Testing Identity Setters:")
    
    result = character.set_name("Thorin Ironbeard")
    print(f"Set name: {result}")
    
    result = character.set_species("Dwarf")
    print(f"Set species: {result}")
    
    result = character.set_character_classes({"Fighter": 3, "Cleric": 2})
    print(f"Set classes: {result}")
    
    result = character.set_background("Soldier")
    print(f"Set background: {result}")
    
    result = character.set_alignment(["Lawful", "Good"])
    print(f"Set alignment: {result}")
    
    # Test personality setters
    print("\n🎭 Testing Personality Setters:")
    
    result = character.set_personality_traits([
        "I am always polite and respectful",
        "I have a strong sense of honor"
    ])
    print(f"Set personality traits: {result}")
    
    result = character.set_ideals(["Honor: I will uphold justice"])
    print(f"Set ideals: {result}")
    
    result = character.set_bonds(["My clan is my life"])
    print(f"Set bonds: {result}")
    
    result = character.set_flaws(["I trust too easily"])
    print(f"Set flaws: {result}")
    
    # Test backstory setters
    print("\n📖 Testing Backstory Setters:")
    
    result = character.set_backstory("Born in the mountain halls, trained as a warrior.")
    print(f"Set backstory: {result}")
    
    result = character.set_detailed_backstory({
        "childhood": "Raised in the dwarven stronghold",
        "training": "Trained as both fighter and cleric",
        "motivation": "Seeks to restore honor to his clan"
    })
    print(f"Set detailed backstory: {result}")
    
    # Test ability score setters
    print("\n💪 Testing Ability Score Setters:")
    
    result = character.set_ability_score("strength", 16)
    print(f"Set strength: {result}")
    
    result = character.set_ability_scores({
        "dexterity": 12,
        "constitution": 15,
        "intelligence": 10,
        "wisdom": 14,
        "charisma": 13
    })
    print(f"Set multiple abilities: {result}")
    
    # Test bulk update
    print("\n🔄 Testing Bulk Update:")
    
    bulk_data = {
        "name": "Thorin Ironbeard the Bold",
        "personality_traits": [
            "I am always polite and respectful",
            "I have a strong sense of honor", 
            "I never back down from a challenge"
        ]
    }
    
    result = character.update_character_data(bulk_data)
    print(f"Bulk update: {result}")
    
    # Test validation
    print("\n✅ Testing Validation:")
    
    validation = character.validate()
    print(f"Validation results:")
    print(f"  Valid: {validation['valid']}")
    print(f"  Issues: {len(validation['issues'])}")
    print(f"  Warnings: {len(validation['warnings'])}")
    
    # Test comprehensive validation
    detailed_validation = character.validate_character_data()
    print(f"Detailed validation:")
    print(f"  Valid: {detailed_validation['valid']}")
    print(f"  Completeness: {detailed_validation['completeness_score']:.1%}")
    print(f"  Issues: {len(detailed_validation['issues'])}")
    print(f"  Warnings: {len(detailed_validation['warnings'])}")
    
    # Test character summary
    print("\n📊 Character Summary:")
    
    summary = character.get_character_summary()
    print(f"Character: {summary['identity']['name']}")
    print(f"Species: {summary['identity']['species']}")
    print(f"Classes: {summary['identity']['classes']}")
    print(f"Level: {summary['identity']['level']}")
    print(f"Alignment: {' '.join(summary['identity']['alignment'])}")
    print(f"Completeness: {summary['validation']['completeness_score']:.1%}")
    
    # Test error handling
    print("\n❌ Testing Error Handling:")
    
    result = character.set_name("")  # Should fail
    print(f"Empty name test: {result}")
    
    result = character.set_ability_score("strength", 25)  # Should fail
    print(f"Invalid ability score test: {result}")
    
    result = character.set_character_classes({"Fighter": 25})  # Should fail
    print(f"Invalid class level test: {result}")
    
    print("\n🎉 All setter tests completed!")

if __name__ == "__main__":
    test_character_setters()
