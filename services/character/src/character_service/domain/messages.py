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
    version: str
    metadata: Dict[str, Any]


@dataclass
class CharacterStateMessage(Message):
    """Message containing character state changes."""

    character_id: UUID
    state_version: int
    state_data: Dict[str, Any]
    previous_version: int
    state_changes: Dict[str, Any]


@dataclass
class CampaignEventMessage(Message):
    """Message about campaign events."""

    event_id: UUID
    character_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    applied: bool
    reverted: bool
    impacts: List[Dict[str, Any]]


@dataclass
class ProgressEventMessage(Message):
    """Message about character progression."""

    character_id: UUID
    progress_type: str
    progress_data: Dict[str, Any]
    experience_points: int
    current_level: int


@dataclass
class StateSyncMessage(Message):
    """Message for state synchronization."""

    character_id: UUID
    requested_version: int
    from_timestamp: datetime
    include_history: bool
    force_sync: bool


@dataclass
class ErrorMessage(Message):
    """Message for error reporting."""

    error_code: str
    error_message: str
    source_message_id: UUID
    retry_count: int
    should_retry: bool
