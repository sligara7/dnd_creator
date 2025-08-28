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
# CAMPAIGN CREATION ENUMS
# ============================================================================

class CampaignCreationOptions(Enum):
    """Types of campaign content that can be created."""
    CAMPAIGN = "campaign"
    CAMPAIGN_SKELETON = "campaign_skeleton"
    CHAPTER = "chapter"
    PLOT_FORK = "plot_fork"
    NPC_FOR_CAMPAIGN = "npc_for_campaign"
    MONSTER_FOR_CAMPAIGN = "monster_for_campaign"
    LOCATION = "location"
    PSYCHOLOGICAL_EXPERIMENT = "psychological_experiment"
    SETTING_THEME = "setting_theme"
    CAMPAIGN_REFINEMENT = "campaign_refinement"

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
    SPELLBOOK = "spellbook"         # Can cast rituals from spellbook (Wizard)
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

# ============================================================================
# SKILL SYSTEM ENUMS - D&D 5e 2024
# ============================================================================

class Skill(Enum):
    """D&D 5e 2024 standard skills with their associated ability scores."""
    # Strength-based skills
    ATHLETICS = "athletics"
    
    # Dexterity-based skills
    ACROBATICS = "acrobatics"  # Now Dexterity (Athletics) in some contexts
    STEALTH = "stealth"
    SLEIGHT_OF_HAND = "sleight_of_hand"  # Often with tools now
    
    # Intelligence-based skills
    ARCANA = "arcana"
    HISTORY = "history"
    INVESTIGATION = "investigation"
    NATURE = "nature"
    RELIGION = "religion"
    DECORUM = "decorum"  # New in 2024 - customs and etiquette
    
    # Wisdom-based skills
    ANIMAL_HANDLING = "animal_handling"  # Now often Wisdom (Nature)
    INSIGHT = "insight"
    MEDICINE = "medicine"  # Now often Intelligence (Survival)
    PERCEPTION = "perception"
    SURVIVAL = "survival"
    
    # Charisma-based skills
    DECEPTION = "deception"
    INTIMIDATION = "intimidation"  # Can use other abilities
    PERFORMANCE = "performance"  # Often with tools
    PERSUASION = "persuasion"

class SkillAbilityMapping(Enum):
    """Maps skills to their primary ability scores in D&D 5e 2024."""
    # Strength
    ATHLETICS_STR = ("athletics", "strength")
    
    # Dexterity
    ACROBATICS_DEX = ("acrobatics", "dexterity")
    STEALTH_DEX = ("stealth", "dexterity")
    SLEIGHT_OF_HAND_DEX = ("sleight_of_hand", "dexterity")
    
    # Intelligence
    ARCANA_INT = ("arcana", "intelligence")
    HISTORY_INT = ("history", "intelligence")
    INVESTIGATION_INT = ("investigation", "intelligence")
    NATURE_INT = ("nature", "intelligence")
    RELIGION_INT = ("religion", "intelligence")
    DECORUM_INT = ("decorum", "intelligence")
    
    # Wisdom
    ANIMAL_HANDLING_WIS = ("animal_handling", "wisdom")
    INSIGHT_WIS = ("insight", "wisdom")
    MEDICINE_WIS = ("medicine", "wisdom")
    PERCEPTION_WIS = ("perception", "wisdom")
    SURVIVAL_WIS = ("survival", "wisdom")
    
    # Charisma
    DECEPTION_CHA = ("deception", "charisma")
    INTIMIDATION_CHA = ("intimidation", "charisma")
    PERFORMANCE_CHA = ("performance", "charisma")
    PERSUASION_CHA = ("persuasion", "charisma")

class SkillSource(Enum):
    """Sources of skill proficiency in D&D 5e 2024."""
    SPECIES = "species"
    CLASS = "class"
    BACKGROUND = "background"
    FEAT = "feat"
    TOOL_SYNERGY = "tool_synergy"  # Tool + skill combination
    MULTICLASS = "multiclass"

# ============================================================================
# FEAT ENUMS - D&D 5e 2024
# ============================================================================

class FeatCategory(Enum):
    """Categories of feats in D&D 5e 2024."""
    ORIGIN = "origin"           # Available at level 1 from background
    GENERAL = "general"         # Available starting at level 4
    FIGHTING_STYLE = "fighting_style"  # For classes with Fighting Style feature
    EPIC_BOON = "epic_boon"     # Awarded at level 19

class FeatPrerequisite(Enum):
    """Common feat prerequisites."""
    NONE = "none"
    ABILITY_SCORE = "ability_score"  # Requires specific ability score
    LEVEL = "level"                  # Requires minimum level
    CLASS_FEATURE = "class_feature"  # Requires specific class feature
    PROFICIENCY = "proficiency"      # Requires specific proficiency
    SPELLCASTING = "spellcasting"    # Requires spellcasting ability

class FeatType(Enum):
    """Types of feat benefits."""
    HALF_FEAT = "half_feat"         # Grants +1 ability score
    FULL_FEAT = "full_feat"         # No ability score increase
    UTILITY = "utility"             # Non-combat benefits
    COMBAT = "combat"               # Combat-focused benefits
    SPELLCASTING = "spellcasting"   # Grants spells or spell-like abilities

# ============================================================================
# FEATURES AND TRAITS ENUMS - D&D 5e 2024
# ============================================================================

class FeatureType(Enum):
    """Types of character features and traits."""
    CLASS_FEATURE = "class_feature"
    SPECIES_TRAIT = "species_trait"
    BACKGROUND_FEATURE = "background_feature"
    FEAT_ABILITY = "feat_ability"
    MAGIC_ITEM_PROPERTY = "magic_item_property"
    TEMPORARY_EFFECT = "temporary_effect"

class FeatureCategory(Enum):
    """Categories of features based on their impact."""
    COMBAT = "combat"              # Combat abilities, attacks, defenses
    EXPLORATION = "exploration"    # Movement, senses, environmental
    SOCIAL = "social"             # Social interaction, persuasion
    UTILITY = "utility"           # Tools, skills, general usefulness
    SPELLCASTING = "spellcasting" # Magic-related features
    PASSIVE = "passive"           # Always-on traits
    ACTIVE = "active"             # Requires action to use
    REACTION = "reaction"         # Triggered by specific events

class FeatureUsage(Enum):
    """How often a feature can be used."""
    ALWAYS = "always"             # Passive, always active
    AT_WILL = "at_will"          # Can be used anytime
    ONCE_PER_TURN = "once_per_turn"
    ONCE_PER_ROUND = "once_per_round"
    SHORT_REST = "short_rest"     # Recharges on short or long rest
    LONG_REST = "long_rest"       # Recharges on long rest only
    DAILY = "daily"               # Once per day
    WEEKLY = "weekly"             # Once per week
    LIMITED_USES = "limited_uses" # Has specific number of uses

class SpeciesTraitType(Enum):
    """Types of species traits in D&D 5e 2024."""
    ABILITY_SCORE_INCREASE = "ability_score_increase"
    DARKVISION = "darkvision"
    KEEN_SENSES = "keen_senses"
    FEY_ANCESTRY = "fey_ancestry"
    TRANCE = "trance"
    DWARVEN_RESILIENCE = "dwarven_resilience"
    STONECUNNING = "stonecunning"
    DWARVEN_COMBAT_TRAINING = "dwarven_combat_training"
    TOOL_PROFICIENCY = "tool_proficiency"
    LUCKY = "lucky"
    BRAVE = "brave"
    HALFLING_NIMBLENESS = "halfling_nimbleness"
    NATURAL_STEALTH = "natural_stealth"
    DRACONIC_ANCESTRY = "draconic_ancestry"
    BREATH_WEAPON = "breath_weapon"
    DAMAGE_RESISTANCE = "damage_resistance"
    INFERNAL_HERITAGE = "infernal_heritage"
    FIENDISH_LEGACY = "fiendish_legacy"

class ClassFeatureType(Enum):
    """Types of class features in D&D 5e 2024."""
    FIGHTING_STYLE = "fighting_style"
    SPELLCASTING = "spellcasting"
    RAGE = "rage"
    UNARMORED_DEFENSE = "unarmored_defense"
    RECKLESS_ATTACK = "reckless_attack"
    DANGER_SENSE = "danger_sense"
    EXTRA_ATTACK = "extra_attack"
    FAST_MOVEMENT = "fast_movement"
    FERAL_INSTINCT = "feral_instinct"
    BRUTAL_CRITICAL = "brutal_critical"
    RELENTLESS_RAGE = "relentless_rage"
    PERSISTENT_RAGE = "persistent_rage"
    INDOMITABLE_MIGHT = "indomitable_might"
    PRIMAL_CHAMPION = "primal_champion"
    SECOND_WIND = "second_wind"
    ACTION_SURGE = "action_surge"
    MARTIAL_ARCHETYPE = "martial_archetype"
    INDOMITABLE = "indomitable"
    SNEAK_ATTACK = "sneak_attack"
    THIEVES_CANT = "thieves_cant"
    CUNNING_ACTION = "cunning_action"
    UNCANNY_DODGE = "uncanny_dodge"
    EVASION = "evasion"
    RELIABLE_TALENT = "reliable_talent"
    BLINDSENSE = "blindsense"
    SLIPPERY_MIND = "slippery_mind"
    ELUSIVE = "elusive"
    STROKE_OF_LUCK = "stroke_of_luck"
