"""
Database models for the D&D Character Creator with Git-like versioning system.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
import hashlib
import uuid
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, ForeignKey, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker

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
    
    id = Column(Integer, primary_key=True, index=True)
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
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("character_repositories.id"), nullable=False)
    
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
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("character_repositories.id"), nullable=False)
    branch_id = Column(Integer, ForeignKey("character_branches.id"), nullable=False)
    
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
    
    id = Column(Integer, primary_key=True, index=True)
    repository_id = Column(Integer, ForeignKey("character_repositories.id"), nullable=False)
    
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
    Legacy database model for D&D characters.
    This is kept for backwards compatibility and simple use cases.
    New characters should use the CharacterRepository system.
    """
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Link to new versioning system (optional)
    repository_id = Column(Integer, ForeignKey("character_repositories.id"), nullable=True)
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


class CharacterSession(Base):
    """Database model for character creation sessions."""
    __tablename__ = "character_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String(36), unique=True, index=True)  # UUID
    character_id = Column(Integer, nullable=True)  # Links to Character if saved
    
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
    
    id = Column(Integer, primary_key=True, index=True)
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

# ============================================================================
# DATABASE ACCESS LAYER - CRUD OPERATIONS
# ============================================================================
"""
This section addresses the comments about database access patterns:

ARCHITECTURE OVERVIEW:
- Database models (Character, CharacterSession, CustomContent) define the schema
- CharacterDB class provides all database operations with proper error handling
- Integration with character_models.py CharacterSheet class for gameplay
- Session management for character creation workflows

OPERATION FLOW:
1. CREATE NEW CHARACTER: CharacterSheet -> CharacterDB.save_character_sheet() -> Database
2. UPDATE EXISTING: Database -> CharacterDB.load_character_sheet() -> modify -> save back
3. IN-GAME PLAY: Load -> use getter/setter methods -> real-time updates -> save back

ACCESS PATTERNS:
- All database access goes through CharacterDB static methods
- Database sessions are properly managed with get_db() context manager
- Character data is converted between CharacterSheet objects and database models
- Supports both direct database operations and CharacterSheet integration
"""

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
# CHARACTER DATABASE OPERATIONS
# ============================================================================

class CharacterDB:
    """
    Database access layer for character operations.
    
    Order of operations:
    1) Create new character -> save to database
    2) Load existing character from database -> update -> save back
    3) Import for in-game play -> use getter/setter methods -> save back
    """
    
    @staticmethod
    def create_character(db: Session, character_data: Dict[str, Any]) -> Character:
        """Create a new character in the database."""
        db_character = Character(
            name=character_data.get("name", ""),
            player_name=character_data.get("player_name"),
            species=character_data.get("species", ""),
            background=character_data.get("background"),
            alignment=character_data.get("alignment"),
            level=character_data.get("level", 1),
            character_classes=character_data.get("character_classes", {}),
            strength=character_data.get("abilities", {}).get("strength", 10),
            dexterity=character_data.get("abilities", {}).get("dexterity", 10),
            constitution=character_data.get("abilities", {}).get("constitution", 10),
            intelligence=character_data.get("abilities", {}).get("intelligence", 10),
            wisdom=character_data.get("abilities", {}).get("wisdom", 10),
            charisma=character_data.get("abilities", {}).get("charisma", 10),
            armor_class=character_data.get("armor_class", 10),
            hit_points=character_data.get("hit_points", 1),
            proficiency_bonus=character_data.get("proficiency_bonus", 2),
            equipment=character_data.get("equipment", {}),
            features=character_data.get("features", {}),
            spells=character_data.get("spells", {}),
            skills=character_data.get("skills", {}),
            backstory=character_data.get("backstory"),
            notes=character_data.get("notes")
        )
        
        db.add(db_character)
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def get_character(db: Session, character_id: int) -> Optional[Character]:
        """Retrieve a character from the database."""
        return db.query(Character).filter(Character.id == character_id, Character.is_active == True).first()
    
    @staticmethod
    def get_character_by_name(db: Session, name: str, player_name: str = None) -> Optional[Character]:
        """Retrieve a character by name and optionally player name."""
        query = db.query(Character).filter(Character.name == name, Character.is_active == True)
        if player_name:
            query = query.filter(Character.player_name == player_name)
        return query.first()
    
    @staticmethod
    def update_character(db: Session, character_id: int, updates: Dict[str, Any]) -> Optional[Character]:
        """Update an existing character in the database."""
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return None
        
        # Update character fields with provided data
        for key, value in updates.items():
            if hasattr(db_character, key):
                setattr(db_character, key, value)
        
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def delete_character(db: Session, character_id: int) -> bool:
        """Soft delete a character (set is_active = False)."""
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return False
        
        db_character.is_active = False
        db.commit()
        return True
    
    @staticmethod
    def list_characters(db: Session, player_name: str = None, limit: int = 50, offset: int = 0) -> List[Character]:
        """List characters with optional filtering."""
        query = db.query(Character).filter(Character.is_active == True)
        
        if player_name:
            query = query.filter(Character.player_name == player_name)
        
        return query.offset(offset).limit(limit).all()
    
    @staticmethod
    def save_character_sheet(db: Session, character_sheet) -> Character:
        """
        Save a CharacterSheet object to the database.
        This bridges the gap between the new character models and database storage.
        """
        character_data = character_sheet.to_dict()
        
        # Check if this character has an ID (existing character)
        if hasattr(character_sheet, 'id') and character_sheet.id:
            return CharacterDB.update_character(db, character_sheet.id, character_data)
        else:
            return CharacterDB.create_character(db, character_data)
    
    @staticmethod
    def load_character_sheet(db: Session, character_id: int):
        """
        Load a character from database and convert to CharacterSheet object.
        Returns None if character not found.
        """
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return None
        
        # Import here to avoid circular imports
        from character_models import CharacterCore, CharacterState
        
        # Create CharacterCore from database data
        character_core = CharacterCore(db_character.name)
        character_core.species = db_character.species
        character_core.background = db_character.background or ""
        character_core.alignment = db_character.alignment.split() if db_character.alignment else ["Neutral", "Neutral"]
        character_core.character_classes = db_character.character_classes or {}
        
        # Set ability scores
        character_core.strength.base_score = db_character.strength
        character_core.dexterity.base_score = db_character.dexterity
        character_core.constitution.base_score = db_character.constitution
        character_core.intelligence.base_score = db_character.intelligence
        character_core.wisdom.base_score = db_character.wisdom
        character_core.charisma.base_score = db_character.charisma
        
        # Set backstory and other data
        character_core.backstory = db_character.backstory or ""
        
        # Create CharacterState
        character_state = CharacterState(character_core)
        character_state.max_hit_points = db_character.hit_points
        character_state.current_hit_points = db_character.hit_points
        
        # Store database ID for future saves
        character_core.id = db_character.id
        
        return {
            "core": character_core,
            "state": character_state,
            "db_character": db_character
        }

# ============================================================================
# CHARACTER SESSION OPERATIONS
# ============================================================================

class CharacterSessionDB:
    """Database operations for character creation sessions."""
    
    @staticmethod
    def create_session(db: Session, session_id: str, initial_data: Dict[str, Any] = None) -> CharacterSession:
        """Create a new character creation session."""
        session = CharacterSession(
            session_id=session_id,
            session_data=initial_data or {},
            current_step="basic_info"
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[CharacterSession]:
        """Get a character creation session."""
        return db.query(CharacterSession).filter(
            CharacterSession.session_id == session_id,
            CharacterSession.is_active == True
        ).first()
    
    @staticmethod
    def update_session(db: Session, session_id: str, updates: Dict[str, Any]) -> Optional[CharacterSession]:
        """Update a character creation session."""
        session = CharacterSessionDB.get_session(db, session_id)
        if not session:
            return None
        
        for key, value in updates.items():
            if hasattr(session, key):
                setattr(session, key, value)
        
        db.commit()
        db.refresh(session)
        return session


# ============================================================================
# USAGE EXAMPLES AND DOCUMENTATION
# ============================================================================

"""
CHARACTER VERSIONING SYSTEM USAGE EXAMPLES:

1. CREATE A NEW CHARACTER WITH VERSIONING:
   ```python
   # Create character data
   character_data = {
       "name": "Gandalf the Grey",
       "species": "Wizard (Maiar)",
       "level": 1,
       "character_classes": {"Wizard": 1},
       "abilities": {"strength": 10, "intelligence": 18, ...}
   }
   
   # Create repository with initial commit
   repo = CharacterRepositoryManager.create_repository(
       db=db,
       name="Gandalf the Grey",
       initial_character_data=character_data,
       player_name="Tolkien",
       description="The wise wizard of Middle-earth"
   )
   ```

2. LEVEL UP CHARACTER:
   ```python
   # Update character data for level 2
   level_2_data = character_data.copy()
   level_2_data["level"] = 2
   level_2_data["character_classes"] = {"Wizard": 2}
   
   # Commit the level up
   commit = CharacterRepositoryManager.commit_character_change(
       db=db,
       repository_id=repo.id,
       branch_name="main",
       character_data=level_2_data,
       commit_message="Level 2: Gained Arcane Recovery",
       commit_type="level_up",
       milestone_name="First Level Up"
   )
   ```

3. CREATE ALTERNATE CHARACTER PATH:
   ```python
   # Create branch for multiclass path at level 3
   multiclass_branch = CharacterRepositoryManager.create_branch(
       db=db,
       repository_id=repo.id,
       new_branch_name="multiclass-fighter",
       source_commit_hash=level_2_commit.commit_hash,
       description="Exploring multiclass with Fighter"
   )
   
   # Commit multiclass level 3
   multiclass_data = level_2_data.copy()
   multiclass_data["level"] = 3
   multiclass_data["character_classes"] = {"Wizard": 2, "Fighter": 1}
   
   multiclass_commit = CharacterRepositoryManager.commit_character_change(
       db=db,
       repository_id=repo.id,
       branch_name="multiclass-fighter",
       character_data=multiclass_data,
       commit_message="Level 3: Multiclassed into Fighter",
       commit_type="level_up"
   )
   ```

4. GET CHARACTER TIMELINE FOR FRONTEND:
   ```python
   timeline = CharacterVersioningAPI.get_character_timeline_for_frontend(
       db=db,
       repository_id=repo.id
   )
   # Returns formatted data for graph visualization
   ```

5. RETRIEVE CHARACTER AT SPECIFIC POINT:
   ```python
   # Get character data at level 2
   level_2_character = CharacterRepositoryManager.get_character_at_commit(
       db=db,
       commit_hash=level_2_commit.commit_hash
   )
   ```

FRONTEND INTEGRATION:
- Use CharacterVersioningAPI.get_character_timeline_for_frontend() for graph data
- Display branches as different colored lines
- Show commits as nodes with level/milestone information
- Allow users to click commits to view character state at that point
- Provide branch creation UI for "What if?" scenarios
- Show diff between commits to highlight changes

DATABASE SCHEMA:
- character_repositories: Main character containers
- character_branches: Different development paths
- character_commits: Individual character states/versions
- character_tags: Mark important milestones
- characters: Legacy table (kept for compatibility)

The system enables:
- Complete character development history
- "What if?" exploration with branches
- Visual timeline of character progression
- Rollback to previous character states
- Comparison between different development paths
- Story/campaign context tracking
- Collaborative character development
"""


# ============================================================================
# MODULE SUMMARY
# ============================================================================
"""
ENHANCED DATABASE MODELS WITH GIT-LIKE CHARACTER VERSIONING

This module provides a comprehensive database layer for D&D character management
with a revolutionary Git-like versioning system that allows players to explore
alternate character development paths.

KEY FEATURES:

1. CHARACTER REPOSITORIES (Git-like System):
   - CharacterRepository: Container for all versions of a character concept
   - CharacterBranch: Different development paths (main, multiclass, alternate stories)
   - CharacterCommit: Individual character states with full data snapshots
   - CharacterTag: Mark important milestones (deaths, resurrections, epic levels)

2. VERSION CONTROL OPERATIONS:
   - Create repositories with initial character commits
   - Branch from any commit to explore alternate paths
   - Commit character changes with detailed change tracking
   - Tag important milestones and story events
   - Retrieve character state at any point in history

3. VISUALIZATION SUPPORT:
   - Complete repository tree data for frontend graphs
   - Parent-child commit relationships for timeline display
   - Branch visualization with merge/split points
   - Diff calculation between character states

4. INTEGRATION SYSTEMS:
   - CharacterRepositoryManager: High-level Git-like operations
   - CharacterVersioningAPI: Frontend-friendly API methods
   - Integration with existing CharacterCore/CharacterState classes
   - Backwards compatibility with legacy Character model

5. USE CASES:
   - Track complete character development history
   - Explore "What if I multiclassed?" scenarios
   - Compare different character builds
   - Rollback to previous character states
   - Visualize character evolution over campaigns
   - Create alternate storyline branches
   - Collaborative character development

6. DATABASE OPERATIONS:
   - CharacterDB: CRUD operations for legacy characters
   - CharacterSessionDB: Character creation session management
   - Proper database session management with context managers
   - Integration with SQLAlchemy ORM

The system transforms character management from a simple database record into
a rich, explorable history that enhances storytelling and player engagement.
Players can see their character's journey visually, explore alternate paths,
and make informed decisions about character development.

FRONTEND VISUALIZATION:
The system is designed to support rich frontend visualizations showing:
- Character development timelines as interactive graphs
- Branch points where different paths diverged
- Commit nodes with level, XP, and milestone information
- Visual diffs between character states
- Tag markers for important story moments

This creates a "comic book multiverse" experience where players can explore
all the different paths their character might have taken.
"""

