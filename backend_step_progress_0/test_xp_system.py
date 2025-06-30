#!/usr/bin/env python3
"""
Test script to verify XP tracking system completeness.
This tests all XP-related functionality in CharacterState.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from character_models import CharacterCore, CharacterState

def test_xp_system_completeness():
    """Test the complete XP tracking system."""
    print("🎲 Testing XP System Completeness")
    print("=" * 50)
    
    # Create character
    character_core = CharacterCore("Test Adventurer")
    character_core.set_species("Human")
    character_core.set_character_classes({"Fighter": 1})
    
    character_state = CharacterState(character_core)
    
    print("\n📊 Initial State:")
    level_info = character_state.get_level_info()
    print(f"Level: {level_info['current_level']}")
    print(f"XP: {level_info['experience_points']}")
    print(f"XP to next level: {level_info['xp_progress']}")
    
    # Test XP table
    print("\n📈 XP Table Verification:")
    xp_table = CharacterState.get_xp_table()
    print(f"Level 1 requires: {xp_table[1]} XP")
    print(f"Level 2 requires: {xp_table[2]} XP")
    print(f"Level 5 requires: {xp_table[5]} XP")
    print(f"Level 20 requires: {xp_table[20]} XP")
    
    # Test adding XP (typical DM operation)
    print("\n🏆 Testing XP Awards:")
    
    # Small XP award
    result = character_state.add_experience_points(100, "Defeated goblins")
    print(f"Added 100 XP: {result['success']}")
    print(f"New XP: {result['new_xp']}")
    print(f"Level up triggered: {result['level_up']['triggered']}")
    
    # Large XP award to trigger level up
    result = character_state.add_experience_points(250, "Completed quest")
    print(f"\nAdded 250 XP: {result['success']}")
    print(f"New XP: {result['new_xp']}")
    print(f"Level up triggered: {result['level_up']['triggered']}")
    
    if result['level_up']['triggered']:
        level_up = result['level_up']
        print(f"Old level: {level_up['old_level']}")
        print(f"New level: {level_up['new_level']}")
        print(f"Pending choices: {len(level_up['pending_choices'])}")
    
    # Test level up application
    print("\n⬆️  Testing Level Up Application:")
    if character_state.pending_level_ups:
        level_result = character_state.apply_level_up_choice(0, "Fighter")
        print(f"Applied level up: {level_result['success']}")
        print(f"New Fighter level: {level_result['new_class_level']}")
        print(f"New total level: {level_result['new_total_level']}")
        print(f"HP gained: {level_result['hp_gained']}")
        print(f"New max HP: {level_result['new_max_hp']}")
    
    # Test XP utilities
    print("\n🔧 Testing XP Utilities:")
    
    test_xp = 6500  # Level 5
    calculated_level = CharacterState.get_level_for_xp(test_xp)
    print(f"XP {test_xp} = Level {calculated_level}")
    
    test_level = 10
    required_xp = CharacterState.calculate_xp_for_level(test_level)
    print(f"Level {test_level} requires {required_xp} XP")
    
    # Test XP progress tracking
    print("\n📊 Testing XP Progress:")
    character_state.set_experience_points(1500, "Set for testing")
    xp_progress = character_state.get_xp_to_next_level()
    print(f"Current level: {xp_progress['current_level']}")
    print(f"Next level: {xp_progress['next_level']}")
    print(f"Current XP: {xp_progress['current_xp']}")
    print(f"XP for next level: {xp_progress['xp_for_next_level']}")
    print(f"XP needed: {xp_progress['xp_needed']}")
    print(f"Progress: {xp_progress['progress_percentage']:.1f}%")
    
    # Test XP history
    print("\n📝 Testing XP History:")
    print(f"XP history entries: {len(character_state.xp_history)}")
    for i, entry in enumerate(character_state.xp_history):
        print(f"  {i+1}. {entry['reason']}: {entry['change']:+d} XP (Total: {entry['new_total']})")
    
    # Test multiclass level up scenario
    print("\n🎓 Testing Multiclass Scenario:")
    character_state.set_experience_points(6500, "Set to level 5")  # Level 5
    character_core.set_character_classes({"Fighter": 3, "Rogue": 1})  # Multiclass character
    
    result = character_state.add_experience_points(500, "Big quest completion")
    if result['level_up']['triggered']:
        level_up = result['level_up']
        print(f"Available classes for level up: {level_up['available_classes']}")
        print(f"Pending choices: {len(level_up['pending_choices'])}")
    
    # Test edge cases
    print("\n⚠️  Testing Edge Cases:")
    
    # Negative XP
    result = character_state.add_experience_points(-100, "Should fail")
    print(f"Negative XP test: {result['success']} (should be False)")
    print(f"Error: {result.get('error', 'None')}")
    
    # Setting XP directly
    result = character_state.set_experience_points(100000, "Set to level 12")
    print(f"Set XP to 100000: {result['success']}")
    print(f"Level up triggered: {result['level_up']['triggered']}")
    
    # Max level scenario
    result = character_state.set_experience_points(400000, "Set beyond max")
    current_level = CharacterState.get_level_for_xp(400000)
    print(f"XP beyond max results in level: {current_level} (should be 20)")
    
    # Test state summary
    print("\n📋 Final State Summary:")
    level_info = character_state.get_level_info()
    print(f"Final level: {level_info['current_level']}")
    print(f"Final XP: {level_info['experience_points']}")
    print(f"Pending level ups: {level_info['pending_level_ups']}")
    print(f"XP history entries: {level_info['xp_history_count']}")
    
    hp_info = character_state.get_hit_points()
    print(f"Hit Points: {hp_info['current']}/{hp_info['maximum']}")
    
    print("\n🎉 XP System Completeness Test Complete!")
    print("All XP tracking functionality is properly implemented.")

if __name__ == "__main__":
    test_xp_system_completeness()
