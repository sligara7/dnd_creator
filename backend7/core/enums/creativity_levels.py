"""
Essential Creativity Level Enums

Streamlined creativity level classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ CHARACTER CREATIVITY LEVELS ============

class CreativityLevel(Enum):
    """Character creation creativity levels."""
    STRICT = auto()         # RAW rules only
    STANDARD = auto()       # Official content
    FLEXIBLE = auto()       # Approved homebrew
    CREATIVE = auto()       # Custom content allowed

class CustomizationScope(Enum):
    """Scope of character customization allowed."""
    NONE = auto()           # No customization
    COSMETIC = auto()       # Appearance only
    MECHANICAL = auto()     # Minor rule tweaks
    FULL = auto()           # Complete customization

class HomebrewLevel(Enum):
    """Homebrew content acceptance levels."""
    NONE = auto()           # Official only
    REVIEWED = auto()       # Peer-reviewed homebrew
    COMMUNITY = auto()      # Popular homebrew
    EXPERIMENTAL = auto()   # Untested content

# ============ CONTENT GENERATION CREATIVITY ============

class GenerationStyle(Enum):
    """Content generation creativity styles."""
    CONSERVATIVE = auto()   # Safe, balanced choices
    BALANCED = auto()       # Mix of safe and creative
    ADVENTUROUS = auto()    # Bold, unique choices
    EXPERIMENTAL = auto()   # Untested combinations

class NameCreativity(Enum):
    """Character naming creativity levels."""
    TRADITIONAL = auto()    # Lore-appropriate names
    MODERN = auto()         # Contemporary names
    CREATIVE = auto()       # Unique combinations
    RANDOM = auto()         # Generated names

class BackstoryDepth(Enum):
    """Character backstory complexity levels."""
    MINIMAL = auto()        # Basic background
    STANDARD = auto()       # Moderate detail
    DETAILED = auto()       # Rich backstory
    ELABORATE = auto()      # Complex history

# ============ RULE INTERPRETATION CREATIVITY ============

class RuleFlexibility(Enum):
    """Rule interpretation flexibility levels."""
    STRICT = auto()         # Rules as written
    LENIENT = auto()        # Rules as intended
    FLEXIBLE = auto()       # Reasonable interpretations
    CREATIVE = auto()       # Innovative applications

class OptionalRules(Enum):
    """Optional rule usage levels."""
    NONE = auto()           # Core rules only
    COMMON = auto()         # Popular variants
    EXTENSIVE = auto()      # Many variants
    ALL = auto()            # All available options

# ============ CREATIVITY PROFILES ============

CREATIVITY_PROFILES = {
    "new_player": {
        "creativity": CreativityLevel.STANDARD,
        "customization": CustomizationScope.COSMETIC,
        "homebrew": HomebrewLevel.NONE,
        "generation": GenerationStyle.CONSERVATIVE,
        "naming": NameCreativity.TRADITIONAL,
        "backstory": BackstoryDepth.MINIMAL,
        "rules": RuleFlexibility.STRICT,
        "optional_rules": OptionalRules.NONE
    },
    "experienced": {
        "creativity": CreativityLevel.FLEXIBLE,
        "customization": CustomizationScope.MECHANICAL,
        "homebrew": HomebrewLevel.REVIEWED,
        "generation": GenerationStyle.BALANCED,
        "naming": NameCreativity.CREATIVE,
        "backstory": BackstoryDepth.STANDARD,
        "rules": RuleFlexibility.LENIENT,
        "optional_rules": OptionalRules.COMMON
    },
    "creative": {
        "creativity": CreativityLevel.CREATIVE,
        "customization": CustomizationScope.FULL,
        "homebrew": HomebrewLevel.COMMUNITY,
        "generation": GenerationStyle.ADVENTUROUS,
        "naming": NameCreativity.CREATIVE,
        "backstory": BackstoryDepth.DETAILED,
        "rules": RuleFlexibility.FLEXIBLE,
        "optional_rules": OptionalRules.EXTENSIVE
    },
    "experimental": {
        "creativity": CreativityLevel.CREATIVE,
        "customization": CustomizationScope.FULL,
        "homebrew": HomebrewLevel.EXPERIMENTAL,
        "generation": GenerationStyle.EXPERIMENTAL,
        "naming": NameCreativity.RANDOM,
        "backstory": BackstoryDepth.ELABORATE,
        "rules": RuleFlexibility.CREATIVE,
        "optional_rules": OptionalRules.ALL
    }
}

# ============ UTILITY FUNCTIONS ============

def get_creativity_profile(profile_name: str) -> dict:
    """Get creativity profile configuration."""
    return CREATIVITY_PROFILES.get(profile_name, CREATIVITY_PROFILES["experienced"])

def allows_homebrew(creativity: CreativityLevel) -> bool:
    """Check if creativity level allows homebrew content."""
    return creativity in [CreativityLevel.FLEXIBLE, CreativityLevel.CREATIVE]

def allows_customization(scope: CustomizationScope) -> bool:
    """Check if customization scope allows modifications."""
    return scope != CustomizationScope.NONE

def is_conservative_approach(generation: GenerationStyle) -> bool:
    """Check if generation style is conservative."""
    return generation == GenerationStyle.CONSERVATIVE

def requires_approval(homebrew: HomebrewLevel) -> bool:
    """Check if homebrew level requires DM approval."""
    return homebrew in [HomebrewLevel.COMMUNITY, HomebrewLevel.EXPERIMENTAL]

def get_backstory_complexity(depth: BackstoryDepth) -> int:
    """Get numeric complexity score for backstory depth."""
    complexity_scores = {
        BackstoryDepth.MINIMAL: 1,
        BackstoryDepth.STANDARD: 2,
        BackstoryDepth.DETAILED: 3,
        BackstoryDepth.ELABORATE: 4
    }
    return complexity_scores.get(depth, 2)

def is_rules_flexible(flexibility: RuleFlexibility) -> bool:
    """Check if rule flexibility allows interpretation."""
    return flexibility in [RuleFlexibility.FLEXIBLE, RuleFlexibility.CREATIVE]

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core creativity levels
    'CreativityLevel',
    'CustomizationScope',
    'HomebrewLevel',
    
    # Generation creativity
    'GenerationStyle',
    'NameCreativity',
    'BackstoryDepth',
    
    # Rule interpretation
    'RuleFlexibility',
    'OptionalRules',
    
    # Profiles
    'CREATIVITY_PROFILES',
    
    # Utility functions
    'get_creativity_profile',
    'allows_homebrew',
    'allows_customization',
    'is_conservative_approach',
    'requires_approval',
    'get_backstory_complexity',
    'is_rules_flexible',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential creativity level enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "creativity_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}