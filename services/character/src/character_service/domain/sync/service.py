"""State synchronization service."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import CharacterNotFoundError
from character_service.domain.models import Character
from character_service.domain.sync.exceptions import (
    SyncConflictError,
    SyncError,
    SyncStateError,
    SyncTimeoutError,
)
from character_service.domain.sync.models import (
    FieldSyncMode,
    StateChange,
    StateVersion,
    SyncConfiguration,
    SyncConflict,
    SyncDirection,
    SyncMessage,
    SyncMetadata,
    SyncState,
    SyncSubscription,
)
from character_service.domain.sync.repositories import (
    StateVersionRepository,
    SyncConflictRepository,
    SyncErrorRepository,
    SyncMessageRepository,
    SyncMetadataRepository,
    SyncSubscriptionRepository,
)
from character_service.domain.sync.utils import (
    detect_changes,
    diff_values,
    extract_value,
    group_changes,
    merge_values,
    reconcile_changes,
    set_value,
    with_retry,
    with_timeout,
)
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.infrastructure.repositories.character import CharacterRepository

logger = logging.getLogger(__name__)


class SynchronizationService:
    """Service for managing state synchronization with campaigns."""

    def __init__(
        self,
        db: AsyncSession,
        char_repository: CharacterRepository,
        state_repository: StateVersionRepository,
        metadata_repository: SyncMetadataRepository,
        message_repository: SyncMessageRepository,
        conflict_repository: SyncConflictRepository,
        error_repository: SyncErrorRepository,
        subscription_repository: SyncSubscriptionRepository,
        message_hub: MessageHubClient,
        sync_interval: int = 5,  # 5 seconds
        message_timeout: int = 10,  # 10 seconds
    ) -> None:
        """Initialize service.

        Args:
            db: Database session
            char_repository: Character repository
            state_repository: State version repository
            metadata_repository: Sync metadata repository
            message_repository: Sync message repository
            conflict_repository: Sync conflict repository
            error_repository: Sync error repository
            subscription_repository: Sync subscription repository
            message_hub: Message hub client
            sync_interval: Sync interval in seconds
            message_timeout: Message timeout in seconds
        """
        self._db = db
        self._char_repo = char_repository
        self._state_repo = state_repository
        self._metadata_repo = metadata_repository
        self._message_repo = message_repository
        self._conflict_repo = conflict_repository
        self._error_repo = error_repository
        self._subscription_repo = subscription_repository
        self._message_hub = message_hub
        self._sync_interval = sync_interval
        self._message_timeout = message_timeout
        self._active_tasks: Set[asyncio.Task] = set()

    async def start(self) -> None:
        """Start synchronization service."""
        # Start background sync task
        sync_task = asyncio.create_task(self._sync_loop())
        self._active_tasks.add(sync_task)
        sync_task.add_done_callback(self._active_tasks.remove)

    async def stop(self) -> None:
        """Stop synchronization service."""
        # Cancel all active tasks
        for task in self._active_tasks:
            task.cancel()
        # Wait for tasks to finish
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

    async def subscribe_to_campaign(
        self,
        character_id: UUID,
        campaign_id: UUID,
        fields: Optional[List[str]] = None,
        sync_mode: SyncDirection = SyncDirection.BIDIRECTIONAL,
    ) -> SyncSubscription:
        """Subscribe to campaign state updates.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            fields: Optional list of fields to sync
            sync_mode: Sync direction mode

        Returns:
            New subscription
        """
        # Verify character exists
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Create subscription
        subscription = SyncSubscription(
            character_id=character_id,
            campaign_id=campaign_id,
            fields=fields or ["*"],
            sync_mode=sync_mode,
            active=True,
            created_at=datetime.utcnow(),
        )
        subscription = await self._subscription_repo.create(subscription)

        # Initialize sync metadata
        metadata = SyncMetadata(
            character_id=character_id,
            campaign_id=campaign_id,
            character_version=0,
            campaign_version=0,
            last_sync=datetime.utcnow(),
        )
        await self._metadata_repo.create(metadata)

        return subscription

    async def unsubscribe_from_campaign(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> None:
        """Unsubscribe from campaign state updates.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
        """
        # Delete subscription and metadata
        await self._subscription_repo.delete(character_id, campaign_id)
        await self._metadata_repo.delete(character_id, campaign_id)

    async def push_changes(
        self,
        character_id: UUID,
        changes: List[StateChange],
    ) -> None:
        """Push character state changes.

        Args:
            character_id: Character ID
            changes: List of state changes
        """
        # Get active subscriptions
        subscriptions = await self._subscription_repo.list_for_character(character_id)
        if not subscriptions:
            return  # No active subscriptions

        # Group changes by field
        grouped = group_changes(changes)

        # Create messages for each subscription
        messages: List[SyncMessage] = []
        for subscription in subscriptions:
            # Filter changes by subscription fields
            sub_changes = []
            for field, field_changes in grouped.items():
                if any(self._field_matches_pattern(field, p) for p in subscription.fields):
                    sub_changes.extend(field_changes)

            if sub_changes:
                # Get latest versions
                metadata = await self._metadata_repo.get(
                    character_id, subscription.campaign_id
                )
                if not metadata:
                    continue

                # Create message
                message = SyncMessage(
                    message_id=uuid4(),
                    character_id=character_id,
                    campaign_id=subscription.campaign_id,
                    character_version=metadata.character_version,
                    campaign_version=metadata.campaign_version,
                    changes=sub_changes,
                    timestamp=datetime.utcnow(),
                )
                messages.append(message)

        # Store and publish messages
        for message in messages:
            await self._message_repo.create(message)
            await self._publish_message(message)

    async def handle_campaign_message(
        self,
        message: SyncMessage,
    ) -> None:
        """Handle incoming campaign state message.

        Args:
            message: Incoming sync message
        """
        try:
            # Get character and metadata
            character = await self._char_repo.get(message.character_id)
            if not character:
                raise CharacterNotFoundError(
                    f"Character {message.character_id} not found"
                )

            metadata = await self._metadata_repo.get(
                message.character_id, message.campaign_id
            )
            if not metadata:
                logger.warning(
                    "No sync metadata for character %s campaign %s",
                    message.character_id,
                    message.campaign_id,
                )
                return

            # Apply changes
            await self._apply_changes(character, message.changes)

            # Update metadata
            metadata.campaign_version = message.campaign_version
            metadata.last_sync = datetime.utcnow()
            await self._metadata_repo.update(
                message.character_id, message.campaign_id, metadata
            )

        except Exception as e:
            logger.error(
                "Error handling campaign message: %s",
                str(e),
                exc_info=True,
            )
            # Store error
            error = SyncError(
                character_id=message.character_id,
                campaign_id=message.campaign_id,
                error_type="message_handling",
                error_message=str(e),
                state_version=metadata.character_version if metadata else 0,
                campaign_version=message.campaign_version,
            )
            await self._error_repo.create(error)

    async def _sync_loop(self) -> None:
        """Background sync loop."""
        while True:
            try:
                # Get active subscriptions
                subscriptions = await self._subscription_repo.list_active()
                for subscription in subscriptions:
                    try:
                        await self._sync_subscription(subscription)
                    except Exception as e:
                        logger.error(
                            "Error syncing subscription %s: %s",
                            subscription.character_id,
                            str(e),
                            exc_info=True,
                        )

            except Exception as e:
                logger.error("Sync loop error: %s", str(e), exc_info=True)

            await asyncio.sleep(self._sync_interval)

    @with_retry()
    async def _sync_subscription(
        self,
        subscription: SyncSubscription,
    ) -> None:
        """Sync single subscription.

        Args:
            subscription: Subscription to sync
        """
        # Get character and metadata
        character = await self._char_repo.get(subscription.character_id)
        if not character:
            logger.warning(
                "Character %s not found for subscription",
                subscription.character_id,
            )
            return

        metadata = await self._metadata_repo.get(
            subscription.character_id, subscription.campaign_id
        )
        if not metadata:
            logger.warning(
                "No sync metadata for character %s campaign %s",
                subscription.character_id,
                subscription.campaign_id,
            )
            return

        # Check for changes since last sync
        latest_version = await self._state_repo.get_latest(subscription.character_id)
        if latest_version and latest_version.version > metadata.character_version:
            # Extract changes
            changes = []
            versions = await self._state_repo.list_versions(
                subscription.character_id,
                start_version=metadata.character_version + 1,
            )
            for version in versions:
                changes.extend(version.changes)

            # Filter changes by subscription fields
            filtered_changes = [
                c
                for c in changes
                if any(
                    self._field_matches_pattern(c.field_path, p)
                    for p in subscription.fields
                )
            ]

            if filtered_changes:
                # Create and send message
                message = SyncMessage(
                    message_id=uuid4(),
                    character_id=subscription.character_id,
                    campaign_id=subscription.campaign_id,
                    character_version=latest_version.version,
                    campaign_version=metadata.campaign_version,
                    changes=filtered_changes,
                    timestamp=datetime.utcnow(),
                )
                await self._message_repo.create(message)
                await self._publish_message(message)

                # Update metadata
                metadata.character_version = latest_version.version
                metadata.last_sync = datetime.utcnow()
                await self._metadata_repo.update(
                    subscription.character_id, subscription.campaign_id, metadata
                )

    async def _apply_changes(
        self,
        character: Character,
        changes: List[StateChange],
    ) -> None:
        """Apply state changes to character.

        Args:
            character: Character to update
            changes: Changes to apply
        """
        # Get current state version
        current_version = await self._state_repo.get_latest(character.id)
        base_state = character.character_data.copy()

        try:
            # Apply changes
            new_state, applied = reconcile_changes(
                changes, base_state, character.character_data
            )

            if applied:
                # Update character
                character.character_data = new_state
                await self._char_repo.update(character.id, character)

                # Create new version
                version = StateVersion(
                    version=(current_version.version + 1) if current_version else 1,
                    timestamp=datetime.utcnow(),
                    parent_version=current_version.version if current_version else None,
                    changes=applied,
                )
                await self._state_repo.create(version)

        except Exception as e:
            logger.error(
                "Error applying changes to character %s: %s",
                character.id,
                str(e),
                exc_info=True,
            )
            raise SyncError(f"Failed to apply changes: {str(e)}")

    @with_timeout(timeout=10)
    async def _publish_message(self, message: SyncMessage) -> None:
        """Publish sync message.

        Args:
            message: Message to publish
        """
        await self._message_hub.publish(
            "character.state.sync",
            {
                "message_id": str(message.message_id),
                "character_id": str(message.character_id),
                "campaign_id": str(message.campaign_id),
                "character_version": message.character_version,
                "campaign_version": message.campaign_version,
                "changes": [
                    {
                        "field_path": c.field_path,
                        "old_value": c.old_value,
                        "new_value": c.new_value,
                        "timestamp": c.timestamp.isoformat(),
                        "source": c.source,
                        "sync_mode": c.sync_mode.value,
                    }
                    for c in message.changes
                ],
                "timestamp": message.timestamp.isoformat(),
                "metadata": message.metadata,
            },
        )

    def _field_matches_pattern(self, field: str, pattern: str) -> bool:
        """Check if field matches subscription pattern.

        Args:
            field: Field path to check
            pattern: Pattern to match against

        Returns:
            Whether field matches pattern
        """
        if pattern == "*":
            return True
        if pattern.endswith(".*"):
            return field.startswith(pattern[:-2])
        return field == pattern
