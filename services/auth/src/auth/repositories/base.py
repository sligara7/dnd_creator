"""Base repository for auth service."""
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel

from auth.clients.storage import StorageClient
from auth.core.exceptions import StorageError

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)


class BaseRepository(Generic[ModelType, CreateSchemaType, UpdateSchemaType], ABC):
    """Base repository with common CRUD operations.

    Args:
        model_type: Response model class
        storage_client: Storage service client
    """

    def __init__(
        self,
        model_type: Type[ModelType],
        storage_client: StorageClient
    ) -> None:
        """Initialize base repository.

        Args:
            model_type: Response model class
            storage_client: Storage service client
        """
        self.model_type = model_type
        self.storage_client = storage_client

    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        """Create new record.

        Args:
            obj_in: Creation model

        Returns:
            Created record

        Raises:
            StorageError: If creation fails
        """
        pass

    @abstractmethod
    async def get(self, id: UUID) -> Optional[ModelType]:
        """Get record by ID.

        Args:
            id: Record ID

        Returns:
            Record if found, None otherwise

        Raises:
            StorageError: If retrieval fails
        """
        pass

    @abstractmethod
    async def update(
        self,
        id: UUID,
        obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        """Update record.

        Args:
            id: Record ID
            obj_in: Update model

        Returns:
            Updated record if found, None otherwise

        Raises:
            StorageError: If update fails
        """
        pass

    @abstractmethod
    async def delete(self, id: UUID) -> bool:
        """Delete record.

        Args:
            id: Record ID

        Returns:
            True if deleted, False if not found

        Raises:
            StorageError: If deletion fails
        """
        pass