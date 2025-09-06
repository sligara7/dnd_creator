"""Conflict resolution service."""
import asyncio
import logging
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import CharacterNotFoundError
from character_service.domain.models import Character
from character_service.domain.sync.conflict.strategies import STRATEGIES, RULE_BASED
from character_service.domain.sync.exceptions import (
    SyncConflictError,
    SyncError,
)
from character_service.domain.sync.models import (
    FieldSyncMode,
    StateChange,
    StateVersion,
    SyncConflict,
    SyncDirection,
    SyncMetadata,
)
from character_service.domain.sync.repositories import (
    StateVersionRepository,
    SyncConflictRepository,
)
from character_service.domain.sync.utils import (
    detect_changes,
    diff_values,
    extract_value,
    merge_values,
    set_value,
)
from character_service.infrastructure.messaging.hub_client import MessageHubClient
from character_service.infrastructure.repositories.character import CharacterRepository

logger = logging.getLogger(__name__)


class ConflictResolver:
    """Service for resolving state conflicts."""

    def __init__(
        self,
        db: AsyncSession,
        char_repository: CharacterRepository,
        state_repository: StateVersionRepository,
        conflict_repository: SyncConflictRepository,
        message_hub: MessageHubClient,
        default_strategy: str = "rule_based",
    ) -> None:
        """Initialize resolver.

        Args:
            db: Database session
            char_repository: Character repository
            state_repository: State version repository
            conflict_repository: Conflict repository
            message_hub: Message hub client
            default_strategy: Default resolution strategy
        """
        self._db = db
        self._char_repo = char_repository
        self._state_repo = state_repository
        self._conflict_repo = conflict_repository
        self._message_hub = message_hub
        self._default_strategy = STRATEGIES.get(default_strategy, RULE_BASED)

    async def resolve_conflicts(
        self,
        character_id: UUID,
        remote_state: Dict,
        remote_version: int,
        campaign_id: UUID,
    ) -> Tuple[Dict, List[SyncConflict]]:
        """Resolve conflicts between states.

        Args:
            character_id: Character ID
            remote_state: Remote state data
            remote_version: Remote state version
            campaign_id: Campaign ID

        Returns:
            Tuple of (resolved state, resolved conflicts)
        """
        # Get character
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Get local state version
        base_version = await self._state_repo.get_by_campaign_version(
            character_id, remote_version
        )
        if not base_version:
            # No common base version, use local state
            base_state = character.character_data.copy()
        else:
            base_state = base_version.changes

        # Detect conflicts
        base_changes = detect_changes(base_state, character.character_data)
        remote_changes = detect_changes(base_state, remote_state)

        # Find conflicting fields
        conflicts = []
        resolved_state = character.character_data.copy()
        for field, local_value in base_changes:
            if any(f == field for f, _ in remote_changes):
                # Field changed in both states
                remote_value = extract_value(remote_state, field)
                base_value = extract_value(base_state, field)

                try:
                    # Get resolution strategy
                    strategy = self._get_strategy(field)

                    # Resolve conflict
                    resolved_value, metadata = strategy.resolve(
                        field_path=field,
                        base_value=base_value,
                        local_value=local_value,
                        remote_value=remote_value,
                        sync_mode=FieldSyncMode.FULL,
                        timestamp=datetime.utcnow(),
                        metadata={
                            "field_path": field,
                            "campaign_id": campaign_id,
                            "remote_version": remote_version,
                        },
                    )

                    # Update resolved state
                    set_value(resolved_state, field, resolved_value)

                    # Record conflict resolution
                    conflict = SyncConflict(
                        character_id=character_id,
                        campaign_id=campaign_id,
                        field_path=field,
                        character_value=local_value,
                        campaign_value=remote_value,
                        character_version=base_version.version if base_version else 0,
                        campaign_version=remote_version,
                        detected_at=datetime.utcnow(),
                        resolved=True,
                        resolution_strategy=metadata["strategy"],
                        resolved_at=datetime.utcnow(),
                        resolved_value=resolved_value,
                    )
                    await self._conflict_repo.create(conflict)
                    conflicts.append(conflict)

                except SyncConflictError as e:
                    # Record unresolved conflict
                    conflict = SyncConflict(
                        character_id=character_id,
                        campaign_id=campaign_id,
                        field_path=field,
                        character_value=local_value,
                        campaign_value=remote_value,
                        character_version=base_version.version if base_version else 0,
                        campaign_version=remote_version,
                        detected_at=datetime.utcnow(),
                        resolved=False,
                        resolution_strategy=None,
                        resolved_at=None,
                        resolved_value=None,
                    )
                    await self._conflict_repo.create(conflict)
                    conflicts.append(conflict)

                    # Keep local value for unresolved conflicts
                    logger.warning(
                        "Unresolved conflict in %s: %s",
                        field,
                        str(e),
                    )

        return resolved_state, conflicts

    def _get_strategy(self, field_path: str) -> str:
        """Get resolution strategy for field.

        Args:
            field_path: Field path

        Returns:
            Resolution strategy
        """
        # Combat stats use rule-based
        if any(
            pattern in field_path
            for pattern in [
                "hit_points",
                "temporary_hit_points",
                "conditions",
                "death_saves",
            ]
        ):
            return STRATEGIES["rule_based"]

        # Resources use rule-based
        if any(
            pattern in field_path
            for pattern in [
                "spell_slots",
                "class_resources",
                "features",
            ]
        ):
            return STRATEGIES["rule_based"]

        # Progress uses incremental
        if any(
            pattern in field_path
            for pattern in [
                "experience_points",
                "proficiency_bonus",
                "level",
            ]
        ):
            return STRATEGIES["incremental"]

        # Equipment uses rule-based
        if any(
            pattern in field_path
            for pattern in [
                "inventory",
                "equipment",
            ]
        ):
            return STRATEGIES["rule_based"]

        # Default to merge strategy
        return STRATEGIES["merge"]

    async def resolve_queued_conflicts(
        self,
        character_id: UUID,
        campaign_id: Optional[UUID] = None,
    ) -> List[SyncConflict]:
        """Resolve queued conflicts for a character.

        Args:
            character_id: Character ID
            campaign_id: Optional campaign ID filter

        Returns:
            List of resolved conflicts
        """
        # Get unresolved conflicts
        conflicts = await self._conflict_repo.list_active(character_id, campaign_id)
        if not conflicts:
            return []

        # Get character
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Try to resolve each conflict
        resolved = []
        for conflict in conflicts:
            try:
                # Get resolution strategy
                strategy = self._get_strategy(conflict.field_path)

                # Get base version
                base_version = await self._state_repo.get_by_campaign_version(
                    character_id, conflict.campaign_version
                )
                base_value = (
                    extract_value(base_version.changes, conflict.field_path)
                    if base_version
                    else None
                )

                # Resolve conflict
                resolved_value, metadata = strategy.resolve(
                    field_path=conflict.field_path,
                    base_value=base_value,
                    local_value=conflict.character_value,
                    remote_value=conflict.campaign_value,
                    sync_mode=FieldSyncMode.FULL,
                    timestamp=datetime.utcnow(),
                    metadata={
                        "field_path": conflict.field_path,
                        "campaign_id": conflict.campaign_id,
                        "campaign_version": conflict.campaign_version,
                    },
                )

                # Update conflict
                conflict.resolved = True
                conflict.resolution_strategy = metadata["strategy"]
                conflict.resolved_at = datetime.utcnow()
                conflict.resolved_value = resolved_value

                await self._conflict_repo.resolve(
                    character_id=character_id,
                    field_path=conflict.field_path,
                    resolution_strategy=metadata["strategy"],
                    resolved_value=resolved_value,
                )

                resolved.append(conflict)

            except SyncConflictError as e:
                logger.warning(
                    "Failed to resolve conflict %s: %s",
                    conflict.field_path,
                    str(e),
                )

        return resolved

    async def notify_conflict_resolution(
        self,
        conflict: SyncConflict,
    ) -> None:
        """Notify about conflict resolution.

        Args:
            conflict: Resolved conflict
        """
        await self._message_hub.publish(
            "character.conflict.resolved",
            {
                "character_id": str(conflict.character_id),
                "campaign_id": str(conflict.campaign_id),
                "field_path": conflict.field_path,
                "resolution_strategy": conflict.resolution_strategy,
                "resolved_value": conflict.resolved_value,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
