"""
Event Store Helpers

Utility functions for event store operations.
"""

from typing import Optional, Dict, Any
from uuid import uuid4

from ..models import ServiceType, MessageType
from .models import EventType
from .service import EventStore

def message_to_event_type(message_type: MessageType) -> Optional[EventType]:
    """Convert a message type to an event type."""
    try:
        return EventType(message_type.value)
    except ValueError:
        return None

def create_event_metadata(
    service_type: ServiceType,
    correlation_id: str,
    causation_id: Optional[str] = None,
    additional_metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create standardized event metadata."""
    metadata = {
        "source_service": service_type.value,
        "correlation_id": correlation_id,
    }
    
    if causation_id:
        metadata["causation_id"] = causation_id
        
    if additional_metadata:
        metadata.update(additional_metadata)
    
    return metadata

async def store_transaction_event(
    event_store: EventStore,
    event_type: EventType,
    service: ServiceType,
    transaction_id: str,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store a transaction-related event."""
    # Create stream ID for transaction if needed
    stream_id = f"transaction-{transaction_id}"
    
    event = await event_store.append_event(
        event_type=event_type,
        source_service=service,
        data=data,
        stream_id=stream_id,
        metadata=metadata or {}
    )
    
    return event.event_id

async def store_service_event(
    event_store: EventStore,
    event_type: EventType,
    service: ServiceType,
    data: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """Store a service operation event."""
    event = await event_store.append_event(
        event_type=event_type,
        source_service=service,
        data=data,
        metadata=metadata or {}
    )
    
    return event.event_id
