"""Message Hub integration."""

import asyncio
import json
from functools import partial
from typing import Any, Awaitable, Callable, Dict, List, Optional

import aio_pika
from pydantic import BaseModel

from image_service.core.config import get_settings
from image_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)

# Event handler type
EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventMetadata(BaseModel):
    """Event metadata."""

    event_type: str
    source_id: str
    correlation_id: str
    timestamp: str


class MessageHubClient:
    """Client for interacting with Message Hub."""

    def __init__(
        self,
        url: Optional[str] = None,
        exchange_name: str = "dnd_events",
        queue_name: str = "image_service",
    ):
        """Initialize the Message Hub client."""
        self.url = url or str(settings.MESSAGE_HUB_URL)
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.handlers: Dict[str, List[EventHandler]] = {}

    async def connect(self) -> None:
        """Connect to Message Hub."""
        try:
            # Create connection
            self.connection = await aio_pika.connect_robust(self.url)
            self.channel = await self.connection.channel()

            # Declare exchange
            self.exchange = await self.channel.declare_exchange(
                self.exchange_name, type=aio_pika.ExchangeType.TOPIC, durable=True
            )

            # Declare queue
            self.queue = await self.channel.declare_queue(
                self.queue_name, durable=True
            )

            # Set up handlers
            await self._setup_handlers()

            logger.info("Connected to Message Hub", url=self.url)
        except Exception as e:
            logger.error("Failed to connect to Message Hub", error=str(e))
            raise

    async def close(self) -> None:
        """Close Message Hub connection."""
        try:
            if self.connection:
                await self.connection.close()
            logger.info("Disconnected from Message Hub")
        except Exception as e:
            logger.error("Failed to close Message Hub connection", error=str(e))
            raise

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> None:
        """Publish an event to Message Hub."""
        if not self.exchange:
            raise RuntimeError("Message Hub not connected")

        try:
            # Create event metadata
            metadata = EventMetadata(
                event_type=event_type,
                source_id=source_id or settings.SERVICE_NAME,
                correlation_id=correlation_id or "",
                timestamp=str(asyncio.get_running_loop().time()),
            )

            # Create message
            message = aio_pika.Message(
                body=json.dumps(
                    {"metadata": metadata.dict(), "data": data}
                ).encode(),
                content_type="application/json",
                headers={"event_type": event_type},
            )

            # Publish message
            await self.exchange.publish(
                message, routing_key=event_type, timeout=settings.MESSAGE_HUB_TIMEOUT
            )

            logger.info(
                "Published event",
                event_type=event_type,
                correlation_id=correlation_id,
            )
        except Exception as e:
            logger.error(
                "Failed to publish event",
                event_type=event_type,
                error=str(e),
            )
            raise

    def subscribe(
        self, event_type: str, handler: EventHandler
    ) -> None:
        """Subscribe to an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

        logger.info(
            "Subscribed to event",
            event_type=event_type,
            handler=handler.__name__,
        )

    async def _setup_handlers(self) -> None:
        """Set up event handlers."""
        if not self.queue or not self.exchange:
            raise RuntimeError("Message Hub not connected")

        # Define message handler
        async def process_message(
            message: aio_pika.IncomingMessage,
        ) -> None:
            """Process incoming messages."""
            async with message.process():
                try:
                    # Get event type from headers
                    event_type = message.headers.get("event_type")
                    if not event_type:
                        logger.warning("Message missing event_type", message=message)
                        return

                    # Parse message
                    body = json.loads(message.body.decode())
                    handlers = self.handlers.get(event_type, [])

                    # Call handlers
                    for handler in handlers:
                        try:
                            await handler(body.get("data", {}))
                        except Exception as e:
                            logger.error(
                                "Handler failed",
                                handler=handler.__name__,
                                error=str(e),
                            )

                    logger.info(
                        "Processed event",
                        event_type=event_type,
                        handler_count=len(handlers),
                    )
                except Exception as e:
                    logger.error("Failed to process message", error=str(e))

        # Bind queue to exchange for each event type
        for event_type in self.handlers:
            await self.queue.bind(
                self.exchange,
                routing_key=event_type,
            )

        # Start consuming messages
        await self.queue.consume(process_message)
