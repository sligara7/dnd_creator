"""Campaign database models."""

from uuid import UUID
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB
from sqlalchemy.sql import func

from ...db.base import Base


class Campaign(Base):
    """Campaign model.

    Represents a D&D campaign, including its theme, metadata, and state.
    """
    __tablename__ = "campaigns"
    __table_args__ = {"schema": "campaign_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    campaign_type = Column(String(50), nullable=False, server_default='traditional')
    state = Column(String(50), nullable=False, server_default='draft')
    theme_id = Column(PGUUID(as_uuid=True))
    theme_data = Column(JSONB, nullable=False, server_default='{}')
    campaign_metadata = Column(JSONB, nullable=False, server_default='{}')
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))


class Chapter(Base):
    """Chapter model.

    Represents a chapter within a campaign, including its content, prerequisites,
    and sequence information.
    """
    __tablename__ = "chapters"
    __table_args__ = {"schema": "campaign_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    campaign_id = Column(PGUUID(as_uuid=True), ForeignKey('campaign_db.campaigns.id'))
    title = Column(String(255), nullable=False)
    description = Column(Text)
    chapter_type = Column(String(50), nullable=False, server_default='story')
    state = Column(String(50), nullable=False, server_default='draft')
    sequence_number = Column(Integer, nullable=False)
    content = Column(JSONB, nullable=False, server_default='{}')
    chapter_metadata = Column(JSONB, nullable=False, server_default='{}')
    prerequisites = Column(JSONB, nullable=False, server_default='[]')
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))