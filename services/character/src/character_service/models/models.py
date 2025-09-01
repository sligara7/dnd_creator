"""SQLAlchemy models for the Character Service"""

from datetime import datetime
from uuid import UUID, uuid4
from sqlalchemy import Column, DateTime, ForeignKey, String, Integer, Boolean, Text, JSON
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.orm import relationship
from character_service.core.database import Base

class InventoryItem(Base):
    """Inventory item model."""
    __tablename__ = "inventory_items"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    root_id = Column(PGUUID(as_uuid=True))  # Original item this was adapted from
    theme = Column(String, nullable=False, server_default="traditional")
    character_id = Column(PGUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    item_data = Column(JSONB, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    equipped = Column(Boolean, nullable=False, default=False)
    container = Column(String)
    notes = Column(Text)
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    character = relationship("Character", back_populates="inventory_items")


class Character(Base):
    """Character model."""
    __tablename__ = "characters"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    parent_id = Column(PGUUID(as_uuid=True))  # Previous version in theme chain
    theme = Column(String, nullable=False, server_default="traditional")
    name = Column(String, nullable=False)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    campaign_id = Column(PGUUID(as_uuid=True), nullable=False)
    character_data = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    journal_entries = relationship("JournalEntry", back_populates="character")
    inventory_items = relationship("InventoryItem", back_populates="character")

class JournalEntry(Base):
    """Journal entry model."""
    __tablename__ = "journal_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    character_id = Column(PGUUID(as_uuid=True), ForeignKey("characters.id"), nullable=False)
    entry_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, server_default="{}")
    tags = Column(JSONB, nullable=False, server_default="[]")
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)
    is_active = Column(Boolean, nullable=False, server_default="true")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Session-related fields
    session_number = Column(Integer)
    session_date = Column(DateTime)
    dm_name = Column(String)
    session_summary = Column(Text)

    # Relationships
    character = relationship("Character", back_populates="journal_entries")
    experience_entries = relationship("ExperienceEntry", back_populates="journal_entry")
    quests = relationship("Quest", back_populates="journal_entry")
    npc_relationships = relationship("NPCRelationship", back_populates="journal_entry")

class ExperienceEntry(Base):
    """Experience entry model."""
    __tablename__ = "experience_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_entry_id = Column(PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    session_id = Column(PGUUID(as_uuid=True))
    data = Column(JSONB, nullable=False, server_default="{}")
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="experience_entries")

class Quest(Base):
    """Quest model."""
    __tablename__ = "quests"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_entry_id = Column(PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, server_default="active")
    importance = Column(String, nullable=False, server_default="normal")
    assigned_by = Column(String)
    rewards = Column(JSONB, nullable=False, server_default="{}")
    progress = Column(JSONB, nullable=False, server_default="[]")
    data = Column(JSONB, nullable=False, server_default="{}")
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="quests")

class NPCRelationship(Base):
    """NPC relationship model."""
    __tablename__ = "npc_relationships"

    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    journal_entry_id = Column(PGUUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    npc_id = Column(PGUUID(as_uuid=True), nullable=False)
    npc_name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    standing = Column(Integer, nullable=False, server_default="0")
    notes = Column(Text)
    last_interaction = Column(DateTime)
    data = Column(JSONB, nullable=False, server_default="{}")
    is_deleted = Column(Boolean, nullable=False, server_default="false")
    deleted_at = Column(DateTime)

    # Relationships
    journal_entry = relationship("JournalEntry", back_populates="npc_relationships")
