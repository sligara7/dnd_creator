"""Content management service."""

import logging
from typing import Optional
from uuid import UUID

from fastapi import Depends

from catalog_service.models import BaseContent, ContentType
from catalog_service.core.exceptions import StorageServiceError
from catalog_service.core.message_hub import MessageHub, get_message_hub
from catalog_service.config import settings

logger = logging.getLogger(__name__)

class ContentService:
    """Service for managing catalog content."""

    def __init__(self, message_hub: MessageHub) -> None:
        """Initialize the content service.
        
        Args:
            message_hub: Message Hub instance
        """
        self.message_hub = message_hub

    async def get_content(
        self, type: ContentType, id: UUID
    ) -> Optional[BaseContent]:
        """Get content by ID.
        
        Args:
            type: Content type
            id: Content UUID

        Returns:
            Content if found, None otherwise
        """
        data = await self.message_hub.get_content(type, id)
        return BaseContent.parse_obj(data) if data else None

    async def create_content(
        self, type: ContentType, content: BaseContent
    ) -> BaseContent:
        """Create new content.
        
        Args:
            type: Content type
            content: Content data

        Returns:
            Created content
        """
        data = await self.message_hub.store_content(type, content)
        created = BaseContent.parse_obj(data)
        
        # Publish creation event
        await self.message_hub.publish_event(
            "created",
            type,
            created.id,
            created.model_dump()
        )
        
        return created

    async def update_content(
        self, type: ContentType, id: UUID, content: BaseContent
    ) -> Optional[BaseContent]:
        """Update existing content.
        
        Args:
            type: Content type
            id: Content UUID
            content: Updated content data

        Returns:
            Updated content if successful, None otherwise
        """
        data = await self.message_hub.update_content(type, id, content)
        if not data:
            return None
            
        updated = BaseContent.parse_obj(data)
        
        # Publish update event
        await self.message_hub.publish_event(
            "updated",
            type,
            updated.id,
            updated.model_dump()
        )
        
        return updated

    async def delete_content(
        self, type: ContentType, id: UUID
    ) -> bool:
        """Delete content by ID.
        
        Args:
            type: Content type
            id: Content UUID

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get content before deletion for event data
            content = await self.get_content(type, id)
            if not content:
                return False
            
            # Delete from storage
            success = await self.message_hub.delete_content(type, id)
            if not success:
                return False
            
            # Publish deletion event
            await self.message_hub.publish_event(
                "deleted",
                type,
                id,
                content.model_dump()
            )
            
            return True
        except StorageServiceError:
            return False

async def get_content_service(
    message_hub: MessageHub = Depends(get_message_hub)
) -> ContentService:
    """FastAPI dependency for content service.
    
    Args:
        message_hub: Message Hub instance
    
    Returns:
        ContentService instance
    """
    return ContentService(message_hub)
