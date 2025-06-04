"""
D&D 2024 Ability Scores System

This package provides classes for managing character ability scores in D&D,
including generation methods, modifiers calculation, and ability-based checks.

Classes:
    AbstractAbilityScores: Base class defining the ability scores system interface
    AbilityScores: Implementation of D&D 2024 ability scores mechanics
    AbilityScoreCalculator: Utility class for calculating scores and modifiers
    LLMAbilityAdvisor: AI-powered helper for ability score recommendations and optimization
"""

# Import main classes for direct access when importing from this package
from backend.core.ability_scores.abstract_ability_scores import AbstractAbilityScores
from backend.core.ability_scores.ability_scores import AbilityScores
from backend.core.ability_scores.ability_score_calculator import AbilityScoreCalculator
from backend.core.ability_scores.llm_ability_advisor import LLMAbilityAdvisor

# Define what gets imported with "from backend.core.ability_scores import *"
__all__ = [
    'AbstractAbilityScores',
    'AbilityScores',
    'AbilityScoreCalculator',
    'LLMAbilityAdvisor'
]