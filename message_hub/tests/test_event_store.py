"""
Event Store Service Tests
"""

import pytest
from datetime import datetime
from typing import AsyncGenerator, List
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from src.event_store.models import Event, EventStream, EventSubscription, EventType, Base
from src.event_store.service import EventStore
from src.models import ServiceType

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest.fixture
async def engine():
    """Create a test database engine."""
    engine = create_async_engine(TEST_DATABASE_URL, echo=True)
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield engine
    
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await engine.dispose()

@pytest.fixture
def session_factory(engine):
    """Create a test session factory."""
    return sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )

@pytest.fixture
async def event_store(session_factory) -> EventStore:
    """Create a test event store instance."""
    store = EventStore(session_factory)
    await store.initialize_database()
    return store

@pytest.mark.asyncio
async def test_append_event(event_store: EventStore):
    """Test appending a single event."""
    event = await event_store.append_event(
        event_type=EventType.CHARACTER_CREATED,
        source_service=ServiceType.CHARACTER_SERVICE,
        data={"character_id": "test-123"},
        metadata={"version": "1.0"}
    )
    
    assert event.event_id is not None
    assert isinstance(UUID(event.event_id), UUID)
    assert event.event_type == EventType.CHARACTER_CREATED
    assert event.source_service == ServiceType.CHARACTER_SERVICE.value
    assert event.data == {"character_id": "test-123"}
    assert event.metadata == {"version": "1.0"}
    assert event.sequence_number == 1

@pytest.mark.asyncio
async def test_get_events(event_store: EventStore):
    """Test retrieving events with filters."""
    # Create test events
    events = []
    for i in range(5):
        event = await event_store.append_event(
            event_type=EventType.CHARACTER_CREATED,
            source_service=ServiceType.CHARACTER_SERVICE,
            data={"character_id": f"test-{i}"}
        )
        events.append(event)
    
    # Test filtering by event type
    filtered = await event_store.get_events(
        event_types=[EventType.CHARACTER_CREATED]
    )
    assert len(filtered) == 5
    
    # Test filtering by sequence
    filtered = await event_store.get_events(after_sequence=2)
    assert len(filtered) == 3
    assert all(e.sequence_number > 2 for e in filtered)
    
    # Test limit
    filtered = await event_store.get_events(limit=2)
    assert len(filtered) == 2

@pytest.mark.asyncio
async def test_create_stream(event_store: EventStore):
    """Test creating an event stream."""
    stream = await event_store.create_stream(
        stream_type="test",
        metadata={"version": "1.0"}
    )
    
    assert stream.stream_id is not None
    assert isinstance(UUID(stream.stream_id), UUID)
    assert stream.stream_type == "test"
    assert stream.metadata == {"version": "1.0"}
    assert stream.created_at is not None
    assert stream.last_event_at is None

@pytest.mark.asyncio
async def test_create_subscription(event_store: EventStore):
    """Test creating an event subscription."""
    subscription = await event_store.create_subscription(
        subscriber_service=ServiceType.CHARACTER_SERVICE,
        event_types=[EventType.CHARACTER_CREATED],
        source_services=[ServiceType.CHARACTER_SERVICE]
    )
    
    assert subscription.subscription_id is not None
    assert isinstance(UUID(subscription.subscription_id), UUID)
    assert subscription.subscriber_service == ServiceType.CHARACTER_SERVICE.value
    assert subscription.event_types == [EventType.CHARACTER_CREATED.value]
    assert subscription.source_services == [ServiceType.CHARACTER_SERVICE.value]
    assert subscription.last_processed_sequence == 0
    assert subscription.last_processed_at is None

@pytest.mark.asyncio
async def test_get_subscription_events(event_store: EventStore):
    """Test retrieving events for a subscription."""
    # Create subscription
    subscription = await event_store.create_subscription(
        subscriber_service=ServiceType.CHARACTER_SERVICE,
        event_types=[EventType.CHARACTER_CREATED]
    )
    
    # Create test events
    events = []
    for i in range(5):
        event = await event_store.append_event(
            event_type=EventType.CHARACTER_CREATED,
            source_service=ServiceType.CHARACTER_SERVICE,
            data={"character_id": f"test-{i}"}
        )
        events.append(event)
    
    # Get events in batches
    all_events = []
    async for batch in event_store.get_subscription_events(
        subscription.subscription_id,
        batch_size=2
    ):
        all_events.extend(batch)
    
    assert len(all_events) == 5
    assert all(isinstance(e, Event) for e in all_events)
    
    # Verify subscription was updated
    async with event_store.session_factory() as session:
        result = await session.execute(
            f"SELECT last_processed_sequence FROM event_subscription WHERE subscription_id = '{subscription.subscription_id}'"
        )
        last_seq = result.scalar()
        assert last_seq == 5
