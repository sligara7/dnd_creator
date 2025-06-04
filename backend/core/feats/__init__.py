"""
D&D 2024 Feats System

This package provides classes for managing character feats in D&D,
including feat selection, validation, prerequisites checking, and benefits application.

Classes:
    AbstractFeats: Base class defining the feats system interface
    Feats: Implementation of D&D 2024 feats system
    FeatManager: Manager class for handling all feat-related operations
    LLMFeatAdvisor: AI-powered helper for feat recommendations and synergies
"""

from backend.core.feats.abstract_feats import AbstractFeats
from backend.core.feats.feats import Feats
from backend.core.feats.feat_manager import FeatManager
from backend.core.feats.llm_feat_advisor import LLMFeatAdvisor

__all__ = [
    'AbstractFeats',
    'Feats',
    'FeatManager',
    'LLMFeatAdvisor',
]