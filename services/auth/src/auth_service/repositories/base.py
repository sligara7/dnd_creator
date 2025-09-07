"""Base repository for common database operations."""

from datetime import datetime
from typing import Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import and_, select, update, func
from sqlalchemy.ext.asyncio import AsyncSession

from auth_service.models.base import BaseModel

T = TypeVar("T", bound=BaseModel)


class BaseRepository(Generic[T]):
    """Base repository with common CRUD operations."""
    
    def __init__(self, db: AsyncSession, model: Type[T]):
        """
        Initialize base repository.
        
        Args:
            db: Database session
            model: SQLAlchemy model class
        """
        self.db = db
        self.model = model
    
    async def get(self, entity_id: UUID) -> Optional[T]:
        """
        Get entity by ID.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            Entity if found, None otherwise
        """
        query = select(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """
        Get all entities.
        
        Args:
            limit: Maximum number of entities to return
            offset: Number of entities to skip
            
        Returns:
            List of entities
        """
        query = select(self.model).where(
            self.model.is_deleted == False
        ).limit(limit).offset(offset)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create(self, **kwargs) -> T:
        """
        Create new entity.
        
        Args:
            **kwargs: Entity attributes
            
        Returns:
            Created entity
        """
        entity = self.model(**kwargs)
        self.db.add(entity)
        await self.db.flush()
        return entity
    
    async def update(
        self,
        entity_id: UUID,
        **kwargs
    ) -> Optional[T]:
        """
        Update entity.
        
        Args:
            entity_id: Entity UUID
            **kwargs: Fields to update
            
        Returns:
            Updated entity if found, None otherwise
        """
        entity = await self.get(entity_id)
        if not entity:
            return None
        
        for key, value in kwargs.items():
            if hasattr(entity, key):
                setattr(entity, key, value)
        
        entity.updated_at = datetime.utcnow()
        await self.db.flush()
        return entity
    
    async def soft_delete(self, entity_id: UUID) -> bool:
        """
        Soft delete entity.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if deleted successfully
        """
        query = update(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.is_deleted == False
            )
        ).values(
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def restore(self, entity_id: UUID) -> bool:
        """
        Restore soft-deleted entity.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if restored successfully
        """
        query = update(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.is_deleted == True
            )
        ).values(
            is_deleted=False,
            deleted_at=None,
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount > 0
    
    async def exists(self, entity_id: UUID) -> bool:
        """
        Check if entity exists.
        
        Args:
            entity_id: Entity UUID
            
        Returns:
            True if entity exists
        """
        query = select(self.model.id).where(
            and_(
                self.model.id == entity_id,
                self.model.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar() is not None
    
    async def count(self) -> int:
        """
        Count total entities.
        
        Returns:
            Number of entities
        """
        query = select(func.count(self.model.id)).where(
            self.model.is_deleted == False
        )
        
        result = await self.db.execute(query)
        return result.scalar() or 0
    
    async def get_by_ids(self, entity_ids: List[UUID]) -> List[T]:
        """
        Get multiple entities by IDs.
        
        Args:
            entity_ids: List of entity UUIDs
            
        Returns:
            List of found entities
        """
        if not entity_ids:
            return []
        
        query = select(self.model).where(
            and_(
                self.model.id.in_(entity_ids),
                self.model.is_deleted == False
            )
        )
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def delete_batch(self, entity_ids: List[UUID]) -> int:
        """
        Soft delete multiple entities.
        
        Args:
            entity_ids: List of entity UUIDs
            
        Returns:
            Number of entities deleted
        """
        if not entity_ids:
            return 0
        
        query = update(self.model).where(
            and_(
                self.model.id.in_(entity_ids),
                self.model.is_deleted == False
            )
        ).values(
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        result = await self.db.execute(query)
        return result.rowcount
