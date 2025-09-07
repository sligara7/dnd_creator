"""Subscription manager for handling incoming campaign events."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from character_service.core.exceptions import (
    EventApplicationError,
    MessageHubError,
    MessageValidationError,
    StateConflictError,
)
from character_service.domain.event import EventImpactService
from character_service.domain.messages import (
    CampaignEventMessage,
    CharacterStateMessage,
    ErrorMessage,
    Message,
    MessageType,
    ProgressEventMessage,
    StateSyncMessage,
)
from character_service.domain.models import CampaignEvent, Character
from character_service.domain.progress import ProgressTrackingService
from character_service.domain.state_publisher import StatePublisher
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.core.metrics import track_event_handling
from character_service.domain.state_version import VersionManager


logger = logging.getLogger(__name__)


class SubscriptionManager:
    """Manages subscriptions to campaign events."""

    def __init__(
        self,
        message_hub: MessageHubClient,
        state_publisher: StatePublisher,
        event_service: EventImpactService,
        progress_service: ProgressTrackingService,
        version_manager: VersionManager,
    ) -> None:
        """Initialize subscription manager."""
        self._message_hub = message_hub
        self._state_publisher = state_publisher
        self._event_service = event_service
        self._progress_service = progress_service
        self._version_manager = version_manager
        self._processing_events: Set[UUID] = set()
        self._character_versions: Dict[UUID, int] = {}

    async def start(self) -> None:
        """Start the subscription manager."""
        self._setup_subscriptions()
        logger.info("Subscription manager started")

    def _setup_subscriptions(self) -> None:
        """Set up message type subscriptions."""
        # Campaign event handlers
        self._message_hub.subscribe(
            MessageType.CAMPAIGN_EVENT_CREATED,
            self._handle_campaign_event,
        )
        self._message_hub.subscribe(
            MessageType.CAMPAIGN_EVENT_APPLIED,
            self._handle_event_applied,
        )
        self._message_hub.subscribe(
            MessageType.CAMPAIGN_EVENT_REVERTED,
            self._handle_event_reverted,
        )

        # Character state handlers
        self._message_hub.subscribe(
            MessageType.CHARACTER_UPDATED,
            self._handle_character_update,
        )
        self._message_hub.subscribe(
            MessageType.STATE_SYNC_REQUESTED,
            self._handle_sync_request,
        )

        # Progress handlers
        self._message_hub.subscribe(
            MessageType.EXPERIENCE_GAINED,
            self._handle_experience_update,
        )
        self._message_hub.subscribe(
            MessageType.LEVEL_CHANGED,
            self._handle_level_update,
        )
        self._message_hub.subscribe(
            MessageType.MILESTONE_ACHIEVED,
            self._handle_milestone_update,
        )
        self._message_hub.subscribe(
            MessageType.ACHIEVEMENT_UNLOCKED,
            self._handle_achievement_update,
        )

    async def _handle_campaign_event(self, message: CampaignEventMessage) -> None:
        """Handle incoming campaign events."""
        with track_event_handling(message.event_type, "campaign_event"):
            try:
                # Check if we're already processing this event
                if message.event_id in self._processing_events:
                    logger.debug(f"Event {message.event_id} already being processed")
                    return

                self._processing_events.add(message.event_id)

                # Create local event record
                event = CampaignEvent(
                    id=message.event_id,
                    character_id=message.character_id,
                    event_type=message.event_type,
                    event_data=message.event_data,
                    impact_type=self._determine_impact_type(
                        message.event_type,
                        message.event_data,
                    ),
                    impact_magnitude=self._calculate_impact_magnitude(message.event_data),
                    timestamp=message.timestamp,
                )

                # Apply event
                impacts = await self._event_service.apply_event(event.id)

                if impacts:
                    # Publish state update if impacts were applied
                    character = await self._event_service._char_repo.get(message.character_id)
                    if character:
                        await self._state_publisher.publish_character_update(character)

            except Exception as e:
                logger.error(
                    f"Error processing campaign event {message.event_id}: {str(e)}",
                    exc_info=True,
                )
                await self._publish_error(message, str(e))
            finally:
                self._processing_events.discard(message.event_id)

    async def _handle_event_applied(self, message: CampaignEventMessage) -> None:
        """Handle event application confirmation."""
        try:
            # Update local event status
            event = await self._event_service.get_event(message.event_id)
            if event and not event.applied:
                await self._event_service.mark_event_applied(event.id)

        except Exception as e:
            logger.error(
                f"Error handling event applied {message.event_id}: {str(e)}",
                exc_info=True,
            )

    async def _handle_event_reverted(self, message: CampaignEventMessage) -> None:
        """Handle event reversion request."""
        try:
            # Revert local event
            await self._event_service.revert_event(message.event_id)

            # Publish state update after reversion
            character = await self._event_service._char_repo.get(message.character_id)
            if character:
                await self._state_publisher.publish_character_update(character)

        except Exception as e:
            logger.error(
                f"Error reverting event {message.event_id}: {str(e)}",
                exc_info=True,
            )
            await self._publish_error(message, str(e))

    async def _handle_character_update(self, message: CharacterStateMessage) -> None:
        """Handle character state updates."""
        with track_event_handling("character_update", "state_update"):
            try:
                # Check version for conflicts
                current_version = self._character_versions.get(message.character_id, 0)
                if message.state_version < current_version:
                    raise StateConflictError(
                        f"State conflict for character {message.character_id}: "
                        f"received version {message.state_version} < "
                        f"current version {current_version}"
                    )

                # Update local character state
                character = await self._event_service._char_repo.get(message.character_id)
                if character:
                    # Attempt to apply changes with base version if provided
                    base_version = getattr(message, "previous_version", None)
                    try:
                        new_version, had_conflict = await self._version_manager.apply_changes(
                            message.character_id,
                            message.state_data,
                            base_version=base_version,
                        )
                        self._character_versions[character.id] = new_version.version
                    except StateConflictError:
                        # Fall back to creating a new version with full state
                        character.character_data = message.state_data
                        await self._event_service._char_repo.update(character.id, character)
                        state_version = await self._version_manager.create_version(character, parent_version=None)
                        self._character_versions[character.id] = state_version.version

            except StateConflictError as e:
                logger.warning(str(e))
                await self._request_state_sync(message.character_id)

            except Exception as e:
                logger.error(
                    f"Error handling character update: {str(e)}",
                    exc_info=True,
                )

    async def _handle_sync_request(self, message: StateSyncMessage) -> None:
        """Handle state synchronization request."""
        try:
            character = await self._event_service._char_repo.get(message.character_id)
            if character:
                await self._state_publisher.publish_character_update(character)

        except Exception as e:
            logger.error(
                f"Error handling sync request: {str(e)}",
                exc_info=True,
            )

    async def _handle_experience_update(self, message: ProgressEventMessage) -> None:
        """Handle experience point updates."""
        with track_event_handling("experience", "progress_update"):
            try:
                amount = message.progress_data.get("amount", 0)
                source = message.progress_data.get("source", "unknown")
                reason = message.progress_data.get("reason", "")

                await self._progress_service.add_experience(
                    message.character_id,
                    amount,
                    source,
                    reason,
                )

            except Exception as e:
                logger.error(
                    f"Error handling experience update: {str(e)}",
                    exc_info=True,
                )
                await self._publish_error(message, str(e))

    async def _handle_level_update(self, message: ProgressEventMessage) -> None:
        """Handle level change updates."""
        with track_event_handling("level", "progress_update"):
            try:
                character = await self._event_service._char_repo.get(message.character_id)
                if character:
                    character.character_data["level"] = message.progress_data["new_level"]
                    await self._event_service._char_repo.update(character.id, character)

            except Exception as e:
                logger.error(
                    f"Error handling level update: {str(e)}",
                    exc_info=True,
                )

    async def _handle_milestone_update(self, message: ProgressEventMessage) -> None:
        """Handle milestone achievement updates."""
        with track_event_handling("milestone", "progress_update"):
            try:
                milestone_data = message.progress_data.get("milestone", {})
                await self._progress_service.add_milestone(
                    message.character_id,
                    milestone_data.get("title", ""),
                    milestone_data.get("description", ""),
                    milestone_data.get("type", "other"),
                    milestone_data.get("data"),
                )

            except Exception as e:
                logger.error(
                    f"Error handling milestone update: {str(e)}",
                    exc_info=True,
                )

    async def _handle_achievement_update(self, message: ProgressEventMessage) -> None:
        """Handle achievement updates."""
        with track_event_handling("achievement", "progress_update"):
            try:
                achievement_data = message.progress_data.get("achievement", {})
                await self._progress_service.add_achievement(
                    message.character_id,
                    achievement_data.get("title", ""),
                    achievement_data.get("description", ""),
                    achievement_data.get("type", "other"),
                    achievement_data.get("data"),
                )

            except Exception as e:
                logger.error(
                    f"Error handling achievement update: {str(e)}",
                    exc_info=True,
                )

    async def _request_state_sync(self, character_id: UUID) -> None:
        """Request state synchronization for a character."""
        message = StateSyncMessage(
            id=uuid4(),
            type=MessageType.STATE_SYNC_REQUESTED,
            timestamp=datetime.utcnow(),
            character_id=character_id,
            requested_version=self._character_versions.get(character_id, 0),
            force_sync=True,
        )
        await self._state_publisher.publish_message(message)

    async def _publish_error(self, source_message: Message, error: str) -> None:
        """Publish an error message."""
        try:
            error_message = ErrorMessage(
                id=uuid4(),
                type=MessageType.ERROR,
                timestamp=datetime.utcnow(),
                error_code="SUBSCRIPTION_ERROR",
                error_message=error,
                source_message_id=source_message.id,
                retry_count=0,
                should_retry=False,
            )
            await self._state_publisher.publish_message(error_message)
        except Exception as e:
            logger.error(f"Error publishing error message: {str(e)}", exc_info=True)

    def _determine_impact_type(self, event_type: str, event_data: Dict[str, Any]) -> str:
        """Determine impact type from event type and data."""
        impact_types = {
            "combat": "hit_points",
            "rest": "hit_points",
            "quest": "experience",
            "training": "ability_score",
            "story": "milestone",
        }
        return impact_types.get(event_type, "other")

    def _calculate_impact_magnitude(self, event_data: Dict[str, Any]) -> int:
        """Calculate impact magnitude from event data."""
        if "damage" in event_data:
            return -event_data["damage"]
        elif "healing" in event_data:
            return event_data["healing"]
        elif "experience" in event_data:
            return event_data["experience"]
        return 0
