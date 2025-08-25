"""
Journal Database Models

SQLAlchemy models for journal entries and related data.
"""

from typing import Dict, Any
import json
from datetime import datetime
from sqlalchemy import (
    Column, String, Integer, DateTime, Text, ForeignKey,
    Index, JSON, Boolean, UniqueConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import JSONB, UUID

from src.models.database_models import Base
from src.core.logging_config import get_logger

logger = get_logger(__name__)

class JournalEntryDB(Base):
    """Database model for journal entries."""
    __tablename__ = "journal_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    character_id = Column(String, ForeignKey("characters.id"), nullable=False)
    entry_type = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    data = Column(JSONB, nullable=False, default=dict)
    tags = Column(JSONB, nullable=False, default=list)
    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    character = relationship("Character", back_populates="journal_entries")
    experience = relationship("ExperienceEntryDB", back_populates="journal_entry")
    quests = relationship("QuestDB", back_populates="journal_entry")
    relationships = relationship("NPCRelationshipDB", back_populates="journal_entry")
    
    # Indices
    __table_args__ = (
        Index("idx_journal_character_id", "character_id"),
        Index("idx_journal_entry_type", "entry_type"),
        Index("idx_journal_timestamp", "timestamp"),
        Index("idx_journal_tags", "tags", postgresql_using="gin"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert database model to dictionary."""
        return {
            "id": str(self.id),
            "character_id": self.character_id,
            "entry_type": self.entry_type,
            "timestamp": self.timestamp.isoformat(),
            "title": self.title,
            "content": self.content,
            "data": self.data,
            "tags": self.tags,
            "experience": [xp.to_dict() for xp in self.experience],
            "quests": [quest.to_dict() for quest in self.quests],
            "relationships": [rel.to_dict() for rel in self.relationships]
        }

class ExperienceEntryDB(Base):
    """Database model for experience entries."""
    __tablename__ = "experience_entries"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    amount = Column(Integer, nullable=False)
    source = Column(String, nullable=False)
    reason = Column(String, nullable=False)
    timestamp = Column(DateTime, nullable=False, default=datetime.utcnow)
    session_id = Column(String)
    data = Column(JSONB, nullable=False, default=dict)
    
    # Relationships
    journal_entry = relationship("JournalEntryDB", back_populates="experience")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert database model to dictionary."""
        return {
            "id": str(self.id),
            "amount": self.amount,
            "source": self.source,
            "reason": self.reason,
            "timestamp": self.timestamp.isoformat(),
            "session_id": self.session_id,
            "data": self.data
        }

class QuestDB(Base):
    """Database model for quests."""
    __tablename__ = "quests"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False, default="active")
    importance = Column(String, nullable=False, default="normal")
    assigned_by = Column(String)
    rewards = Column(JSONB, nullable=False, default=dict)
    progress = Column(JSONB, nullable=False, default=list)
    data = Column(JSONB, nullable=False, default=dict)
    
    # Relationships
    journal_entry = relationship("JournalEntryDB", back_populates="quests")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert database model to dictionary."""
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "importance": self.importance,
            "assigned_by": self.assigned_by,
            "rewards": self.rewards,
            "progress": self.progress,
            "data": self.data
        }

class NPCRelationshipDB(Base):
    """Database model for NPC relationships."""
    __tablename__ = "npc_relationships"
    
    id = Column(UUID(as_uuid=True), primary_key=True)
    journal_entry_id = Column(UUID(as_uuid=True), ForeignKey("journal_entries.id"), nullable=False)
    npc_id = Column(String, nullable=False)
    npc_name = Column(String, nullable=False)
    relationship_type = Column(String, nullable=False)
    standing = Column(Integer, nullable=False, default=0)
    notes = Column(Text)
    last_interaction = Column(DateTime)
    data = Column(JSONB, nullable=False, default=dict)
    
    # Relationships
    journal_entry = relationship("JournalEntryDB", back_populates="relationships")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint("journal_entry_id", "npc_id", name="uq_relationship_npc"),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert database model to dictionary."""
        return {
            "id": str(self.id),
            "npc_id": self.npc_id,
            "npc_name": self.npc_name,
            "relationship_type": self.relationship_type,
            "standing": self.standing,
            "notes": self.notes,
            "last_interaction": self.last_interaction.isoformat() if self.last_interaction else None,
            "data": self.data
        }
