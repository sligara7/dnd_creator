"""Event publication manager for publishing events to the Message Hub."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set
from uuid import UUID, uuid4

from character_service.core.exceptions import (
    EventApplicationError,
    MessageHubError,
    MessageValidationError,
)
from character_service.domain.event import EventImpactService
from character_service.domain.messages import (
    CampaignEventMessage,
    CharacterStateMessage,
    ErrorMessage,
    Message,
    MessageType,
    ProgressEventMessage,
)
from character_service.domain.models import (
    CampaignEvent,
    Character,
    EventImpact,
    CharacterProgress,
)
from character_service.domain.state_publisher import StatePublisher
from character_service.infrastructure.messaging.hub_client import (
    MessageHubClient,
    MessageHubConfig,
)
from character_service.core.metrics import (
    track_message_publish,
    track_batch_size,
    track_retry,
    track_in_flight_with_type,
)


logger = logging.getLogger(__name__)


class PublicationConfig:
    """Configuration for event publication."""

    def __init__(
        self,
        batch_size: int = 100,
        batch_timeout: float = 1.0,
        retry_max_attempts: int = 3,
        retry_initial_delay: float = 0.1,
        retry_max_delay: float = 5.0,
        retry_jitter: float = 0.1,
    ) -> None:
        """Initialize configuration."""
        self.batch_size = batch_size
        self.batch_timeout = batch_timeout
        self.retry_max_attempts = retry_max_attempts
        self.retry_initial_delay = retry_initial_delay
        self.retry_max_delay = retry_max_delay
        self.retry_jitter = retry_jitter


class EventPublicationManager:
    """Manages publication of events to the Message Hub."""

    def __init__(
        self,
        state_publisher: StatePublisher,
        event_service: EventImpactService,
        config: PublicationConfig,
    ) -> None:
        """Initialize manager."""
        self._state_publisher = state_publisher
        self._event_service = event_service
        self.config = config
        self._batch_queue: asyncio.Queue[Message] = asyncio.Queue()
        self._in_flight: Set[UUID] = set()
        self._batch_task: Optional[asyncio.Task] = None
        self._retry_schedules: Dict[UUID, int] = {}

    async def start(self) -> None:
        """Start the publication manager."""
        if self._batch_task is None:
            self._batch_task = asyncio.create_task(self._process_batch_queue())
            logger.info("Event publication manager started")

    async def stop(self) -> None:
        """Stop the publication manager."""
        if self._batch_task is not None:
            self._batch_task.cancel()
            try:
                await self._batch_task
            except asyncio.CancelledError:
                pass
            self._batch_task = None
            logger.info("Event publication manager stopped")

    async def publish_event(self, event: CampaignEvent) -> None:
        """Publish a campaign event."""
        try:
            message = CampaignEventMessage(
                id=uuid4(),
                type=MessageType.CAMPAIGN_EVENT_CREATED,
                timestamp=datetime.utcnow(),
                event_id=event.id,
                character_id=event.character_id,
                event_type=event.event_type,
                event_data=event.event_data,
            )
            await self._enqueue_message(message)
        except Exception as e:
            logger.error(f"Failed to publish campaign event: {str(e)}", exc_info=True)
            raise EventApplicationError(f"Failed to publish event: {str(e)}")

    async def publish_character_update(
        self,
        character: Character,
        previous_data: Optional[Dict] = None,
    ) -> None:
        """Publish a character update."""
        try:
            message = await self._state_publisher.create_state_message(
                character,
                previous_data,
            )
            await self._enqueue_message(message)
        except Exception as e:
            logger.error(
                f"Failed to publish character update: {str(e)}",
                exc_info=True,
            )
            raise EventApplicationError(f"Failed to publish update: {str(e)}")

    async def publish_progress_update(
        self,
        progress: CharacterProgress,
        update_type: str,
    ) -> None:
        """Publish a progress update."""
        try:
            message = ProgressEventMessage(
                id=uuid4(),
                type=self._get_progress_message_type(update_type),
                timestamp=datetime.utcnow(),
                character_id=progress.character_id,
                progress_type=update_type,
                progress_data=self._get_progress_data(progress, update_type),
            )
            await self._enqueue_message(message)
        except Exception as e:
            logger.error(
                f"Failed to publish progress update: {str(e)}",
                exc_info=True,
            )
            raise EventApplicationError(f"Failed to publish progress: {str(e)}")

    async def _enqueue_message(self, message: Message) -> None:
        """Add a message to the publication queue."""
        if message.id in self._in_flight:
            raise MessageValidationError(f"Message {message.id} already in flight")

        await self._batch_queue.put(message)
        self._in_flight.add(message.id)
        logger.debug(f"Enqueued message {message.id} for publication")

    async def _process_batch_queue(self) -> None:
        """Process messages in batches."""
        while True:
            try:
                batch = await self._collect_batch()
                if not batch:
                    continue

                await self._publish_batch(batch)

                # Clear successful messages from in_flight set
                for message in batch:
                    self._in_flight.discard(message.id)
                    self._retry_schedules.pop(message.id, None)

            except Exception as e:
                logger.error(
                    f"Error processing message batch: {str(e)}",
                    exc_info=True,
                )
                # Messages will be retried in next batch
                await asyncio.sleep(0.1)

    async def _collect_batch(self) -> List[Message]:
        """Collect messages into a batch."""
        batch: List[Message] = []
        try:
            # Wait for first message
            first_message = await self._batch_queue.get()
            batch.append(first_message)

            # Try to get more messages
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
                        self._batch_queue.get(),
                        timeout=timeout,
                    )
                    batch.append(message)
                except asyncio.TimeoutError:
                    break

        except Exception as e:
            logger.error(f"Error collecting message batch: {str(e)}", exc_info=True)

        return batch

    async def _publish_batch(self, batch: List[Message]) -> None:
        """Publish a batch of messages with retry."""
        retry_batch = []
        error_messages = []

        # Track batch size
        track_batch_size(len(batch))

        for message in batch:
            retry_count = self._retry_schedules.get(message.id, 0)
            with track_message_publish(message.type.name):
                try:
                    # Check if message has exceeded retry attempts
                    if retry_count >= self.config.retry_max_attempts:
                        error_messages.append(
                            self._create_error_message(
                                message,
                                "Max retry attempts exceeded",
                                retry_count,
                            )
                        )
                        continue

                    # Calculate backoff delay
                    if retry_count > 0:
                        delay = min(
                            self.config.retry_initial_delay * (2 ** retry_count),
                            self.config.retry_max_delay,
                        )
                        await asyncio.sleep(delay)
                        track_retry(message.type.name)

                    # Track in-flight message
                    with track_in_flight_with_type(message.type.name):
                        # Attempt to publish
                        await self._state_publisher.publish_message(message)
                        logger.debug(f"Successfully published message {message.id}")

                except Exception as e:
                    logger.error(
                        f"Error publishing message {message.id}: {str(e)}",
                        exc_info=True,
                    )
                    # Add to retry batch or error messages
                    if retry_count < self.config.retry_max_attempts:
                        retry_batch.append(message)
                        self._retry_schedules[message.id] = retry_count + 1
                    else:
                        error_messages.append(
                            self._create_error_message(
                                message,
                                str(e),
                                retry_count,
                                should_retry=False,
                            )
                        )

        # Re-queue messages for retry
        for message in retry_batch:
            await self._batch_queue.put(message)

        # Publish error messages
        for error in error_messages:
            try:
                await self._state_publisher.publish_message(error)
            except Exception as e:
                logger.error(
                    f"Failed to publish error message: {str(e)}",
                    exc_info=True,
                )

    def _create_error_message(
        self,
        source_message: Message,
        error_message: str,
        retry_count: int,
        should_retry: bool = True,
    ) -> ErrorMessage:
        """Create an error message for a failed publication."""
        return ErrorMessage(
            id=uuid4(),
            type=MessageType.ERROR,
            timestamp=datetime.utcnow(),
            error_code="PUBLICATION_ERROR",
            error_message=error_message,
            source_message_id=source_message.id,
            retry_count=retry_count,
            should_retry=should_retry,
        )

    def _get_progress_message_type(self, update_type: str) -> MessageType:
        """Get message type for progress update."""
        type_map = {
            "experience": MessageType.EXPERIENCE_GAINED,
            "level": MessageType.LEVEL_CHANGED,
            "milestone": MessageType.MILESTONE_ACHIEVED,
            "achievement": MessageType.ACHIEVEMENT_UNLOCKED,
        }
        return type_map.get(update_type, MessageType.CHARACTER_UPDATED)

    def _get_progress_data(
        self,
        progress: CharacterProgress,
        update_type: str,
    ) -> Dict:
        """Get progress data for message."""
        if update_type == "experience":
            return {
                "experience_points": progress.experience_points,
                "current_level": progress.current_level,
            }
        elif update_type == "level":
            return {
                "previous_level": progress.previous_level,
                "current_level": progress.current_level,
                "level_updated_at": progress.level_updated_at.isoformat(),
            }
        elif update_type == "milestone":
            return {
                "milestones": progress.milestones,
            }
        elif update_type == "achievement":
            return {
                "achievements": progress.achievements,
            }
        return {}
