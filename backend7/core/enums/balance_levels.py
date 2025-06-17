"""
Essential D&D Balance Level Enums

Streamlined balance level classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ POWER BALANCE LEVELS ============

class PowerLevel(Enum):
    """Character power level classifications."""
    LOW = auto()
    STANDARD = auto()
    HIGH = auto()
    EPIC = auto()

class BalanceTier(Enum):
    """Game balance tier classifications."""
    TIER_1 = "local_heroes"      # Levels 1-4
    TIER_2 = "realm_heroes"      # Levels 5-10
    TIER_3 = "realm_masters"     # Levels 11-16
    TIER_4 = "world_masters"     # Levels 17-20

class CampaignStyle(Enum):
    """Campaign balance style preferences."""
    GRITTY = auto()
    STANDARD = auto()
    HEROIC = auto()
    MYTHIC = auto()

# ============ MECHANICAL BALANCE LEVELS ============

class StatGenMethod(Enum):
    """Ability score generation balance levels."""
    POINT_BUY = "balanced"
    STANDARD_ARRAY = "balanced"
    ROLLING_4D6 = "variable"
    ROLLING_3D6 = "low_power"
    ELITE_ARRAY = "high_power"

class WealthLevel(Enum):
    """Starting wealth balance levels."""
    POOR = auto()
    STANDARD = auto()
    WEALTHY = auto()
    NOBLE = auto()

class MagicItemRarity(Enum):
    """Magic item availability balance."""
    RARE = "low_magic"
    UNCOMMON = "standard_magic"
    COMMON = "high_magic"
    ABUNDANT = "epic_magic"

# ============ ENCOUNTER BALANCE LEVELS ============

class DifficultyScale(Enum):
    """Encounter difficulty balance scale."""
    EASY = auto()
    MEDIUM = auto()
    HARD = auto()
    DEADLY = auto()

class RestFrequency(Enum):
    """Rest frequency balance impact."""
    FREQUENT = "easy_mode"
    STANDARD = "balanced"
    RARE = "hard_mode"
    SURVIVAL = "gritty_mode"

# ============ BALANCE CONFIGURATION ============

BALANCE_PROFILES = {
    "new_players": {
        "power_level": PowerLevel.STANDARD,
        "stat_generation": StatGenMethod.STANDARD_ARRAY,
        "wealth": WealthLevel.STANDARD,
        "magic_items": MagicItemRarity.UNCOMMON,
        "difficulty": DifficultyScale.EASY,
        "rest_frequency": RestFrequency.FREQUENT
    },
    "experienced": {
        "power_level": PowerLevel.HIGH,
        "stat_generation": StatGenMethod.POINT_BUY,
        "wealth": WealthLevel.WEALTHY,
        "magic_items": MagicItemRarity.COMMON,
        "difficulty": DifficultyScale.MEDIUM,
        "rest_frequency": RestFrequency.STANDARD
    },
    "hardcore": {
        "power_level": PowerLevel.LOW,
        "stat_generation": StatGenMethod.ROLLING_3D6,
        "wealth": WealthLevel.POOR,
        "magic_items": MagicItemRarity.RARE,
        "difficulty": DifficultyScale.HARD,
        "rest_frequency": RestFrequency.RARE
    },
    "epic_campaign": {
        "power_level": PowerLevel.EPIC,
        "stat_generation": StatGenMethod.ELITE_ARRAY,
        "wealth": WealthLevel.NOBLE,
        "magic_items": MagicItemRarity.ABUNDANT,
        "difficulty": DifficultyScale.DEADLY,
        "rest_frequency": RestFrequency.STANDARD
    }
}

# ============ UTILITY FUNCTIONS ============

def get_balance_profile(profile_name: str) -> dict:
    """Get balance profile configuration."""
    return BALANCE_PROFILES.get(profile_name, BALANCE_PROFILES["experienced"])

def get_tier_for_level(level: int) -> BalanceTier:
    """Get balance tier for character level."""
    if 1 <= level <= 4:
        return BalanceTier.TIER_1
    elif 5 <= level <= 10:
        return BalanceTier.TIER_2
    elif 11 <= level <= 16:
        return BalanceTier.TIER_3
    elif 17 <= level <= 20:
        return BalanceTier.TIER_4
    else:
        return BalanceTier.TIER_1

def is_balanced_combination(power_level: PowerLevel, difficulty: DifficultyScale) -> bool:
    """Check if power level and difficulty are balanced."""
    balanced_combinations = {
        PowerLevel.LOW: [DifficultyScale.EASY, DifficultyScale.MEDIUM],
        PowerLevel.STANDARD: [DifficultyScale.MEDIUM],
        PowerLevel.HIGH: [DifficultyScale.MEDIUM, DifficultyScale.HARD],
        PowerLevel.EPIC: [DifficultyScale.HARD, DifficultyScale.DEADLY]
    }
    return difficulty in balanced_combinations.get(power_level, [])

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Enums
    'PowerLevel',
    'BalanceTier',
    'CampaignStyle',
    'StatGenMethod',
    'WealthLevel',
    'MagicItemRarity',
    'DifficultyScale',
    'RestFrequency',
    
    # Configuration
    'BALANCE_PROFILES',
    
    # Utility functions
    'get_balance_profile',
    'get_tier_for_level',
    'is_balanced_combination',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D balance level enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "balance_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}