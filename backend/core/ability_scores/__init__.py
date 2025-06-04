"""
D&D Character Creator - Ability Scores Package

This package contains classes related to ability scores management in D&D,
including ability score generation, calculation of modifiers, and score-based checks.
"""

# Import main classes for direct access when importing from this package
from backend.core.ability_scores.abstract_ability_scores import AbstractAbilityScores
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.ability_scores.ability_score_calculator import AbilityScoreCalculator

# Define what gets imported with "from backend.core.ability_scores import *"
__all__ = [
    'AbstractAbilityScores',
    'AbilityScores',
    'AbilityScoreCalculator',
]

# Package metadata
__version__ = '0.1.0'
__author__ = 'D&D Character Creator Team'