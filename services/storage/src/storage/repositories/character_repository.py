"""Repository implementation for character database operations."""

from datetime import datetime
from typing import Dict, List, Optional, Union
from uuid import UUID

from sqlalchemy import select, update, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from storage.databases.character_db.models import (
    Character,
    CharacterCondition,
    CharacterVersion,
    ClassResource,
    Inventory,
    InventoryItem,
    JournalEntry,
    Spellcasting,
    Theme,
    ThemeFeature,
    ThemeEquipment,
    ProgressionRule,
    ThemeState,
    VersionGraph,
    VersionNode,
    VersionEdge,
)
from storage.core.base import BaseRepository

class CharacterRepository(BaseRepository):
    """Character database operations."""

    def __init__(self, session: AsyncSession):
        super().__init__(session)
        self.session = session

    async def create_character(self, character_data: Dict) -> Character:
        """Create a new character."""
        character = Character(**character_data)
        self.session.add(character)
        await self.session.commit()
        await self.session.refresh(character)
        return character

    async def get_character(self, character_id: UUID) -> Optional[Character]:
        """Get a character by ID."""
        query = select(Character).where(
            and_(
                Character.id == character_id,
                Character.is_deleted == False
            )
        ).options(
            selectinload(Character.inventory),
            selectinload(Character.spellcasting),
            selectinload(Character.conditions),
            selectinload(Character.journal_entries),
            selectinload(Character.class_resources)
        )
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_character(self, character_id: UUID, character_data: Dict) -> Optional[Character]:
        """Update a character."""
        if not character_data:
            return None
            
        query = update(Character).where(
            and_(
                Character.id == character_id,
                Character.is_deleted == False
            )
        ).values(
            **character_data,
            updated_at=datetime.utcnow()
        )
        await self.session.execute(query)
        await self.session.commit()
        return await self.get_character(character_id)

    async def delete_character(self, character_id: UUID) -> bool:
        """Soft delete a character."""
        query = update(Character).where(
            and_(
                Character.id == character_id,
                Character.is_deleted == False
            )
        ).values(
            is_deleted=True,
            deleted_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0

    async def create_version(self, version_data: Dict) -> CharacterVersion:
        """Create a new character version."""
        version = CharacterVersion(**version_data)
        self.session.add(version)
        await self.session.commit()
        await self.session.refresh(version)
        return version

    async def get_character_versions(self, character_id: UUID) -> List[CharacterVersion]:
        """Get all versions of a character."""
        query = select(CharacterVersion).where(
            CharacterVersion.character_id == character_id
        ).order_by(CharacterVersion.version_number.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_theme(self, theme_data: Dict) -> Theme:
        """Create a new theme."""
        theme = Theme(**theme_data)
        self.session.add(theme)
        await self.session.commit()
        await self.session.refresh(theme)
        return theme

    async def get_theme(self, theme_id: UUID) -> Optional[Theme]:
        """Get a theme by ID."""
        query = select(Theme).where(Theme.id == theme_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_inventory(self, inventory_data: Dict) -> Inventory:
        """Create a new inventory."""
        inventory = Inventory(**inventory_data)
        self.session.add(inventory)
        await self.session.commit()
        await self.session.refresh(inventory)
        return inventory

    async def add_item_to_inventory(self, inventory_id: UUID, item_data: Dict) -> InventoryItem:
        """Add an item to an inventory."""
        item = InventoryItem(inventory_id=inventory_id, **item_data)
        self.session.add(item)
        await self.session.commit()
        await self.session.refresh(item)
        return item

    async def create_spellcasting(self, spellcasting_data: Dict) -> Spellcasting:
        """Create spellcasting information for a character."""
        spellcasting = Spellcasting(**spellcasting_data)
        self.session.add(spellcasting)
        await self.session.commit()
        await self.session.refresh(spellcasting)
        return spellcasting

    async def add_journal_entry(self, journal_data: Dict) -> JournalEntry:
        """Add a journal entry for a character."""
        entry = JournalEntry(**journal_data)
        self.session.add(entry)
        await self.session.commit()
        await self.session.refresh(entry)
        return entry

    async def get_journal_entries(self, character_id: UUID) -> List[JournalEntry]:
        """Get all journal entries for a character."""
        query = select(JournalEntry).where(
            and_(
                JournalEntry.character_id == character_id,
                JournalEntry.is_deleted == False
            )
        ).order_by(JournalEntry.session_date.desc())
        result = await self.session.execute(query)
        return result.scalars().all()

    async def create_character_condition(self, condition_data: Dict) -> CharacterCondition:
        """Add a condition to a character."""
        condition = CharacterCondition(**condition_data)
        self.session.add(condition)
        await self.session.commit()
        await self.session.refresh(condition)
        return condition

    async def get_active_conditions(self, character_id: UUID) -> List[CharacterCondition]:
        """Get all active conditions for a character."""
        query = select(CharacterCondition).where(
            and_(
                CharacterCondition.character_id == character_id,
                CharacterCondition.end_time == None
            )
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def add_class_resource(self, resource_data: Dict) -> ClassResource:
        """Add a class resource to a character."""
        resource = ClassResource(**resource_data)
        self.session.add(resource)
        await self.session.commit()
        await self.session.refresh(resource)
        return resource

    async def update_class_resource(
        self, resource_id: UUID, updates: Dict
    ) -> Optional[ClassResource]:
        """Update a class resource."""
        query = update(ClassResource).where(
            ClassResource.id == resource_id
        ).values(**updates)
        await self.session.execute(query)
        await self.session.commit()

        query = select(ClassResource).where(ClassResource.id == resource_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def create_version_graph(self, graph_data: Dict) -> VersionGraph:
        """Create a new version graph."""
        graph = VersionGraph(**graph_data)
        self.session.add(graph)
        await self.session.commit()
        await self.session.refresh(graph)
        return graph

    async def add_version_node(self, node_data: Dict) -> VersionNode:
        """Add a node to a version graph."""
        node = VersionNode(**node_data)
        self.session.add(node)
        await self.session.commit()
        await self.session.refresh(node)
        return node

    async def add_version_edge(self, edge_data: Dict) -> VersionEdge:
        """Add an edge to a version graph."""
        edge = VersionEdge(**edge_data)
        self.session.add(edge)
        await self.session.commit()
        await self.session.refresh(edge)
        return edge