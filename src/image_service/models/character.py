"""
Models for character visualization.
"""

from enum import Enum, auto
from typing import List, Optional
from uuid import UUID
from pydantic import BaseModel, Field

class CharacterClass(str, Enum):
    """D&D character classes."""
    ARTIFICER = "artificer"
    BARBARIAN = "barbarian"
    BARD = "bard"
    CLERIC = "cleric"
    DRUID = "druid"
    FIGHTER = "fighter"
    MONK = "monk"
    PALADIN = "paladin"
    RANGER = "ranger"
    ROGUE = "rogue"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    WIZARD = "wizard"

class CharacterRace(str, Enum):
    """D&D character races."""
    DRAGONBORN = "dragonborn"
    DWARF = "dwarf"
    ELF = "elf"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALFLING = "halfling"
    HALF_ORC = "half-orc"
    HUMAN = "human"
    TIEFLING = "tiefling"

class NPCType(str, Enum):
    """Types of NPCs."""
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    COMMONER = "commoner"
    SAGE = "sage"
    CRIMINAL = "criminal"
    PRIEST = "priest"
    ENTERTAINER = "entertainer"

class MonsterType(str, Enum):
    """Types of monsters."""
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

class EquipmentVisuals(BaseModel):
    """Visual representation of equipment."""
    armor: Optional[str] = Field(None, description="Armor type and appearance")
    weapon: Optional[str] = Field(None, description="Weapon type and appearance")
    shield: Optional[str] = Field(None, description="Shield type and appearance")
    accessories: List[str] = Field(default_factory=list, description="Additional equipment and accessories")

class ThemeStyle(BaseModel):
    """Visual theme and style settings."""
    art_style: str = Field(..., description="Art style (e.g., realistic, anime, painterly)")
    color_scheme: str = Field(..., description="Color scheme (e.g., vibrant, muted, dark)")
    mood: str = Field(..., description="Emotional mood (e.g., heroic, mysterious, threatening)")

class PortraitSize(str, Enum):
    """Standard portrait sizes."""
    TINY = "tiny"  # 128x128
    SMALL = "small"  # 256x256
    MEDIUM = "medium"  # 512x512
    LARGE = "large"  # 1024x1024
    HUGE = "huge"  # 2048x2048

    def dimensions(self) -> tuple[int, int]:
        """Get pixel dimensions for this size."""
        sizes = {
            "tiny": (128, 128),
            "small": (256, 256),
            "medium": (512, 512),
            "large": (1024, 1024),
            "huge": (2048, 2048)
        }
        return sizes[self.value]

class PortraitMetadata(BaseModel):
    """Metadata for a character portrait."""
    width: int = Field(..., description="Image width in pixels")
    height: int = Field(..., description="Image height in pixels")
    character_id: UUID = Field(..., description="Associated character ID")
    character_name: str = Field(..., description="Character name")
    character_class: Optional[CharacterClass] = Field(None, description="Character class")
    character_race: Optional[CharacterRace] = Field(None, description="Character race")
    npc_type: Optional[NPCType] = Field(None, description="NPC type if applicable")
    monster_type: Optional[MonsterType] = Field(None, description="Monster type if applicable")
    equipment: Optional[EquipmentVisuals] = Field(None, description="Equipment visuals")
    theme: ThemeStyle = Field(..., description="Visual theme and style")

    def copy(self, update: dict = None) -> 'PortraitMetadata':
        """Create a copy with optional updates."""
        data = self.model_dump()
        if update:
            data.update(update)
        return PortraitMetadata(**data)

class CharacterPortraitRequest(BaseModel):
    """Request to generate a character portrait."""
    size: PortraitSize = Field(..., description="Portrait size")
    metadata: PortraitMetadata = Field(..., description="Portrait metadata")
    background_style: str = Field(..., description="Background style (e.g., neutral, action, dungeon)")
    pose: str = Field(..., description="Character pose")
    expression: str = Field(..., description="Facial expression")
    lighting: str = Field(..., description="Lighting style")
