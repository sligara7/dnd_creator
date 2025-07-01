#!/usr/bin/env python3
"""
Comprehensive Character Creation Test Suite

This test suite validates the primary purpose of the D&D Character Creator backend:
1. Creating new and unique characters based on user concepts (PRIMARY)
2. Updating/leveling existing characters using journal data (SECONDARY)
3. Generating NPCs (TERTIARY)
4. Generating monsters (QUATERNARY)
5. Generating individual items (FINAL)

Focus: Complete character generation with backstory, class, species, feats, 
weapons, armor, and spells while maximizing creativity through LLM assistance
and ensuring D&D 5e 2024 compatibility.
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

# Import character creation components
from creation import CharacterCreator, CreationConfig
from llm_service import create_llm_service
from creation_validation import validate_all_databases

# Test logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CharacterTestCase:
    """Test case for character creation scenarios."""
    name: str
    concept: str
    level: int
    expected_elements: Dict[str, Any]
    user_preferences: Optional[Dict[str, Any]] = None
    description: str = ""

@dataclass
class TestResult:
    """Result of a character creation test."""
    test_name: str
    success: bool
    character_data: Optional[Dict[str, Any]] = None
    validation_results: Dict[str, bool] = None
    creation_time: float = 0.0
    error_message: str = ""
    creativity_score: int = 0  # 1-10 scale
    dnd_compatibility: bool = False

class ComprehensiveCharacterCreationTest:
    """Comprehensive test suite for character creation functionality."""
    
    def __init__(self):
        self.llm_service = None
        self.character_creator = None
        self.test_results: List[TestResult] = []
        
    async def setup(self):
        """Set up test environment."""
        logger.info("Setting up comprehensive character creation test environment...")
        
        # Validate all databases first
        logger.info("Validating D&D databases...")
        if not validate_all_databases():
            raise Exception("Database validation failed - cannot proceed with character creation tests")
        logger.info("✅ All D&D databases validated successfully")
        
        # Initialize LLM service
        try:
            self.llm_service = create_llm_service()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.warning(f"⚠️ LLM service initialization failed: {e}")
            self.llm_service = None
        
        # Initialize character creator
        config = CreationConfig()
        self.character_creator = CharacterCreator(self.llm_service, config)
        logger.info("✅ Character creator initialized")
        
    def get_primary_test_cases(self) -> List[CharacterTestCase]:
        """Get primary character creation test cases covering diverse concepts."""
        return [
            # Classic D&D Archetypes
            CharacterTestCase(
                name="classic_fighter",
                concept="A noble human fighter wielding sword and shield, defender of the innocent",
                level=3,
                expected_elements={
                    "species": ["Human", "Variant Human"],
                    "classes": ["Fighter"],
                    "weapons": ["Longsword", "Sword", "Shield"],
                    "armor": ["Chain Mail", "Plate", "Armor"],
                    "alignment": ["Lawful", "Good"],
                    "backstory_themes": ["noble", "defender", "honor"]
                },
                description="Classic heroic fighter archetype with traditional D&D elements"
            ),
            
            CharacterTestCase(
                name="mysterious_wizard",
                concept="An ancient elven wizard seeking forbidden knowledge in dusty tomes",
                level=5,
                expected_elements={
                    "species": ["Elf", "High Elf"],
                    "classes": ["Wizard"],
                    "spells": ["Fireball", "Detect Magic", "Identify", "Magic Missile"],
                    "equipment": ["Spellbook", "Component Pouch", "Arcane Focus"],
                    "backstory_themes": ["ancient", "knowledge", "forbidden", "scholar"]
                },
                user_preferences={"verbose_generation": True},
                description="Classic spellcaster with focus on magical knowledge and elven longevity"
            ),
            
            # Creative and Unique Concepts
            CharacterTestCase(
                name="dragonborn_bard_chef",
                concept="A dragonborn bard who uses cooking as both art and magic, traveling between taverns",
                level=4,
                expected_elements={
                    "species": ["Dragonborn"],
                    "classes": ["Bard"],
                    "tools": ["Cook's Utensils", "Chef", "Cooking"],
                    "spells": ["Prestidigitation", "Create Food", "Goodberry"],
                    "backstory_themes": ["cooking", "tavern", "travel", "performance"]
                },
                description="Creative combination of species, class, and unique profession"
            ),
            
            CharacterTestCase(
                name="tiefling_paladin_redemption",
                concept="A tiefling paladin seeking redemption for their family's dark past through acts of heroism",
                level=6,
                expected_elements={
                    "species": ["Tiefling"],
                    "classes": ["Paladin"],
                    "alignment": ["Good", "Lawful Good"],
                    "spells": ["Divine Smite", "Cure Wounds", "Protection"],
                    "backstory_themes": ["redemption", "family", "dark past", "heroism"]
                },
                description="Narrative-rich character with internal conflict and character growth"
            ),
            
            # High-Level Complex Characters
            CharacterTestCase(
                name="multiclass_ranger_rogue",
                concept="A half-elf scout who blends nature magic with stealth, hunting down poachers",
                level=8,
                expected_elements={
                    "species": ["Half-Elf"],
                    "classes": ["Ranger", "Rogue"],
                    "skills": ["Stealth", "Survival", "Nature", "Investigation"],
                    "spells": ["Hunter's Mark", "Pass without Trace"],
                    "weapons": ["Longbow", "Shortsword"],
                    "backstory_themes": ["scout", "nature", "stealth", "poacher", "hunter"]
                },
                user_preferences={"allow_multiclass": True},
                description="Complex multiclass character with environmental theme"
            ),
            
            CharacterTestCase(
                name="high_level_warlock",
                concept="A human warlock bound to an ancient sea entity, commanding storms and tides",
                level=12,
                expected_elements={
                    "species": ["Human"],
                    "classes": ["Warlock"],
                    "spells": ["Eldritch Blast", "Hex", "Control Water", "Call Lightning"],
                    "patron": ["Fathomless", "Sea", "Ocean", "Storm"],
                    "backstory_themes": ["ancient", "sea", "entity", "storm", "tide", "bound"]
                },
                description="High-level character with unique patron relationship and elemental theme"
            ),
            
            # Exotic and Creative Concepts
            CharacterTestCase(
                name="artificer_inventor",
                concept="A gnome artificer who invents clockwork companions and magical gadgets",
                level=7,
                expected_elements={
                    "species": ["Gnome", "Rock Gnome"],
                    "classes": ["Artificer"],
                    "tools": ["Tinker's Tools", "Smith's Tools"],
                    "equipment": ["Clockwork", "Gadget", "Invention"],
                    "backstory_themes": ["inventor", "clockwork", "companion", "gadget", "tinker"]
                },
                description="Technology-focused character with crafting emphasis"
            ),
            
            CharacterTestCase(
                name="unusual_barbarian_scholar",
                concept="An orc barbarian who is secretly a brilliant philosopher and poet",
                level=5,
                expected_elements={
                    "species": ["Orc", "Half-Orc"],
                    "classes": ["Barbarian"],
                    "skills": ["Philosophy", "History", "Insight"],
                    "equipment": ["Books", "Poetry", "Journal"],
                    "backstory_themes": ["secret", "philosopher", "poet", "brilliant", "scholar"]
                },
                description="Subversive character concept challenging typical stereotypes"
            ),
            
            # Custom Content Testing
            CharacterTestCase(
                name="custom_content_character",
                concept="A unique crystal-touched sorcerer from the Shimmering Peaks who channels gem magic",
                level=9,
                expected_elements={
                    "classes": ["Sorcerer"],
                    "custom_elements": ["crystal", "gem", "Shimmering Peaks"],
                    "spells": ["Magic Missile", "Shield", "Fireball"],
                    "backstory_themes": ["crystal", "touched", "Shimmering Peaks", "gem", "magic"]
                },
                user_preferences={"allow_custom_content": True},
                description="Character requiring custom content generation for unique elements"
            )
        ]
    
    async def run_character_creation_test(self, test_case: CharacterTestCase) -> TestResult:
        """Run a single character creation test."""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧙 TESTING: {test_case.name}")
        logger.info(f"📖 CONCEPT: {test_case.concept}")
        logger.info(f"📊 LEVEL: {test_case.level}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Create character
            creation_result = await self.character_creator.create_character(
                prompt=test_case.concept,
                user_preferences=test_case.user_preferences
            )
            
            creation_time = time.time() - start_time
            
            if not creation_result.success:
                return TestResult(
                    test_name=test_case.name,
                    success=False,
                    creation_time=creation_time,
                    error_message=creation_result.error or "Unknown creation error"
                )
            
            character_data = creation_result.data
            raw_data = character_data.get("raw_data", {})
            
            logger.info(f"✅ Character created successfully in {creation_time:.2f}s")
            
            # Validate character completeness
            validation_results = self.validate_character_completeness(raw_data, test_case)
            
            # Assess creativity and D&D compatibility
            creativity_score = self.assess_creativity(raw_data, test_case)
            dnd_compatibility = self.assess_dnd_compatibility(raw_data)
            
            # Log character summary
            self.log_character_summary(raw_data, test_case.name)
            
            # Check if verbose logs were generated (for test cases that request it)
            if test_case.user_preferences and test_case.user_preferences.get("verbose_generation"):
                if hasattr(creation_result, 'verbose_logs') and creation_result.verbose_logs:
                    logger.info(f"📝 Verbose generation logs: {len(creation_result.verbose_logs)} steps")
                    for log_entry in creation_result.verbose_logs[:3]:  # Show first 3 steps
                        logger.info(f"   {log_entry.get('step', 'unknown')}: {log_entry.get('description', 'no description')}")
            
            return TestResult(
                test_name=test_case.name,
                success=True,
                character_data=character_data,
                validation_results=validation_results,
                creation_time=creation_time,
                creativity_score=creativity_score,
                dnd_compatibility=dnd_compatibility
            )
            
        except Exception as e:
            creation_time = time.time() - start_time
            logger.error(f"❌ Character creation failed: {str(e)}")
            return TestResult(
                test_name=test_case.name,
                success=False,
                creation_time=creation_time,
                error_message=str(e)
            )
    
    def validate_character_completeness(self, character_data: Dict[str, Any], test_case: CharacterTestCase) -> Dict[str, bool]:
        """Validate that the character has all required D&D 5e components."""
        validation = {
            "has_name": bool(character_data.get("name")),
            "has_species": bool(character_data.get("species")),
            "has_classes": bool(character_data.get("classes")),
            "has_background": bool(character_data.get("background")),
            "has_alignment": bool(character_data.get("alignment")),
            "has_ability_scores": bool(character_data.get("ability_scores")),
            "has_skills": bool(character_data.get("skill_proficiencies")),
            "has_backstory": bool(character_data.get("backstory")),
            "has_personality": (
                bool(character_data.get("personality_traits")) and
                bool(character_data.get("ideals")) and
                bool(character_data.get("bonds")) and
                bool(character_data.get("flaws"))
            ),
            "has_equipment": (
                bool(character_data.get("weapons")) or
                bool(character_data.get("armor")) or
                bool(character_data.get("equipment"))
            ),
            "has_feats": (
                bool(character_data.get("origin_feat")) or
                bool(character_data.get("general_feats"))
            )
        }
        
        # Check spells for spellcasters
        classes = character_data.get("classes", {})
        spellcasting_classes = ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Artificer"]
        is_spellcaster = any(cls in spellcasting_classes for cls in classes.keys())
        
        if is_spellcaster:
            validation["has_spells"] = bool(character_data.get("spells_known"))
        else:
            validation["has_spells"] = True  # Not required for non-spellcasters
        
        # Check level-appropriate content
        level = character_data.get("level", 1)
        validation["appropriate_level"] = (
            level == test_case.level and
            all(class_level <= level for class_level in classes.values())
        )
        
        return validation
    
    def assess_creativity(self, character_data: Dict[str, Any], test_case: CharacterTestCase) -> int:
        """Assess the creativity of the generated character (1-10 scale)."""
        creativity_score = 5  # Base score
        
        # Check for unique combinations
        species = character_data.get("species", "")
        classes = character_data.get("classes", {})
        primary_class = list(classes.keys())[0] if classes else ""
        
        # Bonus for unusual species-class combinations
        unusual_combinations = [
            ("Tiefling", "Paladin"), ("Orc", "Wizard"), ("Halfling", "Barbarian"),
            ("Dragonborn", "Rogue"), ("Gnome", "Barbarian"), ("Half-Orc", "Bard")
        ]
        
        if any(species in combo and primary_class in combo for combo in unusual_combinations):
            creativity_score += 2
        
        # Check backstory creativity
        backstory = character_data.get("backstory", "").lower()
        creative_backstory_elements = [
            "unique", "unusual", "secret", "hidden", "mysterious", "forbidden",
            "ancient", "lost", "cursed", "blessed", "chosen", "prophecy"
        ]
        
        backstory_creativity = sum(1 for element in creative_backstory_elements if element in backstory)
        creativity_score += min(2, backstory_creativity)
        
        # Check for custom content
        if test_case.expected_elements.get("custom_elements"):
            creativity_score += 1
        
        # Check equipment creativity
        equipment = character_data.get("equipment", {})
        tools = character_data.get("tools", [])
        
        creative_equipment = ["Cook's Utensils", "Tinker's Tools", "Artisan", "Unique", "Custom"]
        if any(item in str(equipment) + str(tools) for item in creative_equipment):
            creativity_score += 1
        
        return min(10, max(1, creativity_score))
    
    def assess_dnd_compatibility(self, character_data: Dict[str, Any]) -> bool:
        """Assess if the character is compatible with D&D 5e 2024 rules."""
        try:
            # Check ability scores are in valid range
            ability_scores = character_data.get("ability_scores", {})
            required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            
            for ability in required_abilities:
                if ability not in ability_scores:
                    return False
                score = ability_scores[ability]
                if not isinstance(score, int) or score < 3 or score > 20:
                    return False
            
            # Check classes exist and have valid levels
            classes = character_data.get("classes", {})
            if not classes:
                return False
            
            valid_classes = [
                "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
                "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard", "Artificer"
            ]
            
            for class_name, level in classes.items():
                if class_name not in valid_classes or not isinstance(level, int) or level < 1 or level > 20:
                    return False
            
            # Check alignment format
            alignment = character_data.get("alignment", [])
            if not isinstance(alignment, list) or len(alignment) != 2:
                return False
            
            valid_ethics = ["Lawful", "Neutral", "Chaotic"]
            valid_morals = ["Good", "Neutral", "Evil"]
            
            if alignment[0] not in valid_ethics or alignment[1] not in valid_morals:
                return False
            
            # Check species is valid
            species = character_data.get("species", "")
            valid_species = [
                "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome",
                "Half-Elf", "Half-Orc", "Tiefling", "Aasimar", "Goliath", "Tabaxi"
            ]
            
            if not any(valid_sp in species for valid_sp in valid_species):
                return False
            
            return True
            
        except Exception:
            return False
    
    def log_character_summary(self, character_data: Dict[str, Any], test_name: str):
        """Log a summary of the created character."""
        name = character_data.get("name", "Unnamed")
        species = character_data.get("species", "Unknown")
        classes = character_data.get("classes", {})
        level = character_data.get("level", 1)
        background = character_data.get("background", "Unknown")
        
        logger.info(f"📋 CHARACTER SUMMARY for {test_name}:")
        logger.info(f"   Name: {name}")
        logger.info(f"   Species: {species}")
        logger.info(f"   Classes: {classes}")
        logger.info(f"   Level: {level}")
        logger.info(f"   Background: {background}")
        
        # Log key equipment
        weapons = character_data.get("weapons", [])
        if weapons:
            weapon_names = [w.get("name", str(w)) for w in weapons[:3]]
            logger.info(f"   Weapons: {', '.join(weapon_names)}")
        
        armor = character_data.get("armor", "")
        if armor:
            logger.info(f"   Armor: {armor}")
        
        # Log spells if applicable
        spells = character_data.get("spells_known", [])
        if spells:
            spell_names = [s.get("name", str(s)) for s in spells[:5]]
            logger.info(f"   Spells: {', '.join(spell_names)}")
        
        # Log feats
        origin_feat = character_data.get("origin_feat", "")
        general_feats = character_data.get("general_feats", [])
        if origin_feat or general_feats:
            feat_list = [origin_feat] if origin_feat else []
            feat_list.extend([f.get("name", str(f)) for f in general_feats[:2]])
            logger.info(f"   Feats: {', '.join(feat_list)}")
    
    async def run_all_tests(self):
        """Run all character creation tests."""
        logger.info("🚀 Starting Comprehensive Character Creation Test Suite")
        logger.info("=" * 80)
        
        test_cases = self.get_primary_test_cases()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📊 PROGRESS: Test {i}/{len(test_cases)}")
            
            result = await self.run_character_creation_test(test_case)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate comprehensive report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE CHARACTER CREATION TEST REPORT")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        logger.info(f"📈 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        logger.info(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        if successful_tests > 0:
            avg_creation_time = sum(r.creation_time for r in self.test_results if r.success) / successful_tests
            avg_creativity = sum(r.creativity_score for r in self.test_results if r.success) / successful_tests
            compatible_characters = len([r for r in self.test_results if r.success and r.dnd_compatibility])
            
            logger.info(f"   Average Creation Time: {avg_creation_time:.2f}s")
            logger.info(f"   Average Creativity Score: {avg_creativity:.1f}/10")
            logger.info(f"   D&D Compatible: {compatible_characters}/{successful_tests} ({compatible_characters/successful_tests*100:.1f}%)")
        
        # Detailed results
        logger.info(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            logger.info(f"   {status} {result.test_name}")
            
            if result.success:
                logger.info(f"      Time: {result.creation_time:.2f}s | Creativity: {result.creativity_score}/10 | D&D Compatible: {'Yes' if result.dnd_compatibility else 'No'}")
                
                if result.validation_results:
                    failed_validations = [k for k, v in result.validation_results.items() if not v]
                    if failed_validations:
                        logger.info(f"      Missing: {', '.join(failed_validations)}")
            else:
                logger.info(f"      Error: {result.error_message}")
        
        # Recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        
        if failed_tests > 0:
            logger.info(f"   - Investigate {failed_tests} failed character creations")
        
        if successful_tests > 0:
            low_creativity = len([r for r in self.test_results if r.success and r.creativity_score < 5])
            if low_creativity > 0:
                logger.info(f"   - Enhance creativity in {low_creativity} character(s) with low scores")
            
            incompatible = len([r for r in self.test_results if r.success and not r.dnd_compatibility])
            if incompatible > 0:
                logger.info(f"   - Fix D&D compatibility issues in {incompatible} character(s)")
            
            slow_tests = len([r for r in self.test_results if r.success and r.creation_time > 10])
            if slow_tests > 0:
                logger.info(f"   - Optimize performance for {slow_tests} slow character creation(s)")
        
        logger.info("\n🎯 CHARACTER CREATION TEST SUITE COMPLETE")
        logger.info("=" * 80)

async def main():
    """Main test execution function."""
    logger.info("🧙‍♂️ D&D Character Creator - Comprehensive Test Suite")
    logger.info("Testing primary functionality: Complete character generation")
    
    test_suite = ComprehensiveCharacterCreationTest()
    
    try:
        await test_suite.setup()
        await test_suite.run_all_tests()
        
        # Return success code based on results
        successful_tests = len([r for r in test_suite.test_results if r.success])
        total_tests = len(test_suite.test_results)
        
        if successful_tests == total_tests:
            logger.info("🎉 ALL TESTS PASSED!")
            return 0
        elif successful_tests > total_tests * 0.8:
            logger.info("⚠️ MOST TESTS PASSED - Some issues to investigate")
            return 1
        else:
            logger.error("❌ MANY TESTS FAILED - Significant issues need attention")
            return 2
            
    except Exception as e:
        logger.error(f"💥 Test suite failed to run: {e}")
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
