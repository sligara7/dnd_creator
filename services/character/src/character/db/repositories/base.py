"""Base repository interface.

This module provides the base repository interface and common functionality
for all database repositories in the character service.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import Select

from ...core.errors import RepositoryError
from ...models.base import BaseDBModel

T = TypeVar("T", bound=BaseDBModel)

class BaseRepository(Generic[T], ABC):
    """Base repository interface for database operations.
    
    Args:
        session: SQLAlchemy async session
        model_type: SQLAlchemy model class
    """
    def __init__(self, session: AsyncSession, model_type: Type[T]):
        self.session = session
        self.model_type = model_type
        
    async def create(self, data: Dict[str, Any]) -> T:
        """Create a new record.
        
        Args:
            data: Record data
            
        Returns:
            Created record
            
        Raises:
            RepositoryError: If creation fails
        """
        try:
            instance = self.model_type(**data)
            self.session.add(instance)
            await self.session.flush()
            return instance
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to create {self.model_type.__name__}: {e}")
    
    async def get_by_id(self, id: UUID) -> Optional[T]:
        """Get record by ID.
        
        Args:
            id: Record ID
            
        Returns:
            Record if found, else None
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            stmt = select(self.model_type).where(self.model_type.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none()
            
        except Exception as e:
            raise RepositoryError(f"Failed to get {self.model_type.__name__} {id}: {e}")
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> List[T]:
        """Get all records with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            
        Returns:
            List of records
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            stmt = (
                select(self.model_type)
                .offset(skip)
                .limit(limit)
            )
            result = await self.session.execute(stmt)
            return result.scalars().all()
            
        except Exception as e:
            raise RepositoryError(f"Failed to get {self.model_type.__name__} list: {e}")
    
    async def update(self, id: UUID, data: Dict[str, Any]) -> Optional[T]:
        """Update a record.
        
        Args:
            id: Record ID
            data: Update data
            
        Returns:
            Updated record if found
            
        Raises:
            RepositoryError: If update fails
        """
        try:
            instance = await self.get_by_id(id)
            if not instance:
                return None
                
            for key, value in data.items():
                setattr(instance, key, value)
                
            await self.session.flush()
            return instance
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to update {self.model_type.__name__} {id}: {e}")
    
    async def delete(self, id: UUID) -> bool:
        """Delete a record.
        
        Args:
            id: Record ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            RepositoryError: If deletion fails
        """
        try:
            instance = await self.get_by_id(id)
            if not instance:
                return False
                
            await self.session.delete(instance)
            await self.session.flush()
            return True
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to delete {self.model_type.__name__} {id}: {e}")
    
    async def exists(self, id: UUID) -> bool:
        """Check if record exists.
        
        Args:
            id: Record ID
            
        Returns:
            True if exists
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            stmt = select(self.model_type.id).where(self.model_type.id == id)
            result = await self.session.execute(stmt)
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            raise RepositoryError(f"Failed to check {self.model_type.__name__} {id}: {e}")
    
    async def count(self, condition: Any = None) -> int:
        """Count records matching condition.
        
        Args:
            condition: Optional filter condition
            
        Returns:
            Record count
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            stmt = select(self.model_type.id)
            if condition is not None:
                stmt = stmt.where(condition)
            result = await self.session.execute(stmt)
            return len(result.all())
            
        except Exception as e:
            raise RepositoryError(f"Failed to count {self.model_type.__name__}: {e}")
    
    @abstractmethod
    def build_query(self) -> Select:
        """Build base query for this repository.
        
        Returns:
            SQLAlchemy select statement
        """
        return select(self.model_type)
        
    async def execute_query(self, query: Select) -> List[T]:
        """Execute a custom query.
        
        Args:
            query: SQLAlchemy select statement
            
        Returns:
            Query results
            
        Raises:
            RepositoryError: If query fails
        """
        try:
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except Exception as e:
            raise RepositoryError(f"Failed to execute {self.model_type.__name__} query: {e}")
            
    def _build_filters(self, filters: Dict[str, Any]) -> List[Any]:
        """Build SQLAlchemy filter conditions from dict.
        
        Args:
            filters: Filter parameters
            
        Returns:
            List of filter conditions
        """
        conditions = []
        for field, value in filters.items():
            if isinstance(value, (list, tuple)):
                conditions.append(getattr(self.model_type, field).in_(value))
            else:
                conditions.append(getattr(self.model_type, field) == value)
        return conditions
