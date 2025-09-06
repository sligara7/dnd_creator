"""Schemas for campaign content generation."""
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from llm_service.schemas.common import ContentMetadata


class StoryElement(str, Enum):
    """Types of story elements."""
    PLOT = "plot"
    QUEST = "quest"
    SCENE = "scene"
    DIALOGUE = "dialogue"
    DESCRIPTION = "description"
    EVENT = "event"


class NPCRole(str, Enum):
    """NPC roles in the story."""
    ALLY = "ally"
    ANTAGONIST = "antagonist"
    MERCHANT = "merchant"
    QUEST_GIVER = "quest_giver"
    LORE_KEEPER = "lore_keeper"
    MENTOR = "mentor"
    NEUTRAL = "neutral"


class LocationType(str, Enum):
    """Types of locations."""
    TOWN = "town"
    DUNGEON = "dungeon"
    WILDERNESS = "wilderness"
    LANDMARK = "landmark"
    BUILDING = "building"
    SHOP = "shop"
    TAVERN = "tavern"


class CampaignContext(BaseModel):
    """Campaign generation context."""
    campaign_theme: str = Field(description="Overall campaign theme")
    party_level: int = Field(ge=1, le=20, description="Average party level")
    party_size: int = Field(ge=1, description="Number of players")
    campaign_type: str = Field(description="Type of campaign (e.g., dungeon crawl, intrigue)")
    setting: str = Field(description="Campaign setting")
    length: str = Field(description="Expected campaign length")
    additional_context: Optional[Dict[str, str]] = None


class StoryRequest(BaseModel):
    """Request for story content generation."""
    element_type: StoryElement = Field(description="Type of story element to generate")
    context: CampaignContext = Field(description="Campaign context")
    parent_element_id: Optional[UUID] = Field(None, description="Parent story element ID")
    parameters: Dict[str, str] = Field(default_factory=dict)


class NPCRequest(BaseModel):
    """Request for NPC generation."""
    role: NPCRole = Field(description="NPC's role in the story")
    context: CampaignContext = Field(description="Campaign context")
    traits: Optional[Dict[str, str]] = Field(None, description="Specific NPC traits")
    relationships: Optional[Dict[str, str]] = Field(
        None,
        description="NPC's relationships with other characters"
    )


class LocationRequest(BaseModel):
    """Request for location generation."""
    location_type: LocationType = Field(description="Type of location")
    context: CampaignContext = Field(description="Campaign context")
    size: str = Field(description="Size of the location")
    purpose: str = Field(description="Location's purpose")
    occupants: Optional[List[str]] = Field(None, description="Notable occupants")
    features: Optional[List[str]] = Field(None, description="Special features")


class StoryContent(BaseModel):
    """Generated story content."""
    content_id: UUID = Field(description="Unique identifier for this content")
    element_type: StoryElement = Field(description="Type of story element")
    content: str = Field(description="Generated content")
    metadata: ContentMetadata = Field(description="Content metadata")
    parent_element_id: Optional[UUID] = None
    child_elements: List[UUID] = Field(default_factory=list)
    summary: str = Field(description="Brief content summary")


class NPCContent(BaseModel):
    """Generated NPC content."""
    content_id: UUID = Field(description="Unique identifier for this NPC")
    name: str = Field(description="NPC name")
    role: NPCRole = Field(description="NPC role")
    description: str = Field(description="Physical description")
    personality: str = Field(description="Personality description")
    motivations: List[str] = Field(description="Character motivations")
    secrets: Optional[List[str]] = Field(None, description="NPC secrets")
    relationships: Dict[str, str] = Field(
        default_factory=dict,
        description="NPC relationships"
    )
    metadata: ContentMetadata = Field(description="Content metadata")


class LocationContent(BaseModel):
    """Generated location content."""
    content_id: UUID = Field(description="Unique identifier for this location")
    name: str = Field(description="Location name")
    location_type: LocationType = Field(description="Location type")
    description: str = Field(description="Location description")
    points_of_interest: List[str] = Field(description="Notable features")
    occupants: List[str] = Field(description="Current occupants")
    secrets: Optional[List[str]] = Field(None, description="Location secrets")
    hooks: List[str] = Field(description="Story hooks tied to this location")
    metadata: ContentMetadata = Field(description="Content metadata")
