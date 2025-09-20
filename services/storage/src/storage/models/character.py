from uuid import UUID
from sqlalchemy import Column, String, Text, JSON, ForeignKey, Integer, Boolean, DateTime
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.sql import func

from ...db.base import Base

class Character(Base):
    __tablename__ = "characters"
    __table_args__ = {"schema": "character_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    name = Column(String(255), nullable=False)
    level = Column(Integer, nullable=False, server_default='1')
    race = Column(String(255), nullable=False)
    character_class = Column(String(255), nullable=False)
    background = Column(String(255), nullable=False)
    alignment = Column(String(50))
    experience_points = Column(Integer, nullable=False, server_default='0')

    # Ability Scores
    strength = Column(Integer, nullable=False)
    dexterity = Column(Integer, nullable=False)
    constitution = Column(Integer, nullable=False)
    intelligence = Column(Integer, nullable=False)
    wisdom = Column(Integer, nullable=False)
    charisma = Column(Integer, nullable=False)

    # Character Stats
    max_hit_points = Column(Integer, nullable=False)
    current_hit_points = Column(Integer, nullable=False)
    temporary_hit_points = Column(Integer, nullable=False, server_default='0')
    armor_class = Column(Integer, nullable=False)
    initiative = Column(Integer, nullable=False)
    speed = Column(Integer, nullable=False)
    inspiration = Column(Boolean, nullable=False, server_default='false')
    proficiency_bonus = Column(Integer, nullable=False)

    # Character Details
    personality_traits = Column(Text)
    ideals = Column(Text)
    bonds = Column(Text)
    flaws = Column(Text)
    backstory = Column(Text)
    appearance = Column(Text)

    # Extended Data
    spells = Column(JSON, nullable=False, server_default='[]')
    inventory = Column(JSON, nullable=False, server_default='[]')
    features = Column(JSON, nullable=False, server_default='[]')
    proficiencies = Column(JSON, nullable=False, server_default='[]')
    campaign_notes = Column(JSON, nullable=False, server_default='[]')
    journal_entries = Column(JSON, nullable=False, server_default='[]')
    relationships = Column(JSON, nullable=False, server_default='[]')

    # Theme and Campaign Data
    campaign_id = Column(PGUUID(as_uuid=True))
    theme_id = Column(PGUUID(as_uuid=True))
    theme_data = Column(JSON, nullable=False, server_default='{}')

    # Metadata
    creator_id = Column(PGUUID(as_uuid=True), nullable=False)
    owner_id = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))

class CharacterVersion(Base):
    __tablename__ = "character_versions"
    __table_args__ = {"schema": "character_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    character_id = Column(PGUUID(as_uuid=True), ForeignKey('character_db.characters.id'))
    version_number = Column(Integer, nullable=False)
    change_type = Column(String(50), nullable=False)
    changes = Column(JSON, nullable=False)
    metadata = Column(JSON, nullable=False, server_default='{}')
    created_by = Column(PGUUID(as_uuid=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))

class CharacterProgress(Base):
    __tablename__ = "character_progress"
    __table_args__ = {"schema": "character_db"}

    id = Column(PGUUID(as_uuid=True), primary_key=True)
    character_id = Column(PGUUID(as_uuid=True), ForeignKey('character_db.characters.id'))
    progress_type = Column(String(50), nullable=False)
    milestone = Column(String(255), nullable=False)
    status = Column(String(50), nullable=False)
    details = Column(JSON, nullable=False, server_default='{}')
    completed_at = Column(DateTime(timezone=True))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    is_deleted = Column(Boolean, nullable=False, server_default='false')
    deleted_at = Column(DateTime(timezone=True))