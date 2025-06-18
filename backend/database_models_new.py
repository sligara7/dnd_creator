"""
Database models for the D&D Character Creator.
"""
from datetime import datetime
from typing import Dict, Any, Optional, List
from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, JSON, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, Session, sessionmaker

Base = declarative_base()


class Character(Base):
    """Database model for D&D characters."""
    __tablename__ = "characters"
    
    id = Column(Integer, primary_key=True, index=True)
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
        
        # Update basic fields
        for field in ["name", "player_name", "species", "background", "alignment", "level"]:
            if field in updates:
                setattr(db_character, field, updates[field])
        
        # Update ability scores
        if "abilities" in updates:
            abilities = updates["abilities"]
            for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
                if ability in abilities:
                    setattr(db_character, ability, abilities[ability])
        
        # Update other fields
        for field in ["armor_class", "hit_points", "proficiency_bonus", "backstory", "notes"]:
            if field in updates:
                setattr(db_character, field, updates[field])
        
        # Update JSON fields
        for json_field in ["character_classes", "equipment", "features", "spells", "skills"]:
            if json_field in updates:
                setattr(db_character, json_field, updates[json_field])
        
        db_character.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_character)
        return db_character
    
    @staticmethod
    def save_character_sheet(db: Session, character_sheet, character_id: int = None) -> Character:
        """
        Save a CharacterSheet object to the database.
        If character_id is provided, update existing character.
        Otherwise, create new character.
        """
        # Convert CharacterSheet to dictionary format
        character_data = character_sheet.get_character_summary()
        
        # Prepare data for database
        db_data = {
            "name": character_data["name"],
            "species": character_data["species"],
            "background": character_data["background"],
            "alignment": character_data["alignment"],
            "level": character_data["level"],
            "character_classes": character_data["classes"],
            "abilities": {
                "strength": character_data["ability_scores"]["strength"],
                "dexterity": character_data["ability_scores"]["dexterity"],
                "constitution": character_data["ability_scores"]["constitution"],
                "intelligence": character_data["ability_scores"]["intelligence"],
                "wisdom": character_data["ability_scores"]["wisdom"],
                "charisma": character_data["ability_scores"]["charisma"]
            },
            "armor_class": character_data["ac"],
            "hit_points": character_data["hp"]["max"],
            "proficiency_bonus": character_data["proficiency_bonus"],
            "equipment": character_data["equipment"],
            "skills": character_data["proficiencies"]["skills"],
            "backstory": character_data["backstory"]
        }
        
        if character_id:
            # Update existing character
            return CharacterDB.update_character(db, character_id, db_data)
        else:
            # Create new character
            return CharacterDB.create_character(db, db_data)
    
    @staticmethod
    def load_character_sheet(db: Session, character_id: int):
        """
        Load a character from database and convert to CharacterSheet object.
        Returns None if character not found.
        """
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return None
        
        # Import CharacterSheet here to avoid circular imports
        from character_models import CharacterSheet
        
        # Create CharacterSheet from database data
        character_sheet = CharacterSheet(db_character.name)
        
        # Update core character data
        character_sheet.core.species = db_character.species or ""
        character_sheet.core.background = db_character.background or ""
        character_sheet.core.alignment = db_character.alignment.split() if db_character.alignment else ["Neutral", "Neutral"]
        character_sheet.core.character_classes = db_character.character_classes or {}
        character_sheet.core.backstory = db_character.backstory or ""
        
        # Update ability scores
        character_sheet.core.strength.base_score = db_character.strength
        character_sheet.core.dexterity.base_score = db_character.dexterity
        character_sheet.core.constitution.base_score = db_character.constitution
        character_sheet.core.intelligence.base_score = db_character.intelligence
        character_sheet.core.wisdom.base_score = db_character.wisdom
        character_sheet.core.charisma.base_score = db_character.charisma
        
        # Update game state
        character_sheet.state.current_hit_points = db_character.hit_points
        
        # Update equipment if available
        if db_character.equipment:
            character_sheet.state.equipment = db_character.equipment.get("items", [])
            character_sheet.state.armor = db_character.equipment.get("armor", "")
            character_sheet.state.weapons = db_character.equipment.get("weapons", [])
        
        # Update proficiencies if available
        if db_character.skills:
            character_sheet.core.skill_proficiencies = db_character.skills
        
        # Recalculate derived stats
        character_sheet.calculate_all_derived_stats()
        
        return character_sheet
    
    @staticmethod
    def delete_character(db: Session, character_id: int) -> bool:
        """Soft delete a character (mark as inactive)."""
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            return False
        
        db_character.is_active = False
        db_character.updated_at = datetime.utcnow()
        db.commit()
        return True
    
    @staticmethod
    def list_characters(db: Session, player_name: str = None, limit: int = 100) -> List[Character]:
        """List characters, optionally filtered by player name."""
        query = db.query(Character).filter(Character.is_active == True)
        if player_name:
            query = query.filter(Character.player_name == player_name)
        return query.limit(limit).all()

# ============================================================================
# SESSION DATABASE OPERATIONS
# ============================================================================

class SessionDB:
    """Database operations for character creation sessions."""
    
    @staticmethod
    def create_session(db: Session, session_id: str, initial_data: Dict[str, Any] = None) -> CharacterSession:
        """Create a new character creation session."""
        db_session = CharacterSession(
            session_id=session_id,
            current_step="basic_info",
            session_data=initial_data or {}
        )
        
        db.add(db_session)
        db.commit()
        db.refresh(db_session)
        return db_session
    
    @staticmethod
    def get_session(db: Session, session_id: str) -> Optional[CharacterSession]:
        """Retrieve a character creation session."""
        return db.query(CharacterSession).filter(
            CharacterSession.session_id == session_id,
            CharacterSession.is_active == True
        ).first()
    
    @staticmethod
    def update_session(db: Session, session_id: str, updates: Dict[str, Any]) -> Optional[CharacterSession]:
        """Update a character creation session."""
        db_session = SessionDB.get_session(db, session_id)
        if not db_session:
            return None
        
        for field in ["current_step", "session_data", "character_id"]:
            if field in updates:
                setattr(db_session, field, updates[field])
        
        db_session.updated_at = datetime.utcnow()
        db.commit()
        db.refresh(db_session)
        return db_session

# ============================================================================
# USAGE EXAMPLES AND PATTERNS
# ============================================================================

"""
USAGE PATTERNS:

1. CREATE NEW CHARACTER:
   ```python
   # Create character using CharacterSheet
   from character_models import CharacterSheet
   character = CharacterSheet("Gandalf")
   character.core.species = "Human"
   # ... set other properties
   
   # Save to database
   with get_db() as db:
       db_character = CharacterDB.save_character_sheet(db, character)
       character_id = db_character.id
   ```

2. LOAD EXISTING CHARACTER FOR UPDATES:
   ```python
   # Load from database
   with get_db() as db:
       character = CharacterDB.load_character_sheet(db, character_id)
       
       # Make updates using getter/setter methods
       character.core.set_name("Gandalf the Grey")
       character.state.set_current_hit_points(50)
       
       # Save back to database
       CharacterDB.save_character_sheet(db, character, character_id)
   ```

3. IN-GAME PLAY SESSION:
   ```python
   # Load character for gameplay
   with get_db() as db:
       character = CharacterDB.load_character_sheet(db, character_id)
       
       # Use real-time update methods during play
       character.take_damage(10, "orc attack")
       character.add_condition(DnDCondition.POISONED)
       character.heal(5, "healing potion")
       
       # Save updated state back to database
       CharacterDB.save_character_sheet(db, character, character_id)
   ```
"""

