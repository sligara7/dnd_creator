"""Message Hub integration for LLM service.

This module handles all message-based communication through the Message Hub service.
"""
import json
from typing import Any, Dict, Optional, Union
from uuid import UUID

import aio_pika
from pydantic import BaseModel

from ..core.config import Settings


class MessageContext(BaseModel):
    """Context information for messages."""
    request_id: UUID
    source_service: str = "llm-service"
    timestamp: str
    correlation_id: Optional[UUID] = None


class MessagePayload(BaseModel):
    """Base model for message payloads."""
    context: MessageContext
    data: Dict[str, Any]
    metadata: Optional[Dict[str, Any]] = None


class MessageHubClient:
    """Client for interacting with the Message Hub service."""

    def __init__(self, settings: Settings):
        """Initialize the Message Hub client."""
        self.settings = settings
        self._connection: Optional[aio_pika.Connection] = None
        self._channel: Optional[aio_pika.Channel] = None
        self._exchange: Optional[aio_pika.Exchange] = None

    async def setup(self) -> None:
        """Set up the Message Hub connection and channel."""
        # Create connection
        self._connection = await aio_pika.connect_robust(
            self.settings.MESSAGE_HUB_URL,
            client_properties={
                "connection_name": "llm_service",
            },
        )

        # Create channel
        self._channel = await self._connection.channel()
        await self._channel.set_qos(prefetch_count=10)

        # Declare exchange
        self._exchange = await self._channel.declare_exchange(
            "llm_service",
            aio_pika.ExchangeType.TOPIC,
            durable=True,
        )

        # Declare queues for handling requests
        await self._setup_request_queues()

    async def _setup_request_queues(self) -> None:
        """Set up queues for handling various requests."""
        # Text generation queue
        text_queue = await self._channel.declare_queue(
            "llm_service.text_generation",
            durable=True,
        )
        await text_queue.bind(
            self._exchange,
            routing_key="llm.text.#",
        )
        await text_queue.consume(self._handle_text_generation)

        # Image generation queue
        image_queue = await self._channel.declare_queue(
            "llm_service.image_generation",
            durable=True,
        )
        await image_queue.bind(
            self._exchange,
            routing_key="llm.image.#",
        )
        await image_queue.consume(self._handle_image_generation)

    async def cleanup(self) -> None:
        """Clean up connections."""
        if self._channel:
            await self._channel.close()
        if self._connection:
            await self._connection.close()

    async def publish_event(
        self,
        event_type: str,
        data: Dict[str, Any],
        routing_key: str,
        correlation_id: Optional[UUID] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish an event to the Message Hub."""
        if not self._exchange:
            raise RuntimeError("Message Hub client not initialized")

        from datetime import datetime

        # Create message context
        context = MessageContext(
            request_id=UUID(int=0),  # Placeholder, should be from request context
            timestamp=datetime.utcnow().isoformat(),
            correlation_id=correlation_id,
        )

        # Create message payload
        payload = MessagePayload(
            context=context,
            data=data,
            metadata=metadata or {},
        )

        # Convert to JSON and publish
        message = aio_pika.Message(
            body=json.dumps(payload.dict()).encode(),
            content_type="application/json",
            headers={
                "event_type": event_type,
                "source_service": "llm_service",
            },
            correlation_id=str(correlation_id) if correlation_id else None,
        )

        await self._exchange.publish(
            message,
            routing_key=routing_key,
        )

    async def _handle_text_generation(
        self, message: aio_pika.IncomingMessage
    ) -> None:
        """Handle text generation requests."""
        async with message.process():
            try:
                # Parse message payload
                data = json.loads(message.body.decode())
                
                # Extract request details
                request_type = data.get("type")
                parameters = data.get("parameters", {})
                theme = data.get("theme", {})

                # Process request based on type
                # This will be implemented once we refactor the text generation
                # service to be message-driven
                result = await self._process_text_generation(
                    request_type,
                    parameters,
                    theme,
                )

                # Publish result
                await self.publish_event(
                    event_type="text_generated",
                    data=result,
                    routing_key=f"llm.text.{request_type}.completed",
                    correlation_id=UUID(message.correlation_id) if message.correlation_id else None,
                )

            except Exception as e:
                # Publish error event
                await self.publish_event(
                    event_type="text_generation_failed",
                    data={"error": str(e)},
                    routing_key=f"llm.text.failed",
                    correlation_id=UUID(message.correlation_id) if message.correlation_id else None,
                )

    async def _handle_image_generation(
        self, message: aio_pika.IncomingMessage
    ) -> None:
        """Handle image generation requests."""
        async with message.process():
            try:
                # Parse message payload
                data = json.loads(message.body.decode())
                
                # Extract request details
                request_type = data.get("type")
                content = data.get("content", {})
                parameters = data.get("parameters", {})

                # Process request based on type
                # This will be implemented once we refactor the image generation
                # service to be message-driven
                result = await self._process_image_generation(
                    request_type,
                    content,
                    parameters,
                )

                # Publish result
                await self.publish_event(
                    event_type="image_generated",
                    data=result,
                    routing_key=f"llm.image.{request_type}.completed",
                    correlation_id=UUID(message.correlation_id) if message.correlation_id else None,
                )

            except Exception as e:
                # Publish error event
                await self.publish_event(
                    event_type="image_generation_failed",
                    data={"error": str(e)},
                    routing_key=f"llm.image.failed",
                    correlation_id=UUID(message.correlation_id) if message.correlation_id else None,
                )

    async def _process_text_generation(
        self,
        request_type: str,
        parameters: Dict[str, Any],
        theme: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process text generation request.

        This is a placeholder that will be implemented when we refactor
        the text generation service to be message-driven.
        """
        raise NotImplementedError

    async def _process_image_generation(
        self,
        request_type: str,
        content: Dict[str, Any],
        parameters: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Process image generation request.

        This is a placeholder that will be implemented when we refactor
        the image generation service to be message-driven.
        """
        raise NotImplementedError