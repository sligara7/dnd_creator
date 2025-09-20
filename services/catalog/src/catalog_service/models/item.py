"""Item catalog models."""

from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel, Field, field_validator

from .base import BaseContent, ContentType

class ItemCategory(str, Enum):
    """Item categories."""
    WEAPON = "weapon"
    ARMOR = "armor"
    EQUIPMENT = "equipment"
    MAGICAL = "magical"

class ItemRarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class DamageProperties(BaseModel):
    """Properties for items that deal damage."""
    dice: str  # Example: "1d8"
    type: str  # Example: "slashing"

class ItemProperties(BaseModel):
    """Properties specific to items."""
    category: ItemCategory
    weight: float = Field(ge=0)
    cost: int = Field(ge=0)
    rarity: ItemRarity = ItemRarity.COMMON
    attunement: bool = False
    equipment_slot: Optional[str] = None
    damage: Optional[DamageProperties] = None

class Item(BaseContent):
    """Model for items in the catalog."""
    type: ContentType = ContentType.ITEM
    properties: ItemProperties

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: ContentType) -> ContentType:
        if v != ContentType.ITEM:
            raise ValueError("Type must be 'item'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "item",
                "name": "Longsword",
                "source": "official",
                "description": "A versatile slashing weapon",
                "properties": {
                    "category": "weapon",
                    "weight": 3.0,
                    "cost": 1500,
                    "rarity": "common",
                    "attunement": False,
                    "equipment_slot": "main_hand",
                    "damage": {
                        "dice": "1d8",
                        "type": "slashing"
                    }
                },
                "metadata": {
                    "version": "1.0.0",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "created_by": "system"
                },
                "theme_data": {
                    "themes": ["medieval", "fantasy"],
                    "adaptations": {}
                },
                "validation": {
                    "balance_score": 1.0,
                    "consistency_check": True,
                    "last_validated": "2025-01-01T00:00:00Z",
                    "validation_notes": {}
                }
            }
        }