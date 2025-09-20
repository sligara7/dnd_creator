"""Message hub client and message models."""

from enum import Enum
from typing import Optional, Any, Dict, List
from pydantic import BaseModel, Field
from datetime import datetime

class MessageType(str, Enum):
    """Message type enumeration."""
    # Storage operations
    STORAGE_CREATE = "storage.create"
    STORAGE_READ = "storage.read"
    STORAGE_UPDATE = "storage.update"
    STORAGE_DELETE = "storage.delete"
    
    # Storage responses
    STORAGE_RESPONSE = "storage.response"
    STORAGE_ERROR = "storage.error"

class MessageHeader(BaseModel):
    """Common message header."""
    message_id: str
    message_type: MessageType
    correlation_id: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    source_service: str = "metrics"
    reply_to: Optional[str] = None

class Message(BaseModel):
    """Base message model."""
    header: MessageHeader
    payload: Dict[str, Any]

# Storage Models
class AlertRule(BaseModel):
    """Alert rule model for storage."""
    id: str
    name: str
    expression: str
    duration: str
    severity: str
    labels: Optional[Dict[str, str]] = None
    annotations: Optional[Dict[str, str]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False

class Dashboard(BaseModel):
    """Dashboard model for storage."""
    id: str
    title: str
    description: Optional[str] = None
    panels: List[Dict[str, Any]]
    refresh_interval: str = "1m"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_deleted: bool = False