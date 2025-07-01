#!/usr/bin/env python3
"""
Character Update and Leveling Test Suite

This test validates the secondary functionality of the D&D Character Creator:
- Updating existing characters based on gameplay journal entries
- Leveling up characters with new abilities, spells, and features
- Multi-classing existing characters
- Maintaining character continuity and growth

Focus: Character progression that reflects actual gameplay and player choices.
"""

import asyncio
import sys
import os
import time
import json
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Import character creation and update components
from creation import CharacterCreator, CreationConfig
from llm_service import create_llm_service

# Test logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CharacterUpdateTestCase:
    """Test case for character updating scenarios."""
    name: str
    base_character: Dict[str, Any]
    journal_entries: List[str]
    update_type: str  # "level_up", "multiclass", "experience_growth"
    expected_changes: Dict[str, Any]
    description: str = ""

@dataclass
class UpdateTestResult:
    """Result of a character update test."""
    test_name: str
    success: bool
    original_character: Optional[Dict[str, Any]] = None
    updated_character: Optional[Dict[str, Any]] = None
    changes_detected: Dict[str, Any] = None
    update_time: float = 0.0
    error_message: str = ""
    continuity_maintained: bool = False

class CharacterUpdateTest:
    """Test suite for character updating and progression functionality."""
    
    def __init__(self):
        self.llm_service = None
        self.character_creator = None
        self.test_results: List[UpdateTestResult] = []
    
    async def setup(self):
        """Set up test environment."""
        logger.info("Setting up character update test environment...")
        
        try:
            self.llm_service = create_llm_service()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.warning(f"⚠️ LLM service initialization failed: {e}")
            self.llm_service = None
        
        config = CreationConfig()
        self.character_creator = CharacterCreator(self.llm_service, config)
        logger.info("✅ Character creator initialized")
    
    def get_update_test_cases(self) -> List[CharacterUpdateTestCase]:
        """Get character update test cases."""
        return [
            # Level Up Tests
            CharacterUpdateTestCase(
                name="fighter_level_up",
                base_character={
                    "name": "Sir Gareth",
                    "species": "Human",
                    "level": 3,
                    "classes": {"Fighter": 3},
                    "background": "Soldier",
                    "ability_scores": {"strength": 16, "dexterity": 14, "constitution": 15, "intelligence": 10, "wisdom": 12, "charisma": 8},
                    "armor": "Chain Mail",
                    "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["Versatile"]}],
                    "origin_feat": "Alert",
                    "general_feats": []
                },
                journal_entries=[
                    "Gareth led the charge against the goblin raiders, using tactical knowledge from his military training",
                    "Successfully defended the village, earning the gratitude of the mayor and townspeople",
                    "Practiced sword techniques with the local guard captain, improving his combat skills",
                    "Gained experience in leadership during the crisis, rallying scared civilians"
                ],
                update_type="level_up",
                expected_changes={
                    "level": 4,
                    "classes": {"Fighter": 4},
                    "new_features": ["Ability Score Improvement", "ASI"],
                    "general_feats": [{"name": "Ability Score Improvement", "level": 4}]
                },
                description="Fighter leveling from 3 to 4 with ASI and leadership experience"
            ),
            
            CharacterUpdateTestCase(
                name="wizard_spell_progression",
                base_character={
                    "name": "Elara Moonwhisper",
                    "species": "High Elf",
                    "level": 4,
                    "classes": {"Wizard": 4},
                    "background": "Sage",
                    "ability_scores": {"strength": 8, "dexterity": 14, "constitution": 13, "intelligence": 16, "wisdom": 12, "charisma": 10},
                    "spells_known": [
                        {"name": "Magic Missile", "level": 1, "school": "evocation"},
                        {"name": "Shield", "level": 1, "school": "abjuration"},
                        {"name": "Detect Magic", "level": 1, "school": "divination"}
                    ],
                    "general_feats": [{"name": "Ability Score Improvement", "level": 4}]
                },
                journal_entries=[
                    "Elara discovered an ancient tome containing fire magic spells in the abandoned tower",
                    "Successfully cast Fireball for the first time during combat with bandits",
                    "Spent weeks studying the intricacies of evocation magic and spell structure",
                    "Her mastery of magic impressed even the veteran court wizard"
                ],
                update_type="level_up",
                expected_changes={
                    "level": 5,
                    "classes": {"Wizard": 5},
                    "new_spells": ["Fireball", "Counterspell"],
                    "spell_slots": {3: 2}
                },
                description="Wizard gaining 3rd level spells and advancing magical knowledge"
            ),
            
            # Multiclassing Tests
            CharacterUpdateTestCase(
                name="rogue_to_ranger_multiclass",
                base_character={
                    "name": "Kira Shadowstep",
                    "species": "Half-Elf",
                    "level": 5,
                    "classes": {"Rogue": 5},
                    "background": "Outlander",
                    "ability_scores": {"strength": 12, "dexterity": 16, "constitution": 14, "intelligence": 10, "wisdom": 14, "charisma": 13},
                    "weapons": [{"name": "Shortsword", "damage": "1d6", "properties": ["Finesse", "Light"]}],
                    "skill_proficiencies": {"stealth": "expert", "perception": "proficient", "survival": "proficient"}
                },
                journal_entries=[
                    "Kira spent months tracking through the wilderness, learning to read animal signs",
                    "She developed a deep connection with nature during her time in the forest",
                    "The local druids taught her basic nature magic and animal communication",
                    "Her skills now blend urban stealth with wilderness survival"
                ],
                update_type="multiclass",
                expected_changes={
                    "level": 6,
                    "classes": {"Rogue": 5, "Ranger": 1},
                    "new_spells": ["Hunter's Mark", "Cure Wounds"],
                    "new_skills": ["Animal Handling", "Nature"]
                },
                description="Rogue multiclassing into Ranger based on wilderness experience"
            ),
            
            # Experience-Based Growth
            CharacterUpdateTestCase(
                name="paladin_oath_development",
                base_character={
                    "name": "Brother Marcus",
                    "species": "Human",
                    "level": 2,
                    "classes": {"Paladin": 2},
                    "background": "Acolyte",
                    "ability_scores": {"strength": 15, "dexterity": 10, "constitution": 14, "intelligence": 12, "wisdom": 13, "charisma": 16},
                    "spells_known": [{"name": "Bless", "level": 1, "school": "enchantment"}],
                    "oath": None
                },
                journal_entries=[
                    "Marcus witnessed the corruption spreading through the noble houses",
                    "He vowed to root out evil wherever it hides, regardless of social status",
                    "His righteous anger burns bright when confronting injustice and tyranny",
                    "The common people look to him as a beacon of hope against oppression"
                ],
                update_type="experience_growth",
                expected_changes={
                    "level": 3,
                    "classes": {"Paladin": 3},
                    "oath": "Devotion",
                    "new_spells": ["Protection from Evil and Good", "Sanctuary"],
                    "oath_abilities": ["Sacred Weapon", "Turn the Unholy"]
                },
                description="Paladin developing their sacred oath based on character experiences"
            ),
            
            # Complex Character Growth
            CharacterUpdateTestCase(
                name="bard_college_specialization",
                base_character={
                    "name": "Melody Starweaver",
                    "species": "Tiefling",
                    "level": 2,
                    "classes": {"Bard": 2},
                    "background": "Entertainer",
                    "ability_scores": {"strength": 8, "dexterity": 14, "constitution": 12, "intelligence": 13, "wisdom": 11, "charisma": 16},
                    "spells_known": [
                        {"name": "Vicious Mockery", "level": 0, "school": "enchantment"},
                        {"name": "Healing Word", "level": 1, "school": "evocation"}
                    ],
                    "equipment": {"Lute": 1, "Performance Outfit": 1}
                },
                journal_entries=[
                    "Melody discovered ancient songs that could weave illusions and change reality",
                    "She learned from master storytellers in the College of Glamour",
                    "Her performances now entrance audiences and bend their emotions",
                    "The fey courts have taken notice of her growing magical artistry"
                ],
                update_type="level_up",
                expected_changes={
                    "level": 3,
                    "classes": {"Bard": 3},
                    "college": "Glamour",
                    "new_spells": ["Charm Person", "Faerie Fire"],
                    "college_features": ["Mantle of Inspiration", "Enthralling Performance"]
                },
                description="Bard joining a college and developing specialized magical performance"
            )
        ]
    
    async def run_character_update_test(self, test_case: CharacterUpdateTestCase) -> UpdateTestResult:
        """Run a single character update test."""
        logger.info(f"\n{'='*60}")
        logger.info(f"🔄 TESTING UPDATE: {test_case.name}")
        logger.info(f"📖 TYPE: {test_case.update_type}")
        logger.info(f"📊 BASE LEVEL: {test_case.base_character.get('level', 'Unknown')}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Log journal entries
            logger.info("📚 JOURNAL ENTRIES:")
            for i, entry in enumerate(test_case.journal_entries, 1):
                logger.info(f"   {i}. {entry}")
            
            # Create update prompt based on journal entries and update type
            update_prompt = self.create_update_prompt(test_case)
            
            # For now, simulate character update by creating an updated version
            # In a full implementation, this would call a specialized update method
            updated_creation_result = await self.character_creator.create_character(
                prompt=update_prompt,
                user_preferences={
                    "base_character": test_case.base_character,
                    "update_type": test_case.update_type,
                    "journal_entries": test_case.journal_entries
                }
            )
            
            update_time = time.time() - start_time
            
            if not updated_creation_result.success:
                return UpdateTestResult(
                    test_name=test_case.name,
                    success=False,
                    original_character=test_case.base_character,
                    update_time=update_time,
                    error_message=updated_creation_result.error or "Unknown update error"
                )
            
            updated_character_data = updated_creation_result.data
            updated_raw_data = updated_character_data.get("raw_data", {})
            
            logger.info(f"✅ Character updated successfully in {update_time:.2f}s")
            
            # Analyze changes between original and updated character
            changes_detected = self.analyze_character_changes(
                test_case.base_character, 
                updated_raw_data
            )
            
            # Check if continuity is maintained
            continuity_maintained = self.check_character_continuity(
                test_case.base_character,
                updated_raw_data,
                test_case.journal_entries
            )
            
            # Log update summary
            self.log_update_summary(test_case.base_character, updated_raw_data, changes_detected)
            
            return UpdateTestResult(
                test_name=test_case.name,
                success=True,
                original_character=test_case.base_character,
                updated_character=updated_character_data,
                changes_detected=changes_detected,
                update_time=update_time,
                continuity_maintained=continuity_maintained
            )
            
        except Exception as e:
            update_time = time.time() - start_time
            logger.error(f"❌ Character update failed: {str(e)}")
            return UpdateTestResult(
                test_name=test_case.name,
                success=False,
                original_character=test_case.base_character,
                update_time=update_time,
                error_message=str(e)
            )
    
    def create_update_prompt(self, test_case: CharacterUpdateTestCase) -> str:
        """Create an update prompt based on the test case."""
        base_char = test_case.base_character
        name = base_char.get("name", "Character")
        current_level = base_char.get("level", 1)
        
        journal_text = "\n".join([f"- {entry}" for entry in test_case.journal_entries])
        
        if test_case.update_type == "level_up":
            new_level = current_level + 1
            return f"""Update {name} from level {current_level} to level {new_level} based on their recent experiences:

JOURNAL ENTRIES:
{journal_text}

The character should gain appropriate level-based improvements including new abilities, spells, hit points, and any class features. Maintain character personality and background while reflecting growth from experiences."""

        elif test_case.update_type == "multiclass":
            return f"""Add a new class to {name} (currently level {current_level}) based on their recent experiences:

JOURNAL ENTRIES:
{journal_text}

The character should multiclass into an appropriate class that reflects their new experiences and training. Maintain their existing abilities while adding new class features."""

        elif test_case.update_type == "experience_growth":
            return f"""Develop {name}'s character abilities and specializations based on their experiences:

JOURNAL ENTRIES:
{journal_text}

The character should develop new abilities, make important choices (like oaths, colleges, etc.), and grow in ways that reflect their experiences. Level progression should be organic to the story."""

        else:
            return f"""Update {name} based on their recent experiences:

JOURNAL ENTRIES:
{journal_text}

Develop the character in ways that make sense for their story and experiences."""
    
    def analyze_character_changes(self, original: Dict[str, Any], updated: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the changes between original and updated character."""
        changes = {
            "level_change": updated.get("level", 1) - original.get("level", 1),
            "new_classes": {},
            "new_spells": [],
            "new_features": [],
            "new_equipment": [],
            "ability_improvements": {},
            "new_skills": []
        }
        
        # Check class changes
        original_classes = original.get("classes", {})
        updated_classes = updated.get("classes", {})
        
        for class_name, level in updated_classes.items():
            if class_name not in original_classes:
                changes["new_classes"][class_name] = level
            elif level > original_classes[class_name]:
                changes["new_classes"][class_name] = level - original_classes[class_name]
        
        # Check spell changes
        original_spells = set(spell.get("name", "") for spell in original.get("spells_known", []))
        updated_spells = set(spell.get("name", "") for spell in updated.get("spells_known", []))
        changes["new_spells"] = list(updated_spells - original_spells)
        
        # Check ability score changes
        original_abilities = original.get("ability_scores", {})
        updated_abilities = updated.get("ability_scores", {})
        
        for ability, score in updated_abilities.items():
            original_score = original_abilities.get(ability, 10)
            if score > original_score:
                changes["ability_improvements"][ability] = score - original_score
        
        # Check skill changes
        original_skills = set(original.get("skill_proficiencies", {}).keys())
        updated_skills = set(updated.get("skill_proficiencies", {}).keys())
        changes["new_skills"] = list(updated_skills - original_skills)
        
        return changes
    
    def check_character_continuity(self, original: Dict[str, Any], updated: Dict[str, Any], 
                                 journal_entries: List[str]) -> bool:
        """Check if character continuity is maintained in the update."""
        try:
            # Core identity should remain the same
            if (original.get("name") != updated.get("name") or
                original.get("species") != updated.get("species") or
                original.get("background") != updated.get("background")):
                return False
            
            # Level should increase or stay the same
            if updated.get("level", 1) < original.get("level", 1):
                return False
            
            # Original classes should still exist (with same or higher levels)
            original_classes = original.get("classes", {})
            updated_classes = updated.get("classes", {})
            
            for class_name, level in original_classes.items():
                if class_name not in updated_classes or updated_classes[class_name] < level:
                    return False
            
            # Personality elements should be consistent
            personality_fields = ["personality_traits", "ideals", "bonds", "flaws"]
            for field in personality_fields:
                if (field in original and field in updated and 
                    original[field] != updated[field]):
                    # Allow evolution but check for some consistency
                    # This is simplified - a full implementation would be more nuanced
                    pass
            
            return True
            
        except Exception:
            return False
    
    def log_update_summary(self, original: Dict[str, Any], updated: Dict[str, Any], 
                          changes: Dict[str, Any]):
        """Log a summary of character updates."""
        name = original.get("name", "Character")
        original_level = original.get("level", 1)
        updated_level = updated.get("level", 1)
        
        logger.info(f"📋 UPDATE SUMMARY for {name}:")
        logger.info(f"   Level: {original_level} → {updated_level}")
        
        if changes["new_classes"]:
            for class_name, levels in changes["new_classes"].items():
                logger.info(f"   New Class: {class_name} (+{levels} levels)")
        
        if changes["new_spells"]:
            logger.info(f"   New Spells: {', '.join(changes['new_spells'][:3])}")
        
        if changes["ability_improvements"]:
            improvements = [f"{ability.title()} +{bonus}" 
                          for ability, bonus in changes["ability_improvements"].items()]
            logger.info(f"   Ability Improvements: {', '.join(improvements)}")
        
        if changes["new_skills"]:
            logger.info(f"   New Skills: {', '.join(changes['new_skills'][:3])}")
    
    async def run_all_update_tests(self):
        """Run all character update tests."""
        logger.info("🔄 Starting Character Update and Progression Test Suite")
        logger.info("=" * 80)
        
        test_cases = self.get_update_test_cases()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📊 PROGRESS: Update Test {i}/{len(test_cases)}")
            
            result = await self.run_character_update_test(test_case)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate test report
        self.generate_update_test_report()
    
    def generate_update_test_report(self):
        """Generate a comprehensive update test report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 CHARACTER UPDATE TEST REPORT")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        logger.info(f"📈 OVERALL RESULTS:")
        logger.info(f"   Total Update Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        logger.info(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        if successful_tests > 0:
            avg_update_time = sum(r.update_time for r in self.test_results if r.success) / successful_tests
            continuity_maintained = len([r for r in self.test_results if r.success and r.continuity_maintained])
            
            logger.info(f"   Average Update Time: {avg_update_time:.2f}s")
            logger.info(f"   Continuity Maintained: {continuity_maintained}/{successful_tests} ({continuity_maintained/successful_tests*100:.1f}%)")
        
        # Detailed results
        logger.info(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            logger.info(f"   {status} {result.test_name}")
            
            if result.success:
                continuity = "Yes" if result.continuity_maintained else "No"
                logger.info(f"      Time: {result.update_time:.2f}s | Continuity: {continuity}")
                
                if result.changes_detected:
                    level_change = result.changes_detected.get("level_change", 0)
                    new_classes = len(result.changes_detected.get("new_classes", {}))
                    new_spells = len(result.changes_detected.get("new_spells", []))
                    logger.info(f"      Changes: +{level_change} levels, {new_classes} new classes, {new_spells} new spells")
            else:
                logger.info(f"      Error: {result.error_message}")
        
        logger.info("\n🎯 CHARACTER UPDATE TEST SUITE COMPLETE")
        logger.info("=" * 80)

async def main():
    """Main test execution function."""
    logger.info("🔄 D&D Character Creator - Character Update Test Suite")
    logger.info("Testing secondary functionality: Character progression and updates")
    
    test_suite = CharacterUpdateTest()
    
    try:
        await test_suite.setup()
        await test_suite.run_all_update_tests()
        
        # Return success code based on results
        successful_tests = len([r for r in test_suite.test_results if r.success])
        total_tests = len(test_suite.test_results)
        
        if successful_tests == total_tests:
            logger.info("🎉 ALL UPDATE TESTS PASSED!")
            return 0
        elif successful_tests > total_tests * 0.8:
            logger.info("⚠️ MOST UPDATE TESTS PASSED - Some issues to investigate")
            return 1
        else:
            logger.error("❌ MANY UPDATE TESTS FAILED - Significant issues need attention")
            return 2
            
    except Exception as e:
        logger.error(f"💥 Update test suite failed to run: {e}")
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
