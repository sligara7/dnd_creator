from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple, Set
import math
import random

class SpellcastingType(Enum):
    """Types of spellcasting in D&D 5e (2024 Edition)"""
    NONE = "none"             # No spellcasting ability
    PREPARED = "prepared"     # Prepare spells from a list (Clerics, Wizards, etc.)
    KNOWN = "known"           # Know a fixed set of spells (Bards, Sorcerers, etc.)
    PACT = "pact"             # Warlock's unique spellcasting
    HYBRID = "hybrid"         # Mixed spellcasting types (certain subclasses)

class ClassResource(Enum):
    """Special resources used by different classes"""
    RAGE = "rage"               # Barbarian
    BARDIC_INSPIRATION = "bardic_inspiration"  # Bard
    CHANNEL_DIVINITY = "channel_divinity"  # Cleric, Paladin
    WILD_SHAPE = "wild_shape"   # Druid
    ACTION_SURGE = "action_surge"  # Fighter
    KI = "ki"                   # Monk
    LAY_ON_HANDS = "lay_on_hands"  # Paladin
    FAVORED_FOE = "favored_foe"  # Ranger
    SNEAK_ATTACK = "sneak_attack"  # Rogue
    SORCERY_POINTS = "sorcery_points"  # Sorcerer
    PACT_SLOTS = "pact_slots"   # Warlock
    ARCANE_RECOVERY = "arcane_recovery"  # Wizard

class SubclassType(Enum):
    """Types of subclasses based on when they're chosen"""
    LEVEL_1 = 1   # Chosen at level 1 (Cleric Domains, Sorcerous Origins)
    LEVEL_2 = 2   # Chosen at level 2 (Wizard Schools)
    LEVEL_3 = 3   # Chosen at level 3 (Fighter Martial Archetypes, etc.)

class AbstractCharacterClass(ABC):
    """
    Abstract base class for D&D character classes following the 2024 revised rules.
    
    A character class in D&D defines a character's abilities, strengths, and specialized 
    training. Each class provides unique features, progression paths, and playstyles.
    """
    
    # XP thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Core D&D classes from the 2024 Player's Handbook
    CORE_CLASSES = [
        "Barbarian", "Bard", "Cleric", "Druid", "Fighter", "Monk",
        "Paladin", "Ranger", "Rogue", "Sorcerer", "Warlock", "Wizard"
    ]
    
    def __init__(self, name: str, level: int = 1, xp: int = 0, 
                 hit_die: str = "d8", constitution_modifier: int = 0):
        """
        Initialize a character class.
        
        Args:
            name: Name of the character class (e.g., "Fighter", "Wizard")
            level: Starting class level
            xp: Starting experience points
            hit_die: Hit die used by this class (e.g., "d8", "d10", "d12")
            constitution_modifier: Character's Constitution modifier for HP
        """
        self.name = name
        self.level = level
        self.xp = xp
        self.hit_dice = hit_die
        self.hit_dice_count = level
        self.max_hit_points = 0
        self.constitution_modifier = constitution_modifier
        
        # Class capabilities
        self.proficiencies = {
            "armor": [],
            "weapons": [],
            "tools": [],
            "skills": []
        }
        self.saving_throws = []
        self.features = {}
        self.ability_score_improvements = []
        
        # Spellcasting properties (if applicable)
        self.spellcaster = False
        self.spellcasting_type = SpellcastingType.NONE
        self.spellcasting_ability = None
        self.spell_slots = {}
        self.spells_known = []
        self.spells_prepared = []
        self.cantrips_known = []
        
        # Class resources
        self.resources = {}
        
        # Subclass information
        self.subclass = None
        self.subclass_type = None
        
        # Calculate initial hit points (max hit die + CON mod at level 1)
        self._calculate_initial_hit_points()
    
    def _calculate_initial_hit_points(self) -> int:
        """Calculate initial hit points for level 1"""
        # Get hit die value (d6 -> 6, d8 -> 8, etc.)
        hit_die_value = int(self.hit_dice[1:])
        
        # Level 1 is always maximum hit die
        self.max_hit_points = hit_die_value + self.constitution_modifier
        return self.max_hit_points
    
    def get_proficiency_bonus(self) -> int:
        """
        Calculate proficiency bonus based on level.
        
        Returns:
            int: Proficiency bonus
        """
        return math.ceil(self.level / 4) + 1
    
    def gain_xp(self, amount: int) -> int:
        """
        Add XP and level up if threshold is reached.
        
        Args:
            amount: Amount of XP to add
            
        Returns:
            int: Current level after XP gain
        """
        self.xp += amount
        while self.level < 20 and self.xp >= self.XP_THRESHOLDS[self.level + 1]:
            self.level_up()
        return self.level
    
    def milestone_level_up(self) -> bool:
        """
        Level up based on milestone achievement.
        
        Returns:
            bool: True if leveled up, False if already at max level
        """
        if self.level < 20:
            self.level_up()
            return True
        return False
    
    def calculate_hit_points(self, roll_for_hp: bool = False) -> int:
        """
        Calculate hit points on level up.
        
        Args:
            roll_for_hp: Whether to roll for HP or use the average
            
        Returns:
            int: Amount of HP gained
        """
        # Get hit die value (d6 -> 6, d8 -> 8, etc.)
        hit_die_value = int(self.hit_dice[1:])
        
        if roll_for_hp:
            # Roll for hit points
            new_hp = random.randint(1, hit_die_value)
        else:
            # Take average
            new_hp = math.floor(hit_die_value / 2) + 1
        
        # Add Constitution modifier
        new_hp += self.constitution_modifier
        
        # Minimum 1 hit point gained per level
        new_hp = max(1, new_hp)
        
        self.max_hit_points += new_hp
        return new_hp
    
    def update_constitution(self, new_constitution_modifier: int) -> int:
        """
        Update HP when Constitution changes.
        
        Args:
            new_constitution_modifier: New Constitution modifier
            
        Returns:
            int: HP adjustment made
        """
        if new_constitution_modifier != self.constitution_modifier:
            # Retroactively apply Constitution modifier change to all levels
            hp_adjustment = (new_constitution_modifier - self.constitution_modifier) * self.level
            self.max_hit_points += hp_adjustment
            self.constitution_modifier = new_constitution_modifier
            return hp_adjustment
        return 0
    
    @abstractmethod
    def level_up(self, roll_for_hp: bool = False) -> Dict[str, Any]:
        """
        Increase level and add appropriate features.
        
        Args:
            roll_for_hp: Whether to roll for HP or use the average
            
        Returns:
            Dict[str, Any]: Information about the level up
        """
        pass
    
    @abstractmethod
    def get_class_features(self, level: int) -> Dict[str, Any]:
        """
        Return class features for the given level.
        
        Args:
            level: Level to get features for
            
        Returns:
            Dict[str, Any]: Features available at the specified level
        """
        pass
    
    @abstractmethod
    def get_spellcasting_info(self, level: int) -> Dict[str, Any]:
        """
        Get spellcasting information for the given level.
        
        Args:
            level: Level to get spellcasting info for
            
        Returns:
            Dict[str, Any]: Spellcasting details (slots, etc.)
        """
        pass
    
    @abstractmethod
    def prepare_spells(self, spell_list: List[str]) -> Tuple[bool, List[str]]:
        """
        Prepare spells from the class spell list.
        
        Args:
            spell_list: List of spells to prepare
            
        Returns:
            Tuple[bool, List[str]]: (Success, List of prepared spells)
        """
        pass
    
    @abstractmethod
    def learn_spell(self, spell_name: str) -> bool:
        """
        Learn a new spell.
        
        Args:
            spell_name: Name of the spell to learn
            
        Returns:
            bool: True if successfully learned
        """
        pass
    
    @abstractmethod
    def can_use_feature(self, feature_name: str) -> bool:
        """
        Check if a feature can be used.
        
        Args:
            feature_name: Name of the feature to check
            
        Returns:
            bool: True if the feature can be used
        """
        pass
    
    @abstractmethod
    def use_feature(self, feature_name: str, **kwargs) -> Dict[str, Any]:
        """
        Use a class feature.
        
        Args:
            feature_name: Name of the feature to use
            **kwargs: Additional feature-specific parameters
            
        Returns:
            Dict[str, Any]: Result of using the feature
        """
        pass
    
    @abstractmethod
    def short_rest(self) -> Dict[str, Any]:
        """
        Perform a short rest, restoring certain class resources.
        
        Returns:
            Dict[str, Any]: Resources restored during the rest
        """
        pass
    
    @abstractmethod
    def long_rest(self) -> Dict[str, Any]:
        """
        Perform a long rest, restoring hit points and class resources.
        
        Returns:
            Dict[str, Any]: Resources restored during the rest
        """
        pass
    
    @abstractmethod
    def set_subclass(self, subclass_name: str) -> bool:
        """
        Set the character's subclass.
        
        Args:
            subclass_name: Name of the subclass
            
        Returns:
            bool: True if successfully set
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert class information to dictionary format.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the class
        """
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "hit_dice": self.hit_dice,
            "hit_dice_count": self.hit_dice_count,
            "max_hit_points": self.max_hit_points,
            "proficiencies": self.proficiencies,
            "saving_throws": self.saving_throws,
            "features": self.features,
            "spellcaster": self.spellcaster,
            "spellcasting_type": self.spellcasting_type.value if self.spellcaster else None,
            "spellcasting_ability": self.spellcasting_ability if self.spellcaster else None,
            "subclass": self.subclass,
            "ability_score_improvements": self.ability_score_improvements
        }
    
    def __str__(self) -> str:
        """String representation of the class."""
        result = f"{self.name} (Level {self.level})"
        if self.subclass:
            result += f" - {self.subclass}"
        return result


class AbstractCharacterClasses(ABC):
    """
    Abstract base class for managing character classes in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the class system, including:
    - Retrieving information about classes
    - Managing class features and progression
    - Handling multiclassing rules
    - Supporting subclasses and class options
    """
    
    @abstractmethod
    def get_all_classes(self) -> List[Dict[str, Any]]:
        """
        Return a list of all available classes.
        
        Returns:
            List[Dict[str, Any]]: List of class summaries
        """
        pass
    
    @abstractmethod
    def get_class_details(self, class_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Optional[Dict[str, Any]]: Class details or None if not found
        """
        pass
    
    @abstractmethod
    def get_class_features(self, class_name: str, level: int) -> Dict[str, Any]:
        """
        Get features available to a class at a given level.
        
        Args:
            class_name: Name of the class
            level: Character level
            
        Returns:
            Dict[str, Any]: Features available at the level
        """
        pass
    
    @abstractmethod
    def get_class_progression(self, class_name: str) -> Dict[int, Dict[str, Any]]:
        """
        Get level progression table for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[int, Dict[str, Any]]: Progression table by level
        """
        pass
    
    @abstractmethod
    def get_saving_throw_proficiencies(self, class_name: str) -> List[str]:
        """
        Get saving throw proficiencies for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[str]: Saving throw proficiencies
        """
        pass
    
    @abstractmethod
    def get_starting_equipment(self, class_name: str) -> Dict[str, Any]:
        """
        Get starting equipment options for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[str, Any]: Starting equipment options
        """
        pass
    
    @abstractmethod
    def get_starting_proficiencies(self, class_name: str) -> Dict[str, List[str]]:
        """
        Get starting proficiencies for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[str, List[str]]: Starting proficiencies by category
        """
        pass
    
    @abstractmethod
    def get_class_spellcasting(self, class_name: str) -> Optional[Dict[str, Any]]:
        """
        Get spellcasting details for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Optional[Dict[str, Any]]: Spellcasting information or None if not a spellcaster
        """
        pass
    
    @abstractmethod
    def get_all_subclasses(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Get all available subclasses for a class.
        
        Args:
            class_name: Name of the class
            
        Returns:
            List[Dict[str, Any]]: Available subclasses
        """
        pass
    
    @abstractmethod
    def get_subclass_details(self, class_name: str, subclass_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details about a specific subclass.
        
        Args:
            class_name: Name of the class
            subclass_name: Name of the subclass
            
        Returns:
            Optional[Dict[str, Any]]: Subclass details or None if not found
        """
        pass
    
    @abstractmethod
    def get_multiclass_requirements(self, class_name: str) -> Dict[str, int]:
        """
        Get ability score requirements for multiclassing.
        
        Args:
            class_name: Name of the class
            
        Returns:
            Dict[str, int]: Minimum ability scores required
        """
        pass
    
    @abstractmethod
    def can_multiclass(self, current_class: str, new_class: str, ability_scores: Dict[str, int]) -> Tuple[bool, str]:
        """
        Check if a character can multiclass into a new class.
        
        Args:
            current_class: Current class name
            new_class: New class name to add
            ability_scores: Character's ability scores
            
        Returns:
            Tuple[bool, str]: (Can multiclass, explanation)
        """
        pass
    
    @abstractmethod
    def create_class_instance(self, class_name: str, level: int = 1, 
                           subclass_name: Optional[str] = None) -> Optional[AbstractCharacterClass]:
        """
        Create an instance of a character class.
        
        Args:
            class_name: Name of the class to create
            level: Starting level
            subclass_name: Optional subclass to use
            
        Returns:
            Optional[AbstractCharacterClass]: Class instance or None if invalid
        """
        pass
    
    @abstractmethod
    def get_class_resources(self, class_name: str, level: int) -> Dict[str, Any]:
        """
        Get class-specific resources at a given level.
        
        Args:
            class_name: Name of the class
            level: Character level
            
        Returns:
            Dict[str, Any]: Available resources
        """
        pass
    
    def class_exists(self, class_name: str) -> bool:
        """
        Check if a class exists.
        
        Args:
            class_name: Name of the class
            
        Returns:
            bool: True if class exists
        """
        return self.get_class_details(class_name) is not None
    
    def subclass_exists(self, class_name: str, subclass_name: str) -> bool:
        """
        Check if a subclass exists for a class.
        
        Args:
            class_name: Name of the class
            subclass_name: Name of the subclass
            
        Returns:
            bool: True if subclass exists
        """
        return self.get_subclass_details(class_name, subclass_name) is not None