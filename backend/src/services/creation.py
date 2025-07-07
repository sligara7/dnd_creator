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
from src.services.creation_validation import (
    validate_basic_structure, validate_custom_content,
    validate_and_enhance_npc, validate_item_for_level,
    validate_and_enhance_creature
)

# Import from centralized enums
from src.core.enums import (
    NPCType, NPCRole, NPCSpecies, NPCClass, CreatureType, CreatureSize, CreatureAlignment,
    ItemType, ItemRarity, WeaponCategory, ArmorCategory, FeatCategory, FeatType, FeatPrerequisite,
    Skill, SkillAbilityMapping, SkillSource
)

# Import core D&D components
from src.models.core_models import AbilityScore, ProficiencyLevel, ASIManager, MagicItemManager
from src.models.character_models import CharacterCore  # DnDCondition, CharacterSheet, CharacterState, CharacterStats - may not exist yet
from src.services.llm_service import create_llm_service, LLMService
from src.models.database_models import CustomContent
from src.services.ability_management import AdvancedAbilityManager
from src.services.generators import (
    BackstoryGenerator, CustomContentGenerator, NPCGenerator
)
from src.models.custom_content_models import ContentRegistry, CustomClass

# Import D&D 5e official data
from src.services.dnd_data import (
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
from src.services.creation_validation import validate_feat_prerequisites

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
        # TODO: Implement CharacterGenerator, CreatureGenerator, ItemGenerator
        # self.character_generator = CharacterGenerator(self.llm_service, self.content_registry)
        self.npc_generator = NPCGenerator(self.llm_service, self.content_registry)
        # self.creature_generator = CreatureGenerator(self.llm_service, self.content_registry)
        # self.item_generator = ItemGenerator(self.llm_service)
        
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
        
        # Check standard D&D spellcasting classes
        if any(cls.lower() in spellcasting_classes for cls in class_names):
            return True
        
        # Check for custom spellcasting classes
        for class_name in class_names:
            class_lower = class_name.lower()
            # Classes ending in "mancer" are typically spellcasters
            if class_lower.endswith("mancer"):
                return True
            # Other magic-related class keywords
            magic_keywords = ["magic", "spell", "arcane", "divine", "elemental", "mystic", 
                            "enchanter", "conjurer", "evoker", "necromancer", "illusionist",
                            "transmuter", "abjurer", "diviner", "witch", "warlock", "sorcerer"]
            if any(keyword in class_lower for keyword in magic_keywords):
                return True
        
        # Check if character already has spells defined (indicating spellcaster intent)
        if character_data.get("spells_known") or character_data.get("spells") or character_data.get("custom_void_spells"):
            return True
            
        return False
    
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
                # Call the main character creation logic instead of the missing method
                character_data = await self._create_character_comprehensive(prompt, level, user_preferences)
                
                result = CreationResult(success=True, data=character_data)
                result.creation_time = time.time() - start_time
                
                if verbose_generation and hasattr(self, 'verbose_logs'):
                    result.verbose_logs = self.verbose_logs
                
                logger.info(f"Character creation completed in {result.creation_time:.2f}s using generators")
                return result
            
            # Fallback to traditional creation method
            logger.info("Using traditional creation method")
            
            # Step 1: Generate base character data
            theme = user_preferences.get("theme") if user_preferences else "traditional D&D"
            base_data = await self._generate_character_data(prompt, level, theme)
            
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
            custom_data = await self._generate_custom_content(base_data, prompt, theme)
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
            enhanced_spell_data = await self._enhance_character_spells(base_data, theme)
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
            enhanced_weapon_data = self._enhance_character_weapons(base_data, theme)
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
            
            # Final data type normalization to ensure consistency
            final_character = self._normalize_character_data_types(final_character)
            
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
    
    async def _generate_character_data(self, description: str, level: int, theme: Optional[str] = None) -> Dict[str, Any]:
        """Generate core character data - foundation for all character types."""
        prompt = self._create_character_prompt(description, level, theme)
        data = await self._generate_with_llm(prompt, "character")
        
        # Debug: Check the type and content of data
        logger.debug(f"Generated character data type: {type(data)}")
        if not isinstance(data, dict):
            logger.error(f"Expected dict from LLM but got {type(data)}: {data}")
            raise TypeError(f"Expected dict from LLM but got {type(data)}")
        
        # Fix common data structure issues
        data = self._fix_character_data_structure(data)
        
        # Normalize data types to prevent inconsistencies
        data = self._normalize_character_data_types(data)
        
        data["level"] = level
        
        return data
    
    def _create_character_prompt(self, description: str, level: int, theme: Optional[str] = None) -> str:
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
        
        # Add theme context if provided
        theme_context = ""
        theme_equipment_guidance = ""
        theme_spell_guidance = ""
        
        if theme:
            theme_context = f"\nCAMPAIGN THEME: {theme}\n"
            
            # Provide dynamic theme guidance based on the theme
            if theme.lower() == "traditional d&d":
                theme_equipment_guidance = """
THEME-AWARE EQUIPMENT SUGGESTIONS (OPTIONAL):
- Traditional D&D: Standard medieval fantasy equipment, swords, shields, plate armor
- Classic weapons: Longswords, battleaxes, longbows, crossbows
- Traditional gear: Adventuring packs, rope, torches, holy symbols, spell components"""
                theme_spell_guidance = """
THEME-AWARE SPELL SUGGESTIONS (OPTIONAL):
- Traditional D&D: Classic fantasy spells from all schools of magic
- Combat spells: Fireball, Magic Missile, Cure Wounds, Shield
- Utility spells: Detect Magic, Light, Mending, Identify"""
            else:
                # Dynamic theme guidance for any other theme
                theme_equipment_guidance = f"""
THEME-AWARE EQUIPMENT SUGGESTIONS (OPTIONAL):
- {theme.title()} Theme: Consider equipment that fits the {theme} aesthetic and setting
- Adapt standard D&D equipment to match the campaign's tone, technology level, and style
- Think about what materials, weapons, and gear would be common in a {theme} setting"""
                theme_spell_guidance = f"""
THEME-AWARE SPELL SUGGESTIONS (OPTIONAL):
- {theme.title()} Theme: Choose spells that complement the {theme} setting and atmosphere
- Consider what types of magic would fit the theme's tone and available power sources
- Adapt spell flavoring to match the {theme} aesthetic while keeping D&D mechanics"""
        
        return f"""Create D&D 5e 2024 character. Return ONLY JSON:{theme_context}

DESCRIPTION: {description}
LEVEL: {level}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":{{"skill_name":"proficient"}},"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],{feat_section}"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":{{"Item":1}},"spells_known":[{{"name":"Spell Name","level":1,"school":"evocation","description":"Spell description"}}],"backstory":"Brief backstory"}}

**IMPORTANT**: Theme is SUGGESTIVE, not mandatory. Player character concept takes priority over theme.
If the character description conflicts with the theme, follow the character description.
{theme_equipment_guidance}
{theme_spell_guidance}

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
    
    def _normalize_character_data_types(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize character data to ensure consistent data types.
        This prevents issues like arrays becoming booleans or other type mismatches.
        """
        # Ensure spells_known is always an array
        if "spells_known" not in character_data:
            character_data["spells_known"] = []
        elif not isinstance(character_data["spells_known"], list):
            logger.warning(f"spells_known was {type(character_data['spells_known'])}, converting to empty array")
            character_data["spells_known"] = []
        
        # Ensure custom spell arrays are always arrays
        custom_spell_fields = ["custom_void_spells", "custom_spells", "spells"]
        for field in custom_spell_fields:
            if field in character_data:
                if not isinstance(character_data[field], list):
                    logger.warning(f"{field} was {type(character_data[field])}, converting to empty array")
                    character_data[field] = []
        
        # Ensure equipment is always a dict
        if "equipment" not in character_data:
            character_data["equipment"] = {}
        elif not isinstance(character_data["equipment"], dict):
            logger.warning(f"equipment was {type(character_data['equipment'])}, converting to empty dict")
            character_data["equipment"] = {}
        
        # Ensure weapons is always an array
        if "weapons" not in character_data:
            character_data["weapons"] = []
        elif not isinstance(character_data["weapons"], list):
            logger.warning(f"weapons was {type(character_data['weapons'])}, converting to empty array")
            character_data["weapons"] = []
        
        # Ensure feats arrays are always arrays
        feat_fields = ["general_feats", "fighting_style_feats", "feats"]
        for field in feat_fields:
            if field in character_data:
                if not isinstance(character_data[field], list):
                    logger.warning(f"{field} was {type(character_data[field])}, converting to empty array")
                    character_data[field] = []
        
        # Ensure species and classes are correct types
        if "species" in character_data:
            if isinstance(character_data["species"], list):
                # Convert list to string (take first element)
                character_data["species"] = character_data["species"][0] if character_data["species"] else "Human"
            elif not isinstance(character_data["species"], str):
                character_data["species"] = str(character_data["species"]) if character_data["species"] else "Human"
        
        if "classes" in character_data:
            if isinstance(character_data["classes"], list):
                # Convert list to dict
                if character_data["classes"]:
                    character_data["classes"] = {character_data["classes"][0]: character_data.get("level", 1)}
                else:
                    character_data["classes"] = {"Fighter": character_data.get("level", 1)}
            elif not isinstance(character_data["classes"], dict):
                character_data["classes"] = {"Fighter": character_data.get("level", 1)}
        
        return character_data

    def _build_character_core(self, character_data: Dict[str, Any]) -> CharacterCore:
        """Build CharacterCore from character data."""
        # Debug: Check the type and content of character_data
        logger.debug(f"Building character core with data type: {type(character_data)}")
        if not isinstance(character_data, dict):
            logger.error(f"Expected dict but got {type(character_data)}: {character_data}")
            raise TypeError(f"Expected dict but got {type(character_data)}")
        
        name = character_data.get("name", "Unknown")
        character_core = CharacterCore(name)
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
        
        # Note: Feat effects are applied through the data structure itself
        # No separate apply_feat_effects method needed
        
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
    
    async def _generate_custom_content(self, character_data: Dict[str, Any], original_prompt: str, theme: Optional[str] = None) -> Dict[str, Any]:
        """Generate custom content if needed."""
        try:
            custom_content = {}
            
            # Generate custom content if character is high level or unique
            level = character_data.get("level", 1)
            if level >= 5 or any(keyword in original_prompt.lower() for keyword in ["unique", "custom", "special"]):
                # Convert single theme to list for generator compatibility
                themes = [theme] if theme else None
                custom_result = await self.custom_content_generator.generate_custom_content_for_character(
                    character_data, original_prompt, themes
                )
                if custom_result:
                    custom_content.update(custom_result)
            
            return custom_content
            
        except Exception as e:
            logger.warning(f"Custom content generation failed: {e}")
            return {}
    
    async def _enhance_character_spells(self, character_data: Dict[str, Any], theme: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e spells based on their class and level.
        STRONGLY prioritizes existing D&D 5e spells over custom spell creation.
        Considers campaign theme for spell selection guidance.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Check if character is a spellcaster
            if not self._is_spellcaster(character_data):
                character_data["spells_known"] = []
                return character_data
            
            # Calculate proper number of spells based on D&D 5e rules
            spell_count = self._calculate_spells_known_for_level(character_data)
            
            # Get appropriate spells for this character (prioritizes existing D&D spells)
            suggested_spells = get_appropriate_spells_for_character(character_data, spell_count)
            
            # Apply theme-aware spell filtering if theme is provided
            if theme:
                suggested_spells = await self._filter_spells_by_theme(suggested_spells, theme, character_data)
            
            # If character already has spells, validate and enhance them
            existing_spells = character_data.get("spells_known", [])
            
            # For spellcasters with no initial spells, populate based on D&D 5e rules
            if not existing_spells and spell_count > 0:
                existing_spells = suggested_spells[:spell_count]
                logger.info(f"Auto-populated {len(existing_spells)} spells for level {level} spellcaster (expected: {spell_count})")
            
            # Validate and enhance existing spells
            
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
                    if len(enhanced_spells) >= spell_count:  # Use calculated spell count
                        break
            
            character_data["spells_known"] = enhanced_spells
            
            # Normalize data types after spell enhancement
            character_data = self._normalize_character_data_types(character_data)
            
            # Add spell slot information
            character_data["spell_slots"] = self._calculate_spell_slots(character_data)
            
            # Log spell source breakdown
            dnd_spells = len([s for s in enhanced_spells if s.get('source') in ['D&D 5e Core', 'D&D 5e Official']])
            custom_spells = len([s for s in enhanced_spells if s.get('source') == 'Custom'])
            
            logger.info(f"Enhanced character with {len(enhanced_spells)} spells ({dnd_spells} D&D 5e spells, {custom_spells} custom spells)")
            
            # PRIORITY 5: For custom classes, populate custom spell fields
            await self._populate_custom_spell_fields(character_data)
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Spell enhancement failed: {e}")
            return character_data
    
    def _calculate_spells_known_for_level(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate the proper number of spells a character should know based on D&D 5e rules.
        """
        classes = character_data.get("classes", {})
        level = character_data.get("level", 1)
        
        max_spells = 0
        
        for class_name, class_level in classes.items():
            class_lower = class_name.lower()
            
            # Wizard spell progression (spellbook)
            if "wizard" in class_lower or any(keyword in class_lower for keyword in ["mage", "arcane", "scholar"]):
                # Wizards: 6 starting spells + 2 per level
                wizard_spells = 6 + (class_level - 1) * 2
                max_spells = max(max_spells, wizard_spells)
                logger.info(f"Wizard-type class '{class_name}' level {class_level}: {wizard_spells} spells")
            
            # Sorcerer spell progression (spells known)
            elif "sorcerer" in class_lower or any(keyword in class_lower for keyword in ["chaos", "wild", "draconic"]):
                # Sorcerer spells known by level (D&D 5e table)
                sorcerer_spells_by_level = {
                    1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 
                    10: 11, 11: 12, 12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 
                    17: 15, 18: 15, 19: 15, 20: 15
                }
                sorcerer_spells = sorcerer_spells_by_level.get(min(class_level, 20), 15)
                max_spells = max(max_spells, sorcerer_spells)
                logger.info(f"Sorcerer-type class '{class_name}' level {class_level}: {sorcerer_spells} spells")
            
            # Warlock spell progression (limited spells known)
            elif "warlock" in class_lower or any(keyword in class_lower for keyword in ["patron", "pact", "fiend", "fey"]):
                # Warlock spells known by level
                warlock_spells_by_level = {
                    1: 1, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 4, 8: 4, 9: 5, 
                    10: 5, 11: 5, 12: 5, 13: 6, 14: 6, 15: 6, 16: 6, 
                    17: 7, 18: 7, 19: 7, 20: 7
                }
                warlock_spells = warlock_spells_by_level.get(min(class_level, 20), 7)
                max_spells = max(max_spells, warlock_spells)
                logger.info(f"Warlock-type class '{class_name}' level {class_level}: {warlock_spells} spells")
            
            # Bard spell progression (spells known)
            elif "bard" in class_lower or any(keyword in class_lower for keyword in ["song", "music", "lore"]):
                # Bard spells known by level
                bard_spells_by_level = {
                    1: 2, 2: 3, 3: 4, 4: 5, 5: 6, 6: 7, 7: 8, 8: 9, 9: 10, 
                    10: 10, 11: 11, 12: 11, 13: 12, 14: 12, 15: 13, 16: 13, 
                    17: 14, 18: 14, 19: 15, 20: 15
                }
                bard_spells = bard_spells_by_level.get(min(class_level, 20), 15)
                max_spells = max(max_spells, bard_spells)
                logger.info(f"Bard-type class '{class_name}' level {class_level}: {bard_spells} spells")
            
            # Ranger/Paladin spell progression (limited spells known)
            elif any(keyword in class_lower for keyword in ["ranger", "paladin", "hunter", "knight"]):
                # Half-casters get fewer spells
                if class_level >= 2:  # They start getting spells at level 2
                    half_caster_level = max(1, (class_level - 1) // 2)
                    half_caster_spells = min(half_caster_level + 1, 11)  # Max ~11 spells
                    max_spells = max(max_spells, half_caster_spells)
                    logger.info(f"Half-caster class '{class_name}' level {class_level}: {half_caster_spells} spells")
            
            # Custom spellcaster classes (use wizard-like progression for powerful customs)
            elif any(keyword in class_lower for keyword in ["mancer", "witch", "mystic", "elementalist", "void", "nether", "shadow"]):
                # Custom magical classes get wizard-like progression
                custom_spells = 6 + (class_level - 1) * 2
                max_spells = max(max_spells, custom_spells)
                logger.info(f"Custom spellcaster class '{class_name}' level {class_level}: {custom_spells} spells (wizard-like progression)")
            
            # Druid/Cleric (prepared spells, but we'll give them a good number to "know"
            elif any(keyword in class_lower for keyword in ["druid", "cleric", "priest", "nature"]):
                # These classes prepare spells, but for our purposes give them many to "know"
                prepared_equivalent = class_level + 10  # Generous spell knowledge
                max_spells = max(max_spells, prepared_equivalent)
                logger.info(f"Divine/Nature caster class '{class_name}' level {class_level}: {prepared_equivalent} spells")
        
        # Ensure minimum spells for any spellcaster
        if max_spells == 0 and self._is_spellcaster(character_data):
            max_spells = max(2, level // 2)  # Minimum progression for unknown spellcasters
            logger.info(f"Default spellcaster progression: {max_spells} spells for level {level}")
        
        return max_spells
    
    async def _populate_custom_spell_fields(self, character_data: Dict[str, Any]) -> None:
        """
        Populate custom spell fields for custom classes with LLM-generated thematic spells.
        Uses LLM to determine spell themes dynamically based on class names.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Check for custom classes that might need thematic spells
            for class_name, class_level in classes.items():
                class_lower = class_name.lower()
                
                # Use LLM to determine if this class should have custom spells and what theme
                theme_info = await self._determine_class_spell_theme(class_name, character_data)
                
                if theme_info and theme_info.get("needs_custom_spells"):
                    custom_field = theme_info.get("spell_field", "custom_spells")
                    spell_theme = theme_info.get("theme", class_name)
                    
                    # Ensure the custom field exists
                    if custom_field not in character_data:
                        character_data[custom_field] = []
                    
                    # Calculate number of custom spells based on level
                    spell_count = min(max(1, class_level // 2), 5)  # 1-5 spells based on level
                    
                    # Create thematic custom spells if the field is empty
                    if not character_data[custom_field]:
                        custom_spells = await self._create_thematic_spells(spell_theme, spell_count, class_level)
                        character_data[custom_field] = custom_spells
                        logger.info(f"Created {len(custom_spells)} custom {spell_theme} spells for {class_name}")
                    
        except Exception as e:
            logger.warning(f"Custom spell field population failed: {e}")

    async def _determine_class_spell_theme(self, class_name: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LLM to determine if a class needs custom spells and what theme they should have.
        """
        try:
            prompt = f"""Analyze this D&D class name and determine if it needs custom thematic spells. Return ONLY JSON:

CLASS NAME: {class_name}
CHARACTER LEVEL: {character_data.get("level", 1)}

Determine if this class name suggests it should have custom thematic spells beyond standard D&D spells.

{{"needs_custom_spells": true/false, "theme": "theme_name", "spell_field": "custom_field_name", "reasoning": "brief explanation"}}

ANALYSIS CRITERIA:
- Standard D&D classes (Fighter, Wizard, Rogue, etc.) should return needs_custom_spells: false
- Custom or uniquely themed classes should return needs_custom_spells: true
- Theme should capture the essence of the class (e.g., "shadow magic", "elemental fire", "void manipulation")
- Spell field should be descriptive (e.g., "custom_shadow_spells", "custom_fire_spells", "custom_void_spells")

EXAMPLES:
- "Fighter" -> {{"needs_custom_spells": false}}
- "Shadow Mancer" -> {{"needs_custom_spells": true, "theme": "shadow magic", "spell_field": "custom_shadow_spells"}}
- "Void Walker" -> {{"needs_custom_spells": true, "theme": "void manipulation", "spell_field": "custom_void_spells"}}
- "Phoenix Sorcerer" -> {{"needs_custom_spells": true, "theme": "phoenix fire magic", "spell_field": "custom_phoenix_spells"}}

Return complete JSON only."""

            response_data = await self._generate_with_llm(prompt, "class_spell_theme")
            
            if isinstance(response_data, dict) and "needs_custom_spells" in response_data:
                logger.info(f"Class theme analysis for '{class_name}': {response_data.get('reasoning', 'No reasoning provided')}")
                return response_data
            else:
                logger.warning(f"Invalid class theme analysis response: {response_data}")
                return {"needs_custom_spells": False}
                
        except Exception as e:
            logger.warning(f"Failed to analyze class spell theme for '{class_name}': {e}")
            return {"needs_custom_spells": False}
    
    async def _create_thematic_spells(self, theme: str, count: int, max_level: int) -> List[Dict[str, Any]]:
        """
        Create thematic custom spells for a specific theme using LLM generation.
        This allows for unlimited theme flexibility instead of hardcoded templates.
        """
        try:
            # Calculate appropriate spell levels based on max_level
            max_spell_level = min(max_level // 2 + 1, 5)
            
            prompt = f"""Create {count} thematic custom D&D 5e spells for a '{theme}' theme. Return ONLY JSON:

THEME: {theme}
SPELL COUNT: {count}
MAX SPELL LEVEL: {max_spell_level}
CHARACTER LEVEL: {max_level}

Create spells that capture the essence of the '{theme}' theme. Each spell should feel unique and thematic.

{{"spells": [
  {{"name": "Spell Name", "level": 1, "school": "evocation", "description": "Detailed spell description", "casting_time": "1 action", "range": "60 feet", "components": "V, S", "duration": "Instantaneous"}},
  {{"name": "Spell Name 2", "level": 2, "school": "transmutation", "description": "Detailed spell description", "casting_time": "1 action", "range": "Self", "components": "V, S, M", "duration": "Concentration, up to 1 minute"}}
]}}

SPELL DESIGN GUIDELINES:
- Spell levels should range from 1 to {max_spell_level}
- Each spell should clearly relate to the '{theme}' theme
- Use appropriate D&D 5e schools of magic: abjuration, conjuration, divination, enchantment, evocation, illusion, necromancy, transmutation
- Include balanced mechanics appropriate for the spell level
- Vary casting times, ranges, components, and durations for diversity
- Make descriptions evocative and thematic

THEME CONSIDERATIONS:
- Consider what magical effects would make sense for '{theme}'
- Think about the aesthetic, materials, energy types, and concepts associated with '{theme}'
- Ensure spells feel cohesive with the theme while being mechanically sound

Return complete JSON with exactly {count} spells."""

            response_data = await self._generate_with_llm(prompt, f"thematic_spells_{theme}")
            
            if isinstance(response_data, dict) and "spells" in response_data:
                spells = response_data["spells"]
                
                # Validate and enhance the generated spells
                validated_spells = []
                for spell in spells[:count]:  # Ensure we don't exceed requested count
                    if isinstance(spell, dict) and "name" in spell:
                        # Add default values for missing fields
                        spell.setdefault("source", "Custom")
                        spell.setdefault("casting_time", "1 action")
                        spell.setdefault("range", "60 feet")
                        spell.setdefault("components", "V, S")
                        spell.setdefault("duration", "Instantaneous")
                        spell.setdefault("level", 1)
                        spell.setdefault("school", "evocation")
                        spell.setdefault("description", f"A {theme}-themed spell.")
                        
                        # Ensure spell level is within bounds
                        spell["level"] = min(spell.get("level", 1), max_spell_level)
                        
                        validated_spells.append(spell)
                
                logger.info(f"Generated {len(validated_spells)} thematic spells for '{theme}' theme")
                return validated_spells
            else:
                logger.warning(f"Invalid response structure for thematic spells: {response_data}")
                return []
                
        except Exception as e:
            logger.warning(f"Failed to generate thematic spells for '{theme}': {e}")
            return []

    async def _filter_spells_by_theme(self, spells: List[Dict[str, Any]], theme: str, character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and prioritize spells based on campaign theme using LLM-generated theme logic.
        Theme is suggestive - enhances spell selection but doesn't override character concept.
        """
        if not theme or not spells:
            return spells
        
        try:
            # Generate theme-appropriate filtering logic using LLM
            theme_logic = await self._generate_theme_spell_logic(theme, character_data)
            
            if not theme_logic:
                logger.info(f"Could not generate theme logic for '{theme}', using all spells")
                return spells
            
            themed_spells = []
            other_spells = []
            
            # Apply LLM-generated theme logic to filter spells
            for spell in spells:
                is_themed = self._evaluate_spell_for_theme(spell, theme_logic)
                
                if is_themed:
                    themed_spells.append(spell)
                else:
                    other_spells.append(spell)
            
            # Combine with themed spells first (prioritized) followed by others
            filtered_spells = themed_spells + other_spells
            
            if themed_spells:
                logger.info(f"Theme '{theme}' filtering: {len(themed_spells)} themed spells prioritized, {len(other_spells)} standard spells available")
            else:
                logger.info(f"Theme '{theme}' filtering: No specific themed spells found, using all {len(spells)} spells")
            
            return filtered_spells
            
        except Exception as e:
            logger.warning(f"Theme-based spell filtering failed: {e}")
            return spells
    
    def _enhance_character_weapons(self, character_data: Dict[str, Any], theme: Optional[str] = None) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e weapons based on their class and level.
        STRONGLY prioritizes existing D&D 5e weapons over custom weapon creation.
        Considers campaign theme for weapon selection guidance.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Get appropriate weapons for this character (prioritizes existing D&D weapons)
            suggested_weapons = get_appropriate_weapons_for_character(character_data)
            
            # Apply theme-aware weapon filtering if theme is provided
            if theme:
                suggested_weapons = self._filter_weapons_by_theme(suggested_weapons, theme, character_data)
            
            # If character already has weapons, validate and enhance them
            existing_weapons = character_data.get("weapons", [])
            
            # For characters with no initial weapons, populate based on D&D 5e rules
            if not existing_weapons:
                weapon_count = min(3, 1 + level // 3)  # 1-3 weapons based on level
                existing_weapons = suggested_weapons[:weapon_count]
                logger.info(f"Auto-populated {len(existing_weapons)} weapons for level {level} character")
            
            # Validate and enhance existing weapons
            enhanced_weapons = []
            existing_weapon_names = set()
            
            for weapon in existing_weapons:
                if isinstance(weapon, dict) and "name" in weapon:
                    weapon_name = weapon["name"]
                    
                    # PRIORITY 1: Check if it's an official D&D 5e weapon
                    if is_existing_dnd_weapon(weapon_name):
                        enhanced_weapons.append(weapon)
                        existing_weapon_names.add(weapon_name)
                        logger.info(f"Validated existing D&D 5e weapon: {weapon_name}")
                    else:
                        # PRIORITY 2: Try to find a similar D&D weapon
                        similar_weapons = find_similar_weapons(weapon_name, 1)
                        if similar_weapons:
                            # Replace with official weapon
                            weapon_data = get_weapon_data(similar_weapons[0])
                            if weapon_data:
                                enhanced_weapons.append(weapon_data)
                                existing_weapon_names.add(similar_weapons[0])
                                logger.info(f"Replaced '{weapon_name}' with official D&D weapon: {similar_weapons[0]}")
                            else:
                                # Keep original if weapon data unavailable
                                weapon["source"] = "Custom"
                                enhanced_weapons.append(weapon)
                                existing_weapon_names.add(weapon_name)
                        else:
                            # PRIORITY 3: Keep custom weapon if no D&D equivalent
                            weapon["source"] = "Custom"
                            enhanced_weapons.append(weapon)
                            existing_weapon_names.add(weapon_name)
                            logger.info(f"Kept custom weapon: {weapon_name}")
            
            # PRIORITY 4: Fill remaining slots with official D&D weapons
            weapon_limit = min(4, 2 + level // 2)  # Scale weapons with level
            for suggested_weapon in suggested_weapons:
                if len(enhanced_weapons) >= weapon_limit:
                    break
                if isinstance(suggested_weapon, dict) and suggested_weapon.get("name") not in existing_weapon_names:
                    enhanced_weapons.append(suggested_weapon)
                    logger.info(f"Added suggested D&D 5e weapon: {suggested_weapon['name']}")
            
            character_data["weapons"] = enhanced_weapons
            
            # Normalize data types after weapon enhancement
            character_data = self._normalize_character_data_types(character_data)
            
            # Log weapon source breakdown
            dnd_weapons = len([w for w in enhanced_weapons if w.get('source') in ['D&D 5e Core', 'D&D 5e Official', None]])
            custom_weapons = len([w for w in enhanced_weapons if w.get('source') == 'Custom'])
            
            logger.info(f"Enhanced character with {len(enhanced_weapons)} weapons ({dnd_weapons} D&D 5e weapons, {custom_weapons} custom weapons)")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Weapon enhancement failed: {e}")
            return character_data

    async def _filter_weapons_by_theme(self, weapons: List[Dict[str, Any]], theme: str, character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Filter and prioritize weapons based on campaign theme using LLM-generated theme logic.
        Theme is suggestive - enhances weapon selection but doesn't override character concept.
        """
        if not theme or not weapons:
            return weapons
        
        try:
            # Generate theme-appropriate filtering logic using LLM
            theme_logic = await self._generate_theme_weapon_logic(theme, character_data)
            
            if not theme_logic:
                logger.info(f"Could not generate weapon theme logic for '{theme}', using all weapons")
                return weapons
            
            themed_weapons = []
            other_weapons = []
            
            # Apply LLM-generated theme logic to filter weapons
            for weapon in weapons:
                is_themed = self._evaluate_weapon_for_theme(weapon, theme_logic)
                
                if is_themed:
                    themed_weapons.append(weapon)
                else:
                    other_weapons.append(weapon)
            
            # Combine with themed weapons first (prioritized) followed by others
            filtered_weapons = themed_weapons + other_weapons
            
            if themed_weapons:
                logger.info(f"Theme '{theme}' filtering: {len(themed_weapons)} themed weapons prioritized, {len(other_weapons)} standard weapons available")
            else:
                logger.info(f"Theme '{theme}' filtering: No specific themed weapons found, using all {len(weapons)} weapons")
            
            return filtered_weapons
            
        except Exception as e:
            logger.warning(f"Theme-based weapon filtering failed: {e}")
            return weapons
    
    def _enhance_character_feats(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e feats based on their level.
        STRONGLY prioritizes existing D&D 5e feats over custom feat creation.
        """
        try:
            level = character_data.get("level", 1)
            classes = character_data.get("classes", {})
            
            # Get appropriate feats for this character level
            available_feats = get_available_feats_for_level(level)
            suggested_feats = get_appropriate_feats_for_character(character_data)
            
            # Validate and enhance origin feat
            origin_feat = character_data.get("origin_feat", "")
            if not origin_feat and level >= 1:
                # Default origin feat
                character_data["origin_feat"] = "Alert" if not suggested_feats else suggested_feats[0].get("name", "Alert")
                logger.info(f"Added default origin feat: {character_data['origin_feat']}")
            elif origin_feat:
                # Validate existing origin feat
                if is_existing_dnd_feat(origin_feat):
                    logger.info(f"Validated existing D&D 5e origin feat: {origin_feat}")
                else:
                    # Try to find similar feat
                    similar_feats = find_similar_feats(origin_feat, 1)
                    if similar_feats:
                        character_data["origin_feat"] = similar_feats[0]
                        logger.info(f"Replaced origin feat '{origin_feat}' with D&D feat: {similar_feats[0]}")
                    else:
                        logger.info(f"Kept custom origin feat: {origin_feat}")
            
            # Validate and enhance general feats
            general_feats = character_data.get("general_feats", [])
            general_feat_levels = [4, 8, 12, 16, 19]
            expected_feats = [l for l in general_feat_levels if l <= level]
            
            enhanced_general_feats = []
            for i, feat_level in enumerate(expected_feats):
                if i < len(general_feats):
                    # Validate existing feat
                    feat = general_feats[i]
                    if isinstance(feat, dict):
                        feat_name = feat.get("name", "")
                        if is_existing_dnd_feat(feat_name):
                            enhanced_general_feats.append(feat)
                            logger.info(f"Validated existing D&D 5e feat: {feat_name}")
                        else:
                            # Try to find similar feat
                            similar_feats = find_similar_feats(feat_name, 1)
                            if similar_feats:
                                feat_data = get_feat_data(similar_feats[0])
                                if feat_data:
                                    enhanced_general_feats.append({
                                        "name": similar_feats[0],
                                        "level": feat_level,
                                        "grants_asi": feat_data.get("grants_asi", False)
                                    })
                                    logger.info(f"Replaced feat '{feat_name}' with D&D feat: {similar_feats[0]}")
                                else:
                                    enhanced_general_feats.append(feat)
                            else:
                                # Keep custom feat
                                feat["source"] = "Custom"
                                enhanced_general_feats.append(feat)
                                logger.info(f"Kept custom feat: {feat_name}")
                    else:
                        # Add default feat if format is wrong
                        enhanced_general_feats.append({
                            "name": "Ability Score Improvement",
                            "level": feat_level,
                            "grants_asi": True
                        })
                else:
                    # Add missing feat
                    if suggested_feats and len(suggested_feats) > i:
                        feat_data = suggested_feats[i]
                        enhanced_general_feats.append({
                            "name": feat_data.get("name", "Ability Score Improvement"),
                            "level": feat_level,
                            "grants_asi": feat_data.get("grants_asi", True)
                        })
                    else:
                        enhanced_general_feats.append({
                            "name": "Ability Score Improvement",
                            "level": feat_level,
                            "grants_asi": True
                        })
                    logger.info(f"Added feat for level {feat_level}")
            
            character_data["general_feats"] = enhanced_general_feats
            
            # Handle epic boon for level 19+
            if level >= 19 and not character_data.get("epic_boon"):
                character_data["epic_boon"] = "Epic Boon of Combat Prowess"
                logger.info("Added epic boon for level 19+ character")
            
            # Ensure fighting style feats is initialized
            if "fighting_style_feats" not in character_data:
                character_data["fighting_style_feats"] = []
            
            logger.info(f"Enhanced character with {len(enhanced_general_feats)} general feats")
            return character_data
            
        except Exception as e:
            logger.warning(f"Feat enhancement failed: {e}")
            return character_data
    
    def _calculate_spell_slots(self, character_data: Dict[str, Any]) -> Dict[str, List[int]]:
        """
        Calculate spell slots based on character class and level according to D&D 5e rules.
        Returns a dictionary with spell slot counts for each spell level.
        """
        try:
            classes = character_data.get("classes", {})
            total_level = character_data.get("level", 1)
            
            # Initialize spell slots structure
            spell_slots = {
                "1st": 0, "2nd": 0, "3rd": 0, "4th": 0, "5th": 0,
                "6th": 0, "7th": 0, "8th": 0, "9th": 0
            }
            
            # Calculate spell slots for each class
            full_caster_levels = 0
            half_caster_levels = 0
            third_caster_levels = 0
            
            for class_name, class_level in classes.items():
                class_lower = class_name.lower()
                
                # Full casters (Wizard, Sorcerer, Cleric, Druid, Bard, Warlock)
                if any(keyword in class_lower for keyword in [
                    "wizard", "sorcerer", "cleric", "druid", "bard", "warlock",
                    "mage", "priest", "witch", "mystic"
                ]):
                    full_caster_levels += class_level
                
                # Half casters (Paladin, Ranger, Artificer)
                elif any(keyword in class_lower for keyword in [
                    "paladin", "ranger", "artificer", "knight", "hunter"
                ]):
                    if class_level >= 2:  # Half-casters start spellcasting at level 2
                        half_caster_levels += class_level
                
                # Third casters (Eldritch Knight, Arcane Trickster)
                elif any(keyword in class_lower for keyword in [
                    "eldritch", "arcane trickster", "spellsword"
                ]):
                    if class_level >= 3:  # Third-casters start spellcasting at level 3
                        third_caster_levels += class_level
                
                # Custom magical classes (treat as full casters)
                elif any(keyword in class_lower for keyword in [
                    "mancer", "elementalist", "void", "shadow", "blood"
                ]):
                    full_caster_levels += class_level
            
            # Calculate effective caster level
            effective_caster_level = (
                full_caster_levels + 
                (half_caster_levels // 2) + 
                (third_caster_levels // 3)
            )
            
            if effective_caster_level == 0:
                return spell_slots
            
            # D&D 5e spell slot progression table
            spell_slot_table = {
                1:  [2, 0, 0, 0, 0, 0, 0, 0, 0],
                2:  [3, 0, 0, 0, 0, 0, 0, 0, 0],
                3:  [4, 2, 0, 0, 0, 0, 0, 0, 0],
                4:  [4, 3, 0, 0, 0, 0, 0, 0, 0],
                5:  [4, 3, 2, 0, 0, 0, 0, 0, 0],
                6:  [4, 3, 3, 0, 0, 0, 0, 0, 0],
                7:  [4, 3, 3, 1, 0, 0, 0, 0, 0],
                8:  [4, 3, 3, 2, 0, 0, 0, 0, 0],
                9:  [4, 3, 3, 3, 1, 0, 0, 0, 0],
                10: [4, 3, 3, 3, 2, 0, 0, 0, 0],
                11: [4, 3, 3, 3, 2, 1, 0, 0, 0],
                12: [4, 3, 3, 3, 2, 1, 0, 0, 0],
                13: [4, 3, 3, 3, 2, 1, 1, 0, 0],
                14: [4, 3, 3, 3, 2, 1, 1, 0, 0],
                15: [4, 3, 3, 3, 2, 1, 1, 1, 0],
                16: [4, 3, 3, 3, 2, 1, 1, 1, 0],
                17: [4, 3, 3, 3, 2, 1, 1, 1, 1],
                18: [4, 3, 3, 3, 3, 1, 1, 1, 1],
                19: [4, 3, 3, 3, 3, 2, 1, 1, 1],
                20: [4, 3, 3, 3, 3, 2, 2, 1, 1]
            }
            
            # Get spell slots for effective caster level
            caster_level = min(effective_caster_level, 20)
            if caster_level in spell_slot_table:
                slots = spell_slot_table[caster_level]
                spell_slots = {
                    "1st": slots[0],
                    "2nd": slots[1],
                    "3rd": slots[2],
                    "4th": slots[3],
                    "5th": slots[4],
                    "6th": slots[5],
                    "7th": slots[6],
                    "8th": slots[7],
                    "9th": slots[8]
                }
            
            logger.info(f"Calculated spell slots for effective caster level {caster_level}: {spell_slots}")
            return spell_slots
            
        except Exception as e:
            logger.warning(f"Spell slot calculation failed: {e}")
            return {
                "1st": 0, "2nd": 0, "3rd": 0, "4th": 0, "5th": 0,
                "6th": 0, "7th": 0, "8th": 0, "9th": 0
            }
    
    def _enhance_character_armor(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Enhance character with appropriate D&D 5e armor based on their class and level.
        STRONGLY prioritizes existing D&D 5e armor over custom armor creation.
        """
        try:
            classes = character_data.get("classes", {})
            level = character_data.get("level", 1)
            
            # Get appropriate armor for this character (prioritizes existing D&D armor)
            suggested_armor = get_appropriate_armor_for_character(character_data)
            
            # If character already has armor, validate it
            existing_armor = character_data.get("armor", "")
            
            # For characters with no initial armor, populate based on D&D 5e rules
            if not existing_armor and suggested_armor:
                character_data["armor"] = suggested_armor["name"]
                logger.info(f"Auto-populated armor: {suggested_armor['name']} for level {level} character")
            elif existing_armor:
                # Validate existing armor
                if is_existing_dnd_armor(existing_armor):
                    logger.info(f"Validated existing D&D 5e armor: {existing_armor}")
                else:
                    # Try to find similar armor
                    similar_armor = find_similar_armor(existing_armor, 1)
                    if similar_armor:
                        character_data["armor"] = similar_armor[0]
                        logger.info(f"Replaced '{existing_armor}' with official D&D armor: {similar_armor[0]}")
                    else:
                        logger.info(f"Kept custom armor: {existing_armor}")
            else:
                # Default armor based on class
                default_armor = self._get_default_armor_for_class(classes)
                character_data["armor"] = default_armor
                logger.info(f"Added default armor: {default_armor}")
            
            return character_data
            
        except Exception as e:
            logger.warning(f"Armor enhancement failed: {e}")
            return character_data
    
    async def _generate_theme_spell_logic(self, theme: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate theme-appropriate spell filtering logic using LLM.
        Returns filtering criteria for the given theme.
        """
        try:
            character_concept = self._extract_character_concept(character_data)
            
            # Provide default traditional D&D logic if theme is traditional D&D
            if theme.lower() == "traditional d&d":
                return {
                    "keywords": ["magic", "arcane", "divine", "elemental", "force", "healing", "protection"],
                    "schools": ["evocation", "conjuration", "transmutation", "abjuration", "divination", "enchantment"],
                    "avoid": [],
                    "description": "Traditional D&D fantasy magic encompassing all schools and classic spell themes"
                }
            
            prompt = f"""Generate spell filtering logic for a '{theme}' campaign theme. Return ONLY JSON:

THEME: {theme}
CHARACTER: {character_concept}

Analyze what types of spells would fit this theme and return filtering criteria:

{{"keywords": ["word1", "word2", "word3"], "schools": ["school1", "school2"], "avoid": ["avoid1", "avoid2"], "description": "Brief description of why these spells fit the theme"}}

SPELL SCHOOLS: abjuration, conjuration, divination, enchantment, evocation, illusion, necromancy, transmutation

Consider the theme's atmosphere, technology level, cultural elements, and typical conflicts.
Think about what types of magic would be common, rare, or forbidden in this setting.
Keywords should relate to elements, concepts, or effects that match the theme.
Schools should reflect the types of magic that would be most prevalent.
Avoid should list schools or concepts that don't fit the theme.

Return complete JSON only."""

            response_data = await self._generate_with_llm(prompt, "theme_spell_logic")
            
            # Validate the response has the expected structure
            if isinstance(response_data, dict) and "keywords" in response_data:
                logger.info(f"Generated spell theme logic for '{theme}': {response_data.get('description', 'No description')}")
                return response_data
            else:
                logger.warning(f"Invalid theme logic response structure: {response_data}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to generate spell theme logic for '{theme}': {e}")
            return None

    async def _generate_theme_weapon_logic(self, theme: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate theme-appropriate weapon filtering logic using LLM.
        Returns filtering criteria for the given theme.
        """
        try:
            character_concept = self._extract_character_concept(character_data)
            
            # Provide default traditional D&D logic if theme is traditional D&D
            if theme.lower() == "traditional d&d":
                return {
                    "keywords": ["sword", "axe", "bow", "mace", "crossbow", "shield", "armor", "steel", "iron"],
                    "types": ["martial", "simple", "ranged", "melee"],
                    "avoid": ["firearm", "mechanical", "technological"],
                    "description": "Traditional D&D medieval fantasy weapons including swords, axes, bows, and classic armor"
                }
            
            prompt = f"""Generate weapon filtering logic for a '{theme}' campaign theme. Return ONLY JSON:

THEME: {theme}
CHARACTER: {character_concept}

Analyze what types of weapons would fit this theme and return filtering criteria:

{{"keywords": ["word1", "word2", "word3"], "types": ["type1", "type2"], "avoid": ["avoid1", "avoid2"], "description": "Brief description of why these weapons fit the theme"}}

WEAPON TYPES: simple, martial, ranged, melee, firearm, magical, natural, mechanical, blessed, silver, enchanted

Consider the theme's technology level, available materials, cultural preferences, and typical combat scenarios.
Think about what weapons would be common, rare, or forbidden in this setting.
Keywords should relate to weapon materials, styles, or types that match the theme.
Types should reflect the categories of weapons that would be most prevalent.
Avoid should list weapon types or materials that don't fit the theme.

Return complete JSON only."""

            response_data = await self._generate_with_llm(prompt, "theme_weapon_logic")
            
            # Validate the response has the expected structure
            if isinstance(response_data, dict) and "keywords" in response_data:
                logger.info(f"Generated weapon theme logic for '{theme}': {response_data.get('description', 'No description')}")
                return response_data
            else:
                logger.warning(f"Invalid weapon theme logic response structure: {response_data}")
                return None
                
        except Exception as e:
            logger.warning(f"Failed to generate weapon theme logic for '{theme}': {e}")
            return None

    def _evaluate_spell_for_theme(self, spell: Dict[str, Any], theme_logic: Dict[str, Any]) -> bool:
        """
        Evaluate if a spell matches the theme using LLM-generated logic.
        """
        try:
            spell_name = spell.get("name", "").lower()
            spell_desc = spell.get("description", "").lower()
            spell_school = spell.get("school", "").lower()
            
            # Check keywords in spell name and description
            keywords = theme_logic.get("keywords", [])
            if any(keyword.lower() in spell_name or keyword.lower() in spell_desc for keyword in keywords):
                return True
            
            # Check school preferences
            preferred_schools = theme_logic.get("schools", [])
            if spell_school in [school.lower() for school in preferred_schools]:
                return True
            
            # Avoid certain schools if specified
            avoid_schools = theme_logic.get("avoid", [])
            if spell_school in [school.lower() for school in avoid_schools]:
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Error evaluating spell for theme: {e}")
            return False

    def _evaluate_weapon_for_theme(self, weapon: Dict[str, Any], theme_logic: Dict[str, Any]) -> bool:
        """
        Evaluate if a weapon matches the theme using LLM-generated logic.
        """
        try:
            weapon_name = weapon.get("name", "").lower()
            weapon_desc = weapon.get("description", "").lower()
            weapon_type = weapon.get("type", "").lower()
            weapon_category = weapon.get("category", "").lower()
            
            # Check keywords in weapon name and description
            keywords = theme_logic.get("keywords", [])
            if any(keyword.lower() in weapon_name or keyword.lower() in weapon_desc for keyword in keywords):
                return True
            
            # Check type preferences
            preferred_types = theme_logic.get("types", [])
            if any(weapon_type_pref.lower() in weapon_type or weapon_type_pref.lower() in weapon_category 
                   for weapon_type_pref in preferred_types):
                return True
            
            # Avoid certain types if specified
            avoid_types = theme_logic.get("avoid", [])
            if any(avoid_type.lower() in weapon_name or avoid_type.lower() in weapon_desc or avoid_type.lower() in weapon_type 
                   for avoid_type in avoid_types):
                return False
            
            return False
            
        except Exception as e:
            logger.warning(f"Error evaluating weapon for theme: {e}")
            return False

    async def _create_character_comprehensive(self, prompt: str, level: int, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Comprehensive character creation logic for factory endpoint compatibility.
        This method orchestrates the use of all sub-generators and returns a complete character dict.
        """
        # Step 1: Generate ability scores
        ability_scores = self._generate_ability_scores(level, user_preferences)
        # Step 2: Select species and background
        species, background = self._select_species_and_background(prompt, user_preferences)
        # Step 3: Select class
        class_name, class_level = self._select_character_class(prompt, level, user_preferences)
        # Step 4: Generate spells for class (if spellcaster)
        spells_known = self._generate_spells_for_class(class_name, class_level, user_preferences)
        # Step 5: Generate equipment
        equipment = self._generate_equipment(class_name, species, background, user_preferences)
        # Step 6: Build character dict
        character = {
            "name": self._generate_character_name(prompt, user_preferences),
            "species": species,
            "background": background,
            "level": level,
            "character_classes": {class_name: class_level},
            "abilities": ability_scores,
            "spells_known": spells_known,
            "equipment": equipment,
            "backstory": self._generate_backstory(prompt, species, class_name, background, user_preferences),
        }
        return character

    def _generate_ability_scores(self, level: int, user_preferences: Optional[Dict[str, Any]] = None) -> Dict[str, int]:
        """Generate ability scores for a character (standard array or point buy)."""
        # Use standard array for simplicity
        return {"strength": 15, "dexterity": 14, "constitution": 13, "intelligence": 12, "wisdom": 10, "charisma": 8}

    def _select_species_and_background(self, prompt: str, user_preferences: Optional[Dict[str, Any]] = None) -> tuple[str, str]:
        """Select species and background based on prompt and preferences."""
        # Simple keyword-based selection for demo
        species = "Human"
        background = "Folk Hero"
        if user_preferences:
            species = user_preferences.get("species", species)
            background = user_preferences.get("background", background)
        if "elf" in prompt.lower():
            species = "Elf"
        if "wizard" in prompt.lower():
            background = "Sage"
        return species, background

    def _select_character_class(self, prompt: str, level: int, user_preferences: Optional[Dict[str, Any]] = None) -> tuple[str, int]:
        """Select class and level based on prompt and preferences."""
        class_name = "Fighter"
        if user_preferences:
            class_name = list(user_preferences.get("character_classes", {class_name: level}).keys())[0]
        if "wizard" in prompt.lower():
            class_name = "Wizard"
        elif "rogue" in prompt.lower():
            class_name = "Rogue"
        return class_name, level

    def _generate_spells_for_class(self, class_name: str, level: int, user_preferences: Optional[Dict[str, Any]] = None) -> list:
        """Generate a list of spells for the class if spellcaster."""
        if class_name.lower() in ["wizard", "sorcerer", "warlock", "bard", "cleric", "druid"]:
            # Return a few standard spells for demo
            return [
                {"name": "Magic Missile", "level": 1, "school": "evocation", "description": "A missile of magical energy."},
                {"name": "Shield", "level": 1, "school": "abjuration", "description": "A magical shield appears and protects you."}
            ]
        return []

    def _generate_equipment(self, class_name: str, species: str, background: str, user_preferences: Optional[Dict[str, Any]] = None) -> dict:
        """Generate starting equipment for the character."""
        # Simple demo: assign standard pack and weapon
        equipment = {"Adventurer's Pack": 1}
        if class_name == "Fighter":
            equipment["Longsword"] = 1
            equipment["Chain Mail"] = 1
        elif class_name == "Wizard":
            equipment["Quarterstaff"] = 1
            equipment["Spellbook"] = 1
        return equipment

    def _generate_character_name(self, prompt: str, user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Generate a character name from the prompt or preferences."""
        if user_preferences and user_preferences.get("name"):
            return user_preferences["name"]
        # Extract a name from the prompt if possible
        for word in prompt.split():
            if word.istitle() and len(word) > 2:
                return word
        return "Generated Character"

    def _generate_backstory(self, prompt: str, species: str, class_name: str, background: str, user_preferences: Optional[Dict[str, Any]] = None) -> str:
        """Generate a simple backstory for the character."""
        return f"A {species} {class_name} with a {background} background, seeking adventure."