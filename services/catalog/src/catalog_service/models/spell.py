"""Spell catalog models."""

from enum import Enum
from typing import Dict

from pydantic import BaseModel, Field, field_validator

from .base import BaseContent, ContentType

class SpellSchool(str, Enum):
    """D&D spell schools."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"

class SpellComponents(BaseModel):
    """Spell component requirements."""
    verbal: bool = False
    somatic: bool = False
    material: str = ""

class SpellProperties(BaseModel):
    """Properties specific to spells."""
    level: int = Field(ge=0, le=9)  # 0 = cantrip
    school: SpellSchool
    casting_time: str
    range: str
    components: SpellComponents
    duration: str
    ritual: bool = False
    concentration: bool = False
    requires_attack_roll: bool = False
    requires_save: bool = False
    save_type: str = ""  # e.g., "dexterity", "wisdom", etc.
    damage: Dict[str, str] = Field(default_factory=dict)  # e.g., {"level_1": "1d8", "level_5": "2d8"}

class Spell(BaseContent):
    """Model for spells in the catalog."""
    type: ContentType = ContentType.SPELL
    properties: SpellProperties

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: ContentType) -> ContentType:
        if v != ContentType.SPELL:
            raise ValueError("Type must be 'spell'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "spell",
                "name": "Fireball",
                "source": "official",
                "description": "A bright streak flashes from your pointing finger to a point you choose within range and then blossoms with a low roar into an explosion of flame.",
                "properties": {
                    "level": 3,
                    "school": "evocation",
                    "casting_time": "1 action",
                    "range": "150 feet",
                    "components": {
                        "verbal": True,
                        "somatic": True,
                        "material": "a tiny ball of bat guano and sulfur"
                    },
                    "duration": "Instantaneous",
                    "ritual": False,
                    "concentration": False,
                    "requires_attack_roll": False,
                    "requires_save": True,
                    "save_type": "dexterity",
                    "damage": {
                        "level_3": "8d6",
                        "level_4": "9d6",
                        "level_5": "10d6"
                    }
                },
                "metadata": {
                    "version": "1.0.0",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "created_by": "system"
                },
                "theme_data": {
                    "themes": ["fire", "destruction"],
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