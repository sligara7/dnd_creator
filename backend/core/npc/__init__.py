"""
D&D 2024 NPC System

This package provides classes for generating and managing non-player characters (NPCs) 
in D&D, including AI-assisted NPC creation and customization.

Classes:
    AbstractNPC: Base class defining the NPC system interface
    NPC: Implementation of D&D 2024 NPCs
    LLMNPCAdvisor: AI-powered advisor for creating compelling and
                   realistic NPCs with personalities and motivations
    LLMMassNPCAdvisor: AI-powered advisor for generating groups of
                      related NPCs with appropriate variations
"""

from backend.core.npc.abstract_npc import AbstractNPC
from backend.core.npc.npc import NPC
from backend.core.npc.llm_npc_advisor import LLMNPCAdvisor
from backend.core.npc.llm_mass_npc_advisor import LLMMassNPCAdvisor

__all__ = [
    'AbstractNPC',
    'NPC',
    'LLMNPCAdvisor',
    'LLMMassNPCAdvisor',
]