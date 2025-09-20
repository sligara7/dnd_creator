"""
Tests for Storage client.
"""
from datetime import datetime, timedelta, timezone
from typing import List
import pytest
from httpx import AsyncClient

from audit_service.core.storage import StorageClient
from audit_service.core.exceptions import StorageError
from audit_service.models.events import Event

@pytest.mark.asyncio
async def test_storage_client_lifecycle():
    """Test Storage client lifecycle."""
    client = StorageClient()
    await client.setup()
    await client.cleanup()

@pytest.mark.asyncio
async def test_store_event(event: Event):
    """Test storing a single event."""
    client = StorageClient()
    await client.setup()
    try:
        event_id = await client.store_event(event)
        assert isinstance(event_id, str)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_store_events(event_batch: List[Event]):
    """Test storing multiple events."""
    client = StorageClient()
    await client.setup()
    try:
        event_ids = await client.store_events(event_batch)
        assert len(event_ids) == len(event_batch)
        assert all(isinstance(id, str) for id in event_ids)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_get_events(event: Event, event_search_params: Dict[str, str]):
    """Test retrieving events."""
    client = StorageClient()
    await client.setup()
    try:
        # Store an event first
        await client.store_event(event)
        
        # Retrieve events
        events = await client.get_events(
            start_date=datetime.fromisoformat(event_search_params["start_date"]),
            end_date=datetime.fromisoformat(event_search_params["end_date"]),
            event_types=event_search_params["event_types"],
            services=[event_search_params["services"]],
            severity=event_search_params["severity"]
        )
        
        assert len(events) == 1
        assert events[0].service == event.service
        assert events[0].type == event.type
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_archive_events(event_batch: List[Event]):
    """Test archiving events."""
    client = StorageClient()
    await client.setup()
    try:
        await client.archive_events(
            events=event_batch,
            archive_id="test_archive"
        )
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_delete_events(event_batch: List[Event]):
    """Test deleting events."""
    client = StorageClient()
    await client.setup()
    try:
        # Store events first
        event_ids = await client.store_events(event_batch)
        
        # Delete the events
        await client.delete_events(event_ids)
        
        # Verify they're gone
        events = await client.get_events(
            start_date=datetime.now(timezone.utc) - timedelta(hours=1),
            end_date=datetime.now(timezone.utc),
            event_types=[event_batch[0].type],
            services=[event_batch[0].service]
        )
        assert len(events) == 0
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_get_storage_stats():
    """Test getting storage statistics."""
    client = StorageClient()
    await client.setup()
    try:
        stats = await client.get_storage_stats()
        assert isinstance(stats, dict)
        assert "total_size_bytes" in stats
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_store_event_no_connection(event: Event):
    """Test storing without connection."""
    client = StorageClient()
    # Don't set up client
    with pytest.raises(StorageError) as exc_info:
        await client.store_event(event)
    assert "Failed to store event" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_events_invalid_dates():
    """Test retrieving with invalid date range."""
    client = StorageClient()
    await client.setup()
    try:
        end_date = datetime.now(timezone.utc)
        start_date = end_date + timedelta(days=1)  # Start after end
        
        with pytest.raises(StorageError) as exc_info:
            await client.get_events(
                start_date=start_date,
                end_date=end_date
            )
        assert "Failed to retrieve events" in str(exc_info.value)
    finally:
        await client.cleanup()

@pytest.mark.asyncio
async def test_archive_events_invalid_id(event_batch: List[Event]):
    """Test archiving with invalid archive ID."""
    client = StorageClient()
    await client.setup()
    try:
        with pytest.raises(StorageError) as exc_info:
            await client.archive_events(
                events=event_batch,
                archive_id=""  # Invalid empty ID
            )
        assert "Failed to archive events" in str(exc_info.value)
    finally:
        await client.cleanup()