"""Base repository implementation."""
from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.infrastructure.models.base import Base

DomainModelType = TypeVar("DomainModelType")
PersistenceModelType = TypeVar("PersistenceModelType", bound=Base)


class BaseRepository(Generic[DomainModelType, PersistenceModelType]):
    """Base repository class."""

    def __init__(self, session: AsyncSession, persistence_class: Type[PersistenceModelType], domain_class: Type[DomainModelType]):
        self._session = session
        self._persistence_class = persistence_class
        self._domain_class = domain_class

    def _to_domain(self, persistence_model: PersistenceModelType) -> DomainModelType:
        """Convert persistence model to domain model."""
        raise NotImplementedError("Subclasses must implement _to_domain")

    def _to_persistence(self, domain_model: DomainModelType) -> PersistenceModelType:
        """Convert domain model to persistence model."""
        raise NotImplementedError("Subclasses must implement _to_persistence")

    async def get(self, entity_id: UUID) -> Optional[DomainModelType]:
        query = select(self._persistence_class).where(
            self._persistence_class.id == entity_id,
            self._persistence_class.is_deleted == False,
        )
        result = await self._session.execute(query)
        entity = result.scalar_one_or_none()
        return self._to_domain(entity) if entity else None

    async def get_all(self) -> List[DomainModelType]:
        query = select(self._persistence_class).where(
            self._persistence_class.is_deleted == False,
        )
        result = await self._session.execute(query)
        entities = result.scalars().all()
        return [self._to_domain(entity) for entity in entities]

    async def create(self, entity: DomainModelType) -> DomainModelType:
        persistence_model = self._to_persistence(entity)
        self._session.add(persistence_model)
        await self._session.flush()
        return self._to_domain(persistence_model)

    async def update(self, entity: DomainModelType) -> DomainModelType:
        persistence_model = self._to_persistence(entity)
        self._session.add(persistence_model)
        persistence_model.updated_at = datetime.utcnow()
        await self._session.flush()
        return self._to_domain(persistence_model)

    async def delete(self, entity_id: UUID) -> bool:
        query = update(self._persistence_class).where(
            self._persistence_class.id == entity_id,
            self._persistence_class.is_deleted == False,
        ).values(
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )
        result = await self._session.execute(query)
        return result.rowcount > 0
