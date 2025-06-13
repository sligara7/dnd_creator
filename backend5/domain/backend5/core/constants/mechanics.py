# File: /backend5/core/constants/mechanics.py

# D&D 5e Game Mechanics Constants

# Combat Constants
INITIATIVE_MODIFIER = 2  # Base initiative modifier
AC_BASE = 10              # Base Armor Class

# Damage Constants
DAMAGE_TYPES = [
    "bludgeoning",
    "piercing",
    "slashing",
    "fire",
    "cold",
    "lightning",
    "poison",
    "necrotic",
    "radiant",
    "psychic",
    "thunder",
]

# Ability Score Constants
ABILITY_SCORE_MIN = 1
ABILITY_SCORE_MAX = 20

# Proficiency Constants
PROFICIENCY_BONUS = {
    1: 2,
    5: 3,
    9: 4,
    13: 5,
    17: 6,
}

# Spell Slot Levels
SPELL_SLOT_LEVELS = [1, 2, 3, 4, 5, 6, 7, 8, 9]

# Miscellaneous Constants
MAX_HIT_DICE = 20  # Maximum number of hit dice for a character
MAX_LEVEL = 20     # Maximum character level in D&D 5e