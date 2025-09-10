"""Test utilities for service layer tests."""
from typing import Dict, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository
from character_service.services.character import AbilityScores


def create_test_ability_scores(
    strength: int = 15,
    dexterity: int = 14,
    constitution: int = 13,
    intelligence: int = 12,
    wisdom: int = 10,
    charisma: int = 8
) -> AbilityScores:
    """Create test ability scores.
    
    Args:
        strength: Strength score
        dexterity: Dexterity score
        constitution: Constitution score
        intelligence: Intelligence score
        wisdom: Wisdom score
        charisma: Charisma score
        
    Returns:
        Dictionary of ability scores
    """
    return {
        "strength": strength,
        "dexterity": dexterity,
        "constitution": constitution,
        "intelligence": intelligence,
        "wisdom": wisdom,
        "charisma": charisma
    }
