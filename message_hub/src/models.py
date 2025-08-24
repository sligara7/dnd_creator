"""
Message Hub Data Models

Pydantic models for request/response data validation.
"""

from enum import Enum
from typing import Dict, Optional, Any, List
from pydantic import BaseModel, Field
from datetime import datetime

class ServiceType(str, Enum):
    """Available service types."""
    CHARACTER_SERVICE = "character-service"
    RULES_SERVICE = "rules-service"
    INVENTORY_SERVICE = "inventory-service"
    SPELLS_SERVICE = "spells-service"
    MESSAGE_HUB = "message-hub"
    VALIDATION_SERVICE = "validation-service"

class MessageType(str, Enum):
    """Types of messages that can be sent between services."""
    # Character events
    CHARACTER_CREATED = "character.created"
    CHARACTER_UPDATED = "character.updated"
    CHARACTER_DELETED = "character.deleted"
    
    # Character attribute events
    ABILITY_SCORES_UPDATED = "ability_scores.updated"
    SKILLS_UPDATED = "skills.updated"
    BACKGROUND_UPDATED = "background.updated"
    RACE_UPDATED = "race.updated"
    CLASS_UPDATED = "class.updated"
    
    # Inventory and equipment events
    INVENTORY_UPDATED = "inventory.updated"
    SPELLS_UPDATED = "spells.updated"
    FEATURES_UPDATED = "features.updated"
    
    # Progression events
    CHARACTER_LEVEL_UP = "character.level_up"
    CHARACTER_EXPERIENCE_GAINED = "character.experience_gained"
    
    # Transaction events
    TRANSACTION_PREPARE = "transaction.prepare"
    TRANSACTION_COMMIT = "transaction.commit"
    TRANSACTION_ROLLBACK = "transaction.rollback"

class ServiceMessage(BaseModel):
    """Message sent between services."""
    source: ServiceType
    destination: ServiceType
    message_type: MessageType
    correlation_id: str = Field(..., description="Unique ID for tracing requests")
    payload: Dict[str, Any]
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    reply_to: Optional[str] = None

class ServiceResponse(BaseModel):
    """Response to a service message."""
    correlation_id: str
    status: str
    data: Dict[str, Any]
    error: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)

class ServiceRegistration(BaseModel):
    """Service registration information."""
    name: ServiceType
    url: str
    health_check: str
    version: str
    capabilities: List[MessageType]

class ServiceStatus(BaseModel):
    """Current status of a registered service."""
    name: ServiceType
    url: str
    status: str
    last_check: datetime
    latency: float
    error: Optional[str] = None
