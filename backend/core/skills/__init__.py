"""
D&D 2024 Skills System

This package provides classes for managing character skills in D&D,
including skill proficiencies, skill checks, and AI-assisted skill recommendations.

Classes:
    AbstractSkills: Base class defining the skills system interface
    Skills: Implementation of D&D 2024 skills system
    LLMSkillsAdvisor: AI-powered helper for skill recommendations and creative usage
"""

from backend.core.skills.abstract_skills import AbstractSkills
from backend.core.skills.skills import Skills
from backend.core.skills.llm_skills_advisor import LLMSkillsAdvisor

__all__ = [
    'AbstractSkills',
    'Skills',
    'LLMSkillsAdvisor',
]