"""
Event models and schemas for the Audit Service.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, ConfigDict

class Actor(BaseModel):
    """Actor who performed the action."""
    id: str = Field(..., description="ID of the actor")
    type: str = Field(..., description="Type of actor (user|service|system)")
    name: str = Field(..., description="Name of the actor")

class Target(BaseModel):
    """Target of the action."""
    id: str = Field(..., description="ID of the target")
    type: str = Field(..., description="Type of target")
    name: str = Field(..., description="Name of the target")

class Context(BaseModel):
    """Event context."""
    request_id: Optional[str] = Field(None, description="Request correlation ID")
    session_id: Optional[str] = Field(None, description="User session ID")
    ip_address: Optional[str] = Field(None, description="Source IP address")
    user_agent: Optional[str] = Field(None, description="User agent string")
    environment: str = Field(..., description="Environment (prod|staging|dev)")
    source: str = Field(..., description="Source application or service")

class EventChanges(BaseModel):
    """Changes made during the event."""
    field: str = Field(..., description="Field that was changed")
    old_value: Optional[Any] = Field(None, description="Previous value")
    new_value: Optional[Any] = Field(None, description="New value")
    change_type: str = Field(..., description="Type of change (create|update|delete)")

class EventData(BaseModel):
    """Additional event data."""
    changes: Optional[List[EventChanges]] = Field(None, description="List of changes made")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    sensitive: bool = Field(False, description="Whether the event contains sensitive data")
    encrypted_fields: List[str] = Field(default_factory=list, description="List of encrypted fields")

class Event(BaseModel):
    """Core audit event model."""
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "service": "character_service",
                "type": "character.created",
                "action": "create",
                "actor": {
                    "id": "user123",
                    "type": "user",
                    "name": "John Doe"
                },
                "target": {
                    "id": "char456",
                    "type": "character",
                    "name": "Aragorn"
                },
                "context": {
                    "request_id": "req789",
                    "session_id": "sess012",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0",
                    "environment": "prod",
                    "source": "web_ui"
                },
                "data": {
                    "changes": [
                        {
                            "field": "name",
                            "old_value": None,
                            "new_value": "Aragorn",
                            "change_type": "create"
                        }
                    ],
                    "metadata": {
                        "campaign_id": "camp123"
                    }
                },
                "severity": "info",
                "outcome": "success",
                "retention_period": "180d"
            }
        }
    )

    id: UUID = Field(default_factory=uuid4, description="Unique event ID")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Event timestamp")
    service: str = Field(..., description="Service that generated the event")
    type: str = Field(..., description="Event type")
    action: str = Field(..., description="Action performed")
    actor: Actor = Field(..., description="Actor who performed the action")
    target: Target = Field(..., description="Target of the action")
    context: Context = Field(..., description="Event context")
    data: EventData = Field(default_factory=EventData, description="Event data")
    severity: str = Field(..., description="Event severity (info|warning|error)")
    outcome: str = Field(..., description="Event outcome (success|failure|error)")
    retention_period: str = Field(
        ..., 
        description="Retention period (30d|90d|180d|1y|7y)",
        pattern="^(30d|90d|180d|1y|7y)$"
    )

class SecurityEvent(Event):
    """Security-related audit event."""
    auth_context: Dict[str, Any] = Field(
        default_factory=dict, 
        description="Authentication context"
    )
    permissions: List[str] = Field(
        default_factory=list,
        description="Relevant permissions"
    )
    risk_level: str = Field(
        ...,
        description="Risk level (low|medium|high|critical)"
    )

class UserEvent(Event):
    """User activity audit event."""
    user_id: str = Field(..., description="User ID")
    user_type: str = Field(..., description="User type")
    session_data: Optional[Dict[str, Any]] = Field(
        None,
        description="Session-related data"
    )

class SystemEvent(Event):
    """System-level audit event."""
    component: str = Field(..., description="System component")
    resource_id: Optional[str] = Field(None, description="Resource identifier")
    operation: str = Field(..., description="Operation performed")
    performance_impact: Optional[str] = Field(
        None,
        description="Impact on system performance"
    )

class ComplianceEvent(Event):
    """Compliance-related audit event."""
    regulation: str = Field(..., description="Applicable regulation")
    compliance_status: str = Field(..., description="Compliance status")
    controls: List[str] = Field(
        default_factory=list,
        description="Affected compliance controls"
    )
    data_categories: List[str] = Field(
        default_factory=list,
        description="Categories of data involved"
    )

class BatchEventUpload(BaseModel):
    """Batch event upload model."""
    events: List[Event]
    
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "example": {
                "events": [
                    {
                        "service": "character_service",
                        "type": "character.modified",
                        "action": "update",
                        "actor": {
                            "id": "user123",
                            "type": "user",
                            "name": "John Doe"
                        },
                        "target": {
                            "id": "char456",
                            "type": "character",
                            "name": "Aragorn"
                        },
                        "context": {
                            "request_id": "req789",
                            "environment": "prod",
                            "source": "web_ui"
                        },
                        "severity": "info",
                        "outcome": "success",
                        "retention_period": "180d"
                    }
                ]
            }
        }
    )