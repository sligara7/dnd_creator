"""Storage-based repository base class."""
from datetime import datetime, UTC
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from ..core.exceptions import DeletedEntityError
from ..storage import StorageClient, StorageQuery


T = TypeVar("T", bound=BaseModel)


class StorageBaseRepository(Generic[T]):
    """Base repository using storage service."""
    
    def __init__(
        self,
        storage: StorageClient,
        model_class: Type[T],
        table: Optional[str] = None,
    ) -> None:
        """Initialize repository.
        
        Args:
            storage: Storage service client
            model_class: Model class
            table: Optional table name override
        """
        self.storage = storage
        self.model_class = model_class
        self._table = table or self.model_class.__name__.lower()
    
    async def get(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            Entity if found and not deleted
            
        Raises:
            StorageError: If query fails
        """
        result = await self.storage.execute(
            StorageQuery.select(
                table=self._table,
                where={
                    "id": entity_id,
                    "is_deleted": False,
                },
            )
        )
        if not result:
            return None
            
        return self.model_class.model_validate(result[0])
    
    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[T]:
        """Get multiple entities.
        
        Args:
            skip: Number of records to skip
            limit: Maximum records to return
            **filters: Additional filters
            
        Returns:
            List of entities
            
        Raises:
            StorageError: If query fails
        """
        # Add is_deleted filter if not explicitly provided
        if "is_deleted" not in filters:
            filters["is_deleted"] = False
            
        results = await self.storage.execute(
            StorageQuery.select(
                table=self._table,
                where=filters,
                offset=skip,
                limit=limit,
            )
        )
        return [self.model_class.model_validate(r) for r in results]
    
    async def create(self, obj_in: Dict[str, Any]) -> T:
        """Create new entity.
        
        Args:
            obj_in: Entity data
            
        Returns:
            Created entity
            
        Raises:
            StorageError: If create fails
        """
        # Set created_at/updated_at timestamps
        now = datetime.now(UTC).isoformat()
        obj_in["created_at"] = now
        obj_in["updated_at"] = now
        obj_in["is_deleted"] = False
        
        results = await self.storage.execute(
            StorageQuery.insert(
                table=self._table,
                data=obj_in,
            )
        )
        if not results:
            raise RuntimeError("Create returned no results")
            
        return self.model_class.model_validate(results[0])
    
    async def update(
        self,
        entity_id: UUID,
        obj_in: Dict[str, Any],
    ) -> Optional[T]:
        """Update entity.
        
        Args:
            entity_id: Entity ID
            obj_in: Updated entity data
            
        Returns:
            Updated entity if found and not deleted
            
        Raises:
            StorageError: If update fails
            DeletedEntityError: If entity is deleted
        """
        # Check if entity exists and is not deleted
        existing = await self.storage.execute(
            StorageQuery.select(
                table=self._table,
                where={"id": entity_id},
            )
        )
        if not existing:
            return None
            
        if existing[0].get("is_deleted"):
            raise DeletedEntityError(
                f"Cannot update {self._table} with ID {entity_id} "
                "because it is marked as deleted"
            )
            
        # Add updated timestamp
        obj_in["updated_at"] = datetime.now(UTC).isoformat()
        
        results = await self.storage.execute(
            StorageQuery.update(
                table=self._table,
                where={"id": entity_id},
                data=obj_in,
            )
        )
        if not results:
            return None
            
        return self.model_class.model_validate(results[0])
    
    async def delete(self, entity_id: UUID) -> bool:
        """Soft delete entity.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if entity was deleted
            
        Raises:
            StorageError: If delete fails
        """
        now = datetime.now(UTC).isoformat()
        results = await self.storage.execute(
            StorageQuery.update(
                table=self._table,
                where={
                    "id": entity_id,
                    "is_deleted": False,
                },
                data={
                    "is_deleted": True,
                    "deleted_at": now,
                    "updated_at": now,
                },
            )
        )
        return bool(results)
    
    async def count(self, **filters: Any) -> int:
        """Count matching entities.
        
        Args:
            **filters: Filters to apply
            
        Returns:
            Number of matching entities
            
        Raises:
            StorageError: If query fails
        """
        # Add is_deleted filter if not explicitly provided
        if "is_deleted" not in filters:
            filters["is_deleted"] = False
            
        results = await self.storage.execute(
            StorageQuery(
                type="count",
                table=self._table,
                where=filters,
            )
        )
        return results[0]["count"]
    
    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists and is not deleted.
        
        Args:
            entity_id: Entity ID
            
        Returns:
            True if entity exists and is not deleted
            
        Raises:
            StorageError: If query fails
        """
        results = await self.storage.execute(
            StorageQuery(
                type="exists",
                table=self._table,
                where={
                    "id": entity_id,
                    "is_deleted": False,
                },
            )
        )
        return results[0]["exists"]
    
    async def batch_create(self, entities: List[Dict[str, Any]]) -> List[T]:
        """Create multiple entities.
        
        Args:
            entities: List of entity data
            
        Returns:
            Created entities
            
        Raises:
            StorageError: If create fails
        """
        if not entities:
            return []
            
        # Add timestamps to all entities
        now = datetime.now(UTC).isoformat()
        for entity in entities:
            entity["created_at"] = now
            entity["updated_at"] = now
            entity["is_deleted"] = False
            
        results = await self.storage.execute(
            StorageQuery(
                type="bulk_insert",
                table=self._table,
                data=entities,
            )
        )
        return [self.model_class.model_validate(r) for r in results]
    
    async def batch_update(
        self,
        updates: List[Dict[str, Any]],
    ) -> List[T]:
        """Update multiple entities.
        
        Args:
            updates: List of updates, each containing id and data
            
        Returns:
            Updated entities
            
        Raises:
            StorageError: If update fails
        """
        if not updates:
            return []
            
        # Add updated timestamp to all updates
        now = datetime.now(UTC).isoformat()
        for update in updates:
            update["data"]["updated_at"] = now
            
        results = await self.storage.execute(
            StorageQuery(
                type="bulk_update",
                table=self._table,
                data=updates,
            )
        )
        return [self.model_class.model_validate(r) for r in results]
    
    async def batch_delete(self, entity_ids: List[UUID]) -> int:
        """Soft delete multiple entities.
        
        Args:
            entity_ids: Entity IDs to delete
            
        Returns:
            Number of entities deleted
            
        Raises:
            StorageError: If delete fails
        """
        if not entity_ids:
            return 0
            
        now = datetime.now(UTC).isoformat()
        results = await self.storage.execute(
            StorageQuery(
                type="bulk_update",
                table=self._table,
                where={
                    "id": {"$in": [str(i) for i in entity_ids]},
                    "is_deleted": False,
                },
                data={
                    "is_deleted": True,
                    "deleted_at": now,
                    "updated_at": now,
                },
            )
        )
        return len(results)