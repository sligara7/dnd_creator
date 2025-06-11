from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from enum import Enum, auto

class SpellLevel(Enum):
    """Enum representing spell levels in D&D"""
    CANTRIP = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9
    # Custom levels could be added for homebrew high-level magic

class CastingTime(Enum):
    """Enum representing spell casting times in D&D"""
    ACTION = "1 action"
    BONUS_ACTION = "1 bonus action"
    REACTION = "1 reaction"
    MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWELVE_HOURS = "12 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    CUSTOM = "custom"  # For special cases

class SpellRange(Enum):
    """Enum representing common spell ranges in D&D"""
    SELF = "self"
    TOUCH = "touch"
    SIGHT = "sight"
    UNLIMITED = "unlimited"
    CUSTOM = "custom"  # For specific distances like 30 feet, 60 feet, etc.

class SpellDuration(Enum):
    """Enum representing spell durations in D&D"""
    INSTANTANEOUS = "instantaneous"
    ONE_ROUND = "1 round"
    ONE_MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    ONE_HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    SEVEN_DAYS = "7 days"
    THIRTY_DAYS = "30 days"
    UNTIL_DISPELLED = "until dispelled"
    CUSTOM = "custom"  # For special durations

class MagicSchool(Enum):
    """Enum representing the schools of magic in D&D"""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration" 
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"
    # The interface allows for custom schools beyond the standard eight

class DamageType(Enum):
    """Enum representing damage types in D&D"""
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing" 
    THUNDER = "thunder"
    # Custom damage types can be added for unique spells

class AreaOfEffect(Enum):
    """Enum representing area of effect shapes in D&D"""
    CONE = "cone"
    CUBE = "cube"
    CYLINDER = "cylinder"
    LINE = "line"
    SPHERE = "sphere"
    EMANATION = "emanation"  # New in 2024 rules
    CUSTOM = "custom"  # For special shapes

class SpellComponent:
    """Class to store information about spell components"""
    
    def __init__(self, verbal: bool = False, somatic: bool = False, material: Optional[str] = None,
                 material_cost: Optional[int] = None, material_consumed: bool = False):
        """
        Initialize spell components.
        
        Per D&D 2024 rules, spells may require:
        - Verbal (V): Speaking mystic words
        - Somatic (S): Performing specific gestures
        - Material (M): Specific physical substances or objects, sometimes with a cost
        
        Args:
            verbal: Whether the spell requires verbal components
            somatic: Whether the spell requires somatic components
            material: Description of material components required
            material_cost: Cost of material components in gold pieces
            material_consumed: Whether material components are consumed when cast
        """
        self.verbal = verbal
        self.somatic = somatic
        self.material = material
        self.material_cost = material_cost
        self.material_consumed = material_consumed

class AbstractSpell(ABC):
    """
    Abstract base class for all D&D spells, following the 2024 edition rules.
    
    This class defines the common attributes and interface that all spells
    must implement, whether official D&D spells or custom creations.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the spell's name.
        
        Returns:
            str: Spell name
        """
        pass
    
    @abstractmethod
    def get_level(self) -> SpellLevel:
        """
        Get the spell's level.
        
        Per D&D 2024 rules, spells range from cantrips (level 0) to level 9.
        
        Returns:
            SpellLevel: Spell level
        """
        pass
    
    @abstractmethod
    def get_school(self) -> MagicSchool:
        """
        Get the spell's school of magic.
        
        Returns:
            MagicSchool: School of magic
        """
        pass
    
    @abstractmethod
    def get_casting_time(self) -> Union[CastingTime, str]:
        """
        Get the spell's casting time.
        
        Returns:
            Union[CastingTime, str]: Casting time
        """
        pass
    
    @abstractmethod
    def get_range(self) -> Union[SpellRange, int, str]:
        """
        Get the spell's range.
        
        Returns:
            Union[SpellRange, int, str]: Range of the spell
        """
        pass
    
    @abstractmethod
    def get_components(self) -> SpellComponent:
        """
        Get the spell's components.
        
        Returns:
            SpellComponent: Components required
        """
        pass
    
    @abstractmethod
    def get_duration(self) -> Union[SpellDuration, str]:
        """
        Get the spell's duration.
        
        Returns:
            Union[SpellDuration, str]: Duration of effect
        """
        pass
    
    @abstractmethod
    def requires_concentration(self) -> bool:
        """
        Check if this spell requires concentration.
        
        Per D&D 2024 rules, concentration spells end if:
        - The caster casts another concentration spell
        - The caster takes damage and fails a Constitution saving throw
        - The caster is incapacitated or killed
        
        Returns:
            bool: True if concentration is required
        """
        pass
    
    @abstractmethod
    def can_be_cast_as_ritual(self) -> bool:
        """
        Check if this spell can be cast as a ritual.
        
        Per D&D 2024 rules, ritual casting:
        - Takes 10 minutes longer than normal casting time
        - Does not consume a spell slot
        - Requires the caster to have the Ritual Casting feature
        - The spell must be prepared/known and have the ritual tag
        
        Returns:
            bool: True if it's a ritual spell
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the spell's description.
        
        Returns:
            str: Full spell description
        """
        pass
    
    @abstractmethod
    def get_higher_level_effect(self, cast_level: int) -> Optional[str]:
        """
        Get the enhanced effect when cast at a higher level.
        
        Per D&D 2024 rules, many spells have increased effects when
        cast using higher-level spell slots.
        
        Args:
            cast_level: The level at which the spell is being cast
            
        Returns:
            Optional[str]: Description of the enhanced effect, None if no enhancement
        """
        pass
    
    @abstractmethod
    def get_classes(self) -> List[str]:
        """
        Get classes that can learn/prepare this spell.
        
        Returns:
            List[str]: List of class names
        """
        pass
    
    @abstractmethod
    def get_damage(self) -> Optional[Dict[str, Any]]:
        """
        Get damage information if the spell deals damage.
        
        Returns:
            Optional[Dict[str, Any]]: Damage details or None
        """
        pass
    
    @abstractmethod
    def get_healing(self) -> Optional[Dict[str, Any]]:
        """
        Get healing information if the spell heals.
        
        Returns:
            Optional[Dict[str, Any]]: Healing details or None
        """
        pass
    
    @abstractmethod
    def get_saving_throw(self) -> Optional[Dict[str, str]]:
        """
        Get saving throw information if the spell requires one.
        
        Returns:
            Optional[Dict[str, str]]: Saving throw details or None
        """
        pass
    
    @abstractmethod
    def get_conditions(self) -> List[Dict[str, Any]]:
        """
        Get conditions that the spell can apply.
        
        Returns:
            List[Dict[str, Any]]: List of conditions
        """
        pass
    
    @abstractmethod
    def get_area_of_effect(self) -> Optional[Dict[str, Any]]:
        """
        Get area of effect if the spell affects an area.
        
        Returns:
            Optional[Dict[str, Any]]: Area details or None
        """
        pass
    
    @abstractmethod
    def cast(self, caster: Any, target: Any = None, cast_level: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Cast the spell.
        
        Args:
            caster: The entity casting the spell
            target: The target of the spell (if any)
            cast_level: The level at which to cast the spell (defaults to spell's level)
            **kwargs: Additional spell-specific parameters
            
        Returns:
            Dict[str, Any]: The result of the spell casting
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the spell to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the spell
        """
        pass


class AbstractSpells(ABC):
    """
    Abstract base class for managing spells in D&D 5e (2024 Edition).
    
    This class provides methods to interact with the spell system, including:
    - Retrieving information about spells
    - Filtering spells based on various criteria
    - Managing spell lists for characters
    - Handling spell casting and effects
    """
    
    @abstractmethod
    def get_all_spells(self) -> List[AbstractSpell]:
        """
        Return a list of all available spells.
        
        Returns:
            List[AbstractSpell]: List of all spells
        """
        pass
    
    @abstractmethod
    def get_spell_details(self, spell_name: str) -> Optional[AbstractSpell]:
        """
        Get detailed information about a spell.
        
        Args:
            spell_name: Name of the spell
            
        Returns:
            Optional[AbstractSpell]: The spell object or None if not found
        """
        pass
    
    @abstractmethod
    def get_spells_by_level(self, level: Union[int, SpellLevel]) -> List[AbstractSpell]:
        """
        Get spells of a specific level.
        
        Args:
            level: Spell level to filter by
            
        Returns:
            List[AbstractSpell]: List of spells at that level
        """
        pass
    
    @abstractmethod
    def get_spells_by_class(self, character_class: str) -> List[AbstractSpell]:
        """
        Get spells available to a specific class.
        
        Per D&D 2024 rules, each class has access to a specific list of spells.
        
        Args:
            character_class: Character class name
            
        Returns:
            List[AbstractSpell]: List of spells available to the class
        """
        pass
    
    @abstractmethod
    def get_spells_by_school(self, school: Union[str, MagicSchool]) -> List[AbstractSpell]:
        """
        Get spells from a specific school of magic.
        
        Args:
            school: School of magic to filter by
            
        Returns:
            List[AbstractSpell]: List of spells from that school
        """
        pass
    
    @abstractmethod
    def filter_spells(self, filters: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Filter spells based on multiple criteria.
        
        Args:
            filters: Dictionary of filter criteria
            
        Returns:
            List[AbstractSpell]: List of filtered spells
        """
        pass
    
    @abstractmethod
    def calculate_spell_save_dc(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell save DC for a character.
        
        Per D&D 2024 rules:
        Spell save DC = 8 + proficiency bonus + spellcasting ability modifier
        
        Args:
            character_data: Character information
            
        Returns:
            int: Calculated spell save DC
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell attack bonus for a character.
        
        Per D&D 2024 rules:
        Spell attack bonus = proficiency bonus + spellcasting ability modifier
        
        Args:
            character_data: Character information
            
        Returns:
            int: Calculated spell attack bonus
        """
        pass
    
    @abstractmethod
    def get_prepared_spells(self, character_data: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Get list of spells a character has prepared.
        
        Per D&D 2024 rules:
        - Prepared casters (like Clerics, Druids) can prepare a number of spells
          equal to their spellcasting ability modifier + their class level
        - Other casters have spells known rather than prepared
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractSpell]: List of prepared spells
        """
        pass
    
    @abstractmethod
    def get_spells_known(self, character_data: Dict[str, Any]) -> List[AbstractSpell]:
        """
        Get list of spells a character knows.
        
        Per D&D 2024 rules:
        - Known casters (like Bards, Sorcerers) know a fixed number of spells
          based on their class and level
        - Prepared casters know all spells on their class list but must prepare a subset
        
        Args:
            character_data: Character information
            
        Returns:
            List[AbstractSpell]: List of known spells
        """
        pass
    
    @abstractmethod
    def get_available_spell_slots(self, character_data: Dict[str, Any]) -> Dict[int, int]:
        """
        Get available spell slots for a character.
        
        Per D&D 2024 rules, spell slots are determined by:
        - Character's class and level
        - Multiclassing uses a combined formula for determining slots
        - Slots are expended when spells are cast and recovered with rests
        
        Args:
            character_data: Character information
            
        Returns:
            Dict[int, int]: Dictionary mapping spell levels to number of slots
        """
        pass
    
    @abstractmethod
    def use_spell_slot(self, character_data: Dict[str, Any], slot_level: int) -> bool:
        """
        Use a spell slot of the specified level.
        
        Per D&D 2024 rules:
        - A spell slot is expended when a spell is cast
        - A higher-level slot can be used to cast a lower-level spell
        - Cantrips don't use spell slots
        
        Args:
            character_data: Character information
            slot_level: Level of slot to use
            
        Returns:
            bool: True if slot was successfully used
        """
        pass
    
    @abstractmethod
    def create_custom_spell(self, spell_data: Dict[str, Any]) -> AbstractSpell:
        """
        Create a custom spell.
        
        This method supports the creation of unique spells beyond standard D&D rules,
        while ensuring they adhere to the basic spell structure.
        
        Args:
            spell_data: Custom spell definition
            
        Returns:
            AbstractSpell: New custom spell instance
        """
        pass
    
    @abstractmethod
    def validate_spell_creation(self, spell_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate a custom spell definition.
        
        Ensures the spell follows the basic structure required by the system,
        while allowing for creative freedom in effects and mechanics.
        
        Args:
            spell_data: Custom spell definition
            
        Returns:
            Tuple[bool, str]: (Is valid, explanation message)
        """
        pass
    
    @abstractmethod
    def validate_spell_casting(self, character_data: Dict[str, Any], spell: AbstractSpell, 
                            slot_level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate if a character can cast a specific spell.
        
        Per D&D 2024 rules, casting requirements include:
        - The spell must be known/prepared
        - The character must have an appropriate spell slot available
        - The character must be able to provide the necessary components
        - The character must not be prevented from casting (e.g., silenced for verbal)
        
        Args:
            character_data: Character information
            spell: The spell to cast
            slot_level: Level at which to cast the spell
            
        Returns:
            Tuple[bool, str]: (True if valid, explanation message)
        """
        pass
    
    @abstractmethod
    def resolve_spell_effect(self, character_data: Dict[str, Any], spell: AbstractSpell,
                          targets: List[Any], slot_level: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Resolve the effect of a spell.
        
        Per D&D 2024 rules, spell resolution may include:
        - Attack rolls (for spell attacks)
        - Saving throws (for spells requiring saves)
        - Damage or healing calculations
        - Condition or status effects
        - Environmental or terrain effects
        
        Args:
            character_data: Character information
            spell: The spell being cast
            targets: Targets of the spell
            slot_level: Level at which the spell is cast
            **kwargs: Additional spell-specific parameters
            
        Returns:
            Dict[str, Any]: Result of the spell effect
        """
        pass