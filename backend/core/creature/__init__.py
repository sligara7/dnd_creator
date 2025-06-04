"""
Creature Package

Provides classes and utilities for creating, managing, and enhancing D&D creatures,
including individual monsters and encounter groups.
"""

__version__ = "0.1.0"

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