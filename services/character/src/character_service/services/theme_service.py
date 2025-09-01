"""Theme management service module."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.version import (
    VersionGraph,
    VersionNode,
    VersionEdge,
    VersionNodeType,
    EdgeType,
)
from character_service.models.models import Character, InventoryItem
from character_service.repositories.version_repository import VersionRepository
from character_service.repositories.character_repository import CharacterRepository

class ThemeService:
    """Service for managing character and item themes."""

    def __init__(self, db: AsyncSession):
        self.db = db
        self.version_repo = VersionRepository(db)
        self.character_repo = CharacterRepository(db)

    async def transition_theme(
        self,
        character_id: UUID,
        new_theme: str,
        chapter_id: UUID,
        equipment_transitions: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        Transition a character to a new theme.
        
        This creates a new character version with the new theme, preserving memory,
        while equipment either resets to root theme versions or gets adapted.
        """
        # Get current character and equipment
        character = await self.character_repo.get(character_id)
        if not character:
            raise ValueError(f"Character not found: {character_id}")

        # Get or create version graph for this character
        graph = await self._get_character_graph(character)

        # Create new character version
        new_character = await self._create_character_version(character, new_theme)
        new_node = await self._add_character_node(graph, new_character)

        # Link to parent version
        parent_node = await self.version_repo.get_node_by_entity(
            character.id, VersionNodeType.CHARACTER)
        if parent_node:
            await self.version_repo.add_edge(
                graph.id, new_node.id, parent_node.id, EdgeType.PARENT)

        # Handle equipment transitions
        new_equipment = []
        for transition in equipment_transitions:
            item_id = UUID(transition["equipment_id"])
            item = await self._get_item(item_id)
            if not item:
                continue

            if transition["transition_type"] == "theme_reset":
                # Reset to root theme version
                root_version = await self._get_root_item(item)
                if root_version and root_version.theme == new_theme:
                    new_equipment.append(root_version)
                    # Add equipment relationship
                    item_node = await self.version_repo.get_node_by_entity(
                        root_version.id, VersionNodeType.EQUIPMENT)
                    if item_node:
                        await self.version_repo.add_edge(
                            graph.id, new_node.id, item_node.id, EdgeType.EQUIPPED)

            elif transition["transition_type"] == "adapt_new":
                # Create new themed version
                new_item = await self._create_item_version(item, new_theme)
                new_equipment.append(new_item)
                # Add to version graph
                item_node = await self._add_equipment_node(graph, new_item)
                root_node = await self.version_repo.get_node_by_entity(
                    item.root_id or item.id, VersionNodeType.EQUIPMENT)
                if root_node:
                    await self.version_repo.add_edge(
                        graph.id, item_node.id, root_node.id, EdgeType.ROOT)
                await self.version_repo.add_edge(
                    graph.id, new_node.id, item_node.id, EdgeType.EQUIPPED)

        # Update character's equipment
        new_character.inventory_items = new_equipment
        await self.db.flush()

        # Return full transition result
        return {
            "character": {
                "id": new_character.id,
                "parent_id": character.id,
                "theme": new_theme,
                "data": self._character_to_dict(new_character)
            },
            "equipment": [
                {
                    "id": item.id,
                    "root_id": item.root_id,
                    "theme": item.theme,
                    "data": self._item_to_dict(item)
                }
                for item in new_equipment
            ],
            "version_graph": await self._get_graph_state(graph.id)
        }

    async def _get_character_graph(self, character: Character) -> VersionGraph:
        """Get or create version graph for a character."""
        # Check for existing graph
        node = await self.version_repo.get_node_by_entity(
            character.id, VersionNodeType.CHARACTER)
        if node:
            return await self.version_repo.get_graph_by_id(node.graph_id)

        # Create new graph
        return await self.version_repo.create_graph(
            name=f"Version graph for {character.name}",
            description=f"Theme version tracking for character {character.id}"
        )

    async def _create_character_version(
        self,
        character: Character,
        new_theme: str
    ) -> Character:
        """Create a new themed version of a character."""
        # Create new character with theme
        new_data = dict(character.character_data)
        new_data["theme_data"] = self._adapt_character_theme(new_data, new_theme)
        
        new_character = await self.character_repo.create({
            "name": character.name,
            "user_id": character.user_id,
            "campaign_id": character.campaign_id,
            "parent_id": character.id,
            "theme": new_theme,
            "character_data": new_data,
            "is_active": True
        })

        # Copy over journal entries (preserve memory)
        for entry in character.journal_entries:
            if not entry.is_deleted:
                new_entry = dict(entry.__dict__)
                new_entry["id"] = uuid4()
                new_entry["character_id"] = new_character.id
                new_character.journal_entries.append(new_entry)

        return new_character

    async def _create_item_version(
        self,
        item: InventoryItem,
        new_theme: str
    ) -> InventoryItem:
        """Create a new themed version of an item."""
        new_data = dict(item.item_data)
        new_data["theme_data"] = self._adapt_item_theme(new_data, new_theme)

        return InventoryItem(
            id=uuid4(),
            root_id=item.root_id or item.id,
            theme=new_theme,
            character_id=item.character_id,
            item_data=new_data,
            quantity=item.quantity,
            equipped=item.equipped
        )

    async def _add_character_node(
        self,
        graph: VersionGraph,
        character: Character
    ) -> VersionNode:
        """Add a character node to the version graph."""
        return await self.version_repo.add_node(
            graph_id=graph.id,
            entity_id=character.id,
            node_type=VersionNodeType.CHARACTER,
            theme=character.theme,
            metadata={
                "name": character.name,
                "version_type": "character",
                "created_at": datetime.utcnow().isoformat()
            }
        )

    async def _add_equipment_node(
        self,
        graph: VersionGraph,
        item: InventoryItem
    ) -> VersionNode:
        """Add an equipment node to the version graph."""
        return await self.version_repo.add_node(
            graph_id=graph.id,
            entity_id=item.id,
            node_type=VersionNodeType.EQUIPMENT,
            theme=item.theme,
            metadata={
                "name": item.item_data.get("name"),
                "version_type": "equipment",
                "created_at": datetime.utcnow().isoformat()
            }
        )

    async def _get_item(self, item_id: UUID) -> Optional[InventoryItem]:
        """Get an inventory item by ID."""
        query = select(InventoryItem).where(InventoryItem.id == item_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def _get_root_item(self, item: InventoryItem) -> Optional[InventoryItem]:
        """Get the root version of an item."""
        if not item.root_id:
            return item
        root = await self._get_item(item.root_id)
        return root if root else item

    async def _get_graph_state(self, graph_id: UUID) -> Dict[str, Any]:
        """Get current state of a version graph."""
        graph = await self.version_repo.get_graph_by_id(graph_id)
        if not graph:
            return {"nodes": [], "edges": []}

        return {
            "nodes": [
                {
                    "id": node.id,
                    "type": node.type,
                    "theme": node.theme,
                    "parent_id": next(
                        (e.target_id for e in node.incoming_edges 
                         if e.type == EdgeType.PARENT),
                        None
                    ),
                    "root_id": next(
                        (e.target_id for e in node.outgoing_edges 
                         if e.type == EdgeType.ROOT),
                        None
                    )
                }
                for node in graph.nodes
            ],
            "edges": [
                {
                    "from": edge.source_id,
                    "to": edge.target_id,
                    "type": edge.type
                }
                for edge in graph.edges
            ]
        }

    def _adapt_character_theme(
        self,
        character_data: Dict[str, Any],
        new_theme: str
    ) -> Dict[str, Any]:
        """Adapt character data to a new theme."""
        # This would contain theme-specific logic for adapting character attributes
        # For now, return basic theme metadata
        return {
            "theme": new_theme,
            "adapted_at": datetime.utcnow().isoformat()
        }

    def _adapt_item_theme(
        self,
        item_data: Dict[str, Any],
        new_theme: str
    ) -> Dict[str, Any]:
        """Adapt item data to a new theme."""
        # This would contain theme-specific logic for adapting item properties
        # For now, return basic theme metadata
        return {
            "theme": new_theme,
            "adapted_at": datetime.utcnow().isoformat()
        }

    def _character_to_dict(self, character: Character) -> Dict[str, Any]:
        """Convert character to dictionary representation."""
        return {
            "id": str(character.id),
            "name": character.name,
            "theme": character.theme,
            "data": character.character_data,
            "journal_entries": [
                {
                    "id": str(entry.id),
                    "content": entry.content
                }
                for entry in character.journal_entries
                if not entry.is_deleted
            ]
        }

    def _item_to_dict(self, item: InventoryItem) -> Dict[str, Any]:
        """Convert inventory item to dictionary representation."""
        return {
            "id": str(item.id),
            "root_id": str(item.root_id) if item.root_id else None,
            "theme": item.theme,
            "data": item.item_data
        }
