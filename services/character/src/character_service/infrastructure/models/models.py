"""SQLAlchemy models for the Character Service."""
from datetime import datetime
from uuid import UUID

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    text,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlalchemy.orm import Mapped, relationship

from character_service.infrastructure.models.base import Base


class Character(Base):
    """Character model using JSONB for flexible data storage."""
    __tablename__ = "characters"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    parent_id = Column(PGUUID(as_uuid=True), nullable=True)
    theme = Column(String, server_default='traditional', nullable=False)
    name = Column(String, nullable=False, index=True)
    user_id = Column(PGUUID(as_uuid=True), nullable=False)
    campaign_id = Column(PGUUID(as_uuid=True), nullable=False)
    character_data = Column(JSONB, nullable=False)
    is_active = Column(Boolean, nullable=False, server_default=text('true'))
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))

    # Relationships
    journal_entries: Mapped[list["JournalEntry"]] = relationship(
        "JournalEntry",
        back_populates="character",
        cascade="all, delete-orphan",
    )


class InventoryItem(Base):
    """Individual inventory item model."""
    __tablename__ = "inventory_items"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    root_id = Column(PGUUID(as_uuid=True), nullable=True)
    theme = Column(String, server_default='traditional', nullable=False)
    character_id = Column(PGUUID(as_uuid=True), nullable=False, index=True)
    item_data = Column(JSONB, nullable=False)
    quantity = Column(Integer, nullable=False, server_default=text('1'))
    equipped = Column(Boolean, nullable=False, server_default=text('false'))
    container = Column(String, nullable=True)
    notes = Column(Text, nullable=True)
    is_deleted = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))


class JournalEntry(Base):
    """Journal entry model with enhanced fields."""
    __tablename__ = "journal_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    character_id = Column(PGUUID(as_uuid=True), ForeignKey('characters.id'), nullable=False, index=True)
    entry_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, server_default=text('{}'))
    tags = Column(JSONB, nullable=False, server_default=text('[]'))
    is_deleted = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, nullable=False, server_default=text('true'))
    session_number = Column(Integer, nullable=True)
    session_date = Column(DateTime, nullable=True)
    dm_name = Column(String, nullable=True)
    session_summary = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=text('now()'))
    updated_at = Column(DateTime, nullable=False, server_default=text('now()'))

    # Relationships
    character: Mapped[Character] = relationship(
        "Character",
        back_populates="journal_entries",
    )
    experience_entries: Mapped[list["ExperienceEntry"]] = relationship(
        "ExperienceEntry",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
    quests: Mapped[list["Quest"]] = relationship(
        "Quest",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )
    npc_relationships: Mapped[list["NPCRelationship"]] = relationship(
        "NPCRelationship",
        back_populates="journal_entry",
        cascade="all, delete-orphan",
    )


class ExperienceEntry(Base):
    """Experience entry model for tracking character advancement."""
    __tablename__ = "experience_entries"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(
        PGUUID(as_uuid=True), 
        ForeignKey('journal_entries.id'), 
        nullable=False, 
        index=True
    )
    amount = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False)
    session_id = Column(PGUUID(as_uuid=True), nullable=True)
    data = Column(JSONB, nullable=False, server_default=text('{}'))
    is_deleted = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    journal_entry: Mapped[JournalEntry] = relationship(
        "JournalEntry",
        back_populates="experience_entries",
    )


class Quest(Base):
    """Quest model for tracking character missions and objectives."""
    __tablename__ = "quests"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(
        PGUUID(as_uuid=True), 
        ForeignKey('journal_entries.id'), 
        nullable=False, 
        index=True
    )
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, server_default=text('active'))
    importance = Column(String, nullable=False, server_default=text('normal'))
    assigned_by = Column(String, nullable=True)
    rewards = Column(JSONB, nullable=False, server_default=text('{}'))
    progress = Column(JSONB, nullable=False, server_default=text('[]'))
    data = Column(JSONB, nullable=False, server_default=text('{}'))
    is_deleted = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    journal_entry: Mapped[JournalEntry] = relationship(
        "JournalEntry",
        back_populates="quests",
    )


class NPCRelationship(Base):
    """NPC relationship model for tracking character interactions."""
    __tablename__ = "npc_relationships"

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(
        PGUUID(as_uuid=True), 
        ForeignKey('journal_entries.id'), 
        nullable=False, 
        index=True
    )
    npc_id = Column(PGUUID(as_uuid=True), nullable=False)
    npc_name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    standing = Column(Integer, nullable=False, server_default=text('0'))
    notes = Column(Text, nullable=True)
    last_interaction = Column(DateTime, nullable=True)
    data = Column(JSONB, nullable=False, server_default=text('{}'))
    is_deleted = Column(Boolean, nullable=False, server_default=text('false'))
    deleted_at = Column(DateTime, nullable=True)

    # Relationships
    journal_entry: Mapped[JournalEntry] = relationship(
        "JournalEntry",
        back_populates="npc_relationships",
    )
