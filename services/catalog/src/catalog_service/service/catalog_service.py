from datetime import datetime
from typing import Dict, List, Optional, Type, Union
from uuid import UUID, uuid4

from catalog_service.core.exceptions import ContentNotFoundError, ValidationError
from catalog_service.core.messaging import MessageHub
from catalog_service.domain.models import (
    BaseContent,
    ContentType,
    Item,
    Monster,
    Spell,
    ValidationResult,
)
from catalog_service.repository.catalog_repository import CatalogRepository
from catalog_service.repository.search_repository import SearchRepository
from catalog_service.service.validation_service import ValidationService


class CatalogService:
    """Core service for catalog operations"""
    def __init__(
        self,
        repository: CatalogRepository,
        search_repository: SearchRepository,
        validation_service: ValidationService,
        message_hub: MessageHub
    ):
        self.repository = repository
        self.search_repository = search_repository
        self.validation_service = validation_service
        self.message_hub = message_hub
        self._content_models = {
            ContentType.ITEM: Item,
            ContentType.SPELL: Spell,
            ContentType.MONSTER: Monster,
        }

    async def get_content(
        self, content_type: ContentType, content_id: UUID
    ) -> Optional[BaseContent]:
        """Get content item by ID"""
        content = await self.repository.get_content(content_type, content_id)
        if not content:
            raise ContentNotFoundError(f"Content not found: {content_id}")
        return content

    async def create_content(
        self,
        content_type: ContentType,
        data: Dict,
    ) -> BaseContent:
        """Create new content item"""
        # Validate content
        model_cls = self._content_models[content_type]
        content_data = {
            "id": uuid4(),
            "type": content_type,
            **data,
            "metadata": {
                "version": "1.0",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "created_by": "system",  # TODO: Get from auth context
            },
        }
        
        # Validate the content
        validation = await self.validation_service.validate_content(
            content_type, content_data
        )
        if not validation.valid:
            raise ValidationError(
                "Content validation failed", 
                validation_errors=validation.issues
            )
            
        content_data["validation"] = {
            "balance_score": validation.balance_score,
            "consistency_check": validation.valid,
            "last_validated": datetime.utcnow(),
        }
        
        # Create the content
        content = model_cls(**content_data)
        await self.repository.create_content(content)
        await self.search_repository.index_content(content)
        
        # Publish event
        await self.message_hub.publish_event(
            "catalog.item.created",
            {
                "content_id": str(content.id),
                "type": content.type,
                "name": content.name,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        return content

    async def update_content(
        self,
        content_type: ContentType,
        content_id: UUID,
        data: Dict,
    ) -> BaseContent:
        """Update existing content item"""
        existing = await self.get_content(content_type, content_id)
        if not existing:
            raise ContentNotFoundError(f"Content not found: {content_id}")

        # Merge updates with existing data
        update_data = {
            **existing.dict(),
            **data,
            "metadata": {
                **existing.metadata.dict(),
                "updated_at": datetime.utcnow(),
            },
        }
        
        # Validate the updated content
        validation = await self.validation_service.validate_content(
            content_type, update_data
        )
        if not validation.valid:
            raise ValidationError(
                "Content validation failed", 
                validation_errors=validation.issues
            )
            
        update_data["validation"] = {
            "balance_score": validation.balance_score,
            "consistency_check": validation.valid,
            "last_validated": datetime.utcnow(),
        }

        # Update the content
        model_cls = self._content_models[content_type]
        updated = model_cls(**update_data)
        await self.repository.update_content(updated)
        await self.search_repository.update_content(updated)
        
        # Publish event
        await self.message_hub.publish_event(
            "catalog.item.updated",
            {
                "content_id": str(updated.id),
                "changes": list(data.keys()),
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        return updated

    async def delete_content(
        self, content_type: ContentType, content_id: UUID
    ) -> bool:
        """Delete content item"""
        content = await self.get_content(content_type, content_id)
        if not content:
            raise ContentNotFoundError(f"Content not found: {content_id}")

        success = await self.repository.delete_content(content_type, content_id)
        if success:
            await self.search_repository.remove_content(content_type, content_id)
            
            # Publish event
            await self.message_hub.publish_event(
                "catalog.item.deleted",
                {
                    "content_id": str(content_id),
                    "type": content_type,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
        return success

    async def search_content(
        self,
        query: str,
        content_type: Optional[ContentType] = None,
        theme: Optional[str] = None,
        page: int = 1,
        size: int = 20,
    ) -> Dict:
        """Search content items"""
        return await self.search_repository.search(
            query,
            content_type=content_type,
            theme=theme,
            page=page,
            size=size,
        )

    async def apply_theme(
        self,
        content_id: UUID,
        theme: str,
        strength: float = 1.0,
        preserve: List[str] = None,
    ) -> BaseContent:
        """Apply theme to content item"""
        content = await self.repository.get_content_by_id(content_id)
        if not content:
            raise ContentNotFoundError(f"Content not found: {content_id}")

        # Apply theme transformations
        content.theme_data.themes.append(theme)
        # TODO: Implement actual theme application logic
        
        await self.repository.update_content(content)
        await self.search_repository.update_content(content)
        
        # Publish event
        await self.message_hub.publish_event(
            "catalog.theme.applied",
            {
                "content_id": str(content_id),
                "theme": theme,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )
        
        return content
