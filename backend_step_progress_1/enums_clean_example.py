"""
D&D 5e Enumerations

This module contains all enum definitions for the D&D Character Creator.
Contains only enum definitions - no orchestration or coordination logic.
"""

from enum import Enum

class CreationOptions(Enum):
    """Types of D&D 5e objects that can be created."""
    CHARACTER = "character"
    MONSTER = "monster"
    NPC = "npc"
    WEAPON = "weapon"
    SPELL = "spell"
    ARMOR = "armor"
    OTHER_ITEM = "other_item"

class CreatureType(Enum):
    """D&D 5e creature types."""
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

# ... rest of enums without orchestration comments
