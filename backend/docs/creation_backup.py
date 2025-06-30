"""
D&D 5e 2024 Unified Creation Module

This module provides a unified, efficient creation system for all D&D content types.
Character creation serves as the foundation, with NPC and creature creation using
subsets of the complete character creation pipeline.

Architecture:
- BaseCreator: Core creation functionality shared by all content types
- CharacterCreator: Complete character creation (the full feature set)
- NPCCreator: Simplified character creation for NPCs
- CreatureCreator: Basic stat block creation using character foundation
- ItemCreator: Item creation with character integration

This eliminates code duplication and ensures consistency across all creation types.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

# Import validation functions from centralized module
from creation_validation import (
    validate_basic_structure, validate_custom_content,
    validate_and_enhance_npc, validate_item_for_level,
    validate_and_enhance_creature
)

# Import from centralized enums
from enums import (
    NPCType, NPCRole, NPCSpecies, NPCClass, CreatureType, CreatureSize, CreatureAlignment,
    ItemType, ItemRarity, WeaponCategory, ArmorCategory
)

# Import core D&D components
from core_models import AbilityScore, ProficiencyLevel, ASIManager, MagicItemManager
from character_models import DnDCondition, CharacterCore, CharacterSheet, CharacterState, CharacterStats
from llm_service import create_llm_service, LLMService
from database_models import CustomContent
from ability_management import AdvancedAbilityManager
from generators import BackstoryGenerator, CustomContentGenerator
from custom_content_models import ContentRegistry, CustomClass

logger = logging.getLogger(__name__)

# ============================================================================
# SHARED CONFIGURATION AND RESULT CLASSES  
# ============================================================================

@dataclass
class CreationConfig:
    """Configuration for character creation process."""
    base_timeout: int = 300        # 5 minutes for LLM requests
    backstory_timeout: int = 300   # 5 minutes for backstory generation
    custom_content_timeout: int = 300  # 5 minutes for custom content
    max_retries: int = 2
    enable_progress_feedback: bool = True
    auto_save: bool = False

class CreationResult:
    """Result container for character creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.data)

# ============================================================================
# MAIN CHARACTER CREATOR CLASS
# ============================================================================

class CharacterCreator:
    """Main character creation orchestrator using shared components."""

# TODO: include "mounts" as part of a character's concept; some created characters concepts may be intricately paired with a mount.  For example: Alexander the Great's bond with his horse (mount) Bucephalus is legendary
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        """Initialize the character creator with shared components."""
        self.llm_service = llm_service or create_llm_service("ollama", model="tinyllama:latest", timeout=300)
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
            
            backstory_dict = await self.backstory_generator.generate_backstory(character_data, backstory_prompt)
            
            # Extract main backstory text from the dict
            if isinstance(backstory_dict, dict):
                # Get the main backstory text - try different possible keys
                backstory_text = backstory_dict.get("main_backstory", "")
                if not backstory_text:
                    backstory_text = backstory_dict.get("backstory", "")
                if not backstory_text:
                    # Combine all text values if no main backstory found
                    text_parts = [str(v) for v in backstory_dict.values() if isinstance(v, str) and v.strip()]
                    backstory_text = " ".join(text_parts) if text_parts else "A mysterious adventurer."
            else:
                # If it's already a string, use it directly
                backstory_text = str(backstory_dict) if backstory_dict else "A mysterious adventurer."
            
            result = CreationResult(success=True)
            result.data = {"backstory": backstory_text}
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
            # Create character sheet using correct parameters
            name = character_data.get("name", "Generated Character")
            species = character_data.get("species", "Human")
            
            # Get primary class and level
            character_classes = character_data.get("character_classes", character_data.get("classes", {"Fighter": 1}))
            if character_classes:
                primary_class = list(character_classes.keys())[0]
                level = list(character_classes.values())[0]
            else:
                primary_class = "Fighter"
                level = character_data.get("level", 1)
            
            character_sheet = quick_character_sheet(name, species, primary_class, level)
            
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

# ============================================================================
# NPC CLASSES AND CREATION
# ============================================================================

class MinorNPC:
    """
    D&D 5e 2024 Minor NPC - Roleplaying focused without stat block.
    Used for shopkeepers, background characters, informants, etc.
    """
    
    def __init__(self, name: str):
        # Basic Identity
        self.name = name
        self.species = NPCSpecies.HUMAN
        self.role = NPCRole.CIVILIAN
        self.alignment = "neutral"
        
        # Roleplaying Attributes
        self.appearance = ""
        self.personality = ""
        self.secret = ""
        self.backstory = ""
        self.motivations: List[str] = []
        self.mannerisms: List[str] = []
        
        # Location and Context
        self.location = ""
        self.occupation = ""
        self.relationships: Dict[str, str] = {}
        
        # Simple traits
        self.notable_features: List[str] = []
        self.languages: List[str] = ["Common"]
        
        # Metadata
        self.description = ""
        self.dm_notes = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert minor NPC to dictionary format."""
        return {
            "name": self.name,
            "type": "minor",
            "species": self.species.value,
            "role": self.role.value,
            "alignment": self.alignment,
            "appearance": self.appearance,
            "personality": self.personality,
            "secret": self.secret,
            "backstory": self.backstory,
            "motivations": self.motivations,
            "mannerisms": self.mannerisms,
            "location": self.location,
            "occupation": self.occupation,
            "relationships": self.relationships,
            "notable_features": self.notable_features,
            "languages": self.languages,
            "description": self.description,
            "dm_notes": self.dm_notes
        }


# ============================================================================
# NPC CREATION (Uses CharacterCreator with NPC-specific settings)
# ============================================================================

class NPCCreator:
    """NPC Creation using CharacterCreator with NPC-specific configurations."""
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        """Initialize NPC creator using CharacterCreator."""
        # NPCs are just characters with specific roles - reuse CharacterCreator
        self.character_creator = CharacterCreator(llm_service, config)
        logger.info("NPCCreator initialized using CharacterCreator")
    
    async def create_npc(self, prompt: str, npc_type: NPCType = NPCType.MINOR, 
                   npc_role: NPCRole = NPCRole.CIVILIAN) -> CreationResult:
        """Create an NPC using CharacterCreator with NPC-specific prompt modifications."""
        try:
            # Enhance prompt for NPC-specific creation
            npc_prompt = self._enhance_prompt_for_npc(prompt, npc_type, npc_role)
            
            # Use CharacterCreator with NPC preferences
            npc_preferences = {
                "level": 1 if npc_type == NPCType.MINOR else random.randint(1, 8),
                "focus": "roleplay" if npc_type == NPCType.MINOR else "combat",
                "npc_type": npc_type.value,
                "npc_role": npc_role.value
            }
            
            # Create character as NPC
            result = await self.character_creator.create_character(npc_prompt, npc_preferences)
            
            if result.success:
                # Add NPC-specific metadata
                result.data["npc_metadata"] = {
                    "type": npc_type.value,
                    "role": npc_role.value,
                    "is_combat_ready": npc_type == NPCType.MAJOR
                }
                
                # Validate and enhance as NPC
                if "raw_data" in result.data:
                    result.data["raw_data"] = validate_and_enhance_npc(
                        result.data["raw_data"], npc_type, npc_role
                    )
            
            return result
            
        except Exception as e:
            logger.error(f"NPC creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"NPC creation failed: {str(e)}"
            return result
    
    def _enhance_prompt_for_npc(self, base_prompt: str, npc_type: NPCType, npc_role: NPCRole) -> str:
        """Enhance prompt for NPC-specific generation."""
        role_descriptions = {
            NPCRole.CIVILIAN: "an ordinary townsperson with everyday concerns",
            NPCRole.MERCHANT: "a trader with business interests and connections",
            NPCRole.GUARD: "law enforcement with authority and combat training",
            NPCRole.NOBLE: "an aristocrat with social influence and resources",
            NPCRole.SCHOLAR: "a learned individual with specialized knowledge",
            NPCRole.ARTISAN: "a skilled craftsperson with professional expertise",
            NPCRole.CRIMINAL: "a lawbreaker with underworld connections",
            NPCRole.SOLDIER: "a military professional with combat experience"
        }
        
        focus = "roleplay-focused with personality and dialogue" if npc_type == NPCType.MINOR else "combat-ready with full abilities"
        
        return f"""
        Create a D&D 5e NPC who is {role_descriptions.get(npc_role, npc_role.value)}.
        
        Base Description: {base_prompt}
        
        Focus: {focus}
        Role: {npc_role.value}
        
        This NPC should be memorable and three-dimensional, appropriate for D&D 5e 2024 rules.
        """.strip()

# Convenience functions for NPC creation
async def create_npc_from_prompt(prompt: str, npc_type: NPCType = NPCType.MINOR) -> CreationResult:
    """Utility function for simple NPC creation."""
    creator = NPCCreator()
    return await creator.create_npc(prompt, npc_type)

def create_major_npc(description: str, level: int = 1, generate_backstory: bool = True, 
                    include_custom_content: bool = False, add_initial_journal: bool = True, 
                    llm_service: LLMService = None) -> CreationResult:
    """Convenience function to create a major NPC (full stat block) with journal support."""
    creator = NPCCreator(llm_service)
    return creator.create_npc(description, NPCType.MAJOR, NPCRole.CIVILIAN)
        """
        
        return enhanced_prompt.strip()
    
    def _enhance_npc_data(self, npc_data: Dict[str, Any], npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Add NPC-specific enhancements to generated data."""
        # Add NPC metadata
        npc_data["npc_metadata"] = {
            "type": npc_type.value,
            "role": npc_role.value,
            "is_combat_ready": npc_type == NPCType.MAJOR,
            "created_at": time.time()
        }
        
        # Add role-specific traits
        if npc_role == NPCRole.MERCHANT:
            npc_data.setdefault("equipment", []).append("merchant's scales")
            npc_data.setdefault("proficiencies", []).append("Insight")
        elif npc_role == NPCRole.GUARD:
            npc_data.setdefault("equipment", []).extend(["chain mail", "spear", "light crossbow"])
            npc_data.setdefault("proficiencies", []).extend(["Perception", "Athletics"])
        elif npc_role == NPCRole.SCHOLAR:
            npc_data.setdefault("equipment", []).extend(["books", "ink and quill"])
            npc_data.setdefault("proficiencies", []).extend(["History", "Investigation"])
        
        return npc_data

    async def _generate_unique_npc_with_llm(self, prompt: str, npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Generate a unique NPC using LLM services."""
        if not self.llm_service:
            raise ValueError("LLM service not available for NPC generation")
        
        # Create specialized prompt for NPC generation
        specialized_prompt = f"""
        Generate a unique D&D 5e NPC based on this description: {prompt}
        
        NPC Type: {npc_type.value}
        NPC Role: {npc_role.value}
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "name": "Unique character name",
            "species": "D&D species/race",
            "class": "D&D class (if applicable)",
            "role": "{npc_role.value}",
            "level": 1-20,
            "alignment": "D&D alignment",
            "appearance": "Physical description",
            "personality": "Personality traits and mannerisms",
            "backstory": "Brief background story",
            "motivation": "What drives this character",
            "secret": "Hidden aspect or secret",
            "abilities": {{
                "strength": 8-18,
                "dexterity": 8-18,
                "constitution": 8-18,
                "intelligence": 8-18,
                "wisdom": 8-18,
                "charisma": 8-18
            }},
            "skills": ["skill1", "skill2", "skill3"],
            "equipment": ["item1", "item2", "item3"],
            "special_abilities": ["ability1", "ability2"],
            "challenge_rating": 0.125-30.0,
            "hit_points": 1-500,
            "armor_class": 8-25,
            "languages": ["Common", "other languages"],
            "location": "Where they might be found",
            "relationships": "Important connections",
            "quirks": ["unique trait 1", "unique trait 2"]
        }}
        
        Make this NPC unique and memorable. Focus on {"roleplay elements" if npc_type == NPCType.MINOR else "combat readiness and tactical abilities"}.
        """
        
        # Get LLM response
        response = await self.llm_service.generate_content(specialized_prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                npc_data = json.loads(json_str)
                logger.info(f"Successfully generated unique NPC: {npc_data.get('name', 'Unknown')}")
                return npc_data
            else:
                raise ValueError("Could not find valid JSON in LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to basic NPC structure
            return self._create_fallback_npc(prompt, npc_type, npc_role)
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return self._create_fallback_npc(prompt, npc_type, npc_role)
    
    def _create_fallback_npc(self, prompt: str, npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Create a basic NPC when LLM generation fails."""
        import random
        
        # Basic fallback names by role
        names_by_role = {
            NPCRole.CIVILIAN: ["Aldric", "Mira", "Tomás", "Elara"],
            NPCRole.MERCHANT: ["Goldwin", "Vera", "Marcus", "Lydia"],
            NPCRole.GUARD: ["Gareth", "Thane", "Kira", "Bron"],
            NPCRole.NOBLE: ["Lord Aldwin", "Lady Celeste", "Duke Raven", "Countess Vale"],
            NPCRole.SCHOLAR: ["Sage Oren", "Magister Lila", "Scholar Finn", "Archivest Naia"],
            NPCRole.ARTISAN: ["Smith Jorik", "Weaver Anya", "Mason Craig", "Baker Rosie"],
            NPCRole.CRIMINAL: ["Sly", "Raven", "Quick-finger Tom", "Shadow"],
            NPCRole.SOLDIER: ["Captain Rex", "Sergeant Maya", "Commander Zara", "Lieutenant Vale"]
        }
        
        return {
            "name": random.choice(names_by_role.get(npc_role, ["Generic NPC"])),
            "species": "Human",
            "class": "Commoner" if npc_type == NPCType.MINOR else "Fighter",
            "role": npc_role.value,
            "level": 1 if npc_type == NPCType.MINOR else random.randint(1, 5),
            "alignment": "Neutral",
            "appearance": f"A typical {npc_role.value}",
            "personality": "Straightforward and practical",
            "backstory": f"A {npc_role.value} with local connections",
            "motivation": "Maintaining their position",
            "secret": "Nothing significant",
            "abilities": {
                "strength": 10, "dexterity": 10, "constitution": 10,
                "intelligence": 10, "wisdom": 10, "charisma": 10
            },
            "skills": ["Insight", "Perception"],
            "equipment": ["Simple clothes", "Belt pouch"],
            "special_abilities": [],
            "challenge_rating": 0.0 if npc_type == NPCType.MINOR else 0.25,
            "hit_points": 4 if npc_type == NPCType.MINOR else 11,
            "armor_class": 10,
            "languages": ["Common"],
            "location": "Local area",
            "relationships": "Local community",
            "quirks": ["Speaks quickly when nervous"]
        }
    
    # _validate_and_enhance_npc method moved to creation_validation.py

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def create_npc_from_prompt(prompt: str, npc_type: NPCType = NPCType.MINOR) -> CreationResult:
    """Utility function for simple NPC creation."""
    creator = NPCCreator()
    return await creator.create_npc(prompt, npc_type)

"""
D&D 5e 2024 Item Creation Module - Refactored

This module provides item creation workflow using shared components
to eliminate code duplication. It handles the complete item creation
process including validation, generation, and level-appropriate content.

Key goals:
- Ensure items are consistent with character concepts
- Ensure items are appropriate for character level
- Generate weapons, armor, spells, and magic items
- Integrate with custom content models

Uses shared_character_generation.py for all common logic.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

# ============================================================================
# ITEM CORE CLASSES
# ============================================================================

@dataclass
class ItemCore:
    """Base class for all D&D items."""
    name: str
    item_type: ItemType
    description: str
    rarity: ItemRarity = ItemRarity.COMMON
    requires_attunement: bool = False
    weight: float = 0.0
    value: int = 0  # in copper pieces
    properties: List[str] = None
    
    def __post_init__(self):
        if self.properties is None:
            self.properties = []

@dataclass
class WeaponCore(ItemCore):
    """D&D weapon implementation."""
    category: WeaponCategory = WeaponCategory.SIMPLE_MELEE
    damage_dice: str = "1d4"
    damage_type: str = "bludgeoning"
    weapon_range: str = "5 feet"  # melee range or ranged distance
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.WEAPON

@dataclass
class ArmorCore(ItemCore):
    """D&D armor implementation."""
    category: ArmorCategory = ArmorCategory.LIGHT
    armor_class_base: int = 10
    dex_bonus_limit: Optional[int] = None  # None means no limit
    strength_requirement: int = 0
    stealth_disadvantage: bool = False
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.ARMOR

@dataclass
class SpellCore(ItemCore):
    """D&D spell implementation."""
    level: int = 0  # 0 for cantrips
    school: str = "abjuration"
    casting_time: str = "1 action"
    spell_range: str = "self"
    components: List[str] = None
    duration: str = "instantaneous"
    classes: List[str] = None  # Which classes can cast this spell
    
    def __post_init__(self):
        super().__post_init__()
        self.item_type = ItemType.SPELL
        if self.components is None:
            self.components = ["V", "S"]
        if self.classes is None:
            self.classes = ["Wizard"]

# ============================================================================
# ITEM CREATOR CLASS
# ============================================================================

class ItemCreator:
    """
    D&D 5e 2024 Item Creation Service with LLM Integration.
    Creates level-appropriate items that fit character concepts.
    Uses shared components to eliminate code duplication.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, 
                 config: Optional[CreationConfig] = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize shared components
        self.validator = CharacterValidator()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.content_registry = ContentRegistry()
        self.content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        self.magic_item_manager = MagicItemManager()
        
        logger.info("ItemCreator initialized with shared components")
    
    async def create_item(self, description: str, item_type: ItemType, 
                   character_level: int = 1, character_concept: str = "",
                   rarity: Optional[ItemRarity] = None) -> CreationResult:
        """
        Create an item that fits the character concept and level.
        
        Args:
            description: Description of the desired item
            item_type: Type of item to create
            character_level: Level of the character (affects item power)
            character_concept: Brief description of the character concept
            rarity: Desired rarity (auto-determined if None)
            
        Returns:
            CreationResult with item data
        """
        start_time = time.time()
        
        try:
            logger.info(f"Creating {item_type.value}: {description}")
            
            # Determine appropriate rarity for level
            if rarity is None:
                rarity = self._determine_rarity_for_level(character_level)
            
            # Create item-specific prompt
            item_prompt = self._create_item_prompt(
                description, item_type, character_level, character_concept, rarity
            )
            
            # Use shared data generator with item preferences
            item_preferences = {
                "content_type": "item",
                "item_type": item_type.value,
                "character_level": character_level,
                "rarity": rarity.value,
                "character_concept": character_concept
            }
            
            result = await self.data_generator.generate_character_data(item_prompt, item_preferences)
            
            if result.success:
                # Build item from generated data
                item_core = self._build_item_from_data(result.data, item_type, rarity)
                
                # Validate item is appropriate for level
                validation_result = validate_item_for_level(item_core, character_level, self._determine_rarity_for_level)
                if not validation_result.success:
                    result.add_warning(f"Item validation warning: {validation_result.error}")
                
                # Update result with item data
                result.data = {
                    "item_core": item_core,
                    "item_stats": self._get_item_stats(item_core),
                    "raw_data": result.data
                }
                
                result.creation_time = time.time() - start_time
                logger.info(f"Item creation completed in {result.creation_time:.2f}s")
            
            return result
            
        except Exception as e:
            logger.error(f"Item creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Item creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def create_item_set(self, character_data: Dict[str, Any]) -> CreationResult:
        """Create a complete set of items for a character."""
        start_time = time.time()
        items = {}
        warnings = []
        
        try:
            character_level = character_data.get("level", 1)
            character_concept = self._extract_character_concept(character_data)
            
            # Create weapons
            if self._needs_weapons(character_data):
                weapon_result = self.create_item(
                    f"Primary weapon for {character_concept}",
                    ItemType.WEAPON,
                    character_level,
                    character_concept
                )
                if weapon_result.success:
                    items["primary_weapon"] = weapon_result.data
                else:
                    warnings.append(f"Failed to create weapon: {weapon_result.error}")
            
            # Create armor
            if self._needs_armor(character_data):
                armor_result = self.create_item(
                    f"Armor for {character_concept}",
                    ItemType.ARMOR,
                    character_level,
                    character_concept
                )
                if armor_result.success:
                    items["armor"] = armor_result.data
                else:
                    warnings.append(f"Failed to create armor: {armor_result.error}")
            
            # Create spells if spellcaster
            if self._is_spellcaster(character_data):
                spell_result = self.create_item(
                    f"Signature spell for {character_concept}",
                    ItemType.SPELL,
                    character_level,
                    character_concept
                )
                if spell_result.success:
                    items["signature_spell"] = spell_result.data
                else:
                    warnings.append(f"Failed to create spell: {spell_result.error}")
            
            # Create magic item for higher levels
            if character_level >= 5:
                magic_item_result = self.create_item(
                    f"Magic item for {character_concept}",
                    ItemType.MAGIC_ITEM,
                    character_level,
                    character_concept
                )
                if magic_item_result.success:
                    items["magic_item"] = magic_item_result.data
                else:
                    warnings.append(f"Failed to create magic item: {magic_item_result.error}")
            
            result = CreationResult(success=True, data={"items": items})
            result.warnings = warnings
            result.creation_time = time.time() - start_time
            
            return result
            
        except Exception as e:
            logger.error(f"Item set creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Item set creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _determine_rarity_for_level(self, level: int) -> ItemRarity:
        """Determine appropriate item rarity for character level."""
        if level <= 4:
            return ItemRarity.COMMON
        elif level <= 8:
            return ItemRarity.UNCOMMON
        elif level <= 12:
            return ItemRarity.RARE
        elif level <= 16:
            return ItemRarity.VERY_RARE
        else:
            return ItemRarity.LEGENDARY
    
    def _create_item_prompt(self, description: str, item_type: ItemType,
                           character_level: int, character_concept: str,
                           rarity: ItemRarity) -> str:
        """Create item-specific prompt for generation."""
        prompt_parts = [
            f"Create a D&D 5e 2024 {item_type.value}: {description}",
            f"Character Level: {character_level}",
            f"Character Concept: {character_concept}",
            f"Item Rarity: {rarity.value}",
        ]
        
        # Add item-type specific guidance
        if item_type == ItemType.WEAPON:
            prompt_parts.extend([
                "Include:",
                "- Appropriate damage dice for level and rarity",
                "- Weapon properties (finesse, versatile, etc.)",
                "- Special abilities if magical",
                "- Weight and value"
            ])
        elif item_type == ItemType.ARMOR:
            prompt_parts.extend([
                "Include:",
                "- Appropriate AC for armor type",
                "- Strength requirements if heavy armor",
                "- Special properties if magical",
                "- Weight and value"
            ])
        elif item_type == ItemType.SPELL:
            prompt_parts.extend([
                "Include:",
                "- Appropriate spell level for character level",
                "- School of magic",
                "- Casting time, range, duration",
                "- Components (V, S, M)",
                "- Spell description and effects"
            ])
        elif item_type == ItemType.MAGIC_ITEM:
            prompt_parts.extend([
                "Include:",
                "- Appropriate power level for character level",
                "- Attunement requirement if needed",
                "- Charges or uses per day if applicable",
                "- Activation method"
            ])
        
        prompt_parts.extend([
            f"Ensure the item fits the character concept: {character_concept}",
            "Follow D&D 5e 2024 item format and balance guidelines."
        ])
        
        return "\n".join(prompt_parts)
    
    def _build_item_from_data(self, item_data: Dict[str, Any], 
                             item_type: ItemType, rarity: ItemRarity) -> ItemCore:
        """Build ItemCore from generated data."""
        name = item_data.get("name", "Unknown Item")
        description = item_data.get("description", "")
        
        # Create appropriate item type
        if item_type == ItemType.WEAPON:
            item = WeaponCore(
                name=name,
                item_type=ItemType.WEAPON,
                description=description,
                rarity=rarity,
                damage_dice=item_data.get("damage_dice", "1d6"),
                damage_type=item_data.get("damage_type", "slashing"),
                weapon_range=item_data.get("range", "5 feet")
            )
            
            # Set weapon category
            if "category" in item_data:
                try:
                    item.category = WeaponCategory(item_data["category"])
                except ValueError:
                    logger.warning(f"Unknown weapon category: {item_data['category']}")
                    
        elif item_type == ItemType.ARMOR:
            item = ArmorCore(
                name=name,
                item_type=ItemType.ARMOR,
                description=description,
                rarity=rarity,
                armor_class_base=item_data.get("armor_class", 11),
                dex_bonus_limit=item_data.get("dex_bonus_limit"),
                strength_requirement=item_data.get("strength_requirement", 0),
                stealth_disadvantage=item_data.get("stealth_disadvantage", False)
            )
            
            # Set armor category
            if "category" in item_data:
                try:
                    item.category = ArmorCategory(item_data["category"])
                except ValueError:
                    logger.warning(f"Unknown armor category: {item_data['category']}")
                    
        elif item_type == ItemType.SPELL:
            item = SpellCore(
                name=name,
                item_type=ItemType.SPELL,
                description=description,
                rarity=rarity,
                level=item_data.get("level", 1),
                school=item_data.get("school", "evocation"),
                casting_time=item_data.get("casting_time", "1 action"),
                spell_range=item_data.get("range", "60 feet"),
                components=item_data.get("components", ["V", "S"]),
                duration=item_data.get("duration", "instantaneous"),
                classes=item_data.get("classes", ["Wizard"])
            )
        else:
            # Generic item
            item = ItemCore(
                name=name,
                item_type=item_type,
                description=description,
                rarity=rarity
            )
        
        # Set common properties
        item.requires_attunement = item_data.get("requires_attunement", False)
        item.weight = item_data.get("weight", 0.0)
        item.value = item_data.get("value", 0)
        item.properties = item_data.get("properties", [])
        
        return item
    
    # _validate_item_for_level method moved to creation_validation.py
    
    def _get_item_stats(self, item: ItemCore) -> Dict[str, Any]:
        """Get item statistics for display."""
        stats = {
            "name": item.name,
            "type": item.item_type.value,
            "rarity": item.rarity.value,
            "description": item.description,
            "weight": item.weight,
            "value": item.value,
            "properties": item.properties,
            "requires_attunement": item.requires_attunement
        }
        
        # Add type-specific stats
        if isinstance(item, WeaponCore):
            stats.update({
                "damage_dice": item.damage_dice,
                "damage_type": item.damage_type,
                "range": item.weapon_range,
                "category": item.category.value
            })
        elif isinstance(item, ArmorCore):
            stats.update({
                "armor_class": item.armor_class_base,
                "dex_bonus_limit": item.dex_bonus_limit,
                "strength_requirement": item.strength_requirement,
                "stealth_disadvantage": item.stealth_disadvantage,
                "category": item.category.value
            })
        elif isinstance(item, SpellCore):
            stats.update({
                "level": item.level,
                "school": item.school,
                "casting_time": item.casting_time,
                "range": item.spell_range,
                "components": item.components,
                "duration": item.duration,
                "classes": item.classes
            })
        
        return stats
    
    def _extract_character_concept(self, character_data: Dict[str, Any]) -> str:
        """Extract a brief character concept from character data."""
        parts = []
        
        if "species" in character_data:
            parts.append(character_data["species"])
        
        if "classes" in character_data:
            classes = character_data["classes"]
            if isinstance(classes, dict):
                primary_class = max(classes.items(), key=lambda x: x[1])[0]
                parts.append(primary_class)
            elif isinstance(classes, list) and classes:
                parts.append(classes[0])
        
        if "background" in character_data:
            parts.append(character_data["background"])
        
        return " ".join(parts) if parts else "adventurer"
    
    def _needs_weapons(self, character_data: Dict[str, Any]) -> bool:
        """Check if character needs weapons."""
        # Most characters need weapons, spellcasters might not need as many
        return True
    
    def _needs_armor(self, character_data: Dict[str, Any]) -> bool:
        """Check if character needs armor."""
        # Most characters need armor
        return True
    
    def _is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character is a spellcaster."""
        spellcasting_classes = ["wizard", "sorcerer", "warlock", "cleric", "druid", 
                               "bard", "paladin", "ranger", "artificer", "eldritch knight", 
                               "arcane trickster"]
        
        classes = character_data.get("classes", [])
        if isinstance(classes, dict):
            class_names = list(classes.keys())
        elif isinstance(classes, list):
            class_names = classes
        else:
            return False
        
        return any(cls.lower() in spellcasting_classes for cls in class_names)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

async def create_item_from_prompt(prompt: str, item_type: ItemType = ItemType.MAGIC_ITEM,
                           character_level: int = 1) -> CreationResult:
    """Utility function for simple item creation."""
    creator = ItemCreator()
    return await creator.create_item(prompt, item_type, character_level)

def create_character_items(character_data: Dict[str, Any]) -> CreationResult:
    """Create a complete item set for a character."""
    creator = ItemCreator()
    return creator.create_item_set(character_data)

"""
D&D 5e 2024 Creature Creation Module with LLM Integration.
Comprehensive creature generation following D&D 5e 2024 stat block format.
Uses shared components to eliminate code duplication.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass

# ============================================================================
# CREATURE CORE CLASS
# ============================================================================

class CreatureCore:
    """
    D&D 5e 2024 Creature stat block implementation.
    Contains all attributes required for a complete creature definition.
    """
    
# TODO: In D&D 5e (2024), mounts are creatures at least one size larger than the rider, with suitable anatomy, that allow the rider to move and act on their turn. A controlled mount's initiative matches the rider's, and it can use Dash, Disengage, or Dodge actions. Independent mounts retain their own initiative and actions. Riders can mount or dismount, and must make a saving throw if the mount is moved against its will or if the rider is knocked prone while mounted

    def __init__(self, name: str):
        # Basic Information
        self.name = name
        self.size = CreatureSize.MEDIUM
        self.creature_type = CreatureType.HUMANOID
        self.alignment = CreatureAlignment.TRUE_NEUTRAL
        
        # Core Stats
        self.armor_class = 10
        self.hit_points = 10
        self.hit_dice = "2d8+2"
        self.speed = {"walk": 30}
        
        # Ability Scores
        self.strength = AbilityScore(10)
        self.dexterity = AbilityScore(10)
        self.constitution = AbilityScore(10)
        self.intelligence = AbilityScore(10)
        self.wisdom = AbilityScore(10)
        self.charisma = AbilityScore(10)
        
        # Combat Stats
        self.challenge_rating = 0.0
        self.proficiency_bonus = 2
        
        # Skills and Proficiencies
        self.saving_throws = {}
        self.skills = {}
        self.damage_vulnerabilities = []
        self.damage_resistances = []
        self.damage_immunities = []
        self.condition_immunities = []
        self.senses = {"passive_perception": 10}
        self.languages = ["Common"]
        
        # Abilities and Actions
        self.special_abilities = []
        self.actions = []
        self.bonus_actions = []
        self.reactions = []
        self.legendary_actions = []
        
        # Lore and Flavor
        self.description = ""
        self.tactics = ""
        self.habitat = ""
        self.treasure = ""

# ============================================================================
# CREATURE CREATOR CLASS
# ============================================================================

class CreatureCreator:
    """
    D&D 5e 2024 Creature Creation Service with LLM Integration.
    Generates complete stat blocks following D&D 5e 2024 format.
    Uses shared components to eliminate code duplication.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, 
                 config: Optional[CreationConfig] = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize shared components
        self.validator = CharacterValidator()
        
        logger.info("CreatureCreator initialized with LLM integration")
    
    def create_creature(self, description: str, challenge_rating: float = 1.0, 
                       creature_type: str = "beast") -> CreationResult:
        """Create a complete D&D 5e 2024 creature using LLM generation."""
        start_time = time.time()
        
        try:
            logger.info(f"Creating unique creature: {description[:50]}... (CR {challenge_rating})")
            
            # Generate unique creature using LLM
            creature_data = self._generate_unique_creature_with_llm(description, challenge_rating, creature_type)
            
            # Validate and enhance the generated creature
            validated_data = validate_and_enhance_creature(creature_data, challenge_rating)
            
            # Create successful result
            result = CreationResult()
            result.success = True
            result.data = validated_data
            result.creation_time = time.time() - start_time
            result.warnings = []
            
            logger.info(f"Unique creature creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Creature creation failed: {str(e)}")
            result = CreationResult()
            result.success = False
            result.error = f"Creature creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    def _generate_unique_creature_with_llm(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Generate a unique creature using LLM services."""
        if not self.llm_service:
            raise ValueError("LLM service not available for creature generation")
        
        # Create specialized prompt for creature generation
        specialized_prompt = f"""
        Generate a unique D&D 5e creature based on this description: {description}
        
        Challenge Rating: {challenge_rating}
        Creature Type: {creature_type}
        
        IMPORTANT: Return ONLY valid JSON in this exact format:
        {{
            "name": "Unique creature name",
            "size": "Tiny/Small/Medium/Large/Huge/Gargantuan",
            "type": "{creature_type}",
            "alignment": "D&D alignment",
            "challenge_rating": {challenge_rating},
            "armor_class": 8-25,
            "hit_points": 1-500,
            "speed": {{
                "walk": "30 ft",
                "fly": "0 ft",
                "swim": "0 ft"
            }},
            "abilities": {{
                "strength": 1-30,
                "dexterity": 1-30,
                "constitution": 1-30,
                "intelligence": 1-30,
                "wisdom": 1-30,
                "charisma": 1-30
            }},
            "saving_throws": ["Str +X", "Dex +X"],
            "skills": ["Perception +X", "Stealth +X"],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["darkvision 60 ft", "passive Perception X"],
            "languages": ["Common", "other languages"],
            "proficiency_bonus": 2-9,
            "description": "Detailed creature description",
            "behavior": "How the creature acts",
            "habitat": "Where it lives",
            "diet": "What it eats",
            "actions": [
                {{
                    "name": "Action Name",
                    "description": "Action description with mechanics",
                    "attack_bonus": "+X to hit",
                    "damage": "XdY + Z damage type",
                    "range": "5 ft or ranged"
                }}
            ],
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "special_abilities": [
                {{
                    "name": "Ability Name",
                    "description": "Ability description and mechanics"
                }}
            ]
        }}
        
        Make this creature unique, memorable, and balanced for CR {challenge_rating}.
        Include appropriate abilities, attacks, and special features.
        """
        
        # Get LLM response
        response = self.llm_service.generate_content(specialized_prompt)
        
        # Parse JSON response
        try:
            # Extract JSON from response
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                creature_data = json.loads(json_str)
                logger.info(f"Successfully generated unique creature: {creature_data.get('name', 'Unknown')}")
                return creature_data
            else:
                raise ValueError("Could not find valid JSON in LLM response")
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            # Fallback to basic creature structure
            return self._create_fallback_creature(description, challenge_rating, creature_type)
        except Exception as e:
            logger.error(f"Error processing LLM response: {e}")
            return self._create_fallback_creature(description, challenge_rating, creature_type)
    
    def _create_fallback_creature(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Create a basic creature when LLM generation fails."""
        import random
        
        # Basic creature names by type
        creature_names = {
            "beast": ["Wild Beast", "Forest Creature", "Mountain Beast"],
            "monstrosity": ["Strange Monstrosity", "Twisted Creature", "Aberrant Beast"],
            "undead": ["Undead Horror", "Restless Spirit", "Skeletal Creature"],
            "dragon": ["Young Dragon", "Dragonling", "Lesser Wyrm"],
            "elemental": ["Elemental Being", "Primal Force", "Nature Spirit"],
            "fey": ["Fey Creature", "Forest Spirit", "Magical Being"],
            "fiend": ["Lesser Fiend", "Demonic Creature", "Infernal Beast"],
            "celestial": ["Celestial Being", "Divine Creature", "Heavenly Spirit"]
        }
        
        # Calculate basic stats based on CR
        cr_adjustments = {
            "hp": max(10, int(challenge_rating * 20 + 10)),
            "ac": max(10, int(challenge_rating + 10)),
            "attack_bonus": max(2, int(challenge_rating + 2)),
            "damage": max(1, int(challenge_rating * 2 + 1))
        }
        
        return {
            "name": random.choice(creature_names.get(creature_type, ["Generic Creature"])),
            "size": "Medium",
            "type": creature_type,
            "alignment": "neutral",
            "challenge_rating": challenge_rating,
            "armor_class": cr_adjustments["ac"],
            "hit_points": cr_adjustments["hp"],
            "speed": {"walk": "30 ft", "fly": "0 ft", "swim": "0 ft"},
            "abilities": {
                "strength": 12, "dexterity": 12, "constitution": 12,
                "intelligence": 8, "wisdom": 12, "charisma": 8
            },
            "saving_throws": [],
            "skills": ["Perception +2"],
            "damage_vulnerabilities": [],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["passive Perception 12"],
            "languages": [],
            "proficiency_bonus": max(2, int((challenge_rating + 7) / 4)),
            "description": f"A {creature_type} creature",
            "behavior": "Acts according to its nature",
            "habitat": "Various environments",
            "diet": "Omnivore",
            "actions": [
                {
                    "name": "Basic Attack",
                    "description": "A simple attack",
                    "attack_bonus": f"+{cr_adjustments['attack_bonus']} to hit",
                    "damage": f"{cr_adjustments['damage']}d6 bludgeoning",
                    "range": "5 ft"
                }
            ],
            "legendary_actions": [],
            "lair_actions": [],
            "regional_effects": [],
            "special_abilities": []
        }
    
    def _validate_and_enhance_creature(self, creature_data: Dict[str, Any], challenge_rating: float) -> Dict[str, Any]:
        """Validate and enhance the generated creature data."""
        # Method implementation moved to creation_validation.py
        return validate_and_enhance_creature(creature_data, challenge_rating)

# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def create_creature_from_prompt(prompt: str, challenge_rating: float = 1.0) -> CreationResult:
    """Utility function for simple creature creation."""
    creator = CreatureCreator()
    return creator.create_creature(prompt, challenge_rating)


"""
Shared Character Generation Components

This module contains all the shared functionality used across character_creation.py,
npc_creation.py, creature_creation.py, and items_creation.py to eliminate code duplication.

Core Components:
- CreationConfig and CreationResult classes
- CharacterValidator for validation logic
- CharacterDataGenerator for LLM-based generation
- JournalBasedEvolution for character evolution
- Shared utility functions

All other modules should import from this module instead of duplicating code.
"""

import json
import logging
import time
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet, CharacterStats
from core_models import AbilityScore, ASIManager, MagicItemManager, CharacterLevelManager, ProficiencyLevel
from custom_content_models import ContentRegistry, FeatManager
from ability_management import AdvancedAbilityManager
from llm_service import create_llm_service, LLMService
from generators import BackstoryGenerator, CustomContentGenerator

logger = logging.getLogger(__name__)

# ============================================================================
# SHARED CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Handles validation of character data."""
    
    @staticmethod
    def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
        """Validate basic character data structure."""
        # Method implementation moved to creation_validation.py
        return validate_basic_structure(character_data)
    
    @staticmethod
    def validate_custom_content(character_data: Dict[str, Any], 
                              needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
        """Validate that custom content requirements are met."""
        # Method implementation moved to creation_validation.py
        return validate_custom_content(character_data, needs_custom_species, needs_custom_class)

# ============================================================================
# SHARED CHARACTER DATA GENERATOR
# ============================================================================

class CharacterDataGenerator:
    """Handles core character data generation using LLM services."""
    
    def __init__(self, llm_service: LLMService, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    async def generate_character_data(self, description: str, level: int) -> CreationResult:
        """Generate core character data with retry logic."""
        start_time = time.time()
        
        needs_custom_species = self._needs_custom_species(description)
        needs_custom_class = self._needs_custom_class(description)
        
        # Create targeted prompt
        prompt = self._create_character_prompt(description, level, needs_custom_species, needs_custom_class)
        
        for attempt in range(self.config.max_retries):
            try:
                logger.info(f"Character generation attempt {attempt + 1}/{self.config.max_retries}")
                
                timeout = max(self.config.base_timeout - (attempt * 5), 10)
                response = await self.llm_service.generate_content(prompt)
                
                # Clean and parse response
                cleaned_response = self._clean_json_response(response)
                character_data = json.loads(cleaned_response)
                character_data["level"] = level
                
                logger.info(f"Before data structure fix - backstory type: {type(character_data.get('backstory'))}, equipment type: {type(character_data.get('equipment'))}")
                
                # Fix data structure mismatches
                character_data = self._fix_data_structure(character_data)
                
                logger.info(f"After data structure fix - backstory type: {type(character_data.get('backstory'))}, equipment type: {type(character_data.get('equipment'))}")
                
                # Validate basic structure
                validation_result = self.validator.validate_basic_structure(character_data)
                if not validation_result.success:
                    if attempt < self.config.max_retries - 1:
                        logger.warning(f"Validation failed: {validation_result.error}, retrying...")
                        continue
                    else:
                        character_data = self._apply_fixes(character_data, description, level)
                
                # Validate custom content requirements
                custom_validation = self.validator.validate_custom_content(
                    character_data, needs_custom_species, needs_custom_class
                )
                
                result = CreationResult(success=True, data=character_data)
                result.warnings.extend(validation_result.warnings + custom_validation.warnings)
                result.creation_time = time.time() - start_time
                
                logger.info("Character generation successful")
                return result
                
            except (TimeoutError, json.JSONDecodeError) as e:
                logger.warning(f"Attempt {attempt + 1} failed: {e}")
                if attempt < self.config.max_retries - 1:
                    prompt = self._get_simplified_prompt(description, level)
                    continue
                else:
                    logger.error("All attempts failed, using fallback")
                    return self._get_fallback_result(description, level, start_time)
            
            except Exception as e:
                logger.error(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == self.config.max_retries - 1:
                    return self._get_fallback_result(description, level, start_time)
        
        return self._get_fallback_result(description, level, start_time)
    
    def _needs_custom_species(self, description: str) -> bool:
        """Determine if description requires custom species."""
        custom_keywords = ["unique", "custom", "new species", "homebrew", "original", "invented"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _needs_custom_class(self, description: str) -> bool:
        """Determine if description requires custom class."""
        custom_keywords = ["custom class", "homebrew class", "new class", "unique class"]
        description_lower = description.lower()
        return any(keyword in description_lower for keyword in custom_keywords)
    
    def _create_character_prompt(self, description: str, level: int, 
                               needs_custom_species: bool, needs_custom_class: bool) -> str:
        """Create optimized character generation prompt."""
        
        custom_instructions = ""
        if needs_custom_species:
            custom_instructions += "CREATE custom species name matching description. "
        if needs_custom_class:
            custom_instructions += "CREATE custom class name matching description. "
        
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}
{custom_instructions}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Skill1","Skill2"],"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":[{{"name":"Item","quantity":1}}],"backstory":"Brief backstory"}}

Match description exactly. Return complete JSON only."""
    
    def _get_simplified_prompt(self, description: str, level: int) -> str:
        """Get simplified prompt for retry attempts."""
        return f"""Character: {description}, Level {level}
JSON: {{"name":"Name","species":"Human","level":{level},"classes":{{"Fighter":{level}}},"background":"Folk Hero","alignment":["Neutral","Good"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Athletics"],"personality_traits":["Brave"],"ideals":["Justice"],"bonds":["Community"],"flaws":["Stubborn"],"armor":"Leather","weapons":[{{"name":"Sword","damage":"1d8","properties":["versatile"]}}],"equipment":[{{"name":"Pack","quantity":1}}],"backstory":"A brave {description} warrior."}}"""
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response."""
        if not response:
            raise ValueError("Empty response")
        
        # Remove markdown and find JSON boundaries
        response = response.replace('```json', '').replace('```', '').strip()
        
        first_brace = response.find('{')
        last_brace = response.rfind('}')
        
        if first_brace == -1 or last_brace == -1:
            raise ValueError("No JSON found in response")
        
        json_str = response[first_brace:last_brace + 1]
        
        # Basic JSON repair
        open_braces = json_str.count('{')
        close_braces = json_str.count('}')
        
        if open_braces > close_braces:
            json_str += '}' * (open_braces - close_braces)
        
        return json_str
    
    def _fix_data_structure(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix data structure mismatches between LLM output and model expectations."""
        
        # Fix species: should be string, not list
        if isinstance(character_data.get("species"), list):
            species_list = character_data["species"]
            character_data["species"] = species_list[0] if species_list else "Human"
        
        # Fix character_classes: should be dict, not list
        if isinstance(character_data.get("character_classes"), list):
            classes_list = character_data["character_classes"]
            if classes_list:
                # Convert list to dict format
                character_data["character_classes"] = {classes_list[0]: character_data.get("level", 1)}
            else:
                character_data["character_classes"] = {"Fighter": character_data.get("level", 1)}
        elif isinstance(character_data.get("classes"), dict):
            # LLM sometimes returns "classes" instead of "character_classes"
            character_data["character_classes"] = character_data["classes"]
        
        # Fix backstory: should be string, not dict
        if isinstance(character_data.get("backstory"), dict):
            backstory_dict = character_data["backstory"]
            # Extract main backstory text from dict
            if "main_backstory" in backstory_dict:
                character_data["backstory"] = backstory_dict["main_backstory"]
            elif "backstory" in backstory_dict:
                character_data["backstory"] = backstory_dict["backstory"]
            elif "description" in backstory_dict:
                character_data["backstory"] = backstory_dict["description"]
            else:
                # Combine all text values from the dict
                text_parts = [str(v) for v in backstory_dict.values() if isinstance(v, str)]
                character_data["backstory"] = " ".join(text_parts) if text_parts else "A mysterious adventurer."
        
        # Fix equipment: should be dict, not list
        if isinstance(character_data.get("equipment"), list):
            equipment_list = character_data["equipment"]
            equipment_dict = {}
            logger.debug(f"Converting equipment list to dict: {equipment_list}")
            for i, item in enumerate(equipment_list):
                if isinstance(item, dict) and "name" in item:
                    item_name = item["name"]
                    quantity = item.get("quantity", 1)
                    equipment_dict[item_name] = quantity
                elif isinstance(item, str):
                    equipment_dict[item] = 1
                else:
                    equipment_dict[f"Item_{i}"] = 1
            character_data["equipment"] = equipment_dict
            logger.debug(f"Converted equipment to dict: {equipment_dict}")
        
        # Ensure equipment is a dict (fallback)
        if not isinstance(character_data.get("equipment"), dict):
            character_data["equipment"] = {"Adventurer's Pack": 1}
        
        # Fix alignment: ensure it's a list of two strings
        if isinstance(character_data.get("alignment"), str):
            # Split string alignment like "Neutral Good" into ["Neutral", "Good"]
            alignment_parts = character_data["alignment"].split()
            if len(alignment_parts) >= 2:
                character_data["alignment"] = [alignment_parts[0], alignment_parts[1]]
            else:
                character_data["alignment"] = ["Neutral", "Good"]
        elif not isinstance(character_data.get("alignment"), list):
            character_data["alignment"] = ["Neutral", "Good"]
        
        return character_data
    
    def _apply_fixes(self, character_data: Dict[str, Any], description: str, level: int) -> Dict[str, Any]:
        """Apply fixes for common character data issues."""
        
        # Fix missing fields with defaults
        defaults = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "classes": {"Fighter": level},
            "ability_scores": {
                "strength": 13, "dexterity": 12, "constitution": 14,
                "intelligence": 11, "wisdom": 10, "charisma": 8
            },
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "skill_proficiencies": ["Athletics"],
            "personality_traits": ["Determined"],
            "ideals": ["Justice"],
            "bonds": ["Hometown"],
            "flaws": ["Stubborn"],
            "armor": "Leather",
            "weapons": [{"name": "Sword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": {"Adventurer's Pack": 1},  # Changed from list to dict
            "backstory": f"A {description} seeking adventure."
        }
        
        for key, value in defaults.items():
            if key not in character_data or not character_data[key]:
                character_data[key] = value
        
        return character_data
    
    def _generate_name_from_description(self, description: str) -> str:
        """Generate a simple name from description."""
        words = description.split()
        if words:
            return words[0].capitalize() + " " + ("Adventurer" if len(words) == 1 else words[-1].capitalize())
        return "Unknown Adventurer"
    
    def _get_fallback_result(self, description: str, level: int, start_time: float) -> CreationResult:
        """Create a fallback character when generation fails."""
        fallback_data = {
            "name": self._generate_name_from_description(description),
            "species": "Human",
            "level": level,
            "classes": {"Fighter": level},
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "ability_scores": {
                "strength": 15, "dexterity": 13, "constitution": 14,
                "intelligence": 12, "wisdom": 10, "charisma": 8
            },
            "skill_proficiencies": ["Athletics", "Intimidation"],
            "personality_traits": ["Brave and determined"],
            "ideals": ["Justice for all"],
            "bonds": ["Protecting my community"],
            "flaws": ["Too trusting of others"],
            "armor": "Chain Mail",
            "weapons": [{"name": "Longsword", "damage": "1d8", "properties": ["versatile"]}],
            "equipment": {"Adventurer's Pack": 1},  # Changed from list to dict
            "backstory": f"A fallback character based on: {description}"
        }
        
        result = CreationResult(success=True, data=fallback_data)
        result.add_warning("Used fallback character due to generation failures")
        result.creation_time = time.time() - start_time
        
        return result

# ============================================================================
# SHARED JOURNAL-BASED EVOLUTION
# ============================================================================

class JournalBasedEvolution:
    """Handles character evolution based on journal entries and play history."""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    def analyze_play_patterns(self, journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze journal entries to determine character play patterns."""
        if not journal_entries:
            return {"themes": [], "suggested_evolution": [], "confidence": 0.0}
        
        # Extract text from all journal entries
        journal_text = " ".join([entry.get("entry", "") for entry in journal_entries])
        
        # Enhanced keyword analysis
        analysis_patterns = {
            "stealth_assassin": {
                "keywords": ["sneak", "hide", "assassin", "shadow", "stealth", "backstab", "ambush", "poison", "silent", "dagger"],
                "weight": 1.0
            },
            "social_diplomat": {
                "keywords": ["persuade", "negotiate", "charm", "diplomat", "talk", "convince", "deception", "insight", "court"],
                "weight": 1.0
            },
            "combat_warrior": {
                "keywords": ["fight", "battle", "attack", "combat", "weapon", "armor", "charge", "defend", "warrior", "sword"],
                "weight": 1.0
            },
            "magic_scholar": {
                "keywords": ["spell", "magic", "cast", "ritual", "arcane", "divine", "study", "research", "tome", "scroll"],
                "weight": 1.0
            },
            "explorer_ranger": {
                "keywords": ["explore", "track", "wilderness", "forest", "survival", "nature", "animal", "guide", "scout"],
                "weight": 1.0
            },
            "healer_support": {
                "keywords": ["heal", "cure", "medicine", "help", "support", "protect", "save", "rescue", "tend", "care"],
                "weight": 1.0
            },
            "leader_commander": {
                "keywords": ["lead", "command", "order", "strategy", "tactics", "rally", "inspire", "organize", "direct"],
                "weight": 1.0
            }
        }
        
        text_lower = journal_text.lower()
        detected_themes = {}
        
        for pattern_name, pattern_data in analysis_patterns.items():
            score = sum(text_lower.count(keyword) for keyword in pattern_data["keywords"])
            if score > 0:
                detected_themes[pattern_name] = {
                    "score": score,
                    "confidence": min(score / 10.0, 1.0)  # Cap at 1.0
                }
        
        # Sort themes by score
        sorted_themes = sorted(detected_themes.items(), key=lambda x: x[1]["score"], reverse=True)
        
        return {
            "themes": [{"name": theme, "score": data["score"], "confidence": data["confidence"]} 
                      for theme, data in sorted_themes],
            "total_entries": len(journal_entries),
            "analysis_confidence": min(len(journal_entries) / 20.0, 1.0)  # Higher confidence with more entries
        }
    
    def suggest_character_evolution(self, current_character: Dict[str, Any], 
                                  play_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Suggest character evolution based on play patterns."""
        suggestions = {
            "multiclass_recommendations": [],
            "feat_suggestions": [],
            "skill_focus": [],
            "equipment_changes": [],
            "roleplay_evolution": "",
            "mechanical_changes": []
        }
        
        current_classes = current_character.get("classes", {})
        primary_class = max(current_classes.items(), key=lambda x: x[1])[0] if current_classes else "Fighter"
        
        themes = play_analysis.get("themes", [])
        if not themes:
            return suggestions
        
        top_theme = themes[0]["name"] if themes else None
        
        # Multiclass suggestions based on play patterns
        class_suggestions = {
            "stealth_assassin": ["Rogue", "Ranger", "Shadow Monk"],
            "social_diplomat": ["Bard", "Paladin", "Warlock"],
            "combat_warrior": ["Fighter", "Barbarian", "Paladin"],
            "magic_scholar": ["Wizard", "Sorcerer", "Warlock"],
            "explorer_ranger": ["Ranger", "Druid", "Scout Rogue"],
            "healer_support": ["Cleric", "Druid", "Divine Soul Sorcerer"],
            "leader_commander": ["Paladin", "Bard", "War Cleric"]
        }
        
        if top_theme in class_suggestions:
            for suggested_class in class_suggestions[top_theme]:
                if suggested_class not in current_classes:
                    suggestions["multiclass_recommendations"].append({
                        "class": suggested_class,
                        "reason": f"Journal shows strong {top_theme.replace('_', ' ')} tendencies",
                        "confidence": themes[0]["confidence"]
                    })
        
        # Feat suggestions
        feat_suggestions = {
            "stealth_assassin": ["Skulker", "Alert", "Assassinate", "Shadow Touched"],
            "social_diplomat": ["Actor", "Fey Touched", "Skill Expert", "Inspiring Leader"],
            "combat_warrior": ["Great Weapon Master", "Polearm Master", "Sentinel", "Tough"],
            "magic_scholar": ["Ritual Caster", "Magic Initiate", "Fey Touched", "Telekinetic"],
            "explorer_ranger": ["Sharpshooter", "Mobile", "Observant", "Nature Adept"],
            "healer_support": ["Healer", "Inspiring Leader", "Tough", "Fey Touched"],
            "leader_commander": ["Inspiring Leader", "Rally", "Tactical Mind", "Command"]
        }
        
        if top_theme in feat_suggestions:
            suggestions["feat_suggestions"] = feat_suggestions[top_theme]
        
        # Roleplay evolution
        evolution_descriptions = {
            "stealth_assassin": f"Character has evolved from {primary_class} into a shadow operative, using stealth and precision over brute force.",
            "social_diplomat": f"Character has grown beyond {primary_class} combat focus into a skilled negotiator and social manipulator.",
            "combat_warrior": f"Character has embraced their {primary_class} nature, becoming an exceptional warrior and tactician.",
            "magic_scholar": f"Character has discovered magical aptitude beyond their {primary_class} training, seeking arcane knowledge.",
            "explorer_ranger": f"Character has developed strong wilderness skills, moving beyond typical {primary_class} boundaries.",
            "healer_support": f"Character has found their calling in protecting and healing others, expanding beyond {primary_class} limitations.",
            "leader_commander": f"Character has naturally evolved into a leadership role, inspiring others beyond typical {primary_class} expectations."
        }
        
        if top_theme in evolution_descriptions:
            suggestions["roleplay_evolution"] = evolution_descriptions[top_theme]
        
        return suggestions

# ============================================================================
# SHARED UTILITY FUNCTIONS
# ============================================================================

def build_character_core(character_data: Dict[str, Any]) -> CharacterCore:
    """Build a CharacterCore from character data."""
    
    character_core = CharacterCore(character_data["name"])
    character_core.species = character_data.get("species", "Human")
    character_core.background = character_data.get("background", "Folk Hero")
    character_core.character_classes = character_data.get("classes", {"Fighter": 1})
    character_core.alignment = character_data.get("alignment", ["Neutral", "Good"])
    
    # Set personality traits
    character_core.personality_traits = character_data.get("personality_traits", ["Brave"])
    character_core.ideals = character_data.get("ideals", ["Justice"])
    character_core.bonds = character_data.get("bonds", ["Community"])
    character_core.flaws = character_data.get("flaws", ["Stubborn"])
    
    # Set proficiencies
    skill_profs = character_data.get("skill_proficiencies", [])
    for skill in skill_profs:
        character_core.skill_proficiencies[skill] = ProficiencyLevel.PROFICIENT
    
    # Set ability scores
    ability_scores = character_data.get("ability_scores", {})
    for ability_name, score in ability_scores.items():
        if hasattr(character_core, ability_name):
            setattr(character_core, ability_name, AbilityScore(score))
    
    return character_core

def quick_character_sheet(name: str, species: str = "Human", character_class: str = "Fighter", 
                         level: int = 1, add_journal: bool = True) -> CharacterSheet:
    """Create a simple character sheet quickly without LLM generation."""
    
    character_sheet = CharacterSheet(name)
    character_sheet.core.species = species
    character_sheet.core.character_classes = {character_class: level}
    
    # Set default ability scores
    character_sheet.core.strength = AbilityScore(15)
    character_sheet.core.dexterity = AbilityScore(13)
    character_sheet.core.constitution = AbilityScore(14)
    character_sheet.core.intelligence = AbilityScore(12)
    character_sheet.core.wisdom = AbilityScore(10)
    character_sheet.core.charisma = AbilityScore(8)
    
    # Calculate derived stats
    character_sheet.calculate_all_derived_stats()
    
    # Add initial journal if requested
    if add_journal:
        character_sheet.add_journal_entry(
            f"{name} the {species} {character_class} begins their adventure with determination and hope.",
            tags=["character_creation", "quick_creation"]
        )
    
    return character_sheet

def create_specialized_prompt(content_type: str, description: str, level: int = None) -> str:
    """Create specialized prompts for different content types."""
    
    if content_type == "creature":
        cr_guidance = f"Challenge Rating appropriate for level {level} encounters" if level else "appropriate Challenge Rating"
        return f"""Create D&D 5e 2024 creature. Return ONLY JSON:

DESCRIPTION: {description}
{cr_guidance}

Include: name, size, type, challenge_rating, armor_class, hit_points, speed, ability_scores, saving_throws, skills, damage_resistances, damage_immunities, condition_immunities, senses, languages, special_abilities, actions, legendary_actions, lair_actions, regional_effects

Match description exactly. Return complete JSON only."""
    
    elif content_type == "item":
        rarity_guidance = f"Rarity appropriate for level {level} characters" if level else "appropriate rarity"
        return f"""Create D&D 5e 2024 magic item. Return ONLY JSON:

DESCRIPTION: {description}
{rarity_guidance}

Include: name, type, rarity, requires_attunement, description, properties, mechanics, cost, weight

Match description exactly. Return complete JSON only."""
    
    elif content_type == "spell":
        spell_level = min((level or 1) // 2, 9) if level else 1
        return f"""Create D&D 5e 2024 spell. Return ONLY JSON:

DESCRIPTION: {description}
Spell level: {spell_level} or lower

Include: name, level, school, casting_time, range, components, duration, description, at_higher_levels, classes

Match description exactly. Return complete JSON only."""
    
    elif content_type == "backstory":
        return f"""Generate a detailed D&D character backstory. Return ONLY JSON:

CHARACTER CONCEPT: {description}
LEVEL: {level or 1}

IMPORTANT: Return only valid JSON in this format:
{{
    "backstory": "A detailed backstory of 2-3 paragraphs...",
    "personality_traits": ["Trait 1", "Trait 2"],
    "ideals": ["Ideal 1"],
    "bonds": ["Bond 1"],
    "flaws": ["Flaw 1"]
}}

Match the character concept exactly. Return complete JSON only."""
    
    else:  # Default to character
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level or 1}

Match description exactly. Return complete JSON only."""

