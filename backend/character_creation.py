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
from llm_service import create_llm_service, LLMService
from database_models import CustomContent
from ability_management import AdvancedAbilityManager
from generators import BackstoryGenerator, CustomContentGenerator
from custom_content_models import ContentRegistry, CustomClass

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
        # Note: AdvancedAbilityManager requires character_core, will create when needed
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.content_registry = ContentRegistry()
        self.custom_content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        
        logger.info("CharacterCreator initialized with shared components")
    
    async def create_character(self, prompt: str, user_preferences: Optional[Dict[str, Any]] = None, import_existing: Optional[Dict[str, Any]] = None) -> CreationResult:
        """
        Create a complete D&D 5e 2024 character from a text prompt or import an existing character.
        If import_existing is provided, use it as the base and evolve using the journal.
        """
        start_time = time.time()
        try:
            if import_existing:
                # Importing an existing character from the database
                character_data = import_existing.copy()
                journal_entries = character_data.get("journal", [])
                # Evolve character based on journal
                evolution_result = self.evolve_character_from_journal(character_data, journal_entries)
                if evolution_result.success:
                    character_data.update(evolution_result.data)
                else:
                    logger.warning(f"Journal-based evolution failed: {evolution_result.error}")
                # Optionally, update backstory after evolution
                backstory_result = await self._generate_enhanced_backstory(character_data, prompt or "Journal evolution")
                if backstory_result.success:
                    character_data.update(backstory_result.data)
                # Create final character sheet
                character_core = build_character_core(character_data)
                final_character = self._create_final_character(character_data, character_core)
                result = CreationResult(success=True)
                result.data = final_character
                result.creation_time = time.time() - start_time
                return result
            # ...existing code for new character creation...
            logger.info(f"Starting character creation with prompt: {prompt[:100]}...")
            # Step 1: Generate base character data using shared generator
            level = user_preferences.get("level", 1) if user_preferences else 1
            base_result = await self.data_generator.generate_character_data(prompt, level)
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
            backstory_result = await self._generate_enhanced_backstory(character_data, prompt)
            if backstory_result.success:
                character_data.update(backstory_result.data)
            else:
                base_result.add_warning(f"Backstory generation failed: {backstory_result.error}")
            # Step 5: Add custom content if needed
            custom_content_result = await self._generate_custom_content(character_data, prompt)
            if custom_content_result.success:
                character_data.update(custom_content_result.data)
            else:
                base_result.add_warning(f"Custom content generation failed: {custom_content_result.error}")
            # Step 6: Add journal (blank or with fun starter entries)
            if "journal" not in character_data:
                character_data["journal"] = self._generate_initial_journal(character_data)
            # Step 7: Create final character sheet
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

    def _generate_initial_journal(self, character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Optionally generate a starter journal for a new character (can be left blank or add fun entries).
        """
        # For now, return a mostly blank journal, but can add a fun starter quest/encounter
        starter_journal = []
        # Example: Add a fun starter entry
        starter_journal.append({
            "date": time.strftime("%Y-%m-%d"),
            "event": "Character created. Ready for adventure!",
            "notes": "First steps into the world."
        })
        # Optionally, add a random previous quest/encounter
        # (This could use LLM or random table in the future)
        return starter_journal
    
    async def _generate_enhanced_backstory(self, character_data: Dict[str, Any], original_prompt: str) -> CreationResult:
        """Generate enhanced backstory using the backstory generator."""
        try:
            # Create specialized prompt for backstory generation
            backstory_prompt = create_specialized_prompt(
                content_type="backstory",
                description=original_prompt,
                level=character_data.get("level", 1)
            )
            
            backstory = await self.backstory_generator.generate_backstory(character_data, backstory_prompt)
            
            result = CreationResult(success=True)
            result.data = {"backstory": backstory}
            return result
            
        except Exception as e:
            logger.error(f"Enhanced backstory generation failed: {str(e)}")
            result = CreationResult()
            result.error = str(e)
            return result
    
    async def _generate_custom_content(self, character_data: Dict[str, Any], original_prompt: str) -> CreationResult:
        """Generate custom content (spells, items, etc.) if needed."""
        try:
            custom_content = {}
            
            # Generate comprehensive custom content
            custom_result = await self.custom_content_generator.generate_custom_content_for_character(
                character_data, original_prompt
            )
            
            if custom_result:
                custom_content.update(custom_result)
            
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
        """
        Evolve character based on journal entries using shared evolution logic.
        This includes detecting class inconsistencies and suggesting multiclassing or custom class creation.
        """
        try:
            # First, use the shared evolution logic
            base_evolution = self.journal_evolution.evolve_from_journal(character_data, journal_entries)
            
            # Analyze journal for class consistency and evolution opportunities
            class_analysis = self._analyze_class_consistency(character_data, journal_entries)
            
            if class_analysis["needs_evolution"]:
                logger.info(f"Journal analysis suggests character evolution: {class_analysis['reason']}")
                
                # Handle different evolution scenarios
                if class_analysis["evolution_type"] == "multiclass":
                    evolution_result = self._suggest_multiclass_evolution(character_data, class_analysis)
                    if evolution_result.success:
                        base_evolution.data.update(evolution_result.data)
                        base_evolution.add_warning(f"Multiclass evolution suggested: {class_analysis['suggested_class']}")
                
                elif class_analysis["evolution_type"] == "custom_class":
                    evolution_result = self._create_custom_class_evolution(character_data, class_analysis)
                    if evolution_result.success:
                        base_evolution.data.update(evolution_result.data)
                        base_evolution.add_warning(f"Custom class created: {evolution_result.data.get('custom_class_name', 'Unknown')}")
                
                elif class_analysis["evolution_type"] == "class_replacement":
                    evolution_result = self._suggest_class_replacement(character_data, class_analysis)
                    if evolution_result.success:
                        base_evolution.data.update(evolution_result.data)
                        base_evolution.add_warning(f"Class replacement suggested: {class_analysis['suggested_class']}")
            
            return base_evolution
            
        except Exception as e:
            logger.error(f"Journal-based evolution failed: {str(e)}")
            result = CreationResult()
            result.error = str(e)
            return result

    def _analyze_class_consistency(self, character_data: Dict[str, Any], 
                                 journal_entries: List[str]) -> Dict[str, Any]:
        """
        Analyze journal entries to detect inconsistencies with current class and suggest evolution.
        """
        current_classes = character_data.get("classes", {})
        primary_class = list(current_classes.keys())[0] if current_classes else "Unknown"
        character_level = character_data.get("level", 1)
        
        # Combine journal entries into analysis text
        journal_text = " ".join([
            entry.get("event", "") + " " + entry.get("notes", "") 
            if isinstance(entry, dict) else str(entry) 
            for entry in journal_entries
        ])
        
        analysis = {
            "needs_evolution": False,
            "evolution_type": None,
            "reason": "",
            "suggested_class": "",
            "confidence": 0.0
        }
        
        # Simple keyword-based analysis (could be enhanced with LLM)
        class_keywords = {
            "assassin": ["stealth", "assassination", "kill", "murder", "poison", "shadow", "rogue"],
            "paladin": ["justice", "honor", "holy", "divine", "oath", "righteous"],
            "bard": ["perform", "music", "song", "entertain", "inspire", "charisma"],
            "wizard": ["study", "research", "magic", "spell", "arcane", "knowledge"],
            "barbarian": ["rage", "fury", "wild", "primal", "strength", "anger"],
            "cleric": ["heal", "prayer", "divine", "god", "faith", "blessing"],
            "druid": ["nature", "wild", "animal", "forest", "natural", "shape"],
            "fighter": ["combat", "weapon", "battle", "tactics", "martial"],
            "monk": ["meditation", "inner peace", "martial arts", "discipline"],
            "ranger": ["track", "hunt", "wilderness", "beast", "bow", "nature"],
            "rogue": ["sneak", "steal", "pickpocket", "trap", "cunning"],
            "sorcerer": ["innate", "natural magic", "charisma", "wild magic"],
            "warlock": ["pact", "patron", "deal", "dark magic", "eldritch"]
        }
        
        # Count keyword matches for each class
        class_scores = {}
        journal_lower = journal_text.lower()
        
        for class_name, keywords in class_keywords.items():
            score = sum(1 for keyword in keywords if keyword in journal_lower)
            if score > 0:
                class_scores[class_name] = score
        
        # Find the most suggested class
        if class_scores:
            suggested_class = max(class_scores, key=class_scores.get)
            max_score = class_scores[suggested_class]
            
            # Check if the suggested class is different from current primary class
            if suggested_class.lower() != primary_class.lower() and max_score >= 3:
                analysis["needs_evolution"] = True
                analysis["suggested_class"] = suggested_class
                analysis["confidence"] = min(max_score / 10.0, 1.0)
                
                # Determine evolution type
                if character_level >= 2 and primary_class.lower() != "unknown":
                    # Check if it's a complete philosophical opposite (like jedi -> assassin)
                    opposing_classes = {
                        "jedi": ["assassin", "rogue", "warlock"],
                        "paladin": ["assassin", "rogue", "warlock"],
                        "cleric": ["warlock", "assassin"],
                        "monk": ["barbarian", "warlock"]
                    }
                    
                    if (primary_class.lower() in opposing_classes and 
                        suggested_class in opposing_classes[primary_class.lower()]):
                        analysis["evolution_type"] = "custom_class"
                        analysis["reason"] = f"Journal shows actions inconsistent with {primary_class} principles, suggesting a unique hybrid class"
                    else:
                        analysis["evolution_type"] = "multiclass"
                        analysis["reason"] = f"Journal shows {suggested_class} activities alongside {primary_class} abilities"
                else:
                    analysis["evolution_type"] = "class_replacement"
                    analysis["reason"] = f"Early character, journal suggests {suggested_class} is a better fit than {primary_class}"
        
        return analysis

    def _suggest_multiclass_evolution(self, character_data: Dict[str, Any], 
                                    class_analysis: Dict[str, Any]) -> CreationResult:
        """Suggest multiclassing into the identified class."""
        result = CreationResult(success=True)
        
        current_classes = character_data.get("classes", {})
        suggested_class = class_analysis["suggested_class"]
        
        # Add the new class at level 1
        new_classes = current_classes.copy()
        new_classes[suggested_class] = 1
        
        result.data = {
            "classes": new_classes,
            "multiclass_suggestion": {
                "new_class": suggested_class,
                "reason": class_analysis["reason"],
                "confidence": class_analysis["confidence"]
            }
        }
        
        return result

    def _create_custom_class_evolution(self, character_data: Dict[str, Any], 
                                     class_analysis: Dict[str, Any]) -> CreationResult:
        """Create a custom class that blends the current class with journal-indicated abilities."""
        try:
            current_classes = character_data.get("classes", {})
            primary_class = list(current_classes.keys())[0] if current_classes else "Unknown"
            suggested_class = class_analysis["suggested_class"]
            
            # Create a hybrid class name
            custom_class_name = f"{primary_class.title()}-{suggested_class.title()}"
            
            # Use the custom content generator to create the hybrid class
            hybrid_description = f"A unique class combining {primary_class} training with {suggested_class} methods"
            
            custom_class_data = {
                "name": custom_class_name,
                "description": hybrid_description,
                "primary_ability": "Varies",
                "hit_die": 8,  # Average between typical class hit dice
                "saves": ["Dexterity", "Wisdom"],  # Flexible saves
                "features": {
                    "1": [{"name": f"Dual Path", "description": f"You have training in both {primary_class} and {suggested_class} traditions"}]
                }
            }
            
            # Register the custom class
            custom_class = CustomClass(
                name=custom_class_name,
                description=hybrid_description,
                hit_die=8,
                primary_ability="Varies",
                saving_throw_proficiencies=["Dexterity", "Wisdom"],
                armor_proficiencies=["Light"],
                weapon_proficiencies=["Simple"],
                tool_proficiencies=[],
                skill_choices=4,
                features=custom_class_data["features"]
            )
            
            self.content_registry.register_class(custom_class)
            
            # Update character classes
            new_classes = {custom_class_name: sum(current_classes.values())}
            
            result = CreationResult(success=True)
            result.data = {
                "classes": new_classes,
                "custom_class_name": custom_class_name,
                "custom_class_data": custom_class_data,
                "evolution_reason": class_analysis["reason"]
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Custom class creation failed: {str(e)}")
            result = CreationResult()
            result.error = str(e)
            return result

    def _suggest_class_replacement(self, character_data: Dict[str, Any], 
                                 class_analysis: Dict[str, Any]) -> CreationResult:
        """Suggest replacing the current class entirely (for low-level characters)."""
        result = CreationResult(success=True)
        
        current_level = character_data.get("level", 1)
        suggested_class = class_analysis["suggested_class"]
        
        # Replace the class entirely
        new_classes = {suggested_class: current_level}
        
        result.data = {
            "classes": new_classes,
            "class_replacement": {
                "new_class": suggested_class,
                "reason": class_analysis["reason"],
                "confidence": class_analysis["confidence"]
            }
        }
        
        return result

# ============================================================================
# UTILITY FUNCTIONS FOR BACKWARDS COMPATIBILITY
# ============================================================================

async def create_character_from_prompt(prompt: str, llm_service: Optional[LLMService] = None) -> CreationResult:
    """Utility function for simple character creation."""
    creator = CharacterCreator(llm_service)
    return await creator.create_character(prompt)

def quick_character_creation(concept: str) -> CreationResult:
    """Quick character creation utility."""
    creator = CharacterCreator()
    return creator.quick_create(concept)
