"""
Message Hub client for the Audit Service.

This module handles communication with the Message Hub service.
"""
from typing import Any, Dict, List, Optional
import json

import structlog
import aio_pika
from aio_pika.abc import AbstractRobustConnection, AbstractChannel
from aio_pika.exceptions import AMQPError
from aio_pika.pool import Pool

from audit_service.core.config import settings
from audit_service.core.exceptions import EventRoutingError
from audit_service.models.events import Event

logger = structlog.get_logger()

class MessageHubClient:
    """Client for interacting with the Message Hub service."""
    
    def __init__(self) -> None:
        """Initialize the Message Hub client."""
        self.logger = logger.bind(component="message_hub_client")
        self._connection: Optional[AbstractRobustConnection] = None
        self._channel_pool: Optional[Pool[AbstractChannel]] = None
        self._exchange_name = "audit.events"
        self._routing_key_prefix = "audit"
        self._max_retries = settings.MAX_RETRIES
        self._retry_delay = settings.RETRY_DELAY
    
    async def setup(self) -> None:
        """Set up the Message Hub connection and channel pool."""
        try:
            # Create connection
            self._connection = await aio_pika.connect_robust(
                settings.MESSAGE_HUB_URL,
                client_properties={
                    "connection_name": "audit_service"
                }
            )
            
            # Create channel pool
            self._channel_pool = Pool(
                self._create_channel,
                max_size=5,
                loop=None
            )
            
            self.logger.info("Connected to Message Hub")
            
        except AMQPError as e:
            self.logger.error(
                "Failed to connect to Message Hub",
                error=str(e)
            )
            raise EventRoutingError(
                message="Failed to connect to Message Hub",
                source="audit_service",
                event_type="connection",
                details={"error": str(e)}
            )
    
    async def _create_channel(self) -> AbstractChannel:
        """Create a new channel."""
        if not self._connection:
            raise EventRoutingError(
                message="No Message Hub connection available",
                source="audit_service",
                event_type="channel",
                details={"error": "Connection not initialized"}
            )
        
        channel = await self._connection.channel()
        await channel.set_qos(prefetch_count=100)
        
        # Declare exchange
        exchange = await channel.declare_exchange(
            name=self._exchange_name,
            type="topic",
            durable=True
        )
        
        return channel
    
    async def cleanup(self) -> None:
        """Clean up resources."""
        if self._channel_pool:
            await self._channel_pool.close()
        
        if self._connection:
            await self._connection.close()
    
    def _get_routing_key(self, event: Event) -> str:
        """Get routing key for an event."""
        return f"{self._routing_key_prefix}.{event.service}.{event.type}"
    
    def _serialize_event(self, event: Event) -> bytes:
        """Serialize event to bytes."""
        return json.dumps(event.model_dump()).encode()
    
    async def publish_event(self, event: Event) -> None:
        """
        Publish an event to the Message Hub.
        
        Args:
            event: Event to publish
            
        Raises:
            EventRoutingError: If publishing fails
        """
        try:
            async with self._channel_pool.acquire() as channel:
                exchange = await channel.get_exchange(self._exchange_name)
                
                # Create message
                message = aio_pika.Message(
                    body=self._serialize_event(event),
                    content_type="application/json",
                    delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                    headers={
                        "service": event.service,
                        "type": event.type,
                        "severity": event.severity,
                        "environment": event.context.environment
                    }
                )
                
                # Publish with retry
                for attempt in range(self._max_retries):
                    try:
                        await exchange.publish(
                            message,
                            routing_key=self._get_routing_key(event)
                        )
                        return
                        
                    except AMQPError as e:
                        if attempt == self._max_retries - 1:
                            raise e
                        
                        self.logger.warning(
                            "Publish attempt failed, retrying",
                            attempt=attempt + 1,
                            max_retries=self._max_retries,
                            error=str(e)
                        )
                        await asyncio.sleep(self._retry_delay)
                        
        except Exception as e:
            raise EventRoutingError(
                message="Failed to publish event",
                source="audit_service",
                event_type=event.type,
                details={"error": str(e)}
            )
    
    async def publish_events(self, events: List[Event]) -> None:
        """
        Publish multiple events to the Message Hub.
        
        Args:
            events: List of events to publish
            
        Raises:
            EventRoutingError: If publishing fails
        """
        try:
            async with self._channel_pool.acquire() as channel:
                exchange = await channel.get_exchange(self._exchange_name)
                
                for event in events:
                    message = aio_pika.Message(
                        body=self._serialize_event(event),
                        content_type="application/json",
                        delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
                        headers={
                            "service": event.service,
                            "type": event.type,
                            "severity": event.severity,
                            "environment": event.context.environment
                        }
                    )
                    
                    # Publish with retry
                    for attempt in range(self._max_retries):
                        try:
                            await exchange.publish(
                                message,
                                routing_key=self._get_routing_key(event)
                            )
                            break
                            
                        except AMQPError as e:
                            if attempt == self._max_retries - 1:
                                raise e
                            
                            self.logger.warning(
                                "Publish attempt failed, retrying",
                                attempt=attempt + 1,
                                max_retries=self._max_retries,
                                error=str(e)
                            )
                            await asyncio.sleep(self._retry_delay)
                
        except Exception as e:
            raise EventRoutingError(
                message="Failed to publish events batch",
                source="audit_service",
                event_type="batch",
                details={"error": str(e)}
            )