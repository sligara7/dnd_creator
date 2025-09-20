"""State management service implementation."""

import hashlib
import json
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import redis.asyncio as redis
from prometheus_client import Counter, Gauge

from ..core.interfaces import BaseStateService, StateError, StateProvider, StateUpdate, StateVersion

# Metrics
state_updates = Counter("game_session_state_updates", "Number of state updates")
state_conflicts = Counter("game_session_state_conflicts", "Number of state conflicts")
state_versions = Gauge("game_session_state_versions", "Number of state versions per session")

logger = logging.getLogger(__name__)

class RedisStateProvider(StateProvider):
    """Redis-based state storage provider."""
    
    def __init__(self, redis_client: redis.Redis) -> None:
        """Initialize the Redis state provider.
        
        Args:
            redis_client: Redis client instance
        """
        self._redis = redis_client
        
    async def get_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            The current session state
            
        Raises:
            StateError: If state cannot be retrieved
        """
        try:
            state_json = await self._redis.get(f"session:{session_id}:state")
            if not state_json:
                return {}
            return json.loads(state_json)
        except Exception as e:
            raise StateError(f"Failed to get state: {e}") from e
            
    async def set_state(
        self,
        session_id: UUID,
        state: Dict[str, Any],
        version: str
    ) -> None:
        """Set the state for a session.
        
        Args:
            session_id: The session ID
            state: The new state
            version: The state version
            
        Raises:
            StateError: If state cannot be set
        """
        try:
            # Store state and version atomically
            async with self._redis.pipeline() as pipe:
                pipe.set(f"session:{session_id}:state", json.dumps(state))
                pipe.set(f"session:{session_id}:version", version)
                await pipe.execute()
        except Exception as e:
            raise StateError(f"Failed to set state: {e}") from e
            
    async def get_version(self, session_id: UUID) -> Optional[str]:
        """Get the current version for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            The current version or None if not found
            
        Raises:
            StateError: If version cannot be retrieved
        """
        try:
            version = await self._redis.get(f"session:{session_id}:version")
            return version.decode() if version else None
        except Exception as e:
            raise StateError(f"Failed to get version: {e}") from e

class StateService(BaseStateService):
    """State management service implementation."""
    
    def __init__(
        self,
        state_provider: StateProvider,
        max_versions: int = 100
    ) -> None:
        """Initialize the state service.
        
        Args:
            state_provider: State storage provider
            max_versions: Maximum number of versions to track per session
        """
        self._provider = state_provider
        self._max_versions = max_versions
        self._change_logs: Dict[UUID, List[StateVersion]] = {}
        
    @property
    def name(self) -> str:
        """Get the service name."""
        return "state"
        
    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing state service")
        
    async def cleanup(self) -> None:
        """Clean up service resources."""
        logger.info("Cleaning up state service")
        self._change_logs.clear()
        
    async def get_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            The current session state
            
        Raises:
            StateError: If state cannot be retrieved
        """
        return await self._provider.get_state(session_id)
        
    async def update_state(
        self,
        session_id: UUID,
        updates: List[StateUpdate]
    ) -> StateVersion:
        """Apply updates to session state.
        
        Args:
            session_id: The session ID
            updates: List of state updates
            
        Returns:
            New state version information
            
        Raises:
            StateError: If state cannot be updated
        """
        try:
            # Get current state and version
            current_state = await self.get_state(session_id)
            current_version = await self._provider.get_version(session_id)
            
            # Apply updates
            new_state = current_state.copy()
            for update in updates:
                path_parts = update.path.split('.')
                target = new_state
                
                # Navigate to the target location
                for i, part in enumerate(path_parts[:-1]):
                    if part not in target:
                        target[part] = {}
                    target = target[part]
                
                # Store previous value and apply update
                update.previous = target.get(path_parts[-1])
                target[path_parts[-1]] = update.value
            
            # Generate new version
            timestamp = datetime.utcnow()
            version_data = {
                "state": new_state,
                "updates": [u.dict() for u in updates],
                "timestamp": timestamp.isoformat()
            }
            new_version = hashlib.sha256(
                json.dumps(version_data, sort_keys=True).encode()
            ).hexdigest()[:12]
            
            # Store new state and version
            await self._provider.set_state(session_id, new_state, new_version)
            
            # Record change
            version = StateVersion(
                version=new_version,
                timestamp=timestamp,
                changes=updates
            )
            
            if session_id not in self._change_logs:
                self._change_logs[session_id] = []
            
            # Add version to change log with size limit
            changes = self._change_logs[session_id]
            changes.append(version)
            if len(changes) > self._max_versions:
                changes.pop(0)
            
            state_updates.inc()
            state_versions.labels(session_id=str(session_id)).set(len(changes))
            
            return version
            
        except Exception as e:
            raise StateError(f"Failed to update state: {e}") from e
            
    async def resolve_conflict(
        self,
        session_id: UUID,
        client_version: str,
        updates: List[StateUpdate]
    ) -> StateVersion:
        """Resolve a state conflict.
        
        Args:
            session_id: The session ID
            client_version: Client's last known version
            updates: Client's pending updates
            
        Returns:
            New state version information
            
        Raises:
            StateError: If conflict cannot be resolved
        """
        try:
            current_version = await self._provider.get_version(session_id)
            
            # If versions match, apply updates normally
            if client_version == current_version:
                return await self.update_state(session_id, updates)
            
            # Find the changes since client version
            changes = self._change_logs.get(session_id, [])
            client_index = -1
            for i, version in enumerate(changes):
                if version.version == client_version:
                    client_index = i
                    break
            
            if client_index == -1:
                raise StateError("Client version too old")
            
            # Get intervening changes
            intervening_changes = changes[client_index + 1:]
            
            # Check for conflicts
            conflict_paths: Set[str] = set()
            for version in intervening_changes:
                for change in version.changes:
                    for update in updates:
                        if change.path == update.path:
                            conflict_paths.add(change.path)
            
            if conflict_paths:
                # Remove conflicting updates
                updates = [u for u in updates if u.path not in conflict_paths]
                state_conflicts.inc()
                logger.warning(
                    f"Resolved conflicts for paths: {conflict_paths} in session {session_id}"
                )
            
            # Apply remaining updates
            if updates:
                return await self.update_state(session_id, updates)
            else:
                # Return current version if no updates remain
                return changes[-1]
            
        except Exception as e:
            raise StateError(f"Failed to resolve conflict: {e}") from e