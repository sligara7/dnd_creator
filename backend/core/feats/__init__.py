"""
D&D Character Creator - Feats Package

This package contains classes related to character feats management in D&D,
including feat selection, validation, prerequisites checking, and benefits application.
"""

# Import main classes for direct access when importing from this package
from backend.core.feats.abstract_feats import AbstractFeats
from backend.core.feats.feats import Feats
from backend.core.feats.feat_manager import FeatManager
from backend.core.feats.llm_feat_advisor import LLMFeatAdvisor

# Define what gets imported with "from backend.core.feats import *"
__all__ = [
    'AbstractFeats',
    'Feats',
    'FeatManager',
    'LLMFeatAdvisor',
]

# Package metadata
__version__ = '0.1.0'
__author__ = 'D&D Character Creator Team'