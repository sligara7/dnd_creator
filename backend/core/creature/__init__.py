"""
D&D 2024 Creature System

This package provides classes for creating, managing, and enhancing D&D creatures,
including individual monsters and encounter groups.

Classes:
    AbstractCreature: Base class defining the creature system interface
    Creature: Implementation of D&D 2024 creature mechanics
    LLMCreatureAdvisor: AI-powered advisor for creating and customizing individual creatures
    LLMMassCreatureAdvisor: AI-powered advisor for generating and balancing groups of creatures
"""

# Import main classes for direct access from package
from backend.core.creature.abstract_creature import AbstractCreature
from backend.core.creature.creature import Creature
from backend.core.creature.llm_creature_advisor import LLMCreatureAdvisor
from backend.core.creature.llm_mass_creature_advisor import LLMMassCreatureAdvisor

# Public API
__all__ = [
    "AbstractCreature",
    "Creature",
    "LLMCreatureAdvisor",
    "LLMMassCreatureAdvisor",
]