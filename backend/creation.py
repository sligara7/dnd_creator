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
            
            # Step 1: Generate base character data
            level = user_preferences.get("level", 1) if user_preferences else 1
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
            
            # Step 5: Create final character sheet
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
        """Create character generation prompt."""
        return f"""Create D&D character. Return ONLY JSON:

DESCRIPTION: {description}
LEVEL: {level}

{{"name":"Name","species":"Species","level":{level},"classes":{{"Class":{level}}},"background":"Background","alignment":["Ethics","Morals"],"ability_scores":{{"strength":15,"dexterity":14,"constitution":13,"intelligence":12,"wisdom":10,"charisma":8}},"skill_proficiencies":["Skill1","Skill2"],"personality_traits":["Trait"],"ideals":["Ideal"],"bonds":["Bond"],"flaws":["Flaw"],"armor":"Armor","weapons":[{{"name":"Weapon","damage":"1d8","properties":["property"]}}],"equipment":{{"Item":1}},"backstory":"Brief backstory"}}

Match description exactly. Return complete JSON only."""
    
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
            
            # Create character sheet using the quick method
            character_sheet = self._quick_character_sheet(name, species, primary_class, level)
            
            # Combine all character information
            final_character = {
                "core": character_core,
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
            logger.error(f"Failed to create final character: {e}")
            return character_data
    
    def _quick_character_sheet(self, name: str, species: str = "Human", 
                              character_class: str = "Fighter", level: int = 1) -> CharacterSheet:
        """Create a simple character sheet quickly."""
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
        
        return character_sheet

# ============================================================================
# NPC CREATOR - SUBSET OF CHARACTER CREATION
# ============================================================================

class NPCCreator(BaseCreator):
    """
    NPC creation using a subset of character creation functionality.
    NPCs don't need the full feature set - just basic stats and roleplay elements.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        super().__init__(llm_service, config)
        
        # Use the character creator for the foundation
        self.character_creator = CharacterCreator(llm_service, config)
        
        logger.info("NPCCreator initialized using character creation foundation")
    
    async def create_npc(self, prompt: str, npc_type: NPCType = NPCType.MAJOR, 
                        npc_role: NPCRole = NPCRole.CIVILIAN) -> CreationResult:
        """
        Create an NPC using simplified character creation.
        This reuses character creation but focuses on NPC-specific needs.
        """
        start_time = time.time()
        
        try:
            logger.info(f"Creating NPC: {prompt[:100]}... (Type: {npc_type.value}, Role: {npc_role.value})")
            
            # Step 1: Create base character data (reuse character creation)
            character_data = await self.character_creator._generate_character_data(prompt, level=5)  # Default level for NPCs
            
            # Step 2: Enhance with NPC-specific elements
            npc_data = await self._enhance_for_npc(character_data, prompt, npc_type, npc_role)
            
            # Step 3: Create NPC-appropriate result
            final_npc = self._create_npc_result(npc_data, npc_type)
            
            result = CreationResult(success=True, data=final_npc)
            result.creation_time = time.time() - start_time
            
            logger.info(f"NPC creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"NPC creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"NPC creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    async def _enhance_for_npc(self, character_data: Dict[str, Any], prompt: str, 
                              npc_type: NPCType, npc_role: NPCRole) -> Dict[str, Any]:
        """Add NPC-specific enhancements to character data."""
        try:
            # Create NPC-specific enhancement prompt
            npc_prompt = f"""Enhance this character for NPC use. Return ONLY JSON:

BASE CHARACTER: {character_data.get('name', 'Unknown')} - {self._extract_character_concept(character_data)}
NPC TYPE: {npc_type.value}
NPC ROLE: {npc_role.value}
DESCRIPTION: {prompt}

{{"personality": "Detailed personality traits","motivations": ["motivation1", "motivation2"],"secrets": ["secret1"],"relationships": {{"relationship_type": "description"}},"location": "Where they can be found","occupation": "Their job or role","quirks": ["memorable quirk1", "quirk2"],"dm_notes": "Useful DM information"}}

Make this NPC memorable and useful for the DM."""
            
            npc_enhancements = await self._generate_with_llm(npc_prompt, "npc_enhancement")
            
            # Merge character data with NPC enhancements
            enhanced_data = character_data.copy()
            enhanced_data.update(npc_enhancements)
            enhanced_data["npc_type"] = npc_type.value
            enhanced_data["npc_role"] = npc_role.value
            
            return enhanced_data
            
        except Exception as e:
            logger.warning(f"NPC enhancement failed: {e}")
            # Return base character data with minimal NPC info
            character_data["npc_type"] = npc_type.value
            character_data["npc_role"] = npc_role.value
            character_data["personality"] = "A typical NPC with standard motivations."
            return character_data
    
    def _create_npc_result(self, npc_data: Dict[str, Any], npc_type: NPCType) -> Dict[str, Any]:
        """Create final NPC result structure."""
        return {
            "name": npc_data.get("name", "Unknown NPC"),
            "type": "npc",
            "npc_type": npc_type.value,
            "npc_role": npc_data.get("npc_role", "civilian"),
            "basic_info": {
                "species": npc_data.get("species", "Human"),
                "classes": npc_data.get("classes", {"Commoner": 1}),
                "alignment": npc_data.get("alignment", ["Neutral", "Good"])
            },
            "roleplay": {
                "personality": npc_data.get("personality", "Friendly and helpful"),
                "motivations": npc_data.get("motivations", ["Help others"]),
                "secrets": npc_data.get("secrets", []),
                "quirks": npc_data.get("quirks", [])
            },
            "location_info": {
                "location": npc_data.get("location", "Local tavern"),
                "occupation": npc_data.get("occupation", "Commoner"),
                "relationships": npc_data.get("relationships", {})
            },
            "dm_notes": npc_data.get("dm_notes", "A helpful NPC for the party."),
            "creation_metadata": {
                "created_at": time.time(),
                "version": "2024",
                "generator": "NPCCreator"
            }
        }

# ============================================================================
# CREATURE CREATOR - BASIC STATS USING CHARACTER FOUNDATION
# ============================================================================

class CreatureCreator(BaseCreator):
    """
    Creature creation using character creation as foundation for stat generation.
    Creatures need basic stats but not the full character feature set.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        super().__init__(llm_service, config)
        
        # Use character creator for stat generation foundation
        self.character_creator = CharacterCreator(llm_service, config)
        
        logger.info("CreatureCreator initialized using character creation foundation")
    
    async def create_creature(self, description: str, challenge_rating: float = 1.0, 
                             creature_type: str = "beast") -> CreationResult:
        """
        Create a creature using character creation foundation for stats.
        """
        start_time = time.time()
        
        try:
            logger.info(f"Creating creature: {description[:100]}... (CR {challenge_rating})")
            
            # Step 1: Generate creature using specialized prompt
            creature_data = await self._generate_creature_data(description, challenge_rating, creature_type)
            
            # Step 2: Validate and enhance
            creature_data = validate_and_enhance_creature(creature_data, challenge_rating)
            
            result = CreationResult(success=True, data=creature_data)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Creature creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Creature creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Creature creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    async def _generate_creature_data(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Generate creature data using specialized prompt."""
        try:
            creature_prompt = f"""Create D&D 5e 2024 creature. Return ONLY JSON:

DESCRIPTION: {description}
CHALLENGE RATING: {challenge_rating}
CREATURE TYPE: {creature_type}

{{"name":"Creature Name","size":"Medium","type":"{creature_type}","challenge_rating":{challenge_rating},"armor_class":12,"hit_points":25,"speed":{{"walk":"30 ft"}},"abilities":{{"strength":15,"dexterity":12,"constitution":14,"intelligence":8,"wisdom":10,"charisma":6}},"saving_throws":[],"skills":["Perception +2"],"damage_resistances":[],"damage_immunities":[],"condition_immunities":[],"senses":["passive Perception 12"],"languages":["Common"],"description":"Creature description","actions":[{{"name":"Attack","description":"Basic attack","attack_bonus":"+4","damage":"1d8+2 slashing"}}],"special_abilities":[]}}

Make this creature unique and balanced for CR {challenge_rating}."""
            
            creature_data = await self._generate_with_llm(creature_prompt, "creature")
            return creature_data
            
        except Exception as e:
            logger.warning(f"Creature generation failed, using fallback: {e}")
            return self._create_fallback_creature(description, challenge_rating, creature_type)
    
    def _create_fallback_creature(self, description: str, challenge_rating: float, creature_type: str) -> Dict[str, Any]:
        """Create a basic creature when generation fails."""
        hp = max(10, int(challenge_rating * 20 + 10))
        ac = max(10, int(challenge_rating + 10))
        attack_bonus = max(2, int(challenge_rating + 2))
        
        return {
            "name": f"{creature_type.title()} Creature",
            "size": "Medium",
            "type": creature_type,
            "challenge_rating": challenge_rating,
            "armor_class": ac,
            "hit_points": hp,
            "speed": {"walk": "30 ft"},
            "abilities": {
                "strength": 12, "dexterity": 12, "constitution": 12,
                "intelligence": 8, "wisdom": 12, "charisma": 8
            },
            "saving_throws": [],
            "skills": ["Perception +2"],
            "damage_resistances": [],
            "damage_immunities": [],
            "condition_immunities": [],
            "senses": ["passive Perception 12"],
            "languages": [],
            "description": f"A {creature_type} creature",
            "actions": [
                {
                    "name": "Basic Attack",
                    "description": "A simple attack",
                    "attack_bonus": f"+{attack_bonus}",
                    "damage": f"1d6+{challenge_rating//2} bludgeoning"
                }
            ],
            "special_abilities": []
        }

# ============================================================================
# ITEM CREATOR - FOCUSED ON ITEMS WITH CHARACTER INTEGRATION
# ============================================================================

class ItemCreator(BaseCreator):
    """
    Item creation with character integration.
    Uses character concept extraction for appropriate item generation.
    """
    
    def __init__(self, llm_service: Optional[LLMService] = None, config: Optional[CreationConfig] = None):
        super().__init__(llm_service, config)
        self.magic_item_manager = MagicItemManager()
        
        logger.info("ItemCreator initialized with character integration")
    
    async def create_item(self, description: str, item_type: ItemType, 
                         character_level: int = 1, character_concept: str = "",
                         rarity: Optional[ItemRarity] = None) -> CreationResult:
        """Create an item using character-focused approach."""
        start_time = time.time()
        
        try:
            logger.info(f"Creating {item_type.value}: {description}")
            
            # Determine appropriate rarity for level
            if rarity is None:
                rarity = self._determine_rarity_for_level(character_level)
            
            # Create item-specific prompt
            item_data = await self._generate_item_data(description, item_type, character_level, character_concept, rarity)
            
            result = CreationResult(success=True, data=item_data)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Item creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Item creation failed: {str(e)}")
            result = CreationResult()
            result.error = f"Item creation failed: {str(e)}"
            result.creation_time = time.time() - start_time
            return result
    
    async def _generate_item_data(self, description: str, item_type: ItemType,
                                 character_level: int, character_concept: str, rarity: ItemRarity) -> Dict[str, Any]:
        """Generate item data using specialized prompt."""
        item_prompt = f"""Create D&D 5e 2024 {item_type.value}. Return ONLY JSON:

DESCRIPTION: {description}
CHARACTER LEVEL: {character_level}
CHARACTER CONCEPT: {character_concept}
RARITY: {rarity.value}

{{"name":"Item Name","type":"{item_type.value}","rarity":"{rarity.value}","description":"Item description","properties":["property1"],"requires_attunement":false,"weight":1.0,"value":100}}

Match description and character concept. Return complete JSON only."""
        
        item_data = await self._generate_with_llm(item_prompt, f"{item_type.value}_item")
        return item_data
    
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

# ============================================================================
# UTILITY FUNCTIONS FOR BACKWARDS COMPATIBILITY
# ============================================================================

async def create_character_from_prompt(prompt: str, level: int = 1) -> CreationResult:
    """Utility function for simple character creation."""
    creator = CharacterCreator()
    return await creator.create_character(prompt, {"level": level})

async def create_npc_from_prompt(prompt: str, npc_type: NPCType = NPCType.MAJOR) -> CreationResult:
    """Utility function for simple NPC creation."""
    creator = NPCCreator()
    return await creator.create_npc(prompt, npc_type)

async def create_creature_from_prompt(prompt: str, challenge_rating: float = 1.0) -> CreationResult:
    """Utility function for simple creature creation."""
    creator = CreatureCreator()
    return await creator.create_creature(prompt, challenge_rating)

async def create_item_from_prompt(prompt: str, item_type: ItemType = ItemType.MAGIC_ITEM,
                                 character_level: int = 1) -> CreationResult:
    """Utility function for simple item creation."""
    creator = ItemCreator()
    return await creator.create_item(prompt, item_type, character_level)
