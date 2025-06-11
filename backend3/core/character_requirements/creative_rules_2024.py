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