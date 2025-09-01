"""Theme and version management schema models."""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID
from pydantic import BaseModel, Field

class EquipmentTransition(BaseModel):
    """Equipment theme transition request."""
    equipment_id: UUID
    transition_type: str = Field(
        ...,
        description="How to handle this equipment during theme transition",
        pattern="^(theme_reset|adapt_new|keep_current)$"
    )

class ThemeTransitionRequest(BaseModel):
    """Request model for theme transition."""
    new_theme: str = Field(..., description="Theme to transition to")
    chapter_id: UUID = Field(..., description="Chapter ID for the transition")
    equipment_transitions: List[EquipmentTransition]

class VersionNodeData(BaseModel):
    """Version node data."""
    id: UUID
    entity_id: UUID
    type: str = Field(..., pattern="^(character|equipment|spell|species|class|feat|background)$")
    theme: str
    parent_id: Optional[UUID] = None
    root_id: Optional[UUID] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)

class VersionEdgeData(BaseModel):
    """Version edge data."""
    from_id: UUID = Field(..., alias="from")
    to_id: UUID = Field(..., alias="to")
    type: str = Field(
        ...,
        pattern="^(parent|root|equipped|owns|knows)$"
    )

class CharacterVersionData(BaseModel):
    """Character version data in theme transition."""
    id: UUID
    parent_id: UUID
    theme: str
    data: Dict[str, Any]

class EquipmentVersionData(BaseModel):
    """Equipment version data in theme transition."""
    id: UUID
    root_id: Optional[UUID]
    theme: str
    data: Dict[str, Any]

class VersionGraphData(BaseModel):
    """Version graph state data."""
    nodes: List[VersionNodeData]
    edges: List[VersionEdgeData]

class ThemeTransitionResponse(BaseModel):
    """Response model for theme transition."""
    character: CharacterVersionData
    equipment: List[EquipmentVersionData]
    version_graph: VersionGraphData

class VersionGraphResponse(BaseModel):
    """Response model for version graph query."""
    graph_id: UUID
    nodes: List[VersionNodeData]
    edges: List[VersionEdgeData]

class VersionNodeResponse(BaseModel):
    """Response model for version node data."""
    id: UUID
    entity_id: UUID
    type: str = Field(..., pattern="^(character|equipment|spell|species|class|feat|background)$")
    theme: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
