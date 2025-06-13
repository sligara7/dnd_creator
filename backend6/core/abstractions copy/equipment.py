from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from ..enums.content_types import (
    EquipmentCategory, WeaponType, ArmorType, WeaponProperty, ContentRarity, ContentSource
)
from ..enums.dnd_constants import DamageType, Currency
from ..enums.validation_types import ValidationResult


class AbstractEquipment(ABC):
    """
    Abstract contract for all D&D equipment in the Creative Content Framework.
    
    This interface defines the rules that both official and generated equipment
    must follow, ensuring D&D 2024 rule compliance while enabling creative freedom.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Equipment name."""
        pass
    
    @property
    @abstractmethod
    def category(self) -> EquipmentCategory:
        """Equipment category."""
        pass
    
    @property
    @abstractmethod
    def rarity(self) -> ContentRarity:
        """Equipment rarity level."""
        pass
    
    @property
    @abstractmethod
    def content_source(self) -> ContentSource:
        """Source of this equipment (core rules, generated, custom, etc.)."""
        pass
    
    @abstractmethod
    def get_cost(self) -> Dict[Currency, int]:
        """
        Get equipment cost in various currencies.
        
        Returns:
            Dictionary mapping currency types to amounts
        """
        pass
    
    @abstractmethod
    def get_weight(self) -> float:
        """
        Get equipment weight in pounds.
        
        Returns:
            Weight in pounds
        """
        pass
    
    @abstractmethod
    def get_description(self) -> str:
        """
        Get equipment description.
        
        Returns:
            Full description of the equipment
        """
        pass
    
    @abstractmethod
    def get_properties(self) -> List[str]:
        """
        Get special properties of this equipment.
        
        Returns:
            List of property names
        """
        pass
    
    @abstractmethod
    def requires_attunement(self) -> bool:
        """
        Check if equipment requires attunement.
        
        Returns:
            True if attunement is required
        """
        pass
    
    @abstractmethod
    def validate_equipment_balance(self) -> List[ValidationResult]:
        """
        Validate equipment power level for its rarity.
        
        Returns:
            List of validation results
        """
        pass


class AbstractWeapon(AbstractEquipment):
    """
    Abstract contract for weapons in the Creative Content Framework.
    """
    
    @property
    @abstractmethod
    def weapon_type(self) -> WeaponType:
        """Type of weapon (simple/martial, melee/ranged)."""
        pass
    
    @abstractmethod
    def get_damage_dice(self) -> str:
        """
        Get weapon damage dice expression.
        
        Returns:
            Damage dice string (e.g., "1d8", "2d6")
        """
        pass
    
    @abstractmethod
    def get_damage_type(self) -> DamageType:
        """
        Get primary damage type.
        
        Returns:
            Type of damage dealt
        """
        pass
    
    @abstractmethod
    def get_weapon_properties(self) -> List[WeaponProperty]:
        """
        Get weapon properties.
        
        Returns:
            List of weapon properties
        """
        pass
    
    @abstractmethod
    def get_range(self) -> Optional[Tuple[int, int]]:
        """
        Get weapon range for ranged weapons.
        
        Returns:
            Tuple of (normal range, maximum range) or None for melee weapons
        """
        pass
    
    @abstractmethod
    def calculate_attack_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate attack bonus for this weapon with given character.
        
        Args:
            character_data: Character information
            
        Returns:
            Total attack bonus
        """
        pass
    
    @abstractmethod
    def calculate_damage_bonus(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate damage bonus for this weapon with given character.
        
        Args:
            character_data: Character information
            
        Returns:
            Damage bonus to add to rolls
        """
        pass
    
    @abstractmethod
    def is_finesse(self) -> bool:
        """Check if weapon has finesse property."""
        pass
    
    @abstractmethod
    def is_versatile(self) -> bool:
        """Check if weapon has versatile property."""
        pass
    
    @abstractmethod
    def get_versatile_damage(self) -> Optional[str]:
        """Get versatile damage dice if applicable."""
        pass


class AbstractArmor(AbstractEquipment):
    """
    Abstract contract for armor in the Creative Content Framework.
    """
    
    @property
    @abstractmethod
    def armor_type(self) -> ArmorType:
        """Type of armor (light, medium, heavy, shield)."""
        pass
    
    @abstractmethod
    def get_base_ac(self) -> int:
        """
        Get base armor class value.
        
        Returns:
            Base AC provided by the armor
        """
        pass
    
    @abstractmethod
    def get_max_dex_bonus(self) -> Optional[int]:
        """
        Get maximum Dexterity bonus allowed.
        
        Returns:
            Maximum Dex bonus or None if unlimited
        """
        pass
    
    @abstractmethod
    def get_strength_requirement(self) -> int:
        """
        Get minimum Strength requirement.
        
        Returns:
            Minimum Strength score required (0 if none)
        """
        pass
    
    @abstractmethod
    def has_stealth_disadvantage(self) -> bool:
        """
        Check if armor imposes stealth disadvantage.
        
        Returns:
            True if stealth checks have disadvantage
        """
        pass
    
    @abstractmethod
    def calculate_ac(self, character_data: Dict[str, Any]) -> int:
        """
        Calculate total AC with character's stats.
        
        Args:
            character_data: Character information including Dex modifier
            
        Returns:
            Total armor class
        """
        pass


class AbstractMagicItem(AbstractEquipment):
    """
    Abstract contract for magic items in the Creative Content Framework.
    """
    
    @abstractmethod
    def get_magical_properties(self) -> Dict[str, Any]:
        """
        Get magical properties and effects.
        
        Returns:
            Dictionary of magical properties
        """
        pass
    
    @abstractmethod
    def get_activation_method(self) -> str:
        """
        Get how the item is activated.
        
        Returns:
            Activation method (action, bonus action, reaction, etc.)
        """
        pass
    
    @abstractmethod
    def get_usage_limits(self) -> Optional[Dict[str, Any]]:
        """
        Get usage limitations if any.
        
        Returns:
            Dictionary with usage limits or None if unlimited
        """
        pass
    
    @abstractmethod
    def can_be_crafted(self) -> bool:
        """
        Check if item can be crafted by players.
        
        Returns:
            True if craftable
        """
        pass
    
    @abstractmethod
    def get_crafting_requirements(self) -> Optional[Dict[str, Any]]:
        """
        Get crafting requirements if item can be crafted.
        
        Returns:
            Crafting requirements or None if not craftable
        """
        pass