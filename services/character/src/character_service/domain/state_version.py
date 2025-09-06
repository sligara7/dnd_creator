"""State versioning and conflict resolution system."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from character_service.core.exceptions import StateConflictError
from character_service.core.metrics import (
    track_event_handling,
    track_in_flight_with_type,
)
from character_service.domain.models import Character
from character_service.infrastructure.repositories.character import CharacterRepository


logger = logging.getLogger(__name__)


class StateVersion:
    """Represents a versioned state with metadata."""

    def __init__(
        self,
        character_id: UUID,
        version: int,
        state_data: Dict,
        timestamp: datetime,
        parent_version: Optional[int] = None,
    ) -> None:
        """Initialize state version."""
        self.character_id = character_id
        self.version = version
        self.state_data = state_data
        self.timestamp = timestamp
        self.parent_version = parent_version


class VersionManager:
    """Manages state versioning and conflict resolution."""

    def __init__(
        self,
        char_repository: CharacterRepository,
        max_conflict_resolution_attempts: int = 3,
        resync_interval: float = 1.0,
        max_version_history: int = 100,
    ) -> None:
        """Initialize version manager."""
        self._char_repo = char_repository
        self._max_attempts = max_conflict_resolution_attempts
        self._resync_interval = resync_interval
        self._max_history = max_version_history
        self._version_cache: Dict[UUID, List[StateVersion]] = {}
        self._locks: Dict[UUID, asyncio.Lock] = {}
        self._dirty_characters: Set[UUID] = set()
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self) -> None:
        """Start version manager."""
        self._cleanup_task = asyncio.create_task(self._run_cleanup())
        logger.info("Version manager started")

    async def stop(self) -> None:
        """Stop version manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
            self._cleanup_task = None
        logger.info("Version manager stopped")

    async def get_character_version(
        self,
        character_id: UUID,
        version: Optional[int] = None,
    ) -> StateVersion:
        """Get a specific version of character state."""
        async with self._get_lock(character_id):
            versions = await self._get_version_history(character_id)
            if not version:
                return versions[-1]  # Latest version

            for v in reversed(versions):
                if v.version == version:
                    return v

            raise StateConflictError(
                f"Version {version} not found for character {character_id}"
            )

    async def create_version(
        self,
        character: Character,
        parent_version: Optional[int] = None,
    ) -> StateVersion:
        """Create a new version for a character."""
        async with self._get_lock(character.id):
            versions = await self._get_version_history(character.id)
            new_version = len(versions) + 1
            state_version = StateVersion(
                character_id=character.id,
                version=new_version,
                state_data=character.character_data.copy(),
                timestamp=datetime.utcnow(),
                parent_version=parent_version,
            )
            versions.append(state_version)
            self._version_cache[character.id] = versions[-self._max_history:]
            return state_version

    async def apply_changes(
        self,
        character_id: UUID,
        changes: Dict,
        base_version: Optional[int] = None,
    ) -> Tuple[StateVersion, bool]:
        """Apply changes with optimistic concurrency control.

        Returns:
            Tuple of (new_version, had_conflict)
        """
        async with self._get_lock(character_id):
            current = await self.get_character_version(character_id)
            if base_version and current.version != base_version:
                # Version mismatch, try to resolve
                merged, had_conflict = await self._resolve_conflict(
                    character_id,
                    current,
                    changes,
                    base_version,
                )
                if merged:
                    character = await self._char_repo.get(character_id)
                    if character:
                        character.character_data = merged.state_data.copy()
                        await self._char_repo.update(character.id, character)
                        return merged, had_conflict
                raise StateConflictError(
                    f"Failed to resolve conflict for character {character_id}"
                )

            # No conflict, apply changes directly
            character = await self._char_repo.get(character_id)
            if character:
                character.character_data.update(changes)
                await self._char_repo.update(character.id, character)
                return await self.create_version(
                    character,
                    parent_version=current.version,
                ), False

            raise StateConflictError(f"Character {character_id} not found")

    async def _resolve_conflict(
        self,
        character_id: UUID,
        current: StateVersion,
        changes: Dict,
        base_version: int,
    ) -> Tuple[Optional[StateVersion], bool]:
        """Try to resolve a version conflict."""
        base = None
        for version in self._version_cache.get(character_id, []):
            if version.version == base_version:
                base = version
                break

        if not base:
            return None, True

        # Compute the diff between base and current
        current_diff = self._compute_diff(base.state_data, current.state_data)
        changes_diff = self._compute_diff(base.state_data, changes)

        # Check for conflicts
        if self._has_conflicts(current_diff, changes_diff):
            return None, True

        # Merge changes
        merged_state = base.state_data.copy()
        merged_state.update(current_diff)
        merged_state.update(changes_diff)

        # Create new version with merged state
        character = await self._char_repo.get(character_id)
        if character:
            character.character_data = merged_state
            await self._char_repo.update(character.id, character)
            return await self.create_version(
                character,
                parent_version=current.version,
            ), True

        return None, True

    def _compute_diff(self, base: Dict, updated: Dict) -> Dict:
        """Compute the difference between two states."""
        diff = {}
        for key, value in updated.items():
            if key not in base or base[key] != value:
                diff[key] = value
        return diff

    def _has_conflicts(self, diff1: Dict, diff2: Dict) -> bool:
        """Check if two diffs have conflicts."""
        # For now, consider changes to the same key a conflict
        return bool(set(diff1.keys()) & set(diff2.keys()))

    async def _get_version_history(self, character_id: UUID) -> List[StateVersion]:
        """Get version history for a character."""
        if character_id not in self._version_cache:
            # Initialize with current state
            character = await self._char_repo.get(character_id)
            if character:
                self._version_cache[character_id] = [
                    StateVersion(
                        character_id=character_id,
                        version=1,
                        state_data=character.character_data.copy(),
                        timestamp=datetime.utcnow(),
                    )
                ]
            else:
                raise StateConflictError(f"Character {character_id} not found")

        return self._version_cache[character_id]

    async def _run_cleanup(self) -> None:
        """Periodically clean up old versions."""
        while True:
            try:
                now = datetime.utcnow()
                for character_id in list(self._version_cache.keys()):
                    versions = self._version_cache[character_id]
                    # Keep only recent versions within max_history
                    self._version_cache[character_id] = versions[-self._max_history:]

                await asyncio.sleep(60)  # Run cleanup every minute
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in version cleanup: {str(e)}", exc_info=True)
                await asyncio.sleep(5)

    def _get_lock(self, character_id: UUID) -> asyncio.Lock:
        """Get or create a lock for a character."""
        if character_id not in self._locks:
            self._locks[character_id] = asyncio.Lock()
        return self._locks[character_id]
