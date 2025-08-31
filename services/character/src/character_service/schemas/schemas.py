"""Pydantic Schemas for Character Service"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class DirectEditRequest(BaseModel):
    updates: Dict[str, Any] = {}
    notes: Optional[str] = None

class CharacterBase(BaseModel):
    """Base Character Schema"""
    name: str
    race: str
    class_: str
    background: str
    alignment: str
    data: Dict[str, Any] = Field(default_factory=dict)
    level: Optional[int] = Field(default=1, ge=1)
    experience: Optional[int] = Field(default=0, ge=0)

class CharacterCreate(CharacterBase):
    """Character Creation Schema"""
    pass

class CharacterUpdate(CharacterBase):
    """Character Update Schema"""
    pass

class Character(CharacterBase):
    """Character Response Schema"""
    id: int
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
    character_id: int

class JournalEntryUpdate(BaseModel):
    """Journal Entry Update Schema"""
    title: Optional[str] = None
    content: Optional[str] = None
    entry_type: Optional[str] = None

class JournalEntry(JournalEntryBase):
    """Journal Entry Response Schema"""
    id: int
    character_id: int
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
    character_id: int

class InventoryItemUpdate(BaseModel):
    """Inventory Item Update Schema"""
    item_data: Optional[Dict[str, Any]] = None
    quantity: Optional[int] = Field(default=None, ge=0)

class InventoryItem(InventoryItemBase):
    """Inventory Item Response Schema"""
    id: int
    character_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CharacterVersionBase(BaseModel):
    """Base Character Version Schema"""
    character_id: int
    version_number: int
    character_data: Dict[str, Any]
    change_description: str

class CharacterVersion(CharacterVersionBase):
    """Character Version Response Schema"""
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
