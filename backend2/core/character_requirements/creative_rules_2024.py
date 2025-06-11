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
                          caster_type: Optional[str] = None) -> bool:
        """
        Register a custom character class.
        
        Args:
            class_name: Name of the custom class (e.g. "Jedi Mind Warrior")
            hit_die: Hit die size (e.g. 8 for d8, 10 for d10)
            multiclass_requirements: Dictionary of ability score requirements
            spellcasting_ability: Primary ability for spellcasting
            caster_type: "full", "half", "third", or "pact"
            
        Returns:
            bool: True if registered successfully
        """
        cls.CUSTOM_CLASSES.add(class_name)
        cls.CUSTOM_HIT_DIE[class_name] = hit_die
        
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
            return cls.ABILITY_SCORE_MIN <= value <= 30
        return cls.ABILITY_SCORE_MIN <= value <= cls.ABILITY_SCORE_MAX
    
    @classmethod
    def is_valid_class(cls, class_name: str) -> bool:
        """Check if a class name is valid (includes custom classes)."""
        return class_name in cls.BASE_CLASSES or class_name in cls.CUSTOM_CLASSES
    
    @classmethod
    def is_valid_skill(cls, skill_name: str) -> bool:
        """Check if a skill name is valid (includes custom skills)."""
        return skill_name in cls.SKILLS or skill_name in cls.CUSTOM_SKILLS
    
    @classmethod
    def get_ability_for_skill(cls, skill_name: str) -> Optional[str]:
        """Get the ability associated with a skill."""
        return cls.SKILLS.get(skill_name) or cls.CUSTOM_SKILLS.get(skill_name)
    
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

    # ===== EQUIPMENT VALIDATION METHODS =====
        
    @classmethod
    def validate_weapon_wielding(cls, character_data: Dict[str, Any], 
                              weapon: AbstractWeapon) -> Tuple[bool, str]:
        """
        Validate if a character can effectively wield a specific weapon.
        
        Args:
            character_data: Character information
            weapon: The weapon to check
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        # Check proficiency
        weapon_name = weapon.get_name()
        weapon_category = weapon.get_category()
        
        has_proficiency = False
        
        # Check for specific weapon proficiency
        if weapon_name in character_data.get("weapon_proficiencies", []):
            has_proficiency = True
            
        # Check for category proficiency
        elif weapon_category in character_data.get("weapon_category_proficiencies", []):
            has_proficiency = True
            
        # Check for strength/dexterity requirements
        str_score = character_data.get("strength", 10)
        dex_score = character_data.get("dexterity", 10)
        
        str_req = getattr(weapon, "strength_requirement", 0)
        
        if str_score < str_req:
            return False, f"Insufficient strength ({str_score}) to wield {weapon_name} effectively (requires {str_req})"
            
        if has_proficiency:
            return True, f"Character can wield {weapon_name} with proficiency"
        else:
            return True, f"Character can wield {weapon_name} without proficiency"
    
    @classmethod
    def validate_armor_wearing(cls, character_data: Dict[str, Any], 
                            armor: AbstractArmor) -> Tuple[bool, str]:
        """
        Validate if a character can effectively wear a specific armor.
        
        Args:
            character_data: Character information
            armor: The armor to check
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        # Check proficiency
        armor_name = armor.get_name()
        armor_category = armor.get_category()
        
        has_proficiency = False
        
        # Check for specific armor proficiency
        if armor_name in character_data.get("armor_proficiencies", []):
            has_proficiency = True
            
        # Check for category proficiency
        elif armor_category in character_data.get("armor_category_proficiencies", []):
            has_proficiency = True
            
        # Check for strength requirement
        str_score = character_data.get("strength", 10)
        str_req = getattr(armor, "strength_requirement", 0)
        
        if str_score < str_req:
            if has_proficiency:
                return True, f"Character can wear {armor_name} but will have movement penalties due to low strength"
            else:
                return False, f"Character lacks proficiency and strength to effectively wear {armor_name}"
                
        if has_proficiency:
            return True, f"Character can wear {armor_name} effectively"
        else:
            return False, f"Character lacks proficiency to wear {armor_name}"
    
    # ===== EXAMPLES AND DEMONSTRATIONS =====
        
    @classmethod
    def create_jedi_example(cls) -> None:
        """
        Create example Jedi class and related content as a demonstration.
        """
        # Register Jedi Mind Warrior class
        cls.register_custom_class(
            "Jedi Mind Warrior", 
            hit_die=10, 
            multiclass_requirements={"wisdom": 13, "charisma": 13},
            spellcasting_ability="wisdom",
            caster_type="full"
        )
        
        # Register Yoda's species
        cls.register_custom_species(
            "Tridactyl",  # Made-up name for Yoda's species
            abilities={
                "ability_bonuses": {"wisdom": 2, "charisma": 1},
                "size": "Small",
                "speed": 25,
                "lifespan": 900,
                "traits": ["Force Sensitivity", "Longevity"]
            }
        )
        
        # Register Force-related skills
        cls.register_custom_skill("Force Perception", "wisdom")
        cls.register_custom_skill("Force Control", "charisma")
        
        # Register Force abilities as feats
        cls.register_custom_feat(
            "Telekinesis Master",
            {
                "prerequisite": {"class": "Jedi Mind Warrior", "level": 3},
                "description": "You can move objects with your mind using the Force",
                "abilities": ["Can cast Telekinesis spell at will"]
            }
        )
        
        # Register Force powers as spells
        cls.register_custom_spell(
            "Force Push",
            {
                "level": 2,
                "casting_time": "1 action",
                "range": "60 feet",
                "components": ["S"],
                "duration": "Instantaneous",
                "description": "You channel the Force to push creatures away from you."
            }
        )

        # Register Force weapon category
        cls.register_custom_weapon_category("Force Weapon")
        
        # Register lightsaber as a weapon
        cls.register_custom_weapon(
            "Lightsaber",
            {
                "category": "Force Weapon",
                "damage_dice": "1d8",
                "damage_type": "radiant",
                "properties": ["Finesse", "Versatile (1d10)", "Sunlight"],
                "weight": 3.0,
                "cost": 1500.0,
                "description": "A weapon of elegance from a more civilized age.",
                "attunement": True,
                "special_abilities": ["Can deflect ranged attacks as a reaction"]
            }
        )
        
        # Register a double-bladed lightsaber variant
        cls.register_custom_weapon(
            "Double-Bladed Lightsaber",
            {
                "category": "Force Weapon",
                "damage_dice": "2d6",
                "damage_type": "radiant",
                "properties": ["Two-Handed", "Special", "Sunlight"],
                "weight": 5.0,
                "cost": 2500.0,
                "description": "A more dangerous lightsaber with blades at both ends.",
                "attunement": True,
                "special_abilities": [
                    "Can make an additional attack as a bonus action",
                    "Can deflect ranged attacks as a reaction"
                ]
            }
        )
        
        # Register Force armor category
        cls.register_custom_armor_category("Force Barrier")
        
        # Register Force Shield as armor
        cls.register_custom_armor(
            "Force Barrier",
            {
                "category": "Force Barrier",
                "base_ac": 16,
                "dex_bonus_allowed": True,
                "max_dex_bonus": None,
                "strength_required": 0,
                "stealth_disadvantage": False,
                "weight": 0.0,
                "cost": 0,
                "description": "A protective barrier created through the Force.",
                "special_abilities": [
                    "Requires concentration to maintain",
                    "Can be dispelled by anti-magic"
                ],
                "duration": "Concentration, up to 1 hour"
            }
        )
        
        logger.info("Jedi example content successfully created!")

    # ===== PERSISTENCE METHODS =====
    
    @classmethod
    def export_custom_content(cls, filename: str) -> bool:
        """
        Export all custom content to a JSON file.
        
        Args:
            filename: Path to save the file
            
        Returns:
            bool: True if successful
        """
        import json
        
        data = {
            "classes": list(cls.CUSTOM_CLASSES),
            "species": list(cls.CUSTOM_SPECIES),
            "feats": list(cls.CUSTOM_FEATS),
            "spells": list(cls.CUSTOM_SPELLS),
            "skills": cls.CUSTOM_SKILLS,
            "weapon_categories": list(cls.CUSTOM_WEAPON_CATEGORIES),
            "armor_categories": list(cls.CUSTOM_ARMOR_CATEGORIES),
            "weapons": cls.CUSTOM_WEAPONS,
            "armor": cls.CUSTOM_ARMOR,
            "metadata": {
                "exported_at": datetime.now().isoformat(),
                "version": "1.0.0"
            }
        }
        
        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            logger.info(f"Custom content exported to {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to export custom content: {e}")
            return False
    
    @classmethod
    def import_custom_content(cls, filename: str) -> bool:
        """
        Import custom content from a JSON file.
        
        Args:
            filename: Path to the file to import
            
        Returns:
            bool: True if successful
        """
        import json
        
        try:
            with open(filename, 'r') as f:
                data = json.load(f)
                
            # Import each type of content
            for class_name in data.get("classes", []):
                if class_name not in cls.CUSTOM_CLASSES:
                    cls.CUSTOM_CLASSES.add(class_name)
                    
            for species_name in data.get("species", []):
                if species_name not in cls.CUSTOM_SPECIES:
                    cls.CUSTOM_SPECIES.add(species_name)
                    
            for feat_name in data.get("feats", []):
                if feat_name not in cls.CUSTOM_FEATS:
                    cls.CUSTOM_FEATS.add(feat_name)
                    
            for spell_name in data.get("spells", []):
                if spell_name not in cls.CUSTOM_SPELLS:
                    cls.CUSTOM_SPELLS.add(spell_name)
                    
            for skill_name, ability in data.get("skills", {}).items():
                if skill_name not in cls.CUSTOM_SKILLS:
                    cls.CUSTOM_SKILLS[skill_name] = ability
                    
            for category in data.get("weapon_categories", []):
                if category not in cls.CUSTOM_WEAPON_CATEGORIES:
                    cls.CUSTOM_WEAPON_CATEGORIES.add(category)
                    
            for category in data.get("armor_categories", []):
                if category not in cls.CUSTOM_ARMOR_CATEGORIES:
                    cls.CUSTOM_ARMOR_CATEGORIES.add(category)
                    
            for weapon_name, properties in data.get("weapons", {}).items():
                if weapon_name not in cls.CUSTOM_WEAPONS:
                    cls.CUSTOM_WEAPONS[weapon_name] = properties
                    
            for armor_name, properties in data.get("armor", {}).items():
                if armor_name not in cls.CUSTOM_ARMOR:
                    cls.CUSTOM_ARMOR[armor_name] = properties
            
            logger.info(f"Custom content imported from {filename}")
            return True
        except Exception as e:
            logger.error(f"Failed to import custom content: {e}")
            return False