"""Storage port interface for campaign service.

This module provides a high-level storage interface that uses Message Hub
for all data operations with the Storage Service's campaign_db.
"""
from datetime import datetime, UTC
from typing import Any, Dict, List, Optional, TypeVar, Generic, Type
from uuid import UUID

from pydantic import BaseModel, model_validator

from ..core.messaging.client import MessageHubClient
from ..storage.exceptions import StorageError


T = TypeVar("T", bound=BaseModel)


class StoragePort(Generic[T]):
    """Storage port for campaign service data operations."""
    
    def __init__(
        self,
        message_hub: MessageHubClient,
        model_class: Type[T],
        database: str = "campaign_db",
    ) -> None:
        """Initialize storage port.
        
        Args:
            message_hub: Message hub client for storage service communication
            model_class: Pydantic model class for entity
            database: Database name in storage service (default: campaign_db)
        """
        self.message_hub = message_hub
        self.model_class = model_class
        self.database = database
        self._table = model_class.model_config.get("table", model_class.__name__.lower())

    async def get(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            Entity if found and not deleted, None otherwise
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            response = await self.message_hub.request(
                "storage.get",
                {
                    "database": self.database,
                    "table": self._table,
                    "id": str(entity_id),
                    "include_deleted": False,
                }
            )
            
            if not response:
                return None

            return self.model_class.model_validate(response["data"])

        except Exception as e:
            raise StorageError(f"Failed to get {self._table}: {str(e)}")

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        **filters: Any,
    ) -> List[T]:
        """Get multiple entities.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            **filters: Additional filters to apply
        
        Returns:
            List of entities
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            # Add is_deleted filter if not explicitly provided
            if "is_deleted" not in filters:
                filters["is_deleted"] = False

            response = await self.message_hub.request(
                "storage.query",
                {
                    "database": self.database,
                    "table": self._table,
                    "filters": filters,
                    "skip": skip,
                    "limit": limit,
                }
            )
            
            if not response:
                return []

            return [
                self.model_class.model_validate(item)
                for item in response["data"]
            ]

        except Exception as e:
            raise StorageError(f"Failed to query {self._table}: {str(e)}")

    async def create(self, data: Dict[str, Any]) -> T:
        """Create new entity.
        
        Args:
            data: Entity data
        
        Returns:
            Created entity
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            # Add timestamps and metadata
            now = datetime.now(UTC).isoformat()
            data["created_at"] = now
            data["updated_at"] = now
            data["is_deleted"] = False

            response = await self.message_hub.request(
                "storage.create",
                {
                    "database": self.database,
                    "table": self._table,
                    "data": data,
                }
            )
            
            if not response or not response.get("data"):
                raise StorageError(f"Failed to create {self._table}: No data returned")

            return self.model_class.model_validate(response["data"])

        except Exception as e:
            raise StorageError(f"Failed to create {self._table}: {str(e)}")

    async def update(
        self,
        entity_id: UUID,
        data: Dict[str, Any],
    ) -> Optional[T]:
        """Update entity.
        
        Args:
            entity_id: Entity ID
            data: Updated entity data
        
        Returns:
            Updated entity if found, None otherwise
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            # Add updated timestamp
            data["updated_at"] = datetime.now(UTC).isoformat()

            response = await self.message_hub.request(
                "storage.update",
                {
                    "database": self.database,
                    "table": self._table,
                    "id": str(entity_id),
                    "data": data,
                }
            )
            
            if not response:
                return None

            return self.model_class.model_validate(response["data"])

        except Exception as e:
            raise StorageError(f"Failed to update {self._table}: {str(e)}")

    async def delete(self, entity_id: UUID) -> bool:
        """Soft delete entity.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            True if entity was deleted, False otherwise
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            now = datetime.now(UTC).isoformat()
            response = await self.message_hub.request(
                "storage.update",
                {
                    "database": self.database,
                    "table": self._table,
                    "id": str(entity_id),
                    "data": {
                        "is_deleted": True,
                        "deleted_at": now,
                        "updated_at": now,
                    }
                }
            )
            
            return bool(response and response.get("success"))

        except Exception as e:
            raise StorageError(f"Failed to delete {self._table}: {str(e)}")

    async def count(self, **filters: Any) -> int:
        """Count matching entities.
        
        Args:
            **filters: Filters to apply
        
        Returns:
            Number of matching entities
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            if "is_deleted" not in filters:
                filters["is_deleted"] = False

            response = await self.message_hub.request(
                "storage.count",
                {
                    "database": self.database,
                    "table": self._table,
                    "filters": filters,
                }
            )
            
            if not response:
                return 0

            return response["count"]

        except Exception as e:
            raise StorageError(f"Failed to count {self._table}: {str(e)}")

    async def exists(self, entity_id: UUID) -> bool:
        """Check if entity exists and is not deleted.
        
        Args:
            entity_id: Entity ID
        
        Returns:
            True if entity exists and is not deleted
        
        Raises:
            StorageError: If storage operation fails
        """
        try:
            response = await self.message_hub.request(
                "storage.exists",
                {
                    "database": self.database,
                    "table": self._table,
                    "id": str(entity_id),
                    "filters": {"is_deleted": False},
                }
            )
            
            if not response:
                return False

            return response["exists"]

        except Exception as e:
            raise StorageError(f"Failed to check existence of {self._table}: {str(e)}")

    async def batch_create(self, items: List[Dict[str, Any]]) -> List[T]:
        """Create multiple entities.
        
        Args:
            items: List of entity data
        
        Returns:
            List of created entities
        
        Raises:
            StorageError: If storage operation fails
        """
        if not items:
            return []

        try:
            # Add timestamps and metadata
            now = datetime.now(UTC).isoformat()
            for item in items:
                item["created_at"] = now
                item["updated_at"] = now
                item["is_deleted"] = False

            response = await self.message_hub.request(
                "storage.batch_create",
                {
                    "database": self.database,
                    "table": self._table,
                    "items": items,
                }
            )
            
            if not response:
                return []

            return [
                self.model_class.model_validate(item)
                for item in response["data"]
            ]

        except Exception as e:
            raise StorageError(f"Failed to batch create {self._table}: {str(e)}")

    async def batch_update(self, updates: List[Dict[str, Any]]) -> List[T]:
        """Update multiple entities.
        
        Args:
            updates: List of updates, each containing id and data
        
        Returns:
            List of updated entities
        
        Raises:
            StorageError: If storage operation fails
        """
        if not updates:
            return []

        try:
            # Add updated timestamp
            now = datetime.now(UTC).isoformat()
            for update in updates:
                update["data"]["updated_at"] = now

            response = await self.message_hub.request(
                "storage.batch_update",
                {
                    "database": self.database,
                    "table": self._table,
                    "updates": updates,
                }
            )
            
            if not response:
                return []

            return [
                self.model_class.model_validate(item)
                for item in response["data"]
            ]

        except Exception as e:
            raise StorageError(f"Failed to batch update {self._table}: {str(e)}")

    async def batch_delete(self, entity_ids: List[UUID]) -> int:
        """Soft delete multiple entities.
        
        Args:
            entity_ids: List of entity IDs to delete
        
        Returns:
            Number of entities deleted
        
        Raises:
            StorageError: If storage operation fails
        """
        if not entity_ids:
            return 0

        try:
            now = datetime.now(UTC).isoformat()
            response = await self.message_hub.request(
                "storage.batch_update",
                {
                    "database": self.database,
                    "table": self._table,
                    "ids": [str(id) for id in entity_ids],
                    "data": {
                        "is_deleted": True,
                        "deleted_at": now,
                        "updated_at": now,
                    }
                }
            )
            
            if not response:
                return 0

            return response["updated_count"]

        except Exception as e:
            raise StorageError(f"Failed to batch delete {self._table}: {str(e)}")