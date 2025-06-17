"""
Essential D&D Culture Exception Types

Streamlined culture-related exception handling following backend7 architecture.
Based on crude_functional.py patterns and essential-only philosophy.
"""

from typing import Optional, Dict, Any, List
from .base import DnDCharacterCreatorError

# ============ CULTURAL COMPATIBILITY EXCEPTIONS ============

class CulturalMismatchError(DnDCharacterCreatorError):
    """Race and cultural background compatibility issues."""
    
    def __init__(self, race: str, culture: str, reason: str, **kwargs):
        message = f"Cultural mismatch: {race} with {culture} culture - {reason}"
        details = {
            "race": race,
            "culture": culture,
            "reason": reason,
            **kwargs
        }
        super().__init__(message, details)
        self.race = race
        self.culture = culture

class LanguageConflictError(DnDCharacterCreatorError):
    """Language selection conflicts with cultural background."""
    
    def __init__(self, language: str, culture: str, conflict_type: str, **kwargs):
        message = f"Language conflict: {language} incompatible with {culture} culture - {conflict_type}"
        details = {
            "language": language,
            "culture": culture,
            "conflict_type": conflict_type,
            **kwargs
        }
        super().__init__(message, details)
        self.language = language
        self.culture = culture
        self.conflict_type = conflict_type

class SocialStructureError(DnDCharacterCreatorError):
    """Character background conflicts with cultural social structure."""
    
    def __init__(self, background: str, social_structure: str, conflict: str, **kwargs):
        message = f"Social structure conflict: {background} background incompatible with {social_structure} structure - {conflict}"
        details = {
            "background": background,
            "social_structure": social_structure,
            "conflict": conflict,
            **kwargs
        }
        super().__init__(message, details)
        self.background = background
        self.social_structure = social_structure

# ============ CULTURAL VALUES EXCEPTIONS ============

class ValueSystemError(DnDCharacterCreatorError):
    """Character values conflict with cultural expectations."""
    
    def __init__(self, character_values: List[str], cultural_values: List[str], **kwargs):
        char_vals = ", ".join(character_values)
        cult_vals = ", ".join(cultural_values)
        message = f"Value system conflict: character values ({char_vals}) clash with cultural values ({cult_vals})"
        details = {
            "character_values": character_values,
            "cultural_values": cultural_values,
            **kwargs
        }
        super().__init__(message, details)
        self.character_values = character_values
        self.cultural_values = cultural_values

class WorldviewConflictError(DnDCharacterCreatorError):
    """Character worldview incompatible with cultural background."""
    
    def __init__(self, character_worldview: str, cultural_worldview: str, **kwargs):
        message = f"Worldview conflict: {character_worldview} vs {cultural_worldview}"
        details = {
            "character_worldview": character_worldview,
            "cultural_worldview": cultural_worldview,
            **kwargs
        }
        super().__init__(message, details)
        self.character_worldview = character_worldview
        self.cultural_worldview = cultural_worldview

# ============ RELIGIOUS PRACTICE EXCEPTIONS ============

class ReligiousConflictError(DnDCharacterCreatorError):
    """Religious practice conflicts with cultural background."""
    
    def __init__(self, deity: str, culture: str, religious_practice: str, **kwargs):
        message = f"Religious conflict: {deity} worship incompatible with {culture} {religious_practice} practices"
        details = {
            "deity": deity,
            "culture": culture,
            "religious_practice": religious_practice,
            **kwargs
        }
        super().__init__(message, details)
        self.deity = deity
        self.culture = culture
        self.religious_practice = religious_practice

# ============ ARTISTIC TRADITION EXCEPTIONS ============

class ArtisticTraditionError(DnDCharacterCreatorError):
    """Artistic traditions conflict with character background."""
    
    def __init__(self, art_form: str, culture: str, tradition_conflict: str, **kwargs):
        message = f"Artistic tradition conflict: {art_form} not practiced in {culture} culture - {tradition_conflict}"
        details = {
            "art_form": art_form,
            "culture": culture,
            "tradition_conflict": tradition_conflict,
            **kwargs
        }
        super().__init__(message, details)
        self.art_form = art_form
        self.culture = culture

# ============ SETTLEMENT TYPE EXCEPTIONS ============

class SettlementMismatchError(DnDCharacterCreatorError):
    """Character background incompatible with settlement type."""
    
    def __init__(self, background: str, settlement_type: str, reason: str, **kwargs):
        message = f"Settlement mismatch: {background} background incompatible with {settlement_type} settlement - {reason}"
        details = {
            "background": background,
            "settlement_type": settlement_type,
            "reason": reason,
            **kwargs
        }
        super().__init__(message, details)
        self.background = background
        self.settlement_type = settlement_type

# ============ UTILITY FUNCTIONS ============

def create_cultural_mismatch(race: str, culture: str, reason: str) -> CulturalMismatchError:
    """Factory function for cultural mismatch errors."""
    return CulturalMismatchError(race, culture, reason)

def create_language_conflict(language: str, culture: str, conflict_type: str) -> LanguageConflictError:
    """Factory function for language conflict errors."""
    return LanguageConflictError(language, culture, conflict_type)

def create_value_system_error(char_values: List[str], cult_values: List[str]) -> ValueSystemError:
    """Factory function for value system errors."""
    return ValueSystemError(char_values, cult_values)

def is_cultural_flexibility_allowed(error: DnDCharacterCreatorError) -> bool:
    """Check if cultural error can be resolved with flexibility."""
    flexible_types = [
        WorldviewConflictError,
        ArtisticTraditionError,
        ValueSystemError
    ]
    return any(isinstance(error, error_type) for error_type in flexible_types)

def requires_cultural_explanation(error: DnDCharacterCreatorError) -> bool:
    """Check if cultural error requires backstory explanation."""
    explanation_required = [
        CulturalMismatchError,
        ReligiousConflictError,
        SocialStructureError,
        SettlementMismatchError
    ]
    return any(isinstance(error, error_type) for error_type in explanation_required)

def get_cultural_severity(error: DnDCharacterCreatorError) -> str:
    """Get cultural error severity level."""
    severity_map = {
        CulturalMismatchError: "warning",
        LanguageConflictError: "info",
        SocialStructureError: "warning",
        ValueSystemError: "info",
        WorldviewConflictError: "info",
        ReligiousConflictError: "warning",
        ArtisticTraditionError: "info",
        SettlementMismatchError: "warning"
    }
    return severity_map.get(type(error), "info")

# ============ ESSENTIAL EXPORTS ============

__all__ = [
    # Cultural compatibility exceptions
    'CulturalMismatchError',
    'LanguageConflictError', 
    'SocialStructureError',
    
    # Cultural values exceptions
    'ValueSystemError',
    'WorldviewConflictError',
    
    # Religious practice exceptions
    'ReligiousConflictError',
    
    # Artistic tradition exceptions
    'ArtisticTraditionError',
    
    # Settlement type exceptions
    'SettlementMismatchError',
    
    # Utility functions
    'create_cultural_mismatch',
    'create_language_conflict',
    'create_value_system_error',
    'is_cultural_flexibility_allowed',
    'requires_cultural_explanation',
    'get_cultural_severity',
]

# ============ MODULE METADATA ============

__version__ = '1.0.0'
__description__ = 'Essential D&D cultural exception handling'
__author__ = 'D&D Character Creator Backend7'

# Backend7 architecture compliance
BACKEND7_COMPLIANCE = {
    "layer": "core/exceptions",
    "focus": "cultural_error_handling_only",
    "line_target": 150,
    "dependencies": ["base"],
    "philosophy": "crude_functional_inspired_simple_cultural_exceptions"
}