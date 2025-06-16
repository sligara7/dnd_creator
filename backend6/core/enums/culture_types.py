"""
Minimal Culture Types for D&D Character Creation.

SIMPLIFIED VERSION: Only essential enums that support character creation.
Culture features are supportive - no complex validation or restriction systems.

Philosophy:
- Character creation comes first
- Culture enhances but never restricts
- Simple enums for basic categorization
- Creative freedom is paramount
"""

from enum import Enum, auto
from typing import Optional

# ============================================================================
# ESSENTIAL CULTURE ENUMS - Character Creation Focus
# ============================================================================

class CultureAuthenticityLevel(Enum):
    """Simple authenticity levels for character creation."""
    CREATIVE = "creative"      # Creative freedom - adapt as needed
    GAMING = "gaming"          # Gaming table friendly - easy to use
    FANTASY = "fantasy"        # Fantasy adaptation - flexible interpretation

    def __str__(self) -> str:
        return self.value
    
    @property
    def is_gaming_friendly(self) -> bool:
        """Check if this level prioritizes gaming table use."""
        return self in [CultureAuthenticityLevel.GAMING, CultureAuthenticityLevel.FANTASY]
    
    @property
    def description(self) -> str:
        """Get description of this authenticity level."""
        descriptions = {
            CultureAuthenticityLevel.CREATIVE: "Maximum creative freedom - adapt culture as needed for your character",
            CultureAuthenticityLevel.GAMING: "Gaming table optimized - easy to pronounce and use during play",
            CultureAuthenticityLevel.FANTASY: "Fantasy adaptation - flexible interpretation for any campaign"
        }
        return descriptions[self]


class CultureType(Enum):
    """Basic culture types for character inspiration."""
    FANTASY = "fantasy"        # Generic fantasy culture
    HISTORICAL = "historical"  # Historical inspiration
    MYTHOLOGICAL = "mythological"  # Mythological inspiration
    ORIGINAL = "original"      # Original creation
    MIXED = "mixed"           # Mixed inspiration

    def __str__(self) -> str:
        return self.value
    
    @property
    def description(self) -> str:
        """Get description of this culture type."""
        descriptions = {
            CultureType.FANTASY: "Generic fantasy culture suitable for any campaign",
            CultureType.HISTORICAL: "Inspired by historical cultures and traditions",
            CultureType.MYTHOLOGICAL: "Based on mythological and legendary sources",
            CultureType.ORIGINAL: "Original creation for unique character backgrounds",
            CultureType.MIXED: "Blend of multiple cultural inspirations"
        }
        return descriptions[self]


# ============================================================================
# OPTIONAL HELPER FUNCTIONS - Simple and Supportive
# ============================================================================

def get_default_authenticity_level() -> CultureAuthenticityLevel:
    """Get default authenticity level for character creation."""
    return CultureAuthenticityLevel.GAMING  # Default to gaming-friendly


def is_gaming_optimized(authenticity_level: CultureAuthenticityLevel) -> bool:
    """Check if authenticity level is optimized for gaming tables."""
    return authenticity_level.is_gaming_friendly


def get_available_culture_types() -> list[CultureType]:
    """Get all available culture types for character creation."""
    return list(CultureType)


def get_available_authenticity_levels() -> list[CultureAuthenticityLevel]:
    """Get all available authenticity levels."""
    return list(CultureAuthenticityLevel)


# ============================================================================
# EXPORTS - Keep it Simple
# ============================================================================

__all__ = [
    # Core enums
    "CultureAuthenticityLevel",
    "CultureType",
    
    # Helper functions
    "get_default_authenticity_level",
    "is_gaming_optimized",
    "get_available_culture_types",
    "get_available_authenticity_levels"
]

# ============================================================================
# MODULE INFO
# ============================================================================

__version__ = "1.0.0"
__description__ = "Minimal Culture Types for D&D Character Creation - Culture Enhances, Never Restricts"