"""
D&D 5e 2024 Character Creation Module - Refactored

This module handles the main character creation workflow using shared components
to eliminate code duplication. It orchestrates the complete character creation
process including validation, generation, and iterative improvements.

Uses shared_character_generation.py for all common logic.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# Import shared components to eliminate duplication
from shared_character_generation import (
    CreationConfig, CreationResult, CharacterDataGenerator, 
    CharacterValidator, JournalBasedEvolution, build_character_core, 
    create_specialized_prompt, quick_character_sheet
)

# Import core D&D components
from core_models import AbilityScore, ProficiencyLevel, ASIManager
from character_models import DnDCondition, CharacterCore, CharacterSheet, CharacterState, CharacterStats
from llm_service_new import create_llm_service, LLMService
from database_models import CustomContent
from ability_management import AdvancedAbilityManager
from generators import BackstoryGenerator, CustomContentGenerator
from custom_content_models import ContentRegistry

logger = logging.getLogger(__name__)

# ============================================================================
# MAIN CHARACTER CREATOR CLASS
# ============================================================================

class CharacterCreator:
    """Main character creation orchestrator using shared components."""
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        """Initialize the character creator with shared components."""
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize shared components
        self.validator = CharacterValidator()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.journal_evolution = JournalBasedEvolution(self.llm_service)
        
        # Initialize D&D-specific managers
        self.ability_manager = AdvancedAbilityManager()
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.custom_content_generator = CustomContentGenerator(self.llm_service)
        self.content_registry = ContentRegistry()
        
        logger.info("CharacterCreator initialized with shared components")
    
    def create_character(self, prompt: str, user_preferences: Optional[Dict[str, Any]] = None) -> CreationResult:
        """
        Create a complete D&D 5e 2024 character from a text prompt.
        
        Args:
            prompt: Natural language description of desired character
            user_preferences: Optional user preferences for creation
            
        Returns:
            CreationResult with character data or error information
        """
        start_time = time.time()
        
        try:
            logger.info(f"Starting character creation with prompt: {prompt[:100]}...")
            
            # Step 1: Generate base character data using shared generator
            base_result = self.data_generator.generate_character_data(prompt, user_preferences)
            if not base_result.success:
                return base_result
            
            # Step 2: Validate the generated data
            validation_result = self.validator.validate_basic_structure(base_result.data)
            if not validation_result.success:
                base_result.error = validation_result.error
                base_result.warnings.extend(validation_result.warnings)
                return base_result
            
            # Step 3: Build character core
            character_data = base_result.data
            character_core = build_character_core(character_data)
            
            # Step 4: Generate backstory
            backstory_result = self._generate_enhanced_backstory(character_data, prompt)
            if backstory_result.success:
                character_data.update(backstory_result.data)
            else:
                base_result.add_warning(f"Backstory generation failed: {backstory_result.error}")
            
            # Step 5: Add custom content if needed
            custom_content_result = self._generate_custom_content(character_data)
            if custom_content_result.success:
                character_data.update(custom_content_result.data)
            else:
                base_result.add_warning(f"Custom content generation failed: {custom_content_result.error}")
            
            # Step 6: Create final character sheet
            final_character = self._create_final_character(character_data, character_core)
            
            # Update result with final data
            base_result.data = final_character
            base_result.creation_time = time.time() - start_time
            
            logger.info(f"Character creation completed in {base_result.creation_time:.2f}s")
            return base_result
            
        except Exception as e:
            logger.error(f"Character creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Character creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _generate_enhanced_backstory(self, character_data: Dict[str, Any], original_prompt: str) -> CreationResult:
        """Generate enhanced backstory using the backstory generator."""
        try:
            # Create specialized prompt for backstory generation
            backstory_prompt = create_specialized_prompt(
                base_prompt=original_prompt,
                character_data=character_data,
                specialization_type="backstory"
            )
            
            backstory = self.backstory_generator.generate_backstory(backstory_prompt, character_data)
            
            result = CreationResult(success=True)
            result.data = {"backstory": backstory}
            return result
            
        except Exception as e:
            logger.error(f"Enhanced backstory generation failed: {str(e)}")
            result = CreationResult()
            result.error = str(e)
            return result
    
    def _generate_custom_content(self, character_data: Dict[str, Any]) -> CreationResult:
        """Generate custom content (spells, items, etc.) if needed."""
        try:
            custom_content = {}
            
            # Check if character needs custom spells
            if self._needs_custom_spells(character_data):
                spells = self.custom_content_generator.generate_custom_spells(character_data)
                custom_content["custom_spells"] = spells
            
            # Check if character needs custom items
            if self._needs_custom_items(character_data):
                items = self.custom_content_generator.generate_custom_items(character_data)
                custom_content["custom_items"] = items
            
            result = CreationResult(success=True)
            result.data = custom_content
            return result
            
        except Exception as e:
            logger.error(f"Custom content generation failed: {str(e)}")
            result = CreationResult()
            result.error = str(e)
            return result
    
    def _needs_custom_spells(self, character_data: Dict[str, Any]) -> bool:
        """Check if character concept requires custom spells."""
        classes = character_data.get("classes", [])
        spellcasting_classes = ["wizard", "sorcerer", "warlock", "cleric", "druid", "bard", "paladin", "ranger"]
        
        return any(cls.lower() in spellcasting_classes for cls in classes)
    
    def _needs_custom_items(self, character_data: Dict[str, Any]) -> bool:
        """Check if character concept requires custom items."""
        # Simple heuristic: higher level characters or specific backgrounds might need custom items
        level = character_data.get("level", 1)
        background = character_data.get("background", "").lower()
        
        return level >= 5 or background in ["noble", "guild artisan", "hermit"]
    
    def _create_final_character(self, character_data: Dict[str, Any], character_core: CharacterCore) -> Dict[str, Any]:
        """Create the final character representation."""
        try:
            # Create character sheet
            character_sheet = quick_character_sheet(character_data)
            
            # Combine all character information
            final_character = {
                "core": character_core.__dict__ if hasattr(character_core, '__dict__') else character_core,
                "sheet": character_sheet,
                "raw_data": character_data,
                "creation_metadata": {
                    "created_at": time.time(),
                    "version": "2024",
                    "generator": "CharacterCreator"
                }
            }
            
            return final_character
            
        except Exception as e:
            logger.error(f"Final character creation failed: {str(e)}")
            # Return basic character data as fallback
            return character_data
    
    def evolve_character_from_journal(self, character_data: Dict[str, Any], 
                                    journal_entries: List[str]) -> CreationResult:
        """Evolve character based on journal entries using shared evolution logic."""
        return self.journal_evolution.evolve_from_journal(character_data, journal_entries)
    
    def quick_create(self, basic_concept: str) -> CreationResult:
        """Quick character creation for simple concepts."""
        config = CreationConfig(
            base_timeout=10,
            backstory_timeout=8,
            custom_content_timeout=5,
            max_retries=1
        )
        
        temp_creator = CharacterCreator(self.llm_service, config)
        return temp_creator.create_character(basic_concept)


# ============================================================================
# UTILITY FUNCTIONS FOR BACKWARDS COMPATIBILITY
# ============================================================================

def create_character_from_prompt(prompt: str, llm_service: Optional[LLMService] = None) -> CreationResult:
    """Utility function for simple character creation."""
    creator = CharacterCreator(llm_service)
    return creator.create_character(prompt)

def quick_character_creation(concept: str) -> CreationResult:
    """Quick character creation utility."""
    creator = CharacterCreator()
    return creator.quick_create(concept)
