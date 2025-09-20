"""Game Session Service - Storage Message Handlers.

This module implements handlers for storage-related message operations.
"""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from structlog import get_logger

from game_session.core.message_hub import MessageHubClient

logger = get_logger(__name__)


class StorageOperations:
    """Storage operation handlers via Message Hub."""

    def __init__(self, message_hub: MessageHubClient):
        """Initialize storage operations.

        Args:
            message_hub: Message Hub client instance.
        """
        self.message_hub = message_hub

    async def save_session_state(
        self,
        session_id: UUID,
        state: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Save session state to storage service.

        Args:
            session_id: Session ID.
            state: State to save.
            metadata: Optional metadata about the state.
        """
        await self.message_hub.publish_event(
            self.message_hub.events["storage"]["save_state"],
            {
                "session_id": str(session_id),
                "state": state,
                "metadata": metadata or {},
                "timestamp": str(datetime.utcnow()),
            }
        )

    async def load_session_state(
        self,
        session_id: UUID,
    ) -> None:
        """Request session state from storage service.

        Args:
            session_id: Session ID.

        Note:
            Response will come through state.session.loaded subscription.
        """
        await self.message_hub.publish_event(
            self.message_hub.events["storage"]["load_state"],
            {
                "session_id": str(session_id),
                "timestamp": str(datetime.utcnow()),
            }
        )

    async def save_session_event(
        self,
        session_id: UUID,
        event_type: str,
        event_data: Dict[str, Any],
    ) -> None:
        """Save session event to storage service.

        Args:
            session_id: Session ID.
            event_type: Type of event.
            event_data: Event data to save.
        """
        await self.message_hub.publish_event(
            self.message_hub.events["storage"]["save_event"],
            {
                "session_id": str(session_id),
                "event_type": event_type,
                "event_data": event_data,
                "timestamp": str(datetime.utcnow()),
            }
        )


class SessionState:
    """Session state container with versioning."""

    def __init__(self):
        """Initialize session state."""
        self.state: Dict[str, Any] = {}
        self.version: str = "0"
        self.last_updated: Optional[datetime] = None

    def update(
        self,
        new_state: Dict[str, Any],
        version: Optional[str] = None,
    ) -> None:
        """Update session state.

        Args:
            new_state: New state to merge.
            version: Optional new version.
        """
        self.state.update(new_state)
        if version:
            self.version = version
        self.last_updated = datetime.utcnow()