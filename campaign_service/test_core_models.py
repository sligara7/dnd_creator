#!/usr/bin/env python3
"""
Test script for Core Models in Campaign Creation Backend
========================================================

This script validates the new core_models.py implementation for campaign creation,
including D&D mechanics, encounter building, and campaign balance utilities.
"""

import sys
import os

# Add the backend_campaign src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.models.core_models import (
    AbilityScore, Skill, EncounterDifficulty, ChallengeRating,
    AbilityScoreUtils, EncounterBuilder, CharacterStatistics,
    CampaignBalanceUtils, CreatureType, Environment
)

def test_ability_scores():
    """Test ability score utilities."""
    print("🧪 Testing Ability Score Utilities...")
    
    # Test modifier calculation
    assert AbilityScoreUtils.calculate_modifier(10) == 0
    assert AbilityScoreUtils.calculate_modifier(8) == -1
    assert AbilityScoreUtils.calculate_modifier(16) == 3
    assert AbilityScoreUtils.calculate_modifier(20) == 5
    
    # Test standard array generation
    standard_array = AbilityScoreUtils.generate_standard_array()
    assert len(standard_array) == 6
    assert all(isinstance(score, int) and 8 <= score <= 15 for score in standard_array.values())
    
    print("✅ Ability Score Utilities: PASSED")

def test_challenge_rating():
    """Test Challenge Rating system."""
    print("🧪 Testing Challenge Rating System...")
    
    # Test CR creation and XP mapping
    cr1 = ChallengeRating(1)
    assert cr1.xp_value == 200
    
    cr_half = ChallengeRating(0.5)
    assert cr_half.xp_value == 100
    
    # Test XP to CR conversion
    cr_from_xp = ChallengeRating.from_xp(450)
    assert cr_from_xp.value == 2  # Closest to 450 XP
    
    # Test party level recommendations
    party_crs = ChallengeRating.for_party_level(5, EncounterDifficulty.MEDIUM, 4)
    assert len(party_crs) > 0
    assert all(isinstance(cr.value, (int, float)) for cr in party_crs)
    
    print("✅ Challenge Rating System: PASSED")

def test_encounter_builder():
    """Test encounter building system."""
    print("🧪 Testing Encounter Builder...")
    
    # Test basic encounter building
    builder = EncounterBuilder(party_level=5, party_size=4, target_difficulty=EncounterDifficulty.MEDIUM)
    
    # Test budget calculation
    budget = builder.calculate_encounter_budget()
    assert budget > 0
    
    # Test single monster suggestion
    single_monster = builder.suggest_single_monster()
    assert len(single_monster) == 1
    assert isinstance(single_monster[0], ChallengeRating)
    
    # Test group encounter suggestion  
    group_monsters = builder.suggest_monster_group(3)
    assert len(group_monsters) == 3
    assert all(isinstance(cr, ChallengeRating) for cr in group_monsters)
    
    # Test encounter validation
    validation = builder.validate_encounter([ChallengeRating(2), ChallengeRating(1)])
    assert 'total_base_xp' in validation
    assert 'adjusted_xp' in validation
    assert 'actual_difficulty' in validation
    assert 'party_thresholds' in validation
    
    print("✅ Encounter Builder: PASSED")

def test_character_statistics():
    """Test character statistics system."""
    print("🧪 Testing Character Statistics...")
    
    # Create test character
    abilities = {
        AbilityScore.STRENGTH: 14,
        AbilityScore.DEXTERITY: 16, 
        AbilityScore.CONSTITUTION: 13,
        AbilityScore.INTELLIGENCE: 12,
        AbilityScore.WISDOM: 15,
        AbilityScore.CHARISMA: 10
    }
    
    char_stats = CharacterStatistics(
        level=5,
        ability_scores=abilities,
        proficiency_bonus=0,  # Will be calculated
        hit_points=45,
        armor_class=16,
        saving_throw_proficiencies=[AbilityScore.DEXTERITY, AbilityScore.WISDOM],
        skill_proficiencies=[Skill.STEALTH, Skill.PERCEPTION]
    )
    
    # Test proficiency bonus calculation
    assert char_stats.proficiency_bonus == 3  # Level 5
    
    # Test ability modifiers
    assert char_stats.get_ability_modifier(AbilityScore.DEXTERITY) == 3
    assert char_stats.get_ability_modifier(AbilityScore.STRENGTH) == 2
    
    # Test saving throws
    dex_save = char_stats.get_saving_throw_bonus(AbilityScore.DEXTERITY)
    assert dex_save == 6  # 3 (mod) + 3 (proficiency)
    
    str_save = char_stats.get_saving_throw_bonus(AbilityScore.STRENGTH)
    assert str_save == 2  # 2 (mod) + 0 (no proficiency)
    
    # Test skill checks
    stealth_bonus = char_stats.get_skill_bonus(Skill.STEALTH)
    assert stealth_bonus == 6  # 3 (dex mod) + 3 (proficiency)
    
    athletics_bonus = char_stats.get_skill_bonus(Skill.ATHLETICS)
    assert athletics_bonus == 2  # 2 (str mod) + 0 (no proficiency)
    
    # Test combat effectiveness
    effectiveness = char_stats.calculate_combat_effectiveness()
    assert 'offensive' in effectiveness
    assert 'defensive' in effectiveness
    assert 'utility' in effectiveness
    assert 'overall' in effectiveness
    
    print("✅ Character Statistics: PASSED")

def test_campaign_balance_utils():
    """Test campaign balance utilities."""
    print("🧪 Testing Campaign Balance Utilities...")
    
    # Test session XP budget calculation
    session_xp = CampaignBalanceUtils.calculate_session_xp_budget(
        party_level=5, party_size=4, session_length_hours=4.0
    )
    assert session_xp > 0
    
    # Test encounter mix suggestions
    encounter_mix = CampaignBalanceUtils.suggest_encounter_mix(
        total_xp_budget=session_xp,
        party_level=5,
        party_size=4
    )
    
    assert len(encounter_mix) >= 3  # Should have multiple encounters
    assert all('type' in enc for enc in encounter_mix)
    assert all('difficulty' in enc for enc in encounter_mix)
    assert all('xp_budget' in enc for enc in encounter_mix)
    assert all('suggested_cr' in enc for enc in encounter_mix)
    
    # Verify budget distribution
    total_budget_used = sum(enc['xp_budget'] for enc in encounter_mix)
    assert abs(total_budget_used - session_xp) <= session_xp * 0.1  # Within 10%
    
    print("✅ Campaign Balance Utilities: PASSED")

def test_enums_and_constants():
    """Test that all enums and constants are properly defined."""
    print("🧪 Testing Enums and Constants...")
    
    # Test ability scores
    assert len(AbilityScore) == 6
    assert AbilityScore.STRENGTH in AbilityScore
    
    # Test skills
    assert len(Skill) >= 18  # Should have all core D&D skills
    assert Skill.PERCEPTION in Skill
    
    # Test creature types
    assert CreatureType.HUMANOID in CreatureType
    assert CreatureType.DRAGON in CreatureType
    
    # Test environments
    assert Environment.DUNGEON in Environment
    assert Environment.FOREST in Environment
    
    # Test encounter difficulties
    assert EncounterDifficulty.MEDIUM in EncounterDifficulty
    assert EncounterDifficulty.DEADLY in EncounterDifficulty
    
    print("✅ Enums and Constants: PASSED")

def test_integration_examples():
    """Test integration examples showing how models work together."""
    print("🧪 Testing Integration Examples...")
    
    # Example: Create a balanced encounter for a 5th level party
    party_level = 5
    party_size = 4
    
    # Build encounter
    encounter_builder = EncounterBuilder(
        party_level=party_level,
        party_size=party_size,
        target_difficulty=EncounterDifficulty.HARD
    )
    
    # Get recommended monsters
    single_monster_cr = encounter_builder.suggest_single_monster()[0]
    group_monster_crs = encounter_builder.suggest_monster_group(2)
    
    # Validate both encounters
    single_validation = encounter_builder.validate_encounter([single_monster_cr])
    group_validation = encounter_builder.validate_encounter(group_monster_crs)
    
    assert single_validation['actual_difficulty'] in [EncounterDifficulty.MEDIUM, EncounterDifficulty.HARD, EncounterDifficulty.DEADLY]
    assert group_validation['actual_difficulty'] in [EncounterDifficulty.MEDIUM, EncounterDifficulty.HARD, EncounterDifficulty.DEADLY]
    
    # Example: Calculate NPC statistics
    npc_abilities = AbilityScoreUtils.generate_standard_array()
    npc_stats = CharacterStatistics(
        level=3,
        ability_scores=npc_abilities,
        proficiency_bonus=0,
        hit_points=22,
        armor_class=14
    )
    
    assert npc_stats.proficiency_bonus == 2  # Level 3
    effectiveness = npc_stats.calculate_combat_effectiveness()
    assert all(isinstance(val, (int, float)) for val in effectiveness.values())
    
    print("✅ Integration Examples: PASSED")

def run_all_tests():
    """Run all tests and report results."""
    print("🚀 Starting Core Models Test Suite...")
    print("=" * 60)
    
    try:
        test_ability_scores()
        test_challenge_rating()
        test_encounter_builder()
        test_character_statistics()
        test_campaign_balance_utils()
        test_enums_and_constants()
        test_integration_examples()
        
        print("=" * 60)
        print("🎉 ALL TESTS PASSED! Core models are working correctly.")
        print("📋 Summary:")
        print("   ✅ Ability Score Utilities")
        print("   ✅ Challenge Rating System")
        print("   ✅ Encounter Builder")
        print("   ✅ Character Statistics")
        print("   ✅ Campaign Balance Utilities") 
        print("   ✅ Enums and Constants")
        print("   ✅ Integration Examples")
        print()
        print("🔧 Core models are ready for campaign creation backend!")
        
        return True
        
    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
