"""Version graph and theme models."""

from datetime import datetime
from uuid import UUID, uuid4
from enum import Enum
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from character_service.core.database import Base

class VersionNodeType(str, Enum):
    """Types of versionable content."""
    CHARACTER = "character"
    EQUIPMENT = "equipment"
    SPELL = "spell"
    SPECIES = "species"
    CLASS = "class"
    FEAT = "feat"
    BACKGROUND = "background"

class EdgeType(str, Enum):
    """Types of version relationships."""
    PARENT = "parent"  # Character version chain
    ROOT = "root"      # Equipment theme reset
    EQUIPPED = "equipped"  # Character-equipment relationship
    OWNS = "owns"     # Character-item relationship
    KNOWS = "knows"   # Character-spell relationship

class VersionGraph(Base):
    """Version graph model."""
    __tablename__ = "version_graphs"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    name = Column(String, nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    nodes = relationship("VersionNode", back_populates="graph")
    edges = relationship("VersionEdge", back_populates="graph")

class VersionNode(Base):
    """Version node model."""
    __tablename__ = "version_nodes"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    graph_id = Column(PGUUID(as_uuid=True), ForeignKey("version_graphs.id"), nullable=False)
    entity_id = Column(PGUUID(as_uuid=True), nullable=False)  # ID of the actual entity
    type = Column(String, nullable=False)  # VersionNodeType
    theme = Column(String, nullable=False)
    node_metadata = Column(JSONB, nullable=False, server_default="{}")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    graph = relationship("VersionGraph", back_populates="nodes")
    outgoing_edges = relationship("VersionEdge", 
                                back_populates="source",
                                foreign_keys="[VersionEdge.source_id]")
    incoming_edges = relationship("VersionEdge", 
                                back_populates="target",
                                foreign_keys="[VersionEdge.target_id]")

class VersionEdge(Base):
    """Version edge model."""
    __tablename__ = "version_edges"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    graph_id = Column(PGUUID(as_uuid=True), ForeignKey("version_graphs.id"), nullable=False)
    source_id = Column(PGUUID(as_uuid=True), ForeignKey("version_nodes.id"), nullable=False)
    target_id = Column(PGUUID(as_uuid=True), ForeignKey("version_nodes.id"), nullable=False)
    type = Column(String, nullable=False)  # EdgeType
    edge_metadata = Column(JSONB, nullable=False, server_default="{}")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    graph = relationship("VersionGraph", back_populates="edges")
    source = relationship("VersionNode", 
                        back_populates="outgoing_edges",
                        foreign_keys=[source_id])
    target = relationship("VersionNode", 
                        back_populates="incoming_edges",
                        foreign_keys=[target_id])
