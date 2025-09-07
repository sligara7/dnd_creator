"""Base repository with common database operations"""

from datetime import datetime
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from search_service.models.database import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository providing common CRUD operations"""

    def __init__(self, db: AsyncSession, model: Type[T]) -> None:
        """Initialize repository with database session and model
        
        Args:
            db: Async database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model

    async def get(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID, excluding soft deleted
        
        Args:
            entity_id: UUID of the entity
            
        Returns:
            Entity if found and not deleted, None otherwise
        """
        query = select(self.model).where(
            self.model.id == entity_id,
            self.model.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[T]:
        """Get all entities with pagination, excluding soft deleted
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            filters: Additional filter conditions
            
        Returns:
            List of entities
        """
        query = select(self.model).where(self.model.is_deleted == False)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def create(self, entity: T) -> T:
        """Create new entity
        
        Args:
            entity: Entity to create
            
        Returns:
            Created entity with generated ID
        """
        self.db.add(entity)
        await self.db.flush()
        await self.db.refresh(entity)
        return entity

    async def update(self, entity_id: UUID, update_data: Dict[str, Any]) -> Optional[T]:
        """Update entity by ID
        
        Args:
            entity_id: UUID of the entity to update
            update_data: Dictionary of fields to update
            
        Returns:
            Updated entity if found, None otherwise
        """
        # Add updated_at timestamp
        update_data["updated_at"] = datetime.utcnow()
        
        query = update(self.model).where(
            self.model.id == entity_id,
            self.model.is_deleted == False
        ).values(**update_data).returning(self.model)
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.scalar_one_or_none()

    async def soft_delete(self, entity_id: UUID) -> bool:
        """Soft delete entity by ID
        
        Args:
            entity_id: UUID of the entity to delete
            
        Returns:
            True if deleted, False if not found
        """
        query = update(self.model).where(
            self.model.id == entity_id,
            self.model.is_deleted == False
        ).values(
            is_deleted=True,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        await self.db.commit()
        
        return result.rowcount > 0

    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists and is not deleted
        
        Args:
            entity_id: UUID of the entity
            
        Returns:
            True if exists and not deleted, False otherwise
        """
        query = select(self.model.id).where(
            self.model.id == entity_id,
            self.model.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None

    async def count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count entities matching filters
        
        Args:
            filters: Optional filter conditions
            
        Returns:
            Count of matching entities
        """
        from sqlalchemy import func
        
        query = select(func.count(self.model.id)).where(
            self.model.is_deleted == False
        )
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    query = query.where(getattr(self.model, key) == value)
        
        result = await self.db.execute(query)
        return result.scalar() or 0
