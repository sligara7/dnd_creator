from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple

class EquipmentCategory(Enum):
    """Official equipment categories in D&D 5e (2024 Edition)."""
    WEAPON = auto()
    ARMOR = auto()
    ADVENTURING_GEAR = auto()
    TOOL = auto()
    MOUNT = auto()
    VEHICLE = auto()
    TRADE_GOOD = auto()
    MAGIC_ITEM = auto()
    # Additional categories can be created for custom equipment

class WeaponType(Enum):
    """Official weapon types in D&D 5e (2024 Edition)."""
    SIMPLE_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_MELEE = auto()
    MARTIAL_RANGED = auto()
    # Additional weapon types can be created for custom equipment

class ArmorType(Enum):
    """Official armor types in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()
    # Additional armor types can be created for custom equipment

class DamageType(Enum):
    """Official damage types in D&D 5e (2024 Edition)."""
    ACID = auto()
    BLUDGEONING = auto()
    COLD = auto()
    FIRE = auto()
    FORCE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    PIERCING = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    SLASHING = auto()
    THUNDER = auto()
    # Additional damage types can be created for custom equipment

class WeaponProperty(Enum):
    """Official weapon properties in D&D 5e (2024 Edition)."""
    AMMUNITION = auto()
    FINESSE = auto()
    HEAVY = auto()
    LIGHT = auto()
    LOADING = auto()
    RANGE = auto()
    REACH = auto()
    SPECIAL = auto()
    THROWN = auto()
    TWO_HANDED = auto()
    VERSATILE = auto()
    # Additional weapon properties can be created for custom equipment

class Currency(Enum):
    """Official currency in D&D 5e (2024 Edition)."""
    CP = auto()  # Copper piece (100 CP = 1 GP)
    SP = auto()  # Silver piece (10 SP = 1 GP)
    EP = auto()  # Electrum piece (2 EP = 1 GP)
    GP = auto()  # Gold piece (base unit)
    PP = auto()  # Platinum piece (1 PP = 10 GP)
    # Additional currencies can be created for custom settings

class AbstractEquipment(ABC):
    """
    Abstract base class defining the contract for equipment in D&D 5e (2024 Edition).
    
    This interface supports both official D&D equipment and custom creations.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Get the equipment's name.
        
        Returns:
            str: Equipment name
        """
        pass
        
    @abstractmethod
    def get_category(self) -> EquipmentCategory:
        """
        Get the equipment's category.
        
        Returns:
            EquipmentCategory: Equipment category
        """
        pass
        
    @abstractmethod
    def get_cost(self) -> Dict[Currency, int]:
        """
        Get the equipment's cost in different currencies.
        
        Returns:
            Dict[Currency, int]: Cost in various currencies
        """
        pass
        
    @abstractmethod
    def get_weight(self) -> float:
        """
        Get the equipment's weight in pounds.
        
        Returns:
            float: Weight in pounds
        """
        pass
        
    @abstractmethod
    def get_description(self) -> str:
        """
        Get the equipment's description.
        
        Returns:
            str: Equipment description
        """
        pass
        
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the equipment to a dictionary representation.
        
        Returns:
            Dict[str, Any]: Dictionary representation of the equipment
        """
        pass


class AbstractWeapon(AbstractEquipment):
    """
    Abstract base class defining the contract for weapons in D&D 5e (2024 Edition).
    
    This interface supports both official D&D weapons and custom creations.
    """
    
    @abstractmethod
    def get_weapon_type(self) -> WeaponType:
        """
        Get the weapon's type.
        
        Returns:
            WeaponType: Type of weapon
        """
        pass
        
    @abstractmethod
    def get_damage_dice(self) -> str:
        """
        Get the weapon's damage dice expression.
        
        Returns:
            str: Damage dice (e.g., "1d8")
        """
        pass
        
    @abstractmethod
    def get_damage_type(self) -> DamageType:
        """
        Get the weapon's damage type.
        
        Returns:
            DamageType: Type of damage dealt
        """
        pass
        
    @abstractmethod
    def get_properties(self) -> List[WeaponProperty]:
        """
        Get the weapon's properties.
        
        Returns:
            List[WeaponProperty]: Weapon properties
        """
        pass
        
    @abstractmethod
    def get_range(self) -> Tuple[int, int]:
        """
        Get the weapon's range (for ranged weapons).
        
        Returns:
            Tuple[int, int]: (Normal range, Maximum range)
        """
        pass
        
    @abstractmethod
    def is_melee(self) -> bool:
        """
        Check if the weapon is melee.
        
        Returns:
            bool: True if melee, False if ranged
        """
        pass
        
    @abstractmethod
    def is_martial(self) -> bool:
        """
        Check if the weapon is martial.
        
        Returns:
            bool: True if martial, False if simple
        """
        pass
        
    @abstractmethod
    def calculate_damage(self, ability_modifier: int, is_versatile: bool = False) -> Tuple[str, int]:
        """
        Calculate weapon damage with ability modifier.
        
        Per D&D 2024 rules:
        - Melee weapons typically add Strength modifier to damage
        - Ranged weapons typically add Dexterity modifier to damage
        - Finesse weapons can use either Strength or Dexterity
        - Versatile weapons deal different damage when wielded with two hands
        
        Args:
            ability_modifier: Relevant ability modifier
            is_versatile: If using versatile weapon with two hands
            
        Returns:
            Tuple[str, int]: (Damage dice expression, Fixed damage bonus)
        """
        pass


class AbstractArmor(AbstractEquipment):
    """
    Abstract base class defining the contract for armor in D&D 5e (2024 Edition).
    
    This interface supports both official D&D armor and custom creations.
    """
    
    @abstractmethod
    def get_armor_type(self) -> ArmorType:
        """
        Get the armor's type.
        
        Returns:
            ArmorType: Type of armor
        """
        pass
        
    @abstractmethod
    def get_base_ac(self) -> int:
        """
        Get the armor's base AC.
        
        Returns:
            int: Base armor class
        """
        pass
        
    @abstractmethod
    def get_strength_requirement(self) -> int:
        """
        Get the armor's minimum strength requirement.
        
        Returns:
            int: Minimum strength required (0 if none)
        """
        pass
        
    @abstractmethod
    def has_stealth_disadvantage(self) -> bool:
        """
        Check if the armor imposes disadvantage on stealth checks.
        
        Returns:
            bool: True if disadvantage, False otherwise
        """
        pass
        
    @abstractmethod
    def get_max_dex_bonus(self) -> Optional[int]:
        """
        Get the maximum dexterity bonus allowed by the armor.
        
        Returns:
            Optional[int]: Maximum dexterity bonus (None if unlimited)
        """
        pass
        
    @abstractmethod
    def calculate_ac(self, dexterity_modifier: int) -> int:
        """
        Calculate total AC with dexterity modifier.
        
        Per D&D 2024 rules:
        - Light armor: AC + full Dexterity modifier
        - Medium armor: AC + Dexterity modifier (max +2)
        - Heavy armor: AC (no Dexterity modifier)
        - Shields: +2 AC
        
        Args:
            dexterity_modifier: Character's dexterity modifier
            
        Returns:
            int: Total armor class
        """
        pass


class AbstractEquipmentManager(ABC):
    """
    Abstract base class for managing equipment in D&D 5e (2024 Edition).
    
    This interface supports working with collections of equipment items.
    """
    
    @abstractmethod
    def get_all_weapons(self) -> Dict[str, AbstractWeapon]:
        """
        Get all available weapons.
        
        Returns:
            Dict[str, AbstractWeapon]: Dictionary of weapons by ID
        """
        pass
        
    @abstractmethod
    def get_all_armor(self) -> Dict[str, AbstractArmor]:
        """
        Get all available armor.
        
        Returns:
            Dict[str, AbstractArmor]: Dictionary of armor by ID
        """
        pass
        
    @abstractmethod
    def get_equipment_by_category(self, category: EquipmentCategory) -> Dict[str, AbstractEquipment]:
        """
        Get equipment by category.
        
        Args:
            category: Equipment category
            
        Returns:
            Dict[str, AbstractEquipment]: Dictionary of equipment by ID
        """
        pass
        
    @abstractmethod
    def get_starting_equipment_options(self, character_class: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get starting equipment options for a character class.
        
        Per D&D 2024 rules, each class has specific starting equipment options.
        
        Args:
            character_class: Character class name
            
        Returns:
            Dict[str, List[Dict[str, Any]]]: Starting equipment options
        """
        pass
        
    @abstractmethod
    def calculate_carrying_capacity(self, strength_score: int, size_multiplier: float = 1.0) -> Dict[str, float]:
        """
        Calculate carrying capacity based on strength.
        
        Per D&D 2024 rules:
        - Carrying capacity = strength score × 15 (in pounds)
        - Push/drag/lift = strength score × 30 (in pounds)
        - Size modifiers: Tiny ×0.5, Small ×1, Medium ×1, Large ×2, etc.
        
        Args:
            strength_score: Character's strength score
            size_multiplier: Multiplier based on creature size
            
        Returns:
            Dict[str, float]: Carrying capacity values
        """
        pass
        
    @abstractmethod
    def create_custom_equipment(self, equipment_data: Dict[str, Any]) -> AbstractEquipment:
        """
        Create a custom equipment item from data.
        
        Args:
            equipment_data: Equipment specifications
            
        Returns:
            AbstractEquipment: Custom equipment instance
        """
        pass