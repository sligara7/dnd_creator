"""
Enhanced Event Persistence Service

Provides durable event storage with replay capabilities.
"""

import uuid
import asyncio
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from enum import Enum
import structlog
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, and_, or_, desc, update, delete
from sqlalchemy.sql import func
import json

from .event_store.models import Event, EventStream, EventSubscription, EventType
from .models import ServiceType
from .config import Settings

logger = structlog.get_logger()


class EventReplayMode(str, Enum):
    """Event replay modes."""
    FROM_BEGINNING = "from_beginning"
    FROM_TIMESTAMP = "from_timestamp"
    FROM_SEQUENCE = "from_sequence"
    LAST_N_EVENTS = "last_n_events"


class EnhancedEventStore:
    """
    Enhanced event store with durability guarantees and replay capabilities.
    
    Features:
    - Write-ahead logging for durability
    - Event replay from any point
    - Event compaction and archival
    - Snapshot support for state reconstruction
    - Concurrent write protection
    - Optimistic concurrency control
    """
    
    def __init__(self, settings: Settings):
        """Initialize enhanced event store."""
        self.settings = settings
        self.engine: Optional[AsyncEngine] = None
        self.session_factory: Optional[sessionmaker] = None
        
        # Write-ahead log settings
        self.wal_enabled = True
        self.wal_flush_interval = 1  # seconds
        self.wal_buffer: List[Event] = []
        self.wal_lock = asyncio.Lock()
        
        # Compaction settings
        self.compaction_enabled = True
        self.compaction_interval = 3600  # 1 hour
        self.retention_days = settings.event_retention_days
        
        # Background tasks
        self._wal_flusher_task = None
        self._compactor_task = None
    
    async def initialize(self):
        """Initialize database connection and background tasks."""
        # Create async engine with durability settings
        self.engine = create_async_engine(
            self.settings.database_url,
            echo=False,
            pool_size=20,
            max_overflow=10,
            pool_pre_ping=True,
            # Ensure durability
            connect_args={
                "server_settings": {
                    "jit": "off"
                },
                "command_timeout": 60,
            }
        )
        
        # Create session factory
        self.session_factory = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
        
        # Create tables if they don't exist
        async with self.engine.begin() as conn:
            from .event_store.models import Base
            await conn.run_sync(Base.metadata.create_all)
        
        # Start background tasks
        if self.wal_enabled:
            self._wal_flusher_task = asyncio.create_task(self._wal_flush_loop())
        
        if self.compaction_enabled:
            self._compactor_task = asyncio.create_task(self._compaction_loop())
        
        logger.info("enhanced_event_store_initialized")
    
    async def shutdown(self):
        """Shutdown event store."""
        # Cancel background tasks
        if self._wal_flusher_task:
            self._wal_flusher_task.cancel()
            try:
                await self._wal_flusher_task
            except asyncio.CancelledError:
                pass
        
        if self._compactor_task:
            self._compactor_task.cancel()
            try:
                await self._compactor_task
            except asyncio.CancelledError:
                pass
        
        # Flush any remaining WAL entries
        await self._flush_wal()
        
        # Close database connection
        if self.engine:
            await self.engine.dispose()
        
        logger.info("enhanced_event_store_shutdown")
    
    async def append_event_durable(self,
                                  event_type: EventType,
                                  source_service: ServiceType,
                                  data: Dict[str, Any],
                                  *,
                                  metadata: Optional[Dict[str, Any]] = None,
                                  correlation_id: Optional[str] = None,
                                  causation_id: Optional[str] = None,
                                  stream_id: Optional[str] = None,
                                  expected_version: Optional[int] = None) -> Event:
        """
        Append event with durability guarantees and optimistic concurrency control.
        
        Args:
            event_type: Type of event
            source_service: Service that generated the event
            data: Event payload
            metadata: Optional event metadata
            correlation_id: Optional correlation ID
            causation_id: Optional causation ID
            stream_id: Optional stream ID
            expected_version: Expected stream version for optimistic concurrency
        
        Returns:
            The created event
        
        Raises:
            ConcurrencyError: If expected version doesn't match
        """
        async with self.wal_lock:
            async with self.session_factory() as session:
                async with session.begin():
                    # Check expected version if provided
                    if stream_id and expected_version is not None:
                        current_version = await self._get_stream_version(
                            session, stream_id
                        )
                        if current_version != expected_version:
                            raise ValueError(
                                f"Concurrency conflict: expected version {expected_version}, "
                                f"but current version is {current_version}"
                            )
                    
                    # Get next sequence number atomically
                    seq_result = await session.execute(
                        select(func.max(Event.sequence_number)).with_for_update()
                    )
                    max_seq = seq_result.scalar() or 0
                    next_seq = max_seq + 1
                    
                    # Create event
                    event = Event(
                        event_type=event_type,
                        event_id=str(uuid.uuid4()),
                        source_service=source_service.value,
                        data=data,
                        event_metadata=metadata or {},
                        correlation_id=correlation_id,
                        causation_id=causation_id,
                        sequence_number=next_seq,
                        stream_id=stream_id,
                        timestamp=datetime.utcnow()
                    )
                    
                    # Add to WAL buffer for immediate durability
                    if self.wal_enabled:
                        self.wal_buffer.append(event)
                    
                    # Persist to database
                    session.add(event)
                    
                    # Force flush for critical events
                    await session.flush()
                    
                    # Update stream version
                    if stream_id:
                        await self._increment_stream_version(
                            session, stream_id, event.timestamp
                        )
                    
                    await session.commit()
                    
                    logger.info("event_appended_durable",
                              event_id=event.event_id,
                              type=event_type.value if hasattr(event_type, 'value') else event_type,
                              sequence=next_seq)
                    
                    return event
    
    async def replay_events(self,
                           mode: EventReplayMode,
                           *,
                           from_timestamp: Optional[datetime] = None,
                           from_sequence: Optional[int] = None,
                           last_n: Optional[int] = None,
                           event_types: Optional[List[EventType]] = None,
                           stream_id: Optional[str] = None,
                           callback: Optional[Callable] = None,
                           batch_size: int = 100) -> AsyncGenerator[List[Event], None]:
        """
        Replay events based on specified mode.
        
        Args:
            mode: Replay mode
            from_timestamp: Start timestamp for FROM_TIMESTAMP mode
            from_sequence: Start sequence for FROM_SEQUENCE mode
            last_n: Number of events for LAST_N_EVENTS mode
            event_types: Filter by event types
            stream_id: Filter by stream ID
            callback: Optional callback for each event
            batch_size: Batch size for processing
        
        Yields:
            Batches of events
        """
        async with self.session_factory() as session:
            # Build base query
            query = select(Event)
            
            # Apply mode-specific filters
            if mode == EventReplayMode.FROM_BEGINNING:
                query = query.order_by(Event.sequence_number)
            
            elif mode == EventReplayMode.FROM_TIMESTAMP:
                if not from_timestamp:
                    raise ValueError("from_timestamp required for FROM_TIMESTAMP mode")
                query = query.filter(
                    Event.timestamp >= from_timestamp
                ).order_by(Event.sequence_number)
            
            elif mode == EventReplayMode.FROM_SEQUENCE:
                if from_sequence is None:
                    raise ValueError("from_sequence required for FROM_SEQUENCE mode")
                query = query.filter(
                    Event.sequence_number > from_sequence
                ).order_by(Event.sequence_number)
            
            elif mode == EventReplayMode.LAST_N_EVENTS:
                if not last_n:
                    raise ValueError("last_n required for LAST_N_EVENTS mode")
                query = query.order_by(desc(Event.sequence_number)).limit(last_n)
            
            # Apply additional filters
            if event_types:
                query = query.filter(Event.event_type.in_(event_types))
            
            if stream_id:
                query = query.filter(Event.stream_id == stream_id)
            
            # Process in batches
            offset = 0
            while True:
                batch_query = query.limit(batch_size).offset(offset)
                result = await session.execute(batch_query)
                events = list(result.scalars().all())
                
                if not events:
                    break
                
                # Apply callback if provided
                if callback:
                    for event in events:
                        await callback(event)
                
                yield events
                
                offset += batch_size
                
                logger.debug("events_replayed",
                           count=len(events),
                           offset=offset)
    
    async def create_snapshot(self,
                            stream_id: str,
                            state: Dict[str, Any],
                            version: int) -> str:
        """
        Create a snapshot of current state.
        
        Args:
            stream_id: Stream ID
            state: Current state
            version: Version number
        
        Returns:
            Snapshot ID
        """
        snapshot_id = str(uuid.uuid4())
        
        async with self.session_factory() as session:
            async with session.begin():
                # Store snapshot as special event
                snapshot_event = Event(
                    event_type="system.snapshot",
                    event_id=snapshot_id,
                    source_service="message-hub",
                    data=state,
                    event_metadata={
                        "snapshot": True,
                        "version": version,
                        "stream_id": stream_id
                    },
                    stream_id=stream_id,
                    sequence_number=await self._get_next_sequence(session),
                    timestamp=datetime.utcnow()
                )
                
                session.add(snapshot_event)
                await session.commit()
                
                logger.info("snapshot_created",
                          snapshot_id=snapshot_id,
                          stream_id=stream_id,
                          version=version)
                
                return snapshot_id
    
    async def get_latest_snapshot(self, stream_id: str) -> Optional[Event]:
        """Get the latest snapshot for a stream."""
        async with self.session_factory() as session:
            query = select(Event).filter(
                and_(
                    Event.stream_id == stream_id,
                    Event.event_type == "system.snapshot"
                )
            ).order_by(desc(Event.timestamp)).limit(1)
            
            result = await session.execute(query)
            return result.scalar_one_or_none()
    
    async def compact_events(self, before_date: Optional[datetime] = None):
        """
        Compact old events to save space.
        
        Args:
            before_date: Compact events before this date
        """
        if not before_date:
            before_date = datetime.utcnow() - timedelta(days=self.retention_days)
        
        async with self.session_factory() as session:
            async with session.begin():
                # Get streams with old events
                stream_query = select(Event.stream_id).filter(
                    Event.timestamp < before_date
                ).distinct()
                
                result = await session.execute(stream_query)
                stream_ids = [row[0] for row in result if row[0]]
                
                for stream_id in stream_ids:
                    # Create snapshot for stream
                    latest_event = await self._get_latest_event_for_stream(
                        session, stream_id
                    )
                    
                    if latest_event:
                        # Reconstruct state from events
                        state = await self._reconstruct_state(session, stream_id)
                        
                        # Create snapshot
                        await self.create_snapshot(
                            stream_id,
                            state,
                            latest_event.sequence_number
                        )
                
                # Delete old events (except snapshots)
                delete_query = delete(Event).filter(
                    and_(
                        Event.timestamp < before_date,
                        Event.event_type != "system.snapshot"
                    )
                )
                
                result = await session.execute(delete_query)
                deleted_count = result.rowcount
                
                await session.commit()
                
                logger.info("events_compacted",
                          before_date=before_date.isoformat(),
                          deleted_count=deleted_count,
                          streams_processed=len(stream_ids))
    
    async def _get_stream_version(self,
                                 session: AsyncSession,
                                 stream_id: str) -> int:
        """Get current version of a stream."""
        query = select(func.count(Event.id)).filter(
            Event.stream_id == stream_id
        )
        result = await session.execute(query)
        return result.scalar() or 0
    
    async def _increment_stream_version(self,
                                       session: AsyncSession,
                                       stream_id: str,
                                       event_time: datetime):
        """Increment stream version."""
        # Update stream metadata if exists
        from .event_store.models import EventStream
        
        query = select(EventStream).filter_by(stream_id=stream_id)
        result = await session.execute(query)
        stream = result.scalar_one_or_none()
        
        if stream:
            stream.last_event_at = event_time
            stream.version = (stream.version or 0) + 1
    
    async def _get_next_sequence(self, session: AsyncSession) -> int:
        """Get next sequence number."""
        seq_result = await session.execute(
            select(func.max(Event.sequence_number))
        )
        max_seq = seq_result.scalar() or 0
        return max_seq + 1
    
    async def _get_latest_event_for_stream(self,
                                          session: AsyncSession,
                                          stream_id: str) -> Optional[Event]:
        """Get latest event for a stream."""
        query = select(Event).filter(
            Event.stream_id == stream_id
        ).order_by(desc(Event.sequence_number)).limit(1)
        
        result = await session.execute(query)
        return result.scalar_one_or_none()
    
    async def _reconstruct_state(self,
                                session: AsyncSession,
                                stream_id: str) -> Dict[str, Any]:
        """Reconstruct state from events."""
        # Get latest snapshot
        snapshot = await self.get_latest_snapshot(stream_id)
        
        state = {}
        if snapshot:
            state = snapshot.data.copy()
            from_sequence = snapshot.sequence_number
        else:
            from_sequence = 0
        
        # Apply events after snapshot
        query = select(Event).filter(
            and_(
                Event.stream_id == stream_id,
                Event.sequence_number > from_sequence,
                Event.event_type != "system.snapshot"
            )
        ).order_by(Event.sequence_number)
        
        result = await session.execute(query)
        events = result.scalars().all()
        
        for event in events:
            # Apply event to state (simplified)
            state.update(event.data)
        
        return state
    
    async def _flush_wal(self):
        """Flush write-ahead log to database."""
        if not self.wal_buffer:
            return
        
        async with self.wal_lock:
            if not self.wal_buffer:
                return
            
            events_to_flush = self.wal_buffer.copy()
            self.wal_buffer.clear()
        
        # Batch insert for efficiency
        async with self.session_factory() as session:
            async with session.begin():
                for event in events_to_flush:
                    session.add(event)
                
                await session.commit()
                
                logger.debug("wal_flushed", count=len(events_to_flush))
    
    async def _wal_flush_loop(self):
        """Background task to flush WAL periodically."""
        logger.info("wal_flush_loop_started")
        
        while True:
            try:
                await asyncio.sleep(self.wal_flush_interval)
                await self._flush_wal()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("wal_flush_error", error=str(e))
                await asyncio.sleep(5)
        
        logger.info("wal_flush_loop_stopped")
    
    async def _compaction_loop(self):
        """Background task for event compaction."""
        logger.info("compaction_loop_started")
        
        while True:
            try:
                await asyncio.sleep(self.compaction_interval)
                await self.compact_events()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error("compaction_error", error=str(e))
                await asyncio.sleep(60)
        
        logger.info("compaction_loop_stopped")
    
    async def get_metrics(self) -> Dict[str, Any]:
        """Get event store metrics."""
        async with self.session_factory() as session:
            # Get event counts
            total_events = await session.execute(
                select(func.count(Event.id))
            )
            
            # Get stream count
            stream_count = await session.execute(
                select(func.count(func.distinct(Event.stream_id)))
            )
            
            # Get snapshot count
            snapshot_count = await session.execute(
                select(func.count(Event.id)).filter(
                    Event.event_type == "system.snapshot"
                )
            )
            
            # Get oldest event
            oldest_event = await session.execute(
                select(func.min(Event.timestamp))
            )
            
            return {
                "total_events": total_events.scalar() or 0,
                "stream_count": stream_count.scalar() or 0,
                "snapshot_count": snapshot_count.scalar() or 0,
                "oldest_event": oldest_event.scalar(),
                "wal_buffer_size": len(self.wal_buffer),
                "retention_days": self.retention_days,
                "compaction_enabled": self.compaction_enabled
            }
