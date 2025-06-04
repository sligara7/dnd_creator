"""
D&D 2024 Character Classes System

This package provides classes for managing D&D character classes,
including class features, progression, subclasses, and multiclassing rules.

Classes:
    AbstractClasses: Base class defining the character classes system interface
    Classes: Implementation of D&D 2024 character classes system
    LLMClassAdvisor: AI-powered helper for class recommendations and features
"""

from backend.core.classes.abstract_classes import AbstractClasses
from backend.core.classes.classes import Classes
from backend.core.classes.llm_class_advisor import LLMClassAdvisor

__all__ = [
    'AbstractClasses',
    'Classes',
    'LLMClassAdvisor',
]