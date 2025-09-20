"""Message publishing interfaces and implementations."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

from aio_pika import Message, connect_robust
from aio_pika.abc import AbstractChannel, AbstractConnection

from character_service.core.config import settings


class MessagePublisher(ABC):
    """Abstract base class for message publishing."""

    @abstractmethod
    async def publish_request(self, target_service: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a request event and await response."""
        pass

    @abstractmethod
    async def publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event without expecting response."""
        pass


class RabbitMQPublisher(MessagePublisher):
    """RabbitMQ implementation of message publisher."""

    def __init__(self) -> None:
        self.connection: Optional[AbstractConnection] = None
        self.channel: Optional[AbstractChannel] = None

    async def connect(self) -> None:
        """Establish connection to RabbitMQ."""
        if not self.connection:
            self.connection = await connect_robust(
                settings.RABBITMQ_URL,
                client_properties={
                    'connection_name': 'character_service'
                }
            )
            self.channel = await self.connection.channel()

    async def publish_request(self, target_service: str, event: Dict[str, Any]) -> Dict[str, Any]:
        """Publish a request event and await response."""
        await self.connect()
        assert self.channel is not None

        # Create a unique correlation ID for this request
        correlation_id = str(uuid4())

        # Declare response queue
        response_queue = await self.channel.declare_queue(
            name=f'character_service.response.{correlation_id}',
            auto_delete=True
        )

        # Publish request
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(event).encode(),
                content_type='application/json',
                correlation_id=correlation_id,
                reply_to=response_queue.name,
                headers={'service': 'character'}
            ),
            routing_key=f'{target_service}.requests'
        )

        # Wait for response
        async with response_queue.iterator() as queue_iter:
            async for message in queue_iter:
                async with message.process():
                    if message.correlation_id == correlation_id:
                        return json.loads(message.body.decode())

    async def publish_event(self, event_type: str, data: Dict[str, Any]) -> None:
        """Publish an event without expecting response."""
        await self.connect()
        assert self.channel is not None

        # Create event message
        message = {
            'type': event_type,
            'data': data,
            'timestamp': datetime.utcnow().isoformat(),
            'service': 'character'
        }

        # Publish to events exchange
        await self.channel.default_exchange.publish(
            Message(
                body=json.dumps(message).encode(),
                content_type='application/json',
                headers={'service': 'character'}
            ),
            routing_key='events'
        )

    async def close(self) -> None:
        """Close RabbitMQ connection."""
        if self.connection:
            await self.connection.close()

"""Message models for inter-service communication."""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, List, Optional
from uuid import UUID


class MessageType(Enum):
    """Types of messages that can be sent/received."""

    # Character state events
    CHARACTER_CREATED = auto()
    CHARACTER_UPDATED = auto()
    CHARACTER_DELETED = auto()
    CHARACTER_STATE_CHANGED = auto()

    # Campaign events
    CAMPAIGN_EVENT_CREATED = auto()
    CAMPAIGN_EVENT_APPLIED = auto()
    CAMPAIGN_EVENT_REVERTED = auto()

    # Progress events
    EXPERIENCE_GAINED = auto()
    LEVEL_CHANGED = auto()
    MILESTONE_ACHIEVED = auto()
    ACHIEVEMENT_UNLOCKED = auto()

    # System events
    STATE_SYNC_REQUESTED = auto()
    STATE_SYNC_COMPLETED = auto()
    HEALTH_CHECK = auto()
    ERROR = auto()


@dataclass
class Message:
    """Base message model."""

    id: UUID
    type: MessageType
    timestamp: datetime
    version: str
    metadata: Dict[str, Any]


@dataclass
class CharacterStateMessage(Message):
    """Message containing character state changes."""

    character_id: UUID
    state_version: int
    state_data: Dict[str, Any]
    previous_version: int
    state_changes: Dict[str, Any]


@dataclass
class CampaignEventMessage(Message):
    """Message about campaign events."""

    event_id: UUID
    character_id: UUID
    event_type: str
    event_data: Dict[str, Any]
    applied: bool
    reverted: bool
    impacts: List[Dict[str, Any]]


@dataclass
class ProgressEventMessage(Message):
    """Message about character progression."""

    character_id: UUID
    progress_type: str
    progress_data: Dict[str, Any]
    experience_points: int
    current_level: int


@dataclass
class StateSyncMessage(Message):
    """Message for state synchronization."""

    character_id: UUID
    requested_version: int
    from_timestamp: datetime
    include_history: bool
    force_sync: bool


@dataclass
class ErrorMessage(Message):
    """Message for error reporting."""

    error_code: str
    error_message: str
    source_message_id: UUID
    retry_count: int
    should_retry: bool
