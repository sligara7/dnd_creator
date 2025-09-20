"""Event models for Message Hub.

Defines event types and structures for message passing and event handling.
"""

from typing import Any, Dict, List, Optional, Union
from enum import Enum
from datetime import datetime
from uuid import UUID
from pydantic import BaseModel, Field


class EventType(str, Enum):
    # Message Events
    MESSAGE_SENT = "message.sent"
    MESSAGE_DELIVERED = "message.delivered"
    MESSAGE_FAILED = "message.failed"
    MESSAGE_RETRIED = "message.retried"
    
    # Service Events
    SERVICE_REGISTERED = "service.registered"
    SERVICE_DEREGISTERED = "service.deregistered"
    SERVICE_HEALTH_CHANGED = "service.health_changed"
    
    # Transaction Events
    TRANSACTION_STARTED = "transaction.started"
    TRANSACTION_COMMITTED = "transaction.committed"
    TRANSACTION_ROLLED_BACK = "transaction.rolled_back"
    
    # Game Session Events
    GAME_SESSION_STARTED = "game.session.started"
    GAME_SESSION_ENDED = "game.session.ended"
    COMBAT_STARTED = "game.combat.started"
    COMBAT_ENDED = "game.combat.ended"
    TURN_STARTED = "game.combat.turn.started"
    TURN_ENDED = "game.combat.turn.ended"
    STATE_UPDATED = "game.state.updated"
    ACTION_PERFORMED = "game.action.performed"
    REACTION_TRIGGERED = "game.reaction.triggered"


class EventStatus(str, Enum):
    """Status of an event in the system."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    RETRYING = "retrying"
    DEAD_LETTER = "dead_letter"


class GameEventPriority(str, Enum):
    """Priority levels for game events."""
    CRITICAL = "critical"  # Combat actions, immediate responses needed
    HIGH = "high"         # Important game state updates
    NORMAL = "normal"     # Regular game flow events
    LOW = "low"          # Background updates, non-critical info


class EventMetadata(BaseModel):
    """Common metadata for all events."""
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    correlation_id: Optional[str] = None
    session_id: Optional[str] = None
    priority: Optional[Union[GameEventPriority, str]] = None
    retry_count: int = 0
    source_trace: List[str] = Field(default_factory=list)


class MessageEvent(BaseModel):
    """Base model for message events."""
    id: UUID
    type: EventType
    source: str
    destination: str
    payload: Dict[str, Any]
    metadata: EventMetadata
    status: EventStatus = EventStatus.PENDING


class ServiceEvent(BaseModel):
    """Base model for service events."""
    id: UUID
    type: EventType
    service_name: str
    status: str
    details: Dict[str, Any]
    metadata: EventMetadata


class GameEvent(BaseModel):
    """Base model for game session events."""
    id: UUID
    type: EventType
    session_id: str
    campaign_id: str
    payload: Dict[str, Any]
    metadata: EventMetadata
    priority: GameEventPriority = GameEventPriority.NORMAL


class CombatEvent(GameEvent):
    """Specialized event for combat actions."""
    combat_id: str
    round_number: int
    turn_order: int
    character_id: str
    target_ids: List[str]
    action_type: str