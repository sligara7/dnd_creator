"""State synchronization repository interfaces."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID

from character_service.domain.sync.models import (
    StateVersion,
    SyncConflict,
    SyncError,
    SyncMessage,
    SyncMetadata,
    SyncSubscription,
)


@runtime_checkable
class StateVersionRepository(Protocol):
    """Repository for managing state versions."""

    async def create(self, version: StateVersion) -> StateVersion:
        """Create a new state version."""
        ...

    async def get(self, character_id: UUID, version: int) -> Optional[StateVersion]:
        """Get state version by character and version number."""
        ...

    async def get_latest(self, character_id: UUID) -> Optional[StateVersion]:
        """Get latest state version for a character."""
        ...

    async def get_by_campaign_version(
        self, character_id: UUID, campaign_version: int
    ) -> List[StateVersion]:
        """Get all versions associated with a campaign version."""
        ...

    async def list_versions(
        self,
        character_id: UUID,
        start_version: Optional[int] = None,
        end_version: Optional[int] = None,
        limit: int = 100,
    ) -> List[StateVersion]:
        """List versions for a character in range."""
        ...


@runtime_checkable
class SyncMetadataRepository(Protocol):
    """Repository for managing sync metadata."""

    async def create(self, metadata: SyncMetadata) -> SyncMetadata:
        """Create new sync metadata."""
        ...

    async def get(self, character_id: UUID, campaign_id: UUID) -> Optional[SyncMetadata]:
        """Get sync metadata for character/campaign pair."""
        ...

    async def update(
        self, character_id: UUID, campaign_id: UUID, metadata: SyncMetadata
    ) -> Optional[SyncMetadata]:
        """Update sync metadata."""
        ...

    async def delete(self, character_id: UUID, campaign_id: UUID) -> bool:
        """Delete sync metadata."""
        ...

    async def list_for_character(self, character_id: UUID) -> List[SyncMetadata]:
        """List all sync metadata for a character."""
        ...

    async def list_for_campaign(self, campaign_id: UUID) -> List[SyncMetadata]:
        """List all sync metadata for a campaign."""
        ...


@runtime_checkable
class SyncMessageRepository(Protocol):
    """Repository for managing sync messages."""

    async def create(self, message: SyncMessage) -> SyncMessage:
        """Create a new sync message."""
        ...

    async def get(self, message_id: UUID) -> Optional[SyncMessage]:
        """Get sync message by ID."""
        ...

    async def list_for_character(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SyncMessage]:
        """List sync messages for a character."""
        ...

    async def delete_before(self, timestamp: datetime) -> int:
        """Delete messages older than timestamp."""
        ...


@runtime_checkable
class SyncConflictRepository(Protocol):
    """Repository for managing sync conflicts."""

    async def create(self, conflict: SyncConflict) -> SyncConflict:
        """Create a new sync conflict."""
        ...

    async def get(self, character_id: UUID, field_path: str) -> Optional[SyncConflict]:
        """Get active conflict for a field."""
        ...

    async def update(
        self, character_id: UUID, field_path: str, conflict: SyncConflict
    ) -> Optional[SyncConflict]:
        """Update sync conflict."""
        ...

    async def resolve(
        self,
        character_id: UUID,
        field_path: str,
        resolution_strategy: str,
        resolved_value: Dict,
    ) -> Optional[SyncConflict]:
        """Resolve a sync conflict."""
        ...

    async def list_active(
        self, character_id: UUID, campaign_id: Optional[UUID] = None
    ) -> List[SyncConflict]:
        """List active conflicts for a character."""
        ...

    async def list_resolved(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SyncConflict]:
        """List resolved conflicts for a character."""
        ...


@runtime_checkable
class SyncErrorRepository(Protocol):
    """Repository for managing sync errors."""

    async def create(self, error: SyncError) -> SyncError:
        """Create a new sync error."""
        ...

    async def get(self, character_id: UUID, error_type: str) -> Optional[SyncError]:
        """Get latest error of type for character."""
        ...

    async def update(
        self, character_id: UUID, error_type: str, error: SyncError
    ) -> Optional[SyncError]:
        """Update sync error."""
        ...

    async def resolve(
        self, character_id: UUID, error_type: str, recovery_strategy: str
    ) -> Optional[SyncError]:
        """Resolve a sync error."""
        ...

    async def list_active(
        self, character_id: UUID, campaign_id: Optional[UUID] = None
    ) -> List[SyncError]:
        """List active errors for a character."""
        ...

    async def list_resolved(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[SyncError]:
        """List resolved errors for a character."""
        ...


@runtime_checkable
class SyncSubscriptionRepository(Protocol):
    """Repository for managing sync subscriptions."""

    async def create(self, subscription: SyncSubscription) -> SyncSubscription:
        """Create a new sync subscription."""
        ...

    async def get(
        self, character_id: UUID, campaign_id: UUID
    ) -> Optional[SyncSubscription]:
        """Get subscription for character/campaign pair."""
        ...

    async def update(
        self, character_id: UUID, campaign_id: UUID, subscription: SyncSubscription
    ) -> Optional[SyncSubscription]:
        """Update sync subscription."""
        ...

    async def delete(self, character_id: UUID, campaign_id: UUID) -> bool:
        """Delete sync subscription."""
        ...

    async def list_for_character(self, character_id: UUID) -> List[SyncSubscription]:
        """List all subscriptions for a character."""
        ...

    async def list_for_campaign(self, campaign_id: UUID) -> List[SyncSubscription]:
        """List all subscriptions for a campaign."""
        ...

    async def list_active(self) -> List[SyncSubscription]:
        """List all active subscriptions."""
        ...
