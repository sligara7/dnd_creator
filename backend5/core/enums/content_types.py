from enum import Enum, auto


class ContentType(Enum):
    """Primary content types for the Creative Content Framework."""
    SPECIES = "species"
    CHARACTER_CLASS = "character_class"
    EQUIPMENT = "equipment"
    SPELL = "spell"
    FEAT = "feat"
    BACKGROUND = "background"
    SUBCLASS = "subclass"


class ContentRarity(Enum):
    """Rarity levels for generated content."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"


class ContentSource(Enum):
    """Source of content creation."""
    CORE_RULES = "core_rules"           # Official D&D content
    GENERATED = "generated"             # AI-generated content
    CUSTOM = "custom"                   # User-created content
    HYBRID = "hybrid"                   # Mix of generated and custom


class EquipmentCategory(Enum):
    """Official equipment categories in D&D 5e (2024 Edition)."""
    WEAPON = auto()
    ARMOR = auto()
    ADVENTURING_GEAR = auto()
    TOOL = auto()
    MOUNT = auto()
    VEHICLE = auto()
    TRADE_GOOD = auto()
    MAGIC_ITEM = auto()


class WeaponType(Enum):
    """Official weapon types in D&D 5e (2024 Edition)."""
    SIMPLE_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_MELEE = auto()
    MARTIAL_RANGED = auto()


class ArmorType(Enum):
    """Official armor types in D&D 5e (2024 Edition)."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()


class WeaponProperty(Enum):
    """Official weapon properties in D&D 5e (2024 Edition)."""
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


class FeatCategory(Enum):
    """Official feat categories in D&D 5e (2024 Edition)."""
    GENERAL = auto()
    HEROIC = auto()
    EPIC = auto()
    SPECIES = auto()
    CLASS = auto()
    BACKGROUND = auto()


class SpeciesSize(Enum):
    """Official species sizes in D&D 5e (2024 Edition)."""
    TINY = auto()
    SMALL = auto()
    MEDIUM = auto()
    LARGE = auto()
    HUGE = auto()
    GARGANTUAN = auto()


class BackstoryElement(Enum):
    """Key elements that make up a character's backstory according to D&D 2024 rules."""
    ORIGIN = auto()
    FAMILY = auto()
    EDUCATION = auto()
    DEFINING_EVENT = auto()
    MOTIVATION = auto()
    CONNECTIONS = auto()
    GOALS = auto()