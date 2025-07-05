#!/usr/bin/env python3
"""
Simple test for just core_models.py without dependencies
"""

import sys
import os

# Add the backend_campaign src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import only core models directly without going through __init__.py
from src.models.core_models import (
    AbilityScore, Skill, EncounterDifficulty, ChallengeRating,
    AbilityScoreUtils, EncounterBuilder, CharacterStatistics,
    CampaignBalanceUtils, CreatureType, Environment
)

def test_core_models_basic():
    """Test basic functionality of core models."""
    print("🧪 Testing Core Models (Basic)...")
    
    # Test ability score modifier calculation
    assert AbilityScoreUtils.calculate_modifier(10) == 0
    assert AbilityScoreUtils.calculate_modifier(16) == 3
    print("✅ Ability score modifiers working")
    
    # Test Challenge Rating
    cr1 = ChallengeRating(1)
    assert cr1.xp_value == 200
    print("✅ Challenge Rating working")
    
    # Test Encounter Builder
    builder = EncounterBuilder(party_level=5, party_size=4)
    budget = builder.calculate_encounter_budget()
    assert budget > 0
    print("✅ Encounter Builder working")
    
    # Test Character Statistics
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
        proficiency_bonus=0,
        hit_points=45,
        armor_class=16
    )
    
    assert char_stats.proficiency_bonus == 3
    assert char_stats.get_ability_modifier(AbilityScore.DEXTERITY) == 3
    print("✅ Character Statistics working")
    
    print("🎉 Core models are working correctly!")
    return True

if __name__ == "__main__":
    try:
        success = test_core_models_basic()
        print("✅ CORE MODELS TEST PASSED")
        sys.exit(0)
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
