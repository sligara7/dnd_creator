"""
Event Store Service

Handles event persistence, retrieval, and subscription management.
"""

import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
import structlog
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, desc
from sqlalchemy.orm import selectinload
from sqlalchemy.sql import func

from .models import Event, EventStream, EventSubscription, EventType, Base
from ..models import ServiceType

logger = structlog.get_logger()

class EventStore:
    """
    Event store service for event sourcing and event-driven architecture.
    
    Responsibilities:
    - Event persistence
    - Event retrieval
    - Stream management
    - Subscription handling
    """
    
    def __init__(self, session_factory):
        """Initialize event store with database session factory."""
        self.session_factory = session_factory
    
    async def append_event(self,
                        event_type: EventType,
                        source_service: ServiceType,
                        data: Dict[str, Any],
                        *,
                        metadata: Optional[Dict[str, Any]] = None,
                        correlation_id: Optional[str] = None,
                        causation_id: Optional[str] = None,
                        stream_id: Optional[str] = None) -> Event:
        """
        Append a new event to the store.
        
        Args:
            event_type: Type of event
            source_service: Service that generated the event
            data: Event payload
            metadata: Optional event metadata
            correlation_id: Optional ID for distributed tracing
            causation_id: Optional ID of event that caused this event
            stream_id: Optional stream to append to
        
        Returns:
            The created event
        """
        async with self.session_factory() as session:
            async with session.begin():
                # Get next sequence number
                seq_result = await session.execute(
                    select(func.max(Event.sequence_number))
                )
                max_seq = seq_result.scalar() or 0
                next_seq = max_seq + 1
                
                # Create event
                event = Event(
                    event_type=event_type,
                    event_id=str(uuid.uuid4()),
                    source_service=source_service.value,
                    data=data,
                    metadata=metadata,
                    correlation_id=correlation_id,
                    causation_id=causation_id,
                    sequence_number=next_seq,
                    stream_id=stream_id
                )
                
                session.add(event)
                
                # Update stream if provided
                if stream_id:
                    await self._update_stream(
                        session, stream_id, event.timestamp
                    )
                
                await session.commit()
                
                logger.info("event_appended",
                          event_id=event.event_id,
                          type=event_type,
                          source=source_service.value,
                          sequence=next_seq)
                
                return event
    
    async def get_events(self,
                       *,
                       after_sequence: Optional[int] = None,
                       event_types: Optional[List[EventType]] = None,
                       source_services: Optional[List[ServiceType]] = None,
                       stream_id: Optional[str] = None,
                       limit: int = 100) -> List[Event]:
        """
        Get events matching specified criteria.
        
        Args:
            after_sequence: Only get events after this sequence number
            event_types: Filter by event types
            source_services: Filter by source services
            stream_id: Filter by stream ID
            limit: Maximum number of events to return
        
        Returns:
            List of matching events
        """
        async with self.session_factory() as session:
            query = select(Event).order_by(Event.sequence_number)
            
            # Apply filters
            if after_sequence is not None:
                query = query.filter(Event.sequence_number > after_sequence)
            
            if event_types:
                query = query.filter(Event.event_type.in_(event_types))
            
            if source_services:
                query = query.filter(
                    Event.source_service.in_([s.value for s in source_services])
                )
            
            if stream_id:
                query = query.filter(Event.stream_id == stream_id)
            
            # Apply limit
            query = query.limit(limit)
            
            # Execute query
            result = await session.execute(query)
            return list(result.scalars().all())
    
    async def create_stream(self,
                         stream_type: str,
                         metadata: Optional[Dict[str, Any]] = None) -> EventStream:
        """Create a new event stream."""
        async with self.session_factory() as session:
            async with session.begin():
                stream = EventStream(
                    stream_id=str(uuid.uuid4()),
                    stream_type=stream_type,
                    metadata=metadata
                )
                
                session.add(stream)
                await session.commit()
                
                logger.info("stream_created",
                          stream_id=stream.stream_id,
                          type=stream_type)
                
                return stream
    
    async def create_subscription(self,
                               subscriber_service: ServiceType,
                               event_types: Optional[List[EventType]] = None,
                               source_services: Optional[List[ServiceType]] = None,
                               metadata: Optional[Dict[str, Any]] = None
                               ) -> EventSubscription:
        """Create a new event subscription."""
        async with self.session_factory() as session:
            async with session.begin():
                subscription = EventSubscription(
                    subscription_id=str(uuid.uuid4()),
                    subscriber_service=subscriber_service.value,
                    event_types=[e.value for e in (event_types or [])],
                    source_services=[s.value for s in (source_services or [])],
                    metadata=metadata
                )
                
                session.add(subscription)
                await session.commit()
                
                logger.info("subscription_created",
                          subscription_id=subscription.subscription_id,
                          subscriber=subscriber_service.value)
                
                return subscription
    
    async def get_subscription_events(self,
                                   subscription_id: str,
                                   batch_size: int = 100
                                   ) -> AsyncGenerator[List[Event], None]:
        """
        Get events for a subscription in batches.
        
        Yields batches of events that match the subscription's criteria
        and haven't been processed yet.
        """
        async with self.session_factory() as session:
            # Get subscription
            subscription = await self._get_subscription(session, subscription_id)
            if not subscription:
                raise ValueError(f"Unknown subscription: {subscription_id}")
            
            while True:
                # Get next batch of events
                events = await self.get_events(
                    after_sequence=subscription.last_processed_sequence,
                    event_types=[EventType(e) for e in subscription.event_types]
                    if subscription.event_types else None,
                    source_services=[ServiceType(s) for s in subscription.source_services]
                    if subscription.source_services else None,
                    limit=batch_size
                )
                
                if not events:
                    break
                
                yield events
                
                # Update subscription
                subscription.last_processed_sequence = events[-1].sequence_number
                subscription.last_processed_at = datetime.utcnow()
                await session.commit()
    
    async def _get_subscription(self,
                             session: AsyncSession,
                             subscription_id: str) -> Optional[EventSubscription]:
        """Get a subscription by ID."""
        result = await session.execute(
            select(EventSubscription).filter_by(subscription_id=subscription_id)
        )
        return result.scalar_one_or_none()
    
    async def _update_stream(self,
                          session: AsyncSession,
                          stream_id: str,
                          event_time: datetime):
        """Update stream's last event timestamp."""
        result = await session.execute(
            select(EventStream).filter_by(stream_id=stream_id)
        )
        stream = result.scalar_one_or_none()
        
        if stream:
            stream.last_event_at = event_time
    
    async def initialize_database(self):
        """Create database tables."""
        async with self.session_factory() as session:
            async with session.begin():
                await session.run_sync(Base.metadata.create_all)
                
                logger.info("event_store_initialized")
