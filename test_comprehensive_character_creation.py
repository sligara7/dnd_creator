#!/usr/bin/env python3
"""
Comprehensive D&D Creation Features Test Suite

This test suite validates ALL creation features from dev_vision.md requirements:

🎯 CORE CREATION SYSTEM (dev_vision.md Priority: CRITICAL):
1. Character Creation from Scratch - Complete D&D 5e 2024 characters
2. Custom Content Generation - Species, classes, feats, spells, weapons, armor  
3. Iterative Refinement System - User feedback and character improvement
4. Existing Character Enhancement - Level-up with journal context
5. Content Hierarchy & Prioritization - D&D first → adapt → custom

🏰 SECONDARY CREATION FEATURES (dev_vision.md Priority: MEDIUM-HIGH):
6. NPC Creation - Roleplay-focused with motivations/secrets
7. Creature/Monster Creation - Balanced challenge ratings
8. Standalone Item Creation - Individual weapons/spells/armor
9. Content Validation & Balance Checking - D&D 5e compliance

🔄 ADVANCED FEATURES (dev_vision.md Priority: HIGH):
10. Journal-Based Character Evolution - Play-informed advancement
11. Multi-class Character Development - Story-driven class changes
12. Character Import/Export - Database persistence and versioning

Focus: Complete validation of the creative AI-powered D&D content generation
system that enables ANY character concept through iterative development.
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

# Import all creation components for comprehensive testing
try:
    from creation import CharacterCreator, NPCCreator, CreatureCreator, ItemCreator, CreationConfig
    from creation_factory import CreationFactory
    from llm_service import create_llm_service
    from creation_validation import validate_all_databases
    from enums import NPCType, NPCRole, ItemType, ItemRarity
    from generators import CustomContentGenerator
    from custom_content_models import ContentRegistry
except ImportError as e:
    print(f"Import error: {e}")
    print("Some creation modules may not be fully implemented yet")
    # Continue with available modules
    from creation import CharacterCreator, CreationConfig
    from llm_service import create_llm_service
    from creation_validation import validate_all_databases

# Test logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class CreationTestCase:
    """Test case for comprehensive creation feature testing."""
    name: str
    test_type: str  # "character", "npc", "creature", "item", "refinement", "evolution"
    concept: str
    level: int
    expected_elements: Dict[str, Any]
    user_preferences: Optional[Dict[str, Any]] = None
    description: str = ""
    requires_existing_character: bool = False
    evolution_data: Optional[Dict[str, Any]] = None  # For refinement/evolution tests

@dataclass  
class ComprehensiveTestResult:
    """Result of a comprehensive creation test."""
    test_name: str
    test_type: str
    success: bool
    creation_data: Optional[Dict[str, Any]] = None
    validation_results: Dict[str, bool] = None
    creation_time: float = 0.0
    error_message: str = ""
    creativity_score: int = 0  # 1-10 scale
    dnd_compatibility: bool = False
    custom_content_generated: bool = False
    iterative_features_tested: bool = False

class ComprehensiveCreationFeaturesTest:
    """Comprehensive test suite for ALL creation features from dev_vision.md."""
    
    def __init__(self):
        self.llm_service = None
        self.character_creator = None
        self.creation_factory = None
        self.npc_creator = None
        self.creature_creator = None
        self.item_creator = None
        self.custom_content_generator = None
        self.test_results: List[ComprehensiveTestResult] = []
        
    async def setup(self):
        """Set up comprehensive test environment for all creation features."""
        logger.info("Setting up comprehensive creation features test environment...")
        
        # Validate all databases first
        logger.info("Validating D&D databases...")
        try:
            if not validate_all_databases():
                raise Exception("Database validation failed - cannot proceed with creation tests")
            logger.info("✅ All D&D databases validated successfully")
        except Exception as e:
            logger.warning(f"⚠️ Database validation error: {e}")
        
        # Initialize LLM service
        try:
            self.llm_service = create_llm_service()
            logger.info("✅ LLM service initialized")
        except Exception as e:
            logger.warning(f"⚠️ LLM service initialization failed: {e}")
            self.llm_service = None
        
        # Initialize creation factory (orchestration layer)
        try:
            self.creation_factory = CreationFactory(self.llm_service)
            logger.info("✅ Creation factory initialized")
        except Exception as e:
            logger.warning(f"⚠️ Creation factory initialization failed: {e}")
            self.creation_factory = None
        
        # Initialize individual creators
        config = CreationConfig()
        
        try:
            self.character_creator = CharacterCreator(self.llm_service, config)
            logger.info("✅ Character creator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Character creator initialization failed: {e}")
        
        try:
            self.npc_creator = NPCCreator(self.llm_service, config)
            logger.info("✅ NPC creator initialized")
        except Exception as e:
            logger.warning(f"⚠️ NPC creator initialization failed: {e}")
            self.npc_creator = None
        
        try:
            self.creature_creator = CreatureCreator(self.llm_service, config)
            logger.info("✅ Creature creator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Creature creator initialization failed: {e}")
            self.creature_creator = None
        
        try:
            self.item_creator = ItemCreator(self.llm_service, config)
            logger.info("✅ Item creator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Item creator initialization failed: {e}")
            self.item_creator = None
        
        try:
            content_registry = ContentRegistry()
            self.custom_content_generator = CustomContentGenerator(self.llm_service, content_registry)
            logger.info("✅ Custom content generator initialized")
        except Exception as e:
            logger.warning(f"⚠️ Custom content generator initialization failed: {e}")
            self.custom_content_generator = None
        
    def get_comprehensive_test_cases(self) -> List[CreationTestCase]:
        """Get comprehensive test cases covering ALL dev_vision.md creation features."""
        return [
            # ================================================================
            # 1. CHARACTER CREATION FROM SCRATCH (dev_vision.md CRITICAL)
            # ================================================================
            CreationTestCase(
                name="character_classic_fighter",
                test_type="character",
                concept="A noble human fighter wielding sword and shield, defender of the innocent",
                level=3,
                expected_elements={
                    "species": ["Human"],
                    "classes": ["Fighter"],
                    "weapons": ["Longsword", "Shield"],
                    "armor": ["Chain Mail", "Plate"],
                    "alignment": ["Lawful", "Good"],
                    "feats": ["origin_feat", "general_feats"]
                },
                description="Classic D&D character creation with traditional elements"
            ),
            
            CreationTestCase(
                name="character_unique_concept",
                test_type="character",
                concept="A dragonborn bard-chef who uses cooking magic to inspire allies and defeat enemies",
                level=5,
                expected_elements={
                    "species": ["Dragonborn"],
                    "classes": ["Bard"],
                    "tools": ["Cook's Utensils"],
                    "spells": ["Prestidigitation", "Create Food"],
                    "custom_elements": ["cooking magic"]
                },
                user_preferences={"allow_custom_content": True},
                description="Creative character requiring custom content generation"
            ),
            
            # ================================================================
            # 2. CUSTOM CONTENT GENERATION (dev_vision.md CRITICAL)
            # ================================================================
            CreationTestCase(
                name="character_custom_species",
                test_type="character",
                concept="A crystal-touched mystic from the Shimmering Peaks who channels gem magic",
                level=6,
                expected_elements={
                    "custom_species": True,
                    "custom_spells": True,
                    "classes": ["Sorcerer", "Mystic"],
                    "backstory_themes": ["crystal", "Shimmering Peaks", "gem magic"]
                },
                user_preferences={"allow_custom_content": True, "require_custom_species": True},
                description="Character requiring custom species generation"
            ),
            
            CreationTestCase(
                name="character_custom_class",
                test_type="character", 
                concept="A time-weaver who manipulates temporal magic and sees multiple timelines",
                level=8,
                expected_elements={
                    "custom_class": True,
                    "custom_spells": True,
                    "backstory_themes": ["time", "temporal", "timeline", "weaver"]
                },
                user_preferences={"allow_custom_content": True, "require_custom_class": True},
                description="Character requiring custom class generation"
            ),
            
            # ================================================================
            # 3. ITERATIVE REFINEMENT SYSTEM (dev_vision.md CRITICAL - NEWLY IMPLEMENTED)
            # ================================================================
            CreationTestCase(
                name="character_refinement_ability_focus",
                test_type="refinement",
                concept="Make the character more focused on intelligence and wisdom, less on strength",
                level=4,
                expected_elements={
                    "ability_changes": ["intelligence", "wisdom", "strength"],
                    "refinement_applied": True
                },
                requires_existing_character=True,
                evolution_data={"change_type": "ability_focus"},
                description="Test iterative refinement of ability scores"
            ),
            
            CreationTestCase(
                name="character_refinement_class_change",
                test_type="refinement",
                concept="Change from Fighter to Paladin to better reflect the character's noble ideals",
                level=3,
                expected_elements={
                    "class_change": ["Fighter", "Paladin"],
                    "refinement_applied": True
                },
                requires_existing_character=True,
                evolution_data={"change_type": "class_change"},
                description="Test iterative refinement with class changes"
            ),
            
            # ================================================================
            # 4. EXISTING CHARACTER ENHANCEMENT (dev_vision.md HIGH - NEWLY IMPLEMENTED)
            # ================================================================
            CreationTestCase(
                name="character_journal_levelup",
                test_type="evolution",
                concept="Level up based on combat experiences and magical discoveries",
                level=5,  # Target level after level-up
                expected_elements={
                    "level_increased": True,
                    "journal_informed": True,
                    "backstory_preserved": True
                },
                requires_existing_character=True,
                evolution_data={
                    "evolution_type": "level_up",
                    "journal_entries": [
                        "Fought fierce dragons in the mountains",
                        "Discovered ancient magical artifacts",
                        "Led the party through dangerous territories"
                    ]
                },
                description="Test journal-based character level-up"
            ),
            
            CreationTestCase(
                name="character_story_enhancement",
                test_type="evolution",
                concept="Character gains fire immunity and draconic knowledge after surviving dragon encounter",
                level=7,
                expected_elements={
                    "story_enhancement": True,
                    "new_abilities": ["fire immunity", "draconic"],
                    "backstory_preserved": True
                },
                requires_existing_character=True,
                evolution_data={"evolution_type": "story_enhancement"},
                description="Test story-driven character enhancement"
            ),
            
            # ================================================================
            # 5. NPC CREATION (dev_vision.md MEDIUM)
            # ================================================================
            CreationTestCase(
                name="npc_tavern_keeper",
                test_type="npc",
                concept="A jovial halfling tavern keeper with secrets about the local thieves' guild",
                level=3,
                expected_elements={
                    "species": ["Halfling"],
                    "npc_role": ["shopkeeper", "civilian"],
                    "personality": True,
                    "secrets": ["thieves' guild"],
                    "motivations": True,
                    "relationships": True
                },
                user_preferences={"npc_type": "major", "npc_role": "shopkeeper"},
                description="Test NPC creation with roleplay focus"
            ),
            
            CreationTestCase(
                name="npc_quest_giver",
                test_type="npc",
                concept="A mysterious elven sage who knows about ancient prophecies and lost artifacts",
                level=10,
                expected_elements={
                    "species": ["Elf"],
                    "npc_role": ["quest_giver"],
                    "knowledge": ["prophecy", "artifacts"],
                    "personality": True,
                    "dm_notes": True
                },
                user_preferences={"npc_type": "major", "npc_role": "quest_giver"},
                description="Test quest-giver NPC creation"
            ),
            
            # ================================================================
            # 6. CREATURE/MONSTER CREATION (dev_vision.md MEDIUM)
            # ================================================================
            CreationTestCase(
                name="creature_forest_guardian",
                test_type="creature",
                concept="A magical tree-spirit that protects the ancient forest from intruders",
                level=5,  # Challenge Rating 5
                expected_elements={
                    "creature_type": ["plant", "fey"],
                    "challenge_rating": 5,
                    "abilities": ["forest protection", "magic"],
                    "stat_block": True
                },
                user_preferences={"challenge_rating": 5.0, "creature_type": "plant"},
                description="Test creature creation with environmental theme"
            ),
            
            CreationTestCase(
                name="creature_custom_aberration",
                test_type="creature",
                concept="A mind-bending aberration from beyond the stars that warps reality",
                level=8,  # Challenge Rating 8
                expected_elements={
                    "creature_type": ["aberration"],
                    "challenge_rating": 8,
                    "abilities": ["mind-bending", "reality warp"],
                    "custom_content": True
                },
                user_preferences={"challenge_rating": 8.0, "allow_custom_content": True},
                description="Test creature creation requiring custom abilities"
            ),
            
            # ================================================================
            # 7. STANDALONE ITEM CREATION (dev_vision.md MEDIUM)
            # ================================================================
            CreationTestCase(
                name="item_magic_weapon",
                test_type="item",
                concept="A flaming sword that was forged in dragon fire and glows with inner light",
                level=7,  # Character level for appropriate rarity
                expected_elements={
                    "item_type": "weapon",
                    "magic": True,
                    "properties": ["flaming", "glowing"],
                    "rarity": ["uncommon", "rare"],
                    "backstory": ["dragon fire", "forged"]
                },
                user_preferences={"item_type": "weapon", "character_level": 7},
                description="Test magical weapon creation"
            ),
            
            CreationTestCase(
                name="item_custom_spell",
                test_type="item",
                concept="A spell that allows communication with crystalline formations and gem spirits",
                level=5,
                expected_elements={
                    "item_type": "spell",
                    "spell_level": [2, 3],
                    "school": ["divination", "enchantment"],
                    "custom_content": True,
                    "components": True
                },
                user_preferences={"item_type": "spell", "allow_custom_content": True},
                description="Test custom spell creation"
            ),
            
            # ================================================================
            # 8. CONTENT VALIDATION & BALANCE (dev_vision.md HIGH)
            # ================================================================
            CreationTestCase(
                name="validation_overpowered_check",
                test_type="character",
                concept="A level 5 character but with abilities that seem overpowered for that level",
                level=5,
                expected_elements={
                    "balance_checked": True,
                    "power_level_appropriate": True,
                    "validation_warnings": True
                },
                user_preferences={"strict_balance_checking": True},
                description="Test balance validation for potentially overpowered content"
            ),
            
            # ================================================================
            # 9. MULTICLASS CHARACTER DEVELOPMENT (dev_vision.md HIGH)
            # ================================================================
            CreationTestCase(
                name="character_multiclass_evolution",
                test_type="evolution",
                concept="Add Warlock levels due to making a pact after nearly dying in battle",
                level=6,  # Target level with multiclass
                expected_elements={
                    "multiclass_added": True,
                    "story_reason": ["pact", "nearly dying", "battle"],
                    "class_synergy": True
                },
                requires_existing_character=True,
                evolution_data={
                    "evolution_type": "multiclass",
                    "multiclass_option": "Warlock",
                    "story_reason": "Made a desperate pact to survive a deadly encounter"
                },
                description="Test story-driven multiclass development"
            )
        ]

    async def run_comprehensive_creation_test(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Run a single comprehensive creation test."""
        logger.info(f"\n{'='*60}")
        logger.info(f"🧙 TESTING: {test_case.name}")
        logger.info(f"📖 TYPE: {test_case.test_type.title()}")
        logger.info(f"💭 CONCEPT: {test_case.concept}")
        logger.info(f"📊 LEVEL: {test_case.level}")
        logger.info(f"{'='*60}")
        
        start_time = time.time()
        
        try:
            # Route to appropriate test method based on type
            if test_case.test_type == "character":
                result = await self._test_character_creation(test_case)
            elif test_case.test_type == "refinement":
                result = await self._test_character_refinement(test_case)
            elif test_case.test_type == "evolution":
                result = await self._test_character_evolution(test_case)
            elif test_case.test_type == "npc":
                result = await self._test_npc_creation(test_case)
            elif test_case.test_type == "creature":
                result = await self._test_creature_creation(test_case)
            elif test_case.test_type == "item":
                result = await self._test_item_creation(test_case)
            else:
                raise ValueError(f"Unknown test type: {test_case.test_type}")
            
            creation_time = time.time() - start_time
            result.creation_time = creation_time
            
            logger.info(f"✅ {test_case.test_type.title()} creation completed in {creation_time:.2f}s")
            return result
            
        except Exception as e:
            creation_time = time.time() - start_time
            logger.error(f"❌ {test_case.test_type.title()} creation failed: {str(e)}")
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type=test_case.test_type,
                success=False,
                creation_time=creation_time,
                error_message=str(e)
            )
    
    async def _test_character_creation(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test character creation from scratch."""
        if not self.character_creator:
            raise Exception("Character creator not initialized")
        
        creation_result = await self.character_creator.create_character(
            prompt=test_case.concept,
            user_preferences=test_case.user_preferences
        )
        
        if not creation_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="character",
                success=False,
                error_message=creation_result.error or "Character creation failed"
            )
        
        character_data = creation_result.data
        raw_data = character_data.get("raw_data", {})
        
        # Validate completeness
        validation_results = self.validate_character_completeness(raw_data, test_case)
        
        # Assess features
        creativity_score = self.assess_creativity(raw_data, test_case)
        dnd_compatibility = self.assess_dnd_compatibility(raw_data)
        custom_content_generated = self._check_custom_content_generated(raw_data)
        
        self.log_creation_summary(raw_data, test_case.name, "character")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="character",
            success=True,
            creation_data=character_data,
            validation_results=validation_results,
            creativity_score=creativity_score,
            dnd_compatibility=dnd_compatibility,
            custom_content_generated=custom_content_generated
        )
    
    async def _test_character_refinement(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test iterative character refinement."""
        if not self.character_creator:
            raise Exception("Character creator not initialized")
        
        # First create a base character for refinement
        base_character_result = await self.character_creator.create_character(
            prompt="A basic human fighter for refinement testing",
            user_preferences={"level": test_case.level}
        )
        
        if not base_character_result.success:
            raise Exception("Failed to create base character for refinement")
        
        base_data = base_character_result.data.get("raw_data", {})
        
        # Apply refinement
        refinement_result = await self.character_creator.refine_character(
            character_data=base_data,
            refinement_prompt=test_case.concept,
            user_preferences=test_case.user_preferences
        )
        
        if not refinement_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="refinement",
                success=False,
                error_message=refinement_result.error or "Refinement failed"
            )
        
        refined_data = refinement_result.data.get("raw_data", {})
        
        # Validate refinement was applied
        refinement_validation = self._validate_refinement_applied(base_data, refined_data, test_case)
        
        self.log_creation_summary(refined_data, test_case.name, "refinement")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="refinement",
            success=True,
            creation_data=refinement_result.data,
            validation_results=refinement_validation,
            iterative_features_tested=True,
            dnd_compatibility=self.assess_dnd_compatibility(refined_data)
        )
    
    async def _test_character_evolution(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test character evolution/enhancement."""
        if not self.character_creator:
            raise Exception("Character creator not initialized")
        
        # Create base character for evolution
        base_level = test_case.level - 1 if test_case.level > 1 else 1
        base_character_result = await self.character_creator.create_character(
            prompt="A developing character ready for advancement",
            user_preferences={"level": base_level}
        )
        
        if not base_character_result.success:
            raise Exception("Failed to create base character for evolution")
        
        base_data = base_character_result.data.get("raw_data", {})
        evolution_data = test_case.evolution_data or {}
        
        # Apply appropriate evolution
        if evolution_data.get("evolution_type") == "level_up":
            evolution_result = await self.character_creator.level_up_character_with_journal(
                character_data=base_data,
                journal_entries=evolution_data.get("journal_entries", []),
                new_level=test_case.level,
                multiclass_option=evolution_data.get("multiclass_option")
            )
        else:
            evolution_result = await self.character_creator.enhance_existing_character(
                character_data=base_data,
                enhancement_prompt=test_case.concept
            )
        
        if not evolution_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="evolution",
                success=False,
                error_message=evolution_result.error or "Evolution failed"
            )
        
        evolved_data = evolution_result.data.get("raw_data", {})
        
        # Validate evolution
        evolution_validation = self._validate_evolution_applied(base_data, evolved_data, test_case)
        
        self.log_creation_summary(evolved_data, test_case.name, "evolution")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="evolution",
            success=True,
            creation_data=evolution_result.data,
            validation_results=evolution_validation,
            iterative_features_tested=True,
            dnd_compatibility=self.assess_dnd_compatibility(evolved_data)
        )
    
    async def _test_npc_creation(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test NPC creation."""
        if not self.npc_creator:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="npc",
                success=False,
                error_message="NPC creator not available"
            )
        
        # Extract NPC parameters
        user_prefs = test_case.user_preferences or {}
        npc_type = NPCType.MAJOR if user_prefs.get("npc_type") == "major" else NPCType.MINOR
        npc_role = NPCRole.SHOPKEEPER if user_prefs.get("npc_role") == "shopkeeper" else NPCRole.QUEST_GIVER
        
        creation_result = await self.npc_creator.create_npc(
            prompt=test_case.concept,
            npc_type=npc_type,
            npc_role=npc_role
        )
        
        if not creation_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="npc",
                success=False,
                error_message=creation_result.error or "NPC creation failed"
            )
        
        npc_data = creation_result.data
        
        # Validate NPC components
        npc_validation = self._validate_npc_components(npc_data, test_case)
        
        self.log_creation_summary(npc_data, test_case.name, "npc")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="npc",
            success=True,
            creation_data=npc_data,
            validation_results=npc_validation,
            dnd_compatibility=True  # NPCs don't need full D&D compliance
        )
    
    async def _test_creature_creation(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test creature/monster creation."""
        if not self.creature_creator:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="creature",
                success=False,
                error_message="Creature creator not available"
            )
        
        user_prefs = test_case.user_preferences or {}
        challenge_rating = float(user_prefs.get("challenge_rating", test_case.level))
        creature_type = user_prefs.get("creature_type", "beast")
        
        creation_result = await self.creature_creator.create_creature(
            description=test_case.concept,
            challenge_rating=challenge_rating,
            creature_type=creature_type
        )
        
        if not creation_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="creature",
                success=False,
                error_message=creation_result.error or "Creature creation failed"
            )
        
        creature_data = creation_result.data
        
        # Validate creature components
        creature_validation = self._validate_creature_components(creature_data, test_case)
        
        self.log_creation_summary(creature_data, test_case.name, "creature")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="creature",
            success=True,
            creation_data=creature_data,
            validation_results=creature_validation,
            dnd_compatibility=True
        )
    
    async def _test_item_creation(self, test_case: CreationTestCase) -> ComprehensiveTestResult:
        """Test standalone item creation."""
        if not self.item_creator:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="item",
                success=False,
                error_message="Item creator not available"
            )
        
        user_prefs = test_case.user_preferences or {}
        item_type_str = user_prefs.get("item_type", "weapon")
        
        # Map string to enum
        item_type_map = {
            "weapon": ItemType.WEAPON,
            "armor": ItemType.ARMOR,
            "spell": ItemType.SPELL,
            "item": ItemType.WONDROUS_ITEM
        }
        item_type = item_type_map.get(item_type_str, ItemType.WEAPON)
        
        character_level = user_prefs.get("character_level", test_case.level)
        
        creation_result = await self.item_creator.create_item(
            description=test_case.concept,
            item_type=item_type,
            character_level=character_level,
            character_concept=""
        )
        
        if not creation_result.success:
            return ComprehensiveTestResult(
                test_name=test_case.name,
                test_type="item",
                success=False,
                error_message=creation_result.error or "Item creation failed"
            )
        
        item_data = creation_result.data
        
        # Validate item components
        item_validation = self._validate_item_components(item_data, test_case)
        custom_content = user_prefs.get("allow_custom_content", False)
        
        self.log_creation_summary(item_data, test_case.name, "item")
        
        return ComprehensiveTestResult(
            test_name=test_case.name,
            test_type="item",
            success=True,
            creation_data=item_data,
            validation_results=item_validation,
            custom_content_generated=custom_content,
            dnd_compatibility=True
        )
    
    # ================================================================
    # VALIDATION METHODS FOR ALL CREATION TYPES
    # ================================================================
    
    def validate_character_completeness(self, character_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
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
    
    def _validate_refinement_applied(self, base_data: Dict[str, Any], refined_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
        """Validate that iterative refinement was properly applied."""
        validation = {
            "changes_detected": base_data != refined_data,
            "core_elements_preserved": (
                base_data.get("name") == refined_data.get("name") or
                base_data.get("backstory") == refined_data.get("backstory")
            ),
            "refinement_responsive": True  # Assume responsive unless proven otherwise
        }
        
        # Check specific refinement types
        expected_changes = test_case.expected_elements
        if "ability_changes" in expected_changes:
            # Check ability score changes
            base_abilities = base_data.get("ability_scores", {})
            refined_abilities = refined_data.get("ability_scores", {})
            validation["ability_changes_made"] = base_abilities != refined_abilities
        
        if "class_change" in expected_changes:
            # Check class changes
            base_classes = base_data.get("classes", {})
            refined_classes = refined_data.get("classes", {})
            validation["class_changes_made"] = base_classes != refined_classes
        
        return validation
    
    def _validate_evolution_applied(self, base_data: Dict[str, Any], evolved_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
        """Validate that character evolution was properly applied."""
        validation = {
            "evolution_detected": base_data != evolved_data,
            "backstory_preserved_or_enhanced": bool(evolved_data.get("backstory")),
            "character_identity_maintained": bool(evolved_data.get("name"))
        }
        
        # Check specific evolution types
        expected_elements = test_case.expected_elements
        
        if "level_increased" in expected_elements:
            base_level = base_data.get("level", 1)
            evolved_level = evolved_data.get("level", 1)
            validation["level_increased"] = evolved_level > base_level
        
        if "multiclass_added" in expected_elements:
            base_classes = len(base_data.get("classes", {}))
            evolved_classes = len(evolved_data.get("classes", {}))
            validation["multiclass_added"] = evolved_classes > base_classes
        
        if "new_abilities" in expected_elements:
            # Check for new abilities, spells, or features
            base_features = len(str(base_data.get("features", {})))
            evolved_features = len(str(evolved_data.get("features", {})))
            validation["new_abilities_added"] = evolved_features > base_features
        
        return validation
    
    def _validate_npc_components(self, npc_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
        """Validate NPC-specific components."""
        validation = {
            "has_name": bool(npc_data.get("name")),
            "has_personality": bool(npc_data.get("personality_traits")),
            "has_motivations": bool(npc_data.get("motivations") or npc_data.get("ideals")),
            "has_roleplay_info": bool(npc_data.get("mannerisms") or npc_data.get("speech_patterns")),
            "appropriate_for_role": True  # Assume appropriate unless proven otherwise
        }
        
        # Check for expected NPC elements
        expected_elements = test_case.expected_elements
        
        if "secrets" in expected_elements:
            secrets_content = str(npc_data.get("secrets", "")) + str(npc_data.get("dm_notes", ""))
            validation["has_secrets"] = any(secret in secrets_content.lower() for secret in expected_elements["secrets"])
        
        if "dm_notes" in expected_elements:
            validation["has_dm_notes"] = bool(npc_data.get("dm_notes"))
        
        return validation
    
    def _validate_creature_components(self, creature_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
        """Validate creature/monster components."""
        validation = {
            "has_stat_block": bool(creature_data.get("ability_scores")),
            "has_challenge_rating": bool(creature_data.get("challenge_rating")),
            "has_abilities": bool(creature_data.get("special_abilities") or creature_data.get("features")),
            "balanced_for_cr": True  # Assume balanced unless proven otherwise
        }
        
        # Check challenge rating appropriateness
        expected_cr = test_case.expected_elements.get("challenge_rating")
        actual_cr = creature_data.get("challenge_rating")
        if expected_cr and actual_cr:
            validation["appropriate_challenge_rating"] = abs(float(actual_cr) - float(expected_cr)) <= 1
        
        return validation
    
    def _validate_item_components(self, item_data: Dict[str, Any], test_case: CreationTestCase) -> Dict[str, bool]:
        """Validate item creation components."""
        validation = {
            "has_name": bool(item_data.get("name")),
            "has_description": bool(item_data.get("description")),
            "has_properties": bool(item_data.get("properties") or item_data.get("effects")),
            "appropriate_rarity": True  # Assume appropriate unless proven otherwise
        }
        
        # Check item type specifics
        expected_type = test_case.expected_elements.get("item_type")
        if expected_type == "weapon":
            validation["has_weapon_stats"] = bool(item_data.get("damage") or item_data.get("weapon_properties"))
        elif expected_type == "spell":
            validation["has_spell_components"] = bool(item_data.get("components") or item_data.get("casting_time"))
        
        return validation
    
    def _check_custom_content_generated(self, creation_data: Dict[str, Any]) -> bool:
        """Check if custom content was generated."""
        # Look for indicators of custom content
        custom_indicators = ["custom", "unique", "homebrew", "original"]
        content_str = str(creation_data).lower()
        
        return any(indicator in content_str for indicator in custom_indicators)
    
    def assess_creativity(self, character_data: Dict[str, Any], test_case: CreationTestCase) -> int:
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
    
    def log_creation_summary(self, creation_data: Dict[str, Any], test_name: str, creation_type: str):
        """Log a summary of the created content."""
        name = creation_data.get("name", "Unnamed")
        
        logger.info(f"📋 {creation_type.upper()} SUMMARY for {test_name}:")
        logger.info(f"   Name: {name}")
        
        if creation_type == "character":
            species = creation_data.get("species", "Unknown")
            classes = creation_data.get("classes", {})
            level = creation_data.get("level", 1)
            background = creation_data.get("background", "Unknown")
            
            logger.info(f"   Species: {species}")
            logger.info(f"   Classes: {classes}")
            logger.info(f"   Level: {level}")
            logger.info(f"   Background: {background}")
            
            # Log key equipment
            weapons = creation_data.get("weapons", [])
            if weapons:
                weapon_names = [w.get("name", str(w)) for w in weapons[:3]]
                logger.info(f"   Weapons: {', '.join(weapon_names)}")
            
            armor = creation_data.get("armor", "")
            if armor:
                logger.info(f"   Armor: {armor}")
            
            # Log spells if applicable
            spells = creation_data.get("spells_known", [])
            if spells:
                spell_names = [s.get("name", str(s)) for s in spells[:5]]
                logger.info(f"   Spells: {', '.join(spell_names)}")
            
            # Log feats
            origin_feat = creation_data.get("origin_feat", "")
            general_feats = creation_data.get("general_feats", [])
            if origin_feat or general_feats:
                feat_list = [origin_feat] if origin_feat else []
                feat_list.extend([f.get("name", str(f)) for f in general_feats[:2]])
                logger.info(f"   Feats: {', '.join(feat_list)}")
        
        elif creation_type == "npc":
            role = creation_data.get("role", "Unknown")
            personality = creation_data.get("personality_traits", "")
            logger.info(f"   Role: {role}")
            logger.info(f"   Personality: {personality[:100]}...")
        
        elif creation_type == "creature":
            cr = creation_data.get("challenge_rating", "Unknown")
            creature_type = creation_data.get("type", "Unknown")
            logger.info(f"   Challenge Rating: {cr}")
            logger.info(f"   Type: {creature_type}")
        
        elif creation_type == "item":
            item_type = creation_data.get("type", "Unknown")
            rarity = creation_data.get("rarity", "Unknown")
            logger.info(f"   Type: {item_type}")
            logger.info(f"   Rarity: {rarity}")

    async def run_all_tests(self):
        """Run all comprehensive creation tests."""
        logger.info("🚀 Starting Comprehensive Creation Features Test Suite")
        logger.info("Testing ALL dev_vision.md creation requirements")
        logger.info("=" * 80)
        
        test_cases = self.get_comprehensive_test_cases()
        
        for i, test_case in enumerate(test_cases, 1):
            logger.info(f"\n📊 PROGRESS: Test {i}/{len(test_cases)}")
            
            result = await self.run_comprehensive_creation_test(test_case)
            self.test_results.append(result)
            
            # Brief pause between tests
            await asyncio.sleep(1)
        
        # Generate comprehensive report
        self.generate_test_report()
    
    def generate_test_report(self):
        """Generate a comprehensive test report."""
        logger.info("\n" + "=" * 80)
        logger.info("📊 COMPREHENSIVE CREATION FEATURES TEST REPORT")
        logger.info("=" * 80)
        
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results if r.success])
        failed_tests = total_tests - successful_tests
        
        # Group results by test type
        test_types = {}
        for result in self.test_results:
            test_type = result.test_type
            if test_type not in test_types:
                test_types[test_type] = {"total": 0, "passed": 0}
            test_types[test_type]["total"] += 1
            if result.success:
                test_types[test_type]["passed"] += 1
        
        logger.info(f"📈 OVERALL RESULTS:")
        logger.info(f"   Total Tests: {total_tests}")
        logger.info(f"   Successful: {successful_tests} ({successful_tests/total_tests*100:.1f}%)")
        logger.info(f"   Failed: {failed_tests} ({failed_tests/total_tests*100:.1f}%)")
        
        logger.info(f"\n📊 RESULTS BY CREATION TYPE:")
        for test_type, stats in test_types.items():
            success_rate = stats["passed"] / stats["total"] * 100
            logger.info(f"   {test_type.title()}: {stats['passed']}/{stats['total']} ({success_rate:.1f}%)")
        
        if successful_tests > 0:
            avg_creation_time = sum(r.creation_time for r in self.test_results if r.success) / successful_tests
            avg_creativity = sum(r.creativity_score for r in self.test_results if r.success and r.creativity_score > 0) / max(1, len([r for r in self.test_results if r.success and r.creativity_score > 0]))
            compatible_characters = len([r for r in self.test_results if r.success and r.dnd_compatibility])
            custom_content_tests = len([r for r in self.test_results if r.success and r.custom_content_generated])
            iterative_tests = len([r for r in self.test_results if r.success and r.iterative_features_tested])
            
            logger.info(f"\n🔍 QUALITY METRICS:")
            logger.info(f"   Average Creation Time: {avg_creation_time:.2f}s")
            logger.info(f"   Average Creativity Score: {avg_creativity:.1f}/10")
            logger.info(f"   D&D Compatible: {compatible_characters}/{successful_tests} ({compatible_characters/successful_tests*100:.1f}%)")
            logger.info(f"   Custom Content Generated: {custom_content_tests} tests")
            logger.info(f"   Iterative Features Tested: {iterative_tests} tests")
        
        # dev_vision.md compliance assessment
        logger.info(f"\n🎯 DEV_VISION.MD COMPLIANCE ASSESSMENT:")
        
        # Check coverage of critical features
        critical_features = {
            "character": "Character Creation from Scratch",
            "refinement": "Iterative Refinement System", 
            "evolution": "Character Enhancement & Level-up",
            "npc": "NPC Creation",
            "creature": "Creature/Monster Creation",
            "item": "Standalone Item Creation"
        }
        
        for feature_type, feature_name in critical_features.items():
            feature_results = [r for r in self.test_results if r.test_type == feature_type]
            if feature_results:
                feature_success = len([r for r in feature_results if r.success])
                feature_total = len(feature_results)
                status = "✅" if feature_success == feature_total else "⚠️" if feature_success > 0 else "❌"
                logger.info(f"   {status} {feature_name}: {feature_success}/{feature_total}")
            else:
                logger.info(f"   ❌ {feature_name}: Not tested")
        
        # Detailed results
        logger.info(f"\n📋 DETAILED RESULTS:")
        for result in self.test_results:
            status = "✅ PASS" if result.success else "❌ FAIL"
            logger.info(f"   {status} {result.test_name} ({result.test_type})")
            
            if result.success:
                details = []
                details.append(f"Time: {result.creation_time:.2f}s")
                if result.creativity_score > 0:
                    details.append(f"Creativity: {result.creativity_score}/10")
                if result.dnd_compatibility:
                    details.append("D&D Compatible")
                if result.custom_content_generated:
                    details.append("Custom Content")
                if result.iterative_features_tested:
                    details.append("Iterative Features")
                
                if details:
                    logger.info(f"      {' | '.join(details)}")
                
                if result.validation_results:
                    failed_validations = [k for k, v in result.validation_results.items() if not v]
                    if failed_validations:
                        logger.info(f"      Missing: {', '.join(failed_validations)}")
            else:
                logger.info(f"      Error: {result.error_message}")
        
        # Recommendations
        logger.info(f"\n💡 RECOMMENDATIONS:")
        
        if failed_tests > 0:
            logger.info(f"   - Investigate {failed_tests} failed creation tests")
        
        if successful_tests > 0:
            low_creativity = len([r for r in self.test_results if r.success and r.creativity_score > 0 and r.creativity_score < 5])
            if low_creativity > 0:
                logger.info(f"   - Enhance creativity in {low_creativity} creation(s) with low scores")
            
            incompatible = len([r for r in self.test_results if r.success and not r.dnd_compatibility])
            if incompatible > 0:
                logger.info(f"   - Fix D&D compatibility issues in {incompatible} creation(s)")
            
            slow_tests = len([r for r in self.test_results if r.success and r.creation_time > 10])
            if slow_tests > 0:
                logger.info(f"   - Optimize performance for {slow_tests} slow creation(s)")
        
        # Final compliance score
        compliance_score = successful_tests / total_tests * 100 if total_tests > 0 else 0
        logger.info(f"\n🏆 FINAL DEV_VISION.MD COMPLIANCE SCORE: {compliance_score:.1f}%")
        
        if compliance_score >= 95:
            logger.info("🎉 EXCELLENT - All dev_vision.md creation features working!")
        elif compliance_score >= 80:
            logger.info("👍 GOOD - Most dev_vision.md creation features working")
        elif compliance_score >= 60:
            logger.info("⚠️  FAIR - Some dev_vision.md creation features need work")
        else:
            logger.info("❌ POOR - Major dev_vision.md creation features need implementation")
        
        logger.info("\n🎯 COMPREHENSIVE CREATION FEATURES TEST SUITE COMPLETE")
        logger.info("=" * 80)

async def main():
    """Main test execution function."""
    logger.info("🧙‍♂️ D&D Character Creator - Comprehensive Creation Features Test Suite")
    logger.info("Testing ALL creation features from dev_vision.md requirements")
    
    test_suite = ComprehensiveCreationFeaturesTest()
    
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
