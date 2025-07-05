"""
Enhanced Database Models for Git-Like Chapter Versioning

Extends the existing database models to support git-like version control
for campaign chapters with branching, commits, and visual graph structure.
"""

import uuid
import enum
from datetime import datetime
from typing import List, Dict, Any

from sqlalchemy import Column, String, Text, DateTime, ForeignKey, JSON, Boolean, Integer
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

# Import base from existing models
# from src.models.database_models import Base

# For now, create a separate base for the new models
Base = declarative_base()

# ============================================================================
# ENHANCED CHAPTER VERSION ENUMS
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
# ENHANCED CHAPTER MODEL WITH GIT-LIKE VERSIONING
# ============================================================================

class ChapterVersion(Base):
    """
    Enhanced Chapter model with git-like versioning capabilities.
    
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

# ============================================================================
# ENHANCED CAMPAIGN MODEL RELATIONSHIPS
# ============================================================================

# Note: These would be added to the existing Campaign model

"""
# Additional relationships to add to existing Campaign model:

class Campaign(Base):
    # ... existing fields ...
    
    # New git-like relationships
    chapter_versions = relationship("ChapterVersion", back_populates="campaign", cascade="all, delete-orphan")
    branches = relationship("CampaignBranch", back_populates="campaign", cascade="all, delete-orphan")
    choices = relationship("ChapterChoice", back_populates="campaign", cascade="all, delete-orphan")
    play_sessions = relationship("PlaySession", back_populates="campaign", cascade="all, delete-orphan")
    merges = relationship("ChapterMerge", back_populates="campaign", cascade="all, delete-orphan")
    
    # Git-like metadata
    current_branch = Column(String(100), default="main")
    total_chapters = Column(Integer, default=0)
    total_branches = Column(Integer, default=1)
    last_played_session = Column(String(36), nullable=True)
"""

# ============================================================================
# DATABASE ACCESS LAYER FOR GIT-LIKE OPERATIONS
# ============================================================================

class ChapterVersionDB:
    """Database operations for git-like chapter versioning."""
    
    @staticmethod
    def create_chapter_version(db, version_data: Dict[str, Any]) -> ChapterVersion:
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
    def get_chapter_by_hash(db, version_hash: str) -> ChapterVersion:
        """Get chapter by version hash."""
        return db.query(ChapterVersion).filter(
            ChapterVersion.version_hash == version_hash
        ).first()
    
    @staticmethod
    def get_branch_head(db, campaign_id: str, branch_name: str) -> ChapterVersion:
        """Get the head (latest) chapter in a branch."""
        return db.query(ChapterVersion).filter(
            ChapterVersion.campaign_id == campaign_id,
            ChapterVersion.branch_name == branch_name,
            ChapterVersion.is_head == True
        ).first()
    
    @staticmethod
    def get_campaign_branches(db, campaign_id: str) -> List[CampaignBranch]:
        """Get all branches for a campaign."""
        return db.query(CampaignBranch).filter(
            CampaignBranch.campaign_id == campaign_id,
            CampaignBranch.is_active == True
        ).all()
    
    @staticmethod
    def create_branch(db, branch_data: Dict[str, Any]) -> CampaignBranch:
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
    def record_player_choice(db, choice_data: Dict[str, Any]) -> ChapterChoice:
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

# ============================================================================
# EXPORTS
# ============================================================================

__all__ = [
    'ChapterVersionTypeEnum',
    'BranchTypeEnum',
    'PlaySessionStatusEnum',
    'ChapterVersion',
    'CampaignBranch', 
    'ChapterChoice',
    'PlaySession',
    'ChapterMerge',
    'ChapterVersionDB'
]
