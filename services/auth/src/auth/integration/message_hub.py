"""Message Hub integration for auth service."""

import asyncio
import json
import logging
from functools import partial
from typing import Any, Awaitable, Callable, Dict, List, Optional
from uuid import UUID

import aio_pika
from pydantic import BaseModel, Field

from auth.core.config import get_settings
from auth.core.exceptions import StorageError

logger = logging.getLogger(__name__)

# Event handler type
EventHandler = Callable[[Dict[str, Any]], Awaitable[None]]


class EventMetadata(BaseModel):
    """Event metadata."""

    event_type: str = Field(..., description="Type of event")
    source_id: str = Field(..., description="Source service ID")
    correlation_id: str = Field(..., description="Correlation ID for tracking")
    timestamp: str = Field(..., description="Event timestamp")


class MessageHubClient:
    """Client for interacting with Message Hub."""

    # Event types published by auth service
    EVENT_USER_CREATED = "auth.user.created"
    EVENT_USER_UPDATED = "auth.user.updated"
    EVENT_USER_DELETED = "auth.user.deleted"
    EVENT_LOGIN_SUCCESS = "auth.login.success"
    EVENT_LOGIN_FAILED = "auth.login.failed"
    EVENT_LOGOUT = "auth.logout"
    EVENT_ROLE_ASSIGNED = "auth.role.assigned"
    EVENT_ROLE_REMOVED = "auth.role.removed"
    EVENT_TOKEN_ISSUED = "auth.token.issued"
    EVENT_TOKEN_REVOKED = "auth.token.revoked"
    EVENT_MFA_ENABLED = "auth.mfa.enabled"
    EVENT_MFA_DISABLED = "auth.mfa.disabled"
    EVENT_API_KEY_CREATED = "auth.api_key.created"
    EVENT_API_KEY_REVOKED = "auth.api_key.revoked"
    EVENT_SECURITY_EVENT = "auth.security.event"

    def __init__(
        self,
        url: Optional[str] = None,
        exchange_name: str = "dnd_events",
        queue_name: str = "auth_service",
        retry_interval: int = 5,
        max_retries: int = 5
    ):
        """Initialize the Message Hub client.

        Args:
            url: Message Hub URL
            exchange_name: Exchange name
            queue_name: Queue name
            retry_interval: Seconds between connection retries
            max_retries: Maximum number of connection retries
        """
        self.settings = get_settings()
        self.url = url or str(self.settings.message_hub_url)
        self.exchange_name = exchange_name
        self.queue_name = queue_name
        self.retry_interval = retry_interval
        self.max_retries = max_retries
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self.exchange: Optional[aio_pika.Exchange] = None
        self.queue: Optional[aio_pika.Queue] = None
        self.handlers: Dict[str, List[EventHandler]] = {}

    async def connect(self) -> None:
        """Connect to Message Hub with retries."""
        retries = 0
        while retries < self.max_retries:
            try:
                # Create connection
                self.connection = await aio_pika.connect_robust(self.url)
                self.channel = await self.connection.channel()

                # Declare exchange
                self.exchange = await self.channel.declare_exchange(
                    self.exchange_name,
                    type=aio_pika.ExchangeType.TOPIC,
                    durable=True
                )

                # Declare queue
                self.queue = await self.channel.declare_queue(
                    self.queue_name,
                    durable=True
                )

                # Set up handlers
                await self._setup_handlers()

                logger.info("Connected to Message Hub", extra={"url": self.url})
                break

            except Exception as e:
                retries += 1
                if retries >= self.max_retries:
                    logger.error(
                        "Failed to connect to Message Hub after retries",
                        extra={"error": str(e)}
                    )
                    raise
                logger.warning(
                    "Failed to connect to Message Hub, retrying...",
                    extra={"attempt": retries, "error": str(e)}
                )
                await asyncio.sleep(self.retry_interval)

    async def close(self) -> None:
        """Close Message Hub connection."""
        try:
            if self.connection:
                await self.connection.close()
            logger.info("Disconnected from Message Hub")
        except Exception as e:
            logger.error(
                "Failed to close Message Hub connection",
                extra={"error": str(e)}
            )
            raise

    async def publish(
        self,
        event_type: str,
        data: Dict[str, Any],
        correlation_id: Optional[str] = None,
        source_id: Optional[str] = None,
        retry: bool = True
    ) -> None:
        """Publish an event to Message Hub.

        Args:
            event_type: Type of event
            data: Event data
            correlation_id: Optional correlation ID
            source_id: Optional source service ID
            retry: Whether to retry on failure

        Raises:
            RuntimeError: If not connected to Message Hub
        """
        if not self.exchange:
            raise RuntimeError("Message Hub not connected")

        try:
            # Create event metadata
            metadata = EventMetadata(
                event_type=event_type,
                source_id=source_id or self.settings.service_name,
                correlation_id=correlation_id or "",
                timestamp=str(asyncio.get_running_loop().time())
            )

            # Create message
            message = aio_pika.Message(
                body=json.dumps({
                    "metadata": metadata.dict(),
                    "data": data
                }).encode(),
                content_type="application/json",
                headers={"event_type": event_type},
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT
            )

            # Publish with retry
            try:
                await self.exchange.publish(
                    message,
                    routing_key=event_type,
                    timeout=self.settings.message_hub_timeout
                )

                logger.info(
                    "Published event",
                    extra={
                        "event_type": event_type,
                        "correlation_id": correlation_id
                    }
                )

            except Exception as e:
                if retry:
                    logger.warning(
                        "Failed to publish event, reconnecting...",
                        extra={
                            "event_type": event_type,
                            "error": str(e)
                        }
                    )
                    await self.connect()
                    await self.publish(
                        event_type,
                        data,
                        correlation_id,
                        source_id,
                        retry=False
                    )
                else:
                    raise

        except Exception as e:
            logger.error(
                "Failed to publish event",
                extra={
                    "event_type": event_type,
                    "error": str(e)
                }
            )
            raise

    def subscribe(self, event_type: str, handler: EventHandler) -> None:
        """Subscribe to an event type.

        Args:
            event_type: Type of event to subscribe to
            handler: Event handler function
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []
        self.handlers[event_type].append(handler)

        logger.info(
            "Subscribed to event",
            extra={
                "event_type": event_type,
                "handler": handler.__name__
            }
        )

    async def _setup_handlers(self) -> None:
        """Set up event handlers.

        Raises:
            RuntimeError: If not connected to Message Hub
        """
        if not self.queue or not self.exchange:
            raise RuntimeError("Message Hub not connected")

        # Define message handler
        async def process_message(message: aio_pika.IncomingMessage) -> None:
            """Process incoming messages.

            Args:
                message: Message to process
            """
            async with message.process():
                try:
                    # Get event type from headers
                    event_type = message.headers.get("event_type")
                    if not event_type:
                        logger.warning(
                            "Message missing event_type",
                            extra={"message": message.body.decode()}
                        )
                        return

                    # Parse message
                    body = json.loads(message.body.decode())
                    metadata = body.get("metadata", {})
                    data = body.get("data", {})
                    handlers = self.handlers.get(event_type, [])

                    # Call handlers
                    for handler in handlers:
                        try:
                            await handler(data)
                        except Exception as e:
                            logger.error(
                                "Handler failed",
                                extra={
                                    "handler": handler.__name__,
                                    "event_type": event_type,
                                    "error": str(e)
                                }
                            )

                    logger.info(
                        "Processed event",
                        extra={
                            "event_type": event_type,
                            "handler_count": len(handlers)
                        }
                    )

                except Exception as e:
                    logger.error(
                        "Failed to process message",
                        extra={"error": str(e)}
                    )

        # Bind queue to exchange for each event type
        for event_type in self.handlers:
            await self.queue.bind(
                self.exchange,
                routing_key=event_type
            )

        # Start consuming messages
        await self.queue.consume(process_message)


# Convenience functions for common auth events
async def publish_user_created(
    client: MessageHubClient,
    user_id: UUID,
    username: str,
    correlation_id: Optional[str] = None
) -> None:
    """Publish user created event.

    Args:
        client: Message Hub client
        user_id: User ID
        username: Username
        correlation_id: Optional correlation ID
    """
    await client.publish(
        MessageHubClient.EVENT_USER_CREATED,
        {
            "user_id": str(user_id),
            "username": username
        },
        correlation_id=correlation_id
    )


async def publish_login_event(
    client: MessageHubClient,
    user_id: UUID,
    success: bool,
    client_info: Optional[Dict] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Publish login event.

    Args:
        client: Message Hub client
        user_id: User ID
        success: Whether login was successful
        client_info: Optional client information
        correlation_id: Optional correlation ID
    """
    event_type = (
        MessageHubClient.EVENT_LOGIN_SUCCESS if success
        else MessageHubClient.EVENT_LOGIN_FAILED
    )
    await client.publish(
        event_type,
        {
            "user_id": str(user_id),
            "client_info": client_info or {}
        },
        correlation_id=correlation_id
    )


async def publish_role_change(
    client: MessageHubClient,
    user_id: UUID,
    role_id: UUID,
    assigned: bool,
    correlation_id: Optional[str] = None
) -> None:
    """Publish role change event.

    Args:
        client: Message Hub client
        user_id: User ID
        role_id: Role ID
        assigned: Whether role was assigned or removed
        correlation_id: Optional correlation ID
    """
    event_type = (
        MessageHubClient.EVENT_ROLE_ASSIGNED if assigned
        else MessageHubClient.EVENT_ROLE_REMOVED
    )
    await client.publish(
        event_type,
        {
            "user_id": str(user_id),
            "role_id": str(role_id)
        },
        correlation_id=correlation_id
    )


async def publish_security_event(
    client: MessageHubClient,
    event_name: str,
    details: Dict[str, Any],
    user_id: Optional[UUID] = None,
    correlation_id: Optional[str] = None
) -> None:
    """Publish security event.

    Args:
        client: Message Hub client
        event_name: Name of security event
        details: Event details
        user_id: Optional user ID
        correlation_id: Optional correlation ID
    """
    data = {
        "event_name": event_name,
        "details": details
    }
    if user_id:
        data["user_id"] = str(user_id)

    await client.publish(
        MessageHubClient.EVENT_SECURITY_EVENT,
        data,
        correlation_id=correlation_id
    )