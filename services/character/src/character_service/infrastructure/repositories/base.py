"""Base repository implementation."""
from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.infrastructure.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class."""

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        """Initialize repository."""
        self._session = session
        self._model_class = model_class

    async def get(self, entity_id: UUID) -> Optional[ModelType]:
        """Get entity by ID."""
        query = select(self._model_class).where(
            self._model_class.id == entity_id,
            self._model_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[ModelType]:
        """Get all active entities."""
        query = select(self._model_class).where(
            self._model_class.is_deleted == False,  # noqa: E712
        )
        result = await self._session.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: ModelType) -> ModelType:
        """Create new entity."""
        self._session.add(entity)
        await self._session.flush()
        return entity

    async def update(self, entity: ModelType) -> ModelType:
        """Update existing entity."""
        self._session.add(entity)
        entity.updated_at = datetime.utcnow()
        await self._session.flush()
        return entity

    async def delete(self, entity_id: UUID) -> bool:
        """Soft delete entity."""
        query = update(self._model_class).where(
            self._model_class.id == entity_id,
            self._model_class.is_deleted == False,  # noqa: E712
        ).values(
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        result = await self._session.execute(query)
        return result.rowcount > 0
