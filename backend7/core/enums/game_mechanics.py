"""
Essential D&D Game Mechanics Enums

Streamlined game mechanics classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CORE ABILITY MECHANICS ============

class AbilityScore(Enum):
    """Core ability score types."""
    STRENGTH = "STR"
    DEXTERITY = "DEX"
    CONSTITUTION = "CON"
    INTELLIGENCE = "INT"
    WISDOM = "WIS"
    CHARISMA = "CHA"

class SavingThrow(Enum):
    """Saving throw types."""
    STRENGTH = auto()
    DEXTERITY = auto()
    CONSTITUTION = auto()
    INTELLIGENCE = auto()
    WISDOM = auto()
    CHARISMA = auto()

class SkillType(Enum):
    """Skill categories by ability."""
    ATHLETICS = "STR"           # Strength
    ACROBATICS = "DEX"          # Dexterity
    SLEIGHT_OF_HAND = "DEX"
    STEALTH = "DEX"
    ARCANA = "INT"              # Intelligence
    HISTORY = "INT"
    INVESTIGATION = "INT"
    NATURE = "INT"
    RELIGION = "INT"
    ANIMAL_HANDLING = "WIS"     # Wisdom
    INSIGHT = "WIS"
    MEDICINE = "WIS"
    PERCEPTION = "WIS"
    SURVIVAL = "WIS"
    DECEPTION = "CHA"           # Charisma
    INTIMIDATION = "CHA"
    PERFORMANCE = "CHA"
    PERSUASION = "CHA"

# ============ COMBAT MECHANICS ============

class ActionEconomy(Enum):
    """Combat action types."""
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    FREE_ACTION = auto()
    MOVEMENT = auto()

class AttackType(Enum):
    """Attack classifications."""
    MELEE = auto()
    RANGED = auto()
    SPELL = auto()
    NATURAL = auto()

class DamageType(Enum):
    """Damage type classifications."""
    ACID = auto()
    BLUDGEONING = auto()
    COLD = auto()
    FIRE = auto()
    FORCE = auto()
    LIGHTNING = auto()
    NECROTIC = auto()
    PIERCING = auto()
    POISON = auto()
    PSYCHIC = auto()
    RADIANT = auto()
    SLASHING = auto()
    THUNDER = auto()

class Condition(Enum):
    """Status conditions."""
    BLINDED = auto()
    CHARMED = auto()
    DEAFENED = auto()
    EXHAUSTION = auto()
    FRIGHTENED = auto()
    GRAPPLED = auto()
    INCAPACITATED = auto()
    INVISIBLE = auto()
    PARALYZED = auto()
    PETRIFIED = auto()
    POISONED = auto()
    PRONE = auto()
    RESTRAINED = auto()
    STUNNED = auto()
    UNCONSCIOUS = auto()

# ============ MAGIC MECHANICS ============

class SpellSchool(Enum):
    """Schools of magic."""
    ABJURATION = auto()
    CONJURATION = auto()
    DIVINATION = auto()
    ENCHANTMENT = auto()
    EVOCATION = auto()
    ILLUSION = auto()
    NECROMANCY = auto()
    TRANSMUTATION = auto()

class SpellLevel(Enum):
    """Spell level classifications."""
    CANTRIP = 0
    FIRST = 1
    SECOND = 2
    THIRD = 3
    FOURTH = 4
    FIFTH = 5
    SIXTH = 6
    SEVENTH = 7
    EIGHTH = 8
    NINTH = 9

class CastingTime(Enum):
    """Spell casting time categories."""
    ACTION = auto()
    BONUS_ACTION = auto()
    REACTION = auto()
    MINUTE = auto()
    HOUR = auto()
    RITUAL = auto()

class SpellRange(Enum):
    """Spell range categories."""
    SELF = auto()
    TOUCH = auto()
    RANGED = auto()
    SIGHT = auto()
    UNLIMITED = auto()

# ============ DICE MECHANICS ============

class DiceType(Enum):
    """Standard dice types."""
    D4 = 4
    D6 = 6
    D8 = 8
    D10 = 10
    D12 = 12
    D20 = 20
    D100 = 100

class AdvantageType(Enum):
    """Advantage/disadvantage mechanics."""
    DISADVANTAGE = -1
    NORMAL = 0
    ADVANTAGE = 1

# ============ UTILITY FUNCTIONS ============

def get_ability_modifier(score: int) -> int:
    """Calculate ability modifier from score."""
    return (score - 10) // 2

def get_proficiency_bonus(level: int) -> int:
    """Get proficiency bonus for character level."""
    return 2 + ((level - 1) // 4)

def is_physical_ability(ability: AbilityScore) -> bool:
    """Check if ability is physical (STR, DEX, CON)."""
    return ability in [AbilityScore.STRENGTH, AbilityScore.DEXTERITY, AbilityScore.CONSTITUTION]

def is_mental_ability(ability: AbilityScore) -> bool:
    """Check if ability is mental (INT, WIS, CHA)."""
    return ability in [AbilityScore.INTELLIGENCE, AbilityScore.WISDOM, AbilityScore.CHARISMA]

def get_skill_ability(skill: SkillType) -> str:
    """Get the ability score associated with a skill."""
    return skill.value

def is_damaging_spell_school(school: SpellSchool) -> bool:
    """Check if spell school typically deals damage."""
    return school in [SpellSchool.EVOCATION, SpellSchool.NECROMANCY]

def is_control_spell_school(school: SpellSchool) -> bool:
    """Check if spell school focuses on control."""
    return school in [SpellSchool.ENCHANTMENT, SpellSchool.ILLUSION, SpellSchool.TRANSMUTATION]

# ============ MECHANICAL MAPPINGS ============

ABILITY_SKILLS = {
    AbilityScore.STRENGTH: [SkillType.ATHLETICS],
    AbilityScore.DEXTERITY: [SkillType.ACROBATICS, SkillType.SLEIGHT_OF_HAND, SkillType.STEALTH],
    AbilityScore.INTELLIGENCE: [SkillType.ARCANA, SkillType.HISTORY, SkillType.INVESTIGATION, SkillType.NATURE, SkillType.RELIGION],
    AbilityScore.WISDOM: [SkillType.ANIMAL_HANDLING, SkillType.INSIGHT, SkillType.MEDICINE, SkillType.PERCEPTION, SkillType.SURVIVAL],
    AbilityScore.CHARISMA: [SkillType.DECEPTION, SkillType.INTIMIDATION, SkillType.PERFORMANCE, SkillType.PERSUASION]
}

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Abilities and skills
    'AbilityScore',
    'SavingThrow',
    'SkillType',
    
    # Combat mechanics
    'ActionEconomy',
    'AttackType',
    'DamageType',
    'Condition',
    
    # Magic mechanics
    'SpellSchool',
    'SpellLevel',
    'CastingTime',
    'SpellRange',
    
    # Dice and advantage
    'DiceType',
    'AdvantageType',
    
    # Mappings
    'ABILITY_SKILLS',
    
    # Utility functions
    'get_ability_modifier',
    'get_proficiency_bonus',
    'is_physical_ability',
    'is_mental_ability',
    'get_skill_ability',
    'is_damaging_spell_school',
    'is_control_spell_school',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D game mechanics enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "game_mechanics_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}