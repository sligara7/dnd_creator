"""Message Hub integration and event handling."""
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

import httpx
import structlog

from llm_service.core.settings import Settings


class EventMetadata:
    """Metadata for events."""
    def __init__(self, event_type: str, source_service: str, correlation_id: Optional[str] = None) -> None:
        self.event_type = event_type
        self.source_service = source_service
        self.correlation_id = correlation_id or str(UUID())
        self.timestamp = datetime.utcnow().isoformat()


class Event:
    """Base event class."""
    def __init__(self, event_type: str, data: Dict[str, Any], source_service: str) -> None:
        self.metadata = EventMetadata(event_type, source_service)
        self.data = data

    def to_dict(self) -> Dict[str, Any]:
        """Convert event to dictionary."""
        return {
            "metadata": {
                "event_type": self.metadata.event_type,
                "source_service": self.metadata.source_service,
                "correlation_id": self.metadata.correlation_id,
                "timestamp": self.metadata.timestamp,
            },
            "data": self.data,
        }


class TextGeneratedEvent(Event):
    """Event for text generation completion."""
    def __init__(
        self,
        request_id: UUID,
        content_type: str,
        content_id: UUID,
        status: str,
        model_used: str,
        token_usage: Dict[str, int],
    ) -> None:
        super().__init__(
            event_type="text_generated",
            source_service="llm_service",
            data={
                "request_id": str(request_id),
                "content_type": content_type,
                "content_id": str(content_id),
                "status": status,
                "model_used": model_used,
                "token_usage": token_usage,
            },
        )


class ImageGeneratedEvent(Event):
    """Event for image generation completion."""
    def __init__(
        self,
        request_id: UUID,
        image_type: str,
        image_id: UUID,
        status: str,
        model_used: str,
        prompt: str,
        parameters: Dict[str, Any],
    ) -> None:
        super().__init__(
            event_type="image_generated",
            source_service="llm_service",
            data={
                "request_id": str(request_id),
                "image_type": image_type,
                "image_id": str(image_id),
                "status": status,
                "model_used": model_used,
                "prompt": prompt,
                "parameters": parameters,
            },
        )


class MessageHubClient:
    """Client for Message Hub service."""

    def __init__(self, settings: Settings, logger: Optional[structlog.BoundLogger] = None) -> None:
        self.settings = settings
        self.logger = logger or structlog.get_logger()

        # Create HTTP client
        self.client = httpx.AsyncClient(
            base_url=settings.message_hub.url,
            headers={
                "Authorization": f"Bearer {settings.message_hub.token.get_secret_value()}",
                "Content-Type": "application/json",
            },
            timeout=settings.message_hub.request_timeout,
        )

    async def close(self) -> None:
        """Close HTTP client."""
        await self.client.aclose()

    async def publish_text_generated(
        self,
        request_id: UUID,
        content_type: str,
        content_id: UUID,
        model: str,
        usage: Dict[str, int],
        status: str = "completed",
    ) -> None:
        """Helper for publishing text generation events."""
        event = TextGeneratedEvent(
            request_id=request_id,
            content_type=content_type,
            content_id=content_id,
            status=status,
            model_used=model,
            token_usage=usage,
        )
        await self.publish_event(event)

    async def publish_image_generated(
        self,
        request_id: UUID,
        image_type: str,
        image_id: UUID,
        model: str,
        prompt: str,
        parameters: Dict[str, Any],
        status: str = "completed",
    ) -> None:
        """Helper for publishing image generation events."""
        event = ImageGeneratedEvent(
            request_id=request_id,
            image_type=image_type,
            image_id=image_id,
            status=status,
            model_used=model,
            prompt=prompt,
            parameters=parameters,
        )
        await self.publish_event(event)

    async def publish_text_failed(
        self,
        request_id: UUID,
        content_type: str,
        error: str,
    ) -> None:
        """Helper for publishing text generation failures."""
        event = TextGeneratedEvent(
            request_id=request_id,
            content_type=content_type,
            content_id=UUID(int=0),  # Placeholder ID for failures
            status="failed",
            model_used="unknown",
            token_usage={"prompt": 0, "completion": 0, "total": 0},
        )
        event.data["error"] = error
        await self.publish_event(event)

    async def publish_image_failed(
        self,
        request_id: UUID,
        image_type: str,
        error: str,
    ) -> None:
        """Helper for publishing image generation failures."""
        event = ImageGeneratedEvent(
            request_id=request_id,
            image_type=image_type,
            image_id=UUID(int=0),  # Placeholder ID for failures
            status="failed",
            model_used="unknown",
            prompt="",
            parameters={},
        )
        event.data["error"] = error
        await self.publish_event(event)

    async def publish_event(self, event: Event) -> None:
        """Publish event to Message Hub."""
        try:
            response = await self.client.post(
                "/events",
                json=event.to_dict(),
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                "event_publish_failed",
                error=str(e),
                event_type=event.metadata.event_type,
                correlation_id=event.metadata.correlation_id,
            )
            raise

        self.logger.info(
            "event_published",
            event_type=event.metadata.event_type,
            correlation_id=event.metadata.correlation_id,
        )

    async def publish_events(self, events: List[Event]) -> None:
        """Publish multiple events to Message Hub."""
        try:
            response = await self.client.post(
                "/events/batch",
                json=[event.to_dict() for event in events],
            )
            response.raise_for_status()
        except Exception as e:
            self.logger.error(
                "batch_event_publish_failed",
                error=str(e),
                event_count=len(events),
            )
            raise

        self.logger.info(
            "batch_events_published",
            event_count=len(events),
        )
