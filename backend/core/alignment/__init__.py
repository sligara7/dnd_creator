"""
D&D Character Creator - Alignment Package

This package contains classes related to character alignment handling in D&D,
including standard alignment management and LLM-enhanced alignment suggestions.
"""

# Import main classes for direct access when importing from this package
from backend.core.alignment.abstract_alignment import AbstractAlignment
from backend.core.alignment.alignment import Alignment, LLMAlignmentAdvisor

# Define what gets imported with "from backend.core.alignment import *"
__all__ = [
    'AbstractAlignment',
    'Alignment',
    'LLMAlignmentAdvisor',
]

# Package metadata
__version__ = '0.1.0'
__author__ = 'D&D Character Creator Team'