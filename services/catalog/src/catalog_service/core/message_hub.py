"""Message Hub integration for catalog service."""

import asyncio
import json
import logging
from typing import Any, Callable, Dict, Optional
import asyncio
from uuid import UUID, uuid4

import aio_pika
from aio_pika import Message, DeliveryMode
from prometheus_client import Counter, Histogram

from catalog_service.config import settings
from catalog_service.models import BaseContent, ContentType
from catalog_service.models.storage import StorageOperation, StorageRequest, StorageResponse
from catalog_service.core.exceptions import StorageServiceError

logger = logging.getLogger(__name__)

# Metrics
MESSAGE_COUNT = Counter(
    "catalog_message_count_total",
    "Total number of messages processed",
    ["type", "operation"]
)

MESSAGE_LATENCY = Histogram(
    "catalog_message_processing_duration_seconds",
    "Message processing duration in seconds",
    ["type"]
)

class MessageHub:
    """Message Hub client for catalog service."""

def __init__(self) -> None:
        """Initialize the Message Hub client."""
        self.connection: Optional[aio_pika.Connection] = None
        self.channel: Optional[aio_pika.Channel] = None
        self._event_handlers: Dict[str, Callable] = {}
        self._storage_responses: Dict[UUID, asyncio.Future] = {}

    async def connect(self) -> None:
        """Connect to Message Hub."""
        try:
            self.connection = await aio_pika.connect_robust(
                settings.MESSAGE_HUB_URL,
                timeout=30
            )
            self.channel = await self.connection.channel()
            logger.info("Connected to Message Hub")

            # Declare exchanges
            await self._setup_exchanges()
            
            # Set up storage response queue
            self.response_queue = await self.channel.declare_queue(
                f"catalog_storage_responses_{uuid4()}",
                auto_delete=True
            )
            await self.response_queue.consume(self._handle_storage_response)
            
            # Set up subscriptions
            await self._setup_subscriptions()
            
        except Exception as e:
            logger.error(f"Failed to connect to Message Hub: {e}")
            raise

    async def _setup_exchanges(self) -> None:
        """Set up required exchanges."""
        if not self.channel:
            raise RuntimeError("Channel not initialized")

        # Catalog events exchange
        await self.channel.declare_exchange(
            "catalog_events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

        # Theme events exchange (for receiving theme updates)
        await self.channel.declare_exchange(
            "theme_events",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )
        
        # Storage operations exchange
        await self.channel.declare_exchange(
            "storage_ops",
            aio_pika.ExchangeType.TOPIC,
            durable=True
        )

    async def _setup_subscriptions(self) -> None:
        """Set up event subscriptions."""
        if not self.channel:
            raise RuntimeError("Channel not initialized")

        # Subscribe to theme updates
        theme_exchange = await self.channel.declare_exchange(
            "theme_events",
            aio_pika.ExchangeType.TOPIC
        )
        
        queue = await self.channel.declare_queue(
            "catalog_theme_updates",
            durable=True
        )
        
        await queue.bind(
            theme_exchange,
            routing_key="theme.updated"
        )
        
        await queue.consume(self._handle_theme_update)

        logger.info("Subscribed to theme updates")

    async def publish_event(
        self,
        event_type: str,
        content_type: ContentType,
        content_id: UUID,
        data: Dict[str, Any]
    ) -> None:
        """Publish catalog event to Message Hub.
        
        Args:
            event_type: Type of event (created, updated, deleted)
            content_type: Type of content
            content_id: Content UUID
            data: Event data
        """
        if not self.channel:
            logger.error("Cannot publish event: not connected to Message Hub")
            return

        try:
            exchange = await self.channel.declare_exchange(
                "catalog_events",
                aio_pika.ExchangeType.TOPIC
            )

            routing_key = f"catalog.{content_type}.{event_type}"
            
            message = Message(
                json.dumps({
                    "event_type": event_type,
                    "content_type": content_type,
                    "content_id": str(content_id),
                    "data": data
                }).encode(),
                delivery_mode=DeliveryMode.PERSISTENT,
                content_type="application/json"
            )

            await exchange.publish(message, routing_key=routing_key)
            MESSAGE_COUNT.labels(type=content_type, operation=event_type).inc()
            
            logger.info(f"Published {event_type} event for {content_type} {content_id}")
            
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")
            raise

    async def _handle_theme_update(
        self, message: aio_pika.IncomingMessage
    ) -> None:
        """Handle theme update events.
        
        Args:
            message: Incoming message from Message Hub
        """
        async with message.process():
            try:
                with MESSAGE_LATENCY.labels("theme_update").time():
                    data = json.loads(message.body.decode())
                    theme_id = data.get("theme_id")
                    logger.info(f"Processing theme update for theme {theme_id}")
                    
                    # TODO: Implement theme update handling
                    # This will be implemented when we add theme adaptation support
                    
                    MESSAGE_COUNT.labels(type="theme", operation="update").inc()
                    
            except Exception as e:
                logger.error(f"Failed to process theme update: {e}")
                # Reject the message to trigger retry
                await message.reject(requeue=True)

    async def _handle_storage_response(self, message: aio_pika.IncomingMessage) -> None:
        """Handle storage operation response.
        
        Args:
            message: Response message from storage service
        """
        async with message.process():
            try:
                response = StorageResponse.parse_raw(message.body.decode())
                future = self._storage_responses.get(response.correlation_id)
                if future and not future.done():
                    future.set_result(response)
            except Exception as e:
                logger.error(f"Failed to process storage response: {e}")
    
    async def _storage_operation(
        self,
        operation: StorageOperation,
        collection: str,
        entity_id: Optional[UUID] = None,
        data: Optional[Dict[str, Any]] = None,
        timeout: float = 30.0
    ) -> StorageResponse:
        """Execute storage operation via Message Hub.
        
        Args:
            operation: Operation type
            collection: Collection/table name
            entity_id: Entity UUID for read/update/delete
            data: Operation data for create/update
            timeout: Operation timeout in seconds
        
        Returns:
            Storage operation response
        
        Raises:
            StorageServiceError: If operation fails
        """
        if not self.channel:
            raise RuntimeError("Not connected to Message Hub")
        
        correlation_id = uuid4()
        request = StorageRequest(
            operation=operation,
            collection=collection,
            correlation_id=correlation_id,
            entity_id=entity_id,
            data=data
        )
        
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        self._storage_responses[correlation_id] = future
        
        try:
            # Send request
            exchange = await self.channel.declare_exchange(
                "storage_ops",
                aio_pika.ExchangeType.TOPIC
            )
            
            await exchange.publish(
                Message(
                    body=request.json().encode(),
                    correlation_id=str(correlation_id),
                    reply_to=self.response_queue.name,
                    content_type="application/json",
                    delivery_mode=DeliveryMode.PERSISTENT
                ),
                routing_key=f"storage.{operation.value}"
            )
            
            # Wait for response
            try:
                response = await asyncio.wait_for(future, timeout)
                if not response.success:
                    raise StorageServiceError(response.error or "Unknown error")
                return response
            except asyncio.TimeoutError:
                raise StorageServiceError("Storage operation timed out")
            
        finally:
            self._storage_responses.pop(correlation_id, None)
    
    async def store_content(
        self,
        content_type: ContentType,
        content: BaseContent
    ) -> Optional[Dict[str, Any]]:
        """Store content in catalog.
        
        Args:
            content_type: Type of content
            content: Content to store
        
        Returns:
            Stored content data if successful
        """
        response = await self._storage_operation(
            StorageOperation.CREATE,
            str(content_type),
            data=content.model_dump()
        )
        return response.data
    
    async def get_content(
        self,
        content_type: ContentType,
        content_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Retrieve content from catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
        
        Returns:
            Content data if found
        """
        response = await self._storage_operation(
            StorageOperation.READ,
            str(content_type),
            entity_id=content_id
        )
        return response.data
    
    async def update_content(
        self,
        content_type: ContentType,
        content_id: UUID,
        content: BaseContent
    ) -> Optional[Dict[str, Any]]:
        """Update content in catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
            content: Updated content
        
        Returns:
            Updated content data if successful
        """
        response = await self._storage_operation(
            StorageOperation.UPDATE,
            str(content_type),
            entity_id=content_id,
            data=content.model_dump()
        )
        return response.data
    
    async def delete_content(
        self,
        content_type: ContentType,
        content_id: UUID
    ) -> bool:
        """Delete content from catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
        
        Returns:
            True if deleted successfully
        """
        response = await self._storage_operation(
            StorageOperation.DELETE,
            str(content_type),
            entity_id=content_id
        )
        return response.success
    
    async def disconnect(self) -> None:
        """Disconnect from Message Hub."""
        try:
            if self.connection:
                await self.connection.close()
                logger.info("Disconnected from Message Hub")
        except Exception as e:
            logger.error(f"Error disconnecting from Message Hub: {e}")

# Global Message Hub instance
message_hub = MessageHub()

async def get_message_hub() -> MessageHub:
    """Get Message Hub instance.
    
    Returns:
        MessageHub instance
    """
    return message_hub