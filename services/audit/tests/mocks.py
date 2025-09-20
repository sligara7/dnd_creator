"""
Test mocks for external services.
"""
from typing import Any, Dict, List, Optional
from datetime import datetime

from audit_service.models.events import Event
from audit_service.core.exceptions import EventRoutingError, StorageError

class MockMessageHubClient:
    """Mock Message Hub client for testing."""
    
    def __init__(self) -> None:
        self.published_events: List[Event] = []
        self.connected = False
    
    async def setup(self) -> None:
        """Set up the mock client."""
        self.connected = True
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.connected = False
        self.published_events = []
    
    async def publish_event(self, event: Event) -> None:
        """Mock publishing a single event."""
        if not self.connected:
            raise EventRoutingError(
                message="No Message Hub connection available",
                source="audit_service",
                event_type="connection",
                details={"error": "Not connected"}
            )
        self.published_events.append(event)
    
    async def publish_events(self, events: List[Event]) -> None:
        """Mock publishing multiple events."""
        if not self.connected:
            raise EventRoutingError(
                message="No Message Hub connection available",
                source="audit_service",
                event_type="connection",
                details={"error": "Not connected"}
            )
        self.published_events.extend(events)

class MockStorageClient:
    """Mock Storage Service client for testing."""
    
    def __init__(self) -> None:
        self.stored_events: Dict[str, Event] = {}
        self.connected = False
    
    async def setup(self) -> None:
        """Set up the mock client."""
        self.connected = True
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        self.connected = False
        self.stored_events = {}
    
    async def store_event(self, event: Event) -> str:
        """Mock storing a single event."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="store",
                details={"error": "Not connected"}
            )
        self.stored_events[str(event.id)] = event
        return str(event.id)
    
    async def store_events(self, events: List[Event]) -> List[str]:
        """Mock storing multiple events."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="store_batch",
                details={"error": "Not connected"}
            )
        event_ids = []
        for event in events:
            event_ids.append(await self.store_event(event))
        return event_ids
    
    async def get_events(
        self,
        start_date: datetime,
        end_date: datetime,
        event_types: Optional[List[str]] = None,
        services: Optional[List[str]] = None,
        severity: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Event]:
        """Mock retrieving events."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="retrieve",
                details={"error": "Not connected"}
            )
            
        filtered_events = []
        for event in self.stored_events.values():
            if start_date <= event.timestamp <= end_date:
                if event_types and event.type not in event_types:
                    continue
                if services and event.service not in services:
                    continue
                if severity and event.severity != severity:
                    continue
                filtered_events.append(event)
        
        return filtered_events[offset:offset + limit]
    
    async def archive_events(self, events: List[Event], archive_id: str) -> None:
        """Mock archiving events."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="archive",
                details={"error": "Not connected"}
            )
        # Just mark them as archived
        for event in events:
            event.data.metadata["archived"] = True
            event.data.metadata["archive_id"] = archive_id
    
    async def delete_events(self, event_ids: List[str]) -> None:
        """Mock deleting events."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="delete",
                details={"error": "Not connected"}
            )
        for event_id in event_ids:
            self.stored_events.pop(event_id, None)
    
    async def get_storage_stats(self) -> Dict[str, Any]:
        """Mock getting storage statistics."""
        if not self.connected:
            raise StorageError(
                backend="storage_service",
                message="Failed to connect",
                operation="stats",
                details={"error": "Not connected"}
            )
        return {
            "total_size_bytes": len(self.stored_events) * 1024,  # Mock size
            "event_count": len(self.stored_events),
            "oldest_event": min((e.timestamp for e in self.stored_events.values()), default=None),
            "newest_event": max((e.timestamp for e in self.stored_events.values()), default=None)
        }