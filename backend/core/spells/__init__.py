"""
D&D 2024 Spellcasting System

This package contains classes for managing spells, spell lists, and spellcasting mechanics
for the D&D character creator tool.

Classes:
    AbstractSpells: Base class defining the spell system interface
    Spell: Implementation of spells and spellcasting for D&D 2024 edition
    LLMSpellsAdvisor: AI-powered helper for spell recommendations and descriptions
"""

from backend.core.spells.abstract_spells import AbstractSpells
from backend.core.spells.spell import Spell
from backend.core.spells.llm_spells_advisor import LLMSpellsAdvisor

__all__ = [
    'AbstractSpells',
    'Spell',
    'LLMSpellsAdvisor',
]