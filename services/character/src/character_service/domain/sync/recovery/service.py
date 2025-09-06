"""Sync recovery service for handling sync failures and network issues."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import CharacterNotFoundError
from character_service.domain.models import Character
from character_service.domain.sync.cache.client import StateCache
from character_service.domain.sync.exceptions import (
    SyncError,
    SyncRetryError,
    SyncStateError,
)
from character_service.domain.sync.models import (
    StateChange,
    StateVersion,
    SyncDirection,
    SyncError,
    SyncMetadata,
    SyncSubscription,
)
from character_service.domain.sync.repositories import (
    StateVersionRepository,
    SyncErrorRepository,
    SyncMetadataRepository,
    SyncSubscriptionRepository,
)
from character_service.domain.sync.utils import (
    detect_changes,
    diff_values,
    extract_value,
    set_value,
    with_retry,
    with_timeout,
)
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.infrastructure.repositories.character import CharacterRepository

logger = logging.getLogger(__name__)


class SyncRecoveryService:
    """Service for recovering from sync failures."""

    def __init__(
        self,
        db: AsyncSession,
        char_repository: CharacterRepository,
        state_repository: StateVersionRepository,
        metadata_repository: SyncMetadataRepository,
        error_repository: SyncErrorRepository,
        subscription_repository: SyncSubscriptionRepository,
        message_hub: MessageHubClient,
        cache: StateCache,
        retry_interval: int = 60,  # 1 minute between retries
        max_retries: int = 5,  # Maximum retry attempts
        recovery_batch_size: int = 10,  # Number of errors to process per batch
    ) -> None:
        """Initialize service.

        Args:
            db: Database session
            char_repository: Character repository
            state_repository: State version repository
            metadata_repository: Sync metadata repository
            error_repository: Error repository
            subscription_repository: Subscription repository
            message_hub: Message hub client
            cache: State cache
            retry_interval: Seconds between retry attempts
            max_retries: Maximum retry attempts
            recovery_batch_size: Errors to process per batch
        """
        self._db = db
        self._char_repo = char_repository
        self._state_repo = state_repository
        self._metadata_repo = metadata_repository
        self._error_repo = error_repository
        self._subscription_repo = subscription_repository
        self._message_hub = message_hub
        self._cache = cache
        self._retry_interval = retry_interval
        self._max_retries = max_retries
        self._batch_size = recovery_batch_size
        self._active_tasks: Set[asyncio.Task] = set()
        self._recovery_strategies = {
            "message_handling": self._recover_message_handling,
            "state_sync": self._recover_state_sync,
            "subscription": self._recover_subscription,
            "conflict": self._recover_conflict,
            "network": self._recover_network,
        }

    async def start(self) -> None:
        """Start recovery service."""
        # Start recovery loop
        recovery_task = asyncio.create_task(self._recovery_loop())
        self._active_tasks.add(recovery_task)
        recovery_task.add_done_callback(self._active_tasks.remove)

    async def stop(self) -> None:
        """Stop recovery service."""
        # Cancel all active tasks
        for task in self._active_tasks:
            task.cancel()
        # Wait for tasks to finish
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

    async def record_error(
        self,
        character_id: UUID,
        campaign_id: UUID,
        error_type: str,
        error_message: str,
        state_version: int,
        campaign_version: int,
        metadata: Optional[Dict] = None,
    ) -> None:
        """Record sync error for recovery.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            error_type: Type of error
            error_message: Error message
            state_version: Current state version
            campaign_version: Current campaign version
            metadata: Optional error metadata
        """
        error = SyncError(
            character_id=character_id,
            campaign_id=campaign_id,
            error_type=error_type,
            error_message=error_message,
            state_version=state_version,
            campaign_version=campaign_version,
            occurred_at=datetime.utcnow(),
            resolved=False,
            retry_count=0,
            metadata=metadata or {},
        )
        await self._error_repo.create(error)

    async def retry_error(
        self,
        error: SyncError,
    ) -> bool:
        """Retry sync error recovery.

        Args:
            error: Error to retry

        Returns:
            Whether retry was successful
        """
        try:
            # Get recovery strategy
            strategy = self._recovery_strategies.get(error.error_type)
            if not strategy:
                logger.warning(
                    "No recovery strategy for error type: %s",
                    error.error_type,
                )
                return False

            # Attempt recovery
            await strategy(error)

            # Mark error resolved
            error.resolved = True
            error.resolved_at = datetime.utcnow()
            await self._error_repo.update(error)

            return True

        except Exception as e:
            logger.error(
                "Error retrying sync error %s: %s",
                error.error_type,
                str(e),
                exc_info=True,
            )
            # Update retry count
            error.retry_count += 1
            error.last_retry = datetime.utcnow()
            await self._error_repo.update(error)

            return False

    async def _recovery_loop(self) -> None:
        """Background recovery loop."""
        while True:
            try:
                # Get unresolved errors for retry
                errors = await self._error_repo.list_for_retry(self._batch_size)
                for error in errors:
                    try:
                        # Check retry count
                        if error.retry_count >= self._max_retries:
                            logger.warning(
                                "Max retries exceeded for error %s",
                                error.error_type,
                            )
                            continue

                        # Check retry interval
                        if error.last_retry:
                            elapsed = datetime.utcnow() - error.last_retry
                            if elapsed.total_seconds() < self._retry_interval:
                                continue

                        # Attempt retry
                        await self.retry_error(error)

                    except Exception as e:
                        logger.error(
                            "Error in recovery loop: %s",
                            str(e),
                            exc_info=True,
                        )

            except Exception as e:
                logger.error("Recovery loop error: %s", str(e), exc_info=True)

            await asyncio.sleep(self._retry_interval)

    async def _recover_message_handling(self, error: SyncError) -> None:
        """Recover from message handling error.

        Args:
            error: Error to recover from
        """
        try:
            # Get character and metadata
            character = await self._char_repo.get(error.character_id)
            if not character:
                raise CharacterNotFoundError(
                    f"Character {error.character_id} not found"
                )

            metadata = await self._metadata_repo.get(
                error.character_id,
                error.campaign_id,
            )
            if not metadata:
                logger.warning(
                    "No sync metadata for character %s campaign %s",
                    error.character_id,
                    error.campaign_id,
                )
                return

            # Republish message
            await self._message_hub.publish(
                "character.state.sync",
                {
                    "character_id": str(error.character_id),
                    "campaign_id": str(error.campaign_id),
                    "character_version": metadata.character_version,
                    "campaign_version": metadata.campaign_version,
                    "state_data": character.character_data,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "Error recovering message handling: %s",
                str(e),
                exc_info=True,
            )
            raise

    async def _recover_state_sync(self, error: SyncError) -> None:
        """Recover from state sync error.

        Args:
            error: Error to recover from
        """
        try:
            # Get character and metadata
            character = await self._char_repo.get(error.character_id)
            if not character:
                raise CharacterNotFoundError(
                    f"Character {error.character_id} not found"
                )

            metadata = await self._metadata_repo.get(
                error.character_id,
                error.campaign_id,
            )
            if not metadata:
                return

            # Get latest state version
            latest_version = await self._state_repo.get_latest(error.character_id)
            if not latest_version:
                return

            # Check for version mismatch
            if latest_version.version != metadata.character_version:
                # Update metadata
                metadata.character_version = latest_version.version
                metadata.last_sync = datetime.utcnow()
                await self._metadata_repo.update(
                    error.character_id,
                    error.campaign_id,
                    metadata,
                )

                # Clear cache
                await self._cache.clear_character_cache(error.character_id)

        except Exception as e:
            logger.error(
                "Error recovering state sync: %s",
                str(e),
                exc_info=True,
            )
            raise

    async def _recover_subscription(self, error: SyncError) -> None:
        """Recover from subscription error.

        Args:
            error: Error to recover from
        """
        try:
            # Get subscription
            subscription = await self._subscription_repo.get(
                error.character_id,
                error.campaign_id,
            )
            if not subscription:
                return

            # Check subscription status
            if not subscription.active:
                # Reactivate subscription
                subscription.active = True
                subscription.last_update = datetime.utcnow()
                await self._subscription_repo.update(
                    error.character_id,
                    error.campaign_id,
                    subscription,
                )

                # Notify campaign
                await self._message_hub.publish(
                    "campaign.subscription.update",
                    {
                        "character_id": str(error.character_id),
                        "campaign_id": str(error.campaign_id),
                        "action": "subscribe",
                        "fields": subscription.fields,
                        "sync_mode": subscription.sync_mode.value,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

        except Exception as e:
            logger.error(
                "Error recovering subscription: %s",
                str(e),
                exc_info=True,
            )
            raise

    async def _recover_conflict(self, error: SyncError) -> None:
        """Recover from conflict error.

        Args:
            error: Error to recover from
        """
        try:
            # Get character state
            character = await self._char_repo.get(error.character_id)
            if not character:
                raise CharacterNotFoundError(
                    f"Character {error.character_id} not found"
                )

            # Get latest version
            latest_version = await self._state_repo.get_latest(error.character_id)
            if not latest_version:
                return

            # Get field value
            field_path = error.metadata.get("field_path")
            if not field_path:
                return

            local_value = extract_value(character.character_data, field_path)
            remote_value = error.metadata.get("remote_value")
            if not remote_value:
                return

            # Use remote value to resolve
            set_value(character.character_data, field_path, remote_value)

            # Update character
            await self._char_repo.update(character.id, character)

            # Create new version
            version = StateVersion(
                character_id=character.id,
                version=latest_version.version + 1,
                timestamp=datetime.utcnow(),
                parent_version=latest_version.version,
                changes=[
                    StateChange(
                        character_id=character.id,
                        field_path=field_path,
                        old_value=local_value,
                        new_value=remote_value,
                        timestamp=datetime.utcnow(),
                        source="conflict_resolution",
                    )
                ],
            )
            await self._state_repo.create(version)

        except Exception as e:
            logger.error(
                "Error recovering conflict: %s",
                str(e),
                exc_info=True,
            )
            raise

    async def _recover_network(self, error: SyncError) -> None:
        """Recover from network error.

        Args:
            error: Error to recover from
        """
        try:
            # Get character and metadata
            character = await self._char_repo.get(error.character_id)
            if not character:
                raise CharacterNotFoundError(
                    f"Character {error.character_id} not found"
                )

            metadata = await self._metadata_repo.get(
                error.character_id,
                error.campaign_id,
            )
            if not metadata:
                return

            # Clear cached data
            await self._cache.clear_character_cache(error.character_id)

            # Request state refresh from campaign
            await self._message_hub.publish(
                "campaign.state.refresh",
                {
                    "character_id": str(error.character_id),
                    "campaign_id": str(error.campaign_id),
                    "character_version": metadata.character_version,
                    "campaign_version": metadata.campaign_version,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )

        except Exception as e:
            logger.error(
                "Error recovering network: %s",
                str(e),
                exc_info=True,
            )
            raise
