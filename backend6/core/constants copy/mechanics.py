"""
D&D 5e Core Mechanics Constants

Fundamental game mechanics as defined by D&D 5e rules.
These are immutable domain knowledge.
"""

# Core ability scores
ABILITY_SCORES = [
    "Strength", "Dexterity", "Constitution", 
    "Intelligence", "Wisdom", "Charisma"
]

# Skills mapped to their governing abilities
SKILLS = {
    "Acrobatics": "Dexterity",
    "Animal Handling": "Wisdom",
    "Arcana": "Intelligence",
    "Athletics": "Strength",
    "Deception": "Charisma",
    "History": "Intelligence",
    "Insight": "Wisdom",
    "Intimidation": "Charisma",
    "Investigation": "Intelligence",
    "Medicine": "Wisdom",
    "Nature": "Intelligence",
    "Perception": "Wisdom",
    "Performance": "Charisma",
    "Persuasion": "Charisma",
    "Religion": "Intelligence",
    "Sleight of Hand": "Dexterity",
    "Stealth": "Dexterity",
    "Survival": "Wisdom"
}

# Schools of magic
SPELL_SCHOOLS = [
    "Abjuration", "Conjuration", "Divination", "Enchantment",
    "Evocation", "Illusion", "Necromancy", "Transmutation"
]

# Damage types
DAMAGE_TYPES = [
    "Acid", "Bludgeoning", "Cold", "Fire", "Force", "Lightning",
    "Necrotic", "Piercing", "Poison", "Psychic", "Radiant", 
    "Slashing", "Thunder"
]

# Condition types
CONDITION_TYPES = [
    "Blinded", "Charmed", "Deafened", "Frightened", "Grappled",
    "Incapacitated", "Invisible", "Paralyzed", "Petrified", "Poisoned",
    "Prone", "Restrained", "Stunned", "Unconscious"
]

# Creature sizes
CREATURE_SIZES = [
    "Tiny", "Small", "Medium", "Large", "Huge", "Gargantuan"
]

# Armor class calculations
ARMOR_CLASS_BASES = {
    "unarmored": 10,
    "light_armor": {"base": 11, "max_dex": None},
    "medium_armor": {"base": 12, "max_dex": 2},
    "heavy_armor": {"base": 14, "max_dex": 0}
}

# Weapon properties
WEAPON_PROPERTIES = [
    "Ammunition", "Finesse", "Heavy", "Light", "Loading",
    "Range", "Reach", "Special", "Thrown", "Two-Handed", "Versatile"
]

# Spell components
SPELL_COMPONENTS = ["V", "S", "M"]  # Verbal, Somatic, Material

# Saving throw types
SAVING_THROWS = ABILITY_SCORES  # Same as ability scores