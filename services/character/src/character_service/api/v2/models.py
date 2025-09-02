"""API models for the Character Service."""
from datetime import datetime
from typing import Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CharacterCreate(BaseModel):
    """Request model for creating a character."""

    name: str = Field(..., description="Character name")
    theme: str = Field("traditional", description="Character theme")
    user_id: UUID = Field(..., description="ID of user creating the character")
    campaign_id: UUID = Field(..., description="ID of campaign the character belongs to")
    character_data: Optional[Dict] = Field(None, description="Initial character data")


class CharacterResponse(BaseModel):
    """Response model for character data."""

    id: UUID
    parent_id: Optional[UUID]
    theme: str
    name: str
    user_id: UUID
    campaign_id: UUID
    character_data: Dict
    is_active: bool
    created_at: datetime
    updated_at: datetime


class InventoryItemCreate(BaseModel):
    """Request model for creating an inventory item."""

    item_data: Dict = Field(..., description="Item data")
    quantity: int = Field(1, description="Item quantity")
    equipped: bool = Field(False, description="Whether item is equipped")
    container: Optional[str] = Field(None, description="Container storing the item")
    notes: Optional[str] = Field(None, description="Item notes")


class InventoryItemUpdate(BaseModel):
    """Request model for updating an inventory item."""

    quantity: Optional[int] = None
    equipped: Optional[bool] = None
    container: Optional[str] = None
    notes: Optional[str] = None


class InventoryItemResponse(BaseModel):
    """Response model for inventory item data."""

    id: UUID
    root_id: Optional[UUID]
    theme: str
    character_id: UUID
    item_data: Dict
    quantity: int
    equipped: bool
    container: Optional[str]
    notes: Optional[str]
    is_deleted: bool
    deleted_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime


class JournalEntryCreate(BaseModel):
    """Request model for creating a journal entry."""

    entry_type: str = Field(..., description="Type of journal entry")
    title: str = Field(..., description="Entry title")
    content: str = Field(..., description="Entry content")
    data: Optional[Dict] = Field({}, description="Additional entry data")
    tags: Optional[List[str]] = Field([], description="Entry tags")
    session_number: Optional[int] = Field(None, description="Session number")
    session_date: Optional[datetime] = Field(None, description="Session date")
    dm_name: Optional[str] = Field(None, description="DM's name")
    session_summary: Optional[str] = Field(None, description="Session summary")


class JournalEntryResponse(BaseModel):
    """Response model for journal entry data."""

    id: UUID
    character_id: UUID
    entry_type: str
    timestamp: datetime
    title: str
    content: str
    data: Dict
    tags: List[str]
    session_number: Optional[int]
    session_date: Optional[datetime]
    dm_name: Optional[str]
    session_summary: Optional[str]
    is_deleted: bool
    deleted_at: Optional[datetime]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ExperienceEntryCreate(BaseModel):
    """Request model for creating an experience entry."""

    amount: int = Field(..., description="Experience points amount")
    source: str = Field(..., description="Source of experience points")
    reason: str = Field(..., description="Reason for experience points")
    session_id: Optional[UUID] = Field(None, description="Associated session ID")
    data: Optional[Dict] = Field({}, description="Additional experience data")


class ExperienceEntryResponse(BaseModel):
    """Response model for experience entry data."""

    id: UUID
    journal_entry_id: UUID
    amount: int
    source: str
    reason: str
    timestamp: datetime
    session_id: Optional[UUID]
    data: Dict
    is_deleted: bool
    deleted_at: Optional[datetime]


class QuestCreate(BaseModel):
    """Request model for creating a quest."""

    title: str = Field(..., description="Quest title")
    description: str = Field(..., description="Quest description")
    status: str = Field("active", description="Quest status")
    importance: str = Field("normal", description="Quest importance")
    assigned_by: Optional[str] = Field(None, description="Quest giver")
    rewards: Optional[Dict] = Field({}, description="Quest rewards")
    data: Optional[Dict] = Field({}, description="Additional quest data")


class QuestResponse(BaseModel):
    """Response model for quest data."""

    id: UUID
    journal_entry_id: UUID
    title: str
    description: str
    status: str
    importance: str
    assigned_by: Optional[str]
    rewards: Dict
    progress: List[Dict]
    data: Dict
    is_deleted: bool
    deleted_at: Optional[datetime]


class NPCRelationshipCreate(BaseModel):
    """Request model for creating an NPC relationship."""

    npc_id: UUID = Field(..., description="NPC's ID")
    npc_name: str = Field(..., description="NPC's name")
    relationship_type: str = Field(..., description="Type of relationship")
    standing: int = Field(0, description="Relationship standing")
    notes: Optional[str] = Field(None, description="Relationship notes")
    data: Optional[Dict] = Field({}, description="Additional relationship data")


class NPCRelationshipResponse(BaseModel):
    """Response model for NPC relationship data."""

    id: UUID
    journal_entry_id: UUID
    npc_id: UUID
    npc_name: str
    relationship_type: str
    standing: int
    notes: Optional[str]
    last_interaction: datetime
    data: Dict
    is_deleted: bool
    deleted_at: Optional[datetime]


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
