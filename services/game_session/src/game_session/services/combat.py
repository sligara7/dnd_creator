"""Combat management service implementation."""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from prometheus_client import Counter, Gauge, Histogram

from ..core.interfaces import BaseCombatService, CombatError, StateService
from ..domain.models import Combat, CombatParticipant, CombatStatus

# Metrics
combat_rounds = Counter("game_session_combat_rounds", "Number of combat rounds")
active_combats = Gauge("game_session_active_combats", "Number of active combats")
turn_duration = Histogram(
    "game_session_turn_duration_seconds",
    "Duration of combat turns",
    buckets=[1, 5, 15, 30, 60, 120]
)

logger = logging.getLogger(__name__)

class CombatService(BaseCombatService):
    """Combat management service implementation."""
    
    def __init__(self, state_service: StateService) -> None:
        """Initialize the combat service.
        
        Args:
            state_service: State management service
        """
        self._state = state_service
        self._active_combats: Dict[UUID, Combat] = {}
        
    @property
    def name(self) -> str:
        """Get the service name."""
        return "combat"
        
    async def initialize(self) -> None:
        """Initialize the service."""
        logger.info("Initializing combat service")
        
    async def cleanup(self) -> None:
        """Clean up service resources."""
        logger.info("Cleaning up combat service")
        self._active_combats.clear()
        
    async def _get_combat(self, session_id: UUID) -> Optional[Combat]:
        """Get combat state for a session.
        
        Args:
            session_id: The session ID
            
        Returns:
            Combat state or None if not in combat
        """
        # Check memory cache first
        if session_id in self._active_combats:
            return self._active_combats[session_id]
            
        # Load from state
        state = await self._state.get_state(session_id)
        if "combat" in state:
            combat = Combat.model_validate(state["combat"])
            if combat.status != CombatStatus.ENDED:
                self._active_combats[session_id] = combat
            return combat
            
        return None
        
    async def _save_combat(self, session_id: UUID, combat: Combat) -> None:
        """Save combat state.
        
        Args:
            session_id: The session ID
            combat: Combat state to save
        """
        await self._state.update_state(
            session_id,
            [{"path": "combat", "value": combat.model_dump()}]
        )
        
        if combat.status == CombatStatus.ENDED:
            self._active_combats.pop(session_id, None)
            active_combats.dec()
        else:
            self._active_combats[session_id] = combat
        
    async def start_combat(
        self,
        session_id: UUID,
        participants: List[UUID]
    ) -> None:
        """Start combat for a session.
        
        Args:
            session_id: The session ID
            participants: List of participant character IDs
            
        Raises:
            CombatError: If combat cannot be started
        """
        try:
            combat = await self._get_combat(session_id)
            
            if combat and combat.status != CombatStatus.ENDED:
                raise CombatError("Combat already in progress")
                
            combat = Combat(
                status=CombatStatus.PREPARING,
                started_at=datetime.utcnow()
            )
            
            await self._save_combat(session_id, combat)
            active_combats.inc()
            logger.info(f"Started combat preparation in session {session_id}")
            
        except Exception as e:
            raise CombatError(f"Failed to start combat: {e}") from e
        
    async def end_combat(self, session_id: UUID) -> None:
        """End combat for a session.
        
        Args:
            session_id: The session ID
            
        Raises:
            CombatError: If combat cannot be ended
        """
        try:
            combat = await self._get_combat(session_id)
            
            if not combat or combat.status == CombatStatus.ENDED:
                return
                
            combat.status = CombatStatus.ENDED
            combat.ended_at = datetime.utcnow()
            
            await self._save_combat(session_id, combat)
            logger.info(f"Ended combat in session {session_id}")
            
        except Exception as e:
            raise CombatError(f"Failed to end combat: {e}") from e
        
    async def add_participant(
        self,
        session_id: UUID,
        character_id: UUID,
        initiative: int
    ) -> None:
        """Add a participant to combat.
        
        Args:
            session_id: The session ID
            character_id: Character ID to add
            initiative: Initiative roll
            
        Raises:
            CombatError: If participant cannot be added
        """
        try:
            combat = await self._get_combat(session_id)
            
            if not combat:
                raise CombatError("No combat in progress")
                
            if combat.status == CombatStatus.ENDED:
                raise CombatError("Combat has ended")
                
            if any(p.character_id == character_id for p in combat.participants):
                raise CombatError("Character already in combat")
                
            participant = CombatParticipant(
                character_id=character_id,
                initiative=initiative
            )
            combat.participants.append(participant)
            
            # Sort participants by initiative
            combat.participants.sort(key=lambda p: p.initiative, reverse=True)
            combat.initiative_order = [p.character_id for p in combat.participants]
            
            # If first participant, start combat
            if len(combat.participants) == 1:
                combat.status = CombatStatus.ACTIVE
                combat.round = 1
                combat.current_turn = participant.character_id
                
            await self._save_combat(session_id, combat)
            logger.info(
                f"Added participant {character_id} to combat in session {session_id}"
            )
            
        except Exception as e:
            raise CombatError(f"Failed to add participant: {e}") from e
        
    async def remove_participant(
        self,
        session_id: UUID,
        character_id: UUID
    ) -> None:
        """Remove a participant from combat.
        
        Args:
            session_id: The session ID
            character_id: Character ID to remove
            
        Raises:
            CombatError: If participant cannot be removed
        """
        try:
            combat = await self._get_combat(session_id)
            
            if not combat:
                return
                
            if combat.status == CombatStatus.ENDED:
                return
                
            # Remove from participants and initiative order
            combat.participants = [
                p for p in combat.participants
                if p.character_id != character_id
            ]
            combat.initiative_order = [
                cid for cid in combat.initiative_order
                if cid != character_id
            ]
            
            # If current turn, advance to next
            if combat.current_turn == character_id:
                if combat.initiative_order:
                    await self.next_turn(session_id)
                else:
                    combat.current_turn = None
            
            # If no participants left, end combat
            if not combat.participants:
                combat.status = CombatStatus.ENDED
                combat.ended_at = datetime.utcnow()
                
            await self._save_combat(session_id, combat)
            logger.info(
                f"Removed participant {character_id} from combat in session {session_id}"
            )
            
        except Exception as e:
            raise CombatError(f"Failed to remove participant: {e}") from e
        
    async def get_current_turn(self, session_id: UUID) -> Optional[UUID]:
        """Get the current turn's character ID.
        
        Args:
            session_id: The session ID
            
        Returns:
            Current character's ID or None if not in combat
            
        Raises:
            CombatError: If current turn cannot be retrieved
        """
        try:
            combat = await self._get_combat(session_id)
            
            if not combat or combat.status != CombatStatus.ACTIVE:
                return None
                
            return combat.current_turn
            
        except Exception as e:
            raise CombatError(f"Failed to get current turn: {e}") from e
        
    async def next_turn(self, session_id: UUID) -> Optional[UUID]:
        """Advance to the next turn.
        
        Args:
            session_id: The session ID
            
        Returns:
            Next character's ID or None if combat ends
            
        Raises:
            CombatError: If turn cannot be advanced
        """
        try:
            combat = await self._get_combat(session_id)
            
            if not combat or combat.status != CombatStatus.ACTIVE:
                return None
                
            if not combat.initiative_order:
                return None
                
            # Find current position in initiative order
            current_pos = -1
            if combat.current_turn:
                try:
                    current_pos = combat.initiative_order.index(combat.current_turn)
                except ValueError:
                    pass
            
            # Get next position
            next_pos = (current_pos + 1) % len(combat.initiative_order)
            
            # If wrapping around, increment round
            if next_pos == 0:
                combat.round += 1
                combat_rounds.inc()
            
            # Update current turn
            combat.current_turn = combat.initiative_order[next_pos]
            
            await self._save_combat(session_id, combat)
            logger.info(
                f"Advanced to next turn ({combat.current_turn}) in session {session_id}"
            )
            
            return combat.current_turn
            
        except Exception as e:
            raise CombatError(f"Failed to advance turn: {e}") from e