"""
Simplified Database Models for D&D Campaign Creation with Git-like Chapter Versioning

This file contains only the campaign-related models with git-like versioning support.
Character creation models have been removed for simplification.
"""

import uuid
import enum
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, Optional, List, TYPE_CHECKING

from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker

# Configure logging
logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from .database_models import Campaign, Chapter, PlotFork

# Custom UUID type that works with SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(36) storing as stringified hex values.
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID())
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return str(value)
        else:
            if not isinstance(value, uuid.UUID):
                return str(uuid.UUID(value))
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value

Base = declarative_base()

# ============================================================================
# CAMPAIGN STATUS ENUMS
# ============================================================================

class CampaignStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"

class ChapterStatusEnum(str, enum.Enum):
    DRAFT = "draft"
    FINALIZED = "finalized"
    IN_PROGRESS = "in_progress"

class PlotForkTypeEnum(str, enum.Enum):
    BRANCH = "branch"
    MERGE = "merge"
    ALTERNATE = "alternate"

# ============================================================================
# GIT-LIKE CHAPTER VERSIONING ENUMS
# ============================================================================

class ChapterVersionTypeEnum(str, enum.Enum):
    """Types of chapter versions in the git-like system."""
    SKELETON = "skeleton"          # Initial bare-bones chapter outline
    DRAFT = "draft"               # Work-in-progress chapter content
    PUBLISHED = "published"       # Finalized chapter ready for play
    PLAYED = "played"            # Chapter that has been played by players
    BRANCH = "branch"            # Alternative storyline branch
    MERGE = "merge"              # Merged multiple storylines

class BranchTypeEnum(str, enum.Enum):
    """Types of story branches."""
    MAIN = "main"                # Primary storyline (like git main/master)
    ALTERNATE = "alternate"      # Alternative story path
    PLAYER_CHOICE = "player_choice"  # Branch created by player decisions
    EXPERIMENTAL = "experimental"    # Testing new story ideas
    PARALLEL = "parallel"       # Concurrent storylines

class PlaySessionStatusEnum(str, enum.Enum):
    """Status of play sessions."""
    SCHEDULED = "scheduled"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# ============================================================================
# CORE CAMPAIGN MODELS
# ============================================================================

class Campaign(Base):
    """
    Core campaign model with git-like versioning support.
    
    Each campaign can have multiple chapters with branching storylines,
    similar to a git repository with branches and commits.
    """
    __tablename__ = "campaigns"
    
    # Core identification
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    title = Column(String(200), nullable=False)
    description = Column(Text)
    themes = Column(JSON, default=list)
    gm_notes = Column(Text)
    status = Column(String(20), default=CampaignStatusEnum.DRAFT.value)
    
    # Git-like versioning metadata
    current_branch = Column(String(100), default="main")
    total_chapters = Column(Integer, default=0)
    total_branches = Column(Integer, default=1)
    last_played_session = Column(String(36), nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Traditional relationships (maintained for backward compatibility)
    chapters = relationship("Chapter", back_populates="campaign", cascade="all, delete-orphan")
    
    # New git-like versioning relationships
    chapter_versions = relationship("ChapterVersion", back_populates="campaign", cascade="all, delete-orphan")
    branches = relationship("CampaignBranch", back_populates="campaign", cascade="all, delete-orphan")
    choices = relationship("ChapterChoice", back_populates="campaign", cascade="all, delete-orphan")
    play_sessions = relationship("PlaySession", back_populates="campaign", cascade="all, delete-orphan")
    merges = relationship("ChapterMerge", back_populates="campaign", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign to dictionary format."""
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "themes": self.themes,
            "gm_notes": self.gm_notes,
            "status": self.status,
            "current_branch": self.current_branch,
            "total_chapters": self.total_chapters,
            "total_branches": self.total_branches,
            "last_played_session": self.last_played_session,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class Chapter(Base):
    """
    Traditional chapter model (maintained for backward compatibility).
    
    For new git-like versioning, use ChapterVersion instead.
    """
    __tablename__ = "chapters"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    status = Column(String(20), default=ChapterStatusEnum.DRAFT.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="chapters")
    plot_forks = relationship("PlotFork", back_populates="chapter", cascade="all, delete-orphan")

class PlotFork(Base):
    """
    Traditional plot fork model (maintained for backward compatibility).
    
    For new git-like versioning, use ChapterChoice and branching instead.
    """
    __tablename__ = "plot_forks"
    
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), nullable=False)
    fork_type = Column(String(20), nullable=False)
    description = Column(Text)
    options = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    chapter = relationship("Chapter", back_populates="plot_forks")

# ============================================================================
# GIT-LIKE CHAPTER VERSIONING MODELS
# ============================================================================

class ChapterVersion(Base):
    """
    Git-like chapter versioning model.
    
    Each chapter can have multiple versions (like git commits),
    with full lineage tracking and branching support.
    """
    __tablename__ = "chapter_versions"
    
    # Core identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Git-like versioning fields
    version_hash = Column(String(12), unique=True, nullable=False, index=True)
    parent_hashes = Column(JSON, default=list)  # List of parent version hashes
    branch_name = Column(String(100), default="main", nullable=False, index=True)
    version_type = Column(String(20), default=ChapterVersionTypeEnum.DRAFT.value)
    
    # Content fields
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(JSON)  # Full chapter content as JSON
    chapter_order = Column(Integer, default=0)  # Order within campaign
    
    # Commit metadata
    commit_message = Column(Text)
    author = Column(String(100), default="system")
    commit_timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Player interaction data
    player_choices = Column(JSON, default=dict)  # Choices that led to this version
    player_consequences = Column(JSON, default=dict)  # Results of player actions
    dm_notes = Column(Text)
    
    # Session tracking
    play_session_id = Column(String(36), ForeignKey("play_sessions.id"), nullable=True)
    session_date = Column(DateTime, nullable=True)
    
    # Version management
    is_head = Column(Boolean, default=True)  # Is this the latest version in its branch?
    is_active = Column(Boolean, default=True)
    merge_parent_hashes = Column(JSON, default=list)  # For merge commits
    
    # Standard timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="chapter_versions")
    play_session = relationship("PlaySession", back_populates="chapter_versions")
    choices = relationship("ChapterChoice", back_populates="chapter_version")
    
    def generate_version_hash(self) -> str:
        """Generate a git-like hash for this chapter version."""
        hash_data = {
            "title": self.title,
            "content": self.content,
            "parent_hashes": sorted(self.parent_hashes) if self.parent_hashes else [],
            "timestamp": self.commit_timestamp.isoformat() if self.commit_timestamp else datetime.utcnow().isoformat(),
            "author": self.author
        }
        hash_string = str(hash_data)
        return hashlib.sha256(hash_string.encode()).hexdigest()[:12]  # 12-char hash like git
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter version to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "version_hash": self.version_hash,
            "parent_hashes": self.parent_hashes,
            "branch_name": self.branch_name,
            "version_type": self.version_type,
            "title": self.title,
            "summary": self.summary,
            "content": self.content,
            "chapter_order": self.chapter_order,
            "commit_message": self.commit_message,
            "author": self.author,
            "commit_timestamp": self.commit_timestamp.isoformat() if self.commit_timestamp else None,
            "player_choices": self.player_choices,
            "player_consequences": self.player_consequences,
            "dm_notes": self.dm_notes,
            "play_session_id": self.play_session_id,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "is_head": self.is_head,
            "is_active": self.is_active,
            "merge_parent_hashes": self.merge_parent_hashes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class CampaignBranch(Base):
    """
    Story branches within a campaign (like git branches).
    
    Tracks different storyline paths and alternate endings.
    """
    __tablename__ = "campaign_branches"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Branch identification
    name = Column(String(100), nullable=False, index=True)
    branch_type = Column(String(20), default=BranchTypeEnum.MAIN.value)
    
    # Branch metadata
    description = Column(Text)
    head_commit = Column(String(12), nullable=False)  # Latest chapter version hash
    parent_branch = Column(String(100), nullable=True)
    
    # Branch status
    is_active = Column(Boolean, default=True)
    is_merged = Column(Boolean, default=False)
    merged_into_branch = Column(String(100), nullable=True)
    merge_timestamp = Column(DateTime, nullable=True)
    
    # Creation tracking
    created_by = Column(String(100), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="branches")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert campaign branch to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "branch_type": self.branch_type,
            "description": self.description,
            "head_commit": self.head_commit,
            "parent_branch": self.parent_branch,
            "is_active": self.is_active,
            "is_merged": self.is_merged,
            "merged_into_branch": self.merged_into_branch,
            "merge_timestamp": self.merge_timestamp.isoformat() if self.merge_timestamp else None,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }

class ChapterChoice(Base):
    """
    Player choices that create new branches or affect story direction.
    
    Tracks significant player decisions and their consequences.
    """
    __tablename__ = "chapter_choices"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id"), nullable=False)
    play_session_id = Column(String(36), ForeignKey("play_sessions.id"), nullable=True)
    
    # Choice description
    choice_description = Column(Text, nullable=False)
    choice_context = Column(JSON, default=dict)  # Situation when choice was made
    
    # Choice details
    options_presented = Column(JSON, default=list)  # What options were available
    choice_made = Column(JSON, default=dict)  # What the players chose
    players_involved = Column(JSON, default=list)  # Which players made the choice
    
    # Consequences
    immediate_consequences = Column(JSON, default=dict)
    long_term_consequences = Column(JSON, default=dict)
    narrative_impact = Column(Text)
    
    # Branching
    resulted_in_branch = Column(String(100), nullable=True)
    alternative_branches = Column(JSON, default=list)  # Other possible outcomes
    
    # Timing
    choice_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="choices")
    chapter_version = relationship("ChapterVersion", back_populates="choices")
    play_session = relationship("PlaySession", back_populates="choices")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter choice to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "chapter_version_id": self.chapter_version_id,
            "play_session_id": self.play_session_id,
            "choice_description": self.choice_description,
            "choice_context": self.choice_context,
            "options_presented": self.options_presented,
            "choice_made": self.choice_made,
            "players_involved": self.players_involved,
            "immediate_consequences": self.immediate_consequences,
            "long_term_consequences": self.long_term_consequences,
            "narrative_impact": self.narrative_impact,
            "resulted_in_branch": self.resulted_in_branch,
            "alternative_branches": self.alternative_branches,
            "choice_timestamp": self.choice_timestamp.isoformat() if self.choice_timestamp else None
        }

class PlaySession(Base):
    """
    Actual play sessions where chapters are experienced.
    
    Tracks when and how chapters were played.
    """
    __tablename__ = "play_sessions"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Session identification
    session_number = Column(Integer, nullable=False)
    session_title = Column(String(200))
    session_date = Column(DateTime, nullable=False)
    
    # Session details
    chapters_played = Column(JSON, default=list)  # List of chapter hashes played
    duration_minutes = Column(Integer)
    players_present = Column(JSON, default=list)
    dm_name = Column(String(100))
    
    # Session outcomes
    major_events = Column(JSON, default=list)
    player_decisions = Column(JSON, default=dict)
    story_progression = Column(Text)
    
    # Session notes
    dm_notes = Column(Text)
    player_feedback = Column(JSON, default=dict)
    
    # Session status
    status = Column(String(20), default=PlaySessionStatusEnum.SCHEDULED.value)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="play_sessions")
    chapter_versions = relationship("ChapterVersion", back_populates="play_session")
    choices = relationship("ChapterChoice", back_populates="play_session")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert play session to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "session_number": self.session_number,
            "session_title": self.session_title,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "chapters_played": self.chapters_played,
            "duration_minutes": self.duration_minutes,
            "players_present": self.players_present,
            "dm_name": self.dm_name,
            "major_events": self.major_events,
            "player_decisions": self.player_decisions,
            "story_progression": self.story_progression,
            "dm_notes": self.dm_notes,
            "player_feedback": self.player_feedback,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

class ChapterMerge(Base):
    """
    Records of branch merges (combining storylines).
    
    Tracks when and how different story branches were combined.
    """
    __tablename__ = "chapter_merges"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Merge details
    source_branch = Column(String(100), nullable=False)
    target_branch = Column(String(100), nullable=False)
    merge_commit_hash = Column(String(12), nullable=False)
    
    # Merge metadata
    merge_strategy = Column(String(50))  # "manual", "auto", "cherry-pick"
    merge_message = Column(Text)
    conflicts_resolved = Column(JSON, default=list)
    
    # Merge author
    merged_by = Column(String(100), nullable=False)
    merge_timestamp = Column(DateTime, default=datetime.utcnow)
    
    # Merge notes
    merge_notes = Column(Text)
    
    # Relationships
    campaign = relationship("Campaign", back_populates="merges")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert chapter merge to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "source_branch": self.source_branch,
            "target_branch": self.target_branch,
            "merge_commit_hash": self.merge_commit_hash,
            "merge_strategy": self.merge_strategy,
            "merge_message": self.merge_message,
            "conflicts_resolved": self.conflicts_resolved,
            "merged_by": self.merged_by,
            "merge_timestamp": self.merge_timestamp.isoformat() if self.merge_timestamp else None,
            "merge_notes": self.merge_notes
        }

# ============================================================================
# DATABASE ACCESS LAYER FOR CAMPAIGNS
# ============================================================================

class CampaignDB:
    """
    Database access layer for campaign, chapter, and plot fork operations.
    """
    
    # ----------- CAMPAIGN CRUD -----------
    @staticmethod
    def create_campaign(db: Session, campaign_data: Dict[str, Any]) -> Campaign:
        """Create a new campaign."""
        db_campaign = Campaign(
            id=campaign_data.get("id", str(uuid.uuid4())),
            title=campaign_data["title"],
            description=campaign_data.get("description"),
            themes=campaign_data.get("themes", []),
            gm_notes=campaign_data.get("gm_notes"),
            status=campaign_data.get("status", CampaignStatusEnum.DRAFT.value),
            current_branch=campaign_data.get("current_branch", "main"),
            total_chapters=campaign_data.get("total_chapters", 0),
            total_branches=campaign_data.get("total_branches", 1),
        )
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def get_campaign(db: Session, campaign_id: str) -> Optional[Campaign]:
        """Get a campaign by ID."""
        return db.query(Campaign).filter(Campaign.id == campaign_id).first()

    @staticmethod
    def update_campaign(db: Session, campaign_id: str, updates: Dict[str, Any]) -> Optional[Campaign]:
        """Update a campaign."""
        db_campaign = CampaignDB.get_campaign(db, campaign_id)
        if not db_campaign:
            return None
        for key, value in updates.items():
            if hasattr(db_campaign, key):
                setattr(db_campaign, key, value)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def delete_campaign(db: Session, campaign_id: str) -> bool:
        """Delete a campaign."""
        db_campaign = CampaignDB.get_campaign(db, campaign_id)
        if not db_campaign:
            return False
        db.delete(db_campaign)
        db.commit()
        return True

    @staticmethod
    def list_campaigns(db: Session, limit: int = 100, offset: int = 0) -> List[Campaign]:
        """List campaigns with pagination."""
        return db.query(Campaign).offset(offset).limit(limit).all()

    # ----------- TRADITIONAL CHAPTER CRUD -----------
    @staticmethod
    def create_chapter(db: Session, chapter_data: Dict[str, Any]) -> Chapter:
        """Create a traditional chapter."""
        db_chapter = Chapter(
            id=chapter_data.get("id", str(uuid.uuid4())),
            campaign_id=chapter_data["campaign_id"],
            title=chapter_data["title"],
            summary=chapter_data.get("summary"),
            content=chapter_data.get("content"),
            status=chapter_data.get("status", ChapterStatusEnum.DRAFT.value),
        )
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter

    @staticmethod
    def get_chapter(db: Session, chapter_id: str) -> Optional[Chapter]:
        """Get a traditional chapter by ID."""
        return db.query(Chapter).filter(Chapter.id == chapter_id).first()

    @staticmethod
    def update_chapter(db: Session, chapter_id: str, updates: Dict[str, Any]) -> Optional[Chapter]:
        """Update a traditional chapter."""
        db_chapter = CampaignDB.get_chapter(db, chapter_id)
        if not db_chapter:
            return None
        for key, value in updates.items():
            if hasattr(db_chapter, key):
                setattr(db_chapter, key, value)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter

    @staticmethod
    def delete_chapter(db: Session, chapter_id: str) -> bool:
        """Delete a traditional chapter."""
        db_chapter = CampaignDB.get_chapter(db, chapter_id)
        if not db_chapter:
            return False
        db.delete(db_chapter)
        db.commit()
        return True

    @staticmethod
    def list_chapters(db: Session, campaign_id: str) -> List[Chapter]:
        """List traditional chapters for a campaign."""
        return db.query(Chapter).filter(Chapter.campaign_id == campaign_id).all()

    # ----------- PLOT FORK CRUD -----------
    @staticmethod
    def create_plot_fork(db: Session, fork_data: Dict[str, Any]) -> PlotFork:
        """Create a plot fork."""
        db_fork = PlotFork(
            id=fork_data.get("id", str(uuid.uuid4())),
            campaign_id=fork_data["campaign_id"],
            chapter_id=fork_data["chapter_id"],
            fork_type=fork_data["fork_type"],
            description=fork_data.get("description"),
            options=fork_data.get("options", []),
        )
        db.add(db_fork)
        db.commit()
        db.refresh(db_fork)
        return db_fork

    @staticmethod
    def get_plot_fork(db: Session, fork_id: str) -> Optional[PlotFork]:
        """Get a plot fork by ID."""
        return db.query(PlotFork).filter(PlotFork.id == fork_id).first()

    @staticmethod
    def list_plot_forks(db: Session, campaign_id: str) -> List[PlotFork]:
        """List plot forks for a campaign."""
        return db.query(PlotFork).filter(PlotFork.campaign_id == campaign_id).all()

    @staticmethod
    def delete_plot_fork(db: Session, fork_id: str) -> bool:
        """Delete a plot fork."""
        db_fork = CampaignDB.get_plot_fork(db, fork_id)
        if not db_fork:
            return False
        db.delete(db_fork)
        db.commit()
        return True

# ============================================================================
# DATABASE ACCESS LAYER FOR GIT-LIKE OPERATIONS
# ============================================================================

class ChapterVersionDB:
    """Database operations for git-like chapter versioning."""
    
    @staticmethod
    def create_chapter_version(db: Session, version_data: Dict[str, Any]) -> ChapterVersion:
        """Create a new chapter version (git commit)."""
        chapter_version = ChapterVersion(
            campaign_id=version_data["campaign_id"],
            version_hash=version_data["version_hash"],
            parent_hashes=version_data.get("parent_hashes", []),
            branch_name=version_data.get("branch_name", "main"),
            version_type=version_data.get("version_type", ChapterVersionTypeEnum.DRAFT.value),
            title=version_data["title"],
            summary=version_data.get("summary"),
            content=version_data.get("content", {}),
            chapter_order=version_data.get("chapter_order", 0),
            commit_message=version_data.get("commit_message", ""),
            author=version_data.get("author", "system"),
            player_choices=version_data.get("player_choices", {}),
            dm_notes=version_data.get("dm_notes"),
            play_session_id=version_data.get("play_session_id")
        )
        
        db.add(chapter_version)
        db.commit()
        db.refresh(chapter_version)
        return chapter_version
    
    @staticmethod
    def get_chapter_by_hash(db: Session, version_hash: str) -> Optional[ChapterVersion]:
        """Get chapter by version hash."""
        return db.query(ChapterVersion).filter(
            ChapterVersion.version_hash == version_hash
        ).first()
    
    @staticmethod
    def get_branch_head(db: Session, campaign_id: str, branch_name: str) -> Optional[ChapterVersion]:
        """Get the head (latest) chapter in a branch."""
        return db.query(ChapterVersion).filter(
            ChapterVersion.campaign_id == campaign_id,
            ChapterVersion.branch_name == branch_name,
            ChapterVersion.is_head == True
        ).first()
    
    @staticmethod
    def get_campaign_branches(db: Session, campaign_id: str) -> List[CampaignBranch]:
        """Get all branches for a campaign."""
        return db.query(CampaignBranch).filter(
            CampaignBranch.campaign_id == campaign_id,
            CampaignBranch.is_active == True
        ).all()
    
    @staticmethod
    def create_branch(db: Session, branch_data: Dict[str, Any]) -> CampaignBranch:
        """Create a new story branch."""
        branch = CampaignBranch(
            campaign_id=branch_data["campaign_id"],
            name=branch_data["name"],
            branch_type=branch_data.get("branch_type", BranchTypeEnum.ALTERNATE.value),
            description=branch_data.get("description", ""),
            head_commit=branch_data["head_commit"],
            parent_branch=branch_data.get("parent_branch"),
            created_by=branch_data.get("created_by", "system")
        )
        
        db.add(branch)
        db.commit()
        db.refresh(branch)
        return branch
    
    @staticmethod
    def record_player_choice(db: Session, choice_data: Dict[str, Any]) -> ChapterChoice:
        """Record a player choice."""
        choice = ChapterChoice(
            campaign_id=choice_data["campaign_id"],
            chapter_version_id=choice_data["chapter_version_id"],
            choice_description=choice_data["choice_description"],
            choice_context=choice_data.get("choice_context", {}),
            options_presented=choice_data.get("options_presented", []),
            choice_made=choice_data.get("choice_made", {}),
            players_involved=choice_data.get("players_involved", []),
            immediate_consequences=choice_data.get("immediate_consequences", {}),
            resulted_in_branch=choice_data.get("resulted_in_branch"),
            play_session_id=choice_data.get("play_session_id")
        )
        
        db.add(choice)
        db.commit()
        db.refresh(choice)
        return choice
    
    @staticmethod
    def create_play_session(db: Session, session_data: Dict[str, Any]) -> PlaySession:
        """Create a new play session."""
        session = PlaySession(
            campaign_id=session_data["campaign_id"],
            session_number=session_data["session_number"],
            session_title=session_data.get("session_title"),
            session_date=session_data["session_date"],
            chapters_played=session_data.get("chapters_played", []),
            duration_minutes=session_data.get("duration_minutes"),
            players_present=session_data.get("players_present", []),
            dm_name=session_data.get("dm_name"),
            major_events=session_data.get("major_events", []),
            player_decisions=session_data.get("player_decisions", {}),
            story_progression=session_data.get("story_progression"),
            dm_notes=session_data.get("dm_notes"),
            player_feedback=session_data.get("player_feedback", {}),
            status=session_data.get("status", PlaySessionStatusEnum.SCHEDULED.value)
        )
        
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def create_chapter_merge(db: Session, merge_data: Dict[str, Any]) -> ChapterMerge:
        """Record a branch merge."""
        merge = ChapterMerge(
            campaign_id=merge_data["campaign_id"],
            source_branch=merge_data["source_branch"],
            target_branch=merge_data["target_branch"],
            merge_commit_hash=merge_data["merge_commit_hash"],
            merge_strategy=merge_data.get("merge_strategy", "manual"),
            merge_message=merge_data.get("merge_message"),
            conflicts_resolved=merge_data.get("conflicts_resolved", []),
            merged_by=merge_data["merged_by"],
            merge_notes=merge_data.get("merge_notes")
        )
        
        db.add(merge)
        db.commit()
        db.refresh(merge)
        return merge

# ============================================================================
# DATABASE CONNECTION SETUP
# ============================================================================

# Database connection setup (to be configured in main app)
engine = None
SessionLocal = None

def init_database(database_url: str):
    """Initialize database connection."""
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    # Core models
    'Campaign',
    'Chapter', 
    'PlotFork',
    # Git-like versioning models
    'ChapterVersion',
    'CampaignBranch',
    'ChapterChoice',
    'PlaySession',
    'ChapterMerge',
    # Enums
    'CampaignStatusEnum',
    'ChapterStatusEnum', 
    'PlotForkTypeEnum',
    'ChapterVersionTypeEnum',
    'BranchTypeEnum',
    'PlaySessionStatusEnum',
    # Database access layers
    'CampaignDB',
    'ChapterVersionDB',
    # Database setup
    'Base',
    'init_database',
    'get_db'
]
