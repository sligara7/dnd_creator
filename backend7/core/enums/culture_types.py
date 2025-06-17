"""
Essential D&D Culture Type Enums

Streamlined culture type classifications following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from enum import Enum, auto

# ============ RACIAL CULTURE TYPES ============

class CultureType(Enum):
    """Primary cultural classifications."""
    HUMAN = auto()
    ELVEN = auto()
    DWARVEN = auto()
    HALFLING = auto()
    GNOME = auto()
    ORCISH = auto()
    DRACONIC = auto()
    CELESTIAL = auto()
    INFERNAL = auto()
    ELEMENTAL = auto()

class SettlementType(Enum):
    """Settlement culture classifications."""
    TRIBAL = auto()         # Small nomadic groups
    VILLAGE = auto()        # Rural communities
    TOWN = auto()           # Trade centers
    CITY = auto()           # Urban centers
    METROPOLIS = auto()     # Major cities
    NOMADIC = auto()        # Wandering peoples

class SocialStructure(Enum):
    """Social organization types."""
    EGALITARIAN = auto()    # Equal social standing
    HIERARCHICAL = auto()   # Clear social ranks
    CASTE = auto()          # Rigid class system
    MERITOCRATIC = auto()   # Achievement-based
    THEOCRATIC = auto()     # Religious leadership
    ANARCHIC = auto()       # No formal structure

# ============ CULTURAL VALUES ============

class CulturalValue(Enum):
    """Core cultural value systems."""
    HONOR = auto()          # Personal integrity
    WISDOM = auto()         # Knowledge and learning
    STRENGTH = auto()       # Physical prowess
    COMMUNITY = auto()      # Collective welfare
    FREEDOM = auto()        # Individual liberty
    TRADITION = auto()      # Ancestral ways
    PROGRESS = auto()       # Innovation and change
    HARMONY = auto()        # Balance and peace

class Worldview(Enum):
    """Cultural worldview perspectives."""
    NATURALISTIC = auto()   # Nature-focused
    CIVILIZED = auto()      # Order and law
    SPIRITUAL = auto()      # Divine connection
    PRAGMATIC = auto()      # Practical approach
    ARTISTIC = auto()       # Beauty and creativity
    SCHOLARLY = auto()      # Knowledge pursuit

# ============ CULTURAL PRACTICES ============

class ReligiousPractice(Enum):
    """Religious practice types."""
    MONOTHEISTIC = auto()   # Single deity
    POLYTHEISTIC = auto()   # Multiple deities
    PANTHEISTIC = auto()    # Nature worship
    ANCESTRAL = auto()      # Ancestor veneration
    PHILOSOPHICAL = auto()  # Ethical systems
    SECULAR = auto()        # Non-religious

class ArtisticTradition(Enum):
    """Cultural artistic focuses."""
    MUSIC = auto()
    VISUAL_ART = auto()
    LITERATURE = auto()
    CRAFTSMANSHIP = auto()
    PERFORMANCE = auto()
    ARCHITECTURE = auto()

# ============ LANGUAGE AND COMMUNICATION ============

class LanguageFamily(Enum):
    """Language family classifications."""
    COMMON = auto()         # Trade tongue
    ANCIENT = auto()        # Old languages
    ELEMENTAL = auto()      # Primordial tongues
    PLANAR = auto()         # Outer plane languages
    RACIAL = auto()         # Species-specific
    REGIONAL = auto()       # Geographic dialects

class CommunicationStyle(Enum):
    """Cultural communication preferences."""
    DIRECT = auto()         # Straightforward
    SUBTLE = auto()         # Indirect, nuanced
    FORMAL = auto()         # Ceremonial
    CASUAL = auto()         # Informal
    ARTISTIC = auto()       # Metaphorical
    SCHOLARLY = auto()      # Technical

# ============ CULTURAL MAPPINGS ============

CULTURE_DEFAULTS = {
    CultureType.HUMAN: {
        "settlement": SettlementType.CITY,
        "structure": SocialStructure.HIERARCHICAL,
        "value": CulturalValue.PROGRESS,
        "worldview": Worldview.CIVILIZED,
        "religion": ReligiousPractice.POLYTHEISTIC,
        "art": ArtisticTradition.LITERATURE,
        "language": LanguageFamily.COMMON,
        "communication": CommunicationStyle.DIRECT
    },
    CultureType.ELVEN: {
        "settlement": SettlementType.VILLAGE,
        "structure": SocialStructure.MERITOCRATIC,
        "value": CulturalValue.WISDOM,
        "worldview": Worldview.NATURALISTIC,
        "religion": ReligiousPractice.PANTHEISTIC,
        "art": ArtisticTradition.MUSIC,
        "language": LanguageFamily.ANCIENT,
        "communication": CommunicationStyle.SUBTLE
    },
    CultureType.DWARVEN: {
        "settlement": SettlementType.CITY,
        "structure": SocialStructure.CASTE,
        "value": CulturalValue.HONOR,
        "worldview": Worldview.PRAGMATIC,
        "religion": ReligiousPractice.ANCESTRAL,
        "art": ArtisticTradition.CRAFTSMANSHIP,
        "language": LanguageFamily.RACIAL,
        "communication": CommunicationStyle.DIRECT
    }
}

# ============ UTILITY FUNCTIONS ============

def get_culture_defaults(culture: CultureType) -> dict:
    """Get default cultural characteristics."""
    return CULTURE_DEFAULTS.get(culture, CULTURE_DEFAULTS[CultureType.HUMAN])

def is_urban_culture(settlement: SettlementType) -> bool:
    """Check if settlement type is urban."""
    return settlement in [SettlementType.CITY, SettlementType.METROPOLIS]

def is_hierarchical(structure: SocialStructure) -> bool:
    """Check if social structure has clear hierarchy."""
    return structure in [SocialStructure.HIERARCHICAL, SocialStructure.CASTE, SocialStructure.THEOCRATIC]

def values_tradition(value: CulturalValue) -> bool:
    """Check if cultural value emphasizes tradition."""
    return value in [CulturalValue.HONOR, CulturalValue.TRADITION, CulturalValue.WISDOM]

def is_nature_focused(worldview: Worldview) -> bool:
    """Check if worldview is nature-oriented."""
    return worldview in [Worldview.NATURALISTIC, Worldview.SPIRITUAL]

def uses_formal_communication(style: CommunicationStyle) -> bool:
    """Check if communication style is formal."""
    return style in [CommunicationStyle.FORMAL, CommunicationStyle.SCHOLARLY]

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Core culture types
    'CultureType',
    'SettlementType',
    'SocialStructure',
    
    # Cultural characteristics
    'CulturalValue',
    'Worldview',
    'ReligiousPractice',
    'ArtisticTradition',
    
    # Language and communication
    'LanguageFamily',
    'CommunicationStyle',
    
    # Mappings
    'CULTURE_DEFAULTS',
    
    # Utility functions
    'get_culture_defaults',
    'is_urban_culture',
    'is_hierarchical',
    'values_tradition',
    'is_nature_focused',
    'uses_formal_communication',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D culture type enumerations'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/enums",
    "focus": "culture_classification_only",
    "line_target": 150,
    "dependencies": [],
    "philosophy": "crude_functional_inspired_essential_enums"
}