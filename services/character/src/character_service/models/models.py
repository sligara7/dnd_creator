"""Database Models for Character Service"""

from datetime import datetime
from typing import List, Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Character(Base):
    """Core Character Model"""
    __tablename__ = "characters"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    user_id = Column(String, index=True)
    campaign_id = Column(String, nullable=True, index=True)
    character_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="character")
    inventory_items = relationship("InventoryItem", back_populates="character")
    character_versions = relationship("CharacterVersion", back_populates="character")

class JournalEntry(Base):
    """Character Journal Entries"""
    __tablename__ = "journal_entries"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    title = Column(String)
    content = Column(Text)
    entry_type = Column(String)  # session, milestone, xp, etc.
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="journal_entries")

class InventoryItem(Base):
    """Character Inventory Items"""
    __tablename__ = "inventory_items"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    item_data = Column(JSON)
    quantity = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="inventory_items")

class CharacterVersion(Base):
    """Character Version History"""
    __tablename__ = "character_versions"

    id = Column(Integer, primary_key=True, index=True)
    character_id = Column(Integer, ForeignKey("characters.id"))
    version_number = Column(Integer)
    character_data = Column(JSON)
    change_description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="character_versions")
