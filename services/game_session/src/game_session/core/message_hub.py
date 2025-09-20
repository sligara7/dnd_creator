"""Game Session Service - Message Hub Client.

This module implements the Message Hub client for event-based communication.
"""
from datetime import datetime
import json
from typing import Any, Callable, Dict, Optional
from uuid import UUID, uuid4

import aio_pika
from aio_pika.abc import AbstractIncomingMessage, AbstractQueue
from aio_pika.pool import Pool
from prometheus_client import Counter, Histogram
from structlog import get_logger

from game_session.core.config import Settings

logger = get_logger(__name__)

# Metrics
MESSAGE_HUB_OPS = Counter(
    "game_session_message_hub_operations_total",
    "Total count of Message Hub operations",
    ["operation", "success"],
)

MESSAGE_HUB_LATENCY = Histogram(
    "game_session_message_hub_operation_latency_seconds",
    "Message Hub operation latency in seconds",
    ["operation"],
)


class MessageHubClient:
    """Message Hub client for event-based communication."""

    def __init__(self, settings: Settings):
        """Initialize Message Hub client.

        Args:
            settings: Service configuration settings.
        """
        self.settings = settings
        self.connection: Optional[aio_pika.Connection] = None
        self.channel_pool: Optional[Pool] = None
        self._handlers: Dict[str, Callable] = {}

        # Event names - follow ICD.md naming convention
        self.events = {
            # Session events we publish
            "publish": {
                "session_state": "session.state.changed",
                "session_combat": "session.combat.changed",
            },
            # Events we subscribe to
            "subscribe": {
                "character_state": "character.state.changed",
                "campaign_state": "campaign.state.changed",
            },
            # Storage service events
            "storage": {
                "save_state": "storage.session.save_state",
                "load_state": "storage.session.load_state",
                "save_event": "storage.session.save_event",
            }
        }

    async def connect(self) -> None:
        """Connect to Message Hub."""
        try:
            # Build connection URL
            connection_str = f"amqp://{self.settings.MESSAGE_HUB_USER}:{self.settings.MESSAGE_HUB_PASSWORD}"
            connection_str += f"@{self.settings.MESSAGE_HUB_HOST}:{self.settings.MESSAGE_HUB_PORT}"
            connection_str += f"/{self.settings.MESSAGE_HUB_VHOST}"

            # Connect with robust connection that auto-reconnects
            self.connection = await aio_pika.connect_robust(
                connection_str,
                ssl=self.settings.MESSAGE_HUB_SSL,
            )

            # Create channel pool
            self.channel_pool = Pool(
                self._create_channel,
                max_size=10,  # Adjust based on needs
                max_usage=1000,  # Recreate channel after 1000 uses
            )

            logger.info("Connected to Message Hub")
            MESSAGE_HUB_OPS.labels("connect", "success").inc()

        except Exception as e:
            logger.error("Failed to connect to Message Hub", error=str(e))
            MESSAGE_HUB_OPS.labels("connect", "failure").inc()
            raise

    async def _create_channel(self) -> aio_pika.Channel:
        """Create channel from connection.

        Returns:
            New channel instance.
        """
        if not self.connection:
            raise RuntimeError("No Message Hub connection")
        return await self.connection.channel()

    async def close(self) -> None:
        """Close Message Hub connection."""
        if self.channel_pool:
            await self.channel_pool.close()
        if self.connection:
            await self.connection.close()
            logger.info("Message Hub connection closed")

    async def publish_event(
        self,
        routing_key: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
    ) -> None:
        """Publish event to Message Hub.

        Args:
            routing_key: Event routing key.
            data: Event data.
            correlation_id: Optional correlation ID for request tracking.
        """
        if not self.channel_pool:
            raise RuntimeError("No Message Hub channel pool")

        try:
            async with MESSAGE_HUB_LATENCY.labels("publish").time(), \
                      self.channel_pool.acquire() as channel:
                # Ensure channel has exchange declared
                exchange = await channel.declare_exchange(
                    "game_events",
                    type="topic",
                    durable=True,
                )

                # Create message with headers
                message = aio_pika.Message(
                    body=json.dumps(data).encode(),
                    content_type="application/json",
                    correlation_id=correlation_id or str(uuid4()),
                    timestamp=datetime.utcnow().timestamp(),
                )

                # Publish with retry
                max_retries = 3
                for attempt in range(max_retries):
                    try:
                        await exchange.publish(
                            message,
                            routing_key=routing_key,
                            mandatory=True,  # Ensure message is routable
                        )
                        MESSAGE_HUB_OPS.labels("publish", "success").inc()
                        return
                    except Exception as e:
                        if attempt == max_retries - 1:
                            raise
                        await asyncio.sleep(0.1 * (attempt + 1))  # Exponential backoff

        except Exception as e:
            logger.error(
                "Failed to publish event",
                routing_key=routing_key,
                error=str(e),
            )
            MESSAGE_HUB_OPS.labels("publish", "failure").inc()
            raise

    async def subscribe(
        self,
        routing_key: str,
        handler: Callable[[Dict[str, Any]], None],
        queue_name: Optional[str] = None,
    ) -> None:
        """Subscribe to events from Message Hub.

        Args:
            routing_key: Event routing key to subscribe to.
            handler: Callback function for handling messages.
            queue_name: Optional queue name for the subscription.
        """
        if not self.channel_pool:
            raise RuntimeError("No Message Hub channel pool")

        try:
            async with self.channel_pool.acquire() as channel:
                # Declare exchange
                exchange = await channel.declare_exchange(
                    "game_events",
                    type="topic",
                    durable=True,
                )

                # Declare queue
                queue = await channel.declare_queue(
                    queue_name or "",  # Empty for auto-generated name
                    durable=True,
                    auto_delete=queue_name is None,  # Auto-delete if no name given
                )

                # Bind queue to exchange
                await queue.bind(
                    exchange=exchange,
                    routing_key=routing_key,
                )

                # Store handler
                self._handlers[routing_key] = handler

                # Start consuming
                await queue.consume(self._message_handler)
                logger.info(
                    "Subscribed to event",
                    routing_key=routing_key,
                    queue=queue.name,
                )
                MESSAGE_HUB_OPS.labels("subscribe", "success").inc()

        except Exception as e:
            logger.error(
                "Failed to subscribe to event",
                routing_key=routing_key,
                error=str(e),
            )
            MESSAGE_HUB_OPS.labels("subscribe", "failure").inc()
            raise

    async def _message_handler(self, message: AbstractIncomingMessage) -> None:
        """Handle incoming messages from subscriptions.

        Args:
            message: Incoming message.
        """
        async with message.process():
            routing_key = message.routing_key
            handler = self._handlers.get(routing_key)

            if not handler:
                logger.error("No handler for routing key", routing_key=routing_key)
                return

            try:
                with MESSAGE_HUB_LATENCY.labels("handle").time():
                    # Parse message body
                    data = json.loads(message.body.decode())

                    # Call handler
                    await handler(data)
                    MESSAGE_HUB_OPS.labels("handle", "success").inc()

            except Exception as e:
                logger.error(
                    "Error handling message",
                    routing_key=routing_key,
                    error=str(e),
                )
                MESSAGE_HUB_OPS.labels("handle", "failure").inc()