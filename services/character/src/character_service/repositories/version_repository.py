"""Version graph repository module."""

from datetime import datetime
from typing import Dict, List, Optional, Any, Tuple
from uuid import UUID, uuid4

from sqlalchemy import select, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from character_service.models.version import (
    VersionGraph,
    VersionNode,
    VersionEdge,
    VersionNodeType,
    EdgeType,
)

class VersionRepository:
    """Repository for managing version graphs."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_graph(self, name: str, description: str = None) -> VersionGraph:
        """Create a new version graph."""
        graph = VersionGraph(
            id=uuid4(),
            name=name,
            description=description
        )
        self.db.add(graph)
        await self.db.flush()
        await self.db.refresh(graph)
        return graph

    async def add_node(
        self, 
        graph_id: UUID,
        entity_id: UUID,
        node_type: VersionNodeType,
        theme: str,
        metadata: Dict[str, Any] = None
    ) -> VersionNode:
        """Add a node to a version graph."""
        node = VersionNode(
            id=uuid4(),
            graph_id=graph_id,
            entity_id=entity_id,
            type=node_type,
            theme=theme,
            metadata=metadata or {}
        )
        self.db.add(node)
        await self.db.flush()
        await self.db.refresh(node)
        return node

    async def add_edge(
        self,
        graph_id: UUID,
        source_id: UUID,
        target_id: UUID,
        edge_type: EdgeType,
        metadata: Dict[str, Any] = None
    ) -> VersionEdge:
        """Add an edge to a version graph."""
        edge = VersionEdge(
            id=uuid4(),
            graph_id=graph_id,
            source_id=source_id,
            target_id=target_id,
            type=edge_type,
            metadata=metadata or {}
        )
        self.db.add(edge)
        await self.db.flush()
        await self.db.refresh(edge)
        return edge

    async def get_node_chain(
        self,
        node_id: UUID,
        edge_type: EdgeType
    ) -> List[VersionNode]:
        """Get a chain of nodes connected by edges of the specified type."""
        # Get the starting node
        query = select(VersionNode).where(VersionNode.id == node_id)
        result = await self.db.execute(query)
        node = result.scalar_one_or_none()
        if not node:
            return []

        chain = [node]
        current = node

        # Follow edges until we reach the end
        while True:
            # For parent chains, follow incoming edges
            if edge_type == EdgeType.PARENT:
                edge_query = select(VersionEdge).where(
                    and_(
                        VersionEdge.target_id == current.id,
                        VersionEdge.type == edge_type
                    )
                )
            # For root chains, follow outgoing edges
            else:
                edge_query = select(VersionEdge).where(
                    and_(
                        VersionEdge.source_id == current.id,
                        VersionEdge.type == edge_type
                    )
                )

            result = await self.db.execute(edge_query)
            edge = result.scalar_one_or_none()
            if not edge:
                break

            # Get the next node
            next_id = edge.source_id if edge_type == EdgeType.PARENT else edge.target_id
            query = select(VersionNode).where(VersionNode.id == next_id)
            result = await self.db.execute(query)
            current = result.scalar_one_or_none()
            if not current:
                break

            chain.append(current)

        return chain

    async def get_node_relationships(
        self,
        node_id: UUID,
        edge_type: EdgeType = None
    ) -> List[Tuple[VersionEdge, VersionNode]]:
        """Get all nodes related to the given node by specified edge type."""
        node_query = (
            select(VersionNode)
            .where(VersionNode.id == node_id)
            .options(
                joinedload(VersionNode.outgoing_edges).joinedload(VersionEdge.target),
                joinedload(VersionNode.incoming_edges).joinedload(VersionEdge.source)
            )
        )
        result = await self.db.execute(node_query)
        node = result.scalar_one_or_none()
        if not node:
            return []

        relationships = []
        
        # Check outgoing edges
        for edge in node.outgoing_edges:
            if edge_type and edge.type != edge_type:
                continue
            relationships.append((edge, edge.target))

        # Check incoming edges
        for edge in node.incoming_edges:
            if edge_type and edge.type != edge_type:
                continue
            relationships.append((edge, edge.source))

        return relationships

    async def get_graph_by_id(self, graph_id: UUID) -> Optional[VersionGraph]:
        """Get a version graph by ID."""
        query = (
            select(VersionGraph)
            .where(VersionGraph.id == graph_id)
            .options(
                joinedload(VersionGraph.nodes),
                joinedload(VersionGraph.edges)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_node_by_entity(
        self,
        entity_id: UUID,
        node_type: VersionNodeType = None,
        theme: str = None
    ) -> Optional[VersionNode]:
        """Get a version node by entity ID, optionally filtered by type and theme."""
        query = select(VersionNode).where(VersionNode.entity_id == entity_id)
        if node_type:
            query = query.where(VersionNode.type == node_type)
        if theme:
            query = query.where(VersionNode.theme == theme)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_root_node(self, node_id: UUID) -> Optional[VersionNode]:
        """Get the root node for a given node by following ROOT edges."""
        chain = await self.get_node_chain(node_id, EdgeType.ROOT)
        return chain[-1] if chain else None

    async def get_parent_node(self, node_id: UUID) -> Optional[VersionNode]:
        """Get the parent node for a given node by following PARENT edges."""
        chain = await self.get_node_chain(node_id, EdgeType.PARENT)
        return chain[1] if len(chain) > 1 else None
