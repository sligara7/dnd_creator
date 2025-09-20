"""Service interfaces and base classes for game session management."""

import abc
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, runtime_checkable
from uuid import UUID

from pydantic import BaseModel

class ServiceError(Exception):
    """Base class for service-level errors."""
    pass

class StateError(ServiceError):
    """Errors related to state management."""
    pass

class CombatError(ServiceError):
    """Errors related to combat management."""
    pass

class SessionError(ServiceError):
    """Errors related to session management."""
    pass

class ValidationError(ServiceError):
    """Errors related to validation."""
    pass

class StateUpdate(BaseModel):
    """Represents a state update."""
    path: str
    value: Any
    previous: Optional[Any] = None
    timestamp: datetime = datetime.utcnow()

class StateVersion(BaseModel):
    """Represents a version of state."""
    version: str
    timestamp: datetime
    changes: List[StateUpdate]

@runtime_checkable
class StateProvider(Protocol):
    """Protocol for state storage providers."""
    
    async def get_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current state for a session."""
        ...
        
    async def set_state(
        self,
        session_id: UUID,
        state: Dict[str, Any],
        version: str
    ) -> None:
        """Set the state for a session."""
        ...
        
    async def get_version(self, session_id: UUID) -> Optional[str]:
        """Get the current version for a session."""
        ...

class BaseGameService(abc.ABC):
    """Base class for game services."""
    
    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Get the service name."""
        ...
        
    @abc.abstractmethod
    async def initialize(self) -> None:
        """Initialize the service."""
        ...
        
    @abc.abstractmethod
    async def cleanup(self) -> None:
        """Clean up service resources."""
        ...
        
    async def __aenter__(self) -> 'BaseGameService':
        """Context manager entry."""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        await self.cleanup()

class BaseStateService(BaseGameService):
    """Base class for state management services."""
    
    @abc.abstractmethod
    async def get_state(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current state for a session."""
        ...
        
    @abc.abstractmethod
    async def update_state(
        self,
        session_id: UUID,
        updates: List[StateUpdate]
    ) -> StateVersion:
        """Apply updates to session state."""
        ...
        
    @abc.abstractmethod
    async def resolve_conflict(
        self,
        session_id: UUID,
        client_version: str,
        updates: List[StateUpdate]
    ) -> StateVersion:
        """Resolve a state conflict."""
        ...

class BaseCombatService(BaseGameService):
    """Base class for combat management services."""
    
    @abc.abstractmethod
    async def start_combat(
        self,
        session_id: UUID,
        participants: List[UUID]
    ) -> None:
        """Start combat for a session."""
        ...
        
    @abc.abstractmethod
    async def end_combat(self, session_id: UUID) -> None:
        """End combat for a session."""
        ...
        
    @abc.abstractmethod
    async def add_participant(
        self,
        session_id: UUID,
        character_id: UUID,
        initiative: int
    ) -> None:
        """Add a participant to combat."""
        ...
        
    @abc.abstractmethod
    async def remove_participant(
        self,
        session_id: UUID,
        character_id: UUID
    ) -> None:
        """Remove a participant from combat."""
        ...
        
    @abc.abstractmethod
    async def get_current_turn(self, session_id: UUID) -> Optional[UUID]:
        """Get the current turn's character ID."""
        ...
        
    @abc.abstractmethod
    async def next_turn(self, session_id: UUID) -> Optional[UUID]:
        """Advance to the next turn."""
        ...

class BaseSessionService(BaseGameService):
    """Base class for session management services."""
    
    @abc.abstractmethod
    async def create_session(
        self,
        campaign_id: UUID,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Create a new game session."""
        ...
        
    @abc.abstractmethod
    async def end_session(self, session_id: UUID) -> None:
        """End a game session."""
        ...
        
    @abc.abstractmethod
    async def add_player(
        self,
        session_id: UUID,
        character_id: UUID,
        user_id: UUID
    ) -> None:
        """Add a player to a session."""
        ...
        
    @abc.abstractmethod
    async def remove_player(
        self,
        session_id: UUID,
        character_id: UUID
    ) -> None:
        """Remove a player from a session."""
        ...
        
    @abc.abstractmethod
    async def get_session_status(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current status of a session."""
        ...
        
    @abc.abstractmethod
    async def validate_action(
        self,
        session_id: UUID,
        character_id: UUID,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> bool:
        """Validate if an action is allowed."""
        ...