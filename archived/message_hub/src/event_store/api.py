"""
Event Store HTTP API Router

Provides REST endpoints for event store operations.
"""

from typing import Dict, List, Optional, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..database import get_session
from ..models import ServiceType
from .models import EventType
from .service import EventStore

router = APIRouter(prefix="/v1/events", tags=["events"])

class EventData(BaseModel):
    """Event data model for API requests."""
    event_type: EventType
    source_service: ServiceType
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    stream_id: Optional[str] = None

class EventResponse(BaseModel):
    """Event response model."""
    event_id: str
    event_type: EventType
    source_service: str
    sequence_number: int
    timestamp: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]
    correlation_id: Optional[str] = None
    causation_id: Optional[str] = None
    stream_id: Optional[str] = None

class StreamRequest(BaseModel):
    """Stream creation request model."""
    stream_type: str
    metadata: Optional[Dict[str, Any]] = None

class StreamResponse(BaseModel):
    """Stream response model."""
    stream_id: str
    stream_type: str
    created_at: str
    last_event_at: Optional[str] = None
    metadata: Dict[str, Any]

class SubscriptionRequest(BaseModel):
    """Subscription creation request model."""
    subscriber_service: ServiceType
    event_types: Optional[List[EventType]] = None
    source_services: Optional[List[ServiceType]] = None
    metadata: Optional[Dict[str, Any]] = None

class SubscriptionResponse(BaseModel):
    """Subscription response model."""
    subscription_id: str
    subscriber_service: str
    event_types: Optional[List[EventType]] = None
    source_services: Optional[List[str]] = None
    last_processed_sequence: int
    last_processed_at: Optional[str] = None
    metadata: Dict[str, Any]

@router.post("/", response_model=EventResponse)
async def append_event(
    event_data: EventData,
    session: AsyncSession = Depends(get_session)
) -> EventResponse:
    """Append a new event to the store."""
    try:
        event_store = EventStore(lambda: session)
        event = await event_store.append_event(
            event_type=event_data.event_type,
            source_service=event_data.source_service,
            data=event_data.data,
            metadata=event_data.metadata,
            correlation_id=event_data.correlation_id,
            causation_id=event_data.causation_id,
            stream_id=event_data.stream_id
        )
        
        return EventResponse(
            event_id=event.event_id,
            event_type=event.event_type,
            source_service=event.source_service,
            sequence_number=event.sequence_number,
            timestamp=event.timestamp.isoformat(),
            data=event.data,
            metadata=event.metadata,
            correlation_id=event.correlation_id,
            causation_id=event.causation_id,
            stream_id=event.stream_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[EventResponse])
async def get_events(
    after_sequence: Optional[int] = None,
    event_types: Optional[List[EventType]] = None,
    source_services: Optional[List[ServiceType]] = None,
    stream_id: Optional[str] = None,
    limit: int = 100,
    session: AsyncSession = Depends(get_session)
) -> List[EventResponse]:
    """Get events based on filters."""
    try:
        event_store = EventStore(lambda: session)
        events = await event_store.get_events(
            after_sequence=after_sequence,
            event_types=event_types,
            source_services=source_services,
            stream_id=stream_id,
            limit=limit
        )
        
        return [
            EventResponse(
                event_id=event.event_id,
                event_type=event.event_type,
                source_service=event.source_service,
                sequence_number=event.sequence_number,
                timestamp=event.timestamp.isoformat(),
                data=event.data,
                metadata=event.metadata,
                correlation_id=event.correlation_id,
                causation_id=event.causation_id,
                stream_id=event.stream_id
            )
            for event in events
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/streams", response_model=StreamResponse)
async def create_stream(
    stream_data: StreamRequest,
    session: AsyncSession = Depends(get_session)
) -> StreamResponse:
    """Create a new event stream."""
    try:
        event_store = EventStore(lambda: session)
        stream = await event_store.create_stream(
            stream_type=stream_data.stream_type,
            metadata=stream_data.metadata
        )
        
        return StreamResponse(
            stream_id=stream.stream_id,
            stream_type=stream.stream_type,
            created_at=stream.created_at.isoformat(),
            last_event_at=stream.last_event_at.isoformat() if stream.last_event_at else None,
            metadata=stream.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/subscriptions", response_model=SubscriptionResponse)
async def create_subscription(
    subscription_data: SubscriptionRequest,
    session: AsyncSession = Depends(get_session)
) -> SubscriptionResponse:
    """Create a new event subscription."""
    try:
        event_store = EventStore(lambda: session)
        subscription = await event_store.create_subscription(
            subscriber_service=subscription_data.subscriber_service,
            event_types=subscription_data.event_types,
            source_services=subscription_data.source_services,
            metadata=subscription_data.metadata
        )
        
        return SubscriptionResponse(
            subscription_id=subscription.subscription_id,
            subscriber_service=subscription.subscriber_service,
            event_types=subscription.event_types,
            source_services=[s.value for s in subscription.source_services] if subscription.source_services else None,
            last_processed_sequence=subscription.last_processed_sequence,
            last_processed_at=subscription.last_processed_at.isoformat() if subscription.last_processed_at else None,
            metadata=subscription.metadata
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
