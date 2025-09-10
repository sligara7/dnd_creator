"""Base repository pattern implementation."""
from datetime import datetime, UTC
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import DeletedEntityError
from campaign_service.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Base repository class with default implementation."""

    def __init__(self, db: AsyncSession, model: Type[ModelType]) -> None:
        """Initialize repository.

        Args:
            db (AsyncSession): Database session
            model (Type[ModelType]): Model class
        """
        self.db = db
        self.model = model

    async def get(self, entity_id: UUID) -> Optional[ModelType]:
        """Get entity by ID.

        Args:
            entity_id (UUID): Entity ID

        Returns:
            Optional[ModelType]: Entity if found, None otherwise
        """
        query = select(self.model).where(
            self.model.id == entity_id,
            self.model.is_deleted == False,  # noqa: E712
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[ModelType]:
        """Get multiple entities.

        Args:
            skip (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Maximum number of records. Defaults to 100.
            **filters: Additional filters to apply

        Returns:
            List[ModelType]: List of entities
        """
        # Add is_deleted filter if not explicitly provided
        if "is_deleted" not in filters:
            filters["is_deleted"] = False

        # Build query with filters
        query = select(self.model)
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)

        # Add pagination
        query = query.offset(skip).limit(limit)

        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, obj_in: dict) -> ModelType:
        """Create new entity.

        Args:
            obj_in (dict): Entity data

        Returns:
            ModelType: Created entity
        """
        db_obj = self.model(**obj_in)
        self.db.add(db_obj)
        await self.db.flush()
        await self.db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        entity_id: UUID,
        obj_in: dict,
    ) -> Optional[ModelType]:
        """Update entity.

        Args:
            entity_id (UUID): Entity ID
            obj_in (dict): Updated entity data

        Returns:
            Optional[ModelType]: Updated entity if found and not deleted, None if not found

        Raises:
            DeletedEntityError: If the entity exists but is soft-deleted
        """
        # First check if entity exists and is deleted
        existing = await self.db.execute(
            select(self.model)
            .where(self.model.id == entity_id)
        )
        entity = existing.scalar_one_or_none()

        if entity is None:
            return None

        if entity.is_deleted:
            raise DeletedEntityError(
                f"Cannot update {self.model.__name__} with ID {entity_id} "
                "because it is marked as deleted"
            )

        # Proceed with update
        obj_in["updated_at"] = datetime.now(UTC)
        query = (
            update(self.model)
            .where(self.model.id == entity_id)
            .values(**obj_in)
            .returning(self.model)
        )
        result = await self.db.execute(query)
        return result.scalar_one()

    async def delete(self, entity_id: UUID) -> bool:
        """Soft delete entity.

        Args:
            entity_id (UUID): Entity ID

        Returns:
            bool: True if entity was deleted, False otherwise
        """
        now = datetime.now(UTC)
        query = (
            update(self.model)
            .where(
                self.model.id == entity_id,
                self.model.is_deleted == False,  # noqa: E712
            )
            .values(
                is_deleted=True,
                deleted_at=now,
                updated_at=now,
            )
        )
        result = await self.db.execute(query)
        return result.rowcount > 0
