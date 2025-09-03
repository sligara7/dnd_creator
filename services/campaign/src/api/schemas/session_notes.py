"""Session notes API schemas."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FeedbackStatus(str, Enum):
    """Session feedback processing status."""
    PENDING = "pending"
    PROCESSED = "processed"
    APPLIED = "applied"


class CharacterType(str, Enum):
    """Type of character in session."""
    PLAYER = "player"
    NPC = "npc"


class EventType(str, Enum):
    """Types of significant events."""
    COMBAT = "combat"
    ROLEPLAY = "roleplay"
    QUEST = "quest"
    DISCOVERY = "discovery"
    DECISION = "decision"
    MILESTONE = "milestone"


class InteractionType(str, Enum):
    """Types of character interactions."""
    COMBAT = "combat"
    DIALOGUE = "dialogue"
    ASSIST = "assist"
    OPPOSE = "oppose"
    TRADE = "trade"
    ALLIANCE = "alliance"
    BETRAYAL = "betrayal"


class CharacterInteraction(BaseModel):
    """Record of interaction between characters."""
    source_character: str = Field(..., description="ID or reference of initiating character")
    target_character: str = Field(..., description="ID or reference of target character")
    interaction_type: InteractionType
    description: str
    outcome: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class SignificantEvent(BaseModel):
    """Record of significant session event."""
    event_type: EventType
    description: str
    location: Optional[str] = None
    characters_involved: List[str] = Field(default_factory=list)
    consequences: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class PlotDecision(BaseModel):
    """Record of major plot decision."""
    decision_point: str
    choice_made: str
    characters_involved: List[str] = Field(default_factory=list)
    immediate_consequences: List[str] = Field(default_factory=list)
    potential_future_impacts: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class CharacterAction(BaseModel):
    """Record of significant character action."""
    action_type: str
    description: str
    outcome: str
    impact_level: str = Field(default="normal")
    metadata: Dict = Field(default_factory=dict)


class CharacterReward(BaseModel):
    """Record of rewards earned by character."""
    reward_type: str
    description: str
    value: Optional[Dict] = None
    reason: str
    metadata: Dict = Field(default_factory=dict)


class CharacterConsequence(BaseModel):
    """Record of consequences for character actions."""
    consequence_type: str
    description: str
    severity: str
    duration: Optional[str] = None
    metadata: Dict = Field(default_factory=dict)


class CreateSessionNoteRequest(BaseModel):
    """Request model for session note creation."""
    campaign_id: UUID
    chapter_id: Optional[UUID] = None
    session_number: int
    title: str
    narrative: str
    dm_id: str
    players_present: List[str]
    objectives_completed: List[str] = Field(default_factory=list)
    significant_events: List[SignificantEvent] = Field(default_factory=list)
    character_interactions: List[CharacterInteraction] = Field(default_factory=list)
    plot_decisions: List[PlotDecision] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class UpdateSessionNoteRequest(BaseModel):
    """Request model for session note updates."""
    title: Optional[str] = None
    narrative: Optional[str] = None
    objectives_completed: Optional[List[str]] = None
    significant_events: Optional[List[SignificantEvent]] = None
    character_interactions: Optional[List[CharacterInteraction]] = None
    plot_decisions: Optional[List[PlotDecision]] = None
    metadata: Optional[Dict] = None


class ProcessNoteFeedbackRequest(BaseModel):
    """Request to process session note feedback."""
    apply_to_campaign: bool = True
    apply_to_characters: bool = True
    apply_to_npcs: bool = True
    custom_rules: Optional[Dict] = None


class SessionNoteCharacterRecord(BaseModel):
    """Character activity record from session."""
    character_id: str
    character_type: CharacterType
    interactions: List[CharacterInteraction] = Field(default_factory=list)
    significant_actions: List[CharacterAction] = Field(default_factory=list)
    rewards_earned: List[CharacterReward] = Field(default_factory=list)
    consequences: List[CharacterConsequence] = Field(default_factory=list)
    traits_demonstrated: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class SessionNoteSummary(BaseModel):
    """Summary of session note."""
    id: UUID
    campaign_id: UUID
    chapter_id: Optional[UUID]
    session_number: int
    title: str
    feedback_status: FeedbackStatus
    created_at: datetime
    feedback_processed_at: Optional[datetime]


class SessionNoteDetail(BaseModel):
    """Detailed session note information."""
    id: UUID
    campaign_id: UUID
    chapter_id: Optional[UUID]
    session_number: int
    title: str
    narrative: str
    dm_id: str
    players_present: List[str]
    objectives_completed: List[str]
    significant_events: List[SignificantEvent]
    character_interactions: List[CharacterInteraction]
    plot_decisions: List[PlotDecision]
    feedback_status: FeedbackStatus
    created_at: datetime
    feedback_processed_at: Optional[datetime]
    metadata: Dict


class FeedbackResult(BaseModel):
    """Result of feedback processing."""
    campaign_updates: Optional[Dict] = None
    character_updates: List[Dict] = Field(default_factory=list)
    npc_updates: List[Dict] = Field(default_factory=list)
    processing_notes: List[str] = Field(default_factory=list)
