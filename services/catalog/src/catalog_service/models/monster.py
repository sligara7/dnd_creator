"""Monster catalog models."""

from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator

from .base import BaseContent, ContentType

class MonsterType(str, Enum):
    """Monster type classifications."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class MonsterSize(str, Enum):
    """Monster size categories."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class MonsterEnvironment(str, Enum):
    """Common monster environments."""
    ARCTIC = "arctic"
    COASTAL = "coastal"
    DESERT = "desert"
    FOREST = "forest"
    GRASSLAND = "grassland"
    HILL = "hill"
    MOUNTAIN = "mountain"
    SWAMP = "swamp"
    UNDERDARK = "underdark"
    UNDERWATER = "underwater"
    URBAN = "urban"

class AbilityScores(BaseModel):
    """D&D ability scores."""
    strength: int = Field(ge=1, le=30)
    dexterity: int = Field(ge=1, le=30)
    constitution: int = Field(ge=1, le=30)
    intelligence: int = Field(ge=1, le=30)
    wisdom: int = Field(ge=1, le=30)
    charisma: int = Field(ge=1, le=30)

class Action(BaseModel):
    """Monster action definition."""
    name: str
    description: str
    attack_bonus: Optional[int] = None
    damage: Optional[Dict[str, str]] = None  # e.g., {"melee": "2d6+4"}
    dc: Optional[Dict[str, Any]] = None  # e.g., {"type": "dexterity", "value": 15}

class MonsterProperties(BaseModel):
    """Properties specific to monsters."""
    monster_type: MonsterType
    size: MonsterSize
    challenge_rating: float = Field(ge=0)
    armor_class: int = Field(ge=0)
    hit_points: int = Field(ge=1)
    hit_dice: str  # e.g., "4d8+8"
    speed: Dict[str, int]  # e.g., {"walk": 30, "fly": 60}
    ability_scores: AbilityScores
    saving_throws: Dict[str, int] = Field(default_factory=dict)
    skills: Dict[str, int] = Field(default_factory=dict)
    damage_vulnerabilities: List[str] = Field(default_factory=list)
    damage_resistances: List[str] = Field(default_factory=list)
    damage_immunities: List[str] = Field(default_factory=list)
    condition_immunities: List[str] = Field(default_factory=list)
    senses: Dict[str, int] = Field(default_factory=dict)
    languages: List[str] = Field(default_factory=list)
    environments: List[MonsterEnvironment] = Field(default_factory=list)
    actions: List[Action] = Field(default_factory=list)
    reactions: List[Action] = Field(default_factory=list)
    legendary_actions: List[Action] = Field(default_factory=list)
    spells: List[str] = Field(default_factory=list)
    treasure_table: Optional[str] = None

class Monster(BaseContent):
    """Model for monsters in the catalog."""
    type: ContentType = ContentType.MONSTER
    properties: MonsterProperties

    @field_validator("type")
    @classmethod
    def validate_type(cls, v: ContentType) -> ContentType:
        if v != ContentType.MONSTER:
            raise ValueError("Type must be 'monster'")
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "type": "monster",
                "name": "Ancient Red Dragon",
                "source": "official",
                "description": "A colossal dragon with crimson scales and an aura of terror.",
                "properties": {
                    "monster_type": "dragon",
                    "size": "gargantuan",
                    "challenge_rating": 24,
                    "armor_class": 22,
                    "hit_points": 546,
                    "hit_dice": "28d20+252",
                    "speed": {
                        "walk": 40,
                        "climb": 40,
                        "fly": 80
                    },
                    "ability_scores": {
                        "strength": 30,
                        "dexterity": 10,
                        "constitution": 29,
                        "intelligence": 18,
                        "wisdom": 15,
                        "charisma": 23
                    },
                    "saving_throws": {
                        "dexterity": 7,
                        "constitution": 16,
                        "wisdom": 9,
                        "charisma": 13
                    },
                    "skills": {
                        "perception": 16,
                        "stealth": 7
                    },
                    "damage_immunities": [
                        "fire"
                    ],
                    "senses": {
                        "blindsight": 60,
                        "darkvision": 120
                    },
                    "languages": [
                        "Common",
                        "Draconic"
                    ],
                    "environments": [
                        "mountain",
                        "hill"
                    ],
                    "actions": [
                        {
                            "name": "Bite",
                            "description": "Melee Weapon Attack",
                            "attack_bonus": 17,
                            "damage": {
                                "piercing": "2d10+10"
                            }
                        }
                    ],
                    "legendary_actions": [
                        {
                            "name": "Tail Attack",
                            "description": "The dragon makes a tail attack.",
                            "attack_bonus": 17,
                            "damage": {
                                "bludgeoning": "2d8+10"
                            }
                        }
                    ]
                },
                "metadata": {
                    "version": "1.0.0",
                    "created_at": "2025-01-01T00:00:00Z",
                    "updated_at": "2025-01-01T00:00:00Z",
                    "created_by": "system"
                },
                "theme_data": {
                    "themes": [
                        "dragon",
                        "fire",
                        "mountain"
                    ],
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