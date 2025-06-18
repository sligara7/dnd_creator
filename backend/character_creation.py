"""
Character Creation Service - Refactored and Simplified

This module provides the main character creation workflow by integrating
the cleaned modular components. It handles the complete character creation
process including validation, generation, and iterative improvements.

Dependencies: All cleaned backend modules
"""

import asyncio
import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Callable

# Import from cleaned modules
from character_models import CharacterCore, CharacterState, CharacterSheet
from core_models import AbilityScore, ASIManager, MagicItemManager, CharacterLevelManager, ProficiencyLevel, AbilityScoreSource
from custom_content_models import ContentRegistry, FeatManager
from ability_management import AdvancedAbilityManager, CustomContentAbilityManager
from llm_services import create_llm_service, LLMService
from generators import BackstoryGenerator, CustomContentGenerator

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION AND RESULT CLASSES
# ============================================================================

@dataclass
class CreationConfig:
    """Configuration for character creation process."""
    base_timeout: int = 20
    backstory_timeout: int = 15
    custom_content_timeout: int = 30
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
# CHARACTER VALIDATOR
# ============================================================================

class CharacterValidator:
    """Handles validation of character data."""
    
    @staticmethod
    def validate_basic_structure(character_data: Dict[str, Any]) -> CreationResult:
        """Validate basic character data structure."""
        result = CreationResult()
        
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        missing_fields = [field for field in required_fields if field not in character_data]
        
        if missing_fields:
            result.error = f"Missing required fields: {', '.join(missing_fields)}"
            return result
        
        # Validate ability scores
        abilities = character_data.get("ability_scores", {})
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in abilities:
                result.add_warning(f"Missing ability score: {ability}")
            else:
                score = abilities[ability]
                if not isinstance(score, int) or score < 1 or score > 30:
                    result.add_warning(f"Invalid {ability} score: {score}")
        
        # Validate level
        level = character_data.get("level", 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            result.add_warning(f"Invalid character level: {level}")
        
        result.success = True
        result.data = character_data
        return result
    
    @staticmethod
    def validate_custom_content(character_data: Dict[str, Any], 
                              needs_custom_species: bool, needs_custom_class: bool) -> CreationResult:
        """Validate that custom content requirements are met."""
        result = CreationResult(success=True, data=character_data)
        
        # Check for custom species if needed
        if needs_custom_species:
            species = character_data.get("species", "").lower()
            standard_species = [
                "human", "elf", "dwarf", "halfling", "dragonborn", "gnome", 
                "half-elf", "half-orc", "tiefling", "aasimar", "genasi", 
                "goliath", "tabaxi", "kenku", "lizardfolk", "tortle"
            ]
            
            if species in standard_species:
                result.add_warning(f"Used standard species '{species}' when custom was expected")
        
        # Check for custom class if needed
        if needs_custom_class:
            classes = character_data.get("classes", {})
            class_names = [name.lower() for name in classes.keys()]
            standard_classes = [
                "barbarian", "bard", "cleric", "druid", "fighter", "monk",
                "paladin", "ranger", "rogue", "sorcerer", "warlock", "wizard",
                "artificer", "blood hunter"
            ]
            
            for class_name in class_names:
                if class_name in standard_classes:
                    result.add_warning(f"Used standard class '{class_name}' when custom was expected")
                    break
        
        return result

# ============================================================================
# CHARACTER DATA GENERATOR
# ============================================================================

class CharacterDataGenerator:
    """Handles core character data generation using LLM services."""
    
    def __init__(self, llm_service: LLMService, config: CreationConfig):
        self.llm_service = llm_service
        self.config = config
        self.validator = CharacterValidator()
    
    def generate_character_data(self, description: str, level: int) -> CreationResult:
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
                response = self.llm_service.generate(prompt, timeout_seconds=timeout)
                
                # Clean and parse response
                cleaned_response = self._clean_json_response(response)
                character_data = json.loads(cleaned_response)
                character_data["level"] = level
                
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
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
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
            "equipment": [{"name": "Adventurer's Pack", "quantity": 1}],
            "backstory": f"A fallback character based on: {description}"
        }
        
        result = CreationResult(success=True, data=fallback_data)
        result.add_warning("Used fallback character due to generation failures")
        result.creation_time = time.time() - start_time
        
        return result

# ============================================================================
# CHARACTER CREATOR
# ============================================================================

class CharacterCreator:
    """Main character creation service integrating all components."""
    
    def __init__(self, llm_service: LLMService = None, config: CreationConfig = None):
        self.llm_service = llm_service or create_llm_service()
        self.config = config or CreationConfig()
        
        # Initialize components
        self.content_registry = ContentRegistry()
        self.data_generator = CharacterDataGenerator(self.llm_service, self.config)
        self.backstory_generator = BackstoryGenerator(self.llm_service)
        self.custom_content_generator = CustomContentGenerator(self.llm_service)
        
        # Initialize managers
        self.feat_manager = FeatManager()
        
        logger.info("Character Creator initialized")
    
    def create_character(self, description: str, level: int = 1, 
                        generate_backstory: bool = True,
                        include_custom_content: bool = False) -> CreationResult:
        """Create a complete D&D character from description."""
        
        start_time = time.time()
        
        try:
            # Generate core character data
            logger.info(f"Creating character: {description} (Level {level})")
            data_result = self.data_generator.generate_character_data(description, level)
            
            if not data_result.success:
                return data_result
            
            character_data = data_result.data
            
            # Create CharacterCore from the data
            character_core = self._build_character_core(character_data)
            
            # Create managers for the character
            asi_manager = ASIManager()
            level_manager = CharacterLevelManager()
            ability_manager = AdvancedAbilityManager(character_core)
            
            # Generate backstory if requested
            backstory = None
            if generate_backstory:
                backstory_prompt = self._build_backstory_prompt(character_data)
                backstory = self.backstory_generator.generate_backstory(backstory_prompt)
            
            # Generate custom content if requested
            custom_content = {}
            if include_custom_content:
                custom_content = self._generate_custom_content(character_data, description)
            
            # Create character sheet
            character_state = CharacterState()
            character_sheet = CharacterSheet(character_core, character_state)
            
            # Build final result
            result_data = {
                "core": character_core.to_dict(),
                "sheet": character_sheet.generate_sheet(),
                "backstory": backstory,
                "custom_content": custom_content,
                "managers": {
                    "asi_info": asi_manager.calculate_available_asis(character_core.character_classes),
                    "level_summary": level_manager.get_level_progression_summary(character_core.character_classes),
                    "ability_summary": ability_manager.get_ability_summary()
                }
            }
            
            result = CreationResult(success=True, data=result_data)
            result.warnings.extend(data_result.warnings)
            result.creation_time = time.time() - start_time
            
            logger.info(f"Character creation completed in {result.creation_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Character creation failed: {e}")
            result = CreationResult(error=str(e))
            result.creation_time = time.time() - start_time
            return result
    
    def _build_character_core(self, character_data: Dict[str, Any]) -> CharacterCore:
        """Build a CharacterCore from character data."""
        
        character_core = CharacterCore(character_data["name"])
        character_core.race = character_data.get("species", "Human")
        character_core.background = character_data.get("background", "Folk Hero")
        character_core.character_classes = character_data.get("classes", {"Fighter": 1})
        
        # Set ability scores
        ability_scores = character_data.get("ability_scores", {})
        for ability_name, score in ability_scores.items():
            if hasattr(character_core, ability_name):
                setattr(character_core, ability_name, AbilityScore(score))
        
        return character_core
    
    def _build_backstory_prompt(self, character_data: Dict[str, Any]) -> str:
        """Build a backstory generation prompt from character data."""
        
        classes = character_data.get("classes", {})
        class_list = ", ".join([f"{cls} {level}" for cls, level in classes.items()])
        
        prompt = f"""Create a compelling backstory for this D&D character:

Name: {character_data.get('name', 'Unknown')}
Species: {character_data.get('species', 'Human')}
Classes: {class_list}
Background: {character_data.get('background', 'Folk Hero')}
Personality: {', '.join(character_data.get('personality_traits', ['Brave']))}
Ideals: {', '.join(character_data.get('ideals', ['Justice']))}
Bonds: {', '.join(character_data.get('bonds', ['Community']))}
Flaws: {', '.join(character_data.get('flaws', ['Stubborn']))}

Generate a rich, detailed backstory that explains their motivations, background, and how they became an adventurer."""
        
        return prompt
    
    def _generate_custom_content(self, character_data: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Generate custom content based on character data."""
        
        custom_content = {}
        
        # Generate custom species if needed
        species = character_data.get("species", "")
        standard_species = ["human", "elf", "dwarf", "halfling", "dragonborn", "gnome"]
        
        if species.lower() not in standard_species:
            try:
                custom_species = self.custom_content_generator.generate_custom_species(
                    f"Create a custom species called '{species}' based on: {description}"
                )
                custom_content["species"] = custom_species.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom species: {e}")
        
        # Generate custom background if non-standard
        background = character_data.get("background", "")
        standard_backgrounds = ["acolyte", "criminal", "folk hero", "noble", "sage", "soldier"]
        
        if background.lower() not in standard_backgrounds:
            try:
                # Use content registry to create custom background
                background_id = self.content_registry.add_custom_background(
                    background,
                    f"Custom background: {background}",
                    character_data.get("skill_proficiencies", [])[:2],
                    character_data.get("equipment", [])[:3]
                )
                custom_background = self.content_registry.get_custom_background(background_id)
                if custom_background:
                    custom_content["background"] = custom_background.__dict__
            except Exception as e:
                logger.warning(f"Failed to generate custom background: {e}")
        
        return custom_content

# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def create_character(description: str, level: int = 1, 
                    generate_backstory: bool = True,
                    include_custom_content: bool = False,
                    llm_service: LLMService = None) -> CreationResult:
    """Convenience function to create a character."""
    
    creator = CharacterCreator(llm_service)
    return creator.create_character(description, level, generate_backstory, include_custom_content)

def quick_character(name: str, species: str = "Human", character_class: str = "Fighter", level: int = 1) -> CharacterCore:
    """Create a simple character quickly without LLM generation."""
    
    character = CharacterCore(name)
    character.race = species
    character.character_classes = {character_class: level}
    
    # Set default ability scores
    character.strength = AbilityScore(15)
    character.dexterity = AbilityScore(13)
    character.constitution = AbilityScore(14)
    character.intelligence = AbilityScore(12)
    character.wisdom = AbilityScore(10)
    character.charisma = AbilityScore(8)
    
    return character

# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
REFACTORED CHARACTER CREATION MODULE

This module has been cleaned and refactored to use the cleaned backend modules:

CLASSES:
- CreationConfig: Configuration for character creation
- CreationResult: Result container with success/error/warning info
- CharacterValidator: Validates character data structure and content
- CharacterDataGenerator: Generates character data using LLM services
- CharacterCreator: Main integration service

KEY FEATURES:
- Clean integration with all refactored modules
- Comprehensive error handling and validation
- Retry logic for LLM generation failures
- Support for custom content generation
- Backstory generation integration
- Fallback character creation when LLM fails

DEPENDENCIES:
- character_models: CharacterCore, CharacterState, CharacterSheet
- core_models: AbilityScore, ASIManager, etc.
- custom_content_models: ContentRegistry, managers
- ability_management: AdvancedAbilityManager
- llm_services: LLM integration
- generators: BackstoryGenerator, CustomContentGenerator

REMOVED:
- Duplicate code and classes
- Legacy/example code
- Overly complex inheritance hierarchies
- Unused async functionality
- Dead code paths
"""
