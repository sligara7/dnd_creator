"""Enums for the character service.

This module provides enums used across the character service models.
"""

from enum import Enum

class ProficiencyLevel(str, Enum):
    """Levels of proficiency."""
    NONE = "none"
    PROFICIENT = "proficient"
    EXPERT = "expert"

class FeatureType(str, Enum):
    """Types of character features."""
    SPECIES_TRAIT = "species_trait"
    CLASS_FEATURE = "class_feature"
    BACKGROUND_FEATURE = "background_feature"
    FEAT_ABILITY = "feat_ability"
    MAGIC_ITEM_PROPERTY = "magic_item_property"
    SPELL_ABILITY = "spell_ability"
    TEMPORARY_EFFECT = "temporary_effect"

class FeatureCategory(str, Enum):
    """Categories of character features."""
    COMBAT = "combat"
    EXPLORATION = "exploration"
    SOCIAL = "social"
    SPELLCASTING = "spellcasting"
    UTILITY = "utility"
    PASSIVE = "passive"
    DEFENSE = "defense"
    MOVEMENT = "movement"

class FeatureUsage(str, Enum):
    """How often a feature can be used."""
    ALWAYS = "always"
    PER_TURN = "per_turn"
    PER_SHORT_REST = "per_short_rest"
    PER_LONG_REST = "per_long_rest"
    PER_DAY = "per_day"
    LIMITED_USE = "limited_use"
    ONE_TIME = "one_time"

class AbilityType(str, Enum):
    """Ability score types."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"

class AlignmentMoral(str, Enum):
    """Moral alignment axis."""
    GOOD = "good"
    NEUTRAL = "neutral"
    EVIL = "evil"

class AlignmentEthical(str, Enum):
    """Ethical alignment axis."""
    LAWFUL = "lawful"
    NEUTRAL = "neutral"
    CHAOTIC = "chaotic"

class WeaponType(str, Enum):
    """Types of weapons."""
    SIMPLE_MELEE = "simple_melee"
    SIMPLE_RANGED = "simple_ranged"
    MARTIAL_MELEE = "martial_melee"
    MARTIAL_RANGED = "martial_ranged"
    NATURAL = "natural"
    IMPROVISED = "improvised"

class ArmorType(str, Enum):
    """Types of armor."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

class DamageType(str, Enum):
    """Types of damage."""
    ACID = "acid"
    BLUDGEONING = "bludgeoning"
    COLD = "cold"
    FIRE = "fire"
    FORCE = "force"
    LIGHTNING = "lightning"
    NECROTIC = "necrotic"
    PIERCING = "piercing"
    POISON = "poison"
    PSYCHIC = "psychic"
    RADIANT = "radiant"
    SLASHING = "slashing"
    THUNDER = "thunder"

class Condition(str, Enum):
    """Character conditions."""
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    FRIGHTENED = "frightened"
    GRAPPLED = "grappled"
    INCAPACITATED = "incapacitated"
    INVISIBLE = "invisible"
    PARALYZED = "paralyzed"
    PETRIFIED = "petrified"
    POISONED = "poisoned"
    PRONE = "prone"
    RESTRAINED = "restrained"
    STUNNED = "stunned"
    UNCONSCIOUS = "unconscious"
    EXHAUSTION = "exhaustion"

class Size(str, Enum):
    """Character/creature sizes."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

class MovementType(str, Enum):
    """Types of movement."""
    WALK = "walk"
    SWIM = "swim"
    FLY = "fly"
    CLIMB = "climb"
    BURROW = "burrow"
    HOVER = "hover"

class VisionType(str, Enum):
    """Types of vision."""
    NORMAL = "normal"
    DARKVISION = "darkvision"
    BLINDSIGHT = "blindsight"
    TREMORSENSE = "tremorsense"
    TRUESIGHT = "truesight"

class Rarity(str, Enum):
    """Item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"
