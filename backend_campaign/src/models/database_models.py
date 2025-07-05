# =========================
# CAMPAIGN DATABASE ACCESS LAYER
# =========================

import uuid
import enum
import logging
import hashlib
from typing import TYPE_CHECKING, Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

if TYPE_CHECKING:
    from .database_models import Campaign, Chapter, PlotFork

class CampaignDB:
    """
    Database access layer for campaign, chapter, and plot fork operations.
    """
    # ----------- CAMPAIGN CRUD -----------
    @staticmethod
    def create_campaign(db: Session, campaign_data: Dict[str, Any]):
        # Import here to avoid circular imports
        from . import database_models as dm
        db_campaign = dm.Campaign(
            id=campaign_data.get("id", str(uuid.uuid4())),
            title=campaign_data["title"],
            description=campaign_data.get("description"),
            themes=campaign_data.get("themes", []),
            gm_notes=campaign_data.get("gm_notes"),
            status=campaign_data.get("status", dm.CampaignStatusEnum.DRAFT.value),
        )
        db.add(db_campaign)
        db.commit()
        db.refresh(db_campaign)
        return db_campaign

    @staticmethod
    def get_campaign(db: Session, campaign_id: str):
        from . import database_models as dm
        return db.query(dm.Campaign).filter(dm.Campaign.id == campaign_id).first()

    @staticmethod
    def update_campaign(db: Session, campaign_id: str, updates: Dict[str, Any]):
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
        db_campaign = CampaignDB.get_campaign(db, campaign_id)
        if not db_campaign:
            return False
        db.delete(db_campaign)
        db.commit()
        return True

    @staticmethod
    def list_campaigns(db: Session, limit: int = 100, offset: int = 0):
        from . import database_models as dm
        return db.query(dm.Campaign).offset(offset).limit(limit).all()

    # ----------- CHAPTER CRUD -----------
    @staticmethod
    def create_chapter(db: Session, chapter_data: Dict[str, Any]):
        from . import database_models as dm
        db_chapter = dm.Chapter(
            id=chapter_data.get("id", str(uuid.uuid4())),
            campaign_id=chapter_data["campaign_id"],
            title=chapter_data["title"],
            summary=chapter_data.get("summary"),
            content=chapter_data.get("content"),
            status=chapter_data.get("status", dm.ChapterStatusEnum.DRAFT.value),
        )
        db.add(db_chapter)
        db.commit()
        db.refresh(db_chapter)
        return db_chapter

    @staticmethod
    def get_chapter(db: Session, chapter_id: str):
        from . import database_models as dm
        return db.query(dm.Chapter).filter(dm.Chapter.id == chapter_id).first()

    @staticmethod
    def update_chapter(db: Session, chapter_id: str, updates: Dict[str, Any]):
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
        db_chapter = CampaignDB.get_chapter(db, chapter_id)
        if not db_chapter:
            return False
        db.delete(db_chapter)
        db.commit()
        return True

    @staticmethod
    def list_chapters(db: Session, campaign_id: str):
        from . import database_models as dm
        return db.query(dm.Chapter).filter(dm.Chapter.campaign_id == campaign_id).all()

    # ----------- PLOT FORK CRUD -----------
    @staticmethod
    def create_plot_fork(db: Session, fork_data: Dict[str, Any]):
        from . import database_models as dm
        db_fork = dm.PlotFork(
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
    def get_plot_fork(db: Session, fork_id: str):
        from . import database_models as dm
        return db.query(dm.PlotFork).filter(dm.PlotFork.id == fork_id).first()

    @staticmethod
    def list_plot_forks(db: Session, campaign_id: str):
        from . import database_models as dm
        return db.query(dm.PlotFork).filter(dm.PlotFork.campaign_id == campaign_id).all()

    @staticmethod
    def delete_plot_fork(db: Session, fork_id: str) -> bool:
        db_fork = CampaignDB.get_plot_fork(db, fork_id)
        if not db_fork:
            return False
        db.delete(db_fork)
        db.commit()
        return True

"""
Database models for the D&D Character Creator with Git-like versioning system.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import uuid
import logging
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.types import TypeDecorator, CHAR
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker
from sqlalchemy.orm.attributes import flag_modified

# Configure logging
logger = logging.getLogger(__name__)


# Custom UUID type that works with SQLite
class GUID(TypeDecorator):
    """Platform-independent GUID type.
    Uses PostgreSQL's UUID type, otherwise uses CHAR(32) storing as stringified hex values.
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
# CHARACTER VERSIONING SYSTEM (Git-like Branching)
# ============================================================================

class CharacterRepository(Base):
    """
    Represents a character's complete version history - like a Git repository.
    This is the root container for all versions/branches of a single character concept.
    """
    __tablename__ = "character_repositories"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), unique=True, index=True, default=lambda: str(uuid.uuid4()))
    
    # Repository metadata
    name = Column(String(100), nullable=False, index=True)  # "Gandalf the Grey"
    description = Column(Text, nullable=True)  # "A wise wizard character with multiple storylines"
    player_name = Column(String(100), nullable=True)
    
    # Repository settings
    is_public = Column(Boolean, default=False)  # Can others see/fork this character?
    allow_forks = Column(Boolean, default=True)  # Can others create branches?
    
    # Initial character data (the "genesis" commit)
    initial_commit_hash = Column(String(64), nullable=True)  # Points to first CharacterCommit
    default_branch = Column(String(50), default="main")  # Default branch name
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    branches = relationship("CharacterBranch", back_populates="repository", cascade="all, delete-orphan")
    commits = relationship("CharacterCommit", back_populates="repository", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "name": self.name,
            "description": self.description,
            "player_name": self.player_name,
            "is_public": self.is_public,
            "allow_forks": self.allow_forks,
            "initial_commit_hash": self.initial_commit_hash,
            "default_branch": self.default_branch,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "branch_count": len(self.branches) if self.branches else 0,
            "commit_count": len(self.commits) if self.commits else 0
        }


class CharacterBranch(Base):
    """
    Represents a branch of character development - like Git branches.
    Examples: "main", "multiclass-wizard", "evil-alternate", "level-20-path"
    """
    __tablename__ = "character_branches"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    
    # Branch metadata
    branch_name = Column(String(50), nullable=False, index=True)  # "main", "multiclass-path", etc.
    description = Column(Text, nullable=True)  # "Path where character becomes a wizard/fighter"
    branch_type = Column(String(20), default="development")  # "main", "development", "experimental", "alternate"
    
    # Branch pointers
    head_commit_hash = Column(String(64), nullable=True)  # Current HEAD of this branch
    parent_branch = Column(String(50), nullable=True)  # Branch this was created from
    branch_point_hash = Column(String(64), nullable=True)  # Commit where this branch started
    
    # Branch status
    is_active = Column(Boolean, default=True)
    is_merged = Column(Boolean, default=False)  # Has this branch been merged back?
    merged_into = Column(String(50), nullable=True)  # Which branch was this merged into?
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    repository = relationship("CharacterRepository", back_populates="branches")
    commits = relationship("CharacterCommit", back_populates="branch", cascade="all, delete-orphan")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "branch_name": self.branch_name,
            "description": self.description,
            "branch_type": self.branch_type,
            "head_commit_hash": self.head_commit_hash,
            "parent_branch": self.parent_branch,
            "branch_point_hash": self.branch_point_hash,
            "is_active": self.is_active,
            "is_merged": self.is_merged,
            "merged_into": self.merged_into,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "commit_count": len(self.commits) if self.commits else 0
        }


class CharacterCommit(Base):
    """
    Represents a single character state/version - like Git commits.
    Each level-up, major change, or story development creates a new commit.
    """
    __tablename__ = "character_commits"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    branch_id = Column(String(36), ForeignKey("character_branches.id"), nullable=False)
    
    # Commit identification
    commit_hash = Column(String(64), unique=True, nullable=False, index=True)  # SHA-256 hash
    short_hash = Column(String(8), nullable=False, index=True)  # First 8 chars for display
    
    # Commit metadata
    commit_message = Column(Text, nullable=False)  # "Level 2: Gained Action Surge"
    commit_type = Column(String(20), default="update")  # "initial", "level_up", "story", "equipment", "death", "resurrection"
    
    # Character level/progression info
    character_level = Column(Integer, nullable=False)
    experience_points = Column(Integer, default=0)
    milestone_name = Column(String(100), nullable=True)  # "Defeated the Dragon", "Learned Fireball"
    
    # Git-like relationship tracking
    parent_commit_hash = Column(String(64), nullable=True)  # Previous commit (null for initial)
    merge_parent_hash = Column(String(64), nullable=True)  # If this is a merge commit
    
    # Character data snapshot (complete character state at this point)
    character_data = Column(JSON, nullable=False)  # Full CharacterCore + CharacterState data
    
    # Change tracking
    changes_summary = Column(JSON, nullable=True)  # What changed from parent commit
    files_changed = Column(JSON, nullable=True)  # Which aspects changed (abilities, equipment, etc.)
    
    # Story/campaign context
    session_date = Column(DateTime, nullable=True)  # When this change happened in real life
    campaign_context = Column(Text, nullable=True)  # What was happening in the story
    dm_notes = Column(Text, nullable=True)  # DM notes about this character state
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)  # Who made this commit (player, DM, auto)
    
    # Relationships
    repository = relationship("CharacterRepository", back_populates="commits")
    branch = relationship("CharacterBranch", back_populates="commits")
    
    def generate_commit_hash(self) -> str:
        """Generate a unique commit hash based on character data and metadata."""
        # Create hash from character data, timestamp, and parent commit
        hash_input = f"{self.character_data}{self.commit_message}{self.created_at}{self.parent_commit_hash}"
        return hashlib.sha256(hash_input.encode()).hexdigest()
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "branch_id": self.branch_id,
            "commit_hash": self.commit_hash,
            "short_hash": self.short_hash,
            "commit_message": self.commit_message,
            "commit_type": self.commit_type,
            "character_level": self.character_level,
            "experience_points": self.experience_points,
            "milestone_name": self.milestone_name,
            "parent_commit_hash": self.parent_commit_hash,
            "merge_parent_hash": self.merge_parent_hash,
            "character_data": self.character_data,
            "changes_summary": self.changes_summary,
            "files_changed": self.files_changed,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "campaign_context": self.campaign_context,
            "dm_notes": self.dm_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }


class CharacterTag(Base):
    """
    Tags for marking important commits - like Git tags.
    Examples: "v1.0-creation", "v2.0-multiclass", "v20.0-epic", "death", "resurrection"
    """
    __tablename__ = "character_tags"
    
    id = Column(String(36), primary_key=True, index=True)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=False)
    
    # Tag information
    tag_name = Column(String(50), nullable=False, index=True)  # "v1.0", "death-by-dragon", "epic-level"
    tag_type = Column(String(20), default="milestone")  # "milestone", "death", "resurrection", "retirement"
    description = Column(Text, nullable=True)
    
    # Points to specific commit
    commit_hash = Column(String(64), nullable=False)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    created_by = Column(String(100), nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "tag_name": self.tag_name,
            "tag_type": self.tag_type,
            "description": self.description,
            "commit_hash": self.commit_hash,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "created_by": self.created_by
        }


# ============================================================================
# LEGACY CHARACTER MODEL (for backwards compatibility)
# ============================================================================

class Character(Base):
    """
    Database model for D&D characters with UUID support.
    Uses UUIDs for better scalability and security.
    Also supports the CharacterRepository versioning system.
    """
    __tablename__ = "characters"
    
    id = Column(String(36), primary_key=True, index=True)
    
    # Link to new versioning system (optional)
    repository_id = Column(String(36), ForeignKey("character_repositories.id"), nullable=True)
    commit_hash = Column(String(64), nullable=True)  # Which commit this represents
    
    # Original character fields
    name = Column(String(100), nullable=False, index=True)
    player_name = Column(String(100), nullable=True)
    
    # Character basics
    species = Column(String(50), nullable=False)
    background = Column(String(50), nullable=True)
    alignment = Column(String(20), nullable=True)
    level = Column(Integer, default=1)
    
    # Character classes (stored as JSON)
    character_classes = Column(JSON, nullable=False, default=dict)
    
    # Ability scores
    strength = Column(Integer, default=10)
    dexterity = Column(Integer, default=10)
    constitution = Column(Integer, default=10)
    intelligence = Column(Integer, default=10)
    wisdom = Column(Integer, default=10)
    charisma = Column(Integer, default=10)
    
    # Derived stats
    armor_class = Column(Integer, default=10)
    hit_points = Column(Integer, default=1)
    proficiency_bonus = Column(Integer, default=2)
    
    # Character data (stored as JSON for flexibility)
    equipment = Column(JSON, nullable=True, default=dict)
    features = Column(JSON, nullable=True, default=dict)
    spells = Column(JSON, nullable=True, default=dict)
    skills = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Additional character data
    backstory = Column(Text, nullable=True)
    notes = Column(Text, nullable=True)
    
    # Approval state: 'pending', 'approved', 'rejected'
    approval_state = Column(String(20), default='pending', nullable=False)
    approval_notes = Column(Text, nullable=True)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "player_name": self.player_name,
            "species": self.species,
            "background": self.background,
            "alignment": self.alignment,
            "level": self.level,
            "character_classes": self.character_classes,
            "abilities": {
                "strength": self.strength,
                "dexterity": self.dexterity,
                "constitution": self.constitution,
                "intelligence": self.intelligence,
                "wisdom": self.wisdom,
                "charisma": self.charisma
            },
            "armor_class": self.armor_class,
            "hit_points": self.hit_points,
            "proficiency_bonus": self.proficiency_bonus,
            "equipment": self.equipment,
            "features": self.features,
            "spells": self.spells,
            "skills": self.skills,
            "backstory": self.backstory,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }
    
    # Relationships
    item_access = relationship("CharacterItemAccess", back_populates="character", cascade="all, delete-orphan")


class CharacterSession(Base):
    """Database model for character creation sessions."""
    __tablename__ = "character_sessions"
    
    id = Column(String(36), primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID
    character_id = Column(String(36), nullable=True)  # Links to Character if saved
    
    # Session data
    current_step = Column(String(50), default="basic_info")
    session_data = Column(JSON, nullable=True, default=dict)
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    expires_at = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)


class CustomContent(Base):
    """Database model for user-created custom content."""
    __tablename__ = "custom_content"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    content_type = Column(String(50), nullable=False)  # "species", "class", "spell", etc.
    
    # Content data
    content_data = Column(JSON, nullable=False)
    description = Column(Text, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # Future: user system
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)

def register_custom_item(db: Session, name: str, item_type: str, description: str = "", properties: Optional[Dict[str, Any]] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom item in the CustomContent table.
    """
    item_data = {
        "name": name,
        "item_type": item_type,
        "description": description,
        "properties": properties or {},
    }
    db_item = CustomContent(
        name=name,
        content_type=item_type,
        content_data=item_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item


# ============================================================================
# UNIFIED ITEM CATALOG SYSTEM - ALL ITEMS GET UUIDS
# ============================================================================

class UnifiedItem(Base):
    """
    Unified table for ALL items (spells, weapons, armor, equipment) - both traditional and custom.
    Every item gets a UUID for consistent tracking and relationships.
    """
    __tablename__ = "unified_items"
    
    # Primary identification
    id = Column(GUID(), primary_key=True, default=uuid.uuid4, index=True)
    name = Column(String(100), nullable=False, index=True)
    item_type = Column(String(50), nullable=False, index=True)  # 'spell', 'weapon', 'armor', 'item', 'tool', 'consumable'
    item_subtype = Column(String(50), nullable=True, index=True)  # 'simple_weapon', 'martial_weapon', 'light_armor', etc.
    source_type = Column(String(20), nullable=False, index=True)  # 'official', 'custom', or 'llm_generated'
    source_info = Column(String(500), nullable=True)  # Extra provenance or LLM prompt info
    llm_metadata = Column(JSON, nullable=True)  # LLM-specific metadata (model, prompt, etc.)
    
    # Content and properties
    content_data = Column(JSON, nullable=False)  # All item properties, stats, descriptions
    short_description = Column(String(500), nullable=True)  # Brief description for catalog views
    
    # D&D 5e specific metadata
    rarity = Column(String(20), nullable=True, index=True)  # 'common', 'uncommon', 'rare', 'very_rare', 'legendary', 'artifact'
    requires_attunement = Column(Boolean, default=False)
    spell_level = Column(Integer, nullable=True, index=True)  # For spells: 0 for cantrips, 1-9 for leveled spells
    spell_school = Column(String(30), nullable=True, index=True)  # For spells: 'evocation', 'conjuration', etc.
    class_restrictions = Column(JSON, nullable=True)  # Array of classes that can use this item ['wizard', 'sorcerer']
    
    # Economics and practical data
    value_gp = Column(Integer, nullable=True)  # Value in gold pieces
    weight_lbs = Column(String(10), nullable=True)  # Weight (can be fractional like "0.5")
    
    # Metadata and versioning
    created_by = Column(String(100), nullable=True)  # Creator (for custom items)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=True)  # Most official items are public
    version = Column(Integer, default=1)  # For tracking updates to items
    
    # Source attribution
    source_book = Column(String(100), nullable=True)  # 'Player\'s Handbook 2024', 'Custom Creation', etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "name": self.name,
            "item_type": self.item_type,
            "item_subtype": self.item_subtype,
            "source_type": self.source_type,
            "source_info": self.source_info,
            "llm_metadata": self.llm_metadata,
            "content_data": self.content_data,
            "short_description": self.short_description,
            "rarity": self.rarity,
            "requires_attunement": self.requires_attunement,
            "spell_level": self.spell_level,
            "spell_school": self.spell_school,
            "class_restrictions": self.class_restrictions,
            "value_gp": self.value_gp,
            "weight_lbs": self.weight_lbs,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public,
            "version": self.version,
            "source_book": self.source_book
        }


class CharacterItemAccess(Base):
    """
    Junction table tracking which items a character has access to (spells known, equipment owned, etc.).
    This replaces the old system of storing item lists directly in character data.
    """
    __tablename__ = "character_item_access"
    
    # Composite primary key
    id = Column(GUID(), primary_key=True, default=uuid.uuid4)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    item_id = Column(GUID(), ForeignKey("unified_items.id"), nullable=False, index=True)
    
    # Access type and status
    access_type = Column(String(30), nullable=False, index=True)  # 'spells_known', 'spells_prepared', 'inventory', 'equipped'
    access_subtype = Column(String(30), nullable=True)  # 'main_hand', 'off_hand', 'armor', 'attuned', etc.
    quantity = Column(Integer, default=1)  # For stackable items
    
    # Acquisition and management
    acquired_at = Column(DateTime, default=datetime.utcnow)
    acquired_method = Column(String(50), nullable=True)  # 'character_creation', 'level_up', 'purchase', 'loot', 'craft'
    is_active = Column(Boolean, default=True)  # Can be deactivated without deletion
    
    # Character-specific customization
    custom_properties = Column(JSON, nullable=True)  # Character-specific modifications to the item
    notes = Column(Text, nullable=True)  # Player notes about this specific item instance
    
    # Relationships
    character = relationship("Character", back_populates="item_access")
    item = relationship("UnifiedItem")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for API responses."""
        return {
            "id": str(self.id),
            "character_id": str(self.character_id),
            "item_id": str(self.item_id),
            "access_type": self.access_type,
            "access_subtype": self.access_subtype,
            "quantity": self.quantity,
            "acquired_at": self.acquired_at.isoformat() if self.acquired_at else None,
            "acquired_method": self.acquired_method,
            "is_active": self.is_active,
            "custom_properties": self.custom_properties,
            "notes": self.notes,
            "item": self.item.to_dict() if self.item else None
        }

def register_custom_npc(db: Session, name: str, npc_type: str, description: str = "", stats: Optional[Dict[str, Any]] = None, challenge_rating: Optional[float] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom NPC in the CustomContent table, with CR support.
    """
    if stats is None:
        stats = {}
    if challenge_rating is not None:
        stats["challenge_rating"] = challenge_rating
    npc_data = {
        "name": name,
        "npc_type": npc_type,
        "description": description,
        "stats": stats,
        "challenge_rating": challenge_rating,
    }
    db_npc = CustomContent(
        name=name,
        content_type="npc",
        content_data=npc_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_npc)
    db.commit()
    db.refresh(db_npc)
    return db_npc

def register_custom_creature(db: Session, name: str, creature_type: str, description: str = "", stat_block: Optional[Dict[str, Any]] = None, challenge_rating: Optional[float] = None, created_by: str = "dungeon_master", is_public: bool = False) -> CustomContent:
    """
    Register a custom creature in the CustomContent table, with CR support.
    """
    if stat_block is None:
        stat_block = {}
    if challenge_rating is not None:
        stat_block["challenge_rating"] = challenge_rating
    creature_data = {
        "name": name,
        "creature_type": creature_type,
        "description": description,
        "stat_block": stat_block,
        "challenge_rating": stat_block.get("challenge_rating"),
    }
    db_creature = CustomContent(
        name=name,
        content_type="creature",
        content_data=creature_data,
        description=description,
        created_by=created_by,
        is_public=is_public,
    )
    db.add(db_creature)
    db.commit()
    db.refresh(db_creature)
    return db_creature

# ============================================================================
# CONTENT CATALOG TABLES - FOR SPELL/EQUIPMENT MANAGEMENT
# ============================================================================

class SpellCatalog(Base):
    """
    Database model for all spells (traditional D&D and custom/generated).
    Provides a unified catalog for spell management and character assignment.
    """
    __tablename__ = "spell_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Spell properties
    level = Column(Integer, nullable=False, index=True)  # 0-9 (0 = cantrip)
    school = Column(String(50), nullable=False, index=True)  # evocation, illusion, etc.
    casting_time = Column(String(100), nullable=False)
    spell_range = Column(String(100), nullable=False)
    components = Column(String(200), nullable=False)  # V, S, M
    duration = Column(String(100), nullable=False)
    concentration = Column(Boolean, default=False)
    ritual = Column(Boolean, default=False)
    
    # Content
    description = Column(Text, nullable=False)
    higher_levels = Column(Text, nullable=True)  # At higher levels description
    
    # Class compatibility (JSON array of class names)
    compatible_classes = Column(JSON, nullable=False, default=list)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom spells
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Custom spell theme (for generated spells)
    spell_theme = Column(String(50), nullable=True)  # "void", "fire", "nature", etc.
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert spell to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "level": self.level,
            "school": self.school,
            "casting_time": self.casting_time,
            "range": self.spell_range,
            "components": self.components,
            "duration": self.duration,
            "concentration": self.concentration,
            "ritual": self.ritual,
            "description": self.description,
            "higher_levels": self.higher_levels,
            "compatible_classes": self.compatible_classes,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "spell_theme": self.spell_theme
        }


class WeaponCatalog(Base):
    """
    Database model for all weapons (traditional D&D and custom/generated).
    Provides a unified catalog for weapon management and character assignment.
    """
    __tablename__ = "weapon_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Weapon properties
    weapon_type = Column(String(50), nullable=False, index=True)  # "simple", "martial"
    weapon_category = Column(String(50), nullable=False, index=True)  # "melee", "ranged"
    damage_dice = Column(String(20), nullable=False)  # "1d8", "2d6", etc.
    damage_type = Column(String(20), nullable=False)  # "slashing", "piercing", "bludgeoning"
    
    # Optional properties (JSON array)
    properties = Column(JSON, nullable=False, default=list)  # ["finesse", "light", "versatile"]
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "15 gp", "2 sp", etc.
    
    # Range (for ranged weapons)
    range_normal = Column(Integer, nullable=True)  # normal range in feet
    range_long = Column(Integer, nullable=True)    # long range in feet
    
    # Versatile damage (for versatile weapons)
    versatile_damage = Column(String(20), nullable=True)  # "1d10" for longsword
    
    # Description and lore
    description = Column(Text, nullable=True)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom weapons
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert weapon to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "weapon_type": self.weapon_type,
            "weapon_category": self.weapon_category,
            "damage_dice": self.damage_dice,
            "damage_type": self.damage_type,
            "properties": self.properties,
            "weight": self.weight,
            "cost": self.cost,
            "range_normal": self.range_normal,
            "range_long": self.range_long,
            "versatile_damage": self.versatile_damage,
            "description": self.description,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


class ArmorCatalog(Base):
    """
    Database model for all armor (traditional D&D and custom/generated).
    Provides a unified catalog for armor management and character assignment.
    """
    __tablename__ = "armor_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Armor properties
    armor_type = Column(String(20), nullable=False, index=True)  # "light", "medium", "heavy", "shield"
    armor_class = Column(String(20), nullable=False)  # "11 + Dex mod", "18", etc.
    
    # Requirements and limitations
    strength_requirement = Column(Integer, nullable=True)  # Minimum Str for heavy armor
    stealth_disadvantage = Column(Boolean, default=False)
    max_dex_bonus = Column(Integer, nullable=True)  # For medium/heavy armor
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "1,500 gp", "10 gp", etc.
    
    # Description and lore
    description = Column(Text, nullable=True)
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, XGE, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom armor
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert armor to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "armor_type": self.armor_type,
            "armor_class": self.armor_class,
            "strength_requirement": self.strength_requirement,
            "stealth_disadvantage": self.stealth_disadvantage,
            "max_dex_bonus": self.max_dex_bonus,
            "weight": self.weight,
            "cost": self.cost,
            "description": self.description,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


class ItemCatalog(Base):
    """
    Database model for all other items (adventuring gear, tools, etc.).
    Provides a unified catalog for general item management and character assignment.
    """
    __tablename__ = "item_catalog"
    
    id = Column(String(36), primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    
    # Item properties
    item_type = Column(String(50), nullable=False, index=True)  # "tool", "consumable", "magic_item", etc.
    item_category = Column(String(50), nullable=True, index=True)  # "artisan_tools", "potion", etc.
    
    # Physical attributes
    weight = Column(Integer, nullable=True)  # in pounds
    cost = Column(String(20), nullable=True)  # "25 gp", "2 sp", etc.
    
    # Usage and properties
    properties = Column(JSON, nullable=False, default=dict)  # Flexible properties storage
    uses_per_day = Column(Integer, nullable=True)  # For limited-use items
    charges = Column(Integer, nullable=True)  # For charged items
    
    # Description and mechanics
    description = Column(Text, nullable=True)
    mechanical_effect = Column(Text, nullable=True)  # Game mechanics description
    
    # Source information
    source = Column(String(50), nullable=False, index=True)  # "D&D 5e Core", "Custom", "Generated"
    source_book = Column(String(100), nullable=True)  # PHB, DMG, etc.
    page_number = Column(Integer, nullable=True)
    
    # Metadata
    created_by = Column(String(100), nullable=True)  # For custom items
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_homebrew = Column(Boolean, default=False)
    
    # Rarity and magic
    rarity = Column(String(20), default="common")  # common, uncommon, rare, etc.
    is_magical = Column(Boolean, default=False)
    requires_attunement = Column(Boolean, default=False)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert item to dictionary format."""
        return {
            "id": self.id,
            "name": self.name,
            "item_type": self.item_type,
            "item_category": self.item_category,
            "weight": self.weight,
            "cost": self.cost,
            "properties": self.properties,
            "uses_per_day": self.uses_per_day,
            "charges": self.charges,
            "description": self.description,
            "mechanical_effect": self.mechanical_effect,
            "source": self.source,
            "source_book": self.source_book,
            "page_number": self.page_number,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_homebrew": self.is_homebrew,
            "rarity": self.rarity,
            "is_magical": self.is_magical,
            "requires_attunement": self.requires_attunement
        }


# ============================================================================
# CHARACTER-CONTENT RELATIONSHIP TABLES
# ============================================================================

class CharacterSpellAccess(Base):
    """
    Many-to-many relationship table for character spell access.
    Tracks which spells a character has access to and their status.
    """
    __tablename__ = "character_spell_access"
    
    id = Column(String(36), primary_key=True, index=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    spell_id = Column(String(36), ForeignKey("spell_catalog.id"), nullable=False, index=True)
    
    # Status tracking
    is_known = Column(Boolean, default=False)      # Spell is in character's known spells
    is_prepared = Column(Boolean, default=False)   # Spell is currently prepared
    is_favorite = Column(Boolean, default=False)   # Player-marked favorite
    
    # Learning information
    learned_at_level = Column(Integer, nullable=True)  # Level when spell was learned
    learned_from = Column(String(100), nullable=True)  # "level_up", "scroll", "tutor", etc.
    
    # Custom spell list assignment (for themed spellcasters)
    spell_list_category = Column(String(50), nullable=True)  # "known", "custom_void", "custom_fire", etc.
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert spell access to dictionary format."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "spell_id": self.spell_id,
            "is_known": self.is_known,
            "is_prepared": self.is_prepared,
            "is_favorite": self.is_favorite,
            "learned_at_level": self.learned_at_level,
            "learned_from": self.learned_from,
            "spell_list_category": self.spell_list_category,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class CharacterEquipmentAccess(Base):
    """
    Many-to-many relationship table for character equipment access.
    Tracks which equipment a character owns and their status.
    """
    __tablename__ = "character_equipment_access"
    
    id = Column(String(36), primary_key=True, index=True)
    character_id = Column(String(36), ForeignKey("characters.id"), nullable=False, index=True)
    
    # Equipment can be from any catalog
    weapon_id = Column(String(36), ForeignKey("weapon_catalog.id"), nullable=True, index=True)
    armor_id = Column(String(36), ForeignKey("armor_catalog.id"), nullable=True, index=True)
    item_id = Column(String(36), ForeignKey("item_catalog.id"), nullable=True, index=True)
    
    # Status tracking
    quantity = Column(Integer, default=1)
    is_equipped = Column(Boolean, default=False)
    is_attuned = Column(Boolean, default=False)  # For magical items
    is_favorite = Column(Boolean, default=False)  # Player-marked favorite
    
    # Equipment slot (for equipped items)
    equipment_slot = Column(String(50), nullable=True)  # "main_hand", "armor", "boots", etc.
    
    # Acquisition information
    acquired_at_level = Column(Integer, nullable=True)  # Level when item was acquired
    acquired_from = Column(String(100), nullable=True)  # "starting_equipment", "loot", "purchase", etc.
    
    # Condition and notes
    condition = Column(String(20), default="normal")  # "normal", "damaged", "broken", etc.
    notes = Column(Text, nullable=True)  # Player notes about the item
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert equipment access to dictionary format."""
        return {
            "id": self.id,
            "character_id": self.character_id,
            "weapon_id": self.weapon_id,
            "armor_id": self.armor_id,
            "item_id": self.item_id,
            "quantity": self.quantity,
            "is_equipped": self.is_equipped,
            "is_attuned": self.is_attuned,
            "is_favorite": self.is_favorite,
            "equipment_slot": self.equipment_slot,
            "acquired_at_level": self.acquired_at_level,
            "acquired_from": self.acquired_from,
            "condition": self.condition,
            "notes": self.notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

############################################################
# CAMPAIGN MANAGEMENT MODELS (Campaign, Chapter, PlotFork) #
############################################################
import enum

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

class Campaign(Base):
    __tablename__ = "campaigns"
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
    
    # Campaign content relationships
    campaign_characters = relationship("CampaignCharacter", cascade="all, delete-orphan")
    campaign_maps = relationship("CampaignMap", cascade="all, delete-orphan")

class Chapter(Base):
    __tablename__ = "chapters"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    title = Column(String(200), nullable=False)
    summary = Column(Text)
    content = Column(Text)
    status = Column(String(20), default=ChapterStatusEnum.DRAFT.value)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    campaign = relationship("Campaign", back_populates="chapters")
    plot_forks = relationship("PlotFork", back_populates="chapter", cascade="all, delete-orphan")

class PlotFork(Base):
    __tablename__ = "plot_forks"
    id = Column(String(36), primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False)
    chapter_id = Column(String(36), ForeignKey("chapters.id"), nullable=False)
    fork_type = Column(String(20), nullable=False)
    description = Column(Text)
    options = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.utcnow)
    chapter = relationship("Chapter", back_populates="plot_forks")



# ============================================================================
# GIT-LIKE CHAPTER VERSIONING MODELS
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
    def get_chapter_by_hash(db: Session, version_hash: str) -> ChapterVersion:
        """Get chapter by version hash."""
        return db.query(ChapterVersion).filter(
            ChapterVersion.version_hash == version_hash
        ).first()
    
    @staticmethod
    def get_branch_head(db: Session, campaign_id: str, branch_name: str) -> ChapterVersion:
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
# ============================================================================
# CAMPAIGN CONTENT MODELS - CHARACTERS, NPCS, MONSTERS, AND MAPS
# ============================================================================

class CampaignCharacterTypeEnum(str, enum.Enum):
    """Types of characters in campaigns."""
    PLAYER_CHARACTER = "player_character"
    NPC = "npc"
    MONSTER = "monster"
    VILLAIN = "villain"
    ALLY = "ally"
    NEUTRAL = "neutral"

class CampaignCharacterStatusEnum(str, enum.Enum):
    """Status of characters in campaigns."""
    ACTIVE = "active"
    DECEASED = "deceased"
    RETIRED = "retired"
    MISSING = "missing"
    CAPTURED = "captured"
    TRANSFORMED = "transformed"

class MapTypeEnum(str, enum.Enum):
    """Types of maps in campaigns."""
    WORLD = "world"
    REGION = "region"
    CITY = "city"
    DUNGEON = "dungeon"
    BUILDING = "building"
    BATTLE = "battle"
    CUSTOM = "custom"

class MapStatusEnum(str, enum.Enum):
    """Status of maps in campaigns."""
    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    HIDDEN = "hidden"

class CampaignCharacter(Base):
    """
    Characters (PCs, NPCs, monsters) within a specific campaign.
    
    Each character gets a unique UUID and is linked to campaign chapters
    where they appear. This tracks campaign-specific character data.
    """
    __tablename__ = "campaign_characters"
    
    # Core identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Character identification
    name = Column(String(100), nullable=False, index=True)
    character_type = Column(String(20), default=CampaignCharacterTypeEnum.NPC.value)
    status = Column(String(20), default=CampaignCharacterStatusEnum.ACTIVE.value)
    
    # Basic character information
    species = Column(String(50), nullable=True)
    character_classes = Column(JSON, default=dict)  # Class levels if applicable
    level = Column(Integer, nullable=True)
    alignment = Column(String(20), nullable=True)
    
    # Physical description
    description = Column(Text, nullable=True)
    appearance = Column(Text, nullable=True)
    portrait_url = Column(String(500), nullable=True)
    
    # Character stats (flexible JSON storage)
    stats = Column(JSON, default=dict)  # AC, HP, abilities, saves, etc.
    abilities = Column(JSON, default=dict)  # Strength, Dex, etc.
    skills = Column(JSON, default=dict)
    equipment = Column(JSON, default=dict)
    spells = Column(JSON, default=dict)
    features = Column(JSON, default=dict)
    
    # Campaign-specific data
    role_in_campaign = Column(String(100), nullable=True)  # "Quest giver", "Final boss", etc.
    backstory = Column(Text, nullable=True)
    motivations = Column(JSON, default=list)
    relationships = Column(JSON, default=dict)  # Relationships with other characters
    secrets = Column(Text, nullable=True)  # DM-only information
    
    # Story progression
    character_arc = Column(JSON, default=dict)  # Character development over time
    first_appearance_chapter = Column(String(12), nullable=True)  # Chapter hash
    last_seen_chapter = Column(String(12), nullable=True)  # Chapter hash
    chapters_appeared = Column(JSON, default=list)  # List of chapter hashes
    
    # Combat and mechanics
    challenge_rating = Column(String(10), nullable=True)  # For monsters/NPCs
    legendary_actions = Column(JSON, default=list)
    lair_actions = Column(JSON, default=list)
    regional_effects = Column(JSON, default=list)
    
    # Player information (for PCs)
    player_name = Column(String(100), nullable=True)
    player_notes = Column(Text, nullable=True)
    character_sheet_data = Column(JSON, default=dict)  # Full character sheet if PC
    
    # Generation metadata
    generated_by = Column(String(50), default="manual")  # "manual", "llm", "import"
    generation_prompt = Column(Text, nullable=True)  # Original prompt if LLM-generated
    source_material = Column(String(100), nullable=True)  # "PHB", "Custom", etc.
    
    # Metadata
    created_by = Column(String(100), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    is_public = Column(Boolean, default=False)
    
    # Relationships
    campaign = relationship("Campaign")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert character to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "character_type": self.character_type,
            "status": self.status,
            "species": self.species,
            "character_classes": self.character_classes,
            "level": self.level,
            "alignment": self.alignment,
            "description": self.description,
            "appearance": self.appearance,
            "portrait_url": self.portrait_url,
            "stats": self.stats,
            "abilities": self.abilities,
            "skills": self.skills,
            "equipment": self.equipment,
            "spells": self.spells,
            "features": self.features,
            "role_in_campaign": self.role_in_campaign,
            "backstory": self.backstory,
            "motivations": self.motivations,
            "relationships": self.relationships,
            "secrets": self.secrets,
            "character_arc": self.character_arc,
            "first_appearance_chapter": self.first_appearance_chapter,
            "last_seen_chapter": self.last_seen_chapter,
            "chapters_appeared": self.chapters_appeared,
            "challenge_rating": self.challenge_rating,
            "legendary_actions": self.legendary_actions,
            "lair_actions": self.lair_actions,
            "regional_effects": self.regional_effects,
            "player_name": self.player_name,
            "player_notes": self.player_notes,
            "character_sheet_data": self.character_sheet_data,
            "generated_by": self.generated_by,
            "generation_prompt": self.generation_prompt,
            "source_material": self.source_material,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active,
            "is_public": self.is_public
        }

class CampaignMap(Base):
    """
    Maps associated with campaigns.
    
    Each map gets a unique UUID and can be linked to specific chapters
    or used throughout the campaign.
    """
    __tablename__ = "campaign_maps"
    
    # Core identification
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    
    # Map identification
    name = Column(String(100), nullable=False, index=True)
    map_type = Column(String(20), default=MapTypeEnum.CUSTOM.value)
    status = Column(String(20), default=MapStatusEnum.DRAFT.value)
    
    # Map information
    description = Column(Text, nullable=True)
    scale = Column(String(50), nullable=True)  # "1 square = 5 feet", "1 hex = 1 mile", etc.
    dimensions = Column(String(50), nullable=True)  # "30x40 squares", "100x150 pixels"
    
    # Map files and data
    image_url = Column(String(500), nullable=True)  # URL to map image
    thumbnail_url = Column(String(500), nullable=True)  # URL to thumbnail
    map_data = Column(JSON, default=dict)  # Grid data, tokens, annotations, etc.
    layers = Column(JSON, default=list)  # Map layers (background, objects, tokens, etc.)
    
    # Geographic information
    parent_map_id = Column(String(36), ForeignKey("campaign_maps.id"), nullable=True)  # For nested maps
    coordinates = Column(JSON, default=dict)  # Position within parent map
    connected_maps = Column(JSON, default=list)  # List of connected map IDs
    
    # Campaign integration
    associated_chapters = Column(JSON, default=list)  # Chapter hashes where this map is used
    first_used_chapter = Column(String(12), nullable=True)  # First chapter hash
    last_used_chapter = Column(String(12), nullable=True)  # Last chapter hash
    
    # Interactive elements
    points_of_interest = Column(JSON, default=list)  # POIs on the map
    hidden_areas = Column(JSON, default=list)  # Areas hidden from players
    dynamic_elements = Column(JSON, default=list)  # Elements that change over time
    
    # Tokens and characters
    character_positions = Column(JSON, default=dict)  # Current character positions
    npc_positions = Column(JSON, default=dict)  # NPC positions
    monster_positions = Column(JSON, default=dict)  # Monster positions
    
    # Battle map specific
    grid_type = Column(String(20), nullable=True)  # "square", "hex", "none"
    grid_size = Column(Integer, nullable=True)  # Size in pixels
    initiative_order = Column(JSON, default=list)  # Combat initiative if battle map
    
    # Generation metadata
    generated_by = Column(String(50), default="manual")  # "manual", "llm", "import"
    generation_prompt = Column(Text, nullable=True)  # Original prompt if LLM-generated
    source_material = Column(String(100), nullable=True)  # Source of map
    
    # Access control
    player_visible = Column(Boolean, default=True)  # Can players see this map?
    dm_notes = Column(Text, nullable=True)  # DM-only notes about the map
    
    # Metadata
    created_by = Column(String(100), default="system")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    
    # Relationships
    campaign = relationship("Campaign")
    parent_map = relationship("CampaignMap", remote_side=[id])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert map to dictionary format."""
        return {
            "id": self.id,
            "campaign_id": self.campaign_id,
            "name": self.name,
            "map_type": self.map_type,
            "status": self.status,
            "description": self.description,
            "scale": self.scale,
            "dimensions": self.dimensions,
            "image_url": self.image_url,
            "thumbnail_url": self.thumbnail_url,
            "map_data": self.map_data,
            "layers": self.layers,
            "parent_map_id": self.parent_map_id,
            "coordinates": self.coordinates,
            "connected_maps": self.connected_maps,
            "associated_chapters": self.associated_chapters,
            "first_used_chapter": self.first_used_chapter,
            "last_used_chapter": self.last_used_chapter,
            "points_of_interest": self.points_of_interest,
            "hidden_areas": self.hidden_areas,
            "dynamic_elements": self.dynamic_elements,
            "character_positions": self.character_positions,
            "npc_positions": self.npc_positions,
            "monster_positions": self.monster_positions,
            "grid_type": self.grid_type,
            "grid_size": self.grid_size,
            "initiative_order": self.initiative_order,
            "generated_by": self.generated_by,
            "generation_prompt": self.generation_prompt,
            "source_material": self.source_material,
            "player_visible": self.player_visible,
            "dm_notes": self.dm_notes,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "is_active": self.is_active
        }

class CharacterChapterAppearance(Base):
    """
    Junction table tracking which characters appear in which chapter versions.
    
    This allows tracking character appearances across the git-like campaign structure.
    """
    __tablename__ = "character_chapter_appearances"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    character_id = Column(String(36), ForeignKey("campaign_characters.id"), nullable=False, index=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id"), nullable=False, index=True)
    
    # Appearance details
    role_in_chapter = Column(String(100), nullable=True)  # "Main antagonist", "Quest giver", etc.
    importance_level = Column(String(20), default="minor")  # "major", "minor", "cameo", "mentioned"
    scene_descriptions = Column(JSON, default=list)  # Descriptions of scenes they're in
    
    # Character state in this chapter
    character_status = Column(String(20), default="active")  # Status at time of chapter
    location = Column(String(100), nullable=True)  # Where they are in this chapter
    character_notes = Column(Text, nullable=True)  # Chapter-specific character notes
    
    # Story progression
    character_development = Column(Text, nullable=True)  # How character develops in this chapter
    relationships_changed = Column(JSON, default=dict)  # Relationship changes in this chapter
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign")
    character = relationship("CampaignCharacter")
    chapter_version = relationship("ChapterVersion")

class MapChapterUsage(Base):
    """
    Junction table tracking which maps are used in which chapter versions.
    
    This allows tracking map usage across the git-like campaign structure.
    """
    __tablename__ = "map_chapter_usage"
    
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    campaign_id = Column(String(36), ForeignKey("campaigns.id"), nullable=False, index=True)
    map_id = Column(String(36), ForeignKey("campaign_maps.id"), nullable=False, index=True)
    chapter_version_id = Column(String(36), ForeignKey("chapter_versions.id"), nullable=False, index=True)
    
    # Usage details
    usage_type = Column(String(50), default="location")  # "location", "battle", "reference", "travel"
    importance_level = Column(String(20), default="minor")  # "primary", "secondary", "minor", "reference"
    scene_descriptions = Column(JSON, default=list)  # Descriptions of scenes using this map
    
    # Map state in this chapter
    map_modifications = Column(JSON, default=dict)  # Temporary changes to the map for this chapter
    active_areas = Column(JSON, default=list)  # Which areas of the map are active/important
    hidden_from_players = Column(JSON, default=list)  # Areas hidden in this chapter
    
    # Token positions for this chapter
    character_positions = Column(JSON, default=dict)  # Character positions specific to this chapter
    dynamic_elements_state = Column(JSON, default=dict)  # State of dynamic elements
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    campaign = relationship("Campaign")
    map = relationship("CampaignMap")
    chapter_version = relationship("ChapterVersion")

# ============================================================================
# DATABASE ACCESS LAYER FOR CAMPAIGN CONTENT
# ============================================================================

class CampaignContentDB:
    """Database operations for campaign characters and maps."""
    
    @staticmethod
    def create_campaign_character(db: Session, character_data: Dict[str, Any]) -> CampaignCharacter:
        """Create a new campaign character."""
        character = CampaignCharacter(
            campaign_id=character_data["campaign_id"],
            name=character_data["name"],
            character_type=character_data.get("character_type", CampaignCharacterTypeEnum.NPC.value),
            species=character_data.get("species"),
            level=character_data.get("level"),
            description=character_data.get("description"),
            stats=character_data.get("stats", {}),
            role_in_campaign=character_data.get("role_in_campaign"),
            backstory=character_data.get("backstory"),
            challenge_rating=character_data.get("challenge_rating"),
            player_name=character_data.get("player_name"),
            created_by=character_data.get("created_by", "system")
        )
        
        db.add(character)
        db.commit()
        db.refresh(character)
        return character
    
    @staticmethod
    def get_campaign_character(db: Session, character_id: str) -> CampaignCharacter:
        """Get campaign character by ID."""
        return db.query(CampaignCharacter).filter(
            CampaignCharacter.id == character_id,
            CampaignCharacter.is_active == True
        ).first()
    
    @staticmethod
    def get_campaign_characters(db: Session, campaign_id: str, character_type: str = None) -> List[CampaignCharacter]:
        """Get all characters for a campaign, optionally filtered by type."""
        query = db.query(CampaignCharacter).filter(
            CampaignCharacter.campaign_id == campaign_id,
            CampaignCharacter.is_active == True
        )
        
        if character_type:
            query = query.filter(CampaignCharacter.character_type == character_type)
        
        return query.all()
    
    @staticmethod
    def create_campaign_map(db: Session, map_data: Dict[str, Any]) -> CampaignMap:
        """Create a new campaign map."""
        map_obj = CampaignMap(
            campaign_id=map_data["campaign_id"],
            name=map_data["name"],
            map_type=map_data.get("map_type", MapTypeEnum.CUSTOM.value),
            description=map_data.get("description"),
            scale=map_data.get("scale"),
            image_url=map_data.get("image_url"),
            map_data=map_data.get("map_data", {}),
            points_of_interest=map_data.get("points_of_interest", []),
            grid_type=map_data.get("grid_type"),
            created_by=map_data.get("created_by", "system")
        )
        
        db.add(map_obj)
        db.commit()
        db.refresh(map_obj)
        return map_obj
    
    @staticmethod
    def get_campaign_map(db: Session, map_id: str) -> CampaignMap:
        """Get campaign map by ID."""
        return db.query(CampaignMap).filter(
            CampaignMap.id == map_id,
            CampaignMap.is_active == True
        ).first()
    
    @staticmethod
    def get_campaign_maps(db: Session, campaign_id: str, map_type: str = None) -> List[CampaignMap]:
        """Get all maps for a campaign, optionally filtered by type."""
        query = db.query(CampaignMap).filter(
            CampaignMap.campaign_id == campaign_id,
            CampaignMap.is_active == True
        )
        
        if map_type:
            query = query.filter(CampaignMap.map_type == map_type)
        
        return query.all()
    
    @staticmethod
    def link_character_to_chapter(db: Session, link_data: Dict[str, Any]) -> CharacterChapterAppearance:
        """Link a character to a chapter version."""
        appearance = CharacterChapterAppearance(
            campaign_id=link_data["campaign_id"],
            character_id=link_data["character_id"],
            chapter_version_id=link_data["chapter_version_id"],
            role_in_chapter=link_data.get("role_in_chapter"),
            importance_level=link_data.get("importance_level", "minor"),
            character_development=link_data.get("character_development")
        )
        
        db.add(appearance)
        db.commit()
        db.refresh(appearance)
        return appearance
    
    @staticmethod
    def link_map_to_chapter(db: Session, link_data: Dict[str, Any]) -> MapChapterUsage:
        """Link a map to a chapter version."""
        usage = MapChapterUsage(
            campaign_id=link_data["campaign_id"],
            map_id=link_data["map_id"],
            chapter_version_id=link_data["chapter_version_id"],
            usage_type=link_data.get("usage_type", "location"),
            importance_level=link_data.get("importance_level", "minor"),
            character_positions=link_data.get("character_positions", {})
        )
        
        db.add(usage)
        db.commit()
        db.refresh(usage)
        return usage

# ============================================================================
# UPDATE CAMPAIGN MODEL WITH NEW RELATIONSHIPS
# ============================================================================

# Add these relationships to the existing Campaign model via monkey patching
# (This approach allows us to extend without redefining the whole class)

def add_campaign_content_relationships():
    """Add content relationships to Campaign model."""
    # This would be called during database initialization
    Campaign.campaign_characters = relationship("CampaignCharacter", cascade="all, delete-orphan")
    Campaign.campaign_maps = relationship("CampaignMap", cascade="all, delete-orphan")

# Database connection setup (to be configured in main app)
engine = None
SessionLocal = None

def init_database(database_url: str):
    """Initialize database connection."""
    global engine, SessionLocal
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    
    # Add content relationships
    add_campaign_content_relationships()

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
    # Campaign core models
    'Campaign', 'Chapter', 'PlotFork', 'CampaignDB',
    
    # Git-like versioning models
    'ChapterVersion', 'CampaignBranch', 'ChapterChoice', 'PlaySession', 'ChapterMerge',
    'ChapterVersionDB',
    
    # Campaign content models
    'CampaignCharacter', 'CampaignMap', 'CharacterChapterAppearance', 'MapChapterUsage',
    'CampaignContentDB',
    
    # Enums
    'CampaignStatusEnum', 'ChapterStatusEnum', 'PlotForkTypeEnum',
    'ChapterVersionTypeEnum', 'BranchTypeEnum', 'PlaySessionStatusEnum',
    'CampaignCharacterTypeEnum', 'CampaignCharacterStatusEnum', 
    'MapTypeEnum', 'MapStatusEnum',
    
    # Database utilities
    'init_database', 'get_db', 'Base'
]

