"""Message Hub client for inter-service communication."""
import asyncio
import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional
from uuid import UUID, uuid4

import aiohttp
from pydantic_settings import BaseSettings
from pydantic import Field

from character_service.core.config import Settings
from character_service.core.exceptions import MessageHubError
from character_service.domain.messages import (
    CampaignEventMessage,
    CharacterStateMessage,
    ErrorMessage,
    Message,
    MessageType,
    ProgressEventMessage,
    StateSyncMessage,
)


class HealthStatus(Enum):
    """Health status of the message hub connection."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


class MessageHubConfig(BaseSettings):
    """Message Hub configuration."""

    hub_url: str = "http://message-hub:8200"
    service_name: str = "character-service"
    service_id: UUID = Field(default_factory=uuid4)
    connect_timeout: float = 5.0
    request_timeout: float = 10.0
    health_check_interval: float = 30.0
    retry_initial_delay: float = 1.0
    retry_max_delay: float = 60.0
    retry_max_attempts: int = 5
    batch_size: int = 100
    batch_timeout: float = 1.0


class MessageHubClient:
    """Client for interacting with the Message Hub service."""

    def __init__(
        self,
        config: MessageHubConfig,
        settings: Settings,
    ) -> None:
        """Initialize the client."""
        self.config = config
        self.settings = settings
        self._session: Optional[aiohttp.ClientSession] = None
        self._health_status = HealthStatus.UNKNOWN
        self._health_check_task: Optional[asyncio.Task] = None
        self._message_handlers: Dict[MessageType, List[Callable]] = {}
        self._outgoing_queue: asyncio.Queue = asyncio.Queue()
        self._batch_task: Optional[asyncio.Task] = None
        self._connected = asyncio.Event()

    async def connect(self) -> None:
        """Connect to the Message Hub service."""
        if self._session is not None:
            await self.disconnect()

        self._session = aiohttp.ClientSession(
            base_url=self.config.hub_url,
            timeout=aiohttp.ClientTimeout(
                connect=self.config.connect_timeout,
                total=self.config.request_timeout,
            ),
        )

        # Register with the Message Hub
        try:
            await self._register_service()
            self._connected.set()
            self._health_status = HealthStatus.HEALTHY
        except Exception as e:
            self._health_status = HealthStatus.UNHEALTHY
            raise MessageHubError(f"Failed to connect to Message Hub: {str(e)}")

        # Start background tasks
        self._health_check_task = asyncio.create_task(self._health_check_loop())
        self._batch_task = asyncio.create_task(self._process_outgoing_queue())

    async def disconnect(self) -> None:
        """Disconnect from the Message Hub service."""
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass
            self._health_check_task = None

        if self._batch_task:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None

        if self._session:
            await self._session.close()
            self._session = None

        self._connected.clear()
        self._health_status = HealthStatus.UNKNOWN

    async def publish(self, message: Message) -> None:
        """Publish a message to the Message Hub."""
        await self._connected.wait()
        await self._outgoing_queue.put(message)

    def subscribe(
        self,
        message_type: MessageType,
        handler: Callable[[Message], None],
    ) -> None:
        """Subscribe to a specific message type."""
        if message_type not in self._message_handlers:
            self._message_handlers[message_type] = []
        self._message_handlers[message_type].append(handler)

    def unsubscribe(
        self,
        message_type: MessageType,
        handler: Callable[[Message], None],
    ) -> None:
        """Unsubscribe from a specific message type."""
        if message_type in self._message_handlers:
            handlers = self._message_handlers[message_type]
            if handler in handlers:
                handlers.remove(handler)
            if not handlers:
                del self._message_handlers[message_type]

    @property
    def health_status(self) -> HealthStatus:
        """Get the current health status."""
        return self._health_status

    async def _register_service(self) -> None:
        """Register this service with the Message Hub."""
        if not self._session:
            raise MessageHubError("Client session not initialized")

        registration_data = {
            "service_name": self.config.service_name,
            "service_id": str(self.config.service_id),
            "message_types": [mt.name for mt in MessageType],
        }

        try:
            async with self._session.post(
                "/api/v1/register",
                json=registration_data,
            ) as response:
                if response.status != 200:
                    raise MessageHubError(
                        f"Failed to register service: {response.status}"
                    )
                response_data = await response.json()
                return response_data["service_token"]
        except aiohttp.ClientError as e:
            raise MessageHubError(f"Registration request failed: {str(e)}")

    async def _health_check_loop(self) -> None:
        """Periodically check Message Hub health."""
        while True:
            try:
                if not self._session:
                    self._health_status = HealthStatus.UNHEALTHY
                    break

                async with self._session.get("/health") as response:
                    if response.status == 200:
                        self._health_status = HealthStatus.HEALTHY
                    else:
                        self._health_status = HealthStatus.DEGRADED
            except Exception:
                self._health_status = HealthStatus.UNHEALTHY

            await asyncio.sleep(self.config.health_check_interval)

    async def _process_outgoing_queue(self) -> None:
        """Process outgoing messages in batches."""
        while True:
            batch: List[Message] = []
            try:
                # Wait for first message
                message = await self._outgoing_queue.get()
                batch.append(message)

                # Try to get more messages up to batch size or timeout
                batch_deadline = (
                    datetime.utcnow() +
                    timedelta(seconds=self.config.batch_timeout)
                )

                while len(batch) < self.config.batch_size:
                    timeout = (batch_deadline - datetime.utcnow()).total_seconds()
                    if timeout <= 0:
                        break

                    try:
                        message = await asyncio.wait_for(
                            self._outgoing_queue.get(),
                            timeout=timeout,
                        )
                        batch.append(message)
                    except asyncio.TimeoutError:
                        break

                # Send batch
                await self._send_message_batch(batch)
            except Exception as e:
                self._health_status = HealthStatus.DEGRADED
                # Log error and retry individual messages
                for message in batch:
                    await self._retry_message(message)

            # Mark all messages in batch as done
            for _ in batch:
                self._outgoing_queue.task_done()

    async def _send_message_batch(self, messages: List[Message]) -> None:
        """Send a batch of messages to the Message Hub."""
        if not self._session:
            raise MessageHubError("Client session not initialized")

        batch_data = [
            {
                "id": str(msg.id),
                "type": msg.type.name,
                "timestamp": msg.timestamp.isoformat(),
                "version": msg.version,
                "metadata": msg.metadata,
                "data": self._serialize_message(msg),
            }
            for msg in messages
        ]

        try:
            async with self._session.post(
                "/api/v1/messages/batch",
                json=batch_data,
            ) as response:
                if response.status != 200:
                    raise MessageHubError(
                        f"Failed to send message batch: {response.status}"
                    )
        except aiohttp.ClientError as e:
            raise MessageHubError(f"Message batch request failed: {str(e)}")

    async def _retry_message(
        self,
        message: Message,
        retry_count: int = 0,
    ) -> None:
        """Retry sending a failed message with exponential backoff."""
        if retry_count >= self.config.retry_max_attempts:
            # Create and send error message
            error_msg = ErrorMessage(
                id=uuid4(),
                type=MessageType.ERROR,
                timestamp=datetime.utcnow(),
                error_code="RETRY_EXHAUSTED",
                error_message=f"Failed to send message after {retry_count} retries",
                source_message_id=message.id,
                retry_count=retry_count,
                should_retry=False,
            )
            await self.publish(error_msg)
            return

        # Calculate delay with exponential backoff
        delay = min(
            self.config.retry_initial_delay * (2 ** retry_count),
            self.config.retry_max_delay,
        )
        await asyncio.sleep(delay)

        try:
            await self.publish(message)
        except Exception:
            await self._retry_message(message, retry_count + 1)

    def _serialize_message(self, message: Message) -> Dict[str, Any]:
        """Serialize a message for transmission."""
        if isinstance(message, CharacterStateMessage):
            return {
                "character_id": str(message.character_id),
                "state_version": message.state_version,
                "state_data": message.state_data,
                "previous_version": message.previous_version,
                "state_changes": message.state_changes,
            }
        elif isinstance(message, CampaignEventMessage):
            return {
                "event_id": str(message.event_id),
                "character_id": str(message.character_id),
                "event_type": message.event_type,
                "event_data": message.event_data,
                "applied": message.applied,
                "reverted": message.reverted,
                "impacts": message.impacts,
            }
        elif isinstance(message, ProgressEventMessage):
            return {
                "character_id": str(message.character_id),
                "progress_type": message.progress_type,
                "progress_data": message.progress_data,
                "experience_points": message.experience_points,
                "current_level": message.current_level,
            }
        elif isinstance(message, StateSyncMessage):
            return {
                "character_id": str(message.character_id),
                "requested_version": message.requested_version,
                "from_timestamp": (
                    message.from_timestamp.isoformat()
                    if message.from_timestamp
                    else None
                ),
                "include_history": message.include_history,
                "force_sync": message.force_sync,
            }
        elif isinstance(message, ErrorMessage):
            return {
                "error_code": message.error_code,
                "error_message": message.error_message,
                "source_message_id": (
                    str(message.source_message_id)
                    if message.source_message_id
                    else None
                ),
                "retry_count": message.retry_count,
                "should_retry": message.should_retry,
            }
        else:
            raise ValueError(f"Unknown message type: {type(message)}")

    def _deserialize_message(
        self,
        message_type: MessageType,
        data: Dict[str, Any],
    ) -> Message:
        """Deserialize a received message."""
        common_args = {
            "id": UUID(data["id"]),
            "type": message_type,
            "timestamp": datetime.fromisoformat(data["timestamp"]),
            "version": data.get("version", "1.0"),
            "metadata": data.get("metadata", {}),
        }

        message_data = data.get("data", {})

        if message_type in [
            MessageType.CHARACTER_CREATED,
            MessageType.CHARACTER_UPDATED,
            MessageType.CHARACTER_STATE_CHANGED,
        ]:
            return CharacterStateMessage(
                character_id=UUID(message_data["character_id"]),
                state_version=message_data["state_version"],
                state_data=message_data["state_data"],
                previous_version=message_data.get("previous_version"),
                state_changes=message_data.get("state_changes"),
                **common_args,
            )
        elif message_type in [
            MessageType.CAMPAIGN_EVENT_CREATED,
            MessageType.CAMPAIGN_EVENT_APPLIED,
            MessageType.CAMPAIGN_EVENT_REVERTED,
        ]:
            return CampaignEventMessage(
                event_id=UUID(message_data["event_id"]),
                character_id=UUID(message_data["character_id"]),
                event_type=message_data["event_type"],
                event_data=message_data["event_data"],
                applied=message_data.get("applied", False),
                reverted=message_data.get("reverted", False),
                impacts=message_data.get("impacts", []),
                **common_args,
            )
        elif message_type in [
            MessageType.EXPERIENCE_GAINED,
            MessageType.LEVEL_CHANGED,
            MessageType.MILESTONE_ACHIEVED,
            MessageType.ACHIEVEMENT_UNLOCKED,
        ]:
            return ProgressEventMessage(
                character_id=UUID(message_data["character_id"]),
                progress_type=message_data["progress_type"],
                progress_data=message_data["progress_data"],
                experience_points=message_data.get("experience_points"),
                current_level=message_data.get("current_level"),
                **common_args,
            )
        elif message_type in [
            MessageType.STATE_SYNC_REQUESTED,
            MessageType.STATE_SYNC_COMPLETED,
        ]:
            return StateSyncMessage(
                character_id=UUID(message_data["character_id"]),
                requested_version=message_data.get("requested_version"),
                from_timestamp=(
                    datetime.fromisoformat(message_data["from_timestamp"])
                    if message_data.get("from_timestamp")
                    else None
                ),
                include_history=message_data.get("include_history", False),
                force_sync=message_data.get("force_sync", False),
                **common_args,
            )
        elif message_type == MessageType.ERROR:
            return ErrorMessage(
                error_code=message_data["error_code"],
                error_message=message_data["error_message"],
                source_message_id=(
                    UUID(message_data["source_message_id"])
                    if message_data.get("source_message_id")
                    else None
                ),
                retry_count=message_data.get("retry_count", 0),
                should_retry=message_data.get("should_retry", True),
                **common_args,
            )
        else:
            raise ValueError(f"Unknown message type: {message_type}")
