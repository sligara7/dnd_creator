"""
D&D 2024 Personality and Backstory System

This package provides classes for generating and managing character personalities
and backstories in D&D, including AI-assisted narrative elements.

Classes:
    AbstractPersonality: Base class defining the personality system interface
    LLMPersonalityAdvisor: AI-powered advisor for creating compelling character
                           personalities and backstories
"""

from backend.core.personality_and_backstory.abstract_personality import AbstractPersonality
from backend.core.personality_and_backstory.llm_personality_advisor import LLMPersonalityAdvisor

__all__ = [
    'AbstractPersonality',
    'LLMPersonalityAdvisor',
]