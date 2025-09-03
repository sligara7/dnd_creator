"""Message hub client for async event handling."""
import json
from typing import Any, Dict, List, Optional, Union, Callable
from uuid import UUID

import aio_pika
from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractIncomingMessage
from aio_pika.pool import Pool
from tenacity import retry, stop_after_attempt, wait_exponential

from ...core.config import settings
from ...core.logging import get_logger

logger = get_logger(__name__)


class MessageHubClient:
    """Client for interacting with the message hub."""

    def __init__(self):
        """Initialize the client."""
        self.connection_pool = None
        self.channel_pool = None
        self._event_handlers = {}
        self._initialized = False

    async def initialize(self):
        """Initialize connection pools."""
        if self._initialized:
            return

        # Create connection pool
        self.connection_pool = Pool(
            self._get_connection,
            max_size=settings.MESSAGE_HUB_POOL_SIZE,
        )

        # Create channel pool
        self.channel_pool = Pool(
            self._get_channel,
            max_size=settings.MESSAGE_HUB_POOL_SIZE,
        )

        self._initialized = True

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def _get_connection(self) -> aio_pika.Connection:
        """Get a connection from the pool."""
        return await connect_robust(
            settings.MESSAGE_HUB_URL,
            client_properties={
                "connection_name": "campaign_service"
            }
        )

    async def _get_channel(self) -> aio_pika.Channel:
        """Get a channel from the pool."""
        async with self.connection_pool.acquire() as connection:
            return await connection.channel()

    async def publish(
        self,
        routing_key: str,
        message: Dict[str, Any],
        correlation_id: Optional[str] = None,
        headers: Optional[Dict] = None
    ) -> None:
        """Publish a message to the message hub."""
        if not self._initialized:
            await self.initialize()

        try:
            async with self.channel_pool.acquire() as channel:
                exchange = await channel.get_exchange(settings.MESSAGE_HUB_EXCHANGE)
                
                await exchange.publish(
                    Message(
                        body=json.dumps(message).encode(),
                        content_type="application/json",
                        correlation_id=correlation_id,
                        headers=headers or {},
                    ),
                    routing_key=routing_key,
                )

                logger.info(
                    "Message published",
                    routing_key=routing_key,
                    correlation_id=correlation_id
                )

        except Exception as e:
            logger.error(
                "Failed to publish message",
                error=str(e),
                routing_key=routing_key,
                correlation_id=correlation_id
            )
            raise

    async def subscribe(
        self,
        queue_name: str,
        callback: Callable[[Dict], Any],
        routing_key: str,
        auto_delete: bool = False
    ) -> None:
        """Subscribe to a queue for message handling."""
        if not self._initialized:
            await self.initialize()

        try:
            async with self.channel_pool.acquire() as channel:
                # Declare queue
                queue = await channel.declare_queue(
                    queue_name,
                    durable=True,
                    auto_delete=auto_delete
                )

                # Bind queue to exchange
                await queue.bind(
                    settings.MESSAGE_HUB_EXCHANGE,
                    routing_key=routing_key
                )

                # Store handler
                self._event_handlers[queue_name] = callback

                # Start consuming
                await queue.consume(self._message_handler)

                logger.info(
                    "Subscribed to queue",
                    queue=queue_name,
                    routing_key=routing_key
                )

        except Exception as e:
            logger.error(
                "Failed to subscribe to queue",
                error=str(e),
                queue=queue_name,
                routing_key=routing_key
            )
            raise

    async def _message_handler(self, message: AbstractIncomingMessage):
        """Handle incoming messages."""
        async with message.process():
            queue_name = message.routing_key
            handler = self._event_handlers.get(queue_name)

            if not handler:
                logger.warning(
                    "No handler found for queue",
                    queue=queue_name
                )
                return

            try:
                body = json.loads(message.body.decode())
                await handler(body)

                logger.info(
                    "Message processed",
                    queue=queue_name,
                    correlation_id=message.correlation_id
                )

            except Exception as e:
                logger.error(
                    "Failed to process message",
                    error=str(e),
                    queue=queue_name,
                    correlation_id=message.correlation_id
                )
                # Don't re-raise to avoid requeuing
                return

    async def request(
        self,
        routing_key: str,
        message: Dict[str, Any],
        correlation_id: Optional[str] = None,
        timeout: float = 30.0
    ) -> Optional[Dict]:
        """Send a request and wait for response."""
        if not self._initialized:
            await self.initialize()

        try:
            async with self.channel_pool.acquire() as channel:
                # Declare response queue
                response_queue = await channel.declare_queue(
                    "",  # Let RabbitMQ generate name
                    exclusive=True,
                    auto_delete=True
                )

                # Generate correlation ID if not provided
                if not correlation_id:
                    correlation_id = str(UUID())

                # Publish request
                exchange = await channel.get_exchange(settings.MESSAGE_HUB_EXCHANGE)
                await exchange.publish(
                    Message(
                        body=json.dumps(message).encode(),
                        content_type="application/json",
                        correlation_id=correlation_id,
                        reply_to=response_queue.name,
                    ),
                    routing_key=routing_key,
                )

                # Wait for response
                try:
                    async with response_queue.iterator() as iterator:
                        async for message in iterator:
                            if message.correlation_id == correlation_id:
                                return json.loads(message.body.decode())
                            
                            if iterator.timeout(timeout):
                                raise TimeoutError("Request timed out")

                finally:
                    await response_queue.delete()

        except Exception as e:
            logger.error(
                "Request failed",
                error=str(e),
                routing_key=routing_key,
                correlation_id=correlation_id
            )
            raise

    async def health_check(self) -> bool:
        """Check message hub connection health."""
        try:
            if not self._initialized:
                await self.initialize()

            async with self.channel_pool.acquire() as channel:
                return channel.is_closed == False

        except Exception as e:
            logger.error("Health check failed", error=str(e))
            return False

    async def close(self):
        """Close all connections."""
        if self.channel_pool:
            await self.channel_pool.close()
        if self.connection_pool:
            await self.connection_pool.close()
        self._initialized = False
