#!/usr/bin/env python3
"""
Direct test for core_models.py implementation
"""

import sys
import os

# Add the backend_campaign src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Import directly from core_models module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'models'))

if __name__ == "__main__":
    try:
        # Import core_models directly
        import core_models
        
        # Test ability score modifier calculation
        assert core_models.AbilityScoreUtils.calculate_modifier(10) == 0
        assert core_models.AbilityScoreUtils.calculate_modifier(16) == 3
        print("✅ Ability score modifiers working")
        
        # Test Challenge Rating
        cr1 = core_models.ChallengeRating(1)
        assert cr1.xp_value == 200
        print("✅ Challenge Rating working")
        
        # Test Encounter Builder
        builder = core_models.EncounterBuilder(party_level=5, party_size=4)
        budget = builder.calculate_encounter_budget()
        assert budget > 0
        print("✅ Encounter Builder working")
        
        # Test Character Statistics
        abilities = {
            core_models.AbilityScore.STRENGTH: 14,
            core_models.AbilityScore.DEXTERITY: 16, 
            core_models.AbilityScore.CONSTITUTION: 13,
            core_models.AbilityScore.INTELLIGENCE: 12,
            core_models.AbilityScore.WISDOM: 15,
            core_models.AbilityScore.CHARISMA: 10
        }
        
        char_stats = core_models.CharacterStatistics(
            level=5,
            ability_scores=abilities,
            proficiency_bonus=0,
            hit_points=45,
            armor_class=16
        )
        
        assert char_stats.proficiency_bonus == 3
        assert char_stats.get_ability_modifier(core_models.AbilityScore.DEXTERITY) == 3
        print("✅ Character Statistics working")
        
        # Test Campaign Balance Utils
        session_xp = core_models.CampaignBalanceUtils.calculate_session_xp_budget(5, 4)
        assert session_xp > 0
        print("✅ Campaign Balance Utils working")
        
        print("🎉 ALL CORE MODELS TESTS PASSED!")
        print("📋 Validated:")
        print("   ✅ Ability Score Utilities")
        print("   ✅ Challenge Rating System")
        print("   ✅ Encounter Builder")
        print("   ✅ Character Statistics")
        print("   ✅ Campaign Balance Utilities")
        
    except Exception as e:
        print(f"❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
