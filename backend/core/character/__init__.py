"""
D&D Character Creator - Character Package

This package contains all classes related to D&D character creation, validation, 
and management. It serves as the core functionality for the character creation system.
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

# Package metadata
__version__ = '0.1.0'
__author__ = 'D&D Character Creator Team'