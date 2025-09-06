"""Character repository implementation."""
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.domain.models import Character as CharacterDomain
from character_service.infrastructure.models.models import Character
from character_service.infrastructure.repositories.base import BaseRepository


class CharacterRepository(BaseRepository[CharacterDomain, Character]):
    """Character repository implementation."""

    def __init__(self, session: AsyncSession):
        """Initialize repository."""
        super().__init__(session, Character, CharacterDomain)

    async def get_by_user_id(self, user_id: UUID) -> List[Character]:
        """Get all active characters for a user."""
        query = select(self._persistence_class).where(
            self._persistence_class.user_id == user_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_campaign_id(self, campaign_id: UUID) -> List[Character]:
        """Get all active characters in a campaign."""
        query = select(self._persistence_class).where(
            self._persistence_class.campaign_id == campaign_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_theme(self, theme: str) -> List[Character]:
        """Get all active characters with a specific theme."""
        query = select(self._persistence_class).where(
            self._persistence_class.theme == theme,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def get_by_parent_id(self, parent_id: UUID) -> Optional[Character]:
        """Get character by parent ID."""
        query = select(self._persistence_class).where(
            self._persistence_class.parent_id == parent_id,
            self._persistence_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    def _to_domain(self, model: Character) -> CharacterDomain:
        """Convert database model to domain model."""
        return CharacterDomain(
            id=model.id,
            parent_id=model.parent_id,
            theme=model.theme,
            name=model.name,
            user_id=model.user_id,
            campaign_id=model.campaign_id,
            character_data=model.character_data,
            is_active=model.is_active,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _to_persistence(self, domain: CharacterDomain) -> Character:
        """Convert domain model to database model."""
        return Character(
            id=domain.id,
            parent_id=domain.parent_id,
            theme=domain.theme,
            name=domain.name,
            user_id=domain.user_id,
            campaign_id=domain.campaign_id,
            character_data=domain.character_data,
            is_active=domain.is_active,
            created_at=domain.created_at,
            updated_at=domain.updated_at,
        )
