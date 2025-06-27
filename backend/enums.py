"""
D&D 5e Enumerations

This module contains all enum definitions for the D&D Character Creator.
Contains only enum definitions - no orchestration or coordination logic.

All enums from across the backend have been consolidated here to eliminate
duplication and provide a single source of truth.
"""

from enum import Enum

# ============================================================================
# CREATION SYSTEM ENUMS
# ============================================================================

class CreationOptions(Enum):
    """Types of D&D 5e objects that can be created."""
    CHARACTER = "character"
    MONSTER = "monster"
    NPC = "npc"
    WEAPON = "weapon"
    SPELL = "spell"
    ARMOR = "armor"
    OTHER_ITEM = "other_item"

# ============================================================================
# CREATURE ENUMS
# ============================================================================

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

# ============================================================================
# CHARACTER ENUMS
# ============================================================================

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

# ============================================================================
# SPELLCASTING ENUMS
# ============================================================================

class SpellSchool(Enum):
    """D&D 5e schools of magic."""
    ABJURATION = "abjuration"
    CONJURATION = "conjuration"
    DIVINATION = "divination"
    ENCHANTMENT = "enchantment"
    EVOCATION = "evocation"
    ILLUSION = "illusion"
    NECROMANCY = "necromancy"
    TRANSMUTATION = "transmutation"

class SpellcastingType(Enum):
    """Types of spellcasting in D&D 5e 2024."""
    NONE = "none"                    # Non-spellcaster
    PREPARED = "prepared"            # Can change spells daily (Cleric, Druid, Paladin, Wizard)
    KNOWN = "known"                  # Fixed list of known spells (Sorcerer, Warlock, Bard, Ranger)
    RITUAL_ONLY = "ritual_only"      # Only ritual casting (some subclasses)
    INNATE = "innate"               # Species/trait-based spellcasting
    HYBRID = "hybrid"               # Mix of prepared and known (some subclasses)

class SpellcastingAbility(Enum):
    """Primary spellcasting abilities for each class."""
    INTELLIGENCE = "intelligence"    # Wizard, Artificer, Eldritch Knight, Arcane Trickster
    WISDOM = "wisdom"               # Cleric, Druid, Ranger
    CHARISMA = "charisma"           # Sorcerer, Warlock, Paladin, Bard

class RitualCastingType(Enum):
    """Types of ritual casting available."""
    NONE = "none"                   # Cannot cast rituals
    PREPARED_ONLY = "prepared_only"  # Can only cast prepared rituals
    ANY_KNOWN = "any_known"         # Can cast any known spell as ritual
    SPECIAL = "special"             # Special ritual casting rules

# ============================================================================
# DAMAGE AND COMBAT ENUMS
# ============================================================================

class DamageType(Enum):
    """D&D 5e damage types."""
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

# ============================================================================
# ITEM ENUMS
# ============================================================================

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

# ============================================================================
# NPC ENUMS
# ============================================================================

class NPCType(Enum):
    """NPC complexity types."""
    MINOR = "minor"      # Roleplaying only, no stat block needed
    MAJOR = "major"      # Full stat block for combat/abilities

class NPCRole(Enum):
    """2024 role-based NPC categories."""
    CIVILIAN = "civilian"
    MERCHANT = "merchant"
    GUARD = "guard"
    NOBLE = "noble"
    SCHOLAR = "scholar"
    ARTISAN = "artisan"
    CRIMINAL = "criminal"
    SOLDIER = "soldier"
    SPELLCASTER = "spellcaster"
    LEADER = "leader"
    HEALER = "healer"
    SCOUT = "scout"

class NPCSpecies(Enum):
    """Common NPC species (expandable with LLM-generated custom species)."""
    HUMAN = "human"
    ELF = "elf"
    DWARF = "dwarf"
    HALFLING = "halfling"
    DRAGONBORN = "dragonborn"
    GNOME = "gnome"
    HALF_ELF = "half-elf"
    HALF_ORC = "half-orc"
    TIEFLING = "tiefling"
    CUSTOM = "custom"  # For LLM-generated species

class NPCClass(Enum):
    """Common NPC classes (expandable with LLM-generated custom classes)."""
    FIGHTER = "fighter"
    WIZARD = "wizard"
    ROGUE = "rogue"
    CLERIC = "cleric"
    RANGER = "ranger"
    BARD = "bard"
    PALADIN = "paladin"
    BARBARIAN = "barbarian"
    SORCERER = "sorcerer"
    WARLOCK = "warlock"
    DRUID = "druid"
    MONK = "monk"
    ARTIFICER = "artificer"
    CUSTOM = "custom"  # For LLM-generated classes
