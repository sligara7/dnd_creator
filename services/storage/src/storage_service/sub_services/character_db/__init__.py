"""Character database sub-service for the storage service.

This module provides database storage and access for character-related data
as a sub-service within the storage service.
"""

from .handler import CharacterDBMessageHandler
from .service import CharacterDBService
from .models.models import (
    Character,
    InventoryItem,
    JournalEntry,
    ExperienceEntry,
    Quest,
    NPCRelationship,
    CampaignEvent,
    EventImpact,
    CharacterProgress
)

__all__ = [
    'CharacterDBMessageHandler',
    'CharacterDBService',
    'Character',
    'InventoryItem',
    'JournalEntry',
    'ExperienceEntry',
    'Quest',
    'NPCRelationship',
    'CampaignEvent',
    'EventImpact',
    'CharacterProgress'
]