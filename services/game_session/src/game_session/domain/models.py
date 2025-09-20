"""Domain models for the Game Session Service."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field

class SessionStatus(str, Enum):
    """Possible states for a game session."""
    CREATED = "created"
    ACTIVE = "active"
    PAUSED = "paused"
    ENDED = "ended"

class CombatStatus(str, Enum):
    """Possible states for combat."""
    INACTIVE = "inactive"
    PREPARING = "preparing"
    ACTIVE = "active"
    ENDED = "ended"

class SessionPlayer(BaseModel):
    """A player in a game session."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    character_id: UUID
    user_id: UUID
    connected: bool = False
    last_seen: Optional[datetime] = None

class CombatParticipant(BaseModel):
    """A participant in combat."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    character_id: UUID
    initiative: int
    conditions: List[str] = Field(default_factory=list)
    position: Optional[Dict[str, int]] = None

class Combat(BaseModel):
    """Combat state within a session."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    status: CombatStatus = CombatStatus.INACTIVE
    round: int = 0
    current_turn: Optional[UUID] = None
    participants: List[CombatParticipant] = Field(default_factory=list)
    initiative_order: List[UUID] = Field(default_factory=list)
    started_at: Optional[datetime] = None
    ended_at: Optional[datetime] = None

class GameSession(BaseModel):
    """A D&D game session."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    campaign_id: UUID
    name: str
    status: SessionStatus = SessionStatus.CREATED
    players: List[SessionPlayer] = Field(default_factory=list)
    combat: Optional[Combat] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    ended_at: Optional[datetime] = None

class StateVersion(BaseModel):
    """Version information for session state."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID = Field(default_factory=uuid4)
    session_id: UUID
    version: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)