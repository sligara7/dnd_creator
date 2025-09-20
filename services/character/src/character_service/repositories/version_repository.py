"""Version graph repository module."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

from character_service.clients.storage_port import (
    StoragePort,
    VersionGraph,
    VersionNode,
    VersionEdge,
    VersionNodeType,
    EdgeType,
)

class VersionRepository:
    """Repository for managing version graphs using storage service."""

    def __init__(self, storage: StoragePort):
        self.storage = storage

    async def create_graph(self, name: str, description: str = None) -> VersionGraph:
        """Create a new version graph."""
        return await self.storage.create_graph(name, description)

    async def add_node(
        self, 
        graph_id: UUID,
        entity_id: UUID,
        node_type: VersionNodeType,
        theme: str,
        metadata: Dict[str, Any] = None
    ) -> VersionNode:
        """Add a node to a version graph."""
        return await self.storage.add_node(
            graph_id=graph_id,
            entity_id=entity_id,
            node_type=node_type,
            theme=theme,
            metadata=metadata
        )

    async def add_edge(
        self,
        graph_id: UUID,
        source_id: UUID,
        target_id: UUID,
        edge_type: EdgeType,
        metadata: Dict[str, Any] = None
    ) -> VersionEdge:
        """Add an edge to a version graph."""
        return await self.storage.add_edge(
            graph_id=graph_id,
            source_id=source_id,
            target_id=target_id,
            edge_type=edge_type,
            metadata=metadata
        )

    async def get_node_chain(
        self,
        node_id: UUID,
        edge_type: EdgeType
    ) -> List[VersionNode]:
        """Get a chain of nodes connected by edges of the specified type."""
        return await self.storage.get_node_chain(node_id, edge_type)

    async def get_node_relationships(
        self,
        node_id: UUID,
        edge_type: EdgeType = None
    ) -> List[Tuple[VersionEdge, VersionNode]]:
        """Get all nodes related to the given node by specified edge type."""
        return await self.storage.get_node_relationships(node_id, edge_type)

    async def get_graph_by_id(self, graph_id: UUID) -> Optional[VersionGraph]:
        """Get a version graph by ID."""
        return await self.storage.get_graph_by_id(graph_id)

    async def get_node_by_entity(
        self,
        entity_id: UUID,
        node_type: VersionNodeType = None,
        theme: str = None
    ) -> Optional[VersionNode]:
        """Get a version node by entity ID, optionally filtered by type and theme."""
        return await self.storage.get_node_by_entity(
            entity_id=entity_id,
            node_type=node_type,
            theme=theme
        )

    async def get_root_node(self, node_id: UUID) -> Optional[VersionNode]:
        """Get the root node for a given node by following ROOT edges."""
        chain = await self.get_node_chain(node_id, EdgeType.ROOT)
        return chain[-1] if chain else None

    async def get_parent_node(self, node_id: UUID) -> Optional[VersionNode]:
        """Get the parent node for a given node by following PARENT edges."""
        chain = await self.get_node_chain(node_id, EdgeType.PARENT)
        return chain[1] if len(chain) > 1 else None
