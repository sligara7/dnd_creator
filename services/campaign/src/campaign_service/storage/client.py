"""Storage service client implementation."""
import asyncio
from datetime import datetime
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from pydantic import BaseModel

from .exceptions import (
    StorageAuthenticationError,
    StorageConnectionError,
    StorageError,
    StorageNotFoundError,
    StorageQueryError,
    StorageTimeoutError,
    StorageValidationError,
)
from .query import StorageQuery


T = TypeVar("T", bound=BaseModel)


class StorageClient:
    """Client for interacting with storage service."""
    
    def __init__(
        self,
        message_hub: Any,  # MessageHub client
        db_name: str = "campaign_db",
        request_timeout: float = 30.0,
    ) -> None:
        """Initialize storage client.
        
        Args:
            message_hub: Message Hub client
            db_name: Database name in storage service
            request_timeout: Request timeout in seconds
            
        Raises:
            ValueError: If parameters invalid
        """
        self.message_hub = message_hub
        self.db_name = db_name
        self.request_timeout = request_timeout
    
    async def execute(
        self,
        query: Union[StorageQuery, Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Execute storage query.
        
        Args:
            query: Query to execute
            
        Returns:
            Query results
            
        Raises:
            StorageError: If query fails
        """
        if isinstance(query, StorageQuery):
            query = query.model_dump()
            
        try:
            response = await self.message_hub.request(
                "storage.query",
                {
                    "db": self.db_name,
                    "query": query,
                },
                timeout=self.request_timeout,
            )
            
            if "error" in response:
                error = response["error"]
                raise self._get_error(error)
                
            return response.get("results", [])
            
        except asyncio.TimeoutError as e:
            raise StorageTimeoutError(
                "Storage request timed out",
                {"timeout": self.request_timeout},
            ) from e
            
        except Exception as e:
            if isinstance(e, StorageError):
                raise
            raise StorageConnectionError(
                "Failed to execute storage query",
                {"error": str(e)},
            ) from e
    
    async def get(
        self,
        model: Type[T],
        id: UUID,
    ) -> Optional[T]:
        """Get single record by ID.
        
        Args:
            model: Model class
            id: Record ID
            
        Returns:
            Model instance if found
            
        Raises:
            StorageError: If query fails
        """
        query = StorageQuery.select(
            table=model.model_config["table"],
            where={"id": id},
        )
        
        results = await self.execute(query)
        if not results:
            return None
            
        return model.model_validate(results[0])
    
    async def get_all(
        self,
        model: Type[T],
        where: Optional[Dict[str, Any]] = None,
        order_by: Optional[List[str]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[T]:
        """Get multiple records.
        
        Args:
            model: Model class
            where: Filter conditions
            order_by: Sort fields
            limit: Max results
            offset: Result offset
            
        Returns:
            List of model instances
            
        Raises:
            StorageError: If query fails
        """
        query = StorageQuery.select(
            table=model.model_config["table"],
            where=where,
            order_by=order_by,
            limit=limit,
            offset=offset,
        )
        
        results = await self.execute(query)
        return [model.model_validate(r) for r in results]
    
    async def create(
        self,
        model: T,
    ) -> T:
        """Create new record.
        
        Args:
            model: Model instance
            
        Returns:
            Created model instance
            
        Raises:
            StorageError: If create fails
        """
        query = StorageQuery.insert(
            table=model.model_config["table"],
            data=model.model_dump(exclude={"id"} if not model.id else set()),
        )
        
        results = await self.execute(query)
        if not results:
            raise StorageError("Create returned no results")
            
        return model.__class__.model_validate(results[0])
    
    async def update(
        self,
        model: T,
    ) -> T:
        """Update existing record.
        
        Args:
            model: Model instance
            
        Returns:
            Updated model instance
            
        Raises:
            StorageError: If update fails
        """
        if not model.id:
            raise ValueError("Model must have ID for update")
            
        query = StorageQuery.update(
            table=model.model_config["table"],
            where={"id": model.id},
            data=model.model_dump(exclude={"id"}),
        )
        
        results = await self.execute(query)
        if not results:
            raise StorageNotFoundError(f"Record not found: {model.id}")
            
        return model.__class__.model_validate(results[0])
    
    async def delete(
        self,
        model: T,
    ) -> None:
        """Delete record.
        
        Args:
            model: Model instance
            
        Raises:
            StorageError: If delete fails
        """
        if not model.id:
            raise ValueError("Model must have ID for delete")
            
        query = StorageQuery.delete(
            table=model.model_config["table"],
            where={"id": model.id},
        )
        
        await self.execute(query)
    
    async def execute_raw(
        self,
        query_type: str,
        query: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """Execute raw storage query.
        
        Args:
            query_type: Query type
            query: Raw query dict
            
        Returns:
            Query results
            
        Raises:
            StorageError: If query fails
        """
        return await self.execute({
            "type": query_type,
            **query,
        })
    
    @staticmethod
    def _get_error(error: Dict[str, Any]) -> StorageError:
        """Get appropriate error from response.
        
        Args:
            error: Error details from response
            
        Returns:
            StorageError instance
        """
        error_type = error.get("type", "unknown")
        message = error.get("message", "Unknown error")
        details = error.get("details")
        
        error_map = {
            "not_found": StorageNotFoundError,
            "validation": StorageValidationError,
            "authentication": StorageAuthenticationError,
            "query": StorageQueryError,
            "timeout": StorageTimeoutError,
            "connection": StorageConnectionError,
        }
        
        error_class = error_map.get(error_type, StorageError)
        return error_class(message, details)