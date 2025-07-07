"""
FastAPI main application for D&D Character Creator - COMPLETE V2 API.

🏛️ UNIFIED V2 ARCHITECTURE:
- Complete factory-based content creation system
- Full character management with CRUD operations
- Real-time gameplay support (combat, rest, state management)
- Character validation and sheet access
- Simplified versioning system
- All v1 functionality reimplemented in clean v2 patterns

COMPLETE V2 ENDPOINTS:
- Factory creation (characters, monsters, NPCs, items, spells)
- Character management (create, read, update, delete, list)
- Gameplay support (state updates, combat, rest)
- Character sheets and validation
- Simplified versioning for character snapshots

This replaces the entire v1 API with a cleaner, more consistent v2 design.
"""
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query, Path, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path as PathLib
import sys
import time
import logging
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add the src directory to Python path for clean imports
sys.path.insert(0, str(PathLib(__file__).parent / "src"))

# Import configuration and services
from src.core.config import settings
from src.services.llm_service import create_llm_service

# Import database models and operations
from src.models.database_models import CharacterDB, init_database, get_db, CustomContent, UnifiedItem
from src.models.character_models import CharacterCore

# Import factory-based creation system
from src.services.creation_factory import CreationFactory
from src.core.enums import CreationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Add performance tracking
performance_metrics = {
    'startup_time': datetime.now(),
    'total_requests': 0,
    'total_processing_time': 0.0,
    'endpoint_metrics': {},
    'error_count': 0
}

def track_request_metrics(endpoint: str, processing_time: float, success: bool):
    """Track metrics for a request"""
    performance_metrics['total_requests'] += 1
    performance_metrics['total_processing_time'] += processing_time
    
    if endpoint not in performance_metrics['endpoint_metrics']:
        performance_metrics['endpoint_metrics'][endpoint] = {
            'requests': 0,
            'total_time': 0.0,
            'errors': 0
        }
    
    metrics = performance_metrics['endpoint_metrics'][endpoint]
    metrics['requests'] += 1
    metrics['total_time'] += processing_time
    
    if not success:
        metrics['errors'] += 1
        performance_metrics['error_count'] += 1

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    try:
        # Initialize database with proper database URL
        database_url = settings.effective_database_url
        init_database(database_url)
        logger.info("Database initialized successfully")
        
        # Initialize LLM service
        llm_service = create_llm_service()
        app.state.llm_service = llm_service
        logger.info("LLM service initialized successfully")
        
        # Initialize creation factory
        creation_factory = CreationFactory(llm_service)
        app.state.creation_factory = creation_factory
        logger.info("Creation factory initialized successfully")
        
        logger.info("🚀 D&D Character Creator API v2 started successfully!")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        logger.info("Shutting down D&D Character Creator API v2")

# Initialize FastAPI app
app = FastAPI(
    title="D&D Character Creator API v2 - Complete",
    description="Complete Factory-based D&D 5e Character Management System",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class DirectEditRequest(BaseModel):
    """
    Generic request model for direct user/DM edits to any object.
    Accepts a dict of fields to update, with optional notes for audit trail.
    """
    updates: Dict[str, Any] = Field(..., description="Fields and values to update. Keys are field names, values are new values.")
    notes: Optional[str] = Field(None, description="Optional notes or reason for the manual edit.")

class CharacterResponse(BaseModel):
    """Character response model."""
    id: str
    name: str
    species: str
    background: str
    level: int
    character_classes: Dict[str, int]
    backstory: str
    created_at: str
    user_modified: Optional[bool] = False

class JournalEntryResponse(BaseModel):
    """Response model for journal entries."""
    id: str
    character_id: str
    title: str
    content: str
    session_date: Optional[str] = None
    session_number: Optional[int] = None
    tags: List[str]
    is_private: bool
    experience_gained: Optional[int] = None
    story_beats: List[str]
    created_at: str
    updated_at: str
    user_modified: Optional[bool] = False

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "D&D Character Creator API v2 - Complete"
    }

# ============================================================================
# BASIC CRUD ENDPOINTS
# ============================================================================

@app.get("/api/v2/characters", response_model=List[CharacterResponse], tags=["characters"])
async def list_characters(
    db = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of characters to return"),
    offset: int = Query(0, ge=0, description="Number of characters to skip")
):
    """List all characters with pagination."""
    characters = CharacterDB.list_characters(db, limit=limit, offset=offset)
    return [CharacterResponse(
        id=char.id,
        name=char.name,
        species=char.species,
        background=char.background,
        level=char.level,
        character_classes=char.character_classes,
        backstory=char.backstory,
        created_at=char.created_at.isoformat(),
        user_modified=getattr(char, 'user_modified', False)
    ) for char in characters]

@app.get("/api/v2/characters/{character_id}", response_model=CharacterResponse, tags=["characters"])
async def get_character(
    character_id: str = Path(..., description="ID of the character to retrieve."),
    db = Depends(get_db)
):
    """Get a specific character by ID."""
    character = CharacterDB.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    return CharacterResponse(
        id=character.id,
        name=character.name,
        species=character.species,
        background=character.background,
        level=character.level,
        character_classes=character.character_classes,
        backstory=character.backstory,
        created_at=character.created_at.isoformat(),
        user_modified=getattr(character, 'user_modified', False)
    )

@app.get("/api/v2/characters/{character_id}/journal", tags=["characters", "journal"])
async def get_character_journal(
    character_id: str = Path(..., description="ID of the character whose journal to retrieve."),
    db = Depends(get_db)
):
    """Get all journal entries for a character."""
    character = CharacterDB.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Return journal entries if they exist
    journal_entries = getattr(character, 'journal_entries', [])
    return journal_entries

@app.get("/api/v2/npcs", tags=["npcs"])
async def list_npcs(
    db = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of NPCs to return"),
    offset: int = Query(0, ge=0, description="Number of NPCs to skip")
):
    """List all NPCs with pagination."""
    npcs = db.query(CustomContent).filter(CustomContent.content_type == "npc").offset(offset).limit(limit).all()
    return [{"id": npc.id, "name": npc.name, "description": npc.description, "content_data": npc.content_data} for npc in npcs]

@app.get("/api/v2/npcs/{npc_id}", tags=["npcs"])
async def get_npc(
    npc_id: str = Path(..., description="ID of the NPC to retrieve."),
    db = Depends(get_db)
):
    """Get a specific NPC by ID."""
    npc = db.query(CustomContent).filter(CustomContent.id == npc_id, CustomContent.content_type == "npc").first()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    return {"id": npc.id, "name": npc.name, "description": npc.description, "content_data": npc.content_data}

@app.get("/api/v2/monsters", tags=["monsters"])
async def list_monsters(
    db = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of monsters to return"),
    offset: int = Query(0, ge=0, description="Number of monsters to skip")
):
    """List all monsters with pagination."""
    monsters = db.query(CustomContent).filter(CustomContent.content_type == "monster").offset(offset).limit(limit).all()
    return [{"id": monster.id, "name": monster.name, "description": monster.description, "content_data": monster.content_data} for monster in monsters]

@app.get("/api/v2/monsters/{monster_id}", tags=["monsters"])
async def get_monster(
    monster_id: str = Path(..., description="ID of the monster to retrieve."),
    db = Depends(get_db)
):
    """Get a specific monster by ID."""
    monster = db.query(CustomContent).filter(CustomContent.id == monster_id, CustomContent.content_type == "monster").first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    return {"id": monster.id, "name": monster.name, "description": monster.description, "content_data": monster.content_data}

@app.get("/api/v2/items", tags=["items"])
async def list_items(
    db = Depends(get_db),
    limit: int = Query(100, ge=1, le=500, description="Maximum number of items to return"),
    offset: int = Query(0, ge=0, description="Number of items to skip")
):
    """List all items with pagination."""
    items = db.query(UnifiedItem).offset(offset).limit(limit).all()
    return [{"id": item.id, "name": item.name, "item_type": item.item_type, "short_description": item.short_description} for item in items]

@app.get("/api/v2/items/{item_id}", tags=["items"])
async def get_item(
    item_id: str = Path(..., description="ID of the item to retrieve."),
    db = Depends(get_db)
):
    """Get a specific item by ID."""
    item = db.query(UnifiedItem).filter(UnifiedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"id": item.id, "name": item.name, "item_type": item.item_type, "short_description": item.short_description}

# ============================================================================
# DIRECT EDIT ENDPOINTS
# ============================================================================

@app.post("/api/v2/characters/{character_id}/direct-edit", response_model=CharacterResponse, tags=["characters", "direct-edit"])
async def direct_edit_character(
    character_id: str = Path(..., description="ID of the character to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db = Depends(get_db)
):
    """
    Directly edit a character's fields (DM/user override). Sets user_modified flag.
    """
    # Load character from database
    character = CharacterDB.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Apply updates from edit.updates to the character object
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist on the character object
    for field, value in updates.items():
        if hasattr(character, field):
            try:
                setattr(character, field, value)
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on character.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag to True and add audit trail
    if hasattr(character, 'user_modified'):
        character.user_modified = True
    else:
        try:
            setattr(character, 'user_modified', True)
        except Exception:
            pass
    
    # Add audit trail entry
    if not hasattr(character, "audit_trail") or character.audit_trail is None:
        character.audit_trail = []
    
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes or None,
        "username": "dev"
    }
    character.audit_trail.append(audit_entry)
    
    # Save the updated character back to the database
    update_fields = {field: getattr(character, field) for field in updates.keys() if hasattr(character, field)}
    update_fields['user_modified'] = True
    update_fields['audit_trail'] = character.audit_trail
    updated_character = CharacterDB.update_character(db, character_id, update_fields)
    if not updated_character:
        raise HTTPException(status_code=500, detail="Failed to save updated character")
    
    # Return the updated character as a CharacterResponse
    return CharacterResponse(
        id=updated_character.id,
        name=updated_character.name,
        species=updated_character.species,
        background=updated_character.background,
        level=updated_character.level,
        character_classes=updated_character.character_classes,
        backstory=updated_character.backstory,
        created_at=updated_character.created_at.isoformat(),
        user_modified=getattr(updated_character, 'user_modified', True)
    )

@app.post("/api/v2/characters/{character_id}/backstory/direct-edit", response_model=CharacterResponse, tags=["characters", "direct-edit"])
async def direct_edit_character_backstory(
    character_id: str = Path(..., description="ID of the character to edit backstory."),
    edit: DirectEditRequest = Body(..., description="New backstory value (use 'backstory' key in updates)."),
    db = Depends(get_db)
):
    """
    Directly edit a character's backstory field (DM/user override). Sets user_modified flag.
    """
    character = CharacterDB.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    updates = edit.updates or {}
    if "backstory" not in updates:
        raise HTTPException(status_code=400, detail="'backstory' field must be provided in updates.")
    
    try:
        character.backstory = updates["backstory"]
        character.user_modified = True
        
        # Add audit trail entry
        if not hasattr(character, "audit_trail") or character.audit_trail is None:
            character.audit_trail = []
        
        audit_entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "fields_changed": ["backstory"],
            "notes": edit.notes or None,
            "username": "dev"
        }
        character.audit_trail.append(audit_entry)
        db.commit()
        db.refresh(character)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update backstory: {e}")
    
    return CharacterResponse(
        id=character.id,
        name=character.name,
        species=character.species,
        background=character.background,
        level=character.level,
        character_classes=character.character_classes,
        backstory=character.backstory,
        created_at=character.created_at.isoformat(),
        user_modified=getattr(character, 'user_modified', True)
    )

@app.post("/api/v2/characters/{character_id}/journal/{entry_id}/direct-edit", tags=["journal", "direct-edit"])
async def direct_edit_journal_entry(
    character_id: str = Path(..., description="ID of the character."),
    entry_id: str = Path(..., description="ID of the journal entry to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db = Depends(get_db)
):
    """
    Directly edit a journal entry's fields (DM/user override). Sets user_modified flag.
    """
    # Ensure character exists
    character = CharacterDB.get_character(db, character_id)
    if not character:
        raise HTTPException(status_code=404, detail="Character not found")
    
    # Ensure journal entry exists
    entry = CharacterDB.get_journal_entry(db, character_id, entry_id)
    if not entry:
        raise HTTPException(status_code=404, detail="Journal entry not found")
    
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist in the entry
    for field, value in updates.items():
        if field in entry:
            try:
                entry[field] = value
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on journal entry.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag and audit trail
    entry["user_modified"] = True
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes or None,
        "username": "dev"
    }
    if "audit_trail" not in entry:
        entry["audit_trail"] = []
    entry["audit_trail"].append(audit_entry)
    
    # Save the updated entry
    updated_entry = CharacterDB.update_journal_entry(db, character_id, entry_id, entry)
    if not updated_entry:
        raise HTTPException(status_code=500, detail="Failed to save updated journal entry")
    
    return JournalEntryResponse(**updated_entry)

@app.post("/api/v2/npcs/{npc_id}/direct-edit", tags=["npcs", "direct-edit"])
async def direct_edit_npc(
    npc_id: str = Path(..., description="ID of the NPC to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """
    Directly edit an NPC's fields (DM/user override). Sets user_modified flag in content_data.
    """
    npc = db.query(CustomContent).filter(CustomContent.id == npc_id, CustomContent.content_type == "npc").first()
    if not npc:
        raise HTTPException(status_code=404, detail="NPC not found")
    
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist in content_data
    for field, value in updates.items():
        if field in npc.content_data:
            try:
                npc.content_data[field] = value
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on NPC.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag and audit trail
    npc.content_data["user_modified"] = True
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes or None,
        "username": "dev"
    }
    if "audit_trail" not in npc.content_data:
        npc.content_data["audit_trail"] = []
    npc.content_data["audit_trail"].append(audit_entry)
    
    db.commit()
    db.refresh(npc)
    
    # Return updated content_data as response
    return {
        "id": npc.id,
        "name": npc.name,
        "content_type": npc.content_type,
        "content_data": npc.content_data,
        "description": npc.description,
        "created_by": npc.created_by,
        "created_at": npc.created_at.isoformat() if npc.created_at else None,
        "updated_at": npc.updated_at.isoformat() if npc.updated_at else None,
        "is_active": npc.is_active,
        "is_public": npc.is_public,
        "user_modified": npc.content_data.get("user_modified", False)
    }

@app.post("/api/v2/monsters/{monster_id}/direct-edit", tags=["monsters", "direct-edit"])
async def direct_edit_monster(
    monster_id: str = Path(..., description="ID of the monster to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """
    Directly edit a monster's fields (DM/user override). Sets user_modified flag in content_data.
    """
    monster = db.query(CustomContent).filter(CustomContent.id == monster_id, CustomContent.content_type == "creature").first()
    if not monster:
        raise HTTPException(status_code=404, detail="Monster not found")
    
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist in content_data
    for field, value in updates.items():
        if field in monster.content_data:
            try:
                monster.content_data[field] = value
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on monster.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag and audit trail
    monster.content_data["user_modified"] = True
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes or None,
        "username": "dev"
    }
    if "audit_trail" not in monster.content_data:
        monster.content_data["audit_trail"] = []
    monster.content_data["audit_trail"].append(audit_entry)
    
    db.commit()
    db.refresh(monster)
    
    # Return updated content_data as response
    return {
        "id": monster.id,
        "name": monster.name,
        "content_type": monster.content_type,
        "content_data": monster.content_data,
        "description": monster.description,
        "created_by": monster.created_by,
        "created_at": monster.created_at.isoformat() if monster.created_at else None,
        "updated_at": monster.updated_at.isoformat() if monster.updated_at else None,
        "is_active": monster.is_active,
        "is_public": monster.is_public,
        "user_modified": monster.content_data.get("user_modified", False)
    }

@app.post("/api/v2/items/{item_id}/direct-edit", tags=["items", "direct-edit"])
async def direct_edit_item(
    item_id: str = Path(..., description="ID of the item to edit directly."),
    edit: DirectEditRequest = Body(..., description="Fields and values to update."),
    db: Session = Depends(get_db)
):
    """
    Directly edit an item's fields (DM/user override). Sets user_modified flag in content_data.
    """
    item = db.query(UnifiedItem).filter(UnifiedItem.id == item_id).first()
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    
    updates = edit.updates or {}
    errors = []
    
    # Only allow updating fields that exist in content_data
    for field, value in updates.items():
        if field in item.content_data:
            try:
                item.content_data[field] = value
            except Exception as e:
                errors.append(f"Failed to update '{field}': {e}")
        else:
            errors.append(f"Field '{field}' does not exist on item.")
    
    if errors:
        raise HTTPException(status_code=400, detail={"errors": errors})
    
    # Set user_modified flag and audit trail
    item.content_data["user_modified"] = True
    
    # Add audit trail entry with username
    audit_entry = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "fields_changed": list(updates.keys()),
        "notes": edit.notes or None,
        "username": "dev"
    }
    if "audit_trail" not in item.content_data:
        item.content_data["audit_trail"] = []
    item.content_data["audit_trail"].append(audit_entry)
    
    db.commit()
    db.refresh(item)
    
    # Return updated content_data as response
    return {
        "id": str(item.id),
        "name": item.name,
        "item_type": item.item_type,
        "content_data": item.content_data,
        "short_description": item.short_description,
        "rarity": item.rarity,
        "requires_attunement": item.requires_attunement,
        "created_by": item.created_by,
        "created_at": item.created_at.isoformat() if item.created_at else None,
        "updated_at": item.updated_at.isoformat() if item.updated_at else None,
        "is_active": item.is_active,
        "is_public": item.is_public,
        "user_modified": item.content_data.get("user_modified", False)
    }

# ============================================================================
# FACTORY ENDPOINTS
# ============================================================================

class FactoryCreateRequest(BaseModel):
    """Request model for factory-based creation from scratch."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    prompt: str
    theme: Optional[str] = Field(None, description="Optional campaign theme")
    user_preferences: Optional[Dict[str, Any]] = None
    extra_fields: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryResponse(BaseModel):
    """Response model for factory operations."""
    success: bool
    creation_type: str
    theme: Optional[str] = None
    object_id: Optional[str] = None
    data: Dict[str, Any]
    warnings: Optional[List[str]] = None
    processing_time: Optional[float] = None

@app.post("/api/v2/factory/create", response_model=FactoryResponse, tags=["factory"])
async def factory_create_from_scratch(request: FactoryCreateRequest, db = Depends(get_db)):
    """
    Create D&D objects from scratch using the factory pattern.
    Supports: character, monster, npc, weapon, armor, spell, other_item
    """
    start_time = time.time()
    
    try:
        # Validate creation type
        try:
            creation_type = CreationOptions(request.creation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid creation type: {request.creation_type}")
        
        logger.info(f"Factory creating {creation_type.value} from scratch: {request.prompt[:100]}...")
        
        # Use the factory to create the object
        factory = app.state.creation_factory
        result = await factory.create_from_scratch(
            creation_type, 
            request.prompt,
            theme=request.theme,
            user_preferences=request.user_preferences or {},
            extra_fields=request.extra_fields or {}
        )
        
        object_id = None
        warnings = []
        
        # Save to database if requested (only for characters currently)
        if request.save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                # Convert result to character data for database
                if hasattr(result, 'to_dict'):
                    character_data = result.to_dict()
                else:
                    character_data = result
                
                # Create character in database
                db_character_data = {
                    "name": character_data.get("name", "Generated Character"),
                    "species": character_data.get("species", "Human"),
                    "background": character_data.get("background", "Folk Hero"),
                    "level": character_data.get("level", 1),
                    "character_classes": character_data.get("character_classes", {"Fighter": 1}),
                    "backstory": character_data.get("backstory", ""),
                    "abilities": character_data.get("abilities", {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    }),
                    "armor_class": 10,
                    "hit_points": 10,
                    "proficiency_bonus": 2,
                    "skills": character_data.get("skills", {}),
                    "equipment": character_data.get("equipment", {})
                }
                
                db_character = CharacterDB.create_character(db, db_character_data)
                object_id = db_character.id
                logger.info(f"Factory-created character saved to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save factory-created character to database: {e}")
                warnings.append(f"Object created but not saved to database: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        logger.info(f"Factory creation completed in {processing_time:.2f}s")
        
        return FactoryResponse(
            success=True,
            creation_type=creation_type.value,
            theme=request.theme,
            object_id=object_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Factory creation failed: {e}")
        return FactoryResponse(
            success=False,
            creation_type=request.creation_type,
            theme=request.theme,
            data={"error": str(e)},
            processing_time=processing_time
        )

@app.get("/api/v2/factory/types", tags=["factory"])
async def get_factory_creation_types():
    """Get available creation types for the factory system."""
    return {
        "creation_types": [option.value for option in CreationOptions],
        "create_from_scratch": {
            "supported": [
                CreationOptions.CHARACTER.value,
                CreationOptions.MONSTER.value,
                CreationOptions.NPC.value,
                CreationOptions.WEAPON.value,
                CreationOptions.ARMOR.value,
                CreationOptions.SPELL.value,
                CreationOptions.OTHER_ITEM.value
            ],
            "description": "Create entirely new objects using LLM generation"
        }
    }

# ============================================================================
# TEST ENDPOINT
# ============================================================================

@app.post("/api/v2/test/mock", tags=["testing"])
async def test_mock_endpoint():
    """Test endpoint that returns static JSON to verify FastAPI is working."""
    return {
        "success": True,
        "message": "FastAPI v2 backend is working correctly",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "test_data": {
            "name": "Test Character v2",
            "species": "Human",
            "level": 1,
            "abilities": {
                "strength": 15,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 10,
                "charisma": 8
            }
        }
    }

class FactoryEvolveRequest(BaseModel):
    """Request model for factory-based evolution/modification."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    character_id: Optional[str] = None  # ID of existing object to evolve
    evolution_prompt: str  # Description of how to evolve/modify the object
    theme: Optional[str] = Field(None, description="Optional campaign theme")
    user_preferences: Optional[Dict[str, Any]] = None
    extra_fields: Optional[Dict[str, Any]] = None
    preserve_backstory: Optional[bool] = True
    save_to_database: Optional[bool] = True

@app.post("/api/v2/factory/evolve", response_model=FactoryResponse, tags=["factory"])
async def factory_evolve_object(request: FactoryEvolveRequest, db = Depends(get_db)):
    """
    Evolve/modify existing D&D objects or create new versions using the factory pattern.
    This can be used for leveling up, retheming, multiclassing, or other modifications.
    """
    start_time = time.time()
    
    try:
        # Validate creation type
        try:
            creation_type = CreationOptions(request.creation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid creation type: {request.creation_type}")
        
        logger.info(f"Factory evolving {creation_type.value}: {request.evolution_prompt[:100]}...")
        
        # For characters, load the existing character if character_id is provided
        base_character_data = None
        if request.character_id and creation_type == CreationOptions.CHARACTER:
            existing_character = CharacterDB.get_character(db, request.character_id)
            if existing_character:
                base_character_data = {
                    "name": existing_character.name,
                    "species": existing_character.species,
                    "background": existing_character.background,
                    "level": existing_character.level,
                    "character_classes": existing_character.character_classes,
                    "backstory": existing_character.backstory if request.preserve_backstory else "",
                    "abilities": {
                        "strength": existing_character.strength,
                        "dexterity": existing_character.dexterity,
                        "constitution": existing_character.constitution,
                        "intelligence": existing_character.intelligence,
                        "wisdom": existing_character.wisdom,
                        "charisma": existing_character.charisma
                    },
                    "skills": existing_character.skills,
                    "equipment": existing_character.equipment
                }
        
        # Create the evolution prompt with base data
        evolution_context = request.evolution_prompt
        if base_character_data:
            evolution_context = f"Based on this existing character: {base_character_data}, {request.evolution_prompt}"
        
        # Use the factory to create the evolved object
        factory = app.state.creation_factory
        result = await factory.create_from_scratch(
            creation_type, 
            evolution_context,
            theme=request.theme,
            user_preferences=request.user_preferences or {},
            extra_fields=request.extra_fields or {}
        )
        
        object_id = None
        warnings = []
        
        # Save to database if requested (only for characters currently)
        if request.save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                # Convert result to character data for database
                if hasattr(result, 'to_dict'):
                    character_data = result.to_dict()
                else:
                    character_data = result
                
                # Create evolved character in database
                db_character_data = {
                    "name": character_data.get("name", "Evolved Character"),
                    "species": character_data.get("species", base_character_data.get("species", "Human") if base_character_data else "Human"),
                    "background": character_data.get("background", base_character_data.get("background", "Folk Hero") if base_character_data else "Folk Hero"),
                    "level": character_data.get("level", base_character_data.get("level", 1) if base_character_data else 1),
                    "character_classes": character_data.get("character_classes", base_character_data.get("character_classes", {"Fighter": 1}) if base_character_data else {"Fighter": 1}),
                    "backstory": character_data.get("backstory", base_character_data.get("backstory", "") if base_character_data and request.preserve_backstory else ""),
                    "abilities": character_data.get("abilities", base_character_data.get("abilities", {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    }) if base_character_data else {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    }),
                    "armor_class": 10,
                    "hit_points": 10,
                    "proficiency_bonus": 2,
                    "skills": character_data.get("skills", base_character_data.get("skills", {}) if base_character_data else {}),
                    "equipment": character_data.get("equipment", base_character_data.get("equipment", {}) if base_character_data else {})
                }
                
                db_character = CharacterDB.create_character(db, db_character_data)
                object_id = db_character.id
                logger.info(f"Factory-evolved character saved to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save factory-evolved character to database: {e}")
                warnings.append(f"Object evolved but not saved to database: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        logger.info(f"Factory evolution completed in {processing_time:.2f}s")
        
        return FactoryResponse(
            success=True,
            creation_type=creation_type.value,
            theme=request.theme,
            object_id=object_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Factory evolution failed: {e}")
        return FactoryResponse(
            success=False,
            creation_type=request.creation_type,
            theme=request.theme,
            data={"error": str(e)},
            processing_time=processing_time
        )
