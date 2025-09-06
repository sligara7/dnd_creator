"""Character evolution models."""
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy import (
    JSON,
    Boolean,
    Column,
    DateTime,
    Enum as SQLAEnum,
    ForeignKey,
    Integer,
    String,
    Text,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship

from character_service.domain.base import Base


class EventType(str, Enum):
    """Character event types."""

    LEVEL_UP = "level_up"
    MILESTONE = "milestone"
    QUEST_COMPLETE = "quest_complete"
    ACHIEVEMENT = "achievement"
    STORY_DEVELOPMENT = "story_development"
    CAMPAIGN_EVENT = "campaign_event"
    DEATH = "death"
    RESURRECTION = "resurrection"
    THEME_TRANSITION = "theme_transition"
    PARTY_ROLE = "party_role"
    TRAINING = "training"
    CUSTOM = "custom"


class MilestoneType(str, Enum):
    """Character milestone types."""

    LEVEL = "level"
    QUEST = "quest"
    STORY = "story"
    ACHIEVEMENT = "achievement"
    THEME = "theme"
    CAMPAIGN = "campaign"
    CUSTOM = "custom"


class ProgressType(str, Enum):
    """Character progress types."""

    XP = "xp"
    MILESTONE = "milestone"
    HYBRID = "hybrid"
    CUSTOM = "custom"


class AchievementCategory(str, Enum):
    """Achievement categories."""

    COMBAT = "combat"
    ROLEPLAY = "roleplay"
    EXPLORATION = "exploration"
    STORY = "story"
    THEME = "theme"
    PARTY = "party"
    CUSTOM = "custom"


class Difficulty(str, Enum):
    """Achievement difficulty."""

    TRIVIAL = "trivial"
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    VERY_HARD = "very_hard"
    LEGENDARY = "legendary"


class CharacterEvent(Base):
    """Character event model."""

    __tablename__ = "character_events"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    event_type = Column(SQLAEnum(EventType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    impact = Column(JSON)
    campaign_event_id = Column(PGUUID)
    metadata = Column(JSON)
    is_processed = Column(Boolean, default=False)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    milestones = relationship("CharacterMilestone", back_populates="event")


class CharacterMilestone(Base):
    """Character milestone model."""

    __tablename__ = "character_milestones"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    event_id = Column(PGUUID, ForeignKey("character_events.id"))
    milestone_type = Column(SQLAEnum(MilestoneType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    requirements = Column(JSON)
    rewards = Column(JSON)
    campaign_milestone_id = Column(PGUUID)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    event = relationship("CharacterEvent", back_populates="milestones")
    progress = relationship("CharacterProgress", back_populates="milestone")


class CharacterProgress(Base):
    """Character progress model."""

    __tablename__ = "character_progress"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    milestone_id = Column(PGUUID, ForeignKey("character_milestones.id"))
    progress_type = Column(SQLAEnum(ProgressType), nullable=False)
    current_xp = Column(Integer, default=0)
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    milestones_completed = Column(Integer, default=0)
    level_progression = Column(JSON)
    requirements = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    # Relationships
    milestone = relationship("CharacterMilestone", back_populates="progress")


class ProgressSnapshot(Base):
    """Progress snapshot model for state capture."""

    __tablename__ = "progress_snapshots"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    event_id = Column(PGUUID, ForeignKey("character_events.id"))
    snapshot_type = Column(String(50), nullable=False)
    state_before = Column(JSON, nullable=False)
    state_after = Column(JSON)
    diff = Column(JSON)
    metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class CharacterAchievement(Base):
    """Character achievement model."""

    __tablename__ = "character_achievements"

    id = Column(PGUUID, primary_key=True)
    character_id = Column(PGUUID, ForeignKey("characters.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    category = Column(SQLAEnum(AchievementCategory), nullable=False)
    difficulty = Column(SQLAEnum(Difficulty), nullable=False)
    requirements = Column(JSON)
    rewards = Column(JSON)
    points = Column(Integer, default=0)
    campaign_achievement_id = Column(PGUUID)
    completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)
    metadata = Column(JSON)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow)
