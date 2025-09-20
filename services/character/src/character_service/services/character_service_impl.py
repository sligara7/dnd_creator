"""Character service implementation using storage port."""

from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from character_service.clients.storage_port import StoragePort, CharacterData
from character_service.services.interfaces import CharacterService

class CharacterServiceImpl(CharacterService):
    """Character service implementation."""

    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def create_character(
        self,
        name: str,
        theme: str,
        user_id: UUID,
        campaign_id: UUID,
        character_data: Optional[Dict] = None,
    ) -> CharacterData:
        """Create a new character."""
        data = CharacterData(
            name=name,
            theme=theme,
            user_id=user_id,
            campaign_id=campaign_id,
            data=character_data or {},
            is_active=True,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        return await self.storage.create_character(data)

    async def get_character(self, character_id: UUID) -> Optional[CharacterData]:
        """Get character by ID."""
        return await self.storage.get_character(character_id)

    async def get_characters_by_user(self, user_id: UUID) -> List[CharacterData]:
        """Get all active characters for a user."""
        return await self.storage.list_characters(
            user_id=user_id,
            active_only=True
        )

    async def get_characters_by_campaign(self, campaign_id: UUID) -> List[CharacterData]:
        """Get all active characters in a campaign."""
        return await self.storage.list_characters(
            campaign_id=campaign_id,
            active_only=True
        )

    async def update_character(self, character: CharacterData) -> CharacterData:
        """Update existing character."""
        return await self.storage.update_character(
            character_id=character.character_id,
            data=character.model_dump(exclude={"character_id", "created_at", "updated_at"})
        )

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete character."""
        return await self.storage.delete_character(character_id)