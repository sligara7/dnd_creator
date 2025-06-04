"""
D&D 2024 Alignment System

This package provides classes for managing character alignments in D&D,
including standard alignments and AI-assisted alignment recommendations.

Classes:
    AbstractAlignment: Base class defining the alignment system interface
    Alignment: Implementation of D&D 2024 alignment mechanics
    LLMAlignmentAdvisor: AI-powered helper for alignment recommendations and roleplaying
"""

# Import main classes for direct access when importing from this package
from backend.core.alignment.abstract_alignment import AbstractAlignment
from backend.core.alignment.alignment import Alignment
from backend.core.alignment.llm_alignment_advisor import LLMAlignmentAdvisor

# Define what gets imported with "from backend.core.alignment import *"
__all__ = [
    'AbstractAlignment',
    'Alignment',
    'LLMAlignmentAdvisor',
]