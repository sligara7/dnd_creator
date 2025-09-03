"""Event handling system for campaign service."""
from enum import Enum
from typing import Dict, List, Optional, Type
from uuid import UUID

from pydantic import BaseModel

from ...core.logging import get_logger
from .client import MessageHubClient

logger = get_logger(__name__)


class EventType(str, Enum):
    """Event types for campaign service."""
    # Campaign events
    CAMPAIGN_CREATED = "campaign.created"
    CAMPAIGN_UPDATED = "campaign.updated"
    CAMPAIGN_DELETED = "campaign.deleted"
    CAMPAIGN_ARCHIVED = "campaign.archived"
    CAMPAIGN_GENERATED = "campaign.generated"

    # Chapter events
    CHAPTER_CREATED = "campaign.chapter.created"
    CHAPTER_UPDATED = "campaign.chapter.updated"
    CHAPTER_DELETED = "campaign.chapter.deleted"
    CHAPTER_COMPLETED = "campaign.chapter.completed"
    CHAPTER_CONTENT_ADDED = "campaign.chapter.content.added"
    CHAPTER_CONTENT_UPDATED = "campaign.chapter.content.updated"
    CHAPTER_CONTENT_REMOVED = "campaign.chapter.content.removed"

    # Version control events
    VERSION_CREATED = "campaign.version.created"
    BRANCH_CREATED = "campaign.version.branch.created"
    MERGE_REQUEST_CREATED = "campaign.version.merge.created"
    MERGE_REQUEST_UPDATED = "campaign.version.merge.updated"
    MERGE_REQUEST_CLOSED = "campaign.version.merge.closed"
    MERGE_REQUEST_MERGED = "campaign.version.merge.merged"
    CONFLICT_DETECTED = "campaign.version.conflict.detected"
    CONFLICT_RESOLVED = "campaign.version.conflict.resolved"

    # Theme events
    THEME_APPLIED = "campaign.theme.applied"
    THEME_UPDATED = "campaign.theme.updated"
    THEME_VALIDATED = "campaign.theme.validated"
    THEME_VALIDATION_FAILED = "campaign.theme.validation.failed"


class BaseEvent(BaseModel):
    """Base event model."""
    event_type: EventType
    campaign_id: UUID
    correlation_id: Optional[str] = None
    metadata: Optional[Dict] = None


class CampaignEvent(BaseEvent):
    """Campaign-related event model."""
    name: str
    status: str
    theme: Optional[Dict] = None
    version: Optional[str] = None


class ChapterEvent(BaseEvent):
    """Chapter-related event model."""
    chapter_id: UUID
    title: str
    status: str
    sequence: int
    type: str


class VersionEvent(BaseEvent):
    """Version control-related event model."""
    version_hash: str
    branch: str
    type: str
    author: str
    message: str


class ThemeEvent(BaseEvent):
    """Theme-related event model."""
    theme_id: UUID
    primary_theme: str
    secondary_theme: Optional[str] = None
    validation_result: Optional[Dict] = None


class EventHandler:
    """Event handler for message hub events."""

    def __init__(self, message_hub: MessageHubClient):
        """Initialize with required dependencies."""
        self.message_hub = message_hub
        self._handlers = {}

    async def initialize(self):
        """Initialize event handling."""
        # Subscribe to campaign events
        await self.message_hub.subscribe(
            "campaign_events",
            self._handle_campaign_event,
            "campaign.#"
        )

        # Subscribe to chapter events
        await self.message_hub.subscribe(
            "chapter_events",
            self._handle_chapter_event,
            "campaign.chapter.#"
        )

        # Subscribe to version events
        await self.message_hub.subscribe(
            "version_events",
            self._handle_version_event,
            "campaign.version.#"
        )

        # Subscribe to theme events
        await self.message_hub.subscribe(
            "theme_events",
            self._handle_theme_event,
            "campaign.theme.#"
        )

    def register_handler(
        self,
        event_type: EventType,
        handler: callable,
        event_class: Type[BaseEvent] = BaseEvent
    ):
        """Register an event handler."""
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append((handler, event_class))

    async def _handle_campaign_event(self, event_data: Dict):
        """Handle campaign events."""
        try:
            event_type = EventType(event_data["event_type"])
            handlers = self._handlers.get(event_type, [])

            for handler, event_class in handlers:
                event = event_class(**event_data)
                await handler(event)

        except Exception as e:
            logger.error(
                "Failed to handle campaign event",
                error=str(e),
                event_data=event_data
            )

    async def _handle_chapter_event(self, event_data: Dict):
        """Handle chapter events."""
        try:
            event_type = EventType(event_data["event_type"])
            handlers = self._handlers.get(event_type, [])

            for handler, event_class in handlers:
                event = event_class(**event_data)
                await handler(event)

        except Exception as e:
            logger.error(
                "Failed to handle chapter event",
                error=str(e),
                event_data=event_data
            )

    async def _handle_version_event(self, event_data: Dict):
        """Handle version control events."""
        try:
            event_type = EventType(event_data["event_type"])
            handlers = self._handlers.get(event_type, [])

            for handler, event_class in handlers:
                event = event_class(**event_data)
                await handler(event)

        except Exception as e:
            logger.error(
                "Failed to handle version event",
                error=str(e),
                event_data=event_data
            )

    async def _handle_theme_event(self, event_data: Dict):
        """Handle theme events."""
        try:
            event_type = EventType(event_data["event_type"])
            handlers = self._handlers.get(event_type, [])

            for handler, event_class in handlers:
                event = event_class(**event_data)
                await handler(event)

        except Exception as e:
            logger.error(
                "Failed to handle theme event",
                error=str(e),
                event_data=event_data
            )
