"""Campaign models for storage service."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Set
from uuid import UUID

from pydantic import BaseModel, Field, model_validator


class CampaignState(str, Enum):
    """Campaign states."""
    DRAFT = "draft"
    ACTIVE = "active"
    PAUSED = "paused"
    COMPLETED = "completed"
    ARCHIVED = "archived"


class CampaignType(str, Enum):
    """Campaign types."""
    TRADITIONAL = "traditional"
    ANTITHETICON = "antitheticon"


class Chapter(BaseModel):
    """Campaign chapter model."""
    
    model_config = {"table": "chapters"}
    
    id: UUID = Field(default_factory=UUID)
    campaign_id: UUID
    title: str
    description: Optional[str] = None
    prerequisites: List[UUID] = Field(default_factory=list)
    order: int = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None


class WorldEffect(BaseModel):
    """Model for tracking world-level effects in campaigns."""
    id: UUID = Field(default_factory=UUID)
    name: str
    description: str
    scope: str  # global, regional, local
    duration: Optional[str] = None
    triggers: List[str] = Field(default_factory=list)
    conditions: Dict[str, str] = Field(default_factory=dict)
    active: bool = True


class Relationship(BaseModel):
    """Model for tracking relationships between entities."""
    id: UUID = Field(default_factory=UUID)
    source_id: UUID
    target_id: UUID
    relationship_type: str
    strength: int = Field(ge=1, le=10)
    metadata: Dict[str, str] = Field(default_factory=dict)
    created_at: datetime
    updated_at: datetime


class Version(BaseModel):
    """Model for campaign version control."""
    number: int
    parent_version: Optional[int] = None
    branch_name: str = "main"
    commit_hash: str
    commit_message: str
    committed_by: UUID
    committed_at: datetime
    metadata: Dict[str, str] = Field(default_factory=dict)


class IdentityNetwork(BaseModel):
    """Model for Antitheticon identity deception networks."""
    nodes: Dict[str, Dict[str, str]] = Field(default_factory=dict)
    edges: List[Dict[str, str]] = Field(default_factory=list)
    layers: Dict[str, List[str]] = Field(default_factory=dict)
    metadata: Dict[str, str] = Field(default_factory=dict)


class Campaign(BaseModel):
    """Campaign model."""
    
    model_config = {"table": "campaigns"}
    
    id: UUID = Field(default_factory=UUID)
    name: str
    description: Optional[str] = None
    creator_id: UUID
    owner_id: UUID
    state: CampaignState = CampaignState.DRAFT
    campaign_type: CampaignType = CampaignType.TRADITIONAL
    
    # Version control
    version: Version
    branches: Dict[str, Version] = Field(default_factory=dict)
    
    # Content and theming
    theme_data: Optional[dict] = None
    provenance: Dict[str, str] = Field(default_factory=dict)
    content_sources: List[str] = Field(default_factory=list)
    
    # World and relationships
    world_effects: List[WorldEffect] = Field(default_factory=list)
    relationships: List[Relationship] = Field(default_factory=list)
    
    # Antitheticon support
    identity_network: Optional[IdentityNetwork] = None
    deception_layers: Dict[str, List[str]] = Field(default_factory=dict)
    
    # Core data
    chapters: List[Chapter] = Field(default_factory=list)
    metadata: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_deleted: bool = False
    deleted_at: Optional[datetime] = None
    
    @model_validator(mode="after")
    def ensure_timestamps(self) -> "Campaign":
        """Ensure timestamps are set."""
        if not self.created_at:
            self.created_at = datetime.utcnow()
        if not self.updated_at:
            self.updated_at = datetime.utcnow()
        return self
    
    @property
    def is_traditional(self) -> bool:
        """Check if campaign is traditional."""
        return self.campaign_type == CampaignType.TRADITIONAL
    
    @property
    def is_antitheticon(self) -> bool:
        """Check if campaign is antitheticon."""
        return self.campaign_type == CampaignType.ANTITHETICON
    
    def to_dict(self) -> dict:
        """Convert to dict for storage service."""
        data = self.model_dump(exclude={"chapters"})
        
        # Convert UUIDs to strings
        data["id"] = str(data["id"])
        data["creator_id"] = str(data["creator_id"])
        data["owner_id"] = str(data["owner_id"])
        
        # Convert timestamps to ISO format
        if data.get("created_at"):
            data["created_at"] = data["created_at"].isoformat()
        if data.get("updated_at"):
            data["updated_at"] = data["updated_at"].isoformat()
        if data.get("deleted_at"):
            data["deleted_at"] = data["deleted_at"].isoformat()
            
        return data