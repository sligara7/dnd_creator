"""
D&D 2024 Character System

This package provides classes for creating, validating, and managing D&D characters,
including ability scores, progression, and export capabilities.

Classes:
    AbstractCharacterClass: Base class defining the character system interface
    Character: Implementation of D&D 2024 character mechanics
    CharacterValidator: Validates character configuration and choices
    AbilityScores: Handles character ability scores and modifiers
    CharacterProgression: Manages character leveling and advancement
    CharacterExporter: Exports character data to various formats
    LLMCharacterAdvisor: AI-powered helper for character optimization and concepts
"""

# Import main classes for direct access when importing from this package
from backend.core.character.abstract_character import AbstractCharacterClass
from backend.core.character.character import Character
from backend.core.character.character_validator import CharacterValidator
from backend.core.character.ability_scores import AbilityScores
from backend.core.character.character_progression import CharacterProgression
from backend.core.character.character_exporter import CharacterExporter
from backend.core.character.llm_character_advisor import LLMCharacterAdvisor

# Define what gets imported with "from backend.core.character import *"
__all__ = [
    'AbstractCharacterClass',
    'Character',
    'CharacterValidator',
    'AbilityScores',
    'CharacterProgression',
    'CharacterExporter',
    'LLMCharacterAdvisor',
]