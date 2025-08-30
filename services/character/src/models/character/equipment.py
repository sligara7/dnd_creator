"""Character equipment and inventory models."""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from enum import Enum

from ..shared.enums import DamageType, WeaponProperty
from ..shared.validators import WeightValidator, DiceValidator
from ..base import BaseModelWithAudit

class Currency(BaseModel):
    """Currency amounts for standard D&D coins."""
    copper: int = Field(0, ge=0, description="Copper pieces")
    silver: int = Field(0, ge=0, description="Silver pieces")
    electrum: int = Field(0, ge=0, description="Electrum pieces")
    gold: int = Field(0, ge=0, description="Gold pieces")
    platinum: int = Field(0, ge=0, description="Platinum pieces")
    
    def add_coins(self, coin_type: str, amount: int) -> None:
        """Add coins of a specific type."""
        if hasattr(self, coin_type.lower()):
            current = getattr(self, coin_type.lower())
            setattr(self, coin_type.lower(), max(0, current + amount))
    
    def remove_coins(self, coin_type: str, amount: int) -> bool:
        """Remove coins if available."""
        if not hasattr(self, coin_type.lower()):
            return False
        
        current = getattr(self, coin_type.lower())
        if current >= amount:
            setattr(self, coin_type.lower(), current - amount)
            return True
        return False
    
    def get_total_in_gold(self) -> float:
        """Calculate total wealth in gold pieces."""
        return (
            self.copper / 100 +
            self.silver / 10 +
            self.electrum / 2 +
            self.gold +
            self.platinum * 10
        )

class ArmorType(str, Enum):
    """Types of armor available in D&D 5e."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

class Armor(BaseModel):
    """Represents a piece of armor."""
    name: str = Field(..., description="Name of the armor")
    type: ArmorType = Field(..., description="Type of armor")
    base_ac: int = Field(..., description="Base armor class provided")
    strength_requirement: Optional[int] = Field(None, description="Minimum strength required")
    stealth_disadvantage: bool = Field(False, description="Whether the armor imposes disadvantage on stealth")
    weight: float = Field(..., description="Weight in pounds")
    cost: Currency = Field(..., description="Cost in various coin types")
    magical: bool = Field(False, description="Whether this is a magic item")
    properties: List[str] = Field(default_factory=list, description="Special properties")
    
    _validate_weight = WeightValidator.validate_weight

class Weapon(BaseModel):
    """Represents a weapon."""
    name: str = Field(..., description="Name of the weapon")
    weapon_type: str = Field(..., description="Type of weapon (simple, martial)")
    damage_dice: str = Field(..., description="Damage dice expression")
    damage_type: DamageType = Field(..., description="Type of damage dealt")
    properties: List[WeaponProperty] = Field(default_factory=list, description="Weapon properties")
    range: Optional[str] = Field(None, description="Range if ranged weapon (e.g., '30/120')")
    weight: float = Field(..., description="Weight in pounds")
    cost: Currency = Field(..., description="Cost in various coin types")
    magical: bool = Field(False, description="Whether this is a magic item")
    bonus: Optional[int] = Field(None, description="Magic bonus to attack and damage")
    additional_damage: Optional[str] = Field(None, description="Additional damage (e.g., '1d6 fire')")
    attunement: bool = Field(False, description="Whether attunement is required")
    
    _validate_weight = WeightValidator.validate_weight
    _validate_damage_dice = DiceValidator.validate_dice_expression

class ItemRarity(str, Enum):
    """Rarity levels for magic items."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class MagicItem(BaseModel):
    """Represents a magic item."""
    name: str = Field(..., description="Name of the item")
    type: str = Field(..., description="Type of item")
    rarity: ItemRarity = Field(..., description="Rarity of the item")
    attunement: bool = Field(False, description="Whether attunement is required")
    charges: Optional[int] = Field(None, description="Number of charges if applicable")
    max_charges: Optional[int] = Field(None, description="Maximum charges if applicable")
    recharge: Optional[str] = Field(None, description="When/how charges recharge")
    properties: List[str] = Field(default_factory=list, description="Special properties")
    weight: float = Field(0.0, description="Weight in pounds")
    description: str = Field(..., description="Description and effects")
    
    _validate_weight = WeightValidator.validate_weight

class Container(BaseModel):
    """Represents a container that can hold other items."""
    name: str = Field(..., description="Name of the container")
    capacity: float = Field(..., description="Weight capacity in pounds")
    weight: float = Field(..., description="Weight in pounds when empty")
    current_weight: float = Field(0.0, description="Current weight of contents")
    contents: List[Dict] = Field(default_factory=list, description="Items in container")
    
    _validate_weight = WeightValidator.validate_weight

class InventoryState(BaseModelWithAudit):
    """Tracks a character's complete inventory."""
    
    # Currency
    currency: Currency = Field(
        default_factory=Currency,
        description="Character's money"
    )
    
    # Equipment slots
    armor: Optional[Armor] = Field(None, description="Worn armor")
    shield: Optional[Armor] = Field(None, description="Equipped shield")
    weapons: List[Weapon] = Field(default_factory=list, description="Equipped weapons")
    
    # Magic items
    attuned_items: List[MagicItem] = Field(
        default_factory=list,
        description="Attuned magic items"
    )
    max_attunements: int = Field(3, description="Maximum number of attunements")
    
    # Inventory organization
    containers: Dict[str, Container] = Field(
        default_factory=dict,
        description="Containers and their contents"
    )
    loose_items: List[Dict] = Field(
        default_factory=list,
        description="Items not in containers"
    )
    
    def add_item(self, item: Dict, container: Optional[str] = None) -> bool:
        """Add an item to inventory."""
        if container and container in self.containers:
            # Check container capacity
            if (self.containers[container].current_weight + item.get("weight", 0)
                <= self.containers[container].capacity):
                self.containers[container].contents.append(item)
                self.containers[container].current_weight += item.get("weight", 0)
                return True
            return False
        else:
            self.loose_items.append(item)
            return True
    
    def remove_item(self, item_name: str, container: Optional[str] = None) -> bool:
        """Remove an item from inventory."""
        if container and container in self.containers:
            for item in self.containers[container].contents:
                if item["name"] == item_name:
                    self.containers[container].contents.remove(item)
                    self.containers[container].current_weight -= item.get("weight", 0)
                    return True
            return False
        else:
            for item in self.loose_items:
                if item["name"] == item_name:
                    self.loose_items.remove(item)
                    return True
            return False
    
    def get_total_weight(self) -> float:
        """Calculate total carried weight."""
        total = sum(item.get("weight", 0) for item in self.loose_items)
        
        if self.armor:
            total += self.armor.weight
        if self.shield:
            total += self.shield.weight
        
        total += sum(weapon.weight for weapon in self.weapons)
        total += sum(container.weight + container.current_weight 
                    for container in self.containers.values())
        
        return total
    
    def can_attune_item(self, item: MagicItem) -> bool:
        """Check if character can attune to an item."""
        if not item.attunement:
            return True
        return len(self.attuned_items) < self.max_attunements
    
    def attune_item(self, item: MagicItem) -> bool:
        """Attempt to attune to a magic item."""
        if self.can_attune_item(item):
            if item not in self.attuned_items:
                self.attuned_items.append(item)
            return True
        return False
    
    def unattune_item(self, item: MagicItem) -> bool:
        """Remove attunement to a magic item."""
        if item in self.attuned_items:
            self.attuned_items.remove(item)
            return True
        return False
