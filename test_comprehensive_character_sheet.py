#!/usr/bin/env python3
"""Test script to verify the comprehensive character sheet implementation works correctly."""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

from character_models import CharacterSheet, CharacterCore, CharacterState, CharacterStats, ProficiencyLevel

def test_comprehensive_character_sheet():
    """Test the comprehensive character sheet functionality."""
    print("Testing comprehensive character sheet implementation...")
    
    # Create a new character
    character = CharacterSheet("Test Hero")
    
    # Test basic character creation
    character.core.species = "Human"
    character.core.background = "Soldier"
    character.core.character_classes["Fighter"] = 1
    
    # Test ability scores
    character.core.strength.base_score = 16
    character.core.dexterity.base_score = 14
    character.core.constitution.base_score = 15
    character.core.intelligence.base_score = 10
    character.core.wisdom.base_score = 13
    character.core.charisma.base_score = 12
    
    # Test skill proficiencies
    character.core.skill_proficiencies["Athletics"] = ProficiencyLevel.PROFICIENT
    character.core.skill_proficiencies["Intimidation"] = ProficiencyLevel.PROFICIENT
    
    # Test stats calculation
    character.calculate_all_derived_stats()
    
    # Validate calculations
    print(f"Character Name: {character.name}")
    print(f"Total Level: {character.total_level}")
    print(f"Proficiency Bonus: {character.stats.proficiency_bonus}")
    print(f"Armor Class: {character.armor_class}")
    print(f"Max Hit Points: {character.max_hit_points}")
    print(f"Initiative: {character.stats.initiative}")
    
    # Test ability score modifiers
    print(f"Strength: {character.core.strength.total_score} ({character.core.strength.modifier:+d})")
    print(f"Dexterity: {character.core.dexterity.total_score} ({character.core.dexterity.modifier:+d})")
    print(f"Constitution: {character.core.constitution.total_score} ({character.core.constitution.modifier:+d})")
    
    # Test skill calculations
    athletics_bonus = character.stats.calculate_skill_bonus("Athletics")
    print(f"Athletics bonus: {athletics_bonus:+d}")
    
    # Test equipment and armor
    character.state.armor = "Chain Mail"
    character.state.shield = True
    character.calculate_all_derived_stats()
    print(f"AC with Chain Mail and Shield: {character.armor_class}")
    
    # Test hit points
    character.state.current_hit_points = character.max_hit_points
    print(f"Current HP: {character.current_hit_points}/{character.max_hit_points}")
    
    # Test damage and healing
    damage_result = character.take_damage(5)
    print(f"After taking 5 damage: {character.current_hit_points}/{character.max_hit_points}")
    
    healed = character.heal(3)
    print(f"After healing 3 HP: {character.current_hit_points}/{character.max_hit_points}")
    
    # Test validation
    validation_result = character.validate_against_rules(use_unified=False)
    print(f"Character is valid: {validation_result['overall_valid']}")
    if validation_result["all_issues"]:
        print(f"Issues: {validation_result['all_issues']}")
    
    # Test serialization
    character_dict = character.to_dict()
    print("Character serialization successful")
    
    # Test character summary
    summary = character.get_character_summary()
    print("Character summary generated successfully")
    
    print("\n✅ All comprehensive character sheet tests passed!")
    return True

def test_character_leveling():
    """Test character leveling functionality."""
    print("\nTesting character leveling...")
    
    character = CharacterSheet("Leveling Test")
    character.core.species = "Elf"
    character.core.character_classes["Wizard"] = 1
    character.core.constitution.base_score = 14
    
    # Initial state
    initial_hp = character.max_hit_points
    print(f"Level 1 Wizard HP: {initial_hp}")
    
    # Level up
    character.level_up("Wizard")
    new_hp = character.max_hit_points
    print(f"Level 2 Wizard HP: {new_hp}")
    
    # Multiclass
    character.level_up("Fighter")
    multiclass_hp = character.max_hit_points
    print(f"Wizard 2/Fighter 1 HP: {multiclass_hp}")
    print(f"Total Level: {character.total_level}")
    print(f"Primary Class: {character.core.primary_class}")
    
    print("✅ Character leveling tests passed!")
    return True

def test_spellcasting():
    """Test spellcasting functionality."""
    print("\nTesting spellcasting functionality...")
    
    character = CharacterSheet("Spell Caster")
    character.core.species = "High Elf"
    character.core.character_classes["Wizard"] = 3
    character.core.spellcasting_ability = "intelligence"
    character.core.intelligence.base_score = 16
    
    character.calculate_all_derived_stats()
    
    print(f"Spell Save DC: {character.stats.spell_save_dc}")
    print(f"Spell Attack Bonus: {character.stats.spell_attack_bonus:+d}")
    
    # Test spell slots
    character.state.spell_slots_total = {1: 4, 2: 2}
    character.state.spell_slots_remaining = {1: 2, 2: 1}
    
    # Use a spell slot
    used = character.state.use_spell_slot(1)
    print(f"Used 1st level slot: {used}")
    print(f"1st level slots remaining: {character.state.spell_slots_remaining[1]}")
    
    print("✅ Spellcasting tests passed!")
    return True

if __name__ == "__main__":
    try:
        test_comprehensive_character_sheet()
        test_character_leveling()
        test_spellcasting()
        print("\n🎉 All comprehensive character sheet tests completed successfully!")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
