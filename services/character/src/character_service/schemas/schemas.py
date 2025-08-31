"""Pydantic Schemas for Character Service"""

from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class CharacterBase(BaseModel):
    """Base Character Schema"""
    name: str
    user_id: str
    campaign_id: Optional[str] = None
    character_data: Dict[str, Any]

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
