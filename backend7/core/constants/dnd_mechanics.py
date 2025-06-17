"""
Essential D&D 5e/2024 Core Mechanics Constants

Streamlined constants focusing only on essential character creation mechanics.
Based on crude_functional.py patterns and backend7 architecture simplification.
"""

# ============ CORE ABILITY SCORES ============

ABILITY_SCORES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]

ABILITY_SCORE_RANGES = {
    "minimum": 1,
    "maximum": 30,
    "standard_array": [15, 14, 13, 12, 10, 8],
    "point_buy_range": (8, 15),
    "starting_maximum": 20  # Before epic levels
}

def get_ability_modifier(score: int) -> int:
    """Calculate ability modifier from score."""
    return (score - 10) // 2

def is_valid_ability_score(score: int) -> bool:
    """Check if ability score is within valid range."""
    return ABILITY_SCORE_RANGES["minimum"] <= score <= ABILITY_SCORE_RANGES["maximum"]

# ============ SKILLS AND PROFICIENCIES ============

SKILLS_BY_ABILITY = {
    "Strength": ["Athletics"],
    "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"],
    "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
    "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
    "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
}

ALL_SKILLS = [skill for skills in SKILLS_BY_ABILITY.values() for skill in skills]

SKILL_TO_ABILITY = {
    skill: ability 
    for ability, skills in SKILLS_BY_ABILITY.items() 
    for skill in skills
}

PROFICIENCY_BONUS_BY_LEVEL = {
    level: 2 + ((level - 1) // 4)
    for level in range(1, 21)
}

def get_proficiency_bonus(level: int) -> int:
    """Get proficiency bonus for character level."""
    return PROFICIENCY_BONUS_BY_LEVEL.get(level, 2)

# ============ DAMAGE TYPES ============

DAMAGE_TYPES = [
    "Acid", "Bludgeoning", "Cold", "Fire", "Force", "Lightning", 
    "Necrotic", "Piercing", "Poison", "Psychic", "Radiant", "Slashing", "Thunder"
]

# ============ CONDITIONS ============

CONDITIONS = [
    "Blinded", "Charmed", "Deafened", "Exhaustion", "Frightened", "Grappled",
    "Incapacitated", "Invisible", "Paralyzed", "Petrified", "Poisoned", 
    "Prone", "Restrained", "Stunned", "Unconscious"
]

# ============ SPELL MECHANICS ============

SPELL_SCHOOLS = [
    "Abjuration", "Conjuration", "Divination", "Enchantment",
    "Evocation", "Illusion", "Necromancy", "Transmutation"
]

SPELL_LEVELS = list(range(0, 10))  # 0 (cantrip) through 9

CANTRIP_DAMAGE_SCALING = {
    1: 1,   # 1st-4th level: 1 die
    5: 2,   # 5th-10th level: 2 dice  
    11: 3,  # 11th-16th level: 3 dice
    17: 4   # 17th-20th level: 4 dice
}

def get_cantrip_dice_count(character_level: int) -> int:
    """Get number of damage dice for cantrips at given level."""
    for level_threshold in sorted(CANTRIP_DAMAGE_SCALING.keys(), reverse=True):
        if character_level >= level_threshold:
            return CANTRIP_DAMAGE_SCALING[level_threshold]
    return 1

# ============ CHARACTER PROGRESSION ============

LEVEL_RANGES = {
    "tier_1": range(1, 5),   # Local Heroes
    "tier_2": range(5, 11),  # Heroes of the Realm  
    "tier_3": range(11, 17), # Masters of the Realm
    "tier_4": range(17, 21)  # Masters of the World
}

POWER_TIERS = {
    "tier_1": {"name": "Local Heroes", "levels": (1, 4)},
    "tier_2": {"name": "Heroes of the Realm", "levels": (5, 10)},
    "tier_3": {"name": "Masters of the Realm", "levels": (11, 16)},
    "tier_4": {"name": "Masters of the World", "levels": (17, 20)}
}

def get_power_tier(level: int) -> str:
    """Get power tier name for character level."""
    for tier, info in POWER_TIERS.items():
        if info["levels"][0] <= level <= info["levels"][1]:
            return tier
    return "tier_1"

# ============ MULTICLASSING ============

MULTICLASS_REQUIREMENTS = {
    "Barbarian": {"Strength": 13},
    "Bard": {"Charisma": 13},
    "Cleric": {"Wisdom": 13},
    "Druid": {"Wisdom": 13},
    "Fighter": {"Strength": 13, "Dexterity": 13},  # Either/or
    "Monk": {"Dexterity": 13, "Wisdom": 13},
    "Paladin": {"Strength": 13, "Charisma": 13},
    "Ranger": {"Dexterity": 13, "Wisdom": 13},
    "Rogue": {"Dexterity": 13},
    "Sorcerer": {"Charisma": 13},
    "Warlock": {"Charisma": 13},
    "Wizard": {"Intelligence": 13}
}

# ============ CURRENCY AND ECONOMICS ============

CURRENCY_CONVERSION = {
    "cp": 1,      # Copper pieces (base)
    "sp": 10,     # Silver pieces
    "ep": 50,     # Electrum pieces  
    "gp": 100,    # Gold pieces
    "pp": 1000    # Platinum pieces
}

def convert_currency(amount: int, from_currency: str, to_currency: str) -> float:
    """Convert between currency types."""
    cp_value = amount * CURRENCY_CONVERSION[from_currency]
    return cp_value / CURRENCY_CONVERSION[to_currency]

# ============ LANGUAGES ============

STANDARD_LANGUAGES = [
    "Common", "Dwarvish", "Elvish", "Giant", "Gnomish", "Goblin", 
    "Halfling", "Orc"
]

EXOTIC_LANGUAGES = [
    "Abyssal", "Celestial", "Draconic", "Deep Speech", "Infernal",
    "Primordial", "Sylvan", "Undercommon"
]

ALL_LANGUAGES = STANDARD_LANGUAGES + EXOTIC_LANGUAGES

# ============ BASIC EQUIPMENT CATEGORIES ============

WEAPON_PROPERTIES = [
    "Ammunition", "Finesse", "Heavy", "Light", "Loading", "Range",
    "Reach", "Special", "Thrown", "Two-Handed", "Versatile"
]

CREATURE_SIZES = [
    "Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"
]

# ============ VALIDATION HELPERS ============

def validate_character_level(level: int) -> bool:
    """Validate character level is within acceptable range."""
    return 1 <= level <= 20

def calculate_ability_modifier(score: int) -> int:
    """Calculate ability modifier (alias for get_ability_modifier)."""
    return get_ability_modifier(score)

def calculate_proficiency_bonus(level: int) -> int:
    """Calculate proficiency bonus (alias for get_proficiency_bonus)."""
    return get_proficiency_bonus(level)

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core mechanics
    'ABILITY_SCORES',
    'ABILITY_SCORE_RANGES', 
    'SKILLS_BY_ABILITY',
    'ALL_SKILLS',
    'SKILL_TO_ABILITY',
    'PROFICIENCY_BONUS_BY_LEVEL',
    
    # Magic system
    'SPELL_SCHOOLS',
    'SPELL_LEVELS',
    'CANTRIP_DAMAGE_SCALING',
    
    # Combat and conditions
    'DAMAGE_TYPES',
    'CONDITIONS',
    'WEAPON_PROPERTIES',
    
    # Character progression
    'LEVEL_RANGES',
    'POWER_TIERS',
    'MULTICLASS_REQUIREMENTS',
    
    # World elements
    'CURRENCY_CONVERSION',
    'ALL_LANGUAGES',
    'CREATURE_SIZES',
    
    # Utility functions
    'get_ability_modifier',
    'is_valid_ability_score',
    'get_proficiency_bonus',
    'get_cantrip_dice_count',
    'get_power_tier',
    'convert_currency',
    'validate_character_level',
    'calculate_ability_modifier',
    'calculate_proficiency_bonus',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D 5e/2024 core mechanics constants'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/constants",  
    "focus": "essential_mechanics_only",
    "line_target": 200,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_simplicity"
}