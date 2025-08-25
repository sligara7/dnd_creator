"""Entity visualization and progression tracking."""

from typing import Dict, List, Optional, Any, Set, Tuple
from dataclasses import dataclass
from enum import Enum
import json
from datetime import datetime

class NodeType(Enum):
    """Types of nodes in the entity graph."""
    ROOT = "root"  # Original creation
    LEVEL_UP = "level_up"  # Level progression
    THEME = "theme"  # Theme variant
    INSTANCE = "instance"  # Copy/instance
    MODIFICATION = "modification"  # Other changes

@dataclass
class GraphNode:
    """Node in the entity progression graph."""
    node_id: str
    entity_id: str
    node_type: NodeType
    data: Dict[str, Any]
    timestamp: datetime
    metadata: Dict[str, Any]
    parent_id: Optional[str] = None
    theme_root_id: Optional[str] = None  # Original entity for theme variants

@dataclass
class GraphEdge:
    """Edge connecting nodes in the graph."""
    source_id: str
    target_id: str
    edge_type: str
    metadata: Dict[str, Any]

class EntityGraph:
    """Manages and visualizes entity progression."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self.theme_roots: Dict[str, str] = {}  # entity_id -> root_node_id for themes

    async def add_node(self, entity_id: str,
                      node_type: NodeType,
                      data: Dict[str, Any],
                      parent_id: Optional[str] = None,
                      metadata: Optional[Dict[str, Any]] = None) -> str:
        """Add a node to the graph."""
        node_id = f"{entity_id}_{len(self.nodes)}"
        
        # For theme nodes, always reference the root
        theme_root_id = None
        if node_type == NodeType.THEME:
            if entity_id in self.theme_roots:
                theme_root_id = self.theme_roots[entity_id]
            else:
                # If no root exists, this becomes the root
                theme_root_id = node_id
                self.theme_roots[entity_id] = node_id

        node = GraphNode(
            node_id=node_id,
            entity_id=entity_id,
            node_type=node_type,
            data=data,
            timestamp=datetime.utcnow(),
            metadata=metadata or {},
            parent_id=parent_id,
            theme_root_id=theme_root_id
        )
        
        self.nodes[node_id] = node
        
        if parent_id:
            self.edges.append(GraphEdge(
                source_id=parent_id,
                target_id=node_id,
                edge_type=node_type.value,
                metadata=metadata or {}
            ))
        
        return node_id

    async def get_entity_progression(self, entity_id: str) -> Dict[str, Any]:
        """Get complete progression tree for an entity."""
        nodes = [node for node in self.nodes.values() if node.entity_id == entity_id]
        edges = [edge for edge in self.edges 
                if edge.source_id in [n.node_id for n in nodes] or 
                   edge.target_id in [n.node_id for n in nodes]]

        return {
            "nodes": [self._node_to_dict(node) for node in nodes],
            "edges": [self._edge_to_dict(edge) for edge in edges]
        }

    async def generate_mermaid_diagram(self, entity_id: str) -> str:
        """Generate Mermaid.js diagram showing entity progression."""
        progression = await self.get_entity_progression(entity_id)
        
        # Start Mermaid graph
        lines = ["graph TD"]
        
        # Add nodes
        for node in progression["nodes"]:
            node_style = self._get_node_style(node["node_type"])
            label = self._create_node_label(node)
            lines.append(f"    {node['node_id']}{node_style}[\"{label}\"]")
        
        # Add edges
        for edge in progression["edges"]:
            edge_style = self._get_edge_style(edge["edge_type"])
            lines.append(f"    {edge['source_id']} {edge_style} {edge['target_id']}")
        
        return "\n".join(lines)

    async def generate_dot_diagram(self, entity_id: str) -> str:
        """Generate GraphViz DOT diagram showing entity progression."""
        progression = await self.get_entity_progression(entity_id)
        
        lines = ["digraph EntityProgression {"]
        lines.append("    rankdir=TD;")
        lines.append("    node [shape=box, style=rounded];")
        
        # Add nodes
        for node in progression["nodes"]:
            node_attrs = self._get_dot_node_attrs(node["node_type"])
            label = self._create_node_label(node)
            lines.append(f"    {node['node_id']} {node_attrs} [label=\"{label}\"];")
        
        # Add edges
        for edge in progression["edges"]:
            edge_attrs = self._get_dot_edge_attrs(edge["edge_type"])
            lines.append(f"    {edge['source_id']} -> {edge['target_id']} {edge_attrs};")
        
        lines.append("}")
        return "\n".join(lines)

    def _node_to_dict(self, node: GraphNode) -> Dict[str, Any]:
        """Convert node to dictionary format."""
        return {
            "node_id": node.node_id,
            "entity_id": node.entity_id,
            "node_type": node.node_type.value,
            "data": node.data,
            "timestamp": node.timestamp.isoformat(),
            "metadata": node.metadata,
            "parent_id": node.parent_id,
            "theme_root_id": node.theme_root_id
        }

    def _edge_to_dict(self, edge: GraphEdge) -> Dict[str, Any]:
        """Convert edge to dictionary format."""
        return {
            "source_id": edge.source_id,
            "target_id": edge.target_id,
            "edge_type": edge.edge_type,
            "metadata": edge.metadata
        }

    def _get_node_style(self, node_type: str) -> str:
        """Get Mermaid.js node style."""
        styles = {
            "root": "()",  # Circle
            "level_up": "{{}}",  # Hexagon
            "theme": "[()]",  # Stadium
            "instance": "[]",  # Rectangle
            "modification": "{}"  # Rectangle with rounded corners
        }
        return styles.get(node_type, "[]")

    def _get_edge_style(self, edge_type: str) -> str:
        """Get Mermaid.js edge style."""
        styles = {
            "level_up": "===>",  # Thick arrow
            "theme": "-.-=>",  # Dotted arrow
            "instance": "-.->",  # Dashed arrow
            "modification": "-->",  # Normal arrow
        }
        return styles.get(edge_type, "-->")

    def _get_dot_node_attrs(self, node_type: str) -> str:
        """Get GraphViz DOT node attributes."""
        attrs = {
            "root": "[shape=circle, style=filled, fillcolor=lightblue]",
            "level_up": "[shape=hexagon, style=filled, fillcolor=lightgreen]",
            "theme": "[shape=oval, style=filled, fillcolor=lightyellow]",
            "instance": "[shape=box, style=filled, fillcolor=lightgray]",
            "modification": "[shape=box, style=\"rounded,filled\", fillcolor=lightpink]"
        }
        return attrs.get(node_type, "[shape=box]")

    def _get_dot_edge_attrs(self, edge_type: str) -> str:
        """Get GraphViz DOT edge attributes."""
        attrs = {
            "level_up": "[penwidth=2.0]",
            "theme": "[style=dotted]",
            "instance": "[style=dashed]",
            "modification": "[]"
        }
        return attrs.get(edge_type, "[]")

    def _create_node_label(self, node: Dict[str, Any]) -> str:
        """Create readable label for node."""
        label_parts = []
        
        # Add type indicator
        label_parts.append(f"[{node['node_type']}]")
        
        # Add name/identifier
        if "name" in node["data"]:
            label_parts.append(node["data"]["name"])
        
        # Add key changes
        changes = []
        if "level" in node["data"]:
            changes.append(f"Level {node['data']['level']}")
        if "theme" in node["data"]:
            changes.append(f"Theme: {node['data']['theme']}")
        if changes:
            label_parts.append("\\n" + ", ".join(changes))
        
        return " ".join(label_parts)
