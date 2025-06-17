"""
Essential Character Progression Type Enums

Streamlined character progression classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CHARACTER LEVEL PROGRESSION ============

class ProgressionType(Enum):
    """Character advancement progression types."""
    SINGLE_CLASS = auto()       # Pure single class
    MULTICLASS = auto()         # Multiple classes
    GESTALT = auto()           # Dual-class progression
    VARIANT = auto()           # Custom progression

class LevelTier(Enum):
    """Character level tier classifications."""
    TIER_1 = "local_heroes"     # Levels 1-4
    TIER_2 = "heroes_realm"     # Levels 5-10
    TIER_3 = "masters_realm"    # Levels 11-16
    TIER_4 = "masters_world"    # Levels 17-20

class AdvancementRate(Enum):
    """Experience advancement rate options."""
    SLOW = auto()              # Slow progression
    STANDARD = auto()          # Normal progression
    FAST = auto()              # Accelerated progression
    MILESTONE = auto()         # Story-based progression

# ============ ABILITY SCORE IMPROVEMENT ============

class ASIType(Enum):
    """Ability Score Improvement types."""
    ABILITY_INCREASE = auto()   # +2 to one ability or +1 to two
    FEAT = auto()              # Take a feat instead
    MIXED = auto()             # +1 ability and half-feat

class StatProgression(Enum):
    """Ability score progression styles."""
    BALANCED = auto()          # Even distribution
    FOCUSED = auto()           # Primary stat focus
    SPECIALIZED = auto()       # Single stat maximization
    FLEXIBLE = auto()          # Situational choices

# ============ SKILL AND PROFICIENCY PROGRESSION ============

class ProficiencyGrowth(Enum):
    """Proficiency acquisition patterns."""
    STANDARD = auto()          # Class-based progression
    EXPANDED = auto()          # Additional proficiencies
    EXPERTISE = auto()         # Double proficiency bonus
    VERSATILE = auto()         # Flexible skill selection

class LanguageProgression(Enum):
    """Language learning progression."""
    STATIC = auto()            # Starting languages only
    GRADUAL = auto()           # Learn over time
    CULTURAL = auto()          # Background-based acquisition
    ADVENTURE = auto()         # Story-driven learning

# ============ SPELL PROGRESSION ============

class SpellProgression(Enum):
    """Spellcasting progression types."""
    FULL_CASTER = auto()       # Wizard, Sorcerer, etc.
    HALF_CASTER = auto()       # Paladin, Ranger, etc.
    THIRD_CASTER = auto()      # Fighter (EK), Rogue (AT)
    NON_CASTER = auto()        # No spellcasting
    WARLOCK = auto()           # Unique progression

class SpellKnownType(Enum):
    """Spell learning mechanisms."""
    KNOWN = auto()             # Fixed spells known
    PREPARED = auto()          # Prepare from full list
    RITUAL = auto()            # Ritual casting only
    INNATE = auto()            # Racial/feature spells

# ============ FEATURE PROGRESSION ============

class FeatureType(Enum):
    """Character feature categories."""
    CLASS_FEATURE = auto()     # Core class abilities
    SUBCLASS_FEATURE = auto()  # Archetype abilities
    RACIAL_FEATURE = auto()    # Species abilities
    BACKGROUND_FEATURE = auto() # Background abilities
    FEAT_FEATURE = auto()      # Feat-granted abilities

class ScalingType(Enum):
    """Feature scaling mechanisms."""
    LEVEL_BASED = auto()       # Scales with character level
    CLASS_BASED = auto()       # Scales with class level
    PROFICIENCY = auto()       # Scales with proficiency bonus
    STATIC = auto()            # No scaling

# ============ PROGRESSION MAPPINGS ============

TIER_LEVEL_RANGES = {
    LevelTier.TIER_1: range(1, 5),
    LevelTier.TIER_2: range(5, 11),
    LevelTier.TIER_3: range(11, 17),
    LevelTier.TIER_4: range(17, 21)
}

ASI_LEVELS = {
    "standard": [4, 8, 12, 16, 19],
    "fighter": [4, 6, 8, 12, 14, 16, 19],
    "rogue": [4, 8, 10, 12, 16, 19]
}

SPELL_SLOT_PROGRESSION = {
    SpellProgression.FULL_CASTER: 1.0,
    SpellProgression.HALF_CASTER: 0.5,
    SpellProgression.THIRD_CASTER: 0.33,
    SpellProgression.WARLOCK: "unique",
    SpellProgression.NON_CASTER: 0.0
}

# ============ UTILITY FUNCTIONS ============

def get_tier_for_level(level: int) -> LevelTier:
    """Get character tier for given level."""
    for tier, level_range in TIER_LEVEL_RANGES.items():
        if level in level_range:
            return tier
    return LevelTier.TIER_1

def get_asi_levels(class_name: str = "standard") -> list:
    """Get ASI levels for class."""
    return ASI_LEVELS.get(class_name.lower(), ASI_LEVELS["standard"])

def has_asi_at_level(level: int, class_name: str = "standard") -> bool:
    """Check if class gets ASI at specific level."""
    return level in get_asi_levels(class_name)

def get_spell_slot_multiplier(progression: SpellProgression) -> float:
    """Get spell slot progression multiplier."""
    multiplier = SPELL_SLOT_PROGRESSION.get(progression, 0.0)
    return multiplier if isinstance(multiplier, float) else 0.0

def is_caster(progression: SpellProgression) -> bool:
    """Check if progression type has spellcasting."""
    return progression != SpellProgression.NON_CASTER

def requires_spell_preparation(spell_type: SpellKnownType) -> bool:
    """Check if spell type requires daily preparation."""
    return spell_type == SpellKnownType.PREPARED

def scales_with_level(scaling: ScalingType) -> bool:
    """Check if feature scales with character advancement."""
    return scaling in [ScalingType.LEVEL_BASED, ScalingType.CLASS_BASED, ScalingType.PROFICIENCY]

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Progression types
    'ProgressionType',
    'LevelTier',
    'AdvancementRate',
    
    # Ability progression
    'ASIType',
    'StatProgression',
    
    # Skill progression
    'ProficiencyGrowth',
    'LanguageProgression',
    
    # Spell progression
    'SpellProgression',
    'SpellKnownType',
    
    # Feature progression
    'FeatureType',
    'ScalingType',
    
    # Mappings
    'TIER_LEVEL_RANGES',
    'ASI_LEVELS',
    'SPELL_SLOT_PROGRESSION',
    
    # Utility functions
    'get_tier_for_level',
    'get_asi_levels',
    'has_asi_at_level',
    'get_spell_slot_multiplier',
    'is_caster',
    'requires_spell_preparation',
    'scales_with_level',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential character progression type enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "progression_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}