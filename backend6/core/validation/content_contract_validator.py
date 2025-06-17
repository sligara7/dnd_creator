"""
Content contract validation that enforces D&D abstract requirements.

This module bridges the gap between abstract contracts and generated content,
ensuring all creative content adheres to D&D framework requirements.
"""

from typing import Dict, List, Any, Type, Optional
from dataclasses import dataclass
from ..abstractions.spell import AbstractSpell
from ..abstractions.character_class import AbstractCharacterClass
from ..abstractions.species import AbstractSpecies
from ..abstractions.equipment import AbstractEquipment
from ..enums.content_types import ContentType
from ..enums.dnd_constants import SpellLevel, MagicSchool, Ability


@dataclass
class ValidationResult:
    """Result of content validation against abstract contract."""
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    fixed_content: Optional[Dict[str, Any]] = None


class ContentContractValidator:
    """
    Validates generated content against D&D abstract contracts.
    
    This is the critical bridge ensuring creative content follows D&D rules
    while preserving creative flexibility where appropriate.
    """
    
    # Define flexibility matrix - what can and cannot be customized
    FLEXIBILITY_MATRIX = {
        ContentType.SPELL: {
            "inflexible": {
                "level": "Must be 0-9",
                "casting_time": "Must use standard D&D formats",
                "range": "Must use D&D measurement units",
                "duration": "Must use D&D time units",
                "components": "Must be V, S, M combinations",
                "school": "Must be one of 8 D&D schools"
            },
            "flexible": {
                "name": "Any creative name allowed",
                "description": "Unlimited creative freedom",
                "damage_type": "Custom damage types allowed",
                "area_of_effect": "Creative shapes within reason",
                "saving_throw": "Any ability save allowed"
            }
        },
        ContentType.CHARACTER_CLASS: {
            "inflexible": {
                "hit_die": "Must be d6, d8, d10, or d12",
                "proficiency_bonus": "Must follow standard progression",
                "level_cap": "Must cap at 20",
                "saving_throws": "Must be exactly 2 proficiencies"
            },
            "flexible": {
                "class_features": "Unlimited creative freedom",
                "subclasses": "Custom archetypes allowed",
                "equipment_proficiencies": "Custom items allowed",
                "spell_lists": "Custom spell selections allowed"
            }
        },
        ContentType.SPECIES: {
            "inflexible": {
                "ability_score_total": "Total ASI cannot exceed +3",
                "size": "Must be Tiny through Gargantuan",
                "speed": "Must be reasonable (10-50 feet typical)"
            },
            "flexible": {
                "racial_features": "Creative abilities allowed",
                "culture": "Unlimited cultural creativity",
                "appearance": "Any physical description",
                "languages": "Custom languages allowed"
            }
        }
    }
    
    @classmethod
    def validate_content(
        cls, 
        content_data: Dict[str, Any], 
        content_type: ContentType
    ) -> ValidationResult:
        """
        Validate content against its abstract contract.
        
        This is THE method that ensures D&D compliance while preserving creativity.
        """
        errors = []
        warnings = []
        
        if content_type == ContentType.SPELL:
            errors.extend(cls._validate_spell_contract(content_data))
        elif content_type == ContentType.CHARACTER_CLASS:
            errors.extend(cls._validate_class_contract(content_data))
        elif content_type == ContentType.SPECIES:
            errors.extend(cls._validate_species_contract(content_data))
        elif content_type == ContentType.EQUIPMENT:
            errors.extend(cls._validate_equipment_contract(content_data))
        
        # Try to auto-fix common issues
        fixed_content = None
        if errors:
            fixed_content = cls._attempt_auto_fix(content_data, content_type, errors)
            
            # Re-validate fixed content
            if fixed_content:
                re_validation = cls.validate_content(fixed_content, content_type)
                if re_validation.is_valid:
                    warnings.append("Content was auto-fixed to meet D&D requirements")
                    errors = []
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            fixed_content=fixed_content
        )
    
    @classmethod
    def _validate_spell_contract(cls, spell_data: Dict[str, Any]) -> List[str]:
        """Validate spell against AbstractSpell contract."""
        errors = []
        
        # INFLEXIBLE requirements from AbstractSpell
        required_fields = ["name", "level", "school", "casting_time", "range", "duration", "components"]
        
        for field in required_fields:
            if field not in spell_data or spell_data[field] is None:
                errors.append(f"Spell missing required D&D field: {field}")
        
        # Validate spell level (0-9 only)
        level = spell_data.get("level")
        if level is not None:
            try:
                level_int = int(level)
                if not (0 <= level_int <= 9):
                    errors.append(f"Invalid spell level {level}: must be 0-9")
            except (ValueError, TypeError):
                errors.append(f"Spell level must be integer 0-9, got: {level}")
        
        # Validate school
        school = spell_data.get("school")
        if school:
            valid_schools = [s.value for s in MagicSchool]
            if school not in valid_schools:
                errors.append(f"Invalid spell school '{school}': must be one of {valid_schools}")
        
        # Validate components format
        components = spell_data.get("components")
        if components and not cls._validate_spell_components(components):
            errors.append(f"Invalid components format '{components}': must be V, S, M combinations")
        
        return errors
    
    @classmethod
    def _validate_class_contract(cls, class_data: Dict[str, Any]) -> List[str]:
        """Validate class against AbstractCharacterClass contract."""
        errors = []
        
        # INFLEXIBLE requirements
        required_fields = ["name", "hit_die", "primary_ability", "saving_throw_proficiencies"]
        
        for field in required_fields:
            if field not in class_data or class_data[field] is None:
                errors.append(f"Class missing required D&D field: {field}")
        
        # Validate hit die (must be standard D&D dice)
        hit_die = class_data.get("hit_die")
        if hit_die is not None:
            try:
                hit_die_int = int(hit_die)
                if hit_die_int not in [6, 8, 10, 12]:
                    errors.append(f"Invalid hit die d{hit_die}: must be d6, d8, d10, or d12")
            except (ValueError, TypeError):
                errors.append(f"Hit die must be integer, got: {hit_die}")
        
        # Validate saving throw proficiencies (exactly 2)
        saves = class_data.get("saving_throw_proficiencies", [])
        if len(saves) != 2:
            errors.append(f"Class must have exactly 2 saving throw proficiencies, has {len(saves)}")
        
        # Validate primary ability
        primary_ability = class_data.get("primary_ability")
        if primary_ability:
            valid_abilities = [a.value for a in Ability]
            if primary_ability not in valid_abilities:
                errors.append(f"Invalid primary ability '{primary_ability}': must be one of {valid_abilities}")
        
        return errors
    
    @classmethod
    def _validate_species_contract(cls, species_data: Dict[str, Any]) -> List[str]:
        """Validate species against AbstractSpecies contract."""
        errors = []
        
        # INFLEXIBLE requirements
        required_fields = ["name", "size", "speed", "ability_score_increases"]
        
        for field in required_fields:
            if field not in species_data or species_data[field] is None:
                errors.append(f"Species missing required D&D field: {field}")
        
        # Validate ability score increases (total cannot exceed +3)
        asi = species_data.get("ability_score_increases", {})
        if asi:
            total_asi = sum(int(v) for v in asi.values() if str(v).isdigit())
            if total_asi > 3:
                errors.append(f"Total ability score increases ({total_asi}) exceed D&D maximum (+3)")
        
        # Validate size
        size = species_data.get("size")
        if size:
            valid_sizes = ["Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"]
            if size not in valid_sizes:
                errors.append(f"Invalid size '{size}': must be one of {valid_sizes}")
        
        # Validate speed (reasonable range)
        speed = species_data.get("speed")
        if speed is not None:
            try:
                speed_int = int(str(speed).replace(" feet", "").replace("ft", "").strip())
                if not (5 <= speed_int <= 60):  # Reasonable range
                    errors.append(f"Speed {speed} outside reasonable range (5-60 feet)")
            except (ValueError, TypeError):
                errors.append(f"Invalid speed format: {speed}")
        
        return errors
    
    @classmethod
    def _validate_equipment_contract(cls, equipment_data: Dict[str, Any]) -> List[str]:
        """Validate equipment against AbstractEquipment contract."""
        errors = []
        
        # Basic requirements
        required_fields = ["name", "type", "rarity"]
        
        for field in required_fields:
            if field not in equipment_data or equipment_data[field] is None:
                errors.append(f"Equipment missing required D&D field: {field}")
        
        # Validate rarity
        rarity = equipment_data.get("rarity")
        if rarity:
            valid_rarities = ["Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Artifact"]
            if rarity not in valid_rarities:
                errors.append(f"Invalid rarity '{rarity}': must be one of {valid_rarities}")
        
        return errors
    
    @classmethod
    def _validate_spell_components(cls, components: str) -> bool:
        """Validate spell components format."""
        if not components:
            return False
        
        # Must contain V, S, or M
        valid_components = {'V', 'S', 'M'}
        component_parts = [c.strip() for c in components.split(',')]
        
        for part in component_parts:
            if part not in valid_components and not part.startswith('M ('):
                return False
        
        return True
    
    @classmethod
    def _attempt_auto_fix(
        cls, 
        content_data: Dict[str, Any], 
        content_type: ContentType, 
        errors: List[str]
    ) -> Optional[Dict[str, Any]]:
        """Attempt to automatically fix common validation errors."""
        fixed_data = content_data.copy()
        
        for error in errors:
            if "spell level" in error.lower() and "must be 0-9" in error:
                # Try to fix spell level
                level = fixed_data.get("level")
                if level is not None:
                    try:
                        level_int = int(level)
                        if level_int < 0:
                            fixed_data["level"] = 0
                        elif level_int > 9:
                            fixed_data["level"] = 9
                    except (ValueError, TypeError):
                        fixed_data["level"] = 1  # Default to 1st level
            
            elif "hit die" in error.lower():
                # Try to fix hit die
                hit_die = fixed_data.get("hit_die")
                if hit_die is not None:
                    try:
                        hit_die_int = int(hit_die)
                        if hit_die_int < 6:
                            fixed_data["hit_die"] = 6
                        elif hit_die_int > 12:
                            fixed_data["hit_die"] = 12
                        elif hit_die_int not in [6, 8, 10, 12]:
                            # Round to nearest valid die
                            valid_dice = [6, 8, 10, 12]
                            fixed_data["hit_die"] = min(valid_dice, key=lambda x: abs(x - hit_die_int))
                    except (ValueError, TypeError):
                        fixed_data["hit_die"] = 8  # Default to d8
        
        return fixed_data if fixed_data != content_data else None
    
    @classmethod
    def get_flexibility_info(cls, content_type: ContentType) -> Dict[str, Dict[str, str]]:
        """Get flexibility information for a content type."""
        return cls.FLEXIBILITY_MATRIX.get(content_type, {})
    
from abc import ABC
from enum import Enum
from typing import Dict, List, Set, Optional, Union, Tuple, Any, Type, TypeVar, Callable
from functools import wraps
import re
import logging
from datetime import datetime

from abstract_spells import AbstractSpell, AbstractSpells
from abstract_species import AbstractSpecies
from abstract_skills import AbstractSkills
from abstract_equipment import AbstractEquipment, AbstractWeapon, AbstractArmor
from abstract_feats import AbstractFeat
from abstract_backgrounds import AbstractBackground
from abstract_classes import AbstractClass

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Type variable for method decorators
F = TypeVar('F', bound=Callable[..., Any])

class CreativeRules2024(ABC):
    """
    Rule engine for D&D 2024 Edition with enhanced support for homebrew content.
    
    This class provides a robust framework for defining, validating, and managing:
    - Custom character classes
    - Custom species
    - Custom feats and spells
    - Custom equipment (weapons and armor)
    - Custom skills
    - Custom backgrounds
    - Custom lineages
    
    It enforces game balance through validation while allowing creative freedom.
    """
    
    # ===== CORE RULES AND CONSTANTS =====
    
    # Ability Score Rules
    ABILITY_SCORE_MIN = 3
    ABILITY_SCORE_MAX = 30  # Increased from 20 to allow for exceptional beings
    STANDARD_ARRAY = [15, 14, 13, 12, 10, 8]
    POINT_BUY_POINTS = 27
    POINT_BUY_COSTS = {
        8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5,
        14: 7, 15: 9, 16: 11, 17: 14, 18: 18
    }
    
    # Character Level Rules
    MIN_LEVEL = 1
    MAX_LEVEL = 20
    XP_BY_LEVEL = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Proficiency Bonus by Level
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Valid Hit Die Sizes
    VALID_HIT_DIE_SIZES = [4, 6, 8, 10, 12]
    
    # Base classes and content registries
    BASE_CLASSES = {
        "Artificer", "Barbarian", "Bard", "Cleric", "Druid", "Fighter",
        "Monk", "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    }
    
    # Base backgrounds
    BASE_BACKGROUNDS = {
        "Acolyte", "Charlatan", "Criminal", "Entertainer", "Folk Hero", "Guild Artisan",
        "Hermit", "Noble", "Outlander", "Sage", "Sailor", "Soldier", "Urchin"
    }
    
    # Base lineages
    BASE_LINEAGES = {
        "Human", "Elf", "Dwarf", "Halfling", "Dragonborn", "Gnome", "Half-Elf", 
        "Half-Orc", "Tiefling"
    }

    # Base languages
    BASE_LANGUAGES = {
        "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", "Halfling", 
        "Orc", "Abyssal", "Celestial", "Draconic", "Deep Speech", "Infernal", 
        "Primordial", "Sylvan", "Undercommon"
    }
    
    # Vision types
    VISION_TYPES = {
        "normal", "darkvision", "blindsight", "tremorsense", "truesight"
    }
    
    # Movement types
    MOVEMENT_TYPES = {
        "walk", "fly", "swim", "climb", "burrow"
    }
    
    # Content registries
    CUSTOM_CLASSES = set()
    CUSTOM_SPECIES = set()
    CUSTOM_FEATS = set()
    CUSTOM_SPELLS = set()
    CUSTOM_SKILLS = {}  # Format: {"Force Sense": "wisdom"}
    CUSTOM_WEAPON_CATEGORIES = set()
    CUSTOM_ARMOR_CATEGORIES = set()
    CUSTOM_WEAPONS = {}  # Format: {"Lightsaber": {"damage_dice": "2d6", "damage_type": "radiant"}}
    CUSTOM_ARMOR = {}    # Format: {"Force Shield": {"base_ac": 18, "dex_bonus_allowed": True}}
    CUSTOM_BACKGROUNDS = set()
    CUSTOM_SUBCLASSES = {}  # Format: {"Fighter": ["Echo Knight", "Rune Knight"]}
    CUSTOM_LINEAGES = set()
    CUSTOM_LANGUAGES = set()
    CUSTOM_PERSONALITY_TRAITS = {}  # Format: {"background": ["trait1", "trait2"]}
    CUSTOM_IDEALS = {}  # Format: {"background": ["ideal1", "ideal2"]}
    CUSTOM_BONDS = {}  # Format: {"background": ["bond1", "bond2"]}
    CUSTOM_FLAWS = {}  # Format: {"background": ["flaw1", "flaw2"]}

    # Class-specific data
    HIT_DIE_BY_CLASS = {
        "Barbarian": 12,
        "Fighter": 10, 
        "Paladin": 10,
        "Ranger": 10,
        "Monk": 8,
        "Rogue": 8,
        "Warlock": 8,
        "Bard": 8,
        "Cleric": 8,
        "Druid": 8,
        "Artificer": 8,
        "Wizard": 6,
        "Sorcerer": 6
    }
    
    CUSTOM_HIT_DIE = {}
    
    # Alignment options
    VALID_ETHICAL_ALIGNMENTS = {"Lawful", "Neutral", "Chaotic", "Other"}
    VALID_MORAL_ALIGNMENTS = {"Good", "Neutral", "Evil", "Other"}
    
    # Skills and abilities
    VALID_ABILITIES = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
    SPELLCASTING_ABILITIES = {"intelligence", "wisdom", "charisma"}
    CASTER_TYPES = {"full", "half", "third", "pact"}
    
    SKILLS = {
        "Athletics": "strength",
        "Acrobatics": "dexterity",
        "Sleight of Hand": "dexterity",
        "Stealth": "dexterity",
        "Arcana": "intelligence",
        "History": "intelligence",
        "Investigation": "intelligence",
        "Nature": "intelligence",
        "Religion": "intelligence",
        "Animal Handling": "wisdom",
        "Insight": "wisdom",
        "Medicine": "wisdom",
        "Perception": "wisdom",
        "Survival": "wisdom",
        "Deception": "charisma",
        "Intimidation": "charisma",
        "Performance": "charisma",
        "Persuasion": "charisma"
    }
    
    # Size categories
    VALID_SIZES = {"Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan", "Custom"}
    
    # Weapon and armor properties
    DAMAGE_TYPES = [
        "bludgeoning", "piercing", "slashing", "acid", "cold", "fire", 
        "force", "lightning", "necrotic", "poison", "psychic", "radiant", "thunder"
    ]
    
    # Multiclassing requirements
    MULTICLASS_REQUIREMENTS = {
        "Artificer": {"intelligence": 13},
        "Barbarian": {"strength": 13},
        "Bard": {"charisma": 13},
        "Cleric": {"wisdom": 13},
        "Druid": {"wisdom": 13},
        "Fighter": {"strength": 13, "dexterity": 13},  # Either STR or DEX
        "Monk": {"dexterity": 13, "wisdom": 13},
        "Paladin": {"strength": 13, "charisma": 13},
        "Ranger": {"dexterity": 13, "wisdom": 13},
        "Rogue": {"dexterity": 13},
        "Sorcerer": {"charisma": 13},
        "Warlock": {"charisma": 13},
        "Wizard": {"intelligence": 13}
    }
    
    CUSTOM_MULTICLASS_REQUIREMENTS = {}
    
    # Subclass levels
    SUBCLASS_LEVELS = {
        "Artificer": 3,
        "Barbarian": 3,
        "Bard": 3,
        "Cleric": 1,
        "Druid": 2,
        "Fighter": 3,
        "Monk": 3,
        "Paladin": 3,
        "Ranger": 3,
        "Rogue": 3,
        "Sorcerer": 1,
        "Warlock": 1,
        "Wizard": 2
    }
    
    CUSTOM_SUBCLASS_LEVELS = {}

    # ===== VALIDATION DECORATOR METHODS =====
    
    @classmethod
    def _is_valid_dice_format(cls, dice_str: str) -> bool:
        """Validate dice notation format like '1d6' or '2d8'."""
        return bool(re.match(r'^\d+d\d+$', dice_str))
    
    @staticmethod
    def validate_name(min_length: int = 3, allow_spaces: bool = True) -> Callable[[F], F]:
        """
        Decorator to validate names of custom content.
        
        Args:
            min_length: Minimum name length
            allow_spaces: Whether spaces are allowed in the name
        """
        def decorator(method: F) -> F:
            @wraps(method)
            def wrapper(cls, name: str, *args, **kwargs):
                if len(name) < min_length:
                    raise ValueError(f"Name '{name}' must be at least {min_length} characters")
                
                # Check for spaces if not allowed
                if not allow_spaces and ' ' in name:
                    raise ValueError(f"Name '{name}' cannot contain spaces")
                    
                # Check for invalid characters
                valid_pattern = r'^[a-zA-Z0-9\s\'\-]+$' if allow_spaces else r'^[a-zA-Z0-9\'\-]+$'
                if not re.match(valid_pattern, name):
                    raise ValueError(f"Name '{name}' contains invalid characters")
                    
                return method(cls, name, *args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    def validate_weapon(method: F) -> F:
        """Validate weapon properties."""
        @wraps(method)
        def wrapper(cls, weapon_name: str, properties: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["damage_dice", "damage_type"]
            for prop in required_props:
                if prop not in properties:
                    raise ValueError(f"Weapon '{weapon_name}' must specify {prop}")
            
            # Validate damage dice format
            if not cls._is_valid_dice_format(properties["damage_dice"]):
                raise ValueError(f"Invalid damage dice format: {properties['damage_dice']}")
            
            # Validate damage type
            if properties["damage_type"].lower() not in cls.DAMAGE_TYPES and "custom" not in properties:
                raise ValueError(f"Invalid damage type: {properties['damage_type']}")
                
            return method(cls, weapon_name, properties, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_armor(method: F) -> F:
        """Validate armor properties."""
        @wraps(method)
        def wrapper(cls, armor_name: str, properties: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["base_ac"]
            for prop in required_props:
                if prop not in properties:
                    raise ValueError(f"Armor '{armor_name}' must specify {prop}")
            
            # Validate AC is within reasonable bounds
            if not (10 <= properties["base_ac"] <= 25):
                raise ValueError(f"Armor base AC should be between 10 and 25, got {properties['base_ac']}")
                
            return method(cls, armor_name, properties, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_spell(method: F) -> F:
        """Validate spell properties."""
        @wraps(method)
        def wrapper(cls, spell_name: str, spell_details: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["level", "casting_time", "range", "duration"]
            for prop in required_props:
                if prop not in spell_details:
                    raise ValueError(f"Spell '{spell_name}' must specify {prop}")
            
            # Validate level
            if not (0 <= spell_details["level"] <= 9):
                raise ValueError(f"Spell level must be between 0 and 9, got {spell_details['level']}")
                
            return method(cls, spell_name, spell_details, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_feat(method: F) -> F:
        """Validate feat properties."""
        @wraps(method)
        def wrapper(cls, feat_name: str, feat_details: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["description"]
            for prop in required_props:
                if prop not in feat_details:
                    raise ValueError(f"Feat '{feat_name}' must specify {prop}")
            
            # Check prerequisites if present
            if "prerequisite" in feat_details:
                prereq = feat_details["prerequisite"]
                
                # If class prerequisite, validate class exists
                if "class" in prereq:
                    class_name = prereq["class"]
                    if not cls.is_valid_class(class_name):
                        raise ValueError(f"Feat '{feat_name}' requires non-existent class '{class_name}'")
                        
            return method(cls, feat_name, feat_details, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_species(method: F) -> F:
        """Validate species properties."""
        @wraps(method)
        def wrapper(cls, species_name: str, abilities: Dict[str, Any], *args, **kwargs):
            # Validate required abilities
            required_abilities = ["size", "speed"]
            for ability in required_abilities:
                if ability not in abilities:
                    raise ValueError(f"Species '{species_name}' must specify {ability}")
            
            # Validate size
            if abilities["size"] not in cls.VALID_SIZES:
                raise ValueError(f"Invalid size '{abilities['size']}' for species '{species_name}'")
                
            # Validate speed
            if not isinstance(abilities["speed"], int) or abilities["speed"] < 5 or abilities["speed"] > 80:
                raise ValueError(f"Speed must be between 5 and 80, got {abilities['speed']}")
                
            # Validate ability bonuses if present
            if "ability_bonuses" in abilities:
                bonuses = abilities["ability_bonuses"]
                                  
                for ability, bonus in bonuses.items():
                    if ability.lower() not in cls.VALID_ABILITIES:
                        raise ValueError(f"Invalid ability '{ability}' in species '{species_name}'")
                    
                    if not isinstance(bonus, int) or bonus < -4 or bonus > 4:
                        raise ValueError(f"Ability bonus must be between -4 and 4, got {bonus}")
                        
            return method(cls, species_name, abilities, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_class(method: F) -> F:
        """Validate class properties."""
        @wraps(method)
        def wrapper(cls, class_name: str, hit_die: int, *args, **kwargs):
            # Validate hit die
            if hit_die not in cls.VALID_HIT_DIE_SIZES:
                raise ValueError(f"Hit die must be one of {cls.VALID_HIT_DIE_SIZES}, got {hit_die}")
                
            # If multiclass requirements are specified
            if len(args) > 0 and args[0] is not None:
                multiclass_requirements = args[0]
                                  
                for ability, score in multiclass_requirements.items():
                    if ability.lower() not in cls.VALID_ABILITIES:
                        raise ValueError(f"Invalid ability '{ability}' in multiclass requirements")
                        
                    if not isinstance(score, int) or score < 3 or score > 20:
                        raise ValueError(f"Ability score requirement must be between 3 and 20, got {score}")
                        
            # If spellcasting ability is specified
            if len(args) > 1 and args[1] is not None:
                spellcasting_ability = args[1].lower()
                
                if spellcasting_ability not in cls.SPELLCASTING_ABILITIES:
                    raise ValueError(f"Spellcasting ability must be one of {cls.SPELLCASTING_ABILITIES}, got {spellcasting_ability}")
                    
            # If caster type is specified
            if len(args) > 2 and args[2] is not None:
                caster_type = args[2].lower()
                
                if caster_type not in cls.CASTER_TYPES:
                    raise ValueError(f"Caster type must be one of {cls.CASTER_TYPES}, got {caster_type}")
                    
            return method(cls, class_name, hit_die, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_skill(method: F) -> F:
        """Validate skill properties."""
        @wraps(method)
        def wrapper(cls, skill_name: str, ability: str, *args, **kwargs):
            # Validate ability
            if ability.lower() not in cls.VALID_ABILITIES:
                raise ValueError(f"Skill ability must be one of {cls.VALID_ABILITIES}, got {ability}")
                    
            return method(cls, skill_name, ability, *args, **kwargs)
        return wrapper

    @staticmethod
    def validate_background(method: F) -> F:
        """Validate background properties."""
        @wraps(method)
        def wrapper(cls, background_name: str, background_details: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["feature", "skill_proficiencies"]
            for prop in required_props:
                if prop not in background_details:
                    raise ValueError(f"Background '{background_name}' must specify {prop}")
            
            # Validate skill proficiencies
            skill_profs = background_details.get("skill_proficiencies", [])
            if not isinstance(skill_profs, list) or len(skill_profs) > 4:
                raise ValueError(f"Background should provide at most 4 skill proficiencies")
                
            for skill in skill_profs:
                if skill not in cls.SKILLS and skill not in cls.CUSTOM_SKILLS:
                    raise ValueError(f"Invalid skill '{skill}' in background '{background_name}'")
                    
            return method(cls, background_name, background_details, *args, **kwargs)
        return wrapper

    @staticmethod
    def validate_lineage(method: F) -> F:
        """Validate lineage properties."""
        @wraps(method)
        def wrapper(cls, lineage_name: str, lineage_details: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["parent_species", "traits"]
            for prop in required_props:
                if prop not in lineage_details:
                    raise ValueError(f"Lineage '{lineage_name}' must specify {prop}")
            
            # Validate parent species
            parent_species = lineage_details["parent_species"]
            if not isinstance(parent_species, list):
                parent_species = [parent_species]
                
            for species in parent_species:
                if not cls.is_valid_species(species):
                    raise ValueError(f"Lineage '{lineage_name}' references invalid species '{species}'")
                    
            return method(cls, lineage_name, lineage_details, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_subclass(method: F) -> F:
        """Validate subclass properties."""
        @wraps(method)
        def wrapper(cls, class_name: str, subclass_name: str, subclass_details: Dict[str, Any], *args, **kwargs):
            # Validate class exists
            if not cls.is_valid_class(class_name):
                raise ValueError(f"Parent class '{class_name}' does not exist")
            
            # Validate required properties
            required_props = ["description", "features"]
            for prop in required_props:
                if prop not in subclass_details:
                    raise ValueError(f"Subclass '{subclass_name}' must specify {prop}")
                    
            # Validate features
            features = subclass_details.get("features", {})
            if not isinstance(features, dict):
                raise ValueError(f"Subclass features must be a dictionary mapping levels to feature lists")
                
            return method(cls, class_name, subclass_name, subclass_details, *args, **kwargs)
        return wrapper
        
    @staticmethod
    def validate_language(method: F) -> F:
        """Validate language properties."""
        @wraps(method)
        def wrapper(cls, language_name: str, language_details: Dict[str, Any], *args, **kwargs):
            # Validate required properties
            required_props = ["script", "typical_speakers"]
            for prop in required_props:
                if prop not in language_details:
                    raise ValueError(f"Language '{language_name}' must specify {prop}")
                    
            return method(cls, language_name, language_details, *args, **kwargs)
        return wrapper
        
    @staticmethod
    def validate_personality_element(method: F) -> F:
        """Validate personality element properties (traits, ideals, bonds, flaws)."""
        @wraps(method)
        def wrapper(cls, element_type: str, background: str, elements: List[str], *args, **kwargs):
            # Validate background exists
            if not cls.is_valid_background(background):
                raise ValueError(f"Background '{background}' does not exist")
            
            # Validate elements
            if not isinstance(elements, list) or not elements:
                raise ValueError(f"{element_type} must be a non-empty list of strings")
                
            for element in elements:
                if not isinstance(element, str) or len(element) < 3:
                    raise ValueError(f"{element_type} must be meaningful strings")
                    
            return method(cls, element_type, background, elements, *args, **kwargs)
        return wrapper
    
    @staticmethod
    def validate_alignment(method: F) -> F:
        """Validate alignment."""
        @wraps(method)
        def wrapper(cls, ethical: str, moral: str, *args, **kwargs):
            # Validate ethical alignment
            if ethical not in cls.VALID_ETHICAL_ALIGNMENTS:
                raise ValueError(f"Invalid ethical alignment '{ethical}'. Must be one of {cls.VALID_ETHICAL_ALIGNMENTS}")
                
            # Validate moral alignment
            if moral not in cls.VALID_MORAL_ALIGNMENTS:
                raise ValueError(f"Invalid moral alignment '{moral}'. Must be one of {cls.VALID_MORAL_ALIGNMENTS}")
                
            return method(cls, ethical, moral, *args, **kwargs)
        return wrapper

    # ===== UTILITY DECORATORS =====
    
    @staticmethod
    def log_registration(method: F) -> F:
        """Log registration of custom content."""
        @wraps(method)
        def wrapper(cls, name: str, *args, **kwargs):
            result = method(cls, name, *args, **kwargs)
            content_type = method.__name__.replace('register_custom_', '')
            logger.info(f"Registered {content_type.title()}: {name}")
            return result
        return wrapper
    
    @staticmethod
    def check_duplicates(method: F) -> F:
        """Check if custom content already exists."""
        @wraps(method)
        def wrapper(cls, name: str, *args, **kwargs):
            # Determine content type from method name
            content_type = method.__name__.replace('register_custom_', '')
            
            # Get appropriate collection based on content type
            if content_type == 'class':
                if name in cls.BASE_CLASSES or name in cls.CUSTOM_CLASSES:
                    raise ValueError(f"Class '{name}' already exists")
            elif content_type == 'species':
                if name in cls.CUSTOM_SPECIES:
                    raise ValueError(f"Species '{name}' already exists")
            elif content_type == 'feat':
                if name in cls.CUSTOM_FEATS:
                    raise ValueError(f"Feat '{name}' already exists")
            elif content_type == 'spell':
                if name in cls.CUSTOM_SPELLS:
                    raise ValueError(f"Spell '{name}' already exists")
            elif content_type == 'skill':
                if name in cls.SKILLS or name in cls.CUSTOM_SKILLS:
                    raise ValueError(f"Skill '{name}' already exists")
            elif content_type == 'weapon':
                if name in cls.CUSTOM_WEAPONS:
                    raise ValueError(f"Weapon '{name}' already exists")
            elif content_type == 'armor':
                if name in cls.CUSTOM_ARMOR:
                    raise ValueError(f"Armor '{name}' already exists")
            elif content_type == 'weapon_category':
                if name in cls.CUSTOM_WEAPON_CATEGORIES:
                    raise ValueError(f"Weapon category '{name}' already exists")
            elif content_type == 'armor_category':
                if name in cls.CUSTOM_ARMOR_CATEGORIES:
                    raise ValueError(f"Armor category '{name}' already exists")
            elif content_type == 'background':
                if name in cls.BASE_BACKGROUNDS or name in cls.CUSTOM_BACKGROUNDS:
                    raise ValueError(f"Background '{name}' already exists")
            elif content_type == 'lineage':
                if name in cls.BASE_LINEAGES or name in cls.CUSTOM_LINEAGES:
                    raise ValueError(f"Lineage '{name}' already exists")
            elif content_type == 'language':
                if name in cls.BASE_LANGUAGES or name in cls.CUSTOM_LANGUAGES:
                    raise ValueError(f"Language '{name}' already exists")
            elif content_type == 'subclass':
                class_name = args[0]
                if class_name in cls.CUSTOM_SUBCLASSES and name in cls.CUSTOM_SUBCLASSES[class_name]:
                    raise ValueError(f"Subclass '{name}' for class '{class_name}' already exists")
                    
            return method(cls, name, *args, **kwargs)
        return wrapper

    # ===== REGISTRATION METHODS =====
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_class
    def register_custom_class(cls, class_name: str, hit_die: int, 
                          multiclass_requirements: Optional[Dict[str, int]] = None,
                          spellcasting_ability: Optional[str] = None,
                          caster_type: Optional[str] = None,
                          subclass_level: Optional[int] = 3) -> bool:
        """
        Register a custom character class.
        
        Args:
            class_name: Name of the custom class (e.g. "Jedi Mind Warrior")
            hit_die: Hit die size (e.g. 8 for d8, 10 for d10)
            multiclass_requirements: Dictionary of ability score requirements
            spellcasting_ability: Primary ability for spellcasting
            caster_type: "full", "half", "third", or "pact"
            subclass_level: Level at which this class gets its subclass
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_CLASSES.add(class_name)
        cls.CUSTOM_HIT_DIE[class_name] = hit_die
        cls.CUSTOM_SUBCLASS_LEVELS[class_name] = subclass_level
        
        if multiclass_requirements:
            cls.CUSTOM_MULTICLASS_REQUIREMENTS[class_name] = multiclass_requirements
        
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_species
    def register_custom_species(cls, species_name: str, abilities: Dict[str, Any]) -> bool:
        """
        Register a custom species.
        
        Args:
            species_name: Name of the custom species
            abilities: Dictionary of species traits and abilities
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_SPECIES.add(species_name)
        # In a full implementation, you'd store more details about the species
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_feat
    def register_custom_feat(cls, feat_name: str, feat_details: Dict[str, Any]) -> bool:
        """
        Register a custom feat.
        
        Args:
            feat_name: Name of the custom feat (e.g. "Force Push")
            feat_details: Dictionary with feat details
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_FEATS.add(feat_name)
        # In a full implementation, you'd store the feat details
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_spell
    def register_custom_spell(cls, spell_name: str, spell_details: Dict[str, Any]) -> bool:
        """
        Register a custom spell.
        
        Args:
            spell_name: Name of the custom spell (e.g. "Force Lightning")
            spell_details: Dictionary with spell details
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_SPELLS.add(spell_name)
        # In a full implementation, you'd store the spell details
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_skill
    def register_custom_skill(cls, skill_name: str, ability: str) -> bool:
        """
        Register a custom skill and its ability.
        
        Args:
            skill_name: Name of the skill (e.g. "Force Attunement")
            ability: Ability the skill is based on
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_SKILLS[skill_name] = ability.lower()
        return True

    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_background
    def register_custom_background(cls, background_name: str, background_details: Dict[str, Any]) -> bool:
        """
        Register a custom background.
        
        Args:
            background_name: Name of the background
            background_details: Dictionary with background details
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_BACKGROUNDS.add(background_name)
        return True
        
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_lineage
    def register_custom_lineage(cls, lineage_name: str, lineage_details: Dict[str, Any]) -> bool:
        """
        Register a custom lineage.
        
        Args:
            lineage_name: Name of the lineage
            lineage_details: Dictionary with lineage details
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_LINEAGES.add(lineage_name)
        return True
        
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_subclass
    def register_custom_subclass(cls, class_name: str, subclass_name: str, subclass_details: Dict[str, Any]) -> bool:
        """
        Register a custom subclass for an existing class.
        
        Args:
            class_name: Name of the parent class
            subclass_name: Name of the subclass
            subclass_details: Dictionary with subclass details
            
        Returns:
            bool: True if registered successfully
        """
        if class_name not in cls.CUSTOM_SUBCLASSES:
            cls.CUSTOM_SUBCLASSES[class_name] = []
            
        cls.CUSTOM_SUBCLASSES[class_name].append(subclass_name)
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_language
    def register_custom_language(cls, language_name: str, language_details: Dict[str, Any]) -> bool:
        """
        Register a custom language.
        
        Args:
            language_name: Name of the language
            language_details: Dictionary with language details
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_LANGUAGES.add(language_name)
        return True
        
    @classmethod
    @log_registration
    @validate_personality_element
    def register_custom_personality_traits(cls, background: str, traits: List[str]) -> bool:
        """
        Register custom personality traits for a background.
        
        Args:
            background: Name of the background
            traits: List of personality trait strings
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_PERSONALITY_TRAITS[background] = traits
        return True
        
    @classmethod
    @log_registration
    @validate_personality_element
    def register_custom_ideals(cls, background: str, ideals: List[str]) -> bool:
        """
        Register custom ideals for a background.
        
        Args:
            background: Name of the background
            ideals: List of ideal strings
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_IDEALS[background] = ideals
        return True
        
    @classmethod
    @log_registration
    @validate_personality_element
    def register_custom_bonds(cls, background: str, bonds: List[str]) -> bool:
        """
        Register custom bonds for a background.
        
        Args:
            background: Name of the background
            bonds: List of bond strings
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_BONDS[background] = bonds
        return True
        
    @classmethod
    @log_registration
    @validate_personality_element
    def register_custom_flaws(cls, background: str, flaws: List[str]) -> bool:
        """
        Register custom flaws for a background.
        
        Args:
            background: Name of the background
            flaws: List of flaw strings
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_FLAWS[background] = flaws
        return True
    
    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    def register_custom_weapon_category(cls, category_name: str) -> bool:
        """
        Register a custom weapon category.
        
        Args:
            category_name: Name of the custom weapon category
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_WEAPON_CATEGORIES.add(category_name)
        return True

    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    def register_custom_armor_category(cls, category_name: str) -> bool:
        """
        Register a custom armor category.
        
        Args:
            category_name: Name of the custom armor category
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_ARMOR_CATEGORIES.add(category_name)
        return True

    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_weapon
    def register_custom_weapon(cls, weapon_name: str, properties: Dict[str, Any]) -> bool:
        """
        Register a custom weapon with validation.
        
        Args:
            weapon_name: Name of the custom weapon (e.g. "Lightsaber")
            properties: Dictionary with weapon properties including:
                - damage_dice: Dice notation (e.g. "1d8")
                - damage_type: Type of damage
                - properties: List of weapon properties
                - category: Weapon category
                - weight: Weight in pounds
                - cost: Cost in gold pieces
                
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_WEAPONS[weapon_name] = properties
        
        # If a new weapon category is specified, register it too
        if "category" in properties and properties["category"] not in cls.CUSTOM_WEAPON_CATEGORIES:
            cls.register_custom_weapon_category(properties["category"])
            
        return True

    @classmethod
    @log_registration
    @check_duplicates
    @validate_name()
    @validate_armor
    def register_custom_armor(cls, armor_name: str, properties: Dict[str, Any]) -> bool:
        """
        Register a custom armor with validation.
        
        Args:
            armor_name: Name of the custom armor (e.g. "Force Shield")
            properties: Dictionary with armor properties including:
                - base_ac: Base armor class
                - dex_bonus_allowed: Whether DEX modifier can be added
                - max_dex_bonus: Maximum DEX bonus allowed (None for unlimited)
                - category: Armor category
                - strength_required: Minimum STR score to avoid speed reduction
                - stealth_disadvantage: Whether armor gives disadvantage on stealth
                
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_ARMOR[armor_name] = properties
        
        # If a new armor category is specified, register it too
        if "category" in properties and properties["category"] not in cls.CUSTOM_ARMOR_CATEGORIES:
            cls.register_custom_armor_category(properties["category"])
            
        return True

    # ===== VALIDATION AND UTILITY METHODS =====
    
    @classmethod
    def is_valid_ability_score(cls, value: int, allow_exceptional: bool = False) -> bool:
        """
        Check if an ability score is within valid range.
        
        Args:
            value: Ability score to check
            allow_exceptional: If True, allows scores up to 30 for special beings
            
        Returns:
            bool: True if valid
        """
        if allow_exceptional:
            return cls.ABILITY_SCORE_MIN <= value <= cls.ABILITY_SCORE_MAX
        return cls.ABILITY_SCORE_MIN <= value <= 20
    
    @classmethod
    def is_valid_class(cls, class_name: str) -> bool:
        """Check if a class name is valid (includes custom classes)."""
        return class_name in cls.BASE_CLASSES or class_name in cls.CUSTOM_CLASSES
    
    @classmethod
    def is_valid_subclass(cls, class_name: str, subclass_name: str) -> bool:
        """Check if a subclass name is valid for the given class."""
        # Would need access to a database of official subclasses
        # For now, just check custom subclasses
        return class_name in cls.CUSTOM_SUBCLASSES and subclass_name in cls.CUSTOM_SUBCLASSES[class_name]
    
    @classmethod
    def is_valid_background(cls, background_name: str) -> bool:
        """Check if a background name is valid."""
        return background_name in cls.BASE_BACKGROUNDS or background_name in cls.CUSTOM_BACKGROUNDS
    
    @classmethod
    def is_valid_lineage(cls, lineage_name: str) -> bool:
        """Check if a lineage name is valid."""
        return lineage_name in cls.BASE_LINEAGES or lineage_name in cls.CUSTOM_LINEAGES
    
    @classmethod
    def is_valid_species(cls, species_name: str) -> bool:
        """Check if a species name is valid."""
        return species_name in cls.BASE_LINEAGES or species_name in cls.CUSTOM_SPECIES
    
    @classmethod
    def is_valid_skill(cls, skill_name: str) -> bool:
        """Check if a skill name is valid (includes custom skills)."""
        return skill_name in cls.SKILLS or skill_name in cls.CUSTOM_SKILLS
    
    @classmethod
    def is_valid_language(cls, language_name: str) -> bool:
        """Check if a language name is valid."""
        return language_name in cls.BASE_LANGUAGES or language_name in cls.CUSTOM_LANGUAGES
    
    @classmethod
    def is_valid_alignment(cls, ethical: str, moral: str) -> bool:
        """Check if an alignment combination is valid."""
        return ethical in cls.VALID_ETHICAL_ALIGNMENTS and moral in cls.VALID_MORAL_ALIGNMENTS
    
    @classmethod
    def is_valid_vision_type(cls, vision_type: str) -> bool:
        """Check if a vision type is valid."""
        return vision_type.lower() in cls.VISION_TYPES
    
    @classmethod
    def is_valid_movement_type(cls, movement_type: str) -> bool:
        """Check if a movement type is valid."""
        return movement_type.lower() in cls.MOVEMENT_TYPES
    
    @classmethod
    def get_ability_for_skill(cls, skill_name: str) -> Optional[str]:
        """Get the ability associated with a skill."""
        return cls.SKILLS.get(skill_name) or cls.CUSTOM_SKILLS.get(skill_name)
    
    @classmethod
    def get_personality_traits(cls, background: str) -> List[str]:
        """Get personality traits for a background."""
        # In a full implementation, this would include official traits from the rulebooks
        return cls.CUSTOM_PERSONALITY_TRAITS.get(background, [])
    
    @classmethod
    def get_ideals(cls, background: str) -> List[str]:
        """Get ideals for a background."""
        # In a full implementation, this would include official ideals from the rulebooks
        return cls.CUSTOM_IDEALS.get(background, [])
    
    @classmethod
    def get_bonds(cls, background: str) -> List[str]:
        """Get bonds for a background."""
        # In a full implementation, this would include official bonds from the rulebooks
        return cls.CUSTOM_BONDS.get(background, [])
    
    @classmethod
    def get_flaws(cls, background: str) -> List[str]:
        """Get flaws for a background."""
        # In a full implementation, this would include official flaws from the rulebooks
        return cls.CUSTOM_FLAWS.get(background, [])
    
    @classmethod
    def can_multiclass_into(cls, new_class: str, ability_scores: Dict[str, int], 
                         ignore_requirements: bool = False) -> Tuple[bool, str]:
        """
        Check if a character meets multiclass requirements.
        
        Args:
            new_class: Class to check for multiclassing
            ability_scores: Character's ability scores
            ignore_requirements: If True, bypasses standard requirements
            
        Returns:
            Tuple[bool, str]: (Success, message)
        """
        if ignore_requirements:
            return True, f"Requirements ignored for {new_class}"
            
        # Handle custom classes first
        if new_class in cls.CUSTOM_CLASSES:
            requirements = cls.CUSTOM_MULTICLASS_REQUIREMENTS.get(new_class, {})
            if not requirements:  # No requirements defined
                return True, f"No requirements for custom class {new_class}"
        elif not cls.is_valid_class(new_class):
            return False, f"Invalid class: {new_class}"
        else:
            requirements = cls.MULTICLASS_REQUIREMENTS.get(new_class, {})
            
        # Check requirements
        for ability, min_score in requirements.items():
            if ability_scores.get(ability, 0) < min_score:
                return False, f"Requires {ability} {min_score}+ to multiclass into {new_class}"
                
        return True, f"Can multiclass into {new_class}"
    
    @classmethod
    def get_hit_die_size(cls, class_name: str) -> int:
        """Get hit die size for a class, including custom classes."""
        if class_name in cls.CUSTOM_HIT_DIE:
            return cls.CUSTOM_HIT_DIE[class_name]
        return cls.HIT_DIE_BY_CLASS.get(class_name, 8)  # Default to d8
    
    @classmethod
    def get_subclass_level(cls, class_name: str) -> int:
        """Get the level at which a class gains its subclass."""
        if class_name in cls.CUSTOM_SUBCLASS_LEVELS:
            return cls.CUSTOM_SUBCLASS_LEVELS[class_name]
        return cls.SUBCLASS_LEVELS.get(class_name, 3)  # Default to level 3
    
    @classmethod
    def get_background_feature(cls, background_name: str) -> Optional[str]:
        """Get the feature for a background."""
        # Would need access to a database of background features
        # Just a placeholder implementation
        return None
    
    @classmethod
    def get_multiclass_spellcaster_level(cls, class_levels: Dict[str, int], 
                                       custom_caster_types: Optional[Dict[str, str]] = None) -> int:
        """
        Calculate multiclass spellcaster level for spell slots.
        
        Args:
            class_levels: Dictionary mapping class names to levels
            custom_caster_types: Dictionary mapping custom classes to caster types
                                ("full", "half", "third", or "pact")
            
        Returns:
            int: Effective spellcaster level for determining spell slots
        """
        full_caster_levels = 0
        half_caster_levels = 0
        third_caster_levels = 0
        
        custom_caster_types = custom_caster_types or {}
        
        for class_name, level in class_levels.items():
            # Handle standard classes
            if class_name in {"Bard", "Cleric", "Druid", "Sorcerer", "Wizard"}:
                full_caster_levels += level
            elif class_name in {"Paladin", "Ranger"}:
                half_caster_levels += level
            elif class_name == "Artificer":
                # Artificer rounds up
                half_caster_levels += (level + 1) // 2  # This rounds up
            # Handle custom classes based on provided caster types
            elif class_name in custom_caster_types:
                caster_type = custom_caster_types[class_name]
                if caster_type == "full":
                    full_caster_levels += level
                elif caster_type == "half":
                    half_caster_levels += level
                elif caster_type == "third":
                    third_caster_levels += level
                # "pact" is handled separately for warlocks
        
        # Calculate total caster level
        return (full_caster_levels + 
                (half_caster_levels // 2) + 
                (third_caster_levels // 3))

    # ===== CHARACTER SHEET VALIDATION METHODS =====
    
    @classmethod
    def validate_character_name(cls, name: str) -> Tuple[bool, str]:
        """Validate a character name."""
        if not name or len(name) < 2:
            return False, "Character name must be at least 2 characters long"
        return True, "Valid character name"
        
    @classmethod
    def validate_character_species(cls, species: str) -> Tuple[bool, str]:
        """Validate a character's species."""
        if species in cls.BASE_LINEAGES or species in cls.CUSTOM_SPECIES:
            return True, "Valid species"
        return False, f"Invalid species: {species}"
        
    @classmethod
    def validate_character_lineage(cls, lineage: Optional[str]) -> Tuple[bool, str]:
        """Validate a character's lineage."""
        if lineage is None:
            return True, "No lineage selected"
        
        if lineage in cls.BASE_LINEAGES or lineage in cls.CUSTOM_LINEAGES:
            return True, "Valid lineage"
        return False, f"Invalid lineage: {lineage}"
        
    @classmethod
    def validate_character_classes(cls, classes: Dict[str, int]) -> Tuple[bool, str]:
        """Validate a character's classes and levels."""
        if not classes:
            return False, "Character must have at least one class"
            
        total_level = sum(classes.values())
        if total_level < cls.MIN_LEVEL or total_level > cls.MAX_LEVEL:
            return False, f"Total character level must be between {cls.MIN_LEVEL} and {cls.MAX_LEVEL}"
            
        for class_name, level in classes.items():
            if not cls.is_valid_class(class_name):
                return False, f"Invalid class: {class_name}"
            if level < 1 or level > cls.MAX_LEVEL:
                return False, f"Invalid level for {class_name}: {level}"
                
        return True, "Valid classes and levels"
        
    @classmethod
    def validate_character_subclasses(cls, classes: Dict[str, int], subclasses: Dict[str, str]) -> Tuple[bool, str]:
        """Validate a character's subclasses."""
        for class_name, subclass in subclasses.items():
            # Check if the character has this class
            if class_name not in classes:
                return False, f"Character doesn't have the {class_name} class for subclass {subclass}"
            
            # Check if the level is high enough for a subclass
            required_level = cls.get_subclass_level(class_name)
            if classes[class_name] < required_level:
                return False, f"Character's {class_name} level ({classes[class_name]}) is too low for subclass {subclass}, needs level {required_level}"
                
        return True, "Valid subclasses"
        
    @classmethod
    def validate_character_background(cls, background: str) -> Tuple[bool, str]:
        """Validate a character's background."""
        if cls.is_valid_background(background):
            return True, "Valid background"
        return False, f"Invalid background: {background}"
        
    @classmethod
    def validate_character_alignment(cls, ethical: str, moral: str) -> Tuple[bool, str]:
        """Validate a character's alignment."""
        if cls.is_valid_alignment(ethical, moral):
            return True, "Valid alignment"
        return False, f"Invalid alignment: {ethical} {moral}"
        
    @classmethod
    def validate_character_ability_scores(cls, ability_scores: Dict[str, int], allow_exceptional: bool = False) -> Tuple[bool, str]:
        """Validate a character's ability scores."""
        for ability, score in ability_scores.items():
            if ability.lower() not in cls.VALID_ABILITIES:
                return False, f"Invalid ability: {ability}"
                
            if not cls.is_valid_ability_score(score, allow_exceptional):
                max_score = cls.ABILITY_SCORE_MAX if allow_exceptional else 20
                return False, f"Invalid score for {ability}: {score} (must be between {cls.ABILITY_SCORE_MIN} and {max_score})"
                
        return True, "Valid ability scores"
        
    @classmethod
    def validate_character_skill_proficiencies(cls, skill_proficiencies: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a character's skill proficiencies."""
        for skill_name in skill_proficiencies:
            if not cls.is_valid_skill(skill_name):
                return False, f"Invalid skill: {skill_name}"
                
        return True, "Valid skill proficiencies"
        
    @classmethod
    def validate_character_saving_throws(cls, saving_throws: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate a character's saving throw proficiencies."""
        for ability in saving_throws:
            if ability.lower() not in cls.VALID_ABILITIES:
                return False, f"Invalid ability for saving throw: {ability}"
                
        return True, "Valid saving throw proficiencies"
        
    @classmethod
    def validate_character_languages(cls, languages: Set[str]) -> Tuple[bool, str]:
        """Validate a character's languages."""
        for language in languages:
            if not cls.is_valid_language(language):
                return False, f"Invalid language: {language}"
                
        return True, "Valid languages"
        
    @classmethod
    def validate_character_feats(cls, feats: List[str]) -> Tuple[bool, str]:
        """Validate a character's feats."""
        # Would need a comprehensive list of official feats
        # For custom feats, we can check:
        for feat in feats:
            if feat in cls.CUSTOM_FEATS:
                continue
            # Otherwise, assume it's an official feat for now
        
        return True, "Assuming all feats are valid (comprehensive validation would require a complete feat database)"
    
    @classmethod
    def validate_character_vision_types(cls, vision_types: Dict[str, int]) -> Tuple[bool, str]:
        """Validate a character's vision types."""
        for vision_type in vision_types:
            if not cls.is_valid_vision_type(vision_type):
                return False, f"Invalid vision type: {vision_type}"
                
        return True, "Valid vision types"
        
    @classmethod
    def validate_character_movement_types(cls, movement_types: Dict[str, int]) -> Tuple[bool, str]:
        """Validate a character's movement types."""
        for movement_type in movement_types:
            if not cls.is_valid_movement_type(movement_type):
                return False, f"Invalid movement type: {movement_type}"
                
        return True, "Valid movement types"

    @classmethod
    def validate_character_spellcasting(cls, spellcasting_ability: Optional[str], spellcasting_classes: Dict[str, Dict[str, Any]]) -> Tuple[bool, str]:
        """Validate a character's spellcasting attributes."""
        if spellcasting_ability and spellcasting_ability.lower() not in cls.SPELLCASTING_ABILITIES:
            return False, f"Invalid spellcasting ability: {spellcasting_ability}"
            
        for class_name in spellcasting_classes:
            if not cls.is_valid_class(class_name):
                return False, f"Invalid spellcasting class: {class_name}"
                
        return True, "Valid spellcasting attributes"
        
    @classmethod
    def validate_character_hit_dice(cls, hit_dice: Dict[str, int], classes: Dict[str, int]) -> Tuple[bool, str]:
        """Validate a character's hit dice against their classes."""
        expected_hit_dice = {}
        
        for class_name, level in classes.items():
            hit_die_size = cls.get_hit_die_size(class_name)
            die_type = f"d{hit_die_size}"
            
            if die_type not in expected_hit_dice:
                expected_hit_dice[die_type] = 0
            expected_hit_dice[die_type] += level
            
        # Check if hit_dice matches expected_hit_dice
        if hit_dice != expected_hit_dice:
            return False, f"Hit dice don't match character classes. Expected: {expected_hit_dice}, Got: {hit_dice}"
            
        return True, "Valid hit dice"
        
####

@classmethod
def validate_character_appearance(cls, appearance: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a character's appearance attributes."""
    # Validate height and weight as reasonable values
    if "height" in appearance and appearance["height"] and not isinstance(appearance["height"], str):
        return False, f"Height must be a string value"
        
    if "weight" in appearance and appearance["weight"] and not isinstance(appearance["weight"], str):
        return False, f"Weight must be a string value"
        
    # Validate age within reasonable bounds
    if "age" in appearance and appearance["age"]:
        try:
            age = int(appearance["age"])
            if age < 0 or age > 1000:  # Allow for long-lived fantasy species
                return False, f"Age must be between 0 and 1000, got {age}"
        except (ValueError, TypeError):
            return False, "Age must be a number"
            
    # Validate size
    if "size" in appearance and appearance["size"] and appearance["size"] not in cls.VALID_SIZES:
        return False, f"Invalid size: {appearance['size']}"
        
    return True, "Valid appearance attributes"

@classmethod
def validate_character_species_variants(cls, species: str, variants: List[str]) -> Tuple[bool, str]:
    """Validate a character's species variants."""
    # This would check against a database of valid variants for each species
    # For now, just ensure it's a list of strings
    if not isinstance(variants, list):
        return False, "Species variants must be a list"
        
    for variant in variants:
        if not isinstance(variant, str) or not variant:
            return False, "Species variants must be non-empty strings"
            
    return True, "Valid species variants"

@classmethod
def validate_character_species_traits(cls, species_traits: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a character's species traits."""
    # Simple validation of structure
    if not isinstance(species_traits, dict):
        return False, "Species traits must be a dictionary"
        
    # In a full implementation, you would check against known species traits
    return True, "Species traits structure is valid"

@classmethod
def validate_character_class_features(cls, class_features: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a character's class features."""
    if not isinstance(class_features, dict):
        return False, "Class features must be a dictionary"
        
    # In a full implementation, you would check against known class features
    return True, "Class features structure is valid"

@classmethod
def validate_character_background_feature(cls, background: str, feature: str) -> Tuple[bool, str]:
    """Validate a character's background feature."""
    if not cls.is_valid_background(background):
        return False, f"Invalid background: {background}"
        
    # In a full implementation, check if this feature belongs to this background
    return True, "Valid background feature"

@classmethod
def validate_character_weapon_proficiencies(cls, weapon_proficiencies: Set[str]) -> Tuple[bool, str]:
    """Validate a character's weapon proficiencies."""
    if not isinstance(weapon_proficiencies, set):
        return False, "Weapon proficiencies must be a set of strings"
        
    # In a full implementation, check against known weapon categories
    return True, "Valid weapon proficiencies"

@classmethod
def validate_character_armor_proficiencies(cls, armor_proficiencies: Set[str]) -> Tuple[bool, str]:
    """Validate a character's armor proficiencies."""
    if not isinstance(armor_proficiencies, set):
        return False, "Armor proficiencies must be a set of strings"
        
    # Check known armor categories
    valid_categories = {"light armor", "medium armor", "heavy armor", "shields"}
    valid_categories.update(cls.CUSTOM_ARMOR_CATEGORIES)
    
    for proficiency in armor_proficiencies:
        if proficiency.lower() not in valid_categories and not proficiency.lower().startswith("custom:"):
            return False, f"Unknown armor proficiency: {proficiency}"
            
    return True, "Valid armor proficiencies"

@classmethod
def validate_character_tool_proficiencies(cls, tool_proficiencies: Dict[str, Any]) -> Tuple[bool, str]:
    """Validate a character's tool proficiencies."""
    if not isinstance(tool_proficiencies, dict):
        return False, "Tool proficiencies must be a dictionary"
        
    # In a full implementation, check against known tools
    return True, "Valid tool proficiencies"

@classmethod
def validate_character_armor(cls, armor: Optional[str]) -> Tuple[bool, str]:
    """Validate a character's armor."""
    if armor is None:
        return True, "No armor equipped"
        
    # Check if it's a known armor type
    # This would require a database of armors
    return True, "Armor validity check would require a database"

@classmethod
def validate_character_weapons(cls, weapons: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate a character's weapons."""
    if not isinstance(weapons, list):
        return False, "Weapons must be a list"
        
    for weapon in weapons:
        if not isinstance(weapon, dict):
            return False, "Each weapon must be a dictionary"
            
        # Check required fields
        if "name" not in weapon:
            return False, "Weapon must have a name"
            
    return True, "Valid weapons structure"

@classmethod
def validate_character_equipment(cls, equipment: List[Dict[str, Any]]) -> Tuple[bool, str]:
    """Validate a character's equipment."""
    if not isinstance(equipment, list):
        return False, "Equipment must be a list"
        
    return True, "Valid equipment structure"

@classmethod
def validate_character_currency(cls, currency: Dict[str, int]) -> Tuple[bool, str]:
    """Validate a character's currency."""
    required_currencies = {"copper", "silver", "electrum", "gold", "platinum"}
    
    if not isinstance(currency, dict):
        return False, "Currency must be a dictionary"
        
    for curr_type, amount in currency.items():
        if curr_type not in required_currencies and not curr_type.startswith("custom_"):
            return False, f"Unknown currency type: {curr_type}"
            
        if not isinstance(amount, int) or amount < 0:
            return False, f"Currency amount must be a non-negative integer, got {amount} for {curr_type}"
            
    return True, "Valid currency"

@classmethod
def validate_character_spells_known(cls, spells_known: Dict[int, List[str]]) -> Tuple[bool, str]:
    """Validate a character's known spells."""
    if not isinstance(spells_known, dict):
        return False, "Spells known must be a dictionary mapping spell levels to spell lists"
        
    for level, spells in spells_known.items():
        if not isinstance(level, int) or level < 0 or level > 9:
            return False, f"Invalid spell level: {level}"
            
        if not isinstance(spells, list):
            return False, f"Spells for level {level} must be a list"
            
    return True, "Valid spells known structure"

@classmethod
def validate_character_spells_prepared(cls, spells_prepared: List[str]) -> Tuple[bool, str]:
    """Validate a character's prepared spells."""
    if not isinstance(spells_prepared, list):
        return False, "Prepared spells must be a list"
        
    # In a full implementation, check against known spells
    return True, "Valid prepared spells structure"

@classmethod
def validate_character_personality_traits(cls, background: str, traits: List[str]) -> Tuple[bool, str]:
    """Validate a character's personality traits."""
    if not cls.is_valid_background(background):
        return False, f"Invalid background: {background}"
        
    if not isinstance(traits, list):
        return False, "Personality traits must be a list"
        
    return True, "Valid personality traits"

@classmethod
def validate_character_ideals(cls, background: str, ideals: List[str]) -> Tuple[bool, str]:
    """Validate a character's ideals."""
    if not cls.is_valid_background(background):
        return False, f"Invalid background: {background}"
        
    if not isinstance(ideals, list):
        return False, "Ideals must be a list"
        
    return True, "Valid ideals"

@classmethod
def validate_character_bonds(cls, background: str, bonds: List[str]) -> Tuple[bool, str]:
    """Validate a character's bonds."""
    if not cls.is_valid_background(background):
        return False, f"Invalid background: {background}"
        
    if not isinstance(bonds, list):
        return False, "Bonds must be a list"
        
    return True, "Valid bonds"

@classmethod
def validate_character_flaws(cls, background: str, flaws: List[str]) -> Tuple[bool, str]:
    """Validate a character's flaws."""
    if not cls.is_valid_background(background):
        return False, f"Invalid background: {background}"
        
    if not isinstance(flaws, list):
        return False, "Flaws must be a list"
        
    return True, "Valid flaws"

@classmethod
def validate_character_backstory(cls, backstory: str) -> Tuple[bool, str]:
    """Validate a character's backstory."""
    # Minimal validation - just check it's a string with some content
    if not isinstance(backstory, str):
        return False, "Backstory must be a string"
        
    # Optional: Check for minimum meaningful length
    # if len(backstory.strip()) < 10:
    #     return False, "Backstory should have meaningful content"
        
    return True, "Valid backstory"

@classmethod
def validate_character_base_speed(cls, speed: int) -> Tuple[bool, str]:
    """Validate a character's base speed."""
    if not isinstance(speed, int):
        return False, "Base speed must be an integer"
        
    if speed < 0 or speed > 120:  # Upper bound for even the fastest creatures
        return False, f"Base speed should be between 0 and 120, got {speed}"
        
    return True, "Valid base speed"

@classmethod 
def validate_entire_character_sheet(cls, character_sheet) -> List[Tuple[bool, str]]:
    """
    Validate an entire character sheet against all rules.
    
    Args:
        character_sheet: A CharacterSheet object
        
    Returns:
        List[Tuple[bool, str]]: List of validation results with messages
    """
    results = []
    
    # Validate name
    results.append(cls.validate_character_name(character_sheet.get_name()))
    
    # Validate species and variants
    species = character_sheet.get_species()
    results.append(cls.validate_character_species(species))
    results.append(cls.validate_character_species_variants(species, character_sheet.get_species_variants()))
    
    # Validate lineage
    results.append(cls.validate_character_lineage(character_sheet.get_lineage()))
    
    # Validate classes and features
    class_levels = character_sheet.get_class_levels()
    results.append(cls.validate_character_classes(class_levels))
    results.append(cls.validate_character_class_features(character_sheet.get_class_features()))
    
    # Validate subclasses
    subclasses = {}
    for class_name in class_levels:
        subclass = character_sheet.get_subclass(class_name)
        if subclass:
            subclasses[class_name] = subclass
    results.append(cls.validate_character_subclasses(class_levels, subclasses))
    
    # Validate background
    background = character_sheet.get_background()
    results.append(cls.validate_character_background(background))
    results.append(cls.validate_character_background_feature(background, character_sheet.get_background_feature()))
    
    # Validate alignment
    ethical, moral = character_sheet.get_alignment()
    results.append(cls.validate_character_alignment(ethical, moral))
    
    # Validate appearance
    results.append(cls.validate_character_appearance(character_sheet.get_appearance()))
    
    # Validate ability scores
    ability_scores = character_sheet.get_ability_scores()
    results.append(cls.validate_character_ability_scores(ability_scores))
    
    # Validate proficiencies
    results.append(cls.validate_character_skill_proficiencies(character_sheet.get_skill_proficiencies()))
    results.append(cls.validate_character_saving_throws(character_sheet.get_saving_throw_proficiencies()))
    results.append(cls.validate_character_weapon_proficiencies(character_sheet.get_weapon_proficiencies()))
    results.append(cls.validate_character_armor_proficiencies(character_sheet.get_armor_proficiencies()))
    results.append(cls.validate_character_tool_proficiencies(character_sheet.get_tool_proficiencies()))
    
    # Validate languages
    results.append(cls.validate_character_languages(character_sheet.get_languages()))
    
    # Validate features and traits
    results.append(cls.validate_character_species_traits(character_sheet.get_species_traits()))
    results.append(cls.validate_character_feats(character_sheet.get_feats()))
    
    # Validate equipment
    results.append(cls.validate_character_armor(character_sheet.get_armor()))
    results.append(cls.validate_character_weapons(character_sheet.get_weapons()))
    results.append(cls.validate_character_equipment(character_sheet.get_equipment()))
    results.append(cls.validate_character_currency(character_sheet.get_currency()))
    
    # Validate spellcasting
    results.append(cls.validate_character_spellcasting(
        character_sheet.get_spellcasting_ability(),
        character_sheet.get_spellcasting_classes()
    ))
    results.append(cls.validate_character_spells_known(character_sheet.get_spells_known()))
    results.append(cls.validate_character_spells_prepared(character_sheet.get_spells_prepared()))
    
    # Validate personality
    results.append(cls.validate_character_personality_traits(background, character_sheet.get_personality_traits()))
    results.append(cls.validate_character_ideals(background, character_sheet.get_ideals()))
    results.append(cls.validate_character_bonds(background, character_sheet.get_bonds()))
    results.append(cls.validate_character_flaws(background, character_sheet.get_flaws()))
    results.append(cls.validate_character_backstory(character_sheet.get_backstory()))
    
    # Validate movement and senses
    results.append(cls.validate_character_base_speed(character_sheet.get_base_speed()))
    results.append(cls.validate_character_vision_types(character_sheet.get_vision_types()))
    results.append(cls.validate_character_movement_types(character_sheet.get_movement_types()))
    
    # Validate hit dice
    results.append(cls.validate_character_hit_dice(character_sheet.get_hit_dice(), class_levels))
    
    return results

# the following used to define rules for how to level up (for all 20 levels) and how to multiclass:
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple

class AbstractMulticlassAndLevelUp(ABC):
    """
    Abstract base class defining the contract for character level-up and multiclassing 
    in D&D 5e (2024 Edition).
    
    This interface focuses exclusively on the rules governing character advancement
    through level-up and multiclassing.
    """
    
    # Experience point thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Proficiency bonus by level
    PROFICIENCY_BONUS = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    @abstractmethod
    def level_up(self, new_class: Optional[str] = None) -> Dict[str, Any]:
        """
        Level up the character in their current class or a new class.
        
        Per D&D 2024 rules, leveling up includes:
        - Increasing hit points (roll or take average of class hit die + CON mod)
        - Gaining class features for the new level
        - Potentially gaining ASI (levels 4, 8, 12, 16, 19)
        - Potentially gaining new spell slots and spells
        - Updating proficiency bonus if applicable
        
        Args:
            new_class: If specified, multiclass into this new class
                      Otherwise, level up in the character's highest class
            
        Returns:
            Dict[str, Any]: Results of the level up process including:
                - new_level: The character's new level
                - hp_increase: Hit points gained
                - new_features: List of new features gained
                - proficiency_increase: Whether proficiency bonus increased
                - new_spells: New spell slots or spells gained (if applicable)
                - asi: Whether an ability score improvement was gained
        """
        pass
    
    @abstractmethod
    def can_multiclass_into(self, new_class: str) -> Tuple[bool, str]:
        """
        Check if character meets ability score requirements to multiclass.
        
        This method should:
        1. Find the class definition for the requested class
        2. Get its multiclassing requirements using get_multiclass_requirements()
        3. Check character's ability scores against these requirements
        4. Support both official classes and custom classes
        
        Args:
            new_class: Class to check for multiclassing
            
        Returns:
            Tuple[bool, str]: (Can multiclass, explanation)
        """
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self, new_class: str) -> Dict[str, List[str]]:
        """
        Get proficiencies gained when multiclassing into a specific class.
        
        Per D&D 2024 rules, multiclass proficiency gains are more limited:
        - No saving throw proficiencies are gained
        - Limited skill proficiencies (typically 1, not the normal starting amount)
        - Limited weapon and armor proficiencies
        - Some tool proficiencies may be gained
        
        Args:
            new_class: Class being multiclassed into
            
        Returns:
            Dict[str, List[str]]: Proficiencies gained by category
        """
        pass
    
    @abstractmethod
    def calculate_multiclass_spellcaster_level(self) -> int:
        """
        Calculate effective spellcaster level for determining spell slots.
        
        Per D&D 2024 rules for multiclassed spellcasters:
        - Add all full-caster levels (Bard, Cleric, Druid, Sorcerer, Wizard)
        - Add half of half-caster levels (Paladin, Ranger), rounded down
        - Add one-third of third-caster levels (Fighter-Eldritch Knight, Rogue-Arcane Trickster), rounded down
        - Warlocks follow different rules and don't combine with other classes for spell slots
        
        Returns:
            int: Effective spellcaster level for spell slot determination
        """
        pass
    
    @abstractmethod
    def get_multiclass_spell_slots(self) -> Dict[int, int]:
        """
        Get available spell slots based on multiclass spellcaster level.
        
        Per D&D 2024 rules, spell slots are determined by combined spellcaster level,
        regardless of which spells from which classes are being cast with those slots.
        
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to number of slots
        """
        pass
    
    @abstractmethod
    def calculate_multiclass_hit_points(self, new_class: str, is_first_level: bool = False) -> int:
        """
        Calculate hit points gained when leveling up in a multiclass.
        
        Per D&D 2024 rules:
        - First level in primary class: Maximum hit die + CON modifier
        - Any other level: Roll or take average of hit die + CON modifier
        
        Args:
            new_class: Class being leveled up in
            is_first_level: Whether this is the first level in this class
            
        Returns:
            int: Hit points gained
        """
        pass
    
    @abstractmethod
    def get_level_in_class(self, class_name: str) -> int:
        """
        Get character's level in a specific class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            int: Level in that class (0 if not taken)
        """
        pass
    
    @abstractmethod
    def get_features_for_multiclass(self, class_name: str, level: int) -> Dict[str, Any]:
        """
        Get features gained for a specific class at a specific level.
        
        Per D&D 2024 rules, some features don't stack when multiclassing:
        - Extra Attack from multiple classes doesn't provide additional attacks
        - Channel Divinity options stack, but not uses per rest
        - Unarmored Defense doesn't stack if gained from multiple classes
        
        Args:
            class_name: Name of the class
            level: Level in that class
            
        Returns:
            Dict[str, Any]: Features gained at that level
        """
        pass
    
    @abstractmethod
    def apply_level_up_choices(self, choices: Dict[str, Any]) -> bool:
        """
        Apply choices made during level up (e.g., new spells, subclass, ASI).
        
        Args:
            choices: Dictionary of level-up choices
            
        Returns:
            bool: Success or failure
        """
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self, class_name: str) -> List[int]:
        """
        Get levels at which a class grants Ability Score Improvements.
        
        Per D&D 2024 rules:
        - Most classes get ASIs at levels 4, 8, 12, 16, 19
        - Fighter gets additional ASIs at levels 6, 14
        - ASIs from different classes stack
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[int]: Levels at which the class grants ASIs
        """
        pass
    
    @abstractmethod
    def check_level_up_eligibility(self) -> Tuple[bool, str]:
        """
        Check if character is eligible for level up based on XP.
        
        Per D&D 2024 rules, characters level up when reaching XP thresholds.
        
        Returns:
            Tuple[bool, str]: (Is eligible, explanation)
        """
        pass
    
    @abstractmethod
    def get_next_level_xp_threshold(self) -> int:
        """
        Get XP needed for next level.
        
        Returns:
            int: XP threshold for next level
        """
        pass
    
    @abstractmethod
    def calculate_character_level(self) -> int:
        """
        Calculate total character level from all class levels.
        
        Per D&D 2024 rules, character level equals the sum of all class levels.
        
        Returns:
            int: Total character level
        """
        pass
    
    @abstractmethod
    def get_available_classes_for_multiclass(self) -> Dict[str, bool]:
        """
        Get all classes and whether character qualifies to multiclass into them.
        
        Returns:
            Dict[str, bool]: Dictionary mapping class names to qualification status
        """
        pass

from typing import Dict, Any, Optional
import logging

from character_core import CharacterCore
from character_state import CharacterState
from character_stats import CharacterStats

logger = logging.getLogger(__name__)

class CharacterSheet:
    """
    Main character sheet class that orchestrates the three sub-components:
    - CharacterCore: Core character build data
    - CharacterState: Current gameplay state
    - CharacterStats: Calculated/derived statistics
    """
    
    def __init__(self, name: str = ""):
        self.core = CharacterCore(name)
        self.state = CharacterState()
        self.stats = CharacterStats(self.core, self.state)
        
        # Validation tracking
        self._last_validation_result: Optional[Dict[str, Any]] = None
        self._validation_timestamp: Optional[str] = None
    
    def validate_against_rules(self, use_unified: bool = True) -> Dict[str, Any]:
        """Validate entire character sheet against D&D rules."""
        try:
            if use_unified:
                from unified_validator import create_unified_validator
                validator = create_unified_validator()
                character_data = self.to_dict()
                result = validator.validate_character(character_data, self)
            else:
                # Fallback validation
                core_validation = self.core.validate()
                result = {
                    "overall_valid": core_validation["valid"],
                    "summary": {
                        "total_issues": len(core_validation["issues"]),
                        "total_warnings": len(core_validation["warnings"]),
                        "validators_run": 1,
                        "validators_passed": 1 if core_validation["valid"] else 0
                    },
                    "all_issues": core_validation["issues"],
                    "all_warnings": core_validation["warnings"],
                    "detailed_results": {"core": core_validation}
                }
            
            self._last_validation_result = result
            return result
            
        except Exception as e:
            logger.error(f"Validation failed: {e}")
            return {
                "overall_valid": False,
                "summary": {"total_issues": 1, "validators_run": 0, "validators_passed": 0},
                "all_issues": [f"Validation error: {str(e)}"],
                "all_warnings": [],
                "detailed_results": {}
            }
    
    def calculate_all_derived_stats(self) -> None:
        """Trigger recalculation of all derived statistics."""
        self.stats.invalidate_cache()
        # Accessing properties will trigger recalculation
        _ = self.stats.proficiency_bonus
        _ = self.stats.armor_class
        _ = self.stats.max_hit_points
        _ = self.stats.initiative
    
    # Convenience properties that delegate to appropriate sub-components
    @property
    def name(self) -> str:
        return self.core.name
    
    @property
    def total_level(self) -> int:
        return self.core.total_level
    
    @property
    def armor_class(self) -> int:
        return self.stats.armor_class
    
    @property
    def current_hit_points(self) -> int:
        return self.state.current_hit_points
    
    @property
    def max_hit_points(self) -> int:
        return self.stats.max_hit_points
    
    # Convenience methods for common operations
    def level_up(self, class_name: str) -> None:
        """Level up in the specified class."""
        current_level = self.core.character_classes.get(class_name, 0)
        self.core.character_classes[class_name] = current_level + 1
        self.calculate_all_derived_stats()
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = self.state.take_damage(damage)
        # Check if character died
        if self.state.current_hit_points == 0:
            # Handle death/unconsciousness
            self.state.add_condition("unconscious")
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character."""
        old_hp = self.state.current_hit_points
        self.state.current_hit_points = min(self.stats.max_hit_points, old_hp + healing)
        healed = self.state.current_hit_points - old_hp
        
        # Remove unconscious condition if healed above 0
        if self.state.current_hit_points > 0 and "unconscious" in self.state.active_conditions:
            self.state.remove_condition("unconscious")
        
        return healed
    
    def get_character_summary(self) -> Dict[str, Any]:
        """Create a comprehensive character summary."""
        return {
            # Core identity
            "name": self.core.name,
            "species": self.core.species,
            "level": self.core.total_level,
            "classes": self.core.character_classes,
            "background": self.core.background,
            
            # Ability scores
            "ability_scores": {
                "strength": self.core.strength.total_score,
                "dexterity": self.core.dexterity.total_score,
                "constitution": self.core.constitution.total_score,
                "intelligence": self.core.intelligence.total_score,
                "wisdom": self.core.wisdom.total_score,
                "charisma": self.core.charisma.total_score
            },
            
            # Combat stats
            "armor_class": self.stats.armor_class,
            "hit_points": {
                "current": self.state.current_hit_points,
                "max": self.stats.max_hit_points,
                "temp": self.state.temporary_hit_points
            },
            "initiative": self.stats.initiative,
            "proficiency_bonus": self.stats.proficiency_bonus,
            
            # Current state
            "conditions": list(self.state.active_conditions.keys()),
            "exhaustion_level": self.state.exhaustion_level,
            
            # Equipment
            "armor": self.state.armor,
            "shield": self.state.shield,
            "weapons": self.state.weapons,
            
            # Validation
            "is_valid": self._last_validation_result.get("overall_valid", False) if self._last_validation_result else None
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entire character sheet to dictionary."""
        return {
            "core": self.core.to_dict(),
            "state": self.state.to_dict(),
            "stats": self.stats.to_dict(),
            "validation": self._last_validation_result
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load character sheet from dictionary."""
        if "core" in data:
            # Load core data
            core_data = data["core"]
            self.core.name = core_data.get("name", "")
            self.core.species = core_data.get("species", "")
            # ... load other core data
        
        if "state" in data:
            # Load state data
            state_data = data["state"]
            self.state.current_hit_points = state_data.get("hit_points", {}).get("current", 0)
            # ... load other state data
        
        # Recalculate stats after loading
        self.calculate_all_derived_stats()

from typing import Dict, List, Optional, Any
from datetime import datetime

class CharacterState:
    """
    IN-GAME INDEPENDENT VARIABLES - Updated during gameplay.
    
    These variables track the character's current state and resources,
    changing frequently during gameplay sessions.
    """
    
    def __init__(self):
        # Experience Points
        self.experience_points: int = 0
        
        # Hit Points - Current Values
        self.current_hit_points: int = 0
        self.temporary_hit_points: int = 0
        self.hit_point_maximum_modifier: int = 0
        
        # Hit Dice - Current Values
        self.hit_dice_remaining: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Spell Slots - Current Values
        self.spell_slots_total: Dict[int, int] = {}     # {1: 4, 2: 3, 3: 2}
        self.spell_slots_remaining: Dict[int, int] = {}  # {1: 2, 2: 1, 3: 0}
        self.spells_known: Dict[int, List[str]] = {}    # {0: ["Fire Bolt"], 1: ["Magic Missile"]}
        self.spells_prepared: List[str] = []
        self.ritual_book_spells: List[str] = []
        
        # Equipment - Current Items
        self.armor: Optional[str] = None
        self.shield: bool = False
        self.weapons: List[Dict[str, Any]] = []
        self.equipment: List[Dict[str, Any]] = []
        self.magical_items: List[Dict[str, Any]] = []
        self.attuned_items: List[str] = []
        self.max_attunement_slots: int = 3
        
        # Currency
        self.currency: Dict[str, int] = {
            "copper": 0, "silver": 0, "electrum": 0, "gold": 0, "platinum": 0
        }
        
        # Conditions and Effects
        self.active_conditions: Dict[str, Dict[str, Any]] = {}
        self.exhaustion_level: int = 0
        
        # Temporary Defenses
        self.temp_damage_resistances: Set[str] = set()
        self.temp_damage_immunities: Set[str] = set()
        self.temp_damage_vulnerabilities: Set[str] = set()
        self.temp_condition_immunities: Set[str] = set()
        
        # Action Economy - Current State
        self.actions_per_turn: int = 1
        self.bonus_actions_per_turn: int = 1
        self.reactions_per_turn: int = 1
        self.actions_used: int = 0
        self.bonus_actions_used: int = 0
        self.reactions_used: int = 0
        
        # Companion Creatures
        self.beast_companion: Optional[Dict[str, Any]] = None
        
        # Adventure Notes
        self.notes: Dict[str, str] = {
            'organizations': "", 'allies': "", 'enemies': "", 'backstory': "", 'other': ""
        }
        
        # Timestamps
        self.last_updated: str = ""
        self.last_long_rest: Optional[str] = None
        self.last_short_rest: Optional[str] = None
    
    def reset_action_economy(self) -> None:
        """Reset action economy for a new turn."""
        self.actions_used = 0
        self.bonus_actions_used = 0
        self.reactions_used = 0
    
    def take_damage(self, damage: int) -> Dict[str, int]:
        """Apply damage to the character."""
        result = {"temp_hp_damage": 0, "hp_damage": 0, "overkill": 0}
        
        # Apply to temporary HP first
        if self.temporary_hit_points > 0:
            temp_damage = min(damage, self.temporary_hit_points)
            self.temporary_hit_points -= temp_damage
            damage -= temp_damage
            result["temp_hp_damage"] = temp_damage
        
        # Then to regular HP
        if damage > 0:
            self.current_hit_points -= damage
            result["hp_damage"] = damage
            
            if self.current_hit_points < 0:
                result["overkill"] = abs(self.current_hit_points)
                self.current_hit_points = 0
        
        return result
    
    def heal(self, healing: int) -> int:
        """Heal the character and return amount healed."""
        # Note: This needs max_hit_points from CharacterStats
        # Will be handled by the main CharacterSheet class
        pass
    
    def use_spell_slot(self, level: int) -> bool:
        """Use a spell slot of the specified level."""
        if level not in self.spell_slots_remaining or self.spell_slots_remaining[level] <= 0:
            return False
        
        self.spell_slots_remaining[level] -= 1
        return True
    
    def add_condition(self, condition: str, duration: Optional[int] = None, 
                     source: Optional[str] = None) -> None:
        """Apply a condition to the character."""
        self.active_conditions[condition] = {
            "duration": duration,
            "source": source,
            "applied_at": datetime.now().isoformat()
        }
    
    def remove_condition(self, condition: str) -> bool:
        """Remove a condition from the character."""
        if condition in self.active_conditions:
            del self.active_conditions[condition]
            return True
        return False
    
    def take_short_rest(self, hit_dice_spent: Optional[Dict[str, int]] = None) -> Dict[str, Any]:
        """Perform a short rest."""
        result = {"hp_recovered": 0, "hit_dice_spent": {}}
        
        if hit_dice_spent:
            # Process hit dice healing
            for die_type, count in hit_dice_spent.items():
                available = self.hit_dice_remaining.get(die_type, 0)
                if available >= count:
                    self.hit_dice_remaining[die_type] = available - count
                    result["hit_dice_spent"][die_type] = count
                    # HP recovery calculation would need CharacterStats
        
        self.last_short_rest = datetime.now().isoformat()
        return result
    
    def take_long_rest(self) -> Dict[str, Any]:
        """Perform a long rest."""
        result = {"hp_recovered": 0, "spell_slots_recovered": {}, "hit_dice_recovered": {}}
        
        # Restore spell slots
        for level, total in self.spell_slots_total.items():
            old_slots = self.spell_slots_remaining.get(level, 0)
            self.spell_slots_remaining[level] = total
            result["spell_slots_recovered"][level] = total - old_slots
        
        # Reduce exhaustion by 1
        if self.exhaustion_level > 0:
            self.exhaustion_level -= 1
        
        self.last_long_rest = datetime.now().isoformat()
        return result
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "experience_points": self.experience_points,
            "hit_points": {
                "current": self.current_hit_points,
                "temporary": self.temporary_hit_points,
                "max_modifier": self.hit_point_maximum_modifier
            },
            "spell_slots": {
                "total": self.spell_slots_total,
                "remaining": self.spell_slots_remaining
            },
            "spells": {
                "known": self.spells_known,
                "prepared": self.spells_prepared,
                "ritual_book": self.ritual_book_spells
            },
            "equipment": {
                "armor": self.armor,
                "shield": self.shield,
                "weapons": self.weapons,
                "items": self.equipment,
                "magical_items": self.magical_items,
                "attuned": self.attuned_items
            },
            "currency": self.currency,
            "conditions": {
                "active": self.active_conditions,
                "exhaustion": self.exhaustion_level
            },
            "action_economy": {
                "actions_used": self.actions_used,
                "bonus_actions_used": self.bonus_actions_used,
                "reactions_used": self.reactions_used
            },
            "notes": self.notes,
            "timestamps": {
                "last_updated": self.last_updated,
                "last_long_rest": self.last_long_rest,
                "last_short_rest": self.last_short_rest
            }
        }

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CharacterStats:
    """
    DEPENDENT VARIABLES - Calculated from other variables.
    
    These variables are computed based on core character data and current state.
    They should be recalculated whenever their dependencies change.
    """
    
    def __init__(self, core: 'CharacterCore', state: 'CharacterState'):
        self.core = core
        self.state = state
        
        # Cached calculated values
        self._proficiency_bonus: Optional[int] = None
        self._armor_class: Optional[int] = None
        self._max_hit_points: Optional[int] = None
        self._initiative: Optional[int] = None
        self._spell_save_dc: Optional[int] = None
        self._spell_attack_bonus: Optional[int] = None
        self._passive_perception: Optional[int] = None
        self._passive_investigation: Optional[int] = None
        self._passive_insight: Optional[int] = None
        
        # Available actions (computed based on class features, etc.)
        self._available_actions: Dict[str, Dict[str, Any]] = {}
        self._available_reactions: Dict[str, Dict[str, Any]] = {}
        
        # Dependencies tracking for cache invalidation
        self._last_core_hash: Optional[int] = None
        self._last_state_hash: Optional[int] = None
    
    def invalidate_cache(self) -> None:
        """Invalidate all cached calculations."""
        self._proficiency_bonus = None
        self._armor_class = None
        self._max_hit_points = None
        self._initiative = None
        self._spell_save_dc = None
        self._spell_attack_bonus = None
        self._passive_perception = None
        self._passive_investigation = None
        self._passive_insight = None
        self._available_actions = {}
        self._available_reactions = {}
    
    def _needs_recalculation(self) -> bool:
        """Check if recalculation is needed based on dependencies."""
        # Simple hash-based dependency tracking
        core_hash = hash(str(self.core.to_dict()))
        state_hash = hash(str(self.state.to_dict()))
        
        if (self._last_core_hash != core_hash or 
            self._last_state_hash != state_hash):
            self._last_core_hash = core_hash
            self._last_state_hash = state_hash
            return True
        return False
    
    @property
    def proficiency_bonus(self) -> int:
        """Calculate proficiency bonus based on character level."""
        if self._proficiency_bonus is None or self._needs_recalculation():
            level = self.core.total_level
            self._proficiency_bonus = 2 + ((level - 1) // 4)
        return self._proficiency_bonus
    
    @property
    def armor_class(self) -> int:
        """Calculate armor class based on equipment and abilities."""
        if self._armor_class is None or self._needs_recalculation():
            self._armor_class = self._calculate_armor_class()
        return self._armor_class
    
    @property
    def max_hit_points(self) -> int:
        """Calculate maximum hit points."""
        if self._max_hit_points is None or self._needs_recalculation():
            self._max_hit_points = self._calculate_max_hit_points()
        return self._max_hit_points
    
    @property
    def initiative(self) -> int:
        """Calculate initiative bonus."""
        if self._initiative is None or self._needs_recalculation():
            self._initiative = self._calculate_initiative()
        return self._initiative
    
    @property
    def spell_save_dc(self) -> int:
        """Calculate spell save DC."""
        if self._spell_save_dc is None or self._needs_recalculation():
            self._spell_save_dc = self._calculate_spell_save_dc()
        return self._spell_save_dc
    
    @property
    def spell_attack_bonus(self) -> int:
        """Calculate spell attack bonus."""
        if self._spell_attack_bonus is None or self._needs_recalculation():
            self._spell_attack_bonus = self._calculate_spell_attack_bonus()
        return self._spell_attack_bonus
    
    @property
    def passive_perception(self) -> int:
        """Calculate passive Perception score."""
        if self._passive_perception is None or self._needs_recalculation():
            self._passive_perception = self._calculate_passive_perception()
        return self._passive_perception
    
    def _calculate_armor_class(self) -> int:
        """Internal method to calculate armor class."""
        base_ac = 10
        dex_mod = self.core.dexterity.modifier
        
        # Check for worn armor
        if self.state.armor:
            armor_type = self.state.armor.lower()
            
            # Light armor
            if any(a in armor_type for a in ["padded", "leather"]):
                if "studded" in armor_type:
                    base_ac = 12 + dex_mod
                else:
                    base_ac = 11 + dex_mod
            
            # Medium armor
            elif any(a in armor_type for a in ["chain shirt", "scale", "breastplate", "half plate"]):
                if "chain shirt" in armor_type:
                    base_ac = 13 + min(dex_mod, 2)
                elif "scale" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "breastplate" in armor_type:
                    base_ac = 14 + min(dex_mod, 2)
                elif "half plate" in armor_type:
                    base_ac = 15 + min(dex_mod, 2)
            
            # Heavy armor
            elif any(a in armor_type for a in ["ring mail", "chain mail", "splint", "plate"]):
                if "ring mail" in armor_type:
                    base_ac = 14
                elif "chain mail" in armor_type:
                    base_ac = 16
                elif "splint" in armor_type:
                    base_ac = 17
                elif "plate" in armor_type:
                    base_ac = 18
        else:
            # Unarmored Defense
            if "Barbarian" in self.core.character_classes:
                con_mod = self.core.constitution.modifier
                barbarian_ac = 10 + dex_mod + con_mod
                base_ac = max(base_ac, barbarian_ac)
            
            if "Monk" in self.core.character_classes:
                wis_mod = self.core.wisdom.modifier
                monk_ac = 10 + dex_mod + wis_mod
                base_ac = max(base_ac, monk_ac)
        
        # Add shield bonus
        if self.state.shield:
            base_ac += 2
        
        return base_ac
    
    def _calculate_max_hit_points(self) -> int:
        """Internal method to calculate maximum hit points."""
        if not self.core.character_classes:
            return 1
        
        con_mod = self.core.constitution.modifier
        total = 0
        
        hit_die_sizes = {
            "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
            "Monk": 8, "Rogue": 8, "Warlock": 8, "Bard": 8, "Cleric": 8, "Druid": 8,
            "Wizard": 6, "Sorcerer": 6
        }
        
        for class_name, level in self.core.character_classes.items():
            if level <= 0:
                continue
                
            hit_die = hit_die_sizes.get(class_name, 8)
            
            # First level is max hit die + CON
            if class_name == self.core.primary_class:
                total += hit_die + con_mod
                remaining_levels = level - 1
            else:
                remaining_levels = level
            
            # Average for remaining levels
            total += remaining_levels * ((hit_die // 2) + 1 + con_mod)
        
        # Add modifiers from state
        total += self.state.hit_point_maximum_modifier
        
        return max(1, total)
    
    def _calculate_initiative(self) -> int:
        """Internal method to calculate initiative."""
        dex_mod = self.core.dexterity.modifier
        bonus = 0
        
        # Check for feats and features
        if "Alert" in self.core.feats:
            bonus += 5
        
        if "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:  # Jack of All Trades
                bonus += self.proficiency_bonus // 2
        
        return dex_mod + bonus
    
    def _calculate_spell_save_dc(self) -> int:
        """Internal method to calculate spell save DC."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return 8 + self.proficiency_bonus + ability_mod
    
    def _calculate_spell_attack_bonus(self) -> int:
        """Internal method to calculate spell attack bonus."""
        if not self.core.spellcasting_ability:
            return 0
        
        ability_mod = self.core.get_ability_score(self.core.spellcasting_ability).modifier
        return self.proficiency_bonus + ability_mod
    
    def _calculate_passive_perception(self) -> int:
        """Internal method to calculate passive Perception."""
        wis_mod = self.core.wisdom.modifier
        prof_bonus = 0
        
        perception_prof = self.core.skill_proficiencies.get("Perception", ProficiencyLevel.NONE)
        if perception_prof == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif perception_prof == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        feat_bonus = 5 if "Observant" in self.core.feats else 0
        
        return 10 + wis_mod + prof_bonus + feat_bonus
    
    def calculate_skill_bonus(self, skill_name: str) -> int:
        """Calculate bonus for a specific skill check."""
        skill_abilities = {
            "Athletics": "strength", "Acrobatics": "dexterity",
            "Sleight of Hand": "dexterity", "Stealth": "dexterity",
            "Arcana": "intelligence", "History": "intelligence",
            "Investigation": "intelligence", "Nature": "intelligence", "Religion": "intelligence",
            "Animal Handling": "wisdom", "Insight": "wisdom", "Medicine": "wisdom",
            "Perception": "wisdom", "Survival": "wisdom",
            "Deception": "charisma", "Intimidation": "charisma",
            "Performance": "charisma", "Persuasion": "charisma"
        }
        
        if skill_name not in skill_abilities:
            return 0
        
        ability = skill_abilities[skill_name]
        ability_mod = self.core.get_ability_score(ability).modifier
        
        # Check proficiency
        prof_level = self.core.skill_proficiencies.get(skill_name, ProficiencyLevel.NONE)
        prof_bonus = 0
        if prof_level == ProficiencyLevel.PROFICIENT:
            prof_bonus = self.proficiency_bonus
        elif prof_level == ProficiencyLevel.EXPERT:
            prof_bonus = self.proficiency_bonus * 2
        
        # Jack of All Trades for non-proficient skills
        if prof_level == ProficiencyLevel.NONE and "Bard" in self.core.character_classes:
            bard_level = self.core.character_classes.get("Bard", 0)
            if bard_level >= 2:
                prof_bonus = self.proficiency_bonus // 2
        
        return ability_mod + prof_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert calculated stats to dictionary."""
        return {
            "proficiency_bonus": self.proficiency_bonus,
            "armor_class": self.armor_class,
            "max_hit_points": self.max_hit_points,
            "initiative": self.initiative,
            "spell_save_dc": self.spell_save_dc,
            "spell_attack_bonus": self.spell_attack_bonus,
            "passive_perception": self.passive_perception,
            "available_actions": self._available_actions,
            "available_reactions": self._available_reactions
        }
    
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Any
from enum import Enum

class ProficiencyLevel(Enum):
    """Enumeration for proficiency levels in D&D 5e."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class AbilityScore:
    """Class representing a D&D ability score with its component values."""
    
    def __init__(self, base_score: int = 10):
        self.base_score: int = base_score
        self.bonus: int = 0
        self.set_score: Optional[int] = None
        self.stacking_bonuses: Dict[str, int] = {}
    
    @property
    def total_score(self) -> int:
        if self.set_score is not None:
            return self.set_score
        return max(1, min(30, self.base_score + self.bonus + sum(self.stacking_bonuses.values())))
    
    @property
    def modifier(self) -> int:
        return (self.total_score - 10) // 2

class CharacterCore:
    """
    CORE INDEPENDENT VARIABLES - Set during character creation/leveling.
    
    These variables define the fundamental character build and rarely change
    except through leveling up or major story events.
    """
    
    def __init__(self, name: str = ""):
        # Basic Character Identity
        self.name: str = name
        self.species: str = ""
        self.species_variants: List[str] = []
        self.lineage: Optional[str] = None
        self.character_classes: Dict[str, int] = {}  # {"Fighter": 3, "Wizard": 2}
        self.subclasses: Dict[str, str] = {}  # {"Fighter": "Champion"}
        self.background: str = ""
        self.alignment_ethical: str = ""  # Lawful, Neutral, Chaotic
        self.alignment_moral: str = ""    # Good, Neutral, Evil
        
        # Appearance and Identity
        self.height: str = ""
        self.weight: str = ""
        self.age: int = 0
        self.eyes: str = ""
        self.hair: str = ""
        self.skin: str = ""
        self.gender: str = ""
        self.pronouns: str = ""
        self.size: str = "Medium"
        
        # Base Ability Scores
        self.strength: AbilityScore = AbilityScore(10)
        self.dexterity: AbilityScore = AbilityScore(10)
        self.constitution: AbilityScore = AbilityScore(10)
        self.intelligence: AbilityScore = AbilityScore(10)
        self.wisdom: AbilityScore = AbilityScore(10)
        self.charisma: AbilityScore = AbilityScore(10)
        
        # Core Proficiencies
        self.skill_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.saving_throw_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.weapon_proficiencies: Set[str] = set()
        self.armor_proficiencies: Set[str] = set()
        self.tool_proficiencies: Dict[str, ProficiencyLevel] = {}
        self.languages: Set[str] = set()
        
        # Core Features and Traits
        self.species_traits: Dict[str, Any] = {}
        self.class_features: Dict[str, Any] = {}
        self.background_feature: str = ""
        self.feats: List[str] = []
        
        # Core Movement and Senses
        self.base_speed: int = 30
        self.base_vision_types: Dict[str, int] = {}  # {"darkvision": 60}
        self.base_movement_types: Dict[str, int] = {}  # {"swim": 30, "fly": 0}
        
        # Core Defenses
        self.base_damage_resistances: Set[str] = set()
        self.base_damage_immunities: Set[str] = set()
        self.base_damage_vulnerabilities: Set[str] = set()
        self.base_condition_immunities: Set[str] = set()
        
        # Core Spellcasting Abilities
        self.spellcasting_ability: Optional[str] = None
        self.spellcasting_classes: Dict[str, Dict[str, Any]] = {}
        self.ritual_casting_classes: Dict[str, bool] = {}
        
        # Character Background & Personality
        self.personality_traits: List[str] = []
        self.ideals: List[str] = []
        self.bonds: List[str] = []
        self.flaws: List[str] = []
        self.backstory: str = ""
        
        # Hit Dice (base values from class)
        self.hit_dice: Dict[str, int] = {}  # {"d8": 3, "d6": 2}
        
        # Character Sheet Metadata
        self.creation_date: str = ""
        self.player_name: str = ""
        self.campaign: str = ""
        self.sources_used: Set[str] = set()
    
    @property
    def total_level(self) -> int:
        """Calculate total character level from all classes."""
        return sum(self.character_classes.values()) if self.character_classes else 1
    
    @property
    def primary_class(self) -> str:
        """Determine primary class (highest level or first class)."""
        if not self.character_classes:
            return ""
        return max(self.character_classes.items(), key=lambda x: x[1])[0]
    
    def get_ability_score(self, ability: str) -> AbilityScore:
        """Get the AbilityScore object for a specific ability."""
        ability_map = {
            "strength": self.strength, "str": self.strength,
            "dexterity": self.dexterity, "dex": self.dexterity,
            "constitution": self.constitution, "con": self.constitution,
            "intelligence": self.intelligence, "int": self.intelligence,
            "wisdom": self.wisdom, "wis": self.wisdom,
            "charisma": self.charisma, "cha": self.charisma
        }
        return ability_map.get(ability.lower())
    
    def validate(self) -> Dict[str, Any]:
        """Validate core character data."""
        issues = []
        warnings = []
        
        # Basic validation
        if not self.name.strip():
            warnings.append("Character name is empty")
        
        if not self.species:
            issues.append("Species is required")
        
        if not self.character_classes:
            issues.append("At least one character class is required")
        
        # Ability score validation
        for ability_name in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            ability = self.get_ability_score(ability_name)
            if ability and (ability.total_score < 1 or ability.total_score > 30):
                issues.append(f"{ability_name.title()} score ({ability.total_score}) must be between 1 and 30")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "species": self.species,
            "species_variants": self.species_variants,
            "lineage": self.lineage,
            "character_classes": self.character_classes,
            "subclasses": self.subclasses,
            "background": self.background,
            "alignment": [self.alignment_ethical, self.alignment_moral],
            "ability_scores": {
                "strength": self.strength.total_score,
                "dexterity": self.dexterity.total_score,
                "constitution": self.constitution.total_score,
                "intelligence": self.intelligence.total_score,
                "wisdom": self.wisdom.total_score,
                "charisma": self.charisma.total_score
            },
            "proficiencies": {
                "skills": dict(self.skill_proficiencies),
                "saving_throws": dict(self.saving_throw_proficiencies),
                "weapons": list(self.weapon_proficiencies),
                "armor": list(self.armor_proficiencies),
                "tools": dict(self.tool_proficiencies),
                "languages": list(self.languages)
            },
            "features": {
                "species_traits": self.species_traits,
                "class_features": self.class_features,
                "background_feature": self.background_feature,
                "feats": self.feats
            },
            "spellcasting": {
                "ability": self.spellcasting_ability,
                "classes": self.spellcasting_classes
            },
            "personality": {
                "traits": self.personality_traits,
                "ideals": self.ideals,
                "bonds": self.bonds,
                "flaws": self.flaws,
                "backstory": self.backstory
            }
        }

import sys
import os
from typing import Dict, List, Any, Optional, Union, Tuple
import logging

# Add project paths for imports
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend4')
sys.path.append('/home/ajs7/dnd_tools/dnd_char_creator/backend')

# Core imports
from character_sheet import CharacterSheet
from create_rules import CreateRules

# Try to import legacy validators with fallbacks
try:
    from backend.core.character.character_validator import CharacterValidator
    LEGACY_VALIDATOR_AVAILABLE = True
except ImportError:
    print("Warning: Legacy CharacterValidator not found, using simplified validation")
    LEGACY_VALIDATOR_AVAILABLE = False

try:
    from backend.services.validation_service import ValidationService
    VALIDATION_SERVICE_AVAILABLE = True
except ImportError:
    print("Warning: ValidationService not found")
    VALIDATION_SERVICE_AVAILABLE = False

logger = logging.getLogger(__name__)


class ValidationResult:
    """Structured validation result container."""
    
    def __init__(self, valid: bool = True, issues: List[str] = None, 
                 warnings: List[str] = None, validator_name: str = "unknown"):
        self.valid = valid
        self.issues = issues or []
        self.warnings = warnings or []
        self.validator_name = validator_name
        self.total_checks = len(self.issues) + len(self.warnings) if self.issues or self.warnings else 1
        self.passed_checks = 1 if valid else 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "valid": self.valid,
            "issues": self.issues,
            "warnings": self.warnings,
            "validator": self.validator_name,
            "total_checks": self.total_checks,
            "passed_checks": self.passed_checks
        }


class SimplifiedCharacterValidator:
    """Fallback validator when legacy systems aren't available."""
    
    def validate_full_character(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Basic character validation."""
        issues = []
        warnings = []
        
        # Basic required fields
        required_fields = ["name", "species", "level", "classes", "ability_scores"]
        for field in required_fields:
            if field not in character_data or not character_data[field]:
                issues.append(f"Missing required field: {field}")
        
        # Validate ability scores
        if "ability_scores" in character_data:
            for ability, score in character_data["ability_scores"].items():
                if not isinstance(score, int) or score < 1 or score > 30:
                    issues.append(f"Invalid {ability} score: {score} (must be 1-30)")
        
        # Validate level
        if "level" in character_data:
            level = character_data["level"]
            if not isinstance(level, int) or level < 1 or level > 20:
                issues.append(f"Invalid character level: {level} (must be 1-20)")
        
        # Validate classes
        if "classes" in character_data:
            classes = character_data["classes"]
            if isinstance(classes, dict):
                total_levels = sum(classes.values())
                if total_levels != character_data.get("level", 1):
                    warnings.append(f"Class levels ({total_levels}) don't match character level ({character_data.get('level', 1)})")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "total_checks": len(issues) + len(warnings) + 1,
            "passed_checks": len(issues) == 0
        }


class UnifiedCharacterValidator:
    """
    Unified character validator that combines multiple validation approaches.
    
    This validator attempts to use:
    1. Legacy CharacterValidator (if available)
    2. ValidationService (if available) 
    3. CreateRules comprehensive validation
    4. Simplified fallback validation
    """
    
    def __init__(self):
        # Initialize available validators
        self.legacy_validator = None
        self.validation_service = None
        self.create_rules = CreateRules()
        self.simplified_validator = SimplifiedCharacterValidator()
        
        # Try to initialize legacy systems
        if LEGACY_VALIDATOR_AVAILABLE:
            try:
                self.legacy_validator = CharacterValidator()
                logger.info("Legacy CharacterValidator initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize legacy validator: {e}")
        
        if VALIDATION_SERVICE_AVAILABLE:
            try:
                self.validation_service = ValidationService()
                logger.info("ValidationService initialized")
            except Exception as e:
                logger.warning(f"Failed to initialize validation service: {e}")
    
    def validate_character(self, character_data: Dict[str, Any], 
                          character_sheet: Optional[CharacterSheet] = None) -> Dict[str, Any]:
        """
        Comprehensive character validation using all available validators.
        
        Args:
            character_data: Character data dictionary
            character_sheet: Optional CharacterSheet object for advanced validation
            
        Returns:
            Comprehensive validation results
        """
        results = {}
        all_issues = []
        all_warnings = []
        overall_valid = True
        
        # 1. Legacy validator
        if self.legacy_validator:
            try:
                legacy_result = self.legacy_validator.validate_full_character(character_data)
                results["legacy_validation"] = ValidationResult(
                    valid=legacy_result.get("valid", False),
                    issues=legacy_result.get("issues", []),
                    warnings=legacy_result.get("warnings", []),
                    validator_name="legacy"
                ).to_dict()
                
                all_issues.extend(legacy_result.get("issues", []))
                all_warnings.extend(legacy_result.get("warnings", []))
                overall_valid = overall_valid and legacy_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"Legacy validation failed: {e}")
                results["legacy_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Legacy validation error: {str(e)}"],
                    validator_name="legacy"
                ).to_dict()
                overall_valid = False
        
        # 2. Simplified validation (always run as baseline)
        try:
            simple_result = self.simplified_validator.validate_full_character(character_data)
            results["simplified_validation"] = ValidationResult(
                valid=simple_result.get("valid", False),
                issues=simple_result.get("issues", []),
                warnings=simple_result.get("warnings", []),
                validator_name="simplified"
            ).to_dict()
            
            # Only add issues if not already caught by legacy validator
            new_issues = [issue for issue in simple_result.get("issues", []) if issue not in all_issues]
            new_warnings = [warning for warning in simple_result.get("warnings", []) if warning not in all_warnings]
            
            all_issues.extend(new_issues)
            all_warnings.extend(new_warnings)
            overall_valid = overall_valid and simple_result.get("valid", False)
            
        except Exception as e:
            logger.error(f"Simplified validation failed: {e}")
            results["simplified_validation"] = ValidationResult(
                valid=False,
                issues=[f"Simplified validation error: {str(e)}"],
                validator_name="simplified"
            ).to_dict()
            overall_valid = False
        
        # 3. CreateRules validation (if character sheet available)
        if character_sheet:
            try:
                rules_validation = self.create_rules.validate_entire_character_sheet(character_sheet)
                
                rules_issues = [msg for valid, msg in rules_validation if not valid]
                rules_warnings = []  # CreateRules might not distinguish warnings
                
                results["rules_validation"] = ValidationResult(
                    valid=all(valid for valid, _ in rules_validation),
                    issues=rules_issues,
                    warnings=rules_warnings,
                    validator_name="create_rules"
                ).to_dict()
                
                # Add unique issues
                new_rules_issues = [issue for issue in rules_issues if issue not in all_issues]
                all_issues.extend(new_rules_issues)
                overall_valid = overall_valid and all(valid for valid, _ in rules_validation)
                
            except Exception as e:
                logger.error(f"CreateRules validation failed: {e}")
                results["rules_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Rules validation error: {str(e)}"],
                    validator_name="create_rules"
                ).to_dict()
                overall_valid = False
        else:
            logger.info("Character sheet not provided, skipping CreateRules validation")
        
        # 4. ValidationService (if available and character sheet provided)
        if self.validation_service and character_sheet:
            try:
                # Assuming ValidationService has a similar interface
                service_result = self.validation_service.validate_character(character_data)
                results["service_validation"] = ValidationResult(
                    valid=service_result.get("valid", False),
                    issues=service_result.get("issues", []),
                    warnings=service_result.get("warnings", []),
                    validator_name="validation_service"
                ).to_dict()
                
                # Add unique issues
                new_service_issues = [issue for issue in service_result.get("issues", []) if issue not in all_issues]
                new_service_warnings = [warning for warning in service_result.get("warnings", []) if warning not in all_warnings]
                
                all_issues.extend(new_service_issues)
                all_warnings.extend(new_service_warnings)
                overall_valid = overall_valid and service_result.get("valid", False)
                
            except Exception as e:
                logger.error(f"ValidationService failed: {e}")
                results["service_validation"] = ValidationResult(
                    valid=False,
                    issues=[f"Service validation error: {str(e)}"],
                    validator_name="validation_service"
                ).to_dict()
                overall_valid = False
        
        # Compile final results
        total_validators = len([v for v in results.values() if v])
        passed_validators = len([v for v in results.values() if v and v.get("valid", False)])
        
        return {
            "overall_valid": overall_valid,
            "summary": {
                "total_issues": len(all_issues),
                "total_warnings": len(all_warnings),
                "validators_run": total_validators,
                "validators_passed": passed_validators,
                "validation_coverage": f"{passed_validators}/{total_validators}" if total_validators > 0 else "0/0"
            },
            "all_issues": all_issues,
            "all_warnings": all_warnings,
            "detailed_results": results,
            "recommendations": self._generate_recommendations(all_issues, all_warnings)
        }
    
    def validate_character_creation_step(self, step_name: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a specific step in character creation."""
        if step_name == "ability_scores":
            return self._validate_ability_scores(character_data.get("ability_scores", {}))
        elif step_name == "class_selection":
            return self._validate_class_selection(character_data.get("classes", {}))
        elif step_name == "equipment":
            return self._validate_equipment(character_data)
        else:
            # Default to full validation
            return self.validate_character(character_data)
    
    def _validate_ability_scores(self, ability_scores: Dict[str, int]) -> Dict[str, Any]:
        """Validate ability scores specifically."""
        issues = []
        warnings = []
        
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        
        for ability in required_abilities:
            if ability not in ability_scores:
                issues.append(f"Missing ability score: {ability}")
            else:
                score = ability_scores[ability]
                if score < 8:
                    warnings.append(f"{ability.title()} score ({score}) is very low")
                elif score > 18:
                    warnings.append(f"{ability.title()} score ({score}) is exceptionally high for starting character")
        
        total_score = sum(ability_scores.values())
        if total_score < 60:
            warnings.append(f"Total ability scores ({total_score}) are quite low")
        elif total_score > 90:
            warnings.append(f"Total ability scores ({total_score}) are very high")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "ability_scores"
        }
    
    def _validate_class_selection(self, classes: Dict[str, int]) -> Dict[str, Any]:
        """Validate class selection and levels."""
        issues = []
        warnings = []
        
        if not classes:
            issues.append("No classes selected")
        else:
            total_levels = sum(classes.values())
            if len(classes) > 1 and min(classes.values()) < 3:
                warnings.append("Multiclassing before level 3 may limit class features")
            
            for class_name, level in classes.items():
                if level < 1:
                    issues.append(f"Invalid level for {class_name}: {level}")
                elif level > 20:
                    issues.append(f"Class level too high for {class_name}: {level}")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "class_selection"
        }
    
    def _validate_equipment(self, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate equipment selection."""
        issues = []
        warnings = []
        
        # Basic equipment validation
        weapons = character_data.get("weapons", [])
        armor = character_data.get("armor", {})
        
        if not weapons:
            warnings.append("No weapons equipped")
        
        if isinstance(armor, dict) and not armor.get("name"):
            warnings.append("No armor equipped")
        elif isinstance(armor, str) and not armor:
            warnings.append("No armor equipped")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "warnings": warnings,
            "step": "equipment"
        }
    
    def _generate_recommendations(self, issues: List[str], warnings: List[str]) -> List[str]:
        """Generate helpful recommendations based on validation results."""
        recommendations = []
        
        if issues:
            recommendations.append("Fix all validation errors before finalizing character")
        
        if warnings:
            recommendations.append("Review warnings to ensure character meets your expectations")
        
        if not issues and not warnings:
            recommendations.append("Character validation passed! Ready for gameplay")
        
        # Specific recommendations based on common issues
        ability_issues = [issue for issue in issues if "ability" in issue.lower()]
        if ability_issues:
            recommendations.append("Consider using point buy or standard array for balanced ability scores")
        
        class_issues = [issue for issue in issues if "class" in issue.lower()]
        if class_issues:
            recommendations.append("Verify class selection meets multiclassing prerequisites")
        
        return recommendations
    
    def get_validation_summary(self, validation_result: Dict[str, Any]) -> str:
        """Generate a human-readable validation summary."""
        if validation_result["overall_valid"]:
            return f"✅ Character validation passed ({validation_result['summary']['validation_coverage']} validators)"
        else:
            issues = len(validation_result["all_issues"])
            warnings = len(validation_result["all_warnings"])
            return f"❌ Character validation failed: {issues} issues, {warnings} warnings"


# Factory function for easy instantiation
def create_unified_validator() -> UnifiedCharacterValidator:
    """Create a unified validator with proper error handling."""
    try:
        return UnifiedCharacterValidator()
    except Exception as e:
        logger.error(f"Failed to create unified validator: {e}")
        # Return a minimal validator as fallback
        return UnifiedCharacterValidator()


# Convenience function for quick validation
def validate_character_quick(character_data: Dict[str, Any], 
                           character_sheet: Optional[CharacterSheet] = None) -> bool:
    """Quick validation that returns just True/False."""
    validator = create_unified_validator()
    result = validator.validate_character(character_data, character_sheet)
    return result["overall_valid"]

