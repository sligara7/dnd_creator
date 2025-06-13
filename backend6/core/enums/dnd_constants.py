from enum import Enum, auto


class Ability(Enum):
    """The six core abilities in D&D 5e."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class Skill(Enum):
    """Official skills in D&D 5e (2024 Edition)."""
    ACROBATICS = "acrobatics"
    ANIMAL_HANDLING = "animal_handling"
    ARCANA = "arcana"
    ATHLETICS = "athletics"
    DECEPTION = "deception"
    HISTORY = "history"
    INSIGHT = "insight"
    INTIMIDATION = "intimidation"
    INVESTIGATION = "investigation"
    MEDICINE = "medicine"
    NATURE = "nature"
    PERCEPTION = "perception"
    PERFORMANCE = "performance"
    PERSUASION = "persuasion"
    RELIGION = "religion"
    SLEIGHT_OF_HAND = "sleight_of_hand"
    STEALTH = "stealth"
    SURVIVAL = "survival"


class ProficiencyLevel(Enum):
    """Proficiency levels for skills in D&D 5e (2024 Edition)."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2


class DamageType(Enum):
    """Official damage types in D&D 5e (2024 Edition)."""
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


class Condition(Enum):
    """Official conditions in D&D 5e (2024 Edition)."""
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


class SpellcastingType(Enum):
    """Types of spellcasting in D&D 5e (2024 Edition)."""
    NONE = "none"
    PREPARED = "prepared"
    KNOWN = "known"
    PACT = "pact"
    HYBRID = "hybrid"


class ClassResource(Enum):
    """Special resources used by different classes."""
    RAGE = "rage"
    BARDIC_INSPIRATION = "bardic_inspiration"
    CHANNEL_DIVINITY = "channel_divinity"
    WILD_SHAPE = "wild_shape"
    ACTION_SURGE = "action_surge"
    KI = "ki"
    LAY_ON_HANDS = "lay_on_hands"
    FAVORED_FOE = "favored_foe"
    SNEAK_ATTACK = "sneak_attack"
    SORCERY_POINTS = "sorcery_points"
    PACT_SLOTS = "pact_slots"
    ARCANE_RECOVERY = "arcane_recovery"


class SubclassType(Enum):
    """Types of subclasses based on when they're chosen."""
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3


class Currency(Enum):
    """Official currency in D&D 5e (2024 Edition)."""
    CP = "cp"  # Copper piece
    SP = "sp"  # Silver piece
    EP = "ep"  # Electrum piece
    GP = "gp"  # Gold piece
    PP = "pp"  # Platinum piece


class SpellLevel(Enum):
    """Spell levels in D&D."""
    CANTRIP = 0
    LEVEL_1 = 1
    LEVEL_2 = 2
    LEVEL_3 = 3
    LEVEL_4 = 4
    LEVEL_5 = 5
    LEVEL_6 = 6
    LEVEL_7 = 7
    LEVEL_8 = 8
    LEVEL_9 = 9


class CastingTime(Enum):
    """Spell casting times in D&D."""
    ACTION = "1 action"
    BONUS_ACTION = "1 bonus action"
    REACTION = "1 reaction"
    MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWELVE_HOURS = "12 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    CUSTOM = "custom"


class SpellRange(Enum):
    """Common spell ranges in D&D."""
    SELF = "self"
    TOUCH = "touch"
    SIGHT = "sight"
    UNLIMITED = "unlimited"
    CUSTOM = "custom"


class SpellDuration(Enum):
    """Spell durations in D&D."""
    INSTANTANEOUS = "instantaneous"
    ONE_ROUND = "1 round"
    ONE_MINUTE = "1 minute"
    TEN_MINUTES = "10 minutes"
    ONE_HOUR = "1 hour"
    EIGHT_HOURS = "8 hours"
    TWENTY_FOUR_HOURS = "24 hours"
    SEVEN_DAYS = "7 days"
    THIRTY_DAYS = "30 days"
    UNTIL_DISPELLED = "until dispelled"
    CUSTOM = "custom"


class MagicSchool(Enum):
    """Schools of magic in D&D."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"


class AreaOfEffect(Enum):
    """Area of effect shapes in D&D."""
    CONE = "cone"
    CUBE = "cube"
    CYLINDER = "cylinder"
    LINE = "line"
    SPHERE = "sphere"
    EMANATION = "emanation"
    CUSTOM = "custom"


class SkillCategory(Enum):
    """Categorization of skills by common usage."""
    SOCIAL = auto()
    EXPLORATION = auto()
    KNOWLEDGE = auto()
    PHYSICAL = auto()
    PERCEPTION = auto()


# D&D 2024 Mechanical Constants
class DNDConstants:
    """Mechanical constants for D&D 2024 rules."""
    
    # Core mechanics
    PROFICIENCY_BONUS_BY_LEVEL = {
        1: 2, 2: 2, 3: 2, 4: 2,
        5: 3, 6: 3, 7: 3, 8: 3,
        9: 4, 10: 4, 11: 4, 12: 4,
        13: 5, 14: 5, 15: 5, 16: 5,
        17: 6, 18: 6, 19: 6, 20: 6
    }
    
    # Ability score limits
    MAX_ABILITY_SCORE = 20
    MIN_ABILITY_SCORE = 1
    STANDARD_ABILITY_ARRAY = [15, 14, 13, 12, 10, 8]
    
    # Species balance guidelines
    MAX_SPECIES_ASI_TOTAL = 3
    TYPICAL_SPECIES_TRAITS = (2, 4)  # Min, Max recommended
    
    # Spell slot progression (full caster)
    FULL_CASTER_SPELL_SLOTS = {
        1: [0, 2, 0, 0, 0, 0, 0, 0, 0, 0],
        2: [0, 3, 0, 0, 0, 0, 0, 0, 0, 0],
        3: [0, 4, 2, 0, 0, 0, 0, 0, 0, 0],
        4: [0, 4, 3, 0, 0, 0, 0, 0, 0, 0],
        5: [0, 4, 3, 2, 0, 0, 0, 0, 0, 0],
        # ... continues to level 20
    }
    
    # Hit dice by class type
    STANDARD_HIT_DICE = {
        'weak': 6,      # Sorcerer, Wizard
        'moderate': 8,  # Bard, Cleric, Druid, Monk, Rogue, Warlock
        'strong': 10,   # Fighter, Paladin, Ranger
        'very_strong': 12  # Barbarian
    }