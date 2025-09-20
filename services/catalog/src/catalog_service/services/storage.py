"""Storage operations through Message Hub."""

import asyncio
import logging
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from catalog_service.core.exceptions import StorageServiceError
from catalog_service.core.message_hub import MessageHub
from catalog_service.models import ContentType
from catalog_service.models.storage import (
    StorageOperation,
    StorageRequest,
    StorageResponse,
    SchemaDefinition,
    CollectionSchema,
    CollectionIndex,
)

logger = logging.getLogger(__name__)

class StorageManager:
    """Manager for storage operations through Message Hub."""

    def __init__(self, message_hub: MessageHub) -> None:
        """Initialize the storage manager.
        
        Args:
            message_hub: Message Hub instance
        """
        self.message_hub = message_hub
        self._pending_requests: Dict[UUID, asyncio.Future[StorageResponse]] = {}

    async def initialize_schema(self) -> None:
        """Initialize catalog database schema."""
        logger.info("Initializing catalog database schema")

        # Define indexes for different content types
        schema = SchemaDefinition(
            collections={
                ContentType.ITEM.value: CollectionSchema(
                    indexes={
                        "name_idx": CollectionIndex(
                            fields=["name"],
                            unique=False
                        ),
                        "source_idx": CollectionIndex(
                            fields=["source"],
                            unique=False
                        ),
                        "category_idx": CollectionIndex(
                            fields=["properties.category"],
                            unique=False
                        ),
                        "themes_idx": CollectionIndex(
                            fields=["theme_data.themes"],
                            unique=False
                        ),
                    }
                ),
                ContentType.SPELL.value: CollectionSchema(
                    indexes={
                        "name_idx": CollectionIndex(
                            fields=["name"],
                            unique=False
                        ),
                        "source_idx": CollectionIndex(
                            fields=["source"],
                            unique=False
                        ),
                        "level_idx": CollectionIndex(
                            fields=["properties.level"],
                            unique=False
                        ),
                        "school_idx": CollectionIndex(
                            fields=["properties.school"],
                            unique=False
                        ),
                        "themes_idx": CollectionIndex(
                            fields=["theme_data.themes"],
                            unique=False
                        ),
                    }
                ),
                ContentType.MONSTER.value: CollectionSchema(
                    indexes={
                        "name_idx": CollectionIndex(
                            fields=["name"],
                            unique=False
                        ),
                        "source_idx": CollectionIndex(
                            fields=["source"],
                            unique=False
                        ),
                        "cr_idx": CollectionIndex(
                            fields=["properties.challenge_rating"],
                            unique=False
                        ),
                        "type_idx": CollectionIndex(
                            fields=["properties.monster_type"],
                            unique=False
                        ),
                        "themes_idx": CollectionIndex(
                            fields=["theme_data.themes"],
                            unique=False
                        ),
                    }
                ),
            }
        )

        request = StorageRequest(
            operation=StorageOperation.SCHEMA_INIT,
            database="catalog_db",
            collection="_schema",  # Special collection for schema operations
            request_id=uuid4(),
            schema=schema
        )

        try:
            response = await self._execute_operation(request)
            if not response.success:
                raise StorageServiceError(
                    f"Failed to initialize schema: {response.error}"
                )
            logger.info("Successfully initialized catalog database schema")
            
        except Exception as e:
            logger.error(f"Schema initialization failed: {e}")
            raise StorageServiceError(str(e))

    async def store_content(
        self, content_type: ContentType, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Store content in catalog.
        
        Args:
            content_type: Type of content
            data: Content data
            
        Returns:
            Stored content data
        """
        request = StorageRequest(
            operation=StorageOperation.CREATE,
            collection=str(content_type),
            request_id=uuid4(),
            data=data
        )

        response = await self._execute_operation(request)
        if not response.success:
            raise StorageServiceError(
                f"Failed to store {content_type} content: {response.error}"
            )
        return response.data

    async def get_content(
        self, content_type: ContentType, content_id: UUID
    ) -> Optional[Dict[str, Any]]:
        """Retrieve content from catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
            
        Returns:
            Content data if found
        """
        request = StorageRequest(
            operation=StorageOperation.READ,
            collection=str(content_type),
            request_id=uuid4(),
            entity_id=content_id
        )

        response = await self._execute_operation(request)
        return response.data if response.success else None

    async def update_content(
        self, content_type: ContentType, content_id: UUID, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Update content in catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
            data: Updated content data
            
        Returns:
            Updated content data if successful
        """
        request = StorageRequest(
            operation=StorageOperation.UPDATE,
            collection=str(content_type),
            request_id=uuid4(),
            entity_id=content_id,
            data=data
        )

        response = await self._execute_operation(request)
        return response.data if response.success else None

    async def delete_content(
        self, content_type: ContentType, content_id: UUID
    ) -> bool:
        """Delete content from catalog.
        
        Args:
            content_type: Type of content
            content_id: Content UUID
            
        Returns:
            True if deleted successfully
        """
        request = StorageRequest(
            operation=StorageOperation.DELETE,
            collection=str(content_type),
            request_id=uuid4(),
            entity_id=content_id
        )

        response = await self._execute_operation(request)
        return response.success

    async def _execute_operation(
        self, request: StorageRequest, timeout: float = 30.0
    ) -> StorageResponse:
        """Execute storage operation via Message Hub.
        
        Args:
            request: Storage operation request
            timeout: Operation timeout in seconds
            
        Returns:
            Operation response
            
        Raises:
            StorageServiceError: If operation fails or times out
        """
        # Create future for response
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[request.request_id] = future

        try:
            # Send request through Message Hub
            await self.message_hub.publish_storage_request(request)

            # Wait for response
            try:
                response = await asyncio.wait_for(future, timeout)
                return response
            except asyncio.TimeoutError:
                raise StorageServiceError("Storage operation timed out")

        finally:
            self._pending_requests.pop(request.request_id, None)

    async def handle_storage_response(self, response: StorageResponse) -> None:
        """Handle storage operation response from Message Hub.
        
        Args:
            response: Storage operation response
        """
        future = self._pending_requests.get(response.request_id)
        if future and not future.done():
            future.set_result(response)