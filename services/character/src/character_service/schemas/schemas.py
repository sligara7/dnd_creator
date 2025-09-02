"""Pydantic Schemas for Character Service"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

class DirectEditRequest(BaseModel):
    updates: Dict[str, Any] = Field(default_factory=dict)
    notes: Optional[str] = None

class CharacterBase(BaseModel):
    """Base Character Schema aligned with the Character model"""
    name: str
    user_id: UUID
    campaign_id: UUID
    parent_id: Optional[UUID] = None
    theme: str = Field(default="traditional")
    character_data: Dict[str, Any] = Field(default_factory=dict)
    is_active: bool = True

class CharacterCreate(CharacterBase):
    """Character Creation Schema"""
    pass

class CharacterUpdate(BaseModel):
    """Character Update Schema"""
    name: Optional[str] = None
    user_id: Optional[UUID] = None
    campaign_id: Optional[UUID] = None
    theme: Optional[str] = None
    character_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

class Character(BaseModel):
    """Character Response Schema"""
    id: UUID
    name: str
    user_id: UUID
    campaign_id: UUID
    parent_id: Optional[UUID] = None
    theme: str
    character_data: Dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class JournalEntryBase(BaseModel):
    """Base Journal Entry Schema"""
    title: str
    content: str
    entry_type: str

class JournalEntryCreate(JournalEntryBase):
    """Journal Entry Creation Schema"""
    character_id: UUID

class JournalEntryUpdate(BaseModel):
    """Journal Entry Update Schema"""
    title: Optional[str] = None
    content: Optional[str] = None
    entry_type: Optional[str] = None

class JournalEntry(JournalEntryBase):
    """Journal Entry Response Schema"""
    id: UUID
    character_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InventoryItemBase(BaseModel):
    """Base Inventory Item Schema"""
    item_data: Dict[str, Any]
    quantity: int = Field(default=1, ge=0)

class InventoryItemCreate(InventoryItemBase):
    """Inventory Item Creation Schema"""
    character_id: UUID

class InventoryItemUpdate(BaseModel):
    """Inventory Item Update Schema"""
    item_data: Optional[Dict[str, Any]] = None
    quantity: Optional[int] = Field(default=None, ge=0)

class InventoryItem(InventoryItemBase):
    """Inventory Item Response Schema"""
    id: UUID
    character_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CombatState(BaseModel):
    """Combat state information."""
    current_hp: int
    temp_hp: int = 0
    conditions: List[str] = Field(default_factory=list)
    death_saves: Dict[str, int] = Field(
        default_factory=lambda: {"successes": 0, "failures": 0}
    )
    concentration: Dict[str, Any] = Field(
        default_factory=lambda: {"active": False, "spell": None}
    )
    exhaustion: int = 0

class ResourceState(BaseModel):
    """Character resource information."""
    hit_dice: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Mapping of hit die type (e.g. 'd10') to {total, used}"
    )
    spell_slots: Dict[str, Dict[str, int]] = Field(
        default_factory=dict,
        description="Mapping of spell level to {total, used}"
    )
    class_resources: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="List of class-specific resource states"
    )

class CharacterVersionBase(BaseModel):
    """Base Character Version Schema"""
    character_id: UUID
    version_number: int
    character_data: Dict[str, Any]
    change_description: str

class CharacterVersion(CharacterVersionBase):
    """Character Version Response Schema"""
    id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
