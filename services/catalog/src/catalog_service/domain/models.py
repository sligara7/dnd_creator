from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class ContentType(str, Enum):
    ITEM = "item"
    SPELL = "spell"
    MONSTER = "monster"


class ContentSource(str, Enum):
    OFFICIAL = "official"
    CUSTOM = "custom"


class ContentMetadata(BaseModel):
    """Metadata for any content item"""
    version: str
    created_at: datetime
    updated_at: datetime
    created_by: str


class ThemeData(BaseModel):
    """Theme information for content items"""
    themes: List[str]
    adaptations: Dict[str, Any] = Field(default_factory=dict)


class ValidationData(BaseModel):
    """Validation information for content items"""
    balance_score: float
    consistency_check: bool
    last_validated: datetime


class BaseContent(BaseModel):
    """Base model for all content items"""
    id: UUID
    type: ContentType
    name: str
    source: ContentSource
    description: str
    properties: Dict[str, Any]
    metadata: ContentMetadata
    theme_data: ThemeData
    validation: ValidationData


class Item(BaseContent):
    """Model for equipment and items"""
    type: ContentType = ContentType.ITEM
    category: str
    properties: Dict[str, Any] = Field(..., examples=[{
        "weight": 1.5,
        "cost": 1000,
        "rarity": "uncommon",
        "attunement": True,
        "equipment_slot": "weapon",
        "damage": {
            "dice": "1d8",
            "type": "piercing"
        }
    }])


class Spell(BaseContent):
    """Model for spells"""
    type: ContentType = ContentType.SPELL
    properties: Dict[str, Any] = Field(..., examples=[{
        "level": 3,
        "school": "evocation",
        "casting_time": "1 action",
        "range": "60 feet",
        "components": {
            "verbal": True,
            "somatic": True,
            "material": "a bit of fur and a glass rod"
        },
        "duration": "instantaneous",
        "ritual": False
    }])


class Monster(BaseContent):
    """Model for monsters"""
    type: ContentType = ContentType.MONSTER
    properties: Dict[str, Any] = Field(..., examples=[{
        "size": "medium",
        "type": "humanoid",
        "alignment": "neutral",
        "armor_class": 15,
        "hit_points": 65,
        "speed": {
            "walk": 30,
            "fly": 0,
            "swim": 0
        },
        "abilities": {
            "strength": 16,
            "dexterity": 14,
            "constitution": 15,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        },
        "challenge_rating": 3
    }])


class ValidationIssue(BaseModel):
    """Validation issue details"""
    type: str
    severity: str
    message: str
    suggestions: List[str]


class ValidationResult(BaseModel):
    """Result of content validation"""
    valid: bool
    balance_score: float
    issues: List[ValidationIssue] = Field(default_factory=list)
