"""
Essential D&D Content Type Enums

Streamlined content type classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CHARACTER CONTENT TYPES ============

class CharacterElement(Enum):
    """Core character building elements."""
    RACE = auto()
    CLASS = auto()
    BACKGROUND = auto()
    FEAT = auto()
    SPELL = auto()
    EQUIPMENT = auto()

class SourceType(Enum):
    """Content source classifications."""
    CORE = "phb"           # Player's Handbook
    EXPANSION = "supplement"
    HOMEBREW = "custom"
    THIRD_PARTY = "external"

class ContentRarity(Enum):
    """Content availability rarity."""
    COMMON = auto()         # Always available
    UNCOMMON = auto()       # DM approval suggested
    RARE = auto()           # DM approval required
    LEGENDARY = auto()      # Campaign-specific

# ============ GAME MECHANICS TYPES ============

class MechanicType(Enum):
    """Core game mechanic categories."""
    ABILITY = auto()        # Ability scores, skills
    COMBAT = auto()         # Attack, damage, AC
    MAGIC = auto()          # Spells, spell slots
    SOCIAL = auto()         # Languages, proficiencies
    EXPLORATION = auto()    # Movement, senses

class ActionType(Enum):
    """Action economy classifications."""
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    FREE = auto()
    PASSIVE = auto()

class DurationType(Enum):
    """Effect duration types."""
    INSTANTANEOUS = auto()
    CONCENTRATION = auto()
    PERMANENT = auto()
    UNTIL_REST = auto()
    TIMED = auto()

# ============ EQUIPMENT TYPES ============

class EquipmentCategory(Enum):
    """Equipment categorization."""
    WEAPON = auto()
    ARMOR = auto()
    SHIELD = auto()
    TOOL = auto()
    GEAR = auto()
    MAGIC_ITEM = auto()

class WeaponType(Enum):
    """Weapon classifications."""
    SIMPLE_MELEE = auto()
    SIMPLE_RANGED = auto()
    MARTIAL_MELEE = auto()
    MARTIAL_RANGED = auto()

class ArmorType(Enum):
    """Armor classifications."""
    LIGHT = auto()
    MEDIUM = auto()
    HEAVY = auto()
    SHIELD = auto()

# ============ SPELL CONTENT TYPES ============

class SpellComponent(Enum):
    """Spell component requirements."""
    VERBAL = "V"
    SOMATIC = "S"
    MATERIAL = "M"
    FOCUS = "F"
    DIVINE_FOCUS = "DF"

class SpellTarget(Enum):
    """Spell targeting types."""
    SELF = auto()
    SINGLE = auto()
    MULTIPLE = auto()
    AREA = auto()
    TOUCH = auto()

class AreaType(Enum):
    """Area of effect shapes."""
    SPHERE = auto()
    CUBE = auto()
    CYLINDER = auto()
    CONE = auto()
    LINE = auto()

# ============ CONTENT VALIDATION TYPES ============

class ValidationLevel(Enum):
    """Content validation strictness."""
    NONE = auto()           # No validation
    BASIC = auto()          # Core rules only
    STANDARD = auto()       # Official content
    STRICT = auto()         # Balanced content only

class ContentStatus(Enum):
    """Content approval status."""
    APPROVED = auto()
    PENDING = auto()
    REJECTED = auto()
    DEPRECATED = auto()

# ============ UTILITY FUNCTIONS ============

def is_official_content(source: SourceType) -> bool:
    """Check if content is from official sources."""
    return source in [SourceType.CORE, SourceType.EXPANSION]

def requires_approval(rarity: ContentRarity) -> bool:
    """Check if content requires DM approval."""
    return rarity in [ContentRarity.UNCOMMON, ContentRarity.RARE, ContentRarity.LEGENDARY]

def get_spell_components(component_string: str) -> list[SpellComponent]:
    """Parse spell component string into enum list."""
    components = []
    if 'V' in component_string:
        components.append(SpellComponent.VERBAL)
    if 'S' in component_string:
        components.append(SpellComponent.SOMATIC)
    if 'M' in component_string:
        components.append(SpellComponent.MATERIAL)
    return components

def is_combat_relevant(mechanic: MechanicType) -> bool:
    """Check if mechanic type affects combat."""
    return mechanic in [MechanicType.ABILITY, MechanicType.COMBAT, MechanicType.MAGIC]

# ============ CONTENT TYPE MAPPINGS ============

CONTENT_CATEGORIES = {
    "character_creation": [
        CharacterElement.RACE,
        CharacterElement.CLASS,
        CharacterElement.BACKGROUND
    ],
    "character_advancement": [
        CharacterElement.FEAT,
        CharacterElement.SPELL
    ],
    "equipment": [
        CharacterElement.EQUIPMENT
    ]
}

ACTION_PRIORITY = {
    ActionType.REACTION: 1,     # Highest priority
    ActionType.FREE: 2,
    ActionType.BONUS_ACTION: 3,
    ActionType.ACTION: 4,
    ActionType.PASSIVE: 5       # Lowest priority
}

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Character content
    'CharacterElement',
    'SourceType',
    'ContentRarity',
    
    # Game mechanics
    'MechanicType',
    'ActionType',
    'DurationType',
    
    # Equipment
    'EquipmentCategory',
    'WeaponType',
    'ArmorType',
    
    # Spells
    'SpellComponent',
    'SpellTarget',
    'AreaType',
    
    # Validation
    'ValidationLevel',
    'ContentStatus',
    
    # Mappings
    'CONTENT_CATEGORIES',
    'ACTION_PRIORITY',
    
    # Utility functions
    'is_official_content',
    'requires_approval',
    'get_spell_components',
    'is_combat_relevant',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D content type enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "content_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}