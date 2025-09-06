"""Cached repository implementations for state synchronization."""
import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import CacheError
from character_service.domain.models import Character
from character_service.domain.sync.cache.client import StateCache
from character_service.domain.sync.exceptions import (
    SyncConflictError,
    SyncError,
)
from character_service.domain.sync.models import (
    StateVersion,
    SyncConflict,
    SyncMetadata,
    SyncSubscription,
)
from character_service.domain.sync.repositories import (
    StateVersionRepository,
    SyncConflictRepository,
    SyncMetadataRepository,
    SyncSubscriptionRepository,
)

logger = logging.getLogger(__name__)


class CachedStateVersionRepository(StateVersionRepository):
    """Cached implementation of state version repository."""

    def __init__(
        self,
        db: AsyncSession,
        repository: StateVersionRepository,
        cache: StateCache,
    ) -> None:
        """Initialize repository.

        Args:
            db: Database session
            repository: Base repository implementation
            cache: State cache
        """
        self._db = db
        self._repository = repository
        self._cache = cache

    async def create(self, version: StateVersion) -> StateVersion:
        """Create new state version.

        Args:
            version: State version to create

        Returns:
            Created state version
        """
        result = await self._repository.create(version)
        # Clear character state cache since it's changed
        await self._cache.delete_state(version.character_id)
        return result

    async def get(
        self,
        character_id: UUID,
        version: int,
    ) -> Optional[StateVersion]:
        """Get state version by character and version number.

        Args:
            character_id: Character ID
            version: Version number

        Returns:
            State version if found
        """
        return await self._repository.get(character_id, version)

    async def get_latest(
        self,
        character_id: UUID,
    ) -> Optional[StateVersion]:
        """Get latest state version for a character.

        Args:
            character_id: Character ID

        Returns:
            Latest state version if found
        """
        return await self._repository.get_latest(character_id)

    async def get_by_campaign_version(
        self,
        character_id: UUID,
        campaign_version: int,
    ) -> List[StateVersion]:
        """Get all versions associated with a campaign version.

        Args:
            character_id: Character ID
            campaign_version: Campaign version number

        Returns:
            List of state versions
        """
        return await self._repository.get_by_campaign_version(
            character_id,
            campaign_version,
        )

    async def list_versions(
        self,
        character_id: UUID,
        start_version: Optional[int] = None,
        end_version: Optional[int] = None,
        limit: int = 100,
    ) -> List[StateVersion]:
        """List versions for a character in range.

        Args:
            character_id: Character ID
            start_version: Optional start version
            end_version: Optional end version
            limit: Maximum number of versions to return

        Returns:
            List of state versions
        """
        return await self._repository.list_versions(
            character_id,
            start_version,
            end_version,
            limit,
        )


class CachedSyncMetadataRepository(SyncMetadataRepository):
    """Cached implementation of sync metadata repository."""

    def __init__(
        self,
        db: AsyncSession,
        repository: SyncMetadataRepository,
        cache: StateCache,
    ) -> None:
        """Initialize repository.

        Args:
            db: Database session
            repository: Base repository implementation
            cache: State cache
        """
        self._db = db
        self._repository = repository
        self._cache = cache

    async def create(self, metadata: SyncMetadata) -> SyncMetadata:
        """Create new sync metadata.

        Args:
            metadata: Sync metadata to create

        Returns:
            Created metadata
        """
        result = await self._repository.create(metadata)
        await self._cache.set_metadata(result)
        return result

    async def get(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> Optional[SyncMetadata]:
        """Get sync metadata for character/campaign pair.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID

        Returns:
            Sync metadata if found
        """
        # Try cache first
        cached = await self._cache.get_metadata(character_id, campaign_id)
        if cached:
            return cached

        # Get from repository and cache
        result = await self._repository.get(character_id, campaign_id)
        if result:
            await self._cache.set_metadata(result)
        return result

    async def update(
        self,
        character_id: UUID,
        campaign_id: UUID,
        metadata: SyncMetadata,
    ) -> Optional[SyncMetadata]:
        """Update sync metadata.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            metadata: Updated metadata

        Returns:
            Updated metadata if successful
        """
        result = await self._repository.update(character_id, campaign_id, metadata)
        if result:
            await self._cache.set_metadata(result)
        return result

    async def delete(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> bool:
        """Delete sync metadata.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID

        Returns:
            Whether metadata was deleted
        """
        result = await self._repository.delete(character_id, campaign_id)
        if result:
            await self._cache.delete_metadata(character_id, campaign_id)
        return result

    async def list_for_character(
        self,
        character_id: UUID,
    ) -> List[SyncMetadata]:
        """List all sync metadata for a character.

        Args:
            character_id: Character ID

        Returns:
            List of sync metadata
        """
        return await self._repository.list_for_character(character_id)

    async def list_for_campaign(
        self,
        campaign_id: UUID,
    ) -> List[SyncMetadata]:
        """List all sync metadata for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of sync metadata
        """
        return await self._repository.list_for_campaign(campaign_id)


class CachedSyncConflictRepository(SyncConflictRepository):
    """Cached implementation of sync conflict repository."""

    def __init__(
        self,
        db: AsyncSession,
        repository: SyncConflictRepository,
        cache: StateCache,
    ) -> None:
        """Initialize repository.

        Args:
            db: Database session
            repository: Base repository implementation
            cache: State cache
        """
        self._db = db
        self._repository = repository
        self._cache = cache

    async def create(self, conflict: SyncConflict) -> SyncConflict:
        """Create a new sync conflict.

        Args:
            conflict: Sync conflict to create

        Returns:
            Created conflict
        """
        result = await self._repository.create(conflict)
        await self._cache.set_conflict(result)
        return result

    async def get(
        self,
        character_id: UUID,
        field_path: str,
    ) -> Optional[SyncConflict]:
        """Get active conflict for a field.

        Args:
            character_id: Character ID
            field_path: Field path

        Returns:
            Active conflict if found
        """
        # Try cache first
        cached = await self._cache.get_conflict(character_id, field_path)
        if cached:
            return cached

        # Get from repository and cache
        result = await self._repository.get(character_id, field_path)
        if result:
            await self._cache.set_conflict(result)
        return result

    async def update(
        self,
        character_id: UUID,
        field_path: str,
        conflict: SyncConflict,
    ) -> Optional[SyncConflict]:
        """Update sync conflict.

        Args:
            character_id: Character ID
            field_path: Field path
            conflict: Updated conflict

        Returns:
            Updated conflict if successful
        """
        result = await self._repository.update(character_id, field_path, conflict)
        if result:
            await self._cache.set_conflict(result)
        return result

    async def resolve(
        self,
        character_id: UUID,
        field_path: str,
        resolution_strategy: str,
        resolved_value: Dict,
    ) -> Optional[SyncConflict]:
        """Resolve a sync conflict.

        Args:
            character_id: Character ID
            field_path: Field path
            resolution_strategy: Resolution strategy used
            resolved_value: Resolved value

        Returns:
            Resolved conflict if successful
        """
        result = await self._repository.resolve(
            character_id,
            field_path,
            resolution_strategy,
            resolved_value,
        )
        if result:
            await self._cache.set_conflict(result)
        return result

    async def list_active(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
    ) -> List[SyncConflict]:
        """List active conflicts for a character.

        Args:
            character_id: Character ID
            campaign_id: Optional campaign ID filter

        Returns:
            List of active conflicts
        """
        return await self._repository.list_active(character_id, campaign_id)

    async def list_resolved(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SyncConflict]:
        """List resolved conflicts for a character.

        Args:
            character_id: Character ID
            campaign_id: Optional campaign ID filter
            start_time: Optional start time
            end_time: Optional end time
            limit: Maximum number of conflicts to return

        Returns:
            List of resolved conflicts
        """
        return await self._repository.list_resolved(
            character_id,
            campaign_id,
            start_time,
            end_time,
            limit,
        )


class CachedSyncSubscriptionRepository(SyncSubscriptionRepository):
    """Cached implementation of sync subscription repository."""

    def __init__(
        self,
        db: AsyncSession,
        repository: SyncSubscriptionRepository,
        cache: StateCache,
    ) -> None:
        """Initialize repository.

        Args:
            db: Database session
            repository: Base repository implementation
            cache: State cache
        """
        self._db = db
        self._repository = repository
        self._cache = cache

    async def create(self, subscription: SyncSubscription) -> SyncSubscription:
        """Create a new sync subscription.

        Args:
            subscription: Sync subscription to create

        Returns:
            Created subscription
        """
        result = await self._repository.create(subscription)
        await self._cache.set_subscription(result)
        return result

    async def get(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> Optional[SyncSubscription]:
        """Get subscription for character/campaign pair.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID

        Returns:
            Subscription if found
        """
        # Try cache first
        cached = await self._cache.get_subscription(character_id, campaign_id)
        if cached:
            return cached

        # Get from repository and cache
        result = await self._repository.get(character_id, campaign_id)
        if result:
            await self._cache.set_subscription(result)
        return result

    async def update(
        self,
        character_id: UUID,
        campaign_id: UUID,
        subscription: SyncSubscription,
    ) -> Optional[SyncSubscription]:
        """Update sync subscription.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID
            subscription: Updated subscription

        Returns:
            Updated subscription if successful
        """
        result = await self._repository.update(
            character_id,
            campaign_id,
            subscription,
        )
        if result:
            await self._cache.set_subscription(result)
        return result

    async def delete(
        self,
        character_id: UUID,
        campaign_id: UUID,
    ) -> bool:
        """Delete sync subscription.

        Args:
            character_id: Character ID
            campaign_id: Campaign ID

        Returns:
            Whether subscription was deleted
        """
        result = await self._repository.delete(character_id, campaign_id)
        if result:
            await self._cache.delete_subscription(character_id, campaign_id)
        return result

    async def list_for_character(
        self,
        character_id: UUID,
    ) -> List[SyncSubscription]:
        """List all subscriptions for a character.

        Args:
            character_id: Character ID

        Returns:
            List of subscriptions
        """
        return await self._repository.list_for_character(character_id)

    async def list_for_campaign(
        self,
        campaign_id: UUID,
    ) -> List[SyncSubscription]:
        """List all subscriptions for a campaign.

        Args:
            campaign_id: Campaign ID

        Returns:
            List of subscriptions
        """
        return await self._repository.list_for_campaign(campaign_id)

    async def list_active(self) -> List[SyncSubscription]:
        """List all active subscriptions.

        Returns:
            List of active subscriptions
        """
        return await self._repository.list_active()
