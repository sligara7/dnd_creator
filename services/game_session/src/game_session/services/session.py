"""Session management service implementation."""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from prometheus_client import Counter, Gauge, Histogram

from ..core.interfaces import BaseSessionService, SessionError, StateService
from ..domain.models import GameSession, SessionPlayer, SessionStatus

# Metrics
active_sessions = Gauge("game_session_active_sessions", "Number of active game sessions")
session_players = Gauge(
    "game_session_players",
    "Number of players per session",
    ["session_id"]
)
session_duration = Histogram(
    "game_session_duration_minutes",
    "Duration of game sessions",
    buckets=[30, 60, 120, 180, 240, 360]
)
action_validation = Counter(
    "game_session_action_validation",
    "Action validation results",
    ["action_type", "result"]
)

logger = logging.getLogger(__name__)

class SessionService(BaseSessionService):
    """Session management service implementation."""
    
    def __init__(
        self,
        state_service: StateService,
        max_players: int = 10
    ) -> None:
        """Initialize the session service.
        
        Args:
            state_service: State management service
            max_players: Maximum players per session
        """
        self._state = state_service
        self._max_players = max_players
        self._active_sessions: Dict[UUID, GameSession] = {}
        
    @property
    def name(self) -> str:
        """Get the service name."""
        return "session"
        
    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing session service")
        
    async def cleanup(self) -> None:
        """Clean up service resources."""
        logger.info("Cleaning up session service")
        self._active_sessions.clear()
        
    async def _get_session(self, session_id: UUID) -> Optional[GameSession]:
        """Get a game session by ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Game session or None if not found
        """
        # Check memory cache first
        if session_id in self._active_sessions:
            return self._active_sessions[session_id]
            
        # Load from state
        state = await self._state.get_state(session_id)
        if "session" in state:
            session = GameSession.model_validate(state["session"])
            if session.status != SessionStatus.ENDED:
                self._active_sessions[session_id] = session
            return session
            
        return None
        
    async def _save_session(self, session: GameSession) -> None:
        """Save a game session.
        
        Args:
            session: The session to save
        """
        await self._state.update_state(
            session.id,
            [{"path": "session", "value": session.model_dump()}]
        )
        
        if session.status == SessionStatus.ENDED:
            self._active_sessions.pop(session.id, None)
            active_sessions.dec()
            session_players.remove(session_id=str(session.id))
            
            # Record session duration
            if session.ended_at and session.created_at:
                duration = (session.ended_at - session.created_at).total_seconds() / 60
                session_duration.observe(duration)
        else:
            self._active_sessions[session.id] = session
            session_players.labels(session_id=str(session.id)).set(len(session.players))
        
    async def create_session(
        self,
        campaign_id: UUID,
        name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> UUID:
        """Create a new game session.
        
        Args:
            campaign_id: Campaign ID
            name: Session name
            metadata: Optional session metadata
            
        Returns:
            New session ID
            
        Raises:
            SessionError: If session cannot be created
        """
        try:
            session = GameSession(
                campaign_id=campaign_id,
                name=name,
                metadata=metadata or {}
            )
            
            await self._save_session(session)
            active_sessions.inc()
            logger.info(f"Created game session {session.id} for campaign {campaign_id}")
            
            return session.id
            
        except Exception as e:
            raise SessionError(f"Failed to create session: {e}") from e
        
    async def end_session(self, session_id: UUID) -> None:
        """End a game session.
        
        Args:
            session_id: The session ID
            
        Raises:
            SessionError: If session cannot be ended
        """
        try:
            session = await self._get_session(session_id)
            
            if not session or session.status == SessionStatus.ENDED:
                return
                
            session.status = SessionStatus.ENDED
            session.ended_at = datetime.utcnow()
            
            await self._save_session(session)
            logger.info(f"Ended game session {session_id}")
            
        except Exception as e:
            raise SessionError(f"Failed to end session: {e}") from e
        
    async def add_player(
        self,
        session_id: UUID,
        character_id: UUID,
        user_id: UUID
    ) -> None:
        """Add a player to a session.
        
        Args:
            session_id: The session ID
            character_id: Character ID to add
            user_id: User ID of the player
            
        Raises:
            SessionError: If player cannot be added
        """
        try:
            session = await self._get_session(session_id)
            
            if not session:
                raise SessionError("Session not found")
                
            if session.status == SessionStatus.ENDED:
                raise SessionError("Session has ended")
                
            if len(session.players) >= self._max_players:
                raise SessionError("Session is full")
                
            if any(p.character_id == character_id for p in session.players):
                raise SessionError("Character already in session")
                
            player = SessionPlayer(
                character_id=character_id,
                user_id=user_id
            )
            session.players.append(player)
            
            if session.status == SessionStatus.CREATED:
                session.status = SessionStatus.ACTIVE
                
            await self._save_session(session)
            logger.info(
                f"Added player {user_id} with character {character_id} to session {session_id}"
            )
            
        except Exception as e:
            raise SessionError(f"Failed to add player: {e}") from e
        
    async def remove_player(
        self,
        session_id: UUID,
        character_id: UUID
    ) -> None:
        """Remove a player from a session.
        
        Args:
            session_id: The session ID
            character_id: Character ID to remove
            
        Raises:
            SessionError: If player cannot be removed
        """
        try:
            session = await self._get_session(session_id)
            
            if not session:
                return
                
            if session.status == SessionStatus.ENDED:
                return
                
            # Remove player
            session.players = [
                p for p in session.players
                if p.character_id != character_id
            ]
            
            # End session if no players left
            if not session.players:
                session.status = SessionStatus.ENDED
                session.ended_at = datetime.utcnow()
            
            await self._save_session(session)
            logger.info(f"Removed character {character_id} from session {session_id}")
            
        except Exception as e:
            raise SessionError(f"Failed to remove player: {e}") from e
        
    async def get_session_status(self, session_id: UUID) -> Dict[str, Any]:
        """Get the current status of a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Session status information
            
        Raises:
            SessionError: If status cannot be retrieved
        """
        try:
            session = await self._get_session(session_id)
            
            if not session:
                return {"status": "not_found"}
                
            return {
                "status": session.status,
                "player_count": len(session.players),
                "created_at": session.created_at.isoformat(),
                "updated_at": session.updated_at.isoformat(),
                "ended_at": session.ended_at.isoformat() if session.ended_at else None,
                "metadata": session.metadata
            }
            
        except Exception as e:
            raise SessionError(f"Failed to get session status: {e}") from e
        
    async def validate_action(
        self,
        session_id: UUID,
        character_id: UUID,
        action_type: str,
        action_data: Dict[str, Any]
    ) -> bool:
        """Validate if an action is allowed.
        
        Args:
            session_id: The session ID
            character_id: Character attempting the action
            action_type: Type of action
            action_data: Action-specific data
            
        Returns:
            True if action is allowed, False otherwise
            
        Raises:
            SessionError: If validation fails
        """
        try:
            session = await self._get_session(session_id)
            
            if not session:
                action_validation.labels(
                    action_type=action_type,
                    result="session_not_found"
                ).inc()
                return False
                
            if session.status != SessionStatus.ACTIVE:
                action_validation.labels(
                    action_type=action_type,
                    result="session_not_active"
                ).inc()
                return False
                
            # Verify character is in session
            character_in_session = any(
                p.character_id == character_id
                for p in session.players
            )
            
            if not character_in_session:
                action_validation.labels(
                    action_type=action_type,
                    result="character_not_in_session"
                ).inc()
                return False
            
            # Add specific action validations here
            # For now, just allow all actions from valid characters
            action_validation.labels(
                action_type=action_type,
                result="allowed"
            ).inc()
            return True
            
        except Exception as e:
            action_validation.labels(
                action_type=action_type,
                result="error"
            ).inc()
            raise SessionError(f"Failed to validate action: {e}") from e