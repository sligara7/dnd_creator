"""Storage service for audit events."""
from datetime import datetime
from typing import Dict, List, Optional

from audit_service.core.exceptions import StorageError
from audit_service.models.events import Event

class StorageService:
    """Service for managing audit event storage."""

    def __init__(self) -> None:
        """Initialize storage service."""
        self._events: Dict[str, Event] = {}

    async def setup(self) -> None:
        """Set up storage service."""
        # No setup needed for in-memory storage
        pass

    async def cleanup(self) -> None:
        """Clean up storage service."""
        # Clear in-memory storage
        self._events.clear()

    async def save_event(self, event: Event) -> None:
        """Save an audit event.
        
        Args:
            event: Event to save
        """
        if not event.id:
            raise StorageError("Event ID is required")
        self._events[event.id] = event

    async def get_event(self, event_id: str) -> Event:
        """Get an event by ID.
        
        Args:
            event_id: Event ID
            
        Returns:
            Event if found
            
        Raises:
            StorageError: If event not found
        """
        if not event_id:
            raise StorageError("Invalid event ID")

        event = self._events.get(event_id)
        if not event:
            raise StorageError("Event not found")
        
        return event

    async def get_events(self, search_params: Dict[str, str]) -> List[Event]:
        """Get events matching search parameters.
        
        Args:
            search_params: Search criteria
            
        Returns:
            List of matching events
        """
        events = []
        for event in self._events.values():
            # Match source and event type if provided
            if search_params.get('source') and event.source != search_params['source']:
                continue
            if search_params.get('event_type') and event.event_type != search_params['event_type']:
                continue
            events.append(event)
        return events

    async def delete_event(self, event_id: str) -> None:
        """Delete an event.
        
        Args:
            event_id: Event ID
            
        Raises:
            StorageError: If event not found
        """
        if not event_id:
            raise StorageError("Invalid event ID")

        if event_id not in self._events:
            raise StorageError("Event not found")
        
        del self._events[event_id]