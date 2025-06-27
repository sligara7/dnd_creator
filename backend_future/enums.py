class CreationOptions(Enum):
    """Options for creating a D&D 5e character."""
    CHARACTER = "character"
    MONSTER = "monster"
    NPC = "npc"
    WEAPON = "weapon"
    SPELL = "spell"
    ARMOR = "armor"
    OTHER_ITEM = "other_item"


# pull all enums into a single file for easier management and import
# for CreationOptions, this should be like a lookup table for how to generate a creation
# for instance, a "WEAPON" should have a subset of models, generators, and validators necessary for creating a weapon
# CHARACTER would have ALL subsets of models, generators, and validators as it is the most complex creation type
# MONSTER would only the set of subsets complete set of models, generators, and validators necessary for creating a monster
# this is a way to create a single entry point for the creation of all D&D 5e objects
# create a script of all models
# create another script of all generators
# create another script of all validators

# then the enum CreationOptions just becomes a "mapping" of which methods, classes within those scripts to create that specific creation
# may need to include schemas / formatters for each creation type in addition to models, generators, and validators


class CreatureType(Enum):
    """D&D 5e creature types."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class CreatureSize(Enum):
    """D&D 5e creature sizes."""
    TINY = "Tiny"
    SMALL = "Small"
    MEDIUM = "Medium"
    LARGE = "Large"
    HUGE = "Huge"
    GARGANTUAN = "Gargantuan"

class CreatureAlignment(Enum):
    """D&D 5e alignments."""
    LAWFUL_GOOD = "lawful good"
    NEUTRAL_GOOD = "neutral good"
    CHAOTIC_GOOD = "chaotic good"
    LAWFUL_NEUTRAL = "lawful neutral"
    TRUE_NEUTRAL = "true neutral"
    CHAOTIC_NEUTRAL = "chaotic neutral"
    LAWFUL_EVIL = "lawful evil"
    NEUTRAL_EVIL = "neutral evil"
    CHAOTIC_EVIL = "chaotic evil"
    UNALIGNED = "unaligned"

class DnDCondition(Enum):
    """D&D 5e 2024 conditions with their effects."""
    BLINDED = "blinded"
    CHARMED = "charmed"
    DEAFENED = "deafened"
    EXHAUSTION = "exhaustion"
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

class ExhaustionLevel:
    """D&D 5e 2024 Exhaustion level effects."""
    
    EFFECTS = {
        0: {"d20_penalty": 0, "speed_penalty": 0, "description": "No exhaustion"},
        1: {"d20_penalty": -2, "speed_penalty": -5, "description": "Fatigued"},
        2: {"d20_penalty": -4, "speed_penalty": -10, "description": "Tired"},
        3: {"d20_penalty": -6, "speed_penalty": -15, "description": "Weary"},
        4: {"d20_penalty": -8, "speed_penalty": -20, "description": "Exhausted"},
        5: {"d20_penalty": -10, "speed_penalty": -25, "description": "Severely Exhausted"},
        6: {"d20_penalty": 0, "speed_penalty": 0, "description": "Death"}
    }

class ProficiencyLevel(Enum):
    """Proficiency levels for D&D 5e skills and abilities."""
    NONE = 0
    PROFICIENT = 1
    EXPERT = 2

class AbilityScoreSource(Enum):
    """Sources of ability score bonuses."""
    BASE = "base"
    ASI = "ability_score_improvement"
    FEAT = "feat"
    MAGIC_ITEM = "magic_item"
    CLASS_FEATURE = "class_feature"
    SPECIES_TRAIT = "species_trait"
    TEMPORARY = "temporary"

class ItemType(Enum):
    """Types of items that can be created."""
    WEAPON = "weapon"
    ARMOR = "armor"
    SHIELD = "shield"
    SPELL = "spell"
    MAGIC_ITEM = "magic_item"
    POTION = "potion"
    SCROLL = "scroll"
    TOOL = "tool"
    ADVENTURING_GEAR = "adventuring_gear"

class ItemRarity(Enum):
    """D&D 5e item rarity levels."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    VERY_RARE = "very_rare"
    LEGENDARY = "legendary"
    ARTIFACT = "artifact"

class WeaponCategory(Enum):
    """D&D 5e weapon categories."""
    SIMPLE_MELEE = "simple_melee"
    SIMPLE_RANGED = "simple_ranged"
    MARTIAL_MELEE = "martial_melee"
    MARTIAL_RANGED = "martial_ranged"

class ArmorCategory(Enum):
    """D&D 5e armor categories."""
    LIGHT = "light"
    MEDIUM = "medium"
    HEAVY = "heavy"
    SHIELD = "shield"

