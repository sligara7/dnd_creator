"""
Core catalog service implementation.
"""

import asyncio
from datetime import datetime
from typing import List, Dict, Any, Optional, Type
from uuid import UUID

from ..models.base import BaseContent, ContentType, ContentSource, ValidationResult
from ..models.content_types import ItemContent, SpellContent, MonsterContent


class CatalogService:
    """Service for managing the unified content catalog."""

    def __init__(self, message_hub_client, search_client, cache_client):
        """Initialize the catalog service with required clients."""
        self.message_hub = message_hub_client
        self.search = search_client
        self.cache = cache_client
        self._content_type_map = {
            ContentType.ITEM: ItemContent,
            ContentType.SPELL: SpellContent,
            ContentType.MONSTER: MonsterContent
        }

    async def get_content(self, content_id: UUID) -> Optional[BaseContent]:
        """Retrieve content by ID."""
        # Try cache first
        cached = await self.cache.get(str(content_id))
        if cached:
            return self._deserialize_content(cached)

        # Fall back to search
        content = await self.search.get_by_id(content_id)
        if content:
            await self.cache.set(str(content_id), content.json())
            return content

        return None

    async def create_content(
        self,
        content_type: ContentType,
        name: str,
        description: str,
        properties: Dict[str, Any],
        source: ContentSource = ContentSource.CUSTOM,
        themes: List[str] = None
    ) -> BaseContent:
        """Create new content in the catalog."""
        content_class = self._content_type_map[content_type]
        content = content_class(
            type=content_type,
            name=name,
            description=description,
            properties=properties,
            source=source,
            theme_data={"themes": themes or []}
        )

        # Validate the content
        validation = await self._validate_content(content)
        content.validation = validation

        # Store and index the content
        await asyncio.gather(
            self.search.index(content),
            self.cache.set(str(content.id), content.json())
        )

        # Publish event
        await self.message_hub.publish("catalog.item.created", {
            "content_id": str(content.id),
            "type": content.type,
            "name": content.name,
            "timestamp": datetime.utcnow().isoformat()
        })

        return content

    async def update_content(
        self,
        content_id: UUID,
        updates: Dict[str, Any]
    ) -> Optional[BaseContent]:
        """Update existing content."""
        content = await self.get_content(content_id)
        if not content:
            return None

        # Apply updates
        for key, value in updates.items():
            if hasattr(content, key):
                setattr(content, key, value)

        # Update metadata
        content.metadata.updated_at = datetime.utcnow()

        # Validate changes
        validation = await self._validate_content(content)
        content.validation = validation

        # Update storage
        await asyncio.gather(
            self.search.update(content),
            self.cache.set(str(content.id), content.json())
        )

        # Publish event
        await self.message_hub.publish("catalog.item.updated", {
            "content_id": str(content.id),
            "changes": list(updates.keys()),
            "timestamp": datetime.utcnow().isoformat()
        })

        return content

    async def delete_content(self, content_id: UUID) -> bool:
        """Delete content from the catalog."""
        content = await self.get_content(content_id)
        if not content:
            return False

        # Remove from storage
        await asyncio.gather(
            self.search.delete(content_id),
            self.cache.delete(str(content_id))
        )

        # Publish event
        await self.message_hub.publish("catalog.item.deleted", {
            "content_id": str(content_id),
            "type": content.type,
            "timestamp": datetime.utcnow().isoformat()
        })

        return True

    async def search_content(
        self,
        query: str = None,
        content_type: ContentType = None,
        themes: List[str] = None,
        page: int = 1,
        size: int = 20
    ) -> Dict[str, Any]:
        """Search the catalog."""
        results = await self.search.search(
            query=query,
            filters={
                "type": content_type.value if content_type else None,
                "themes": themes
            },
            page=page,
            size=size
        )

        return {
            "total": results["total"],
            "page": page,
            "items": [self._deserialize_content(item) for item in results["items"]]
        }

    async def get_recommendations(
        self,
        character_id: Optional[UUID] = None,
        campaign_id: Optional[UUID] = None,
        content_type: Optional[ContentType] = None,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get content recommendations."""
        # Get context from other services via Message Hub
        context = {}
        if character_id:
            char_data = await self.message_hub.request(
                "character.get_context",
                {"character_id": str(character_id)}
            )
            context["character"] = char_data

        if campaign_id:
            campaign_data = await self.message_hub.request(
                "campaign.get_context",
                {"campaign_id": str(campaign_id)}
            )
            context["campaign"] = campaign_data

        # Get recommendations from search service
        results = await self.search.recommend(
            context=context,
            content_type=content_type.value if content_type else None,
            limit=limit
        )

        return [
            {
                "id": item["id"],
                "type": item["type"],
                "name": item["name"],
                "description": item["description"],
                "score": item["score"],
                "reason": item["reason"]
            }
            for item in results
        ]

    async def apply_theme(
        self,
        content_id: UUID,
        theme: str,
        strength: float = 1.0,
        preserve: List[str] = None
    ) -> Optional[BaseContent]:
        """Apply a theme to content."""
        content = await self.get_content(content_id)
        if not content:
            return None

        # Request theme adaptation from LLM service
        adaptation = await self.message_hub.request(
            "llm.adapt_theme",
            {
                "content": content.dict(),
                "theme": theme,
                "strength": strength,
                "preserve": preserve or []
            }
        )

        if not adaptation:
            return None

        # Update content with themed version
        themed_content = self._content_type_map[content.type](**adaptation)
        themed_content.id = content.id  # Preserve ID
        themed_content.metadata = content.metadata  # Preserve metadata
        themed_content.metadata.updated_at = datetime.utcnow()

        # Add theme to theme data
        if theme not in themed_content.theme_data.themes:
            themed_content.theme_data.themes.append(theme)

        # Store updated content
        await asyncio.gather(
            self.search.update(themed_content),
            self.cache.set(str(themed_content.id), themed_content.json())
        )

        # Publish event
        await self.message_hub.publish("catalog.theme.applied", {
            "content_id": str(themed_content.id),
            "theme": theme,
            "timestamp": datetime.utcnow().isoformat()
        })

        return themed_content

    async def _validate_content(self, content: BaseContent) -> ValidationResult:
        """Validate content and return validation result."""
        # Request validation from LLM service
        validation = await self.message_hub.request(
            "llm.validate_content",
            {"content": content.dict()}
        )

        if not validation:
            return ValidationResult()

        result = ValidationResult(
            balance_score=validation.get("balance_score", 0.0),
            consistency_check=validation.get("consistency_check", False),
            last_validated=datetime.utcnow(),
            issues=validation.get("issues", [])
        )

        # Publish validation event
        await self.message_hub.publish("catalog.item.validated", {
            "content_id": str(content.id),
            "valid": result.consistency_check,
            "balance_score": result.balance_score,
            "timestamp": datetime.utcnow().isoformat()
        })

        return result

    def _deserialize_content(self, data: Dict[str, Any]) -> BaseContent:
        """Deserialize content from storage format."""
        if isinstance(data, str):
            import json
            data = json.loads(data)

        content_type = ContentType(data["type"])
        content_class = self._content_type_map[content_type]
        return content_class(**data)
