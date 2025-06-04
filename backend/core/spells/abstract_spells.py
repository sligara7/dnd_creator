from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union, Tuple, Set
from enum import Enum

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
        self.verbal = verbal
        self.somatic = somatic
        self.material = material
        self.material_cost = material_cost
        self.material_consumed = material_consumed
    
    def __str__(self):
        components = []
        if self.verbal:
            components.append("V")
        if self.somatic:
            components.append("S")
        if self.material:
            mat = "M"
            if self.material_cost:
                mat += f" ({self.material} worth {self.material_cost} gp"
                if self.material_consumed:
                    mat += ", which the spell consumes"
                mat += ")"
            else:
                mat += f" ({self.material})"
            components.append(mat)
        return ", ".join(components)

class AbstractSpell(ABC):
    """
    Abstract base class for all D&D spells, following the 2024 edition rules.
    
    This class defines the common attributes and interface for all spells
    in the Dungeons & Dragons game.
    """
    
    def __init__(self, name: str, level: Union[int, SpellLevel], school: Union[str, MagicSchool], 
                 casting_time: Union[str, CastingTime], spell_range: Union[str, int, SpellRange],
                 components: SpellComponent, duration: Union[str, SpellDuration],
                 concentration: bool = False, ritual: bool = False):
        """
        Initialize a new spell.
        
        Args:
            name: The name of the spell
            level: Spell level (0 for cantrips)
            school: The school of magic the spell belongs to
            casting_time: How long it takes to cast the spell
            spell_range: How far the spell can reach
            components: The components required to cast the spell (V, S, M)
            duration: How long the spell's effects last
            concentration: Whether the spell requires concentration
            ritual: Whether the spell can be cast as a ritual
        """
        self.name = name
        
        # Convert level to SpellLevel enum if it's an int
        if isinstance(level, int):
            try:
                self.level = SpellLevel(level)
            except ValueError:
                raise ValueError(f"Invalid spell level: {level}")
        else:
            self.level = level
            
        # Convert school to MagicSchool enum if it's a string
        if isinstance(school, str):
            try:
                self.school = MagicSchool(school.lower())
            except ValueError:
                raise ValueError(f"Invalid magic school: {school}")
        else:
            self.school = school
            
        # Convert casting_time to CastingTime enum if it's a string
        if isinstance(casting_time, str):
            if casting_time in [e.value for e in CastingTime]:
                self.casting_time = CastingTime(casting_time)
            else:
                self.casting_time = CastingTime.CUSTOM
                self.custom_casting_time = casting_time
        else:
            self.casting_time = casting_time
            
        # Handle spell range
        if isinstance(spell_range, str):
            if spell_range in [e.value for e in SpellRange]:
                self.range = SpellRange(spell_range)
                self.range_value = 0
            else:
                self.range = SpellRange.CUSTOM
                self.range_value = spell_range
        elif isinstance(spell_range, int):
            self.range = SpellRange.CUSTOM
            self.range_value = spell_range
        else:
            self.range = spell_range
            self.range_value = 0
            
        # Components
        self.components = components
        
        # Duration and concentration
        if isinstance(duration, str):
            if duration in [e.value for e in SpellDuration]:
                self.duration = SpellDuration(duration)
                self.custom_duration = None
            else:
                self.duration = SpellDuration.CUSTOM
                self.custom_duration = duration
        else:
            self.duration = duration
            self.custom_duration = None
            
        self.concentration = concentration
        self.ritual = ritual
        
        # Additional properties
        self.description = ""
        self.higher_level_description = ""
        self.classes = []
        self.damage = {}  # Dict with keys like 'dice', 'type', 'bonus'
        self.healing = {}  # Dict with keys like 'dice', 'bonus'
        self.saving_throw = None  # Type of saving throw required
        self.conditions = []  # Conditions that might be applied
        self.area_of_effect = None  # Dict with keys like 'type', 'size'
    
    def __str__(self):
        """Return a string representation of the spell."""
        level_str = "Cantrip" if self.level == SpellLevel.CANTRIP else f"Level {self.level.value}"
        ritual_str = " (ritual)" if self.ritual else ""
        conc_str = "Concentration, " if self.concentration else ""
        
        # Format range
        if self.range == SpellRange.CUSTOM:
            range_str = f"{self.range_value} feet"
        else:
            range_str = self.range.value.capitalize()
        
        # Format duration
        if self.duration == SpellDuration.CUSTOM:
            duration_str = self.custom_duration
        else:
            duration_str = self.duration.value.capitalize()
        
        return (
            f"{self.name}\n"
            f"{level_str} {self.school.value.capitalize()}{ritual_str}\n"
            f"Casting Time: {self.casting_time.value if hasattr(self.casting_time, 'value') else self.custom_casting_time}\n"
            f"Range: {range_str}\n"
            f"Components: {self.components}\n"
            f"Duration: {conc_str}{duration_str}\n\n"
            f"{self.description}"
        )
    
    def is_cantrip(self) -> bool:
        """Check if this spell is a cantrip."""
        return self.level == SpellLevel.CANTRIP
    
    def can_be_cast_as_ritual(self) -> bool:
        """Check if this spell can be cast as a ritual."""
        return self.ritual
    
    def requires_concentration(self) -> bool:
        """Check if this spell requires concentration."""
        return self.concentration
    
    def get_higher_level_effect(self, cast_level: int) -> Optional[str]:
        """
        Get the enhanced effect when cast at a higher level.
        
        Args:
            cast_level: The level at which the spell is being cast
            
        Returns:
            Optional[str]: Description of the enhanced effect, None if no enhancement
        """
        if cast_level <= self.level.value or not self.higher_level_description:
            return None
        return self.higher_level_description
    
    @abstractmethod
    def cast(self, caster: Any, target: Any = None, cast_level: Optional[int] = None, **kwargs) -> Dict[str, Any]:
        """
        Cast the spell.
        
        This abstract method must be implemented by all concrete spell classes.
        
        Args:
            caster: The entity casting the spell
            target: The target of the spell (if any)
            cast_level: The level at which to cast the spell (defaults to spell's level)
            **kwargs: Additional spell-specific parameters
            
        Returns:
            Dict[str, Any]: The result of the spell casting
        """
        pass
    
    def set_description(self, description: str, higher_level: Optional[str] = None) -> None:
        """
        Set the spell description.
        
        Args:
            description: The main description of the spell
            higher_level: Optional description of effects when cast at higher levels
        """
        self.description = description
        if higher_level:
            self.higher_level_description = higher_level
    
    def add_damage(self, dice: str, damage_type: Union[str, DamageType], bonus: int = 0) -> None:
        """
        Add damage information to the spell.
        
        Args:
            dice: The dice expression (e.g., "2d6")
            damage_type: The type of damage
            bonus: Any additional damage bonus
        """
        if isinstance(damage_type, str):
            try:
                damage_type = DamageType(damage_type.lower())
            except ValueError:
                raise ValueError(f"Invalid damage type: {damage_type}")
                
        self.damage = {
            'dice': dice,
            'type': damage_type,
            'bonus': bonus
        }
    
    def add_healing(self, dice: str, bonus: int = 0) -> None:
        """
        Add healing information to the spell.
        
        Args:
            dice: The dice expression (e.g., "2d8")
            bonus: Any additional healing bonus
        """
        self.healing = {
            'dice': dice,
            'bonus': bonus
        }
    
    def add_saving_throw(self, ability: str, effect_on_save: str = "half", dc_ability: Optional[str] = None) -> None:
        """
        Add saving throw information to the spell.
        
        Args:
            ability: The ability used for the saving throw (e.g., "dexterity")
            effect_on_save: What happens on a successful save (e.g., "half", "none")
            dc_ability: The caster ability used to calculate the DC (defaults to spellcasting ability)
        """
        self.saving_throw = {
            'ability': ability,
            'effect_on_save': effect_on_save,
            'dc_ability': dc_ability
        }
    
    def set_area_of_effect(self, shape: Union[str, AreaOfEffect], size: int) -> None:
        """
        Set the area of effect for the spell.
        
        Args:
            shape: The shape of the area (cone, cube, cylinder, line, sphere, emanation)
            size: The size of the area in feet
        """
        if isinstance(shape, str):
            try:
                shape = AreaOfEffect(shape.lower())
            except ValueError:
                raise ValueError(f"Invalid area of effect shape: {shape}")
                
        self.area_of_effect = {
            'shape': shape,
            'size': size
        }
    
    def add_condition(self, condition: str, duration: Optional[str] = None) -> None:
        """
        Add a condition that the spell can apply.
        
        Args:
            condition: The condition name (e.g., "charmed", "frightened")
            duration: How long the condition lasts
        """
        self.conditions.append({
            'name': condition,
            'duration': duration
        })
    
    def add_class(self, character_class: str) -> None:
        """
        Add a class that can use this spell.
        
        Args:
            character_class: The name of the class
        """
        if character_class not in self.classes:
            self.classes.append(character_class)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the spell to a dictionary for serialization.
        
        Returns:
            Dict[str, Any]: A dictionary representation of the spell
        """
        return {
            'name': self.name,
            'level': self.level.value,
            'school': self.school.value,
            'casting_time': self.casting_time.value if hasattr(self.casting_time, 'value') else self.custom_casting_time,
            'range': self.range.value if self.range != SpellRange.CUSTOM else f"{self.range_value} feet",
            'components': {
                'verbal': self.components.verbal,
                'somatic': self.components.somatic,
                'material': self.components.material,
                'material_cost': self.components.material_cost,
                'material_consumed': self.components.material_consumed
            },
            'duration': self.duration.value if self.duration != SpellDuration.CUSTOM else self.custom_duration,
            'concentration': self.concentration,
            'ritual': self.ritual,
            'description': self.description,
            'higher_level': self.higher_level_description,
            'classes': self.classes,
            'damage': self.damage,
            'healing': self.healing,
            'saving_throw': self.saving_throw,
            'conditions': self.conditions,
            'area_of_effect': self.area_of_effect
        }


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
    def calculate_spell_save_dc(self, character_data: Dict[str, Any], spell: AbstractSpell) -> int:
        """
        Calculate spell save DC for a character.
        
        Args:
            character_data: Character information
            spell: The spell being cast
            
        Returns:
            int: Calculated spell save DC
        """
        pass
    
    @abstractmethod
    def calculate_spell_attack_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate spell attack bonus for a character.
        
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
        
        Args:
            spell_data: Custom spell definition
            
        Returns:
            AbstractSpell: New custom spell instance
        """
        pass
    
    @abstractmethod
    def validate_spell_casting(self, character_data: Dict[str, Any], spell: AbstractSpell, 
                            slot_level: Optional[int] = None) -> Tuple[bool, str]:
        """
        Validate if a character can cast a specific spell.
        
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
    
    def spell_exists(self, spell_name: str) -> bool:
        """
        Check if a spell exists.
        
        Args:
            spell_name: Name of the spell
            
        Returns:
            bool: True if spell exists, False otherwise
        """
        return self.get_spell_details(spell_name) is not None