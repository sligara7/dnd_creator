"""
D&D 2024 Species System

This package provides classes for managing character species (formerly races) in D&D,
including standard species, custom species creation, and AI-assisted species features.

Classes:
    AbstractSpecies: Base class defining the species system interface
    SpeciesSize: Enumeration of available species sizes
    Species: Implementation of standard D&D 2024 species
    CustomSpecies: Support for creating custom species
    SpeciesManager: Manager class for handling all species-related operations
    LLMSpeciesAdvisor: AI-powered helper for species recommendations and generation
"""

from backend.core.species.abstract_species import AbstractSpecies, SpeciesSize
from backend.core.species.species import Species, CustomSpecies, SpeciesManager
from backend.core.species.llm_species_advisor import LLMSpeciesAdvisor

__all__ = [
    'AbstractSpecies',
    'SpeciesSize',
    'Species',
    'CustomSpecies',
    'SpeciesManager',
    'LLMSpeciesAdvisor',
]