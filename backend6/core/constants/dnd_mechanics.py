"""
D&D 5e/2024 Core Mechanics Constants.

Immutable constants representing the fundamental rules and mechanics of D&D 5e/2024.
These are foundational domain knowledge that never changes and forms the basis
for all content generation and validation.
"""

from typing import Dict, List, Tuple, Any


# ============ CORE ABILITY SYSTEM ============

ABILITY_SCORES = [
    "Strength", "Dexterity", "Constitution", 
    "Intelligence", "Wisdom", "Charisma"
]

ABILITY_SCORE_RANGES = {
    "minimum": 1,
    "standard_minimum": 8,
    "maximum": 30,
    "standard_maximum": 20,
    "starting_standard": 15,
    "starting_point_buy": 27
}

# Ability modifier calculation
def get_ability_modifier(score: int) -> int:
    """Calculate ability modifier from ability score."""
    return (score - 10) // 2

ABILITY_MODIFIERS = {
    score: get_ability_modifier(score) 
    for score in range(1, 31)
}

# ============ SKILLS SYSTEM ============

SKILLS_BY_ABILITY = {
    "Strength": ["Athletics"],
    "Dexterity": ["Acrobatics", "Sleight of Hand", "Stealth"],
    "Intelligence": ["Arcana", "History", "Investigation", "Nature", "Religion"],
    "Wisdom": ["Animal Handling", "Insight", "Medicine", "Perception", "Survival"],
    "Charisma": ["Deception", "Intimidation", "Performance", "Persuasion"]
}

# Flattened skills list
ALL_SKILLS = [
    skill for skill_list in SKILLS_BY_ABILITY.values() 
    for skill in skill_list
]

SKILL_TO_ABILITY = {
    skill: ability 
    for ability, skills in SKILLS_BY_ABILITY.items() 
    for skill in skills
}

# ============ MAGIC SYSTEM ============

SPELL_SCHOOLS = [
    "Abjuration", "Conjuration", "Divination", "Enchantment",
    "Evocation", "Illusion", "Necromancy", "Transmutation"
]

SPELL_LEVELS = list(range(0, 10))  # 0 (cantrips) through 9

SPELL_COMPONENTS = {
    "verbal": "V",
    "somatic": "S", 
    "material": "M"
}

SPELL_DURATIONS = [
    "Instantaneous", "1 round", "1 minute", "10 minutes",
    "1 hour", "8 hours", "24 hours", "7 days", "30 days",
    "Until dispelled", "Concentration"
]

SPELL_RANGES = [
    "Self", "Touch", "5 feet", "10 feet", "30 feet", "60 feet",
    "90 feet", "120 feet", "150 feet", "300 feet", "500 feet",
    "1 mile", "Sight", "Unlimited"
]

CASTING_TIMES = [
    "1 action", "1 bonus action", "1 reaction", "1 minute",
    "10 minutes", "1 hour", "8 hours", "12 hours", "24 hours"
]

# Spell slot progression by class level
FULL_CASTER_SPELL_SLOTS = {
    1: [2, 0, 0, 0, 0, 0, 0, 0, 0],
    2: [3, 0, 0, 0, 0, 0, 0, 0, 0],
    3: [4, 2, 0, 0, 0, 0, 0, 0, 0],
    4: [4, 3, 0, 0, 0, 0, 0, 0, 0],
    5: [4, 3, 2, 0, 0, 0, 0, 0, 0],
    # ... continue for all levels
}

# ============ COMBAT SYSTEM ============

DAMAGE_TYPES = [
    "Acid", "Bludgeoning", "Cold", "Fire", "Force", "Lightning",
    "Necrotic", "Piercing", "Poison", "Psychic", "Radiant", 
    "Slashing", "Thunder"
]

PHYSICAL_DAMAGE_TYPES = ["Bludgeoning", "Piercing", "Slashing"]
ELEMENTAL_DAMAGE_TYPES = ["Acid", "Cold", "Fire", "Lightning", "Thunder"]
ENERGY_DAMAGE_TYPES = ["Force", "Necrotic", "Psychic", "Radiant"]

CONDITIONS = [
    "Blinded", "Charmed", "Deafened", "Frightened", "Grappled",
    "Incapacitated", "Invisible", "Paralyzed", "Petrified", "Poisoned",
    "Prone", "Restrained", "Stunned", "Unconscious"
]

ARMOR_TYPES = {
    "light": ["Padded", "Leather", "Studded leather"],
    "medium": ["Hide", "Chain shirt", "Scale mail", "Breastplate", "Half plate"],
    "heavy": ["Ring mail", "Chain mail", "Splint", "Plate"]
}

WEAPON_CATEGORIES = {
    "simple_melee": ["Club", "Dagger", "Dart", "Javelin", "Mace", "Quarterstaff", 
                     "Sickle", "Spear"],
    "simple_ranged": ["Light crossbow", "Dart", "Shortbow", "Sling"],
    "martial_melee": ["Battleaxe", "Flail", "Glaive", "Greataxe", "Greatsword",
                      "Halberd", "Lance", "Longsword", "Maul", "Morningstar",
                      "Pike", "Rapier", "Scimitar", "Shortsword", "Trident",
                      "War pick", "Warhammer", "Whip"],
    "martial_ranged": ["Blowgun", "Hand crossbow", "Heavy crossbow", "Longbow", "Net"]
}

WEAPON_PROPERTIES = [
    "Ammunition", "Finesse", "Heavy", "Light", "Loading",
    "Range", "Reach", "Special", "Thrown", "Two-Handed", "Versatile"
]

# ============ CHARACTER PROGRESSION ============

PROFICIENCY_BONUS_BY_LEVEL = {
    1: 2, 2: 2, 3: 2, 4: 2, 5: 3, 6: 3, 7: 3, 8: 3,
    9: 4, 10: 4, 11: 4, 12: 4, 13: 5, 14: 5, 15: 5, 16: 5,
    17: 6, 18: 6, 19: 6, 20: 6
}

ABILITY_SCORE_IMPROVEMENT_LEVELS = [4, 8, 12, 16, 19]

POWER_TIERS = {
    "tier_1": {"levels": (1, 4), "description": "Local Heroes"},
    "tier_2": {"levels": (5, 10), "description": "Heroes of the Realm"},
    "tier_3": {"levels": (11, 16), "description": "Masters of the Realm"},
    "tier_4": {"levels": (17, 20), "description": "Masters of the World"}
}

def get_power_tier(level: int) -> str:
    """Get power tier for a given character level."""
    for tier, data in POWER_TIERS.items():
        min_level, max_level = data["levels"]
        if min_level <= level <= max_level:
            return tier
    return "unknown"

# ============ CREATURE SYSTEM ============

CREATURE_SIZES = [
    "Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"
]

CREATURE_TYPES = [
    "Aberration", "Beast", "Celestial", "Construct", "Dragon", "Elemental",
    "Fey", "Fiend", "Giant", "Humanoid", "Monstrosity", "Ooze",
    "Plant", "Undead"
]

ALIGNMENTS = [
    "Lawful Good", "Neutral Good", "Chaotic Good",
    "Lawful Neutral", "True Neutral", "Chaotic Neutral",
    "Lawful Evil", "Neutral Evil", "Chaotic Evil"
]

# ============ EQUIPMENT AND ECONOMY ============

CURRENCY_CONVERSION = {
    "cp": 1,     # Copper piece (base unit)
    "sp": 10,    # Silver piece
    "ep": 50,    # Electrum piece
    "gp": 100,   # Gold piece
    "pp": 1000   # Platinum piece
}

EQUIPMENT_CATEGORIES = [
    "Armor", "Weapons", "Adventuring Gear", "Tools", "Mounts and Vehicles",
    "Trade Goods", "Magic Items"
]

RARITY_LEVELS = [
    "Common", "Uncommon", "Rare", "Very Rare", "Legendary", "Artifact"
]

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

# ============ MULTICLASSING REQUIREMENTS ============

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

# ============ UTILITY FUNCTIONS ============

def is_valid_ability_score(score: int) -> bool:
    """Check if ability score is within valid range."""
    return ABILITY_SCORE_RANGES["minimum"] <= score <= ABILITY_SCORE_RANGES["maximum"]

def get_proficiency_bonus(level: int) -> int:
    """Get proficiency bonus for character level."""
    return PROFICIENCY_BONUS_BY_LEVEL.get(level, 2)

def convert_currency(amount: int, from_currency: str, to_currency: str) -> float:
    """Convert between currency types."""
    from_value = CURRENCY_CONVERSION.get(from_currency.lower(), 1)
    to_value = CURRENCY_CONVERSION.get(to_currency.lower(), 1)
    
    # Convert to copper pieces, then to target currency
    copper_value = amount * from_value
    return copper_value / to_value

def is_spell_level_valid(spell_level: int) -> bool:
    """Check if spell level is valid."""
    return spell_level in SPELL_LEVELS

def get_spell_slots_for_level(character_level: int, caster_type: str = "full") -> List[int]:
    """Get spell slots for character level and caster type."""
    if caster_type == "full":
        return FULL_CASTER_SPELL_SLOTS.get(character_level, [0] * 9)
    # Add half-caster and third-caster logic as needed
    return [0] * 9