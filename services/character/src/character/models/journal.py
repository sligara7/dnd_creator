"""Journal models for the character service.

This module provides models for character journals, including session logs,
experience tracking, and milestone achievements.
"""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import Field
from sqlmodel import JSON

from .base import BaseDBModel, BaseVersionedDBModel

class JournalEntry(BaseDBModel):
    """Individual character journal entry."""
    character_id: UUID
    session_date: datetime
    content: str
    xp_gained: int = Field(default=0, ge=0)
    milestones: List[str] = Field(default_factory=list)
    dm_notes: Optional[str] = None
    session_number: Optional[int] = None
    session_title: Optional[str] = None
    party_members: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    npcs_met: List[str] = Field(default_factory=list)
    quests_updated: List[Dict] = Field(default_factory=list)
    items_acquired: List[Dict] = Field(default_factory=list)
    items_lost: List[Dict] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)

class CharacterJournal(BaseVersionedDBModel):
    """Complete character journal with all entries and summary data."""
    character_id: UUID
    entries: List[JournalEntry] = Field(default_factory=list)
    total_xp: int = Field(default=0, ge=0)
    milestones_achieved: List[str] = Field(default_factory=list)
    notes: Dict[str, str] = Field(default_factory=dict, sa_column=JSON)

    # Campaign Integration
    campaign_id: Optional[UUID] = None
    party_name: Optional[str] = None
    active_quests: List[Dict] = Field(default_factory=list)
    completed_quests: List[Dict] = Field(default_factory=list)
    faction_standings: Dict[str, int] = Field(default_factory=dict)
    reputation_scores: Dict[str, int] = Field(default_factory=dict)
    
    # Achievements and Tracking
    notable_achievements: List[Dict] = Field(default_factory=list)
    combat_statistics: Dict = Field(default_factory=dict, sa_column=JSON)
    roleplay_highlights: List[Dict] = Field(default_factory=list)
    character_development_notes: List[Dict] = Field(default_factory=list)

class CampaignJournal(BaseVersionedDBModel):
    """Campaign-wide journal integrating multiple character journals."""
    campaign_id: UUID
    title: str
    description: Optional[str] = None
    dm_id: UUID
    players: List[Dict] = Field(default_factory=list)
    session_summaries: List[Dict] = Field(default_factory=list)
    world_notes: Dict = Field(default_factory=dict, sa_column=JSON)
    plot_points: List[Dict] = Field(default_factory=list)
    active_storylines: List[Dict] = Field(default_factory=list)
    completed_storylines: List[Dict] = Field(default_factory=list)
    world_state: Dict = Field(default_factory=dict, sa_column=JSON)
    metadata: Dict = Field(default_factory=dict, sa_column=JSON)
