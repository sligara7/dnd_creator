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
from backend.creation_validation import (
    validate_basic_structure, validate_custom_content,
    validate_and_enhance_npc, validate_item_for_level,
    validate_and_enhance_creature
)

# Import from centralized enums
from backend.enums import (
    NPCType, NPCRole, NPCSpecies, NPCClass, CreatureType, CreatureSize, CreatureAlignment,
    ItemType, ItemRarity, WeaponCategory, ArmorCategory, FeatCategory, FeatType, FeatPrerequisite,
    Skill, SkillAbilityMapping, SkillSource
)

# Import core D&D components
from backend.core_models import AbilityScore, ProficiencyLevel, ASIManager, MagicItemManager
from backend.character_models import CharacterCore  # DnDCondition, CharacterSheet, CharacterState, CharacterStats - may not exist yet
from backend.llm_service import create_llm_service, LLMService
from backend.database_models import CustomContent
from backend.ability_management import AdvancedAbilityManager
from backend.generators import (
    BackstoryGenerator, CustomContentGenerator, CharacterGenerator, 
    NPCGenerator, CreatureGenerator, ItemGenerator
)
from backend.custom_content_models import ContentRegistry, CustomClass

# Import D&D 5e official data
from backend.dnd_data import (
    DND_SPELL_DATABASE, CLASS_SPELL_LISTS, COMPLETE_SPELL_LIST, SPELL_LOOKUP,
    DND_WEAPON_DATABASE, ALL_WEAPONS, WEAPON_LOOKUP, CLASS_WEAPON_PROFICIENCIES,
    DND_FEAT_DATABASE, ALL_FEATS, FEAT_LOOKUP, FEAT_AVAILABILITY,
    DND_ARMOR_DATABASE, ALL_ARMOR, ARMOR_LOOKUP, CLASS_ARMOR_PROFICIENCIES,
    DND_TOOLS_DATABASE, ALL_TOOLS, TOOLS_LOOKUP,
    DND_ADVENTURING_GEAR_DATABASE, ALL_ADVENTURING_GEAR, ADVENTURING_GEAR_LOOKUP, CLASS_EQUIPMENT_PREFERENCES,
    is_existing_dnd_spell, find_similar_spells, is_existing_dnd_weapon, find_similar_weapons,
    is_existing_dnd_feat, find_similar_feats, get_feat_data,
    is_existing_dnd_armor, find_similar_armor, get_armor_data, get_appropriate_armor_for_character,
    is_existing_dnd_tool, find_similar_tools, get_tool_data, get_appropriate_tools_for_character,
    is_existing_dnd_gear, find_similar_gear, get_gear_data, get_appropriate_equipment_pack_for_character,
    get_weapon_data, get_appropriate_spells_for_character, get_appropriate_weapons_for_character,
    get_appropriate_feats_for_character, get_available_feats_for_level,
    get_spell_schools_for_class
)
from backend.creation_validation import validate_feat_prerequisites

logger = logging.getLogger(__name__)

# ============================================================================
# SHARED CONFIGURATION AND RESULT CLASSES  
# ============================================================================

@dataclass
class CreationConfig:
    """Configuration for all creation processes."""
    base_timeout: int = 300
    max_retries: int = 2
    enable_progress_feedback: bool = True
    auto_save: bool = False

class CreationResult:
    """Result container for all creation operations."""
    
    def __init__(self, success: bool = False, data: Dict[str, Any] = None, 
                 error: str = "", warnings: List[str] = None):
        self.success = success
        self.data = data or {}
        self.error = error
        self.warnings = warnings or []
        self.creation_time: float = 0.0
        self.verbose_logs: List[Dict[str, Any]] = []  # For detailed LLM interaction logs
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
    
    def is_valid(self) -> bool:
        """Check if the result is valid."""
        return self.success and bool(self.data)

# ============================================================================
# BASE CREATOR CLASS - FOUNDATION FOR ALL CONTENT TYPES
# ============================================================================

class BaseCreator(ABC):
    """
    Base creator class that provides core functionality for all content types.
    Character creation contains the complete feature set, while other creators
    use subsets of this functionality.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, 
                 config: Optional[CreationConfig] = None):
        self.llm_service = llm_service or create_llm_service("ollama", model="tinyllama:latest", timeout=300)
        self.config = config or CreationConfig()
        
        # Core shared components used by all content types
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.content_registry = ContentRegistry()
        self.custom_content_generator = CustomContentGenerator(self.llm_service, self.content_registry)
        
        # Advanced integrated generators for comprehensive content creation
        self.character_generator = CharacterGenerator(self.llm_service, self.content_registry)
        self.npc_generator = NPCGenerator(self.llm_service, self.content_registry)
        self.creature_generator = CreatureGenerator(self.llm_service, self.content_registry)
        self.item_generator = ItemGenerator(self.llm_service)
        
        logger.info(f"{self.__class__.__name__} initialized with shared components")
    
    async def _generate_with_llm(self, prompt: str, content_type: str = "content") -> Dict[str, Any]:
        """
        Core LLM generation method used by all content types.
        This is the foundation that all creation types build upon.
        """
        import time
        
        for attempt in range(self.config.max_retries):
            try:
                start_time = time.time()
                logger.info(f"LLM generation attempt {attempt + 1}/{self.config.max_retries} for {content_type}")
                
                # Log the prompt being sent for verbose mode
                if hasattr(self, 'verbose_logs'):
                    self.verbose_logs.append({
                        'type': 'llm_request',
                        'timestamp': time.time(),
                        'content_type': content_type,
                        'attempt': attempt + 1,
                        'prompt': prompt,
                        'prompt_length': len(prompt)
                    })
                
                response = await self.llm_service.generate_content(prompt)
                generation_time = time.time() - start_time
                
                cleaned_response = self._clean_json_response(response)
                data = json.loads(cleaned_response)
                
                # Log the response for verbose mode
                if hasattr(self, 'verbose_logs'):
                    self.verbose_logs.append({
                        'type': 'llm_response',
                        'timestamp': time.time(),
                        'content_type': content_type,
                        'attempt': attempt + 1,
                        'raw_response': response,
                        'cleaned_response': cleaned_response,
                        'parsed_data': data,
                        'response_length': len(response),
                        'generation_time': generation_time,
                        'success': True
                    })
                
                logger.info(f"LLM generation successful for {content_type} in {generation_time:.2f}s")
                return data
                
            except (json.JSONDecodeError, Exception) as e:
                generation_time = time.time() - start_time
                
                # Log the failure for verbose mode
                if hasattr(self, 'verbose_logs'):
                    self.verbose_logs.append({
                        'type': 'llm_error',
                        'timestamp': time.time(),
                        'content_type': content_type,
                        'attempt': attempt + 1,
                        'error': str(e),
                        'generation_time': generation_time,
                        'success': False
                    })
                
                logger.warning(f"LLM generation attempt {attempt + 1} failed in {generation_time:.2f}s: {e}")
                if attempt == self.config.max_retries - 1:
                    raise e
        
        raise Exception(f"All LLM generation attempts failed for {content_type}")
    
    def _clean_json_response(self, response: str) -> str:
        """Clean and extract JSON from LLM response - shared by all creators."""
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
    
    def _extract_character_concept(self, character_data: Dict[str, Any]) -> str:
        """Extract character concept - used by all content types."""
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
    
    def _is_spellcaster(self, character_data: Dict[str, Any]) -> bool:
        """Check if character is a spellcaster - used for items and abilities."""
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
    
    def _get_feat_section_for_level(self, level: int) -> str:
        """Get appropriate feat section for character level based on D&D 5e 2024 rules."""
        feat_parts = []
        
        # Origin feat (always available at level 1)
        feat_parts.append('"origin_feat":"Origin Feat Name"')
        
        # General feats available at levels 4, 8, 12, 16, 19
        general_feat_levels = [4, 8, 12, 16, 19]
        available_general_feats = [l for l in general_feat_levels if l <= level]
        
        if available_general_feats:
            general_feats = ['{"name":"General Feat","level":' + str(l) + ',"grants_asi":true}' 
                           for l in available_general_feats]
            feat_parts.append('"general_feats":[' + ','.join(general_feats) + ']')
        else:
            feat_parts.append('"general_feats":[]')
        
        # Epic Boon at level 19
        if level >= 19:
            feat_parts.append('"epic_boon":"Epic Boon Name"')
        
        # Fighting style feats (conditional)
        feat_parts.append('"fighting_style_feats":[]')
        
        return ','.join(feat_parts) + ','
    
    def _determine_character_skills(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine character skills based on D&D 5e 2024 rules.
        Skills come from species, class, background, and feats.
        """
        skills = {}
        skill_sources = {}
        
        # Get character details
        species = character_data.get("species", "Human")
        classes = character_data.get("classes", {"Fighter": 1})
        background = character_data.get("background", "Folk Hero")
        level = character_data.get("level", 1)
        
        # Add species-based skills
        species_skills = self._get_species_skills(species)
        for skill in species_skills:
            skills[skill] = "proficient"
            skill_sources[skill] = "species"
        
        # Add class-based skills
        for class_name, class_level in classes.items():
            class_skills = self._get_class_skills(class_name, class_level)
            for skill in class_skills:
                if skill not in skills:
                    skills[skill] = "proficient"
                    skill_sources[skill] = "class"
                elif skills[skill] == "proficient":
                    # Already proficient, check for expertise
                    if self._class_grants_expertise(class_name, skill):
                        skills[skill] = "expert"
        
        # Add background-based skills
        background_skills = self._get_background_skills(background)
        for skill in background_skills:
            if skill not in skills:
                skills[skill] = "proficient"
                skill_sources[skill] = "background"
        
        # Add feat-based skills
        feat_skills = self._get_feat_skills(character_data)
        for skill, proficiency_level in feat_skills.items():
            if skill not in skills:
                skills[skill] = proficiency_level
                skill_sources[skill] = "feat"
            elif skills[skill] == "proficient" and proficiency_level == "expert":
                skills[skill] = "expert"
        
        # Store skill proficiencies in character data
        character_data["skill_proficiencies"] = skills
        character_data["skill_sources"] = skill_sources
        
        return character_data
    
    def _get_species_skills(self, species: str) -> List[str]:
        """Get skill proficiencies granted by species."""
        species_skills = {
            "Human": ["persuasion"],  # Variant Human often gets a skill
            "Elf": ["perception"],
            "Dwarf": ["history"],  # Knowledge of stonework and dwarven history
            "Halfling": ["stealth"],
            "Dragonborn": ["intimidation"],
            "Gnome": ["arcana"],  # Rock gnome tinkering knowledge
            "Half-Elf": ["persuasion", "deception"],  # Choose 2 from any
            "Half-Orc": ["intimidation"],
            "Tiefling": ["deception"],
            "Aasimar": ["insight"],
            "Goliath": ["athletics"],
            "Firbolg": ["nature"],
            "Kenku": ["deception", "stealth"],
            "Tabaxi": ["perception", "stealth"],
            "Tortle": ["survival"],
            "Lizardfolk": ["nature", "survival"],
            "Aarakocra": ["perception"],
            "Genasi": [],  # Varies by subtype
            "Githyanki": ["intimidation"],
            "Githzerai": ["insight"]
        }
        return species_skills.get(species, [])
    
    def _get_class_skills(self, class_name: str, level: int) -> List[str]:
        """Get skill proficiencies granted by class."""
        class_skills = {
            "Barbarian": ["animal_handling", "athletics", "intimidation", "nature", "perception", "survival"],
            "Bard": ["any_three"],  # Choose any 3 skills
            "Cleric": ["history", "insight", "medicine", "persuasion", "religion"],
            "Druid": ["arcana", "animal_handling", "insight", "medicine", "nature", "perception", "religion", "survival"],
            "Fighter": ["acrobatics", "animal_handling", "athletics", "history", "insight", "intimidation", "perception", "survival"],
            "Monk": ["acrobatics", "athletics", "history", "insight", "religion", "stealth"],
            "Paladin": ["athletics", "insight", "intimidation", "medicine", "persuasion", "religion"],
            "Ranger": ["animal_handling", "athletics", "insight", "investigation", "nature", "perception", "stealth", "survival"],
            "Rogue": ["acrobatics", "athletics", "deception", "insight", "intimidation", "investigation", "perception", "performance", "persuasion", "sleight_of_hand", "stealth"],
            "Sorcerer": ["arcana", "deception", "insight", "intimidation", "persuasion", "religion"],
            "Warlock": ["arcana", "deception", "history", "intimidation", "investigation", "nature", "religion"],
            "Wizard": ["arcana", "history", "insight", "investigation", "medicine", "religion"]
        }
        
        available_skills = class_skills.get(class_name, [])
        
        # For classes that choose from a list, simulate selection
        if class_name == "Bard":
            return ["persuasion", "performance", "deception"]  # Common bard skills
        elif class_name == "Fighter":
            return ["athletics", "intimidation"]  # Common fighter choices (2 skills)
        elif class_name == "Rogue":
            return ["stealth", "sleight_of_hand", "perception", "investigation"]  # 4 skills typical
        elif class_name == "Ranger":
            return ["survival", "nature", "perception"]  # 3 skills typical
        else:
            # Return first 2 skills for most classes
            return available_skills[:2] if len(available_skills) >= 2 else available_skills
    
    def _get_background_skills(self, background: str) -> List[str]:
        """Get skill proficiencies granted by background."""
        background_skills = {
            "Acolyte": ["insight", "religion"],
            "Criminal": ["deception", "stealth"],
            "Folk Hero": ["animal_handling", "survival"],
            "Noble": ["history", "persuasion"],
            "Sage": ["arcana", "history"],
            "Soldier": ["athletics", "intimidation"],
            "Charlatan": ["deception", "sleight_of_hand"],
            "Entertainer": ["acrobatics", "performance"],
            "Guild Artisan": ["insight", "persuasion"],
            "Hermit": ["medicine", "religion"],
            "Outlander": ["athletics", "survival"],
            "Sailor": ["athletics", "perception"],
            "Urchin": ["sleight_of_hand", "stealth"],
            "Artisan": ["history", "investigation"],
            "Courtier": ["insight", "persuasion"],
            "Investigator": ["insight", "investigation"],
            "Scholar": ["arcana", "history"],
            "Spy": ["deception", "stealth"]
        }
        return background_skills.get(background, ["insight", "persuasion"])  # Default
    
    def _get_feat_skills(self, character_data: Dict[str, Any]) -> Dict[str, str]:
        """Get skill proficiencies granted by feats."""
        feat_skills = {}
        
        # Check origin feat
        origin_feat = character_data.get("origin_feat", "")
        if origin_feat == "Skilled":
            # Skilled feat grants proficiency in 3 skills
            feat_skills.update({
                "athletics": "proficient",
                "perception": "proficient",
                "investigation": "proficient"
            })
        elif origin_feat == "Prodigy":
            # Prodigy grants 1 skill and 1 expertise
            feat_skills["insight"] = "expert"
        
        # Check general feats
        general_feats = character_data.get("general_feats", [])
        for feat in general_feats:
            feat_name = feat.get("name", "")
            if feat_name == "Skilled":
                feat_skills.update({
                    "survival": "proficient",
                    "medicine": "proficient",
                    "nature": "proficient"
                })
            elif feat_name == "Observant":
                if "investigation" not in feat_skills:
                    feat_skills["investigation"] = "proficient"
                if "perception" not in feat_skills:
                    feat_skills["perception"] = "proficient"
        
        return feat_skills
    
    def _class_grants_expertise(self, class_name: str, skill: str) -> bool:
        """Check if a class grants expertise in a specific skill."""
        expertise_classes = {
            "Rogue": ["stealth", "sleight_of_hand", "deception", "investigation", "perception", "insight"],
            "Bard": ["persuasion", "deception", "performance", "insight"]
        }
        
        if class_name in expertise_classes:
            return skill in expertise_classes[class_name]
        return False

# ============================================================================
# CHARACTER CREATOR - THE COMPLETE FEATURE SET
# ============================================================================

class CharacterCreator(BaseCreator):
    """
    Complete character creation orchestrator.
    This contains ALL features and serves as the foundation for NPCs and creatures.
    """

    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        super().__init__(llm_service, config)
        
        # Full feature set - advanced managers only available for complete characters
        self.ability_manager = None  # Created when needed with character_core
        
        logger.info("CharacterCreator initialized with complete feature set")
    
    async def create_character(self, prompt: str, user_preferences: Optional[Dict[str, Any]] = None, 
                             import_existing: Optional[Dict[str, Any]] = None) -> CreationResult:
        """
        Create a complete D&D 5e 2024 character with full features.
        This is the most comprehensive creation method.
        """
        start_time = time.time()
        
        # Initialize verbose logging if requested
        verbose_generation = user_preferences.get("verbose_generation", False) if user_preferences else False
        if verbose_generation:
            self.verbose_logs = []
            self.verbose_logs.append({
                'type': 'creation_start',
                'timestamp': time.time(),
                'prompt': prompt,
                'user_preferences': user_preferences,
                'import_existing': import_existing
            })
        
        try:
            logger.info(f"Starting complete character creation: {prompt[:100]}...")
            
            # Check if user prefers generator-based creation (default for dev_vision.md compliance)
            use_generators = user_preferences.get("use_generators", True) if user_preferences else True
            level = user_preferences.get("level", 1) if user_preferences else 1
            
            if use_generators:
                # Use integrated generators for dev_vision.md compliant character creation
                logger.info("Using integrated CharacterGenerator for comprehensive character creation")
                character_data = await self.generate_character_with_generators(prompt, level, user_preferences)
                
                result = CreationResult(success=True, data=character_data)
                result.creation_time = time.time() - start_time
                
                if verbose_generation and hasattr(self, 'verbose_logs'):
                    result.verbose_logs = self.verbose_logs
                
                logger.info(f"Character creation completed in {result.creation_time:.2f}s using generators")
                return result
            
            # Fallback to traditional creation method
            logger.info("Using traditional creation method")
            
            # Step 1: Generate base character data
            base_data = await self._generate_character_data(prompt, level)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'base_character_data',
                    'description': 'Generated base character data (name, class, stats, skills)',
                    'level': level,
                    'data_keys': list(base_data.keys()) if base_data else []
                })
            
            # Step 2: Build character core
            character_core = self._build_character_core(base_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'character_core',
                    'description': f'Built character core for {character_core.name}',
                    'character_name': character_core.name,
                    'species': character_core.species,
                    'classes': character_core.character_classes
                })
            
            # Step 3: Generate enhanced backstory
            backstory_data = await self._generate_enhanced_backstory(base_data, prompt)
            base_data.update(backstory_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhanced_backstory',
                    'description': 'Generated detailed backstory and character history',
                    'backstory_keys': list(backstory_data.keys()) if backstory_data else []
                })
            
            # Step 4: Generate custom content if needed
            custom_data = await self._generate_custom_content(base_data, prompt)
            base_data.update(custom_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'custom_content',
                    'description': 'Generated custom equipment and special abilities',
                    'custom_keys': list(custom_data.keys()) if custom_data else []
                })
            
            # Step 5: Enhance character spells
            enhanced_spell_data = self._enhance_character_spells(base_data)
            base_data.update(enhanced_spell_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhance_spells',
                    'description': 'Enhanced character spells with appropriate D&D 5e spells',
                    'spell_count': len(enhanced_spell_data.get("spells_known", []))
                })
            
            # Step 6: Enhance character weapons
            enhanced_weapon_data = self._enhance_character_weapons(base_data)
            base_data.update(enhanced_weapon_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhance_weapons',
                    'description': 'Enhanced character weapons with appropriate D&D 5e weapons',
                    'weapon_count': len(enhanced_weapon_data.get("weapons", []))
                })
            
            # Step 7: Enhance character feats
            enhanced_feat_data = self._enhance_character_feats(base_data)
            base_data.update(enhanced_feat_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhance_feats',
                    'description': 'Enhanced character feats with appropriate D&D 5e feats',
                    'feat_count': len(enhanced_feat_data.get("general_feats", [])) + (1 if enhanced_feat_data.get("origin_feat") else 0)
                })
            
            # Step 8: Enhance character armor
            enhanced_armor_data = self._enhance_character_armor(base_data)
            base_data.update(enhanced_armor_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhance_armor',
                    'description': 'Enhanced character armor with appropriate D&D 5e armor',
                    'armor': enhanced_armor_data.get("armor", "None")
                })
            
            # Step 9: Enhance character equipment and tools
            enhanced_equipment_data = self._enhance_character_equipment(base_data)
            base_data.update(enhanced_equipment_data)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_step',
                    'timestamp': time.time(),
                    'step': 'enhance_equipment',
                    'description': 'Enhanced character equipment with appropriate D&D 5e gear and tools',
                    'equipment_count': len(enhanced_equipment_data.get("equipment", {})),
                    'tools_count': len(enhanced_equipment_data.get("tools", []))
                })
            
            # Step 10: Create final character sheet
            final_character = self._create_final_character(base_data, character_core)
            
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_complete',
                    'timestamp': time.time(),
                    'total_time': time.time() - start_time,
                    'character_name': character_core.name,
                    'final_level': getattr(character_core, 'level', level)
                })
            
            result = CreationResult(success=True, data=final_character)
            result.creation_time = time.time() - start_time
            
            # Add verbose logs to result if generated
            if verbose_generation and hasattr(self, 'verbose_logs'):
                result.verbose_logs = self.verbose_logs
            
            logger.info(f"Character creation completed in {result.creation_time:.2f}s: {character_core.name}")
            return result
            
        except Exception as e:
            if verbose_generation and hasattr(self, 'verbose_logs'):
                self.verbose_logs.append({
                    'type': 'creation_error',
                    'timestamp': time.time(),
                    'error': str(e),
                    'total_time': time.time() - start_time
                })
            
            logger.error(f"Character creation failed: {e}")
            result = CreationResult(success=False, error=str(e))
            result.creation_time = time.time() - start_time
            
            # Add verbose logs to error result if generated
            if verbose_generation and hasattr(self, 'verbose_logs'):
                result.verbose_logs = self.verbose_logs
            
            return result
            
            logger.info(f"Complete character creation finished in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Character creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    async def _generate_character_data(self, description: str, level: int) -> Dict[str, Any]:
        """Generate core character data - foundation for all character types."""
        prompt = self._create_character_prompt(description, level)
        data = await self._generate_with_llm(prompt, "character")
        
        # Fix common data structure issues
        data = self._fix_character_data_structure(data)
        data["level"] = level
        
        return data
    
    def _create_character_prompt(self, description: str, level: int) -> str:
        """Create character generation prompt with D&D 5e 2024 feats and skills."""
        # Determine feat availability based on level
        feat_section = self._get_feat_section_for_level(level)
        
        # Create a sample character data to get appropriate spells
        sample_character = {"level": level, "classes": {"Wizard": level}}  # Default for spell selection
        suggested_spells = get_appropriate_spells_for_character(sample_character, 8)
        
        # Format spell suggestions for the prompt
        spell_examples = []
        for spell in suggested_spells[:6]:  # Show first 6 as examples
            spell_examples.append(f'"{spell["name"]}" (Level {spell["level"]}, {spell["school"].title()})')
        
        spell_suggestion_text = ", ".join(spell_examples) if spell_examples else "Magic Missile, Fire Bolt, Cure Wounds"
        
        return f"""Create D&D 5e 2024 character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":{{"skill_name":"proficient"}},"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],{feat_section}"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":{{"Item":1}},"spells_known":[{{"name":"Spell Name","level":1,"school":"evocation","description":"Spell description"}}],"backstory":"Brief backstory"}}

D&D 5e 2024 SKILL RULES:
- Skills from Species: Each species grants specific skill proficiencies
- Skills from Class: Classes grant choice of skills from their list (2-4 skills typically)
- Skills from Background: Each background grants 2 specific skills
- Skills from Feats: Some feats grant additional skill proficiencies or expertise
- Expertise: Some classes (Rogue, Bard) can double proficiency bonus for certain skills
- Tool Synergy: Tool proficiency + relevant skill can grant advantage

STANDARD SKILLS (2024):
Strength: Athletics
Dexterity: Acrobatics, Stealth, Sleight of Hand
Intelligence: Arcana, History, Investigation, Nature, Religion, Decorum
Wisdom: Animal Handling, Insight, Medicine, Perception, Survival  
Charisma: Deception, Intimidation, Performance, Persuasion

SPELL SELECTION PRIORITY (VERY IMPORTANT):
1. **MANDATORY FIRST PRIORITY**: Use ONLY existing D&D 5e spells when possible
2. **REQUIRED**: Choose from these D&D 5e spells: {spell_suggestion_text}
3. **FORBIDDEN**: Do NOT create new spells unless absolutely necessary for character concept
4. **REQUIRED**: Spellcasters must have level-appropriate spells (cantrips + leveled spells)
5. **REQUIRED**: Match spells to class theme (Wizard=all schools, Cleric=divine, Druid=nature, etc.)
6. **SPELL FORMAT**: Use exact spell names from D&D 5e: "Magic Missile", "Fireball", "Cure Wounds", etc.

COMMON D&D 5E SPELLS BY CLASS:
- Wizard: Magic Missile, Shield, Mage Armor, Detect Magic, Fireball, Lightning Bolt, Counterspell
- Cleric: Cure Wounds, Guiding Bolt, Bless, Spiritual Weapon, Hold Person, Dispel Magic
- Druid: Goodberry, Cure Wounds, Entangle, Barkskin, Moonbeam, Call Lightning, Conjure Animals
- Sorcerer: Fire Bolt, Shield, Magic Missile, Misty Step, Fireball, Haste, Counterspell
- Warlock: Eldritch Blast, Hex, Armor of Agathys, Hold Person, Hunger of Hadar, Counterspell
- Bard: Vicious Mockery, Healing Word, Dissonant Whispers, Heat Metal, Hypnotic Pattern, Counterspell
- Paladin: Divine Smite, Bless, Cure Wounds, Aid, Lesser Restoration, Protection from Energy
- Ranger: Hunter's Mark, Cure Wounds, Entangle, Pass without Trace, Spike Growth, Conjure Animals

**CRITICAL**: Only use existing D&D 5e spell names. Do not invent new spells.

WEAPON SELECTION PRIORITY (VERY IMPORTANT):
1. **MANDATORY FIRST PRIORITY**: Use ONLY existing D&D 5e weapons when possible
2. **REQUIRED**: Choose from standard D&D weapons: Longsword, Shortsword, Dagger, Rapier, Battleaxe, Greatsword, Longbow, Shortbow, etc.
3. **FORBIDDEN**: Do NOT create new weapons unless absolutely necessary for character concept
4. **REQUIRED**: Match weapons to class proficiencies (Simple/Martial) and character abilities
5. **WEAPON FORMAT**: Use exact weapon names from D&D 5e: "Longsword", "Rapier", "Longbow", etc.

D&D 5e 2024 WEAPON CATEGORIES AND PROPERTIES:
Simple Melee: Club, Dagger, Greatclub, Handaxe, Javelin, Light Hammer, Mace, Quarterstaff, Sickle, Spear
Simple Ranged: Dart, Light Crossbow, Shortbow, Sling
Martial Melee: Battleaxe, Flail, Glaive, Greataxe, Greatsword, Halberd, Lance, Longsword, Maul, Morningstar, Pike, Rapier, Scimitar, Shortsword, Trident, Warhammer, War Pick, Whip
Martial Ranged: Blowgun, Hand Crossbow, Heavy Crossbow, Longbow, Musket, Pistol

WEAPON PROPERTIES:
- Finesse: Use STR or DEX for attacks (Dagger, Dart, Rapier, Scimitar, Shortsword, Whip)
- Light: Can dual-wield (Club, Dagger, Handaxe, Light Hammer, Sickle, Hand Crossbow, Scimitar, Shortsword)
- Heavy: Disadvantage if STR/DEX < 13 (Glaive, Greataxe, Greatsword, Halberd, Lance, Maul, Pike, Heavy Crossbow, Longbow)
- Reach: +5 feet reach (Glaive, Halberd, Lance, Pike, Whip)
- Thrown: Can be thrown (Dagger, Handaxe, Javelin, Light Hammer, Spear, Dart, Trident)
- Two-Handed: Requires both hands (Greatclub, Glaive, Greataxe, Greatsword, Halberd, Lance, Maul, Pike, Light Crossbow, Longbow, Heavy Crossbow, Shortbow)
- Versatile: 1-hand or 2-hand damage (Quarterstaff, Spear, Battleaxe, Longsword, Trident, Warhammer, War Pick)

WEAPON MASTERY PROPERTIES (2024):
- Cleave: Hit adjacent enemy on successful hit (Greataxe, Halberd)
- Graze: Deal ability mod damage on miss (Glaive, Greatsword)
- Nick: Light weapon extra attack as part of Attack action (Dagger, Light Hammer, Sickle, Scimitar)
- Push: Push target 10 feet (Greatclub, Pike, Warhammer, Heavy Crossbow)
- Sap: Target has disadvantage on next attack (Mace, Spear, Flail, Longsword, Morningstar, War Pick)
- Slow: Reduce target speed by 10 feet (Club, Javelin, Light Crossbow, Sling, Whip, Longbow, Musket)
- Topple: Force Constitution save or prone (Quarterstaff, Battleaxe, Lance, Maul, Trident)
- Vex: Advantage on next attack against target (Handaxe, Dart, Rapier, Shortsword, Blowgun, Hand Crossbow, Shortbow, Pistol)

COMMON D&D 5E WEAPONS BY CLASS:
- Fighter/Paladin: Longsword, Greatsword, Battleaxe, Warhammer, Longbow, Heavy Crossbow
- Ranger: Shortsword, Scimitar, Longbow, Handaxe, Javelin
- Rogue: Rapier, Shortsword, Dagger, Hand Crossbow, Shortbow
- Cleric: Mace, Warhammer, Light Crossbow, Javelin
- Wizard/Sorcerer: Dagger, Quarterstaff, Light Crossbow, Dart
- Barbarian: Greataxe, Handaxe, Javelin, Longbow
- Bard: Rapier, Shortsword, Dagger, Shortbow
- Monk: Quarterstaff, Shortsword, Dagger, Dart, Sling
- Warlock: Dagger, Light Crossbow, Shortsword
- Druid: Quarterstaff, Sickle, Sling, Spear, Dart

**CRITICAL**: Only use existing D&D 5e armor names. Do not invent new armor.

EQUIPMENT & TOOLS SELECTION PRIORITY (VERY IMPORTANT):
1. **MANDATORY FIRST PRIORITY**: Use ONLY existing D&D 5e equipment and tools when possible
2. **REQUIRED**: Choose from standard D&D equipment packs and tools based on class and background
3. **REQUIRED**: Include appropriate spellcasting focus for spellcasters (Crystal, Holy Symbol, Druidic Focus)
4. **REQUIRED**: Include class-appropriate tools (Thieves' Tools for Rogues, Smith's Tools for Fighters, etc.)

D&D 5e 2024 EQUIPMENT PACKS BY CLASS:
- Barbarian/Druid/Fighter/Monk/Paladin/Ranger: Explorer's Pack
- Bard: Entertainer's Pack
- Cleric: Priest's Pack
- Rogue: Burglar's Pack
- Sorcerer: Dungeoneer's Pack
- Warlock/Wizard: Scholar's Pack

D&D 5e 2024 TOOLS BY CLASS/BACKGROUND:
Artisan's Tools: Alchemist's Supplies, Brewer's Supplies, Calligrapher's Supplies, Carpenter's Tools, Smith's Tools, etc.
Specialist Kits: Thieves' Tools, Disguise Kit, Forgery Kit, Herbalism Kit, Poisoner's Kit
Gaming Sets: Dice Set, Dragonchess Set, Playing Card Set
Musical Instruments: Lute, Flute, Drum, Bagpipes, etc.

**CRITICAL**: Only use existing D&D 5e equipment and tool names. Do not invent new items.

Match description exactly. Prioritize existing D&D 5e spells, weapons, feats, armor, and equipment over custom content. Include appropriate skills and items for level. Return complete JSON only."""

# ============================================================================
# CHARACTER CREATION METHODS - SPELL AND WEAPON ENHANCEMENT
# ============================================================================

    def _fix_character_data_structure(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fix data structure mismatches - shared logic for all character types."""
        # Fix species: should be string, not list
        if isinstance(character_data.get("species"), list):
            species_list = character_data["species"]
            character_data["species"] = species_list[0] if species_list else "Human"
        
        # Fix classes: should be dict
        if isinstance(character_data.get("classes"), list):
            classes_list = character_data["classes"]
            if classes_list:
                character_data["classes"] = {classes_list[0]: character_data.get("level", 1)}
            else:
                character_data["classes"] = {"Fighter": character_data.get("level", 1)}
        
        # Fix equipment: should be dict
        if isinstance(character_data.get("equipment"), list):
            equipment_list = character_data["equipment"]
            equipment_dict = {}
            for item in equipment_list:
                if isinstance(item, dict) and "name" in item:
                    equipment_dict[item["name"]] = item.get("quantity", 1)
                elif isinstance(item, str):
                    equipment_dict[item] = 1
            character_data["equipment"] = equipment_dict
        
        # Ensure equipment is a dict
        if not isinstance(character_data.get("equipment"), dict):
            character_data["equipment"] = {"Adventurer's Pack": 1}
        
        # Fix alignment: ensure it's a list of two strings
        if isinstance(character_data.get("alignment"), str):
            alignment_parts = character_data["alignment"].split()
            if len(alignment_parts) >= 2:
                character_data["alignment"] = [alignment_parts[0], alignment_parts[1]]
            else:
                character_data["alignment"] = ["Neutral", "Good"]
        elif not isinstance(character_data.get("alignment"), list):
            character_data["alignment"] = ["Neutral", "Good"]
        
        # Fix feats: ensure proper structure for D&D 5e 2024
        if "origin_feat" in character_data and not character_data["origin_feat"]:
            character_data["origin_feat"] = "Alert"  # Default origin feat
        
        if "general_feats" not in character_data:
            character_data["general_feats"] = []
        elif not isinstance(character_data["general_feats"], list):
            character_data["general_feats"] = []
            
        # Ensure general feats have proper structure
        level = character_data.get("level", 1)
        expected_general_feats = len([l for l in [4, 8, 12, 16, 19] if l <= level])
        current_general_feats = len(character_data.get("general_feats", []))
        
        # Add missing general feats if character level qualifies
        if current_general_feats < expected_general_feats:
            for i in range(current_general_feats, expected_general_feats):
                feat_level = [4, 8, 12, 16, 19][i]
                character_data["general_feats"].append({
                    "name": "Ability Score Improvement", 
                    "level": feat_level,
                    "grants_asi": True
                })
        
        if "fighting_style_feats" not in character_data:
            character_data["fighting_style_feats"] = []
            
        if "epic_boon" not in character_data and level >= 19:
            character_data["epic_boon"] = "Epic Boon of Combat Prowess"
        
        # Fix skills: ensure proper D&D 5e 2024 skill structure
        if "skill_proficiencies" not in character_data:
            character_data["skill_proficiencies"] = {}
        elif isinstance(character_data["skill_proficiencies"], list):
            # Convert old list format to dict format
            skill_list = character_data["skill_proficiencies"]
            character_data["skill_proficiencies"] = {}
            for skill in skill_list:
                if isinstance(skill, str):
                    character_data["skill_proficiencies"][skill] = "proficient"
        
        # Determine skills based on species, class, background, and feats
        character_data = self._determine_character_skills(character_data)
        
        return character_data
    
    def _build_character_core(self, character_data: Dict[str, Any]) -> CharacterCore:
        """Build CharacterCore from character data."""
        character_core = CharacterCore(character_data["name"])
        character_core.species = character_data.get("species", "Human")
        character_core.background = character_data.get("background", "Folk Hero")
        character_core.character_classes = character_data.get("classes", {"Fighter": 1})
        character_core.alignment = character_data.get("alignment", ["Neutral", "Good"])
        
        # Set ability scores
        ability_scores = character_data.get("ability_scores", {})
        for ability_name, score in ability_scores.items():
            if hasattr(character_core, ability_name):
                setattr(character_core, ability_name, AbilityScore(score))
        
        # Set feats (D&D 5e 2024)
        character_core.origin_feat = character_data.get("origin_feat", "")
        character_core.general_feats = character_data.get("general_feats", [])
        character_core.fighting_style_feats = character_data.get("fighting_style_feats", [])
        character_core.epic_boon = character_data.get("epic_boon", "")
        character_core.feat_abilities = character_data.get("feat_abilities", {})
        
        # Set skill proficiencies with proper proficiency levels
        skill_proficiencies = character_data.get("skill_proficiencies", {})
        for skill_name, proficiency_level in skill_proficiencies.items():
            if proficiency_level == "expert":
                character_core.skill_proficiencies[skill_name] = ProficiencyLevel.EXPERT
            elif proficiency_level == "proficient":
                character_core.skill_proficiencies[skill_name] = ProficiencyLevel.PROFICIENT
            else:
                character_core.skill_proficiencies[skill_name] = ProficiencyLevel.NONE
        
        # Apply feat effects to character
        character_core.apply_feat_effects()
        
        return character_core
    
    async def _generate_enhanced_backstory(self, character_data: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Generate enhanced backstory."""
        try:
            backstory_prompt = f"""Generate a detailed D&D character backstory. Return ONLY JSON:

CHARACTER CONCEPT: {original_prompt}
LEVEL: {character_data.get("level", 1)}

{{"backstory": "A detailed backstory of 2-3 paragraphs..."}}

Match the character concept exactly. Return complete JSON only."""
            
            backstory_data = await self._generate_with_llm(backstory_prompt, "backstory")
            return backstory_data
            
        except Exception as e:
            logger.warning(f"Backstory generation failed: {e}")
            return {"backstory": f"A {character_data.get('species', 'human')} {list(character_data.get('classes', {}).keys())[0] if character_data.get('classes') else 'adventurer'} seeking adventure."}
    
    async def _generate_custom_content(self, character_data: Dict[str, Any], original_prompt: str) -> Dict[str, Any]:
        """Generate custom content if needed."""
        try:
            custom_content = {}
            
            # Generate custom content if character is high level or unique
            level = character_data.get("level", 1)
            if level >= 5 or any(keyword in original_prompt.lower() for keyword in ["unique", "custom", "special"]):
                custom_result = await self.custom_content_generator.generate_custom_content_for_character(
                    character_data, original_prompt
                )
                if custom_result:
                    custom_content.update(custom_result)
            
            return custom_content
            
        except Exception as e:
            logger.warning(f"Custom content generation failed: {e}")
            return {}
    
    def _enhance_character_spells(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e spells based on their class and level.
        STRONGLY prioritizes existing D&D 5e spells over custom spell creation.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Check if character is a spellcaster
            if not self._is_spellcaster(character_data):
                character_data["spells_known"] = []
                return character_data
            
            # Get appropriate spells for this character (prioritizes existing D&D spells)
            suggested_spells = get_appropriate_spells_for_character(character_data, 15)
            
            # If character already has spells, validate and enhance them
            existing_spells = character_data.get("spells_known", [])
            
            # Validate and enhance existing spells
            enhanced_spells = []
            existing_spell_names = set()
            
            for spell in existing_spells:
                if isinstance(spell, dict) and "name" in spell:
                    spell_name = spell["name"]
                    
                    # PRIORITY 1: Check if it's an official D&D 5e spell
                    if is_existing_dnd_spell(spell_name):
                        enhanced_spells.append(spell)
                        existing_spell_names.add(spell_name)
                        logger.info(f"Validated existing D&D 5e spell: {spell_name}")
                    else:
                        # PRIORITY 2: Try to find a similar D&D spell
                        similar_spells = find_similar_spells(spell_name, 1)
                        if similar_spells:
                            # Replace with official spell
                            spell_data = {
                                "name": similar_spells[0],
                                "level": spell.get("level", 1),
                                "school": spell.get("school", "evocation"),
                                "description": spell.get("description", f"Official D&D 5e spell {similar_spells[0]}"),
                                "source": "D&D 5e Official"
                            }
                            enhanced_spells.append(spell_data)
                            existing_spell_names.add(similar_spells[0])
                            logger.info(f"Replaced '{spell_name}' with official D&D spell: {similar_spells[0]}")
                        else:
                            # PRIORITY 3: Keep custom spell if no D&D equivalent
                            spell["source"] = "Custom"
                            enhanced_spells.append(spell)
                            existing_spell_names.add(spell_name)
                            logger.info(f"Kept custom spell: {spell_name}")
            
            # PRIORITY 4: Fill remaining slots with official D&D spells
            for suggested_spell in suggested_spells:
                if suggested_spell["name"] not in existing_spell_names:
                    enhanced_spells.append(suggested_spell)
                    logger.info(f"Added suggested D&D 5e spell: {suggested_spell['name']}")
                    if len(enhanced_spells) >= 12:  # Reasonable spell limit
                        break
            
            character_data["spells_known"] = enhanced_spells
            
            # Add spell slot information
            character_data["spell_slots"] = self._calculate_spell_slots(character_data)
            
            # Log spell source breakdown
            dnd_spells = len([s for s in enhanced_spells if s.get('source') in ['D&D 5e Core', 'D&D 5e Official']])
            custom_spells = len([s for s in enhanced_spells if s.get('source') == 'Custom'])
            
            logger.info(f"Enhanced character with {len(enhanced_spells)} spells ({dnd_spells} D&D 5e spells, {custom_spells} custom spells)")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Spell enhancement failed: {e}")
            return character_data
    
    def _enhance_character_weapons(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e weapons based on their class and level.
        STRONGLY prioritizes existing D&D 5e weapons over custom weapon creation.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Get appropriate weapons for this character (prioritizes existing D&D weapons)
            suggested_weapons = get_appropriate_weapons_for_character(character_data, 5)
            
            # If character already has weapons, validate and enhance them
            existing_weapons = character_data.get("weapons", [])
            
            # Validate and enhance existing weapons
            enhanced_weapons = []
            existing_weapon_names = set()
            
            for weapon in existing_weapons:
                if isinstance(weapon, dict) and "name" in weapon:
                    weapon_name = weapon["name"]
                    
                    # PRIORITY 1: Check if it's an official D&D 5e weapon
                    if is_existing_dnd_weapon(weapon_name):
                        # Get official weapon data and merge
                        official_data = get_weapon_data(weapon_name)
                        if official_data:
                            # Merge with existing data, prioritizing official stats
                            enhanced_weapon = {**weapon, **official_data}
                            enhanced_weapon["source"] = "D&D 5e Official"
                            enhanced_weapons.append(enhanced_weapon)
                            existing_weapon_names.add(weapon_name)
                            logger.info(f"Enhanced official D&D weapon: {weapon_name}")
                        else:
                            enhanced_weapons.append(weapon)
                            existing_weapon_names.add(weapon_name)
                    else:
                        # PRIORITY 2: Try to find a similar D&D weapon
                        similar_weapons = find_similar_weapons(weapon_name, 1)
                        if similar_weapons:
                            # Replace with official weapon
                            official_data = get_weapon_data(similar_weapons[0])
                            if official_data:
                                enhanced_weapons.append(official_data)
                                existing_weapon_names.add(similar_weapons[0])
                                logger.info(f"Replaced '{weapon_name}' with official D&D weapon: {similar_weapons[0]}")
                            else:
                                weapon["source"] = "Custom"
                                enhanced_weapons.append(weapon)
                                existing_weapon_names.add(weapon_name)
                        else:
                            # PRIORITY 3: Keep custom weapon if no D&D equivalent
                            weapon["source"] = "Custom"
                            enhanced_weapons.append(weapon)
                            existing_weapon_names.add(weapon_name)
                            logger.info(f"Kept custom weapon: {weapon_name}")
            
            # PRIORITY 4: Fill with appropriate official D&D weapons if needed
            if len(enhanced_weapons) < 2:  # Ensure character has at least 2 weapons
                for suggested_weapon in suggested_weapons:
                    if suggested_weapon["name"] not in existing_weapon_names:
                        enhanced_weapons.append(suggested_weapon)
                        logger.info(f"Added suggested D&D 5e weapon: {suggested_weapon['name']}")
                        if len(enhanced_weapons) >= 3:  # Reasonable weapon limit
                            break
            
            character_data["weapons"] = enhanced_weapons
            
            # Log weapon source breakdown
            dnd_weapons = len([w for w in enhanced_weapons if w.get('source') in ['D&D 5e Core', 'D&D 5e Official']])
            custom_weapons = len([w for w in enhanced_weapons if w.get('source') == 'Custom'])
            
            logger.info(f"Enhanced character with {len(enhanced_weapons)} weapons ({dnd_weapons} D&D 5e weapons, {custom_weapons} custom weapons)")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Weapon enhancement failed: {e}")
            return character_data
    
    def _enhance_character_feats(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e feats based on their class, level, and background.
        STRONGLY prioritizes existing D&D 5e feats over custom feat creation.
        """
        try:
            level = character_data.get("level", 1)
            classes = character_data.get("classes", {})
            primary_class = list(classes.keys())[0] if classes else "Fighter"
            
            # Get appropriate feats for this character (prioritizes existing D&D feats)
            suggested_feats = get_appropriate_feats_for_character(character_data, 10)
            
            # Validate and enhance existing feats
            enhanced_feats = {
                "origin_feat": "",
                "general_feats": [],
                "fighting_style_feats": [],
                "epic_boon": ""
            }
            
            # Process existing feats if any
            existing_origin_feat = character_data.get("origin_feat", "")
            existing_general_feats = character_data.get("general_feats", [])
            existing_fighting_style_feats = character_data.get("fighting_style_feats", [])
            existing_epic_boon = character_data.get("epic_boon", "")
            
            # PRIORITY 1: Validate existing origin feat
            if existing_origin_feat:
                if is_existing_dnd_feat(existing_origin_feat):
                    feat_data = get_feat_data(existing_origin_feat)
                    if feat_data and feat_data.get("category") == "Origin":
                        enhanced_feats["origin_feat"] = existing_origin_feat
                        logger.info(f"Validated existing D&D 5e origin feat: {existing_origin_feat}")
                    else:
                        logger.warning(f"Invalid origin feat: {existing_origin_feat}, will replace")
                else:
                    logger.info(f"Custom origin feat detected: {existing_origin_feat}")
                    enhanced_feats["origin_feat"] = existing_origin_feat
            
            # PRIORITY 2: Assign origin feat if missing
            if not enhanced_feats["origin_feat"]:
                origin_suggestions = [f for f in suggested_feats if f["category"] == "Origin"]
                if origin_suggestions:
                    enhanced_feats["origin_feat"] = origin_suggestions[0]["name"]
                    logger.info(f"Added suggested D&D 5e origin feat: {enhanced_feats['origin_feat']}")
                else:
                    enhanced_feats["origin_feat"] = "Alert"  # Default fallback
                    logger.info(f"Added default origin feat: Alert")
            
            # PRIORITY 3: Validate and enhance general feats
            asi_levels = [l for l in [4, 8, 12, 16, 19] if l <= level]
            general_suggestions = [f for f in suggested_feats if f["category"] == "General"]
            
            for existing_feat in existing_general_feats:
                if isinstance(existing_feat, dict) and "name" in existing_feat:
                    feat_name = existing_feat["name"]
                    if is_existing_dnd_feat(feat_name):
                        feat_data = get_feat_data(feat_name)
                        if feat_data and feat_data.get("category") == "General":
                            enhanced_feats["general_feats"].append(existing_feat)
                            logger.info(f"Validated existing D&D 5e general feat: {feat_name}")
                        else:
                            logger.warning(f"Invalid general feat: {feat_name}")
                    else:
                        logger.info(f"Custom general feat detected: {feat_name}")
                        enhanced_feats["general_feats"].append(existing_feat)
                elif isinstance(existing_feat, str):
                    if is_existing_dnd_feat(existing_feat):
                        feat_data = get_feat_data(existing_feat)
                        if feat_data and feat_data.get("category") == "General":
                            enhanced_feats["general_feats"].append({
                                "name": existing_feat,
                                "level": 4,  # Default to first ASI level
                                "grants_asi": feat_data.get("asi_bonus", False)
                            })
                            logger.info(f"Validated existing D&D 5e general feat: {existing_feat}")
            
            # Fill missing general feats
            while len(enhanced_feats["general_feats"]) < len(asi_levels) and general_suggestions:
                for suggestion in general_suggestions:
                    if suggestion["name"] not in [f.get("name", f) if isinstance(f, dict) else f for f in enhanced_feats["general_feats"]]:
                        enhanced_feats["general_feats"].append({
                            "name": suggestion["name"],
                            "level": asi_levels[len(enhanced_feats["general_feats"])],
                            "grants_asi": suggestion.get("asi_bonus", False)
                        })
                        logger.info(f"Added suggested D&D 5e general feat: {suggestion['name']}")
                        break
                else:
                    break
            
            # PRIORITY 4: Validate fighting style feats
            if primary_class in ["Fighter", "Paladin", "Ranger"]:
                fighting_suggestions = [f for f in suggested_feats if f["category"] == "Fighting Style"]
                
                if existing_fighting_style_feats:
                    for existing_feat in existing_fighting_style_feats:
                        feat_name = existing_feat if isinstance(existing_feat, str) else existing_feat.get("name", "")
                        if is_existing_dnd_feat(feat_name):
                            feat_data = get_feat_data(feat_name)
                            if feat_data and feat_data.get("category") == "Fighting Style":
                                enhanced_feats["fighting_style_feats"].append(feat_name)
                                logger.info(f"Validated existing D&D 5e fighting style feat: {feat_name}")
                
                # Add fighting style if missing
                if not enhanced_feats["fighting_style_feats"] and fighting_suggestions:
                    enhanced_feats["fighting_style_feats"].append(fighting_suggestions[0]["name"])
                    logger.info(f"Added suggested D&D 5e fighting style feat: {fighting_suggestions[0]['name']}")
            
            # PRIORITY 5: Validate epic boon
            if level >= 20:
                if existing_epic_boon:
                    if is_existing_dnd_feat(existing_epic_boon):
                        feat_data = get_feat_data(existing_epic_boon)
                        if feat_data and feat_data.get("category") == "Epic Boon":
                            enhanced_feats["epic_boon"] = existing_epic_boon
                            logger.info(f"Validated existing D&D 5e epic boon: {existing_epic_boon}")
                        else:
                            logger.warning(f"Invalid epic boon: {existing_epic_boon}")
                    else:
                        logger.info(f"Custom epic boon detected: {existing_epic_boon}")
                        enhanced_feats["epic_boon"] = existing_epic_boon
                
                # Add epic boon if missing
                if not enhanced_feats["epic_boon"]:
                    epic_suggestions = [f for f in suggested_feats if f["category"] == "Epic Boon"]
                    if epic_suggestions:
                        enhanced_feats["epic_boon"] = epic_suggestions[0]["name"]
                        logger.info(f"Added suggested D&D 5e epic boon: {enhanced_feats['epic_boon']}")
            
            # Update character data with enhanced feats
            character_data.update(enhanced_feats)
            
            # Log feat source breakdown
            dnd_feats = sum([
                1 if is_existing_dnd_feat(enhanced_feats["origin_feat"]) else 0,
                len([f for f in enhanced_feats["general_feats"] if is_existing_dnd_feat(f.get("name", f) if isinstance(f, dict) else f)]),
                len([f for f in enhanced_feats["fighting_style_feats"] if is_existing_dnd_feat(f)]),
                1 if enhanced_feats["epic_boon"] and is_existing_dnd_feat(enhanced_feats["epic_boon"]) else 0
            ])
            
            total_feats = sum([
                1 if enhanced_feats["origin_feat"] else 0,
                len(enhanced_feats["general_feats"]),
                len(enhanced_feats["fighting_style_feats"]),
                1 if enhanced_feats["epic_boon"] else 0
            ])
            
            custom_feats = total_feats - dnd_feats
            
            logger.info(f"Enhanced character with {total_feats} feats ({dnd_feats} D&D 5e feats, {custom_feats} custom feats)")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Feat enhancement failed: {e}")
            return character_data
    
    def _enhance_character_armor(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e armor based on their class and level.
        STRONGLY prioritizes existing D&D 5e armor over custom armor creation.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            primary_class = list(classes.keys())[0] if classes else "Fighter"
            
            # Validate existing armor or assign default based on class
            existing_armor = character_data.get("armor", "")
            
            # Handle case where armor might be a list (from custom content)
            if isinstance(existing_armor, list):
                existing_armor = existing_armor[0] if existing_armor else ""
                character_data["armor"] = existing_armor
            
            if existing_armor:
                # Keep existing armor
                logger.info(f"Character has existing armor: {existing_armor}")
            else:
                # Assign default armor based on class proficiency
                if primary_class in ["Fighter", "Paladin"]:
                    character_data["armor"] = "Chain Mail"
                elif primary_class in ["Cleric", "Ranger", "Barbarian", "Druid"]:
                    character_data["armor"] = "Leather Armor"
                elif primary_class in ["Rogue", "Bard", "Monk"]:
                    character_data["armor"] = "Leather Armor"
                else:
                    character_data["armor"] = "Padded Armor"
                
                logger.info(f"Added default armor for {primary_class}: {character_data['armor']}")
            
            # Log armor assignment
            logger.info(f"Character equipped with armor: {character_data['armor']}")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Armor enhancement failed: {e}")
            return character_data
    
    def _enhance_character_equipment(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e equipment based on their class, background, and level.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            primary_class = list(classes.keys())[0] if classes else "Fighter"
            background = character_data.get("background", "Folk Hero")
            
            # If character already has equipment, validate and enhance it
            existing_equipment = character_data.get("equipment", {})
            if not isinstance(existing_equipment, dict):
                existing_equipment = {}
            
            # Start with existing equipment
            enhanced_equipment = existing_equipment.copy()
            existing_item_names = set(existing_equipment.keys())
            
            # Add essential class-based equipment if missing
            class_equipment = {
                "Fighter": ["Shield", "Rope (50 feet)", "Rations (1 day)"],
                "Wizard": ["Spellbook", "Component Pouch", "Ink and Quill"],
                "Cleric": ["Holy Symbol", "Prayer Book", "Incense"],
                "Rogue": ["Thieves' Tools", "Crowbar", "Dark Cloak"],
                "Ranger": ["Quiver", "Hunting Trap", "Traveler's Clothes"],
                "Barbarian": ["Bedroll", "Waterskin", "Belt Pouch"],
                "Bard": ["Musical Instrument", "Costume", "Sealing Wax"],
                "Druid": ["Leather Armor", "Druidic Focus", "Herbal Pouch"],
                "Paladin": ["Holy Symbol", "Chain Mail", "Emblem"],
                "Sorcerer": ["Component Pouch", "Simple Weapon", "Light Crossbow"],
                "Warlock": ["Component Pouch", "Leather Armor", "Simple Weapon"],
                "Monk": ["Monk's Robes", "Prayer Beads", "Rice Paper"]
            }
            
            essential_items = class_equipment.get(primary_class, ["Backpack", "Bedroll", "Rations (1 day)"])
            for item in essential_items:
                if item not in existing_item_names:
                    enhanced_equipment[item] = 1
                    existing_item_names.add(item)
                    logger.info(f"Added essential {primary_class} equipment: {item}")
            
            # Add background-based equipment if missing
            background_equipment = {
                "Folk Hero": ["Smith's Tools", "Artisan's Tools"],
                "Criminal": ["Thieves' Tools", "Crowbar"],
                "Acolyte": ["Holy Symbol", "Prayer Book", "Incense"],
                "Noble": ["Signet Ring", "Fine Clothes", "Purse"],
                "Sage": ["Ink and Quill", "Parchment", "Small Knife"],
                "Soldier": ["Playing Cards", "Common Clothes", "Belt Pouch"],
                "Entertainer": ["Musical Instrument", "Costume", "Makeup"],
                "Guild Artisan": ["Artisan's Tools", "Letter of Introduction"],
                "Hermit": ["Herbalism Kit", "Scroll Case", "Winter Blanket"],
                "Outlander": ["Staff", "Hunting Trap", "Traveler's Clothes"]
            }
            
            bg_items = background_equipment.get(background, ["Common Clothes", "Belt Pouch"])
            for item in bg_items:
                if item not in existing_item_names:
                    enhanced_equipment[item] = 1
                    existing_item_names.add(item)
                    logger.info(f"Added {background} background equipment: {item}")
            
            # Ensure basic adventuring gear
            basic_gear = ["Backpack", "Bedroll", "Rations (1 day)", "Waterskin", "Rope (50 feet)", "Torch", "Flint and Steel"]
            for item in basic_gear:
                if item not in existing_item_names:
                    enhanced_equipment[item] = 2 if item == "Torch" else 1
                    existing_item_names.add(item)
                    if len(enhanced_equipment) >= 25:  # Final equipment limit
                        break
            
            character_data["equipment"] = enhanced_equipment
            
            logger.info(f"Enhanced character with {len(enhanced_equipment)} equipment items")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Equipment enhancement failed: {e}")
            return character_data
    
    def _calculate_spell_slots(self, character_data: Dict[str, Any]) -> Dict[int, int]:
        """Calculate spell slots for a character based on their classes and level."""
        classes = character_data.get("classes", {})
        total_level = character_data.get("level", 1)
        
        # Simplified spell slot calculation
        # In a full implementation, this would handle multiclassing properly
        spell_slots = {}
        
        for class_name, class_level in classes.items():
            if class_name in ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard"]:
                # Full casters
                for slot_level in range(1, min(10, (class_level + 1) // 2 + 1)):
                    if slot_level <= 9:
                        if slot_level == 1:
                            spell_slots[slot_level] = spell_slots.get(slot_level, 0) + min(4, class_level + 1)
                        elif slot_level == 2:
                            spell_slots[slot_level] = spell_slots.get(slot_level, 0) + max(0, min(3, class_level - 2))
                        else:
                            spell_slots[slot_level] = spell_slots.get(slot_level, 0) + max(0, min(3, class_level - slot_level * 2))
            
            elif class_name in ["Paladin", "Ranger"]:
                # Half casters
                if class_level >= 2:
                    for slot_level in range(1, min(6, (class_level - 1) // 2 + 1)):
                        if slot_level <= 5:
                            spell_slots[slot_level] = spell_slots.get(slot_level, 0) + max(0, min(4, class_level - slot_level))
        
        return spell_slots
    
    def _create_final_character(self, character_data: Dict[str, Any], character_core: CharacterCore) -> Dict[str, Any]:
        """Create the final character representation."""
        try:
            # Create character sheet
            name = character_data.get("name", "Generated Character")
            species = character_data.get("species", "Human")
            
            character_classes = character_data.get("classes", {"Fighter": 1})
            if character_classes:
                primary_class = list(character_classes.keys())[0]
                level = list(character_classes.values())[0]
            else:
                primary_class = "Fighter"
                level = character_data.get("level", 1)
            
            # Create character representation without CharacterSheet for now
            character_representation = {
                "core": character_core,
                "name": name,
                "species": species,
                "primary_class": primary_class,
                "level": level,
                "raw_data": character_data
            }
            
            # Combine all character information
            final_character = {
                "core": character_core,
                "character": character_representation,
                "raw_data": character_data,
                "creation_metadata": {
                    "created_at": time.time(),
                    "version": "2024",
                    "generator": "CharacterCreator"
                }
            }
            
            return final_character
            
        except Exception as e:
            logger.error(f"Failed to create final character: {e}")
            return character_data
    
    # ============================================================================
    # ITERATIVE REFINEMENT METHODS (dev_vision.md CRITICAL REQUIREMENT)
    # ============================================================================
    
    async def refine_character(self, character_data: Dict[str, Any], refinement_prompt: str, 
                             user_preferences: Optional[Dict[str, Any]] = None) -> CreationResult:
        """
        Iteratively refine an existing character based on user feedback.
        
        This is a CRITICAL dev_vision.md requirement for user-driven character improvement.
        """
        logger.info(f"Starting character refinement: {refinement_prompt}")
        
        try:
            # Create refinement prompt that preserves character identity
            character_concept = self._extract_character_concept(character_data)
            
            refinement_full_prompt = f"""
            ORIGINAL CHARACTER: {character_concept}
            
            CHARACTER DATA: {json.dumps(character_data, indent=2)}
            
            REFINEMENT REQUEST: {refinement_prompt}
            
            Create an improved version of this character that:
            1. Applies the requested refinement changes
            2. Preserves the character's core identity and backstory
            3. Maintains D&D 5e 2024 compatibility
            4. Keeps the same name and background unless specifically requested to change
            
            Respond with complete character data in the same format as the original.
            """
            
            # Generate refined character
            refined_data = await self._generate_character_data(refinement_full_prompt, character_data.get("level", 1))
            
            # Enhance the refined character
            refined_data = self._enhance_character_spells(refined_data)
           

            refined_data = self._enhance_character_weapons(refined_data)
            refined_data = self._enhance_character_feats(refined_data)
            refined_data = self._enhance_character_equipment(refined_data)
            
            # Build character core
            character_core = self._build_character_core(refined_data)
            
            # Generate enhanced backstory incorporating refinement
            if self.llm_service:
                backstory_prompt = f"""
                ORIGINAL CHARACTER: {character_concept}
                REFINEMENT APPLIED: {refinement_prompt}
                
                Create an enhanced backstory that:
                1. Incorporates the character refinement changes
                2. Explains how the character developed these new aspects
                3. Maintains narrative consistency
                4. Keeps the core character identity
                """
                refined_data = await self._generate_enhanced_backstory(refined_data, backstory_prompt)
            
            return CreationResult(
                success=True,
                data={
                    "character_core": character_core,
                    "raw_data": refined_data,
                    "refinement_applied": refinement_prompt,
                    "creation_type": "character_refinement"
                }
            )
            
        except Exception as e:
            logger.error(f"Character refinement failed: {str(e)}")
            return CreationResult(success=False, error=f"Character refinement failed: {str(e)}")
    
    async def level_up_character_with_journal(self, character_data: Dict[str, Any], 
                                            journal_entries: List[str],
                                            new_level: int,
                                            multiclass_option: Optional[str] = None) -> CreationResult:
        """
        Level up a character using journal entries for context.
        
        This is a HIGH dev_vision.md requirement for journal-informed character advancement.
        """
        logger.info(f"Starting journal-based level up to level {new_level}")
        
        try:
            current_level = character_data.get("level", 1)
            character_concept = self._extract_character_concept(character_data)
            
            # Create journal-informed level-up prompt
            journal_context = "\n".join([f"- {entry}" for entry in journal_entries])
            
            levelup_prompt = f"""
            EXISTING CHARACTER: {character_concept}
            CURRENT LEVEL: {current_level}
            TARGET LEVEL: {new_level}
            
            JOURNAL ENTRIES (PLAY EXPERIENCE):
            {journal_context}
            
            CHARACTER DATA: {json.dumps(character_data, indent=2)}
            
            Level up this character from level {current_level} to {new_level} based on their actual play experiences.
            
            Requirements:
            1. Preserve character identity, name, and core backstory
            2. Add appropriate class features for the new level
            3. Reflect the journal experiences in advancement choices
            4. Add spells, feats, ability score improvements as appropriate
            5. {"Consider adding " + multiclass_option + " levels if appropriate" if multiclass_option else "Focus on existing classes"}
            6. Maintain D&D 5e 2024 compatibility
            
            Respond with complete updated character data.
            """
            
            # Generate leveled character
            leveled_data = await self._generate_character_data(levelup_prompt, new_level)
            
            # Ensure level is correct
            leveled_data["level"] = new_level
            
            # Handle multiclass if specified
            if multiclass_option and multiclass_option not in leveled_data.get("classes", {}):
                current_classes = leveled_data.get("classes", {})
                # Add one level of the new class
                current_classes[multiclass_option] = 1
                leveled_data["classes"] = current_classes
            
            # Enhance the leveled character
            leveled_data = self._enhance_character_spells(leveled_data)
            leveled_data = self._enhance_character_weapons(leveled_data)
            leveled_data = self._enhance_character_feats(leveled_data)
            leveled_data = self._enhance_character_equipment(leveled_data)
            
            # Build character core
            character_core = self._build_character_core(leveled_data)
            
            # Generate enhanced backstory incorporating play experiences
            if self.llm_service:
                backstory_prompt = f"""
                CHARACTER: {character_concept}
                LEVEL UP: {current_level} → {new_level}
                PLAY EXPERIENCES: {journal_context}
                
                Create an enhanced backstory that:
                1. Incorporates the character's actual play experiences
                2. Explains their growth and new abilities
                3. Reflects lessons learned in their adventures
                4. Maintains character consistency and personality
                """
                leveled_data = await self._generate_enhanced_backstory(leveled_data, backstory_prompt)
            
            return CreationResult(
                success=True,
                data={
                    "character_core": character_core,
                    "raw_data": leveled_data,
                    "journal_entries": journal_entries,
                    "level_progression": f"{current_level} → {new_level}",
                    "creation_type": "character_levelup"
                }
            )
            
        except Exception as e:
            logger.error(f"Journal-based level up failed: {str(e)}")
            return CreationResult(success=False, error=f"Journal-based level up failed: {str(e)}")
    
    async def enhance_existing_character(self, character_data: Dict[str, Any], 
                                       enhancement_prompt: str) -> CreationResult:
        """
        Enhance an existing character with story-driven improvements.
        
        This supports dev_vision.md requirements for character evolution based on story events.
        """
        logger.info(f"Starting character enhancement: {enhancement_prompt}")
        
        try:
            character_concept = self._extract_character_concept(character_data)
            
            enhancement_full_prompt = f"""
            EXISTING CHARACTER: {character_concept}
            
            CHARACTER DATA: {json.dumps(character_data, indent=2)}
            
            ENHANCEMENT REQUEST: {enhancement_prompt}
            
            Enhance this character based on the story event or development described.
            
            Requirements:
            1. Preserve character identity, name, and core backstory
            2. Add new abilities, knowledge, or traits as appropriate
            3. Integrate the enhancement into the character's narrative
            4. Maintain D&D 5e 2024 balance and compatibility
            5. Explain how the enhancement manifests mechanically
            
            Respond with complete enhanced character data.
            """
            
            # Generate enhanced character
            enhanced_data = await self._generate_character_data(enhancement_full_prompt, character_data.get("level", 1))
            
            # Enhance the character
            enhanced_data = self._enhance_character_spells(enhanced_data)
            enhanced_data = self._enhance_character_weapons(enhanced_data)
            enhanced_data = self._enhance_character_feats(enhanced_data)
            enhanced_data = self._enhance_character_equipment(enhanced_data)
            
            # Build character core
            character_core = self._build_character_core(enhanced_data)
            
            # Generate enhanced backstory
            if self.llm_service:
                backstory_prompt = f"""
                CHARACTER: {character_concept}
                ENHANCEMENT: {enhancement_prompt}
                
                Create an enhanced backstory that:
                1. Incorporates the character enhancement event
                2. Explains how they gained new abilities or knowledge
                3. Shows character growth and development
                4. Maintains personality and core traits
                """
                enhanced_data = await self._generate_enhanced_backstory(enhanced_data, backstory_prompt)
            
            return CreationResult(
                success=True,
                data={
                    "character_core": character_core,
                    "raw_data": enhanced_data,
                    "enhancement_applied": enhancement_prompt,
                    "creation_type": "character_enhancement"
                }
            )
            
        except Exception as e:
            logger.error(f"Character enhancement failed: {str(e)}")
            return CreationResult(success=False, error=f"Character enhancement failed: {str(e)}")
    
    async def apply_user_feedback(self, character_data: Dict[str, Any], 
                                feedback: Dict[str, Any]) -> CreationResult:
        """
        Apply structured user feedback to improve a character.
        
        This supports dev_vision.md iterative development requirements.
        """
        logger.info("Applying user feedback to character")
        
        try:
            feedback_items = []
            
            # Process different types of feedback
            if "ability_scores" in feedback:
                feedback_items.append(f"Adjust ability scores: {feedback['ability_scores']}")
            
            if "classes" in feedback:
                feedback_items.append(f"Class changes: {feedback['classes']}")
            
            if "equipment" in feedback:
                feedback_items.append(f"Equipment changes: {feedback['equipment']}")
            
            if "personality" in feedback:
                feedback_items.append(f"Personality adjustments: {feedback['personality']}")
            
            if "backstory" in feedback:
                feedback_items.append(f"Backstory changes: {feedback['backstory']}")
            
            if "general" in feedback:
                feedback_items.append(f"General feedback: {feedback['general']}")
            
            # Combine all feedback into a refinement prompt
            combined_feedback = "; ".join(feedback_items)
            
            # Use the refinement system
            return await self.refine_character(character_data, combined_feedback, {"apply_feedback": True})
            
        except Exception as e:
            logger.error(f"User feedback application failed: {str(e)}")
            return CreationResult(success=False, error=f"User feedback application failed: {str(e)}")
    
    # ============================================================================
    # GENERATOR INTEGRATION METHODS
    # ============================================================================
    
    async def generate_character_with_generators(self, prompt: str, level: int = 1, 
                                               user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Use the integrated CharacterGenerator for comprehensive D&D 5e 2024 character creation.
        This method leverages the full generator pipeline for dev_vision.md compliance.
        """
        logger.info(f"Creating character with integrated generators: level {level}")
        
        # Parse character concept from prompt
        character_concept = self._parse_character_concept(prompt, level)
        
        # Use CharacterGenerator for complete character creation
        character_data = await self.character_generator.generate_character(character_concept, prompt)
        
        # Apply additional validation and enhancement from creation system
        character_data = self._enhance_character_spells(character_data)
        character_data = self._enhance_character_weapons(character_data)
        character_data = self._enhance_character_feats(character_data)
        character_data = self._enhance_character_armor(character_data)
        character_data = self._enhance_character_equipment(character_data)
        
        logger.info(f"Character '{character_data.get('name', 'Unknown')}' created successfully with generators")
        return character_data
    
    async def generate_npc_with_generators(self, npc_role: str, user_description: str = "") -> Dict[str, Any]:
        """Use the integrated NPCGenerator for NPC creation."""
        logger.info(f"Creating NPC with integrated generators: {npc_role}")
        
        npc_data = await self.npc_generator.generate_npc(npc_role, user_description)
        
        # Apply NPC-specific validation and enhancement
        npc_data = validate_and_enhance_npc(npc_data)
        
        logger.info(f"NPC '{npc_role}' created successfully with generators")
        return npc_data
    
    async def generate_creature_with_generators(self, creature_type: str, user_description: str = "") -> Dict[str, Any]:
        """Use the integrated CreatureGenerator for creature creation."""
        logger.info(f"Creating creature with integrated generators: {creature_type}")
        
        creature_data = await self.creature_generator.generate_creature(creature_type, user_description)
        
        # Apply creature-specific validation and enhancement
        creature_data = validate_and_enhance_creature(creature_data)
        
        logger.info(f"Creature '{creature_type}' created successfully with generators")
        return creature_data
    
    async def generate_item_with_generators(self, item_type: str, name: str = "", 
                                          description: str = "", extra_fields: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Use the integrated ItemGenerator for item creation."""
        logger.info(f"Creating item with integrated generators: {item_type}")
        
        item_data = await self.item_generator.generate_item(item_type, name, description, extra_fields)
        
        # Apply item-specific validation
        level = extra_fields.get("level", 1) if extra_fields else 1
        item_data = validate_item_for_level(item_data, level)
        
        logger.info(f"Item '{name or item_type}' created successfully with generators")
        return item_data
    
    def _parse_character_concept(self, prompt: str, level: int) -> Dict[str, Any]:
        """Parse character concept from user prompt for generator input."""
        # Extract basic information from prompt
        prompt_lower = prompt.lower()
        
        # Default character concept
        concept = {
            "name": "Unknown Adventurer",
            "level": level,
            "classes": {},
            "species": "Human",
            "background": "Folk Hero",
            "alignment": ["Neutral", "Good"],
            "equipment": []
        }
        
        # Extract class hints
        class_keywords = {
            "fighter": "Fighter", "warrior": "Fighter", "knight": "Fighter",
            "wizard": "Wizard", "mage": "Wizard", "sorcerer": "Sorcerer",
            "cleric": "Cleric", "priest": "Cleric", "paladin": "Paladin",
            "rogue": "Rogue", "thief": "Rogue", "assassin": "Rogue",
            "ranger": "Ranger", "hunter": "Ranger", "druid": "Druid",
            "bard": "Bard", "musician": "Bard", "barbarian": "Barbarian",
            "monk": "Monk", "warlock": "Warlock"
        }
        
        for keyword, class_name in class_keywords.items():
            if keyword in prompt_lower:
                concept["classes"] = {class_name: level}
                break
        
        # If no class found, default to Fighter
        if not concept["classes"]:
            concept["classes"] = {"Fighter": level}
        
        # Extract species hints
        species_keywords = {
            "elf": "Elf", "elven": "Elf", "dwarf": "Dwarf", "dwarven": "Dwarf",
            "halfling": "Halfling", "tiefling": "Tiefling", "dragonborn": "Dragonborn",
            "human": "Human", "gnome": "Gnome", "half-orc": "Half-Orc", "orc": "Half-Orc"
        }
        
        for keyword, species_name in species_keywords.items():
            if keyword in prompt_lower:
                concept["species"] = species_name
                break
        
        # Extract name if quoted or obvious
        import re
        name_match = re.search(r'named? ["\']?([A-Za-z]+)["\']?', prompt)
        if name_match:
            concept["name"] = name_match.group(1).title()
        elif re.search(r'^[A-Z][a-z]+ ', prompt):
            # If prompt starts with a capitalized word, assume it's a name
            first_word = prompt.split()[0]
            if first_word.isalpha() and first_word[0].isupper():
                concept["name"] = first_word
        
        return concept

