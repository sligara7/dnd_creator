from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union, Any, Tuple, Set

class SpellcastingType(Enum):
    """Types of spellcasting in D&D 5e (2024 Edition)"""
    NONE = "none"             # No spellcasting ability
    PREPARED = "prepared"     # Prepare spells from a list (Clerics, Wizards, etc.)
    KNOWN = "known"           # Know a fixed set of spells (Bards, Sorcerers, etc.)
    PACT = "pact"             # Warlock's unique spellcasting
    HYBRID = "hybrid"         # Mixed spellcasting types (certain subclasses)

class ClassResource(Enum):
    """Special resources used by different classes"""
    # Core class resources (extendable for custom classes)
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
    # Custom resources can be added as needed

class SubclassType(Enum):
    """Types of subclasses based on when they're chosen"""
    LEVEL_1 = 1   # Chosen at level 1 (Cleric Domains, Sorcerous Origins)
    LEVEL_2 = 2   # Chosen at level 2 (Wizard Schools)
    LEVEL_3 = 3   # Chosen at level 3 (Fighter Martial Archetypes, etc.)
    # Custom subclass levels can be defined as needed

class AbstractCharacterClass(ABC):
    """
    Abstract base class defining the contract for character classes in D&D 5e (2024 Edition).
    
    This interface supports both official D&D classes and custom classes,
    enforcing the core rules while allowing creative freedom.
    """
    
    # XP thresholds for each level according to 2024 rules
    XP_THRESHOLDS = {
        1: 0, 2: 300, 3: 900, 4: 2700, 5: 6500, 6: 14000, 7: 23000, 8: 34000,
        9: 48000, 10: 64000, 11: 85000, 12: 100000, 13: 120000, 14: 140000,
        15: 165000, 16: 195000, 17: 225000, 18: 265000, 19: 305000, 20: 355000
    }
    
    # Maximum level in D&D 5e
    MAX_LEVEL = 20
    
    @abstractmethod
    def get_hit_die(self) -> str:
        """
        Get the hit die type for this class (d6, d8, d10, or d12).
        
        Returns:
            str: Hit die (e.g., "d8")
        """
        pass
    
    @abstractmethod
    def get_proficiency_bonus(self, level: int) -> int:
        """
        Get proficiency bonus based on level.
        
        Per 2024 rules:
        - Levels 1-4: +2
        - Levels 5-8: +3
        - Levels 9-12: +4
        - Levels 13-16: +5
        - Levels 17-20: +6
        
        Args:
            level: Character level
            
        Returns:
            int: Proficiency bonus
        """
        pass
    
    @abstractmethod
    def get_saving_throw_proficiencies(self) -> List[str]:
        """
        Get saving throw proficiencies (each class gets 2).
        
        Returns:
            List[str]: List of ability scores with proficient saving throws
        """
        pass
    
    @abstractmethod
    def get_armor_proficiencies(self) -> List[str]:
        """
        Get armor proficiencies for this class.
        
        Returns:
            List[str]: Armor proficiencies
        """
        pass
    
    @abstractmethod
    def get_weapon_proficiencies(self) -> List[str]:
        """
        Get weapon proficiencies for this class.
        
        Returns:
            List[str]: Weapon proficiencies
        """
        pass
    
    @abstractmethod
    def get_tool_proficiencies(self) -> List[str]:
        """
        Get tool proficiencies for this class.
        
        Returns:
            List[str]: Tool proficiencies
        """
        pass
    
    @abstractmethod
    def get_skill_choices(self) -> Tuple[List[str], int]:
        """
        Get available skills and number of choices for this class.
        
        Returns:
            Tuple[List[str], int]: (Available skills, number to choose)
        """
        pass
    
    @abstractmethod
    def get_starting_equipment(self) -> Dict[str, Any]:
        """
        Get starting equipment options.
        
        Returns:
            Dict[str, Any]: Starting equipment choices
        """
        pass
    
    @abstractmethod
    def get_features_by_level(self, level: int) -> Dict[str, Any]:
        """
        Get class features gained at a specific level.
        
        Args:
            level: Class level
            
        Returns:
            Dict[str, Any]: Features gained at that level
        """
        pass
    
    @abstractmethod
    def get_ability_score_improvement_levels(self) -> List[int]:
        """
        Get levels at which Ability Score Improvements are gained.
        
        Per 2024 rules, standard ASI levels are 4, 8, 12, 16, and 19.
        
        Returns:
            List[int]: Levels with ASIs
        """
        pass
    
    @abstractmethod
    def get_spellcasting_ability(self) -> Optional[str]:
        """
        Get the spellcasting ability for this class, if any.
        
        Returns:
            Optional[str]: Ability used for spellcasting or None
        """
        pass
    
    @abstractmethod
    def get_spellcasting_type(self) -> SpellcastingType:
        """
        Get the type of spellcasting this class uses.
        
        Returns:
            SpellcastingType: Spellcasting type
        """
        pass
    
    @abstractmethod
    def get_spell_slots_by_level(self, class_level: int) -> Dict[int, int]:
        """
        Get available spell slots by spell level at a given class level.
        
        Args:
            class_level: Level in this class
            
        Returns:
            Dict[int, int]: {spell_level: num_slots}
        """
        pass
    
    @abstractmethod
    def get_cantrips_known(self, class_level: int) -> int:
        """
        Get number of cantrips known at a given level.
        
        Args:
            class_level: Level in this class
            
        Returns:
            int: Number of cantrips known
        """
        pass
    
    @abstractmethod
    def get_spells_known(self, class_level: int, ability_modifier: int = 0) -> int:
        """
        Get number of spells known or prepared at a given level.
        
        For prepared casters, this often includes ability modifier.
        
        Args:
            class_level: Level in this class
            ability_modifier: Spellcasting ability modifier
            
        Returns:
            int: Number of spells known/prepared
        """
        pass
    
    @abstractmethod
    def get_subclass_type(self) -> SubclassType:
        """
        Get when this class chooses a subclass.
        
        Returns:
            SubclassType: When subclass is chosen
        """
        pass
    
    @abstractmethod
    def get_multiclass_requirements(self) -> Dict[str, int]:
        """
        Get ability score requirements for multiclassing into this class.
        
        Returns:
            Dict[str, int]: Minimum scores needed {ability: min_score}
        """
        pass
    
    @abstractmethod
    def get_multiclass_proficiencies(self) -> Dict[str, List[str]]:
        """
        Get proficiencies gained when multiclassing into this class.
        
        Returns:
            Dict[str, List[str]]: Proficiencies by category
        """
        pass
    
    @abstractmethod
    def get_class_resources(self, level: int) -> Dict[str, Any]:
        """
        Get class-specific resources at a given level.
        
        Args:
            level: Class level
            
        Returns:
            Dict[str, Any]: Resources and their values/uses
        """
        pass

    @abstractmethod
    def get_multiclass_requirements(self) -> Dict[str, int]:
        """
        Get ability score requirements for multiclassing into this class.
        
        Returns:
            Dict[str, int]: Minimum scores needed {ability: min_score}
        """
        pass

from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from ..entities.character import Character

@dataclass
class ClassFeature:
    """Value object for class features."""
    name: str
    description: str
    level_acquired: int
    feature_type: str  # "passive", "active", "resource"
    uses_per_rest: Optional[str] = None  # "short", "long", None

class AbstractCharacterClass(ABC):
    """
    Abstract base class defining the contract for all D&D character classes.
    
    This ensures that custom classes follow D&D rules while allowing creative flexibility.
    Enforces strict rules for core mechanics, flexible implementation for flavor.
    """
    
    @property
    @abstractmethod
    def class_name(self) -> str:
        """The official name of the class."""
        pass
    
    @property
    @abstractmethod
    def hit_die(self) -> int:
        """Hit die size (d6, d8, d10, d12)."""
        pass
    
    @property
    @abstractmethod
    def primary_ability(self) -> List[str]:
        """Primary ability scores for this class."""
        pass
    
    @property
    @abstractmethod
    def saving_throw_proficiencies(self) -> List[str]:
        """Saving throw proficiencies granted by this class."""
        pass
    
    @abstractmethod
    def get_class_features(self, level: int) -> List[ClassFeature]:
        """
        Get all class features available at the specified level.
        
        Args:
            level: Class level to check
            
        Returns:
            List of ClassFeature objects
        """
        pass
    
    @abstractmethod
    def get_spellcasting_progression(self, level: int) -> Optional[Dict[str, Any]]:
        """
        Get spellcasting progression if this class has spellcasting.
        
        Args:
            level: Class level
            
        Returns:
            Spellcasting data or None if not a spellcaster
        """
        pass
    
    @abstractmethod
    def validate_multiclass_prerequisites(self, character: Character) -> List[str]:
        """
        Validate prerequisites for multiclassing into this class.
        
        Args:
            character: Character attempting to multiclass
            
        Returns:
            List of validation errors (empty if valid)
        """
        pass
    
    def get_proficiency_bonus(self, level: int) -> int:
        """Calculate proficiency bonus for level (standardized across all classes)."""
        if level >= 17:
            return 6
        elif level >= 13:
            return 5
        elif level >= 9:
            return 4
        elif level >= 5:
            return 3
        else:
            return 2
    
    def calculate_hit_points_for_level(self, level: int, constitution_modifier: int, 
                                     method: str = "average") -> int:
        """Calculate hit points for this class level."""
        if level == 1:
            return self.hit_die + constitution_modifier
        
        if method == "average":
            return (self.hit_die // 2) + 1 + constitution_modifier
        elif method == "max":
            return self.hit_die + constitution_modifier
        else:  # Roll
            # Would integrate with dice rolling system
            return (self.hit_die // 2) + 1 + constitution_modifier  # Default to average

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend5/core/abstractions/species.py
class AbstractSpecies(ABC):
    """Abstract base class for all character species."""
    
    @property
    @abstractmethod
    def species_name(self) -> str:
        """Official species name."""
        pass
    
    @property
    @abstractmethod
    def size(self) -> str:
        """Creature size (Tiny, Small, Medium, Large, etc.)."""
        pass
    
    @property
    @abstractmethod
    def speed(self) -> Dict[str, int]:
        """Movement speeds (walking, flying, swimming, etc.)."""
        pass
    
    @abstractmethod
    def get_ability_score_increases(self) -> Dict[str, int]:
        """Ability score increases granted by this species."""
        pass
    
    @abstractmethod
    def get_species_traits(self) -> List[Dict[str, Any]]:
        """Special traits granted by this species."""
        pass
    
    @abstractmethod
    def get_proficiencies(self) -> Dict[str, List[str]]:
        """Proficiencies granted by species."""
        pass
    
    def get_languages(self) -> List[str]:
        """Languages known by this species (can be overridden)."""
        return ["Common"]

# filepath: /home/ajs7/dnd_tools/dnd_char_creator/backend5/core/abstractions/equipment.py
class AbstractWeapon(ABC):
    """Abstract base class for weapons."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def damage_dice(self) -> str:
        pass
    
    @property
    @abstractmethod
    def damage_type(self) -> str:
        pass
    
    @property
    @abstractmethod
    def weapon_type(self) -> str:  # "simple", "martial"
        pass
    
    @property
    @abstractmethod
    def properties(self) -> List[str]:
        """Weapon properties (finesse, reach, etc.)."""
        pass
    
    @abstractmethod
    def get_attack_bonus(self, character: Character) -> int:
        """Calculate attack bonus for this weapon with given character."""
        pass

class AbstractArmor(ABC):
    """Abstract base class for armor."""
    
    @property
    @abstractmethod
    def name(self) -> str:
        pass
    
    @property
    @abstractmethod
    def armor_class_base(self) -> int:
        pass
    
    @property
    @abstractmethod
    def armor_type(self) -> str:  # "light", "medium", "heavy", "shield"
        pass
    
    @abstractmethod
    def calculate_armor_class(self, character: Character) -> int:
        """Calculate AC for this armor with given character."""
        pass