"""Game Session Service - Storage Models.

This module defines data models for storage-related operations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class SessionMetadata(BaseModel):
    """Session metadata model."""

    campaign_id: UUID
    name: str
    status: str = "active"
    metadata: Dict[str, Any] = Field(default_factory=dict)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class SessionState(BaseModel):
    """Session state model."""

    id: UUID
    session_id: UUID
    state: Dict[str, Any]
    version: str
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SessionEvent(BaseModel):
    """Session event model."""

    id: UUID
    session_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    created_at: datetime = Field(default_factory=datetime.utcnow)


class StorageSaveStateRequest(BaseModel):
    """Storage save state request model."""

    session_id: UUID
    state: Dict[str, Any]
    metadata: Dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StorageSaveStateResponse(BaseModel):
    """Storage save state response model."""

    session_id: UUID
    version: str
    timestamp: datetime


class StorageLoadStateRequest(BaseModel):
    """Storage load state request model."""

    session_id: UUID
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StorageLoadStateResponse(BaseModel):
    """Storage load state response model."""

    session_id: UUID
    state: Dict[str, Any]
    version: str
    metadata: Dict[str, Any]
    timestamp: datetime


class StorageSaveEventRequest(BaseModel):
    """Storage save event request model."""

    session_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class StorageSaveEventResponse(BaseModel):
    """Storage save event response model."""

    session_id: UUID
    event_id: UUID
    timestamp: datetime