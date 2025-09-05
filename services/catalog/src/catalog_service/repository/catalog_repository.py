from datetime import datetime
from typing import List, Optional, Union
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from catalog_service.domain.models import (
    BaseContent,
    ContentType,
    Item,
    Monster,
    Spell,
)
from catalog_service.repository.models import Content, Theme


class CatalogRepository:
    """Repository for catalog operations"""

    def __init__(self, db: AsyncSession):
        self.db = db
        self._model_map = {
            ContentType.ITEM: Item,
            ContentType.SPELL: Spell,
            ContentType.MONSTER: Monster,
        }

    async def get_content(
        self, content_type: ContentType, content_id: UUID
    ) -> Optional[BaseContent]:
        """Get content item by ID and type"""
        query = (
            select(Content)
            .options(joinedload(Content.themes))
            .where(
                Content.id == content_id,
                Content.type == content_type,
                Content.is_deleted == False,
            )
        )
        result = await self.db.execute(query)
        db_content = result.scalar_one_or_none()
        
        if not db_content:
            return None
            
        return self._to_domain_model(db_content)

    async def get_content_by_id(self, content_id: UUID) -> Optional[BaseContent]:
        """Get content item by ID"""
        query = (
            select(Content)
            .options(joinedload(Content.themes))
            .where(Content.id == content_id, Content.is_deleted == False)
        )
        result = await self.db.execute(query)
        db_content = result.scalar_one_or_none()
        
        if not db_content:
            return None
            
        return self._to_domain_model(db_content)

    async def create_content(self, content: BaseContent) -> BaseContent:
        """Create new content item"""
        db_content = Content(
            id=content.id,
            type=content.type,
            name=content.name,
            source=content.source,
            description=content.description,
            properties=content.properties,
            version=content.metadata.version,
            created_at=content.metadata.created_at,
            updated_at=content.metadata.updated_at,
            created_by=content.metadata.created_by,
            theme_adaptations=content.theme_data.adaptations,
            balance_score=content.validation.balance_score,
            consistency_check=content.validation.consistency_check,
            last_validated=content.validation.last_validated,
        )
        
        # Add themes
        if content.theme_data.themes:
            themes = await self._get_themes_by_names(content.theme_data.themes)
            db_content.themes.extend(themes)
        
        self.db.add(db_content)
        await self.db.flush()
        await self.db.refresh(db_content)
        
        return self._to_domain_model(db_content)

    async def update_content(self, content: BaseContent) -> BaseContent:
        """Update existing content item"""
        db_content = await self._get_db_content(content.id)
        if not db_content:
            return None
            
        # Update fields
        db_content.name = content.name
        db_content.description = content.description
        db_content.properties = content.properties
        db_content.updated_at = datetime.utcnow()
        db_content.theme_adaptations = content.theme_data.adaptations
        db_content.balance_score = content.validation.balance_score
        db_content.consistency_check = content.validation.consistency_check
        db_content.last_validated = content.validation.last_validated
        
        # Update themes
        if content.theme_data.themes:
            themes = await self._get_themes_by_names(content.theme_data.themes)
            db_content.themes = themes
        
        await self.db.flush()
        await self.db.refresh(db_content)
        
        return self._to_domain_model(db_content)

    async def delete_content(
        self, content_type: ContentType, content_id: UUID
    ) -> bool:
        """Soft delete content item"""
        db_content = await self._get_db_content(content_id)
        if not db_content or db_content.type != content_type:
            return False
            
        db_content.is_deleted = True
        db_content.deleted_at = datetime.utcnow()
        await self.db.flush()
        
        return True

    async def _get_db_content(self, content_id: UUID) -> Optional[Content]:
        """Get database content model by ID"""
        query = (
            select(Content)
            .options(joinedload(Content.themes))
            .where(Content.id == content_id, Content.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_themes_by_names(self, theme_names: List[str]) -> List[Theme]:
        """Get theme models by names"""
        query = select(Theme).where(Theme.name.in_(theme_names))
        result = await self.db.execute(query)
        return result.scalars().all()

    def _to_domain_model(self, db_content: Content) -> BaseContent:
        """Convert database model to domain model"""
        model_cls = self._model_map[db_content.type]
        
        return model_cls(
            id=db_content.id,
            type=db_content.type,
            name=db_content.name,
            source=db_content.source,
            description=db_content.description,
            properties=db_content.properties,
            metadata={
                "version": db_content.version,
                "created_at": db_content.created_at,
                "updated_at": db_content.updated_at,
                "created_by": db_content.created_by,
            },
            theme_data={
                "themes": [theme.name for theme in db_content.themes],
                "adaptations": db_content.theme_adaptations,
            },
            validation={
                "balance_score": db_content.balance_score,
                "consistency_check": db_content.consistency_check,
                "last_validated": db_content.last_validated,
            },
        )
