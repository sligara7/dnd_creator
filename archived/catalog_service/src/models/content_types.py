"""
Content type models for the Catalog Service.
"""

from typing import List, Dict, Any, Optional
from pydantic import Field

from .base import BaseContent, ContentType, ContentSource


class DamageDice(BaseModel):
    """Damage dice specification."""
    dice: str  # e.g., "1d6"
    type: str  # e.g., "piercing"


class ItemContent(BaseContent):
    """Model for items in the catalog."""
    type: ContentType = ContentType.ITEM
    category: str  # weapon, armor, equipment, magical
    properties: Dict[str, Any] = Field(default_factory=lambda: {
        "weight": 0.0,
        "cost": 0,
        "rarity": "common",
        "attunement": False,
        "equipment_slot": None,
        "damage": None
    })


class SpellContent(BaseContent):
    """Model for spells in the catalog."""
    type: ContentType = ContentType.SPELL
    properties: Dict[str, Any] = Field(default_factory=lambda: {
        "level": 0,
        "school": None,
        "casting_time": "1 action",
        "range": None,
        "components": {
            "verbal": False,
            "somatic": False,
            "material": None
        },
        "duration": None,
        "ritual": False
    })


class MonsterContent(BaseContent):
    """Model for monsters in the catalog."""
    type: ContentType = ContentType.MONSTER
    properties: Dict[str, Any] = Field(default_factory=lambda: {
        "size": None,
        "type": None,
        "alignment": None,
        "challenge_rating": 0,
        "environment": [],
        "stats": {
            "hp": 0,
            "ac": 10,
            "speed": {},
            "str": 10,
            "dex": 10,
            "con": 10,
            "int": 10,
            "wis": 10,
            "cha": 10
        },
        "abilities": [],
        "actions": [],
        "legendary_actions": []
    })
