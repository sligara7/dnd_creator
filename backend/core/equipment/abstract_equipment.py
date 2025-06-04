from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import Dict, List, Optional, Union, Any, Tuple

class EquipmentCategory(Enum):
    """Enumeration of equipment categories in D&D 5e (2024 Edition)."""
    WEAPON = auto()
    ARMOR = auto()
    ADVENTURING_GEAR = auto()
    TOOL = auto()
    MOUNT = auto()
    VEHICLE = auto()
    TRADE_GOOD = auto()
    MAGIC_ITEM = auto()

class WeaponType(Enum):
    """Enumeration of weapon types in D&D 5e (2024 Edition)."""
    SIMPLE_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_MELEE = auto()
    MARTIAL_RANGED = auto()

class ArmorType(Enum):
    """Enumeration of armor types in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()

class DamageType(Enum):
    """Enumeration of damage types in D&D 5e (2024 Edition)."""
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

class WeaponProperty(Enum):
    """Enumeration of weapon properties in D&D 5e (2024 Edition)."""
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

class Currency(Enum):
    """Enumeration of currency in D&D 5e."""
    CP = auto()  # Copper
    SP = auto()  # Silver
    EP = auto()  # Electrum
    GP = auto()  # Gold
    PP = auto()  # Platinum

class AbstractEquipment(ABC):
    """
    Abstract base class for equipment items in D&D 5e (2024 Edition).
    
    Equipment in D&D includes:
    - Weapons: Used for combat
    - Armor: Provides protection
    - Adventuring Gear: Various tools and items for exploration and survival
    - Tools: Items for specific skills or trades
    - Mounts & Vehicles: For transportation
    - Trade Goods: For commerce
    - Magic Items: Enchanted objects with special properties
    """
    
    def __init__(self, name: str, category: EquipmentCategory, cost: Dict[Currency, int], 
                 weight: float, description: str = ""):
        """
        Initialize equipment item.
        
        Args:
            name: Item name
            category: Equipment category
            cost: Cost in different currencies
            weight: Weight in pounds
            description: Item description
        """
        self.name = name
        self.category = category
        self.cost = cost
        self.weight = weight
        self.description = description
    
    @abstractmethod
    def get_all_weapons(self) -> List[Dict[str, Any]]:
        """
        Return list of available weapons.
        
        Returns:
            List[Dict[str, Any]]: List of weapon dictionaries
        """
        pass
    
    @abstractmethod
    def get_all_armor(self) -> List[Dict[str, Any]]:
        """
        Return list of available armor.
        
        Returns:
            List[Dict[str, Any]]: List of armor dictionaries
        """
        pass
    
    @abstractmethod
    def get_all_gear(self) -> List[Dict[str, Any]]:
        """
        Return list of adventuring gear.
        
        Returns:
            List[Dict[str, Any]]: List of gear dictionaries
        """
        pass
    
    @abstractmethod
    def get_equipment_details(self, item_id: str) -> Dict[str, Any]:
        """
        Get detailed information about an equipment item.
        
        Args:
            item_id: Unique identifier for the equipment
            
        Returns:
            Dict[str, Any]: Dictionary with item details
        """
        pass
    
    @abstractmethod
    def calculate_weapon_damage(self, weapon_id: str, ability_scores: Dict[str, int]) -> Dict[str, Any]:
        """
        Calculate damage for a weapon.
        
        Args:
            weapon_id: Unique identifier for the weapon
            ability_scores: Character's ability scores
            
        Returns:
            Dict[str, Any]: Dictionary with damage details
        """
        pass
    
    @abstractmethod
    def calculate_armor_class(self, armor_id: str, dexterity_modifier: int) -> int:
        """
        Calculate AC from armor and dexterity.
        
        Args:
            armor_id: Unique identifier for the armor
            dexterity_modifier: Character's dexterity modifier
            
        Returns:
            int: Calculated armor class
        """
        pass
    
    @abstractmethod
    def validate_equipment_requirements(self, character_data: Dict[str, Any], item_id: str) -> bool:
        """
        Check if character meets requirements for equipment.
        
        Args:
            character_data: Character information
            item_id: Unique identifier for the equipment
            
        Returns:
            bool: True if requirements are met, False otherwise
        """
        pass
    
    @abstractmethod
    def get_starting_equipment(self, class_name: str) -> List[Dict[str, Any]]:
        """
        Get starting equipment options for a class.
        
        Args:
            class_name: Name of the character class
            
        Returns:
            List[Dict[str, Any]]: List of starting equipment options
        """
        pass
    
    @abstractmethod
    def get_equipment_by_type(self, equipment_type: EquipmentCategory) -> List[Dict[str, Any]]:
        """
        Get equipment items by type.
        
        Args:
            equipment_type: Type of equipment to retrieve
            
        Returns:
            List[Dict[str, Any]]: List of equipment items
        """
        pass
    
    @abstractmethod
    def get_weapon_properties(self, weapon_id: str) -> List[WeaponProperty]:
        """
        Get properties of a weapon.
        
        Args:
            weapon_id: Unique identifier for the weapon
            
        Returns:
            List[WeaponProperty]: List of weapon properties
        """
        pass
    
    @abstractmethod
    def calculate_carrying_capacity(self, strength_score: int, size: str) -> Dict[str, float]:
        """
        Calculate character's carrying capacity.
        
        Args:
            strength_score: Character's Strength score
            size: Character's size (e.g., "Medium", "Small")
            
        Returns:
            Dict[str, float]: Dictionary with carrying capacity details
        """
        pass
    
    @abstractmethod
    def calculate_attack_bonus(self, weapon_id: str, ability_scores: Dict[str, int], 
                             proficiency_bonus: int, is_proficient: bool) -> int:
        """
        Calculate attack bonus for a weapon.
        
        Args:
            weapon_id: Unique identifier for the weapon
            ability_scores: Character's ability scores
            proficiency_bonus: Character's proficiency bonus
            is_proficient: Whether character is proficient with the weapon
            
        Returns:
            int: Attack bonus
        """
        pass
    
    @abstractmethod
    def format_currency(self, cost: Dict[Currency, int]) -> str:
        """
        Format currency for display.
        
        Args:
            cost: Cost in different currencies
            
        Returns:
            str: Formatted currency string
        """
        pass
    
    def __str__(self) -> str:
        """
        String representation of equipment.
        
        Returns:
            str: Formatted equipment string
        """
        return f"{self.name} ({self.category.name.lower().replace('_', ' ')})"
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert equipment to dictionary.
        
        Returns:
            Dict[str, Any]: Dictionary representation of equipment
        """
        return {
            "name": self.name,
            "category": self.category.name,
            "cost": {currency.name: value for currency, value in self.cost.items()},
            "weight": self.weight,
            "description": self.description
        }

class AbstractWeapon(AbstractEquipment):
    """Abstract base class for weapons."""
    
    def __init__(self, name: str, weapon_type: WeaponType, damage_dice: str, 
                 damage_type: DamageType, properties: List[WeaponProperty], 
                 cost: Dict[Currency, int], weight: float, description: str = "",
                 range_normal: int = 0, range_max: int = 0):
        """
        Initialize weapon.
        
        Args:
            name: Weapon name
            weapon_type: Type of weapon
            damage_dice: Damage dice expression (e.g., "1d8")
            damage_type: Type of damage dealt
            properties: List of weapon properties
            cost: Cost in different currencies
            weight: Weight in pounds
            description: Weapon description
            range_normal: Normal range for ranged weapons
            range_max: Maximum range for ranged weapons
        """
        super().__init__(name, EquipmentCategory.WEAPON, cost, weight, description)
        self.weapon_type = weapon_type
        self.damage_dice = damage_dice
        self.damage_type = damage_type
        self.properties = properties
        self.range_normal = range_normal
        self.range_max = range_max
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weapon to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "weapon_type": self.weapon_type.name,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type.name,
            "properties": [prop.name for prop in self.properties],
            "range_normal": self.range_normal,
            "range_max": self.range_max
        })
        return base_dict

class AbstractArmor(AbstractEquipment):
    """Abstract base class for armor."""
    
    def __init__(self, name: str, armor_type: ArmorType, base_ac: int, 
                 strength_requirement: int, stealth_disadvantage: bool,
                 cost: Dict[Currency, int], weight: float, description: str = "",
                 max_dex_bonus: Optional[int] = None):
        """
        Initialize armor.
        
        Args:
            name: Armor name
            armor_type: Type of armor
            base_ac: Base armor class provided
            strength_requirement: Minimum strength to wear without penalty
            stealth_disadvantage: Whether armor imposes disadvantage on stealth
            cost: Cost in different currencies
            weight: Weight in pounds
            description: Armor description
            max_dex_bonus: Maximum dexterity bonus applied to AC
        """
        super().__init__(name, EquipmentCategory.ARMOR, cost, weight, description)
        self.armor_type = armor_type
        self.base_ac = base_ac
        self.strength_requirement = strength_requirement
        self.stealth_disadvantage = stealth_disadvantage
        self.max_dex_bonus = max_dex_bonus
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary."""
        base_dict = super().to_dict()
        base_dict.update({
            "armor_type": self.armor_type.name,
            "base_ac": self.base_ac,
            "strength_requirement": self.strength_requirement,
            "stealth_disadvantage": self.stealth_disadvantage,
            "max_dex_bonus": self.max_dex_bonus
        })
        return base_dict