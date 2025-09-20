"""Repository layer for character database."""

from datetime import datetime
from typing import Dict, List, Optional, TypeVar
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.expression import desc

from .models import (
    Character, CharacterCondition, CharacterVersion, ClassResource,
    Inventory, InventoryItem, JournalEntry, Spellcasting, Theme
)

T = TypeVar('T')  # Generic type for entities


class BaseRepository:
    """Base repository with common CRUD operations."""

    def __init__(self, db: AsyncSession, model: T):
        """Initialize with database session and model."""
        self.db = db
        self.model = model

    async def create(self, data: Dict) -> T:
        """Create new entity."""
        entity = self.model(**data)
        self.db.add(entity)
        await self.db.flush()
        return entity

    async def get(self, entity_id: UUID) -> Optional[T]:
        """Get entity by ID."""
        query = select(self.model).where(
            and_(
                self.model.id == entity_id,
                self.model.is_deleted.is_(False) if hasattr(self.model, 'is_deleted') else True
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def update(self, entity_id: UUID, data: Dict) -> Optional[T]:
        """Update entity."""
        entity = await self.get(entity_id)
        if entity:
            for key, value in data.items():
                setattr(entity, key, value)
            await self.db.flush()
        return entity

    async def delete(self, entity_id: UUID, hard_delete: bool = False) -> bool:
        """Delete entity."""
        entity = await self.get(entity_id)
        if entity:
            if hard_delete:
                await self.db.delete(entity)
            elif hasattr(entity, 'is_deleted'):
                entity.is_deleted = True
                entity.deleted_at = datetime.utcnow()
            await self.db.flush()
            return True
        return False

    async def list(
        self,
        filters: Optional[Dict] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[T]:
        """List entities with optional filters."""
        query = select(self.model)

        if filters:
            conditions = []
            for key, value in filters.items():
                if hasattr(self.model, key):
                    conditions.append(getattr(self.model, key) == value)
            if conditions:
                query = query.where(and_(*conditions))

        if hasattr(self.model, 'is_deleted'):
            query = query.where(self.model.is_deleted.is_(False))

        query = query.limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()


class CharacterRepository(BaseRepository):
    """Repository for Character model."""

    def __init__(self, db: AsyncSession):
        """Initialize with Character model."""
        super().__init__(db, Character)

    async def get_by_campaign(
        self,
        campaign_id: UUID,
        include_deleted: bool = False
    ) -> List[Character]:
        """Get all characters in a campaign."""
        query = select(self.model).where(self.model.campaign_id == campaign_id)
        if not include_deleted:
            query = query.where(self.model.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_owner(
        self,
        owner_id: UUID,
        include_deleted: bool = False
    ) -> List[Character]:
        """Get all characters owned by a user."""
        query = select(self.model).where(self.model.owner_id == owner_id)
        if not include_deleted:
            query = query.where(self.model.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def search(
        self,
        query: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Character]:
        """Search characters by name or other fields."""
        search = f"%{query}%"
        query = select(self.model).where(
            and_(
                self.model.is_deleted.is_(False),
                or_(
                    self.model.name.ilike(search),
                    self.model.player_name.ilike(search),
                    self.model.race.ilike(search),
                    self.model.class_name.ilike(search)
                )
            )
        ).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()


class CharacterVersionRepository(BaseRepository):
    """Repository for CharacterVersion model."""

    def __init__(self, db: AsyncSession):
        """Initialize with CharacterVersion model."""
        super().__init__(db, CharacterVersion)

    async def get_latest_version(
        self,
        character_id: UUID
    ) -> Optional[CharacterVersion]:
        """Get latest version of a character."""
        query = select(self.model).where(
            self.model.character_id == character_id
        ).order_by(desc(self.model.version_number)).limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_version_history(
        self,
        character_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[CharacterVersion]:
        """Get version history for a character."""
        query = select(self.model).where(
            self.model.character_id == character_id
        ).order_by(desc(self.model.version_number)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_theme(
        self,
        theme_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[CharacterVersion]:
        """Get all character versions for a theme."""
        query = select(self.model).where(
            self.model.theme_id == theme_id
        ).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()


class InventoryRepository(BaseRepository):
    """Repository for Inventory model."""

    def __init__(self, db: AsyncSession):
        """Initialize with Inventory model."""
        super().__init__(db, Inventory)

    async def get_by_character(self, character_id: UUID) -> Optional[Inventory]:
        """Get inventory for a character."""
        query = select(self.model).where(self.model.character_id == character_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class InventoryItemRepository(BaseRepository):
    """Repository for InventoryItem model."""

    def __init__(self, db: AsyncSession):
        """Initialize with InventoryItem model."""
        super().__init__(db, InventoryItem)

    async def get_by_inventory(
        self,
        inventory_id: UUID,
        equipped_only: bool = False
    ) -> List[InventoryItem]:
        """Get all items in an inventory."""
        query = select(self.model).where(self.model.inventory_id == inventory_id)
        if equipped_only:
            query = query.where(self.model.is_equipped.is_(True))
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_attuned_items(self, inventory_id: UUID) -> List[InventoryItem]:
        """Get all attuned items in an inventory."""
        query = select(self.model).where(
            and_(
                self.model.inventory_id == inventory_id,
                self.model.is_attuned.is_(True)
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class SpellcastingRepository(BaseRepository):
    """Repository for Spellcasting model."""

    def __init__(self, db: AsyncSession):
        """Initialize with Spellcasting model."""
        super().__init__(db, Spellcasting)

    async def get_by_character(self, character_id: UUID) -> Optional[Spellcasting]:
        """Get spellcasting for a character."""
        query = select(self.model).where(self.model.character_id == character_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()


class ConditionRepository(BaseRepository):
    """Repository for CharacterCondition model."""

    def __init__(self, db: AsyncSession):
        """Initialize with CharacterCondition model."""
        super().__init__(db, CharacterCondition)

    async def get_active_conditions(
        self,
        character_id: UUID
    ) -> List[CharacterCondition]:
        """Get active conditions for a character."""
        now = datetime.utcnow()
        query = select(self.model).where(
            and_(
                self.model.character_id == character_id,
                or_(
                    self.model.end_time.is_(None),
                    self.model.end_time > now
                )
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class ClassResourceRepository(BaseRepository):
    """Repository for ClassResource model."""

    def __init__(self, db: AsyncSession):
        """Initialize with ClassResource model."""
        super().__init__(db, ClassResource)

    async def get_by_character(self, character_id: UUID) -> List[ClassResource]:
        """Get all class resources for a character."""
        query = select(self.model).where(self.model.character_id == character_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_recharge_type(
        self,
        character_id: UUID,
        recharge_type: str
    ) -> List[ClassResource]:
        """Get resources by recharge type."""
        query = select(self.model).where(
            and_(
                self.model.character_id == character_id,
                self.model.recharge == recharge_type
            )
        )
        result = await self.db.execute(query)
        return result.scalars().all()


class JournalRepository(BaseRepository):
    """Repository for JournalEntry model."""

    def __init__(self, db: AsyncSession):
        """Initialize with JournalEntry model."""
        super().__init__(db, JournalEntry)

    async def get_by_character(
        self,
        character_id: UUID,
        limit: int = 100,
        offset: int = 0
    ) -> List[JournalEntry]:
        """Get journal entries for a character."""
        query = select(self.model).where(
            self.model.character_id == character_id
        ).order_by(desc(self.model.session_date)).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_session_date(
        self,
        character_id: UUID,
        start_date: datetime,
        end_date: Optional[datetime] = None
    ) -> List[JournalEntry]:
        """Get journal entries by session date range."""
        conditions = [
            self.model.character_id == character_id,
            self.model.session_date >= start_date
        ]
        if end_date:
            conditions.append(self.model.session_date <= end_date)

        query = select(self.model).where(and_(*conditions)).order_by(desc(self.model.session_date))
        result = await self.db.execute(query)
        return result.scalars().all()


class ThemeRepository(BaseRepository):
    """Repository for Theme model."""

    def __init__(self, db: AsyncSession):
        """Initialize with Theme model."""
        super().__init__(db, Theme)

    async def get_by_name(self, name: str) -> Optional[Theme]:
        """Get theme by name."""
        query = select(self.model).where(self.model.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_children(self, parent_id: UUID) -> List[Theme]:
        """Get child themes."""
        query = select(self.model).where(self.model.parent_id == parent_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_hierarchy(self, theme_id: UUID) -> Dict:
        """Get complete theme hierarchy."""
        theme = await self.get(theme_id)
        if not theme:
            return {}

        result = {
            "id": theme.id,
            "name": theme.name,
            "metadata": theme.metadata
        }

        children = await self.get_children(theme.id)
        if children:
            result["children"] = []
            for child in children:
                child_hierarchy = await self.get_hierarchy(child.id)
                result["children"].append(child_hierarchy)

        return result