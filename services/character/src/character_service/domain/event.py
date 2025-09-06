"""Event impact service module."""
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID, uuid4

from character_service.core.exceptions import (CharacterNotFoundError,
                                          EventApplicationError,
                                          EventNotFoundError)
from character_service.domain.models import CampaignEvent, Character, EventImpact
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.event import (
    CampaignEventRepository, EventImpactRepository)
from character_service.domain.state_version import VersionManager


class EventImpactService:
    """Service for handling campaign events and their impacts on characters."""

    def __init__(
        self,
        event_repository: CampaignEventRepository,
        impact_repository: EventImpactRepository,
        character_repository: CharacterRepository,
        version_manager: VersionManager,
    ) -> None:
        """Initialize service."""
        self._event_repo = event_repository
        self._impact_repo = impact_repository
        self._char_repo = character_repository
        self._version_manager = version_manager

    async def create_event(
        self,
        character_id: UUID,
        event_type: str,
        event_data: dict,
        impact_type: str,
        impact_magnitude: int,
        journal_entry_id: Optional[UUID] = None,
    ) -> CampaignEvent:
        """Create a new campaign event for a character."""
        # Verify character exists
        character = await self._char_repo.get(character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {character_id} not found")

        # Create event
        event = CampaignEvent(
            id=uuid4(),
            character_id=character_id,
            journal_entry_id=journal_entry_id,
            event_type=event_type,
            event_data=event_data,
            impact_type=impact_type,
            impact_magnitude=impact_magnitude,
            timestamp=datetime.utcnow(),
        )
        await self._event_repo.create(event)
        return event

    async def apply_event(
        self,
        event_id: UUID,
    ) -> List[EventImpact]:
        """Apply a campaign event to the character."""
        # Get event
        event = await self._event_repo.get(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        if event.applied:
            return []  # Already applied

        # Get character
        character = await self._char_repo.get(event.character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {event.character_id} not found")

        # Calculate impacts
        impacts = await self._calculate_impacts(event, character)

        # Apply impacts
        applied_impacts = []
        for impact in impacts:
            try:
                # Store the current state for possible reversion
                current_state = self._get_state_snapshot(character, impact.impact_type)
                impact.reversion_data = current_state

                # Apply the impact
                await self._apply_impact(impact, character)
                impact.applied = True
                impact.applied_at = datetime.utcnow()
                await self._impact_repo.update(impact.id, impact)
                applied_impacts.append(impact)

            except Exception as e:
                # If any impact fails, revert all previous impacts
                for applied in applied_impacts:
                    await self._revert_impact(applied, character)
                raise EventApplicationError(f"Failed to apply event {event_id}: {str(e)}")

        # Mark event as applied
        event.applied = True
        event.applied_at = datetime.utcnow()
        await self._event_repo.update(event.id, event)

        # Create new state version after applying event
        await self._version_manager.create_version(character, parent_version=None)

        return applied_impacts

    async def revert_event(
        self,
        event_id: UUID,
    ) -> List[EventImpact]:
        """Revert all impacts of a campaign event."""
        # Get event
        event = await self._event_repo.get(event_id)
        if not event:
            raise EventNotFoundError(f"Event {event_id} not found")

        if not event.applied:
            return []  # Not applied yet

        # Get character
        character = await self._char_repo.get(event.character_id)
        if not character:
            raise CharacterNotFoundError(f"Character {event.character_id} not found")

        # Get all impacts for this event
        impacts = await self._impact_repo.get_event_impacts(event_id, include_reverted=False)
        reverted_impacts = []

        # Revert impacts in reverse order
        for impact in reversed(impacts):
            await self._revert_impact(impact, character)
            reverted_impacts.append(impact)

        # Mark event as not applied
        event.applied = False
        event.applied_at = None
        await self._event_repo.update(event.id, event)

        # Create new state version after reversion
        await self._version_manager.create_version(character, parent_version=None)

        return reverted_impacts

    async def get_character_events(
        self,
        character_id: UUID,
        include_deleted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[CampaignEvent]:
        """Get all events for a character."""
        return await self._event_repo.get_character_events(
            character_id,
            include_deleted=include_deleted,
            limit=limit,
            offset=offset,
        )

    async def get_character_impacts(
        self,
        character_id: UUID,
        include_reverted: bool = False,
        limit: int = 100,
        offset: int = 0,
    ) -> List[EventImpact]:
        """Get all impacts for a character."""
        return await self._impact_repo.get_character_impacts(
            character_id,
            include_reverted=include_reverted,
            limit=limit,
            offset=offset,
        )

    async def _calculate_impacts(
        self,
        event: CampaignEvent,
        character: Character,
    ) -> List[EventImpact]:
        """Calculate the impacts of an event on a character."""
        impacts = []

        # Calculate appropriate impacts based on event type and magnitude
        impact = EventImpact(
            id=uuid4(),
            event_id=event.id,
            character_id=character.id,
            impact_type=event.impact_type,
            impact_data=self._get_impact_data(event, character),
        )
        impacts.append(impact)

        # Store impacts
        for impact in impacts:
            await self._impact_repo.create(impact)

        return impacts

    def _get_impact_data(self, event: CampaignEvent, character: Character) -> Dict:
        """Get impact data based on event type and character state."""
        if event.impact_type == "experience":
            return {
                "amount": event.impact_magnitude,
                "source": event.event_type,
                "reason": event.event_data.get("reason", ""),
            }
        elif event.impact_type == "ability_score":
            return {
                "ability": event.event_data["ability"],
                "adjustment": event.impact_magnitude,
            }
        elif event.impact_type == "hit_points":
            return {
                "amount": event.impact_magnitude,
                "type": event.event_data.get("damage_type", ""),
            }
        # Add more impact types as needed
        return {}

    def _get_state_snapshot(self, character: Character, impact_type: str) -> Dict:
        """Get a snapshot of the current state for potential reversion."""
        if impact_type == "experience":
            return {"experience_points": character.character_data.get("experience_points", 0)}
        elif impact_type == "ability_score":
            return {"ability_scores": character.character_data.get("ability_scores", {})}
        elif impact_type == "hit_points":
            return {"hit_points": character.character_data.get("hit_points", {})}
        # Add more state snapshots as needed
        return {}

    async def _apply_impact(self, impact: EventImpact, character: Character) -> None:
        """Apply an impact to a character."""
        if impact.impact_type == "experience":
            await self._apply_experience_impact(impact, character)
        elif impact.impact_type == "ability_score":
            await self._apply_ability_score_impact(impact, character)
        elif impact.impact_type == "hit_points":
            await self._apply_hit_points_impact(impact, character)
        # Add more impact type handlers as needed

    async def _revert_impact(self, impact: EventImpact, character: Character) -> None:
        """Revert an impact on a character."""
        if not impact.reversion_data:
            return

        if impact.impact_type == "experience":
            character.character_data["experience_points"] = impact.reversion_data["experience_points"]
        elif impact.impact_type == "ability_score":
            character.character_data["ability_scores"] = impact.reversion_data["ability_scores"]
        elif impact.impact_type == "hit_points":
            character.character_data["hit_points"] = impact.reversion_data["hit_points"]
        # Add more reversion handlers as needed

        await self._char_repo.update(character.id, character)
        await self._impact_repo.mark_reverted(impact.id, impact.reversion_data)

    async def _apply_experience_impact(self, impact: EventImpact, character: Character) -> None:
        """Apply an experience impact to a character."""
        current_xp = character.character_data.get("experience_points", 0)
        character.character_data["experience_points"] = current_xp + impact.impact_data["amount"]
        await self._char_repo.update(character.id, character)

    async def _apply_ability_score_impact(self, impact: EventImpact, character: Character) -> None:
        """Apply an ability score impact to a character."""
        ability = impact.impact_data["ability"]
        adjustment = impact.impact_data["adjustment"]
        current_score = character.character_data["ability_scores"].get(ability, 10)
        character.character_data["ability_scores"][ability] = current_score + adjustment
        await self._char_repo.update(character.id, character)

    async def _apply_hit_points_impact(self, impact: EventImpact, character: Character) -> None:
        """Apply a hit points impact to a character."""
        amount = impact.impact_data["amount"]
        current_hp = character.character_data["hit_points"]["current"]
        character.character_data["hit_points"]["current"] = max(
            0,
            min(
                current_hp + amount,
                character.character_data["hit_points"]["maximum"]
            )
        )
        await self._char_repo.update(character.id, character)
