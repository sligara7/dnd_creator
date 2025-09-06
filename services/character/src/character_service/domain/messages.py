"""Message models for inter-service communication."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID


class MessageType(Enum):
    """Types of messages that can be sent/received."""

    # Character state events
    CHARACTER_CREATED = auto()
    CHARACTER_UPDATED = auto()
    CHARACTER_DELETED = auto()
    CHARACTER_STATE_CHANGED = auto()

    # Campaign events
    CAMPAIGN_EVENT_CREATED = auto()
    CAMPAIGN_EVENT_APPLIED = auto()
    CAMPAIGN_EVENT_REVERTED = auto()

    # Progress events
    EXPERIENCE_GAINED = auto()
    LEVEL_CHANGED = auto()
    MILESTONE_ACHIEVED = auto()
    ACHIEVEMENT_UNLOCKED = auto()

    # System events
    STATE_SYNC_REQUESTED = auto()
    STATE_SYNC_COMPLETED = auto()
    HEALTH_CHECK = auto()
    ERROR = auto()


@dataclass
class Message:
    """Base message model."""

    id: UUID
    type: MessageType
    timestamp: datetime
    version: str = "1.0"
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CharacterStateMessage(Message):
    """Message containing character state changes."""

    character_id: UUID
    state_version: int
    state_data: Dict[str, Any]
    previous_version: Optional[int] = None
    state_changes: Optional[Dict[str, Any]] = None


@dataclass
class CampaignEventMessage(Message):
    """Message about campaign events."""

    event_id: UUID
    character_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    applied: bool = False
    reverted: bool = False
    impacts: List[Dict[str, Any]] = field(default_factory=list)


@dataclass
class ProgressEventMessage(Message):
    """Message about character progression."""

    character_id: UUID
    progress_type: str
    progress_data: Dict[str, Any]
    experience_points: Optional[int] = None
    current_level: Optional[int] = None


@dataclass
class StateSyncMessage(Message):
    """Message for state synchronization."""

    character_id: UUID
    requested_version: Optional[int] = None
    from_timestamp: Optional[datetime] = None
    include_history: bool = False
    force_sync: bool = False


@dataclass
class ErrorMessage(Message):
    """Message for error reporting."""

    error_code: str
    error_message: str
    source_message_id: Optional[UUID] = None
    retry_count: int = 0
    should_retry: bool = True
