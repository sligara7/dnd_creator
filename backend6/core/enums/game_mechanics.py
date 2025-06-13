"""
Core D&D 5e/2024 Game Mechanics Enumerations.

These enums represent the fundamental, unchangeable D&D mechanics that form
the foundation of the character creation system. They are infrastructure-independent
and represent pure business concepts.
"""

from enum import Enum


class Ability(Enum):
    """The six core abilities in D&D 5e/2024."""
    STRENGTH = "strength"
    DEXTERITY = "dexterity"
    CONSTITUTION = "constitution"
    INTELLIGENCE = "intelligence"
    WISDOM = "wisdom"
    CHARISMA = "charisma"


class Skill(Enum):
    """Official skills in D&D 5e/2024."""
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
    """Proficiency levels for skills in D&D 5e/2024."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2


class DamageType(Enum):
    """Official damage types in D&D 5e/2024."""
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


class ActionType(Enum):
    """D&D action economy types."""
    ACTION = "action"
    BONUS_ACTION = "bonus_action"
    REACTION = "reaction"
    FREE = "free"
    LEGENDARY = "legendary"
    MYTHIC = "mythic"


class Condition(Enum):
    """Official conditions in D&D 5e/2024."""
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


class MagicSchool(Enum):
    """Schools of magic in D&D 5e/2024."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"


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


class SpellRange(Enum):
    """Spell ranges in D&D."""
    SELF = "self"
    TOUCH = "touch"
    SIGHT = "sight"
    UNLIMITED = "unlimited"


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


class AreaOfEffect(Enum):
    """Area of effect shapes in D&D."""
    CONE = "cone"
    CUBE = "cube"
    CYLINDER = "cylinder"
    LINE = "line"
    SPHERE = "sphere"
    EMANATION = "emanation"


class Currency(Enum):
    """Official currency in D&D 5e/2024."""
    CP = "cp"  # Copper piece
    SP = "sp"  # Silver piece
    EP = "ep"  # Electrum piece
    GP = "gp"  # Gold piece
    PP = "pp"  # Platinum piece


class PowerTier(Enum):
    """Power tiers matching D&D 5e level ranges."""
    TIER_1 = "tier_1"    # Levels 1-4: Local heroes
    TIER_2 = "tier_2"    # Levels 5-10: Heroes of the realm
    TIER_3 = "tier_3"    # Levels 11-16: Masters of the realm
    TIER_4 = "tier_4"    # Levels 17-20: Masters of the world
    
    @property
    def level_range(self) -> tuple[int, int]:
        """Get the level range for this tier."""
        ranges = {
            self.TIER_1: (1, 4),
            self.TIER_2: (5, 10),
            self.TIER_3: (11, 16),
            self.TIER_4: (17, 20)
        }
        return ranges[self]
    
    @classmethod
    def from_level(cls, level: int) -> 'PowerTier':
        """Get power tier for a specific level."""
        if 1 <= level <= 4:
            return cls.TIER_1
        elif 5 <= level <= 10:
            return cls.TIER_2
        elif 11 <= level <= 16:
            return cls.TIER_3
        elif 17 <= level <= 20:
            return cls.TIER_4
        else:
            raise ValueError(f"Invalid level: {level}")