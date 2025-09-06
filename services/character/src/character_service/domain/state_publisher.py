"""State publication service for character state changes."""
from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from character_service.domain.event import EventImpactService
from character_service.domain.messages import (
    CharacterStateMessage,
    CampaignEventMessage,
    Message,
    MessageType,
    ProgressEventMessage,
)
from character_service.domain.models import Character, CampaignEvent, EventImpact
from character_service.infrastructure.messaging.hub_client import MessageHubClient


class StatePublisher:
    """Handles publishing character state changes to the Message Hub."""

    def __init__(
        self,
        message_hub: MessageHubClient,
        event_service: EventImpactService,
    ) -> None:
        """Initialize the state publisher."""
        self._message_hub = message_hub
        self._event_service = event_service
        self._setup_handlers()

    async def publish_message(self, message: Message) -> None:
        """Publish a prepared message via the Message Hub."""
        await self._message_hub.publish(message)

    async def create_state_message(
        self,
        character: Character,
        previous_data: Optional[Dict[str, Any]] = None,
    ) -> CharacterStateMessage:
        """Create a CharacterStateMessage for the given character."""
        state_changes = None
        if previous_data is not None:
            state_changes = self._calculate_state_changes(previous_data, character.character_data)

        return CharacterStateMessage(
            id=uuid4(),
            type=MessageType.CHARACTER_UPDATED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            state_version=self._get_state_version(character),
            state_data=character.character_data,
            previous_version=self._get_state_version(character) - 1 if self._get_state_version(character) > 1 else 0,
            state_changes=state_changes or {},
        )

    def _setup_handlers(self) -> None:
        """Set up message handlers for incoming messages."""
        self._message_hub.subscribe(
            MessageType.CAMPAIGN_EVENT_CREATED,
            self._handle_campaign_event,
        )
        self._message_hub.subscribe(
            MessageType.STATE_SYNC_REQUESTED,
            self._handle_sync_request,
        )

    async def publish_character_created(
        self,
        character: Character,
    ) -> None:
        """Publish character creation event."""
        message = CharacterStateMessage(
            id=uuid4(),
            type=MessageType.CHARACTER_CREATED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            state_version=1,
            state_data=character.character_data,
            previous_version=0,
            state_changes={},
        )
        await self._message_hub.publish(message)

    async def publish_character_updated(
        self,
        character: Character,
        previous_data: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Publish character update event."""
        # Calculate state changes if previous data available
        state_changes = None
        if previous_data:
            state_changes = self._calculate_state_changes(
                previous_data,
                character.character_data,
            )

        message = CharacterStateMessage(
            id=uuid4(),
            type=MessageType.CHARACTER_UPDATED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            state_version=self._get_state_version(character),
            state_data=character.character_data,
            previous_version=self._get_state_version(character) - 1 if self._get_state_version(character) > 1 else 0,
            state_changes=state_changes or {},
        )
        await self._message_hub.publish(message)

    async def publish_experience_gained(
        self,
        character: Character,
        amount: int,
        source: str,
        reason: str,
    ) -> None:
        """Publish experience gain event."""
        message = ProgressEventMessage(
            id=uuid4(),
            type=MessageType.EXPERIENCE_GAINED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            progress_type="experience",
            progress_data={
                "amount": amount,
                "source": source,
                "reason": reason,
            },
            experience_points=character.character_data.get("experience_points", 0),
            current_level=character.character_data.get("level", 1),
        )
        await self._message_hub.publish(message)

    async def publish_level_changed(
        self,
        character: Character,
        previous_level: int,
        new_level: int,
    ) -> None:
        """Publish level change event."""
        message = ProgressEventMessage(
            id=uuid4(),
            type=MessageType.LEVEL_CHANGED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            progress_type="level",
            progress_data={
                "previous_level": previous_level,
                "new_level": new_level,
                "class": character.character_data.get("character_class", ""),
            },
            experience_points=character.character_data.get("experience_points", 0),
            current_level=new_level,
        )
        await self._message_hub.publish(message)

    async def publish_milestone_achieved(
        self,
        character: Character,
        milestone_id: UUID,
        title: str,
        milestone_type: str,
    ) -> None:
        """Publish milestone achievement event."""
        message = ProgressEventMessage(
            id=uuid4(),
            type=MessageType.MILESTONE_ACHIEVED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            progress_type="milestone",
            progress_data={
                "milestone_id": str(milestone_id),
                "title": title,
                "type": milestone_type,
            },
            experience_points=character.character_data.get("experience_points", 0),
            current_level=character.character_data.get("level", 1),
        )
        await self._message_hub.publish(message)

    async def publish_achievement_unlocked(
        self,
        character: Character,
        achievement_id: UUID,
        title: str,
        achievement_type: str,
    ) -> None:
        """Publish achievement unlock event."""
        message = ProgressEventMessage(
            id=uuid4(),
            type=MessageType.ACHIEVEMENT_UNLOCKED,
            timestamp=datetime.utcnow(),
            version="1.0",
            metadata={},
            character_id=character.id,
            progress_type="achievement",
            progress_data={
                "achievement_id": str(achievement_id),
                "title": title,
                "type": achievement_type,
            },
            experience_points=character.character_data.get("experience_points", 0),
            current_level=character.character_data.get("level", 1),
        )
        await self._message_hub.publish(message)

    async def _handle_campaign_event(
        self,
        message: CampaignEventMessage,
    ) -> None:
        """Handle incoming campaign events."""
        # Create local event record
        event = CampaignEvent(
            id=message.event_id,
            character_id=message.character_id,
            event_type=message.event_type,
            event_data=message.event_data,
            impact_type=self._determine_impact_type(message.event_type),
            impact_magnitude=self._calculate_impact_magnitude(message.event_data),
            timestamp=message.timestamp,
        )

        # Process event through event service
        impacts = await self._event_service.apply_event(event.id)

        # Publish state changes if any impacts were applied
        if impacts:
            # Get updated character state
            character = await self._event_service._char_repo.get(message.character_id)
            if character:
                await self.publish_character_updated(character)

    async def _handle_sync_request(
        self,
        message: CharacterStateMessage,
    ) -> None:
        """Handle state sync requests."""
        character = await self._event_service._char_repo.get(message.character_id)
        if character:
            await self.publish_character_updated(character)

    def _calculate_state_changes(
        self,
        previous: Dict[str, Any],
        current: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Calculate changes between two states."""
        changes = {}
        for key in current:
            if key not in previous or previous[key] != current[key]:
                changes[key] = {
                    "old": previous.get(key),
                    "new": current[key],
                }
        return changes

    def _get_state_version(self, character: Character) -> int:
        """Get the current state version for a character.
        
        This is a placeholder - in a real implementation, we'd track versions
        explicitly in the database.
        """
        return 1  # Replace with actual version tracking

    def _determine_impact_type(self, event_type: str) -> str:
        """Determine impact type from event type."""
        impact_types = {
            "combat": "hit_points",
            "rest": "hit_points",
            "quest": "experience",
            "training": "ability_score",
            "story": "milestone",
        }
        return impact_types.get(event_type, "other")

    def _calculate_impact_magnitude(self, event_data: Dict[str, Any]) -> int:
        """Calculate impact magnitude from event data."""
        if "damage" in event_data:
            return -event_data["damage"]
        elif "healing" in event_data:
            return event_data["healing"]
        elif "experience" in event_data:
            return event_data["experience"]
        return 0
