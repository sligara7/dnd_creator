"""Game Session Service - WebSocket Models.

This module defines data models for WebSocket communication.
"""
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Union
from uuid import UUID

from pydantic import BaseModel, Field


class WebSocketEventType(str, Enum):
    """WebSocket event types."""

    # Connection Events
    CONNECTION_ESTABLISHED = "connection_established"
    CONNECTION_ERROR = "connection_error"
    HEARTBEAT = "heartbeat"

    # State Events
    STATE_UPDATE = "state_update"
    SYNC_REQUEST = "sync_request"
    SYNC_RESPONSE = "sync_response"

    # Combat Events
    INITIATIVE_ROLL = "initiative_roll"
    TURN_CHANGE = "turn_change"
    ACTION_DECLARE = "action_declare"
    ACTION_RESOLVE = "action_resolve"


class BaseEvent(BaseModel):
    """Base model for all WebSocket events."""

    type: WebSocketEventType
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class ConnectionEvent(BaseEvent):
    """Connection event data."""

    session_id: UUID
    player_id: UUID


class ConnectionErrorEvent(BaseEvent):
    """Connection error event data."""

    code: str
    message: str


class HeartbeatEvent(BaseEvent):
    """Heartbeat event data."""

    pass


class StateChange(BaseModel):
    """State change data."""

    path: str
    value: Any
    previous: Any


class StateUpdateEvent(BaseEvent):
    """State update event data."""

    update_id: UUID
    changes: List[StateChange]


class SyncRequestEvent(BaseEvent):
    """State sync request event data."""

    paths: List[str]


class SyncResponseEvent(BaseEvent):
    """State sync response event data."""

    state: Dict[str, Any]
    version: str


class InitiativeRollEvent(BaseEvent):
    """Initiative roll event data."""

    character_id: UUID
    roll: int
    modifiers: Dict[str, Any]


class TurnChangeEvent(BaseEvent):
    """Turn change event data."""

    active_character: UUID
    round: int
    turn_number: int


class ActionDeclareEvent(BaseEvent):
    """Action declaration event data."""

    action_id: UUID
    character_id: UUID
    action_type: str
    targets: List[UUID]
    details: Dict[str, Any]


class ActionOutcome(BaseModel):
    """Action outcome data."""

    target_id: UUID
    effects: List[str]
    damage: Dict[str, int]
    conditions: List[str]


class ActionResolveEvent(BaseEvent):
    """Action resolution event data."""

    action_id: UUID
    outcomes: List[ActionOutcome]


# Event type mapping for deserialization
EVENT_TYPE_MAP = {
    WebSocketEventType.CONNECTION_ESTABLISHED: ConnectionEvent,
    WebSocketEventType.CONNECTION_ERROR: ConnectionErrorEvent,
    WebSocketEventType.HEARTBEAT: HeartbeatEvent,
    WebSocketEventType.STATE_UPDATE: StateUpdateEvent,
    WebSocketEventType.SYNC_REQUEST: SyncRequestEvent,
    WebSocketEventType.SYNC_RESPONSE: SyncResponseEvent,
    WebSocketEventType.INITIATIVE_ROLL: InitiativeRollEvent,
    WebSocketEventType.TURN_CHANGE: TurnChangeEvent,
    WebSocketEventType.ACTION_DECLARE: ActionDeclareEvent,
    WebSocketEventType.ACTION_RESOLVE: ActionResolveEvent,
}