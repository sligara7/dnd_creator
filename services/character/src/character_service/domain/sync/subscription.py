"""Subscription service for managing campaign state subscriptions."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import CharacterNotFoundError
from character_service.domain.models import Character
from character_service.domain.sync.exceptions import (
    SyncError,
    SyncSubscriptionError,
    SyncTimeoutError,
)
from character_service.domain.sync.models import (
    StateChange,
    SyncDirection,
    SyncMetadata,
    SyncState,
    SyncSubscription,
)
from character_service.domain.sync.repositories import (
    SyncMetadataRepository,
    SyncSubscriptionRepository,
)
from character_service.domain.sync.utils import with_retry, with_timeout
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.infrastructure.repositories.character import CharacterRepository

logger = logging.getLogger(__name__)


class SubscriptionService:
    """Service for managing campaign state subscriptions."""

    def __init__(
        self,
        db: AsyncSession,
        char_repository: CharacterRepository,
        subscription_repository: SyncSubscriptionRepository,
        metadata_repository: SyncMetadataRepository,
        message_hub: MessageHubClient,
        heartbeat_interval: int = 30,  # 30 seconds
        subscription_timeout: int = 300,  # 5 minutes
    ) -> None:
        """Initialize service.

        Args:
            db: Database session
            char_repository: Character repository
            subscription_repository: Subscription repository
            metadata_repository: Sync metadata repository
            message_hub: Message hub client
            heartbeat_interval: Heartbeat interval in seconds
            subscription_timeout: Subscription timeout in seconds
        """
        self._db = db
        self._char_repo = char_repository
        self._subscription_repo = subscription_repository
        self._metadata_repo = metadata_repository
        self._message_hub = message_hub
        self._heartbeat_interval = heartbeat_interval
        self._subscription_timeout = subscription_timeout
        self._active_tasks: Set[asyncio.Task] = set()
        self._active_subscriptions: Dict[Tuple[UUID, UUID], datetime] = {}

    async def start(self) -> None:
        """Start subscription service."""
        # Start heartbeat task
        heartbeat_task = asyncio.create_task(self._heartbeat_loop())
        self._active_tasks.add(heartbeat_task)
        heartbeat_task.add_done_callback(self._active_tasks.remove)

        # Start cleanup task
        cleanup_task = asyncio.create_task(self._cleanup_loop())
        self._active_tasks.add(cleanup_task)
        cleanup_task.add_done_callback(self._active_tasks.remove)

    async def stop(self) -> None:
        """Stop subscription service."""
        # Cancel all active tasks
        for task in self._active_tasks:
            task.cancel()
        # Wait for tasks to finish
        if self._active_tasks:
            await asyncio.gather(*self._active_tasks, return_exceptions=True)

    @with_retry()
    async def create_subscription(
        self,
        character_id: UUID,
        campaign_id: UUID,
        fields: Optional[List[str]] = None,
        sync_mode: SyncDirection = SyncDirection.BIDIRECTIONAL,
    ) -> SyncSubscription:
        """Create new campaign subscription.

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

        # Check if subscription already exists
        existing = await self._subscription_repo.get(character_id, campaign_id)
        if existing and existing.active:
            raise SyncSubscriptionError("Subscription already exists")

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

        # Track active subscription
        self._active_subscriptions[(character_id, campaign_id)] = datetime.utcnow()

        # Notify campaign service
        await self._send_subscription_notification(subscription, "subscribe")

        return subscription

    @with_retry()
    async def update_subscription(
        self,
        character_id: UUID,
        campaign_id: UUID,
        fields: Optional[List[str]] = None,
        sync_mode: Optional[SyncDirection] = None,
        active: Optional[bool] = None,
    ) -> Optional[SyncSubscription]:
        """Update existing subscription.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            fields: Optional list of fields to sync
            sync_mode: Optional sync direction mode
            active: Optional active state

        Returns:
            Updated subscription if successful
        """
        # Get existing subscription
        subscription = await self._subscription_repo.get(character_id, campaign_id)
        if not subscription:
            return None

        # Update fields
        if fields is not None:
            subscription.fields = fields
        if sync_mode is not None:
            subscription.sync_mode = sync_mode
        if active is not None:
            subscription.active = active

        # Update last modified
        subscription.last_update = datetime.utcnow()

        # Save changes
        subscription = await self._subscription_repo.update(
            character_id, campaign_id, subscription
        )

        # Update tracking
        if subscription.active:
            self._active_subscriptions[(character_id, campaign_id)] = datetime.utcnow()
        else:
            self._active_subscriptions.pop((character_id, campaign_id), None)

        # Notify campaign service
        if active is not None:
            await self._send_subscription_notification(
                subscription,
                "subscribe" if active else "unsubscribe",
            )

        return subscription

    @with_retry()
    async def delete_subscription(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> bool:
        """Delete subscription.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID

        Returns:
            Whether subscription was deleted
        """
        # Get subscription first
        subscription = await self._subscription_repo.get(character_id, campaign_id)
        if subscription and subscription.active:
            # Notify campaign service
            await self._send_subscription_notification(subscription, "unsubscribe")

        # Delete subscription and metadata
        success = await self._subscription_repo.delete(character_id, campaign_id)
        if success:
            await self._metadata_repo.delete(character_id, campaign_id)
            self._active_subscriptions.pop((character_id, campaign_id), None)

        return success

    @with_retry()
    async def list_active_subscriptions(
        self,
        character_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
    ) -> List[SyncSubscription]:
        """List active subscriptions.

        Args:
            character_id: Optional character ID filter
            campaign_id: Optional campaign ID filter

        Returns:
            List of active subscriptions
        """
        if character_id:
            return await self._subscription_repo.list_for_character(character_id)
        if campaign_id:
            return await self._subscription_repo.list_for_campaign(campaign_id)
        return await self._subscription_repo.list_active()

    async def _heartbeat_loop(self) -> None:
        """Background heartbeat loop."""
        while True:
            try:
                # Get active subscriptions
                subscriptions = await self._subscription_repo.list_active()
                for subscription in subscriptions:
                    try:
                        await self._send_heartbeat(subscription)
                    except Exception as e:
                        logger.error(
                            "Error sending heartbeat for subscription %s: %s",
                            subscription.character_id,
                            str(e),
                            exc_info=True,
                        )

            except Exception as e:
                logger.error("Heartbeat loop error: %s", str(e), exc_info=True)

            await asyncio.sleep(self._heartbeat_interval)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                # Find expired subscriptions
                now = datetime.utcnow()
                expired = [
                    (char_id, camp_id)
                    for (char_id, camp_id), last_seen in self._active_subscriptions.items()
                    if (now - last_seen).total_seconds() > self._subscription_timeout
                ]

                # Deactivate expired subscriptions
                for char_id, camp_id in expired:
                    try:
                        await self.update_subscription(
                            char_id,
                            camp_id,
                            active=False,
                        )
                    except Exception as e:
                        logger.error(
                            "Error deactivating subscription %s: %s",
                            char_id,
                            str(e),
                            exc_info=True,
                        )

            except Exception as e:
                logger.error("Cleanup loop error: %s", str(e), exc_info=True)

            await asyncio.sleep(self._subscription_timeout)

    @with_timeout(timeout=10)
    async def _send_subscription_notification(
        self,
        subscription: SyncSubscription,
        action: str,
    ) -> None:
        """Send subscription notification to campaign service.

        Args:
            subscription: Subscription to notify about
            action: Action being taken (subscribe/unsubscribe)
        """
        await self._message_hub.publish(
            "campaign.subscription.update",
            {
                "message_id": str(uuid4()),
                "character_id": str(subscription.character_id),
                "campaign_id": str(subscription.campaign_id),
                "action": action,
                "fields": subscription.fields,
                "sync_mode": subscription.sync_mode.value,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

    @with_timeout(timeout=5)
    async def _send_heartbeat(self, subscription: SyncSubscription) -> None:
        """Send subscription heartbeat.

        Args:
            subscription: Subscription to send heartbeat for
        """
        await self._message_hub.publish(
            "campaign.subscription.heartbeat",
            {
                "message_id": str(uuid4()),
                "character_id": str(subscription.character_id),
                "campaign_id": str(subscription.campaign_id),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        # Update last seen time
        self._active_subscriptions[
            (subscription.character_id, subscription.campaign_id)
        ] = datetime.utcnow()

    async def handle_subscription_response(
        self,
        message: Dict,
    ) -> None:
        """Handle subscription response from campaign service.

        Args:
            message: Response message
        """
        try:
            character_id = UUID(message["character_id"])
            campaign_id = UUID(message["campaign_id"])
            status = message["status"]

            if status == "accepted":
                # Update subscription state
                await self.update_subscription(
                    character_id,
                    campaign_id,
                    active=True,
                )
            elif status == "rejected":
                # Deactivate subscription
                await self.update_subscription(
                    character_id,
                    campaign_id,
                    active=False,
                )
                # Log rejection reason
                logger.warning(
                    "Subscription rejected: %s",
                    message.get("reason", "No reason provided"),
                )
            else:
                logger.warning("Unknown subscription status: %s", status)

        except Exception as e:
            logger.error(
                "Error handling subscription response: %s",
                str(e),
                exc_info=True,
            )
            raise

    async def handle_subscription_error(
        self,
        message: Dict,
    ) -> None:
        """Handle subscription error from campaign service.

        Args:
            message: Error message
        """
        try:
            character_id = UUID(message["character_id"])
            campaign_id = UUID(message["campaign_id"])
            error = message["error"]

            # Log error
            logger.error(
                "Subscription error for character %s campaign %s: %s",
                character_id,
                campaign_id,
                error,
            )

            # Deactivate subscription
            await self.update_subscription(
                character_id,
                campaign_id,
                active=False,
            )

        except Exception as e:
            logger.error(
                "Error handling subscription error: %s",
                str(e),
                exc_info=True,
            )
            raise
