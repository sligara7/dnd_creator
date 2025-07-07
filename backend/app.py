# =========================================================================
# RETHEME CHARACTERS ENDPOINT (BULK, BRANCHING)
# =========================================================================
from pydantic import BaseModel
from fastapi import Body
from typing import List, Dict, Any, Optional

class RethemeCharactersRequest(BaseModel):
    character_ids: List[str]
    theme: str
    branch_name: Optional[str] = None  # Optional: custom branch name prefix
    description: Optional[str] = None

class RethemeCharactersResult(BaseModel):
    character_id: str
    success: bool
    new_branch_id: Optional[str] = None
    new_branch_name: Optional[str] = None
    error: Optional[str] = None

class RethemeCharactersResponse(BaseModel):
    results: List[RethemeCharactersResult]
    theme: str


import asyncio

@app.post("/api/v2/characters/retheme", response_model=RethemeCharactersResponse, tags=["characters", "theming", "versioning"])
async def retheme_characters(request: RethemeCharactersRequest = Body(...), db = Depends(get_db)):
    """
    Retheme a list of characters with a new campaign theme. Each rethemed character is saved as a new branch/version.
    Processes all characters asynchronously for performance.
    """
    factory = app.state.creation_factory
    logger.info(f"Starting retheming for {len(request.character_ids)} characters with theme '{request.theme}'")

    async def retheme_one(character_id: str) -> RethemeCharactersResult:
        try:
            # Load character
            character = CharacterDB.get_character(db, character_id)
            if not character:
                logger.warning(f"Character not found: {character_id}")
                return RethemeCharactersResult(character_id=character_id, success=False, error="Character not found")
            character_data = character.to_dict() if hasattr(character, 'to_dict') else dict(character)

            # Generate rethemed version using LLM-driven logic
            theme_prompt = f"Retheme this character for the campaign theme: '{request.theme}'. Keep core identity, but adapt all flavor, spells, equipment, and backstory to fit the new theme."
            try:
                rethemed = await factory.evolve_existing(
                    CreationOptions.CHARACTER,
                    character_data,
                    theme_prompt,
                    theme=request.theme,
                    preserve_backstory=True,
                    user_preferences={}
                )
            except Exception as e:
                logger.error(f"LLM retheming failed for {character_id}: {e}")
                return RethemeCharactersResult(character_id=character_id, success=False, error=f"LLM retheming failed: {e}")

            # Save as a new branch/version using the helper
            branch_name = request.branch_name or f"theme-{request.theme.replace(' ', '_').lower()}"
            branch_description = request.description or f"Rethemed for campaign theme: {request.theme}"
            try:
                branch_info = CharacterDB.create_theme_branch_for_character(
                    db,
                    character_id=character_id,
                    theme=request.theme,
                    branch_name=branch_name,
                    description=branch_description,
                    base_version=None
                )
                CharacterDB.save_character_sheet(db, rethemed, character_id, branch=branch_info.branch_name)
                logger.info(f"Rethemed character {character_id} saved to branch {branch_info.branch_name}")
                return RethemeCharactersResult(
                    character_id=character_id,
                    success=True,
                    new_branch_id=getattr(branch_info, 'branch_id', None),
                    new_branch_name=getattr(branch_info, 'branch_name', branch_name)
                )
            except Exception as e:
                logger.error(f"Failed to save rethemed character {character_id}: {e}")
                return RethemeCharactersResult(character_id=character_id, success=False, error=f"Branch save failed: {e}")
        except Exception as e:
            logger.error(f"Retheming failed for {character_id}: {e}")
            return RethemeCharactersResult(character_id=character_id, success=False, error=str(e))

    # Run all retheming tasks concurrently
    tasks = [retheme_one(cid) for cid in request.character_ids]
    results = await asyncio.gather(*tasks)
    logger.info(f"Retheming complete for theme '{request.theme}'. Success: {sum(1 for r in results if r.success)}, Failures: {sum(1 for r in results if not r.success)}")
    return RethemeCharactersResponse(results=results, theme=request.theme)
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

import sys
import json
import logging
import time
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pathlib import Path

# Import performance monitoring
import psutil
import os
import sys
import time
import logging
from datetime import datetime, timedelta

# Add the src directory to Python path for clean imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import configuration and services
from src.core.config import settings
from src.services.llm_service import create_llm_service

# Import database models and operations
from src.models.database_models import CharacterDB, init_database, get_db
from src.models.character_models import CharacterCore
from src.models.character_models import CharacterCore

# Import factory-based creation system
from src.services.creation_factory import CreationFactory

from src.core.enums import CreationOptions

# Unified catalog API
# from src.api.unified_catalog_api import unified_catalog_router

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

# Register unified catalog API router
# app.include_router(unified_catalog_router)

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

class FactoryCreateRequest(BaseModel):
    """Request model for factory-based creation from scratch."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    prompt: str
    theme: Optional[str] = Field(None, description="Optional campaign theme (e.g., 'western', 'cyberpunk', 'steampunk', 'horror')")
    user_preferences: Optional[Dict[str, Any]] = None
    extra_fields: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryEvolveRequest(BaseModel):
    """Request model for factory-based evolution of existing objects."""
    creation_type: str
    character_id: str
    evolution_prompt: str
    theme: Optional[str] = Field(None, description="Optional campaign theme for evolution context")
    preserve_backstory: Optional[bool] = True
    user_preferences: Optional[Dict[str, Any]] = None
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
    verbose_logs: Optional[List[Dict[str, Any]]] = None

class CharacterCreateRequest(BaseModel):
    """Character creation request."""
    name: str
    species: Optional[str] = "Human"
    background: Optional[str] = "Folk Hero"
    character_classes: Optional[Dict[str, int]] = {"Fighter": 1}
    backstory: Optional[str] = ""
    alignment: Optional[List[str]] = ["Neutral", "Good"]
    abilities: Optional[Dict[str, int]] = None

class CharacterUpdateRequest(BaseModel):
    """Character update request."""
    name: Optional[str] = None
    species: Optional[str] = None
    background: Optional[str] = None
    character_classes: Optional[Dict[str, int]] = None
    backstory: Optional[str] = None
    alignment: Optional[List[str]] = None
    abilities: Optional[Dict[str, int]] = None
    level: Optional[int] = None

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

class CharacterStateUpdateRequest(BaseModel):
    """Character state update for gameplay."""
    current_hp: Optional[int] = None
    temp_hp: Optional[int] = None
    add_condition: Optional[Dict[str, Any]] = None
    remove_condition: Optional[str] = None
    exhaustion_level: Optional[int] = None

class CharacterRestRequest(BaseModel):
    """Character rest request."""
    rest_type: str  # "short" or "long"

class CharacterVersionRequest(BaseModel):
    """Character version snapshot request."""
    version_name: str
    description: Optional[str] = None
    session_notes: Optional[str] = None

# ============================================================================
# INVENTORY MANAGEMENT MODELS
# ============================================================================

class InventoryItemRequest(BaseModel):
    """Request model for adding an item to character inventory."""
    name: str
    description: Optional[str] = None
    quantity: int = 1
    weight: Optional[float] = None
    value: Optional[float] = None  # in gold pieces
    item_type: Optional[str] = None  # "weapon", "armor", "tool", "consumable", "magic_item", etc.
    rarity: Optional[str] = None  # "common", "uncommon", "rare", "very_rare", "legendary", "artifact"
    requires_attunement: bool = False  # Whether the item can be attuned to
    attuned: bool = False  # Whether the item is currently attuned (for magical items)
    properties: Optional[Dict[str, Any]] = None  # Additional item properties

class InventoryUpdateRequest(BaseModel):
    """Request model for updating an existing inventory item."""
    quantity: Optional[int] = None
    description: Optional[str] = None
    rarity: Optional[str] = None
    requires_attunement: Optional[bool] = None
    attuned: Optional[bool] = None
    properties: Optional[Dict[str, Any]] = None

class EquipmentSlotRequest(BaseModel):
    """Request model for equipping/unequipping items."""
    item_name: str
    slot: str  # "main_hand", "off_hand", "armor", "helmet", "boots", etc.
    action: str  # "equip" or "unequip"

class InventoryResponse(BaseModel):
    """Response model for inventory operations."""
    success: bool
    message: str
    inventory: List[Dict[str, Any]]
    equipped_items: Dict[str, str]
    attuned_items: List[str]
    user_modified: Optional[bool] = False


# ============================================================================
# JOURNAL MANAGEMENT MODELS
# ============================================================================

class JournalEntryRequest(BaseModel):
    """Request model for creating journal entries."""
    title: str
    content: str
    session_date: Optional[str] = None  # ISO date string
    session_number: Optional[int] = None
    tags: Optional[List[str]] = None
    is_private: bool = False  # Whether only the character owner can see this entry
    experience_gained: Optional[int] = None
    story_beats: Optional[List[str]] = None  # Key story moments for character development

class JournalEntryUpdateRequest(BaseModel):
    """Request model for updating journal entries."""
    title: Optional[str] = None
    content: Optional[str] = None
    session_date: Optional[str] = None
    session_number: Optional[int] = None
    tags: Optional[List[str]] = None
    is_private: Optional[bool] = None
    experience_gained: Optional[int] = None
    story_beats: Optional[List[str]] = None


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



# =========================================================================
# JOURNAL MANAGEMENT ENDPOINTS (CRUD)
# =========================================================================
from pydantic import conint


# ============================================================================
# GENERIC DIRECT EDIT REQUEST MODEL
# ============================================================================
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field

class DirectEditRequest(BaseModel):
    """
    Generic request model for direct user/DM edits to any object.
    Accepts a dict of fields to update, with optional notes for audit trail.
    """
    updates: Dict[str, Any] = Field(..., description="Fields and values to update. Keys are field names, values are new values.")
    notes: Optional[str] = Field(None, description="Optional notes or reason for the manual edit.")

# =========================================================================
# XP TRACKING MODELS & ENDPOINTS (CRITICAL DEV_VISION.MD REQUIREMENT)
# =========================================================================

class XPAwardRequest(BaseModel):
    """Request model for awarding XP to a character."""
    amount: int = Field(..., gt=0)
    reason: Optional[str] = None
    journal_entry_id: Optional[str] = None  # Link to a journal entry if relevant

class XPAwardResponse(BaseModel):
    """Response model for XP award."""
    character_id: str
    new_xp_total: int
    xp_awarded: int
    level_up: bool
    new_level: Optional[int] = None
    message: str
    xp_history: Optional[list] = None
    level_up_notification: Optional[str] = None  # New: notification message if level-up occurred

class XPHistoricalEntry(BaseModel):
    """Model for a single XP award history entry."""
    id: str
    character_id: str
    amount: int
    reason: Optional[str] = None
    journal_entry_id: Optional[str] = None
    awarded_at: str
    level_up: bool = False
    new_level: Optional[int] = None

class XPHistoricalResponse(BaseModel):
    """Response model for XP award history."""
    character_id: str
    xp_history: list


# XP Award endpoint
@app.post("/api/v2/characters/{character_id}/xp", response_model=XPAwardResponse, tags=["xp"])
async def award_xp(character_id: str, xp_data: XPAwardRequest, db = Depends(get_db)):
    """Award XP to a character, with automatic level-up detection and milestone/traditional support."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Award XP using DB model (should handle both milestone/traditional)
        result = CharacterDB.award_xp(
            db,
            character_id=character_id,
            amount=xp_data.amount,
            reason=xp_data.reason,
            journal_entry_id=xp_data.journal_entry_id
        )
        # result should include: new_xp_total, level_up (bool), new_level, xp_history (optional)
        # Prepare level-up notification if level_up is True
        level_up_notification = None
        if result.get("level_up", False):
            new_level = result.get("new_level")
            level_up_notification = f"Congratulations! Character has leveled up to level {new_level}."

        return XPAwardResponse(
            character_id=character_id,
            new_xp_total=result.get("new_xp_total", 0),
            xp_awarded=xp_data.amount,
            level_up=result.get("level_up", False),
            new_level=result.get("new_level"),
            message=result.get("message", "XP awarded successfully"),
            xp_history=result.get("xp_history"),
            level_up_notification=level_up_notification
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to award XP to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"XP award failed: {str(e)}")

# XP History endpoint
@app.get("/api/v2/characters/{character_id}/xp/history", response_model=XPHistoricalResponse, tags=["xp"])
async def get_xp_history(character_id: str, db = Depends(get_db)):
    """Retrieve XP award history for a character."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        xp_history = CharacterDB.get_xp_history(db, character_id)
        # xp_history should be a list of dicts or XPHistoricalEntry
        return XPHistoricalResponse(character_id=character_id, xp_history=xp_history)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get XP history for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve XP history: {str(e)}")
from fastapi import Path

@app.get("/api/v2/characters/{character_id}/journal/{entry_id}", response_model=JournalEntryResponse, tags=["journal"])
async def get_journal_entry(character_id: str = Path(...), entry_id: str = Path(...), db = Depends(get_db)):
    """Retrieve a single journal entry by its ID."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Retrieve journal entry
        entry = CharacterDB.get_journal_entry(db, character_id, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")

        return JournalEntryResponse(**entry)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get journal entry {entry_id} for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve journal entry")



@app.put("/api/v2/characters/{character_id}/journal/{entry_id}", response_model=JournalEntryResponse, tags=["journal"])
async def update_journal_entry(
    character_id: str = Path(...),
    entry_id: str = Path(...),
    update_data: JournalEntryUpdateRequest = ...,
    db = Depends(get_db)
):
    """Update a journal entry for a character."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Ensure journal entry exists
        entry = CharacterDB.get_journal_entry(db, character_id, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")

        # Update the journal entry
        updated_entry = CharacterDB.update_journal_entry(db, character_id, entry_id, update_data.dict(exclude_unset=True))
        if not updated_entry:
            raise HTTPException(status_code=500, detail="Failed to update journal entry")

        return JournalEntryResponse(**updated_entry)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update journal entry {entry_id} for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to update journal entry")


@app.delete("/api/v2/characters/{character_id}/journal/{entry_id}", tags=["journal"])
async def delete_journal_entry(
    character_id: str = Path(...),
    entry_id: str = Path(...),
    db = Depends(get_db)
):
    """Delete a journal entry for a character."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Ensure journal entry exists
        entry = CharacterDB.get_journal_entry(db, character_id, entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")

        # Delete the journal entry
        success = CharacterDB.delete_journal_entry(db, character_id, entry_id)
        if not success:
            raise HTTPException(status_code=500, detail="Failed to delete journal entry")

        return {"message": "Journal entry deleted successfully", "entry_id": entry_id, "character_id": character_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete journal entry {entry_id} for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete journal entry")

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
        },
        "evolve_existing": {
            "supported": [
                CreationOptions.CHARACTER.value,
                CreationOptions.MONSTER.value,
                CreationOptions.NPC.value
            ],
            "description": "Evolve existing objects using their history and new prompts"
        }
    }

@app.post("/api/v2/test/mock", tags=["testing"])
async def test_mock_endpoint():
    """Test endpoint that returns static JSON to verify FastAPI is working."""
    return {
        "success": True,
        "message": "FastAPI v2 backend is working correctly",
        "timestamp": "2025-06-30T12:00:00Z",
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

# ============================================================================
# FACTORY-BASED CREATION ENDPOINTS
# ============================================================================

@app.post("/api/v2/factory/create", response_model=FactoryResponse, tags=["factory"])
async def factory_create_from_scratch(request: FactoryCreateRequest, db = Depends(get_db)):
    """
    Create D&D objects from scratch using the factory pattern.
    Supports: character, monster, npc, weapon, armor, spell, other_item
    """
    import time
    start_time = time.time()
    
    try:
        # Validate creation type
        try:
            creation_type = CreationOptions(request.creation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid creation type: {request.creation_type}")
        
        logger.info(f"Factory creating {creation_type.value} from scratch: {request.prompt[:100]}...")
        if request.theme:
            logger.info(f"Using campaign theme: {request.theme}")
        
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
                # Always convert result to dict first, regardless of type
                if isinstance(result, CharacterCore):
                    character_data = result.to_dict()
                elif hasattr(result, 'to_dict') and callable(getattr(result, 'to_dict')):
                    character_data = result.to_dict()
                else:
                    character_data = result
                
                # Ensure we have a dictionary to work with before proceeding
                if not isinstance(character_data, dict):
                    raise Exception(f"Unable to convert character data to dictionary. Got: {type(character_data)}")
                
                # Normalize the character data structure for database storage
                # Handle multiple possible data layouts from the factory
                
                # Try different possible structures from the factory response
                core_data = {}
                raw_data = {}
                
                # Option 1: Direct CharacterCore.to_dict() output
                if "name" in character_data and "species" in character_data:
                    core_data = character_data
                # Option 2: Nested structure with "core" key
                elif "core" in character_data:
                    core_obj = character_data.get("core", {})
                    
                    # Check if core_obj is a CharacterCore or dict
                    if isinstance(core_obj, dict):
                        core_data = core_obj
                    elif hasattr(core_obj, 'to_dict'):
                        # It's a CharacterCore object, convert it
                        core_data = core_obj.to_dict()
                    elif hasattr(core_obj, '__class__') and core_obj.__class__.__name__ == 'CharacterCore':
                        # Manual extraction from CharacterCore
                        core_data = {
                            "name": getattr(core_obj, 'name', 'Generated Character'),
                            "species": getattr(core_obj, 'species', 'Human'),
                            "background": getattr(core_obj, 'background', 'Folk Hero'),
                            "alignment": getattr(core_obj, 'alignment', 'Neutral Good'),
                            "level": 1,
                            "character_classes": getattr(core_obj, 'character_classes', {"Fighter": 1})
                        }
                    else:
                        core_data = {}
                # Option 3: Structure with "character" wrapper
                elif "character" in character_data:
                    character_obj = character_data["character"]
                    
                    # Check if character_obj is a CharacterCore or dict
                    if isinstance(character_obj, dict) and "core" in character_obj:
                        core_data = character_obj["core"]
                    elif hasattr(character_obj, 'to_dict'):
                        # It's a CharacterCore object, convert it
                        core_data = character_obj.to_dict()
                    elif hasattr(character_obj, '__class__') and character_obj.__class__.__name__ == 'CharacterCore':
                        # Manual extraction from CharacterCore
                        core_data = {
                            "name": getattr(character_obj, 'name', 'Generated Character'),
                            "species": getattr(character_obj, 'species', 'Human'),
                            "background": getattr(character_obj, 'background', 'Folk Hero'),
                            "alignment": getattr(character_obj, 'alignment', 'Neutral Good'),
                            "level": 1,
                            "character_classes": getattr(character_obj, 'character_classes', {"Fighter": 1})
                        }
                # Option 4: raw_data structure
                elif "raw_data" in character_data:
                    raw_data = character_data["raw_data"]
                    if isinstance(raw_data, dict) and "name" in raw_data:
                        core_data = raw_data
                
                # Extract character information for database
                if raw_data and "name" in raw_data:
                    # Use raw_data as primary source if available
                    db_character_data = {
                        "name": raw_data.get("name", "Generated Character"),
                        "species": raw_data.get("species", "Human"),
                        "background": raw_data.get("background", "Folk Hero"),
                        "alignment": raw_data.get("alignment", "Neutral Good"),
                        "level": raw_data.get("level", 1),
                        "character_classes": raw_data.get("classes", raw_data.get("character_classes", {"Fighter": 1})),
                        "backstory": raw_data.get("backstory", ""),
                        "abilities": raw_data.get("ability_scores", raw_data.get("attributes", {
                            "strength": 10, "dexterity": 10, "constitution": 10,
                            "intelligence": 10, "wisdom": 10, "charisma": 10
                        })),
                        "armor_class": 10,  # Default for now
                        "hit_points": 10,   # Default for now
                        "proficiency_bonus": 2,
                        "skills": raw_data.get("skill_proficiencies", {}),
                        "equipment": raw_data.get("equipment", {})
                    }
                elif core_data and "name" in core_data:
                    # Use core_data structure
                    db_character_data = {
                        "name": core_data.get("name", "Generated Character"),
                        "species": core_data.get("species", "Human"),
                        "background": core_data.get("background", "Folk Hero"),
                        "alignment": " ".join(core_data.get("alignment", ["Neutral", "Good"])) if isinstance(core_data.get("alignment"), list) else core_data.get("alignment", "Neutral Good"),
                        "level": core_data.get("level", 1),
                        "character_classes": core_data.get("character_classes", core_data.get("classes", {"Fighter": 1})),
                        "backstory": core_data.get("personality", {}).get("backstory", core_data.get("backstory", "")),
                        "abilities": core_data.get("ability_scores", {
                            "strength": 10, "dexterity": 10, "constitution": 10,
                            "intelligence": 10, "wisdom": 10, "charisma": 10
                        }),
                        "armor_class": 10,  # Default for now
                        "hit_points": 10,   # Default for now
                        "proficiency_bonus": 2,
                        "skills": core_data.get("proficiencies", {}).get("skills", {}),
                        "equipment": {}
                    }
                else:
                    logger.warning(f"Could not extract character data from result structure: {list(character_data.keys()) if isinstance(character_data, dict) else type(character_data)}")
                    raise Exception("Unable to extract character data from factory result")
                
                db_character = CharacterDB.create_character(db, db_character_data)
                object_id = db_character.id
                logger.info(f"Factory-created character saved to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save factory-created character to database: {e}")
                warnings.append(f"Object created but not saved to database: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data - convert CharacterCore to dict for JSON serialization
        def convert_to_serializable(obj):
            """Recursively convert objects to serializable format."""
            if isinstance(obj, CharacterCore):
                try:
                    if hasattr(obj, 'to_dict') and callable(getattr(obj, 'to_dict')):
                        return obj.to_dict()
                    else:
                        # Manual conversion for CharacterCore objects
                        return {
                            "name": getattr(obj, 'name', 'Generated Character'),
                            "species": getattr(obj, 'species', 'Human'),
                            "background": getattr(obj, 'background', 'Folk Hero'),
                            "alignment": getattr(obj, 'alignment', 'Neutral Good'),
                            "level": getattr(obj, 'level', 1),
                            "character_classes": getattr(obj, 'character_classes', {'Fighter': 1}),
                            "backstory": getattr(obj, 'backstory', ''),
                            "ability_scores": {
                                "strength": getattr(obj.strength, 'total_score', 10) if hasattr(obj, 'strength') and obj.strength else 10,
                                "dexterity": getattr(obj.dexterity, 'total_score', 10) if hasattr(obj, 'dexterity') and obj.dexterity else 10,
                                "constitution": getattr(obj.constitution, 'total_score', 10) if hasattr(obj, 'constitution') and obj.constitution else 10,
                                "intelligence": getattr(obj.intelligence, 'total_score', 10) if hasattr(obj, 'intelligence') and obj.intelligence else 10,
                                "wisdom": getattr(obj.wisdom, 'total_score', 10) if hasattr(obj, 'wisdom') and obj.wisdom else 10,
                                "charisma": getattr(obj.charisma, 'total_score', 10) if hasattr(obj, 'charisma') and obj.charisma else 10
                            },
                            "skills": getattr(obj, 'skill_proficiencies', {}),
                            "feats": getattr(obj, 'feats', []),
                            "languages": list(getattr(obj, 'languages', set())),
                            "weapon_proficiencies": list(getattr(obj, 'weapon_proficiencies', set())),
                            "armor_proficiencies": list(getattr(obj, 'armor_proficiencies', set()))
                        }
                except Exception as e:
                    logger.warning(f"Failed to convert CharacterCore manually: {e}")
                    return {"error": "CharacterCore conversion failed", "raw": str(obj)}
            elif isinstance(obj, dict):
                return {k: convert_to_serializable(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [convert_to_serializable(item) for item in obj]
            elif isinstance(obj, set):
                return list(obj)
            else:
                # For primitive types and other objects
                try:
                    # Try JSON serialization test
                    import json
                    json.dumps(obj)
                    return obj
                except (TypeError, ValueError):
                    return str(obj)
        
        try:
            response_data = convert_to_serializable(result)
            logger.info(f"Successfully converted result to serializable format")
        except Exception as e:
            logger.error(f"Failed to convert result to serializable format: {e}")
            response_data = {"error": "Failed to serialize character data", "raw_data": str(result)}
        
        logger.info(f"Factory creation completed in {processing_time:.2f}s")
        
        # Get verbose logs if available
        verbose_logs = None
        if hasattr(factory, 'last_verbose_logs') and factory.last_verbose_logs:
            verbose_logs = factory.last_verbose_logs
        
        # Track metrics for this request
        track_request_metrics("/api/v2/factory/create", processing_time, True)
        
        return FactoryResponse(
            success=True,
            creation_type=creation_type.value,
            theme=request.theme,
            object_id=object_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time,
            verbose_logs=verbose_logs
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Factory creation failed: {e}")
        # Track metrics for this request
        track_request_metrics("/api/v2/factory/create", processing_time, False)
        return FactoryResponse(
            success=False,
            creation_type=request.creation_type,
            theme=request.theme,
            data={"error": str(e)},
            processing_time=processing_time
        )

@app.post("/api/v2/factory/evolve", response_model=FactoryResponse, tags=["factory"])
async def factory_evolve_existing(request: FactoryEvolveRequest, db = Depends(get_db)):
    """Evolve existing D&D objects using their history and new prompts."""
    import time
    start_time = time.time()
    
    try:
        # Validate creation type
        try:
            creation_type = CreationOptions(request.creation_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid creation type: {request.creation_type}")
        
        if creation_type not in [CreationOptions.CHARACTER, CreationOptions.MONSTER, CreationOptions.NPC]:
            raise HTTPException(status_code=400, detail=f"Evolution not supported for: {creation_type.value}")
        
        logger.info(f"Factory evolving {creation_type.value} ID {request.character_id}: {request.evolution_prompt[:100]}...")
        
        # Load existing object from database
        if creation_type == CreationOptions.CHARACTER:
            existing_character = CharacterDB.get_character(db, request.character_id)
            if not existing_character:
                raise HTTPException(status_code=404, detail="Character not found")
            existing_data = existing_character.to_dict()
        else:
            # For monsters/NPCs, implement similar loading logic when available
            raise HTTPException(status_code=501, detail=f"Evolution for {creation_type.value} not yet implemented")
        
        # Use the factory to evolve the object
        factory = app.state.creation_factory
        result = await factory.evolve_existing(
            creation_type,
            existing_data,
            request.evolution_prompt,
            theme=request.theme,
            preserve_backstory=request.preserve_backstory,
            user_preferences=request.user_preferences or {}
        )
        
        object_id = request.character_id
        warnings = []
        
        # Save evolved object back to database if requested
        if request.save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                CharacterDB.save_character_sheet(db, result, request.character_id)
                logger.info(f"Evolved character saved back to database")
            except Exception as e:
                logger.warning(f"Failed to save evolved character: {e}")
                warnings.append(f"Evolution completed but not saved: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        logger.info(f"Factory evolution completed in {processing_time:.2f}s")
        
        # Track metrics for this request
        track_request_metrics("/api/v2/factory/evolve", processing_time, True)
        
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
        # Track metrics for this request
        track_request_metrics("/api/v2/factory/evolve", processing_time, False)
        return FactoryResponse(
            success=False,
            creation_type=request.creation_type,
            theme=request.theme,
            data={"error": str(e)},
            processing_time=processing_time
        )

# ============================================================================
# CHARACTER MANAGEMENT ENDPOINTS
# ============================================================================

@app.post("/api/v2/characters", response_model=CharacterResponse, tags=["characters"])
async def create_character(character_data: CharacterCreateRequest, db = Depends(get_db)):
    """Create a new character directly (non-LLM path)."""
    try:
        # Set default abilities if not provided
        abilities = character_data.abilities or {
            "strength": 10, "dexterity": 10, "constitution": 10,
            "intelligence": 10, "wisdom": 10, "charisma": 10
        }
        
        # Calculate total level
        total_level = sum(character_data.character_classes.values()) if character_data.character_classes else 1
        
        db_character_data = {
            "name": character_data.name,
            "species": character_data.species,
            "background": character_data.background,
            "alignment": " ".join(character_data.alignment),
            "level": total_level,
            "character_classes": character_data.character_classes,
            "backstory": character_data.backstory,
            "abilities": abilities,
            "armor_class": 10,  # Default AC
            "hit_points": 8 + abilities.get("constitution", 10) - 10,  # Basic HP calculation
            "proficiency_bonus": 2,  # Level 1 default
            "skills": {},
            "equipment": {}
        }
        
        db_character = CharacterDB.create_character(db, db_character_data)
        
        return CharacterResponse(
            id=db_character.id,
            name=db_character.name,
            species=db_character.species,
            background=db_character.background,
            level=db_character.level,
            character_classes=db_character.character_classes,
            backstory=db_character.backstory,
            created_at=db_character.created_at.isoformat()
        )
        
    except Exception as e:
        logger.error(f"Failed to create character: {e}")
        raise HTTPException(status_code=500, detail=f"Character creation failed: {str(e)}")

@app.get("/api/v2/characters", response_model=List[CharacterResponse], tags=["characters"])
async def list_characters(db = Depends(get_db)):
    """List all characters."""
    try:
        characters = CharacterDB.list_characters(db)
        return [
            CharacterResponse(
                id=char.id,
                name=char.name,
                species=char.species,
                background=char.background,
                level=char.level,
                character_classes=char.character_classes,
                backstory=char.backstory,
                created_at=char.created_at.isoformat()
            )
            for char in characters
        ]
    except Exception as e:
        logger.error(f"Failed to list characters: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve characters")

@app.get("/api/v2/characters/{character_id}", response_model=CharacterResponse, tags=["characters"])
async def get_character(character_id: str, db = Depends(get_db)):
    """Get a specific character by ID."""
    try:
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
            created_at=character.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character")

@app.put("/api/v2/characters/{character_id}", response_model=CharacterResponse, tags=["characters"])
async def update_character(character_id: str, character_data: CharacterUpdateRequest, db = Depends(get_db)):
    """Update an existing character."""
    try:
        # Load existing character
        existing_character = CharacterDB.get_character(db, character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Update fields that are provided
        update_data = {}
        if character_data.name is not None:
            update_data["name"] = character_data.name
        if character_data.species is not None:
            update_data["species"] = character_data.species
        if character_data.background is not None:
            update_data["background"] = character_data.background
        if character_data.character_classes is not None:
            update_data["character_classes"] = character_data.character_classes
            update_data["level"] = sum(character_data.character_classes.values())
        if character_data.backstory is not None:
            update_data["backstory"] = character_data.backstory
        if character_data.alignment is not None:
            update_data["alignment"] = " ".join(character_data.alignment)
        if character_data.abilities is not None:
            update_data["abilities"] = character_data.abilities
        if character_data.level is not None:
            update_data["level"] = character_data.level
        
        # Update character in database
        updated_character = CharacterDB.update_character(db, character_id, update_data)
        if not updated_character:
            raise HTTPException(status_code=500, detail="Failed to update character")
        
        return CharacterResponse(
            id=updated_character.id,
            name=updated_character.name,
            species=updated_character.species,
            background=updated_character.background,
            level=updated_character.level,
            character_classes=updated_character.character_classes,
            backstory=updated_character.backstory,
            created_at=updated_character.created_at.isoformat()
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Character update failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/sheet", tags=["characters"])
async def get_character_sheet(character_id: str, db = Depends(get_db)):
    """Get complete character sheet with all details."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character_sheet.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character sheet {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character sheet")

@app.delete("/api/v2/characters/{character_id}", tags=["characters"])
async def delete_character(character_id: str, db = Depends(get_db)):
    """Delete a character."""
    try:
        result = CharacterDB.delete_character(db, character_id)
        if not result:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return {"message": "Character deleted successfully", "character_id": character_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete character")

# ============================================================================
# REAL-TIME GAMEPLAY ENDPOINTS
# ============================================================================

@app.put("/api/v2/characters/{character_id}/state", tags=["gameplay"])
async def update_character_state(character_id: str, state_updates: CharacterStateUpdateRequest, db = Depends(get_db)):
    """Update character state for in-game play."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply state updates
        if state_updates.current_hp is not None:
            character_sheet.state.current_hp = state_updates.current_hp
        if state_updates.temp_hp is not None:
            character_sheet.state.temp_hp = state_updates.temp_hp
        if state_updates.exhaustion_level is not None:
            character_sheet.state.exhaustion_level = state_updates.exhaustion_level
        
        # Handle conditions
        if state_updates.add_condition:
            condition_name = state_updates.add_condition.get("condition")
            if condition_name:
                character_sheet.state.add_condition(condition_name)
        
        if state_updates.remove_condition:
            character_sheet.state.remove_condition(state_updates.remove_condition)
        
        # Save updated state back to database
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Updated character state for ID {character_id}")
        return {
            "message": "Character state updated successfully",
            "character_id": character_id,
            "current_state": character_sheet.state.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character state {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"State update failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/state", tags=["gameplay"])
async def get_character_state(character_id: str, db = Depends(get_db)):
    """Get real-time character state snapshot."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character_sheet.state.to_dict()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character state {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character state")

@app.post("/api/v2/characters/{character_id}/combat", tags=["gameplay"])
async def apply_combat_effects(character_id: str, combat_data: Dict[str, Any], db = Depends(get_db)):
    """Apply combat round effects to character."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply combat effects
        action = combat_data.get("action")
        if action == "take_damage":
            damage = combat_data.get("damage", 0)
            current_hp = getattr(character_sheet.state, 'current_hp', 100)
            character_sheet.state.current_hp = max(0, current_hp - damage)
        elif action == "heal":
            healing = combat_data.get("healing", 0)
            current_hp = getattr(character_sheet.state, 'current_hp', 100)
            max_hp = getattr(character_sheet.state, 'max_hit_points', 100)
            character_sheet.state.current_hp = min(max_hp, current_hp + healing)
        elif action == "add_condition":
            condition = combat_data.get("condition")
            if condition:
                character_sheet.state.add_condition(condition)
        elif action == "remove_condition":
            condition = combat_data.get("condition")
            if condition:
                character_sheet.state.remove_condition(condition)
        
        # Save updated state
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Applied combat effects to character {character_id}")
        return {
            "message": "Combat effects applied successfully",
            "character_id": character_id,
            "action_applied": action,
            "current_state": character_sheet.state.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply combat effects to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Combat effects failed: {str(e)}")

@app.post("/api/v2/characters/{character_id}/rest", tags=["gameplay"])
async def apply_rest_effects(character_id: str, rest_data: CharacterRestRequest, db = Depends(get_db)):
    """Apply rest effects to character."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        rest_type = rest_data.rest_type
        rest_result = {}
        
        if rest_type == "short":
            # Short rest: partial healing, some abilities restored
            max_hp = getattr(character_sheet.state, 'max_hit_points', 100)
            current_hp = getattr(character_sheet.state, 'current_hp', max_hp)
            healing = max_hp // 4  # Heal 1/4 of max HP on short rest
            character_sheet.state.current_hp = min(max_hp, current_hp + healing)
            
            rest_result = {
                "rest_type": "short",
                "hp_healed": healing,
                "new_hp": character_sheet.state.current_hp,
                "max_hp": max_hp
            }
            
        elif rest_type == "long":
            # Long rest: full HP recovery, spell slots, abilities reset
            max_hp = getattr(character_sheet.state, 'max_hit_points', 100)
            character_sheet.state.current_hp = max_hp
            
            # Clear exhaustion (reduce by 1 level)
            if hasattr(character_sheet.state, 'exhaustion_level'):
                character_sheet.state.exhaustion_level = max(0, character_sheet.state.exhaustion_level - 1)
            
            # Remove certain conditions (simplified - remove all temporary conditions)
            if hasattr(character_sheet.state, 'conditions') and isinstance(character_sheet.state.conditions, list):
                # Keep only permanent conditions
                character_sheet.state.conditions = [c for c in character_sheet.state.conditions if c.get('permanent', False)]
            
            rest_result = {
                "rest_type": "long",
                "hp_restored": True,
                "new_hp": max_hp,
                "max_hp": max_hp,
                "exhaustion_reduced": True,
                "conditions_cleared": True
            }
        
        # Save updated state
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Applied {rest_type} rest to character {character_id}")
        return {
            "message": f"{rest_type.capitalize()} rest completed successfully",
            "character_id": character_id,
            "rest_result": rest_result,
            "current_state": character_sheet.state.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply rest to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Rest failed: {str(e)}")

# ============================================================================
# CHARACTER VALIDATION ENDPOINTS
# ============================================================================

@app.post("/api/v2/validate/character", tags=["validation"])
async def validate_character(character_data: CharacterCreateRequest):
    """Validate a character's build for D&D 5e compliance using creation_validation.py."""
    try:
        # Convert request to validation format
        validation_data = {
            "name": character_data.name,
            "species": character_data.species,
            "background": character_data.background,
            "level": 1,  # Default for new character
            "classes": character_data.character_classes,
            "ability_scores": character_data.abilities or {},
            "backstory": character_data.backstory
        }
        
        # Use creation_validation.py for validation
        from src.services.creation_validation import validate_basic_structure
        validation_result = validate_basic_structure(validation_data)
        
        return {
            "valid": validation_result.success,
            "issues": [validation_result.error] if validation_result.error else [],
            "warnings": validation_result.warnings,
            "character_name": character_data.name
        }
        
    except Exception as e:
        logger.error(f"Character validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/validate", tags=["validation"])
async def validate_existing_character(character_id: str, db = Depends(get_db)):
    """Validate an existing character from the database using creation_validation.py."""
    try:
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Convert character to dict format for validation
        character_data = {
            "name": character.name,
            "species": character.species,
            "background": character.background,
            "level": character.level if hasattr(character, 'level') else 1,
            "classes": character.character_classes,
            "ability_scores": getattr(character, 'ability_scores', {}),
            "backstory": character.backstory
        }
        
        # Use creation_validation.py for validation
        from src.services.creation_validation import validate_basic_structure
        validation_result = validate_basic_structure(character_data)
        
        return {
            "character_id": character_id,
            "character_name": character.name,
            "valid": validation_result.success,
            "issues": [validation_result.error] if validation_result.error else [],
            "warnings": validation_result.warnings
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Character validation failed for ID {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


# ============================================================================
# SIMPLIFIED CHARACTER VERSIONING ENDPOINTS
# ============================================================================

@app.post("/api/v2/characters/{character_id}/versions", tags=["versioning"])
async def create_character_version(character_id: str, version_data: CharacterVersionRequest, db = Depends(get_db)):
    """Create a character version snapshot (simplified versioning)."""
    try:
        # Load current character
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Get full character sheet
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        
        # Create version snapshot
        version_snapshot = {
            "version_name": version_data.version_name,
            "description": version_data.description,
            "session_notes": version_data.session_notes,
            "character_data": character_sheet.to_dict() if character_sheet else character.to_dict(),
            "created_at": "2025-06-30T12:00:00Z",  # Would use actual timestamp
            "character_level": character.level
        }
        
        # In a real implementation, you'd save this to a versions table
        # For now, return the snapshot
        
        logger.info(f"Created version snapshot '{version_data.version_name}' for character {character_id}")
        return {
            "message": "Character version created successfully",
            "character_id": character_id,
            "version": version_snapshot
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create character version {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Version creation failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/versions", tags=["versioning"])
async def list_character_versions(character_id: str, db = Depends(get_db)):
    """List all versions of a character (simplified versioning)."""
    try:
        # Verify character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # In a real implementation, you'd query a versions table
        # For now, return a mock response
        versions = [
            {
                "version_name": "Initial Creation",
                "description": "Character first created",
                "created_at": character.created_at.isoformat(),
                "character_level": 1
            },
            {
                "version_name": "Current",
                "description": "Current character state",
                "created_at": character.updated_at.isoformat() if hasattr(character, 'updated_at') else character.created_at.isoformat(),
                "character_level": character.level
            }
        ]
        
        return {
            "character_id": character_id,
            "character_name": character.name,
            "versions": versions
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list character versions {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character versions")



# ============================================================================
# ADVANCED CHARACTER BRANCHING ENDPOINTS (GIT-LIKE)
# ============================================================================

class CharacterBranchCreateRequest(BaseModel):
    """Request model for creating a new character branch."""
    branch_name: str
    base_version: Optional[str] = None  # Optional: which version/branch to branch from
    description: Optional[str] = None

class CharacterBranchResponse(BaseModel):
    """Response model for character branch creation."""
    branch_id: str
    branch_name: str
    base_version: Optional[str] = None
    description: Optional[str] = None
    created_at: str
    character_id: str

class CharacterBranchListResponse(BaseModel):
    """Response model for listing character branches."""
    character_id: str
    branches: list

class CharacterBranchMergeRequest(BaseModel):
    """Request model for merging two character branches."""
    source_branch_id: str
    target_branch_id: str
    merge_strategy: Optional[str] = "manual"  # e.g., "manual", "ours", "theirs"
    message: Optional[str] = None

class CharacterBranchMergeResponse(BaseModel):
    """Response model for branch merge operation."""
    success: bool
    message: str
    merged_branch_id: Optional[str] = None
    conflicts: Optional[list] = None

class CharacterBranchApprovalRequest(BaseModel):
    """Request model for branch approval workflow."""
    branch_id: str
    approved: bool
    reviewer: Optional[str] = None
    comments: Optional[str] = None

class CharacterBranchApprovalResponse(BaseModel):
    """Response model for branch approval workflow."""
    branch_id: str
    approved: bool
    reviewer: Optional[str] = None
    comments: Optional[str] = None
    message: str

@app.post("/api/v2/characters/{character_id}/branches", response_model=CharacterBranchResponse, tags=["versioning"])
async def create_character_branch(character_id: str, branch_data: CharacterBranchCreateRequest, db = Depends(get_db)):
    """Create a new branch for a character (advanced versioning)."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Create the branch using the database model
        branch = CharacterDB.create_branch(
            db,
            character_id=character_id,
            branch_name=branch_data.branch_name,
            base_version=branch_data.base_version,
            description=branch_data.description
        )
        if not branch:
            raise HTTPException(status_code=500, detail="Failed to create branch")

        return CharacterBranchResponse(
            branch_id=branch.id,
            branch_name=branch.branch_name,
            base_version=branch.base_version,
            description=branch.description,
            created_at=branch.created_at.isoformat() if hasattr(branch, 'created_at') else "",
            character_id=character_id
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to create branch for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Branch creation failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/branches", response_model=CharacterBranchListResponse, tags=["versioning"])
async def list_character_branches(character_id: str, db = Depends(get_db)):
    """List all branches for a character (advanced versioning)."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Retrieve all branches for this character
        branches = CharacterDB.list_branches(db, character_id)
        # Convert to dicts if needed
        branch_dicts = [
            {
                "branch_id": b.id,
                "branch_name": b.branch_name,
                "base_version": getattr(b, 'base_version', None),
                "description": getattr(b, 'description', None),
                "created_at": b.created_at.isoformat() if hasattr(b, 'created_at') else "",
                "character_id": character_id
            }
            for b in branches
        ]
        return CharacterBranchListResponse(character_id=character_id, branches=branch_dicts)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to list branches for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list branches: {str(e)}")

@app.post("/api/v2/characters/{character_id}/branches/merge", response_model=CharacterBranchMergeResponse, tags=["versioning"])
async def merge_character_branches(character_id: str, merge_data: CharacterBranchMergeRequest, db = Depends(get_db)):
    """Merge two character branches (advanced versioning)."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Perform the merge using the database model
        merge_result = CharacterDB.merge_branches(
            db,
            character_id=character_id,
            source_branch_id=merge_data.source_branch_id,
            target_branch_id=merge_data.target_branch_id,
            merge_strategy=merge_data.merge_strategy,
            message=merge_data.message
        )
        if not merge_result.get("success", False):
            return CharacterBranchMergeResponse(
                success=False,
                message=merge_result.get("message", "Merge failed"),
                merged_branch_id=None,
                conflicts=merge_result.get("conflicts")
            )
        return CharacterBranchMergeResponse(
            success=True,
            message=merge_result.get("message", "Merge successful"),
            merged_branch_id=merge_result.get("merged_branch_id"),
            conflicts=merge_result.get("conflicts")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to merge branches for character {character_id}: {e}")
        return CharacterBranchMergeResponse(success=False, message=f"Merge failed: {str(e)}")

@app.post("/api/v2/characters/{character_id}/branches/approve", response_model=CharacterBranchApprovalResponse, tags=["versioning"])
async def approve_character_branch(character_id: str, approval_data: CharacterBranchApprovalRequest, db = Depends(get_db)):
    """Approve or reject a character branch (approval workflow)."""
    try:
        # Ensure character exists
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")

        # Perform the approval using the database model
        approval_result = CharacterDB.approve_branch(
            db,
            character_id=character_id,
            branch_id=approval_data.branch_id,
            approved=approval_data.approved,
            reviewer=approval_data.reviewer,
            comments=approval_data.comments
        )
        if not approval_result.get("success", False):
            return CharacterBranchApprovalResponse(
                branch_id=approval_data.branch_id,
                approved=approval_data.approved,
                reviewer=approval_data.reviewer,
                comments=approval_data.comments,
                message=approval_result.get("message", "Approval failed")
            )
        return CharacterBranchApprovalResponse(
            branch_id=approval_data.branch_id,
            approved=approval_data.approved,
            reviewer=approval_data.reviewer,
            comments=approval_data.comments,
            message=approval_result.get("message", "Approval successful")
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to approve branch for character {character_id}: {e}")
        return CharacterBranchApprovalResponse(
            branch_id=approval_data.branch_id,
            approved=approval_data.approved,
            reviewer=approval_data.reviewer,
            comments=approval_data.comments,
            message=f"Approval failed: {str(e)}"
        )

# ============================================================================
# INVENTORY MANAGEMENT ENDPOINTS
# ============================================================================

@app.get("/api/v2/characters/{character_id}/inventory", response_model=InventoryResponse, tags=["inventory"])
async def get_character_inventory(character_id: str, db = Depends(get_db)):
    """Get character's current inventory, equipped items, and attuned items."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return InventoryResponse(
            success=True,
            message="Inventory retrieved successfully",
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except Exception as e:
        logger.error(f"Failed to get inventory for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Get inventory failed: {str(e)}")

@app.post("/api/v2/characters/{character_id}/inventory/items", response_model=InventoryResponse, tags=["inventory"])
async def add_inventory_item(character_id: str, item_data: InventoryItemRequest, db = Depends(get_db)):
    """Add an item to character inventory."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Add item to inventory
        CharacterDB.add_inventory_item(db, character_id, item_data.dict())
        
        return InventoryResponse(
            success=True,
            message="Item added to inventory",
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except Exception as e:
        logger.error(f"Failed to add inventory item to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Add inventory item failed: {str(e)}")

@app.put("/api/v2/characters/{character_id}/inventory/items/{item_name}", response_model=InventoryResponse, tags=["inventory"])
async def update_inventory_item(character_id: str, item_name: str, item_data: InventoryUpdateRequest, db = Depends(get_db)):
    """Update an existing inventory item."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Update item in inventory
        CharacterDB.update_inventory_item(db, character_id, item_name, item_data.dict())
        
        return InventoryResponse(
            success=True,
            message="Inventory item updated",
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except Exception as e:
        logger.error(f"Failed to update inventory item for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Update inventory item failed: {str(e)}")

@app.delete("/api/v2/characters/{character_id}/inventory/items/{item_name}", response_model=InventoryResponse, tags=["inventory"])
async def delete_inventory_item(character_id: str, item_name: str, db = Depends(get_db)):
    """Remove an item from character inventory."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Remove item from inventory
        CharacterDB.remove_inventory_item(db, character_id, item_name)
        
        return InventoryResponse(
            success=True,
            message="Item removed from inventory",
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except Exception as e:
        logger.error(f"Failed to remove inventory item from character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Remove inventory item failed: {str(e)}")

@app.post("/api/v2/characters/{character_id}/inventory/equip", response_model=InventoryResponse, tags=["inventory"])
async def equip_inventory_item(character_id: str, slot_data: EquipmentSlotRequest, db = Depends(get_db)):
    """Equip an item from inventory to a character's equipment slot."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Equip or unequip item
        if slot_data.action == "equip":
            CharacterDB.equip_item(db, character_id, slot_data.item_name, slot_data.slot)
        elif slot_data.action == "unequip":
            CharacterDB.unequip_item(db, character_id, slot_data.item_name, slot_data.slot)
        else:
            raise HTTPException(status_code=400, detail="Invalid action, must be 'equip' or 'unequip'")
        
        return InventoryResponse(
            success=True,
            message=f"Item {slot_data.action}ped successfully",
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except Exception as e:
        logger.error(f"Failed to equip/unequip item for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Equip/unequip item failed: {str(e)}")

@app.post("/api/v2/characters/{character_id}/inventory/attune", response_model=InventoryResponse, tags=["inventory"])
async def attune_item(character_id: str, item_name: str = Query(...), action: str = Query(...), db = Depends(get_db)):
    """Attune or unattune a magical item (max 3 attuned items)."""
    try:
        # Load character to ensure they exist
        character = CharacterDB.get_character(db, character_id)
        if not character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        if action == "attune":
            # Get detailed attunement info for better error messages
            attunement_info = CharacterDB.get_attunement_info(db, character_id)
            
            if attunement_info["attunement_slots_used"] >= 3:
                attuned_list = [item["name"] for item in attunement_info["attuned_items"]]
                raise HTTPException(
                    status_code=400, 
                    detail=f"Cannot attune to {item_name}: Character already has 3 attuned items (D&D 5e limit). Currently attuned: {', '.join(attuned_list)}"
                )
            
            # Check if item exists and requires attunement
            item_requires_attunement = False
            for item in attunement_info.get("attuneable_items", []):
                if item["name"] == item_name:
                    item_requires_attunement = True
                    break
            
            # Check if already attuned
            for item in attunement_info.get("attuned_items", []):
                if item["name"] == item_name:
                    raise HTTPException(status_code=400, detail=f"Character is already attuned to {item_name}")
            
            if not item_requires_attunement:
                # Check if item exists but doesn't require attunement
                item_exists = False
                for item in attunement_info.get("non_attuneable_items", []):
                    if item["name"] == item_name:
                        item_exists = True
                        break
                
                if item_exists:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Cannot attune to {item_name}: This item does not require attunement"
                    )
                else:
                    raise HTTPException(
                        status_code=404, 
                        detail=f"Item {item_name} not found in character's inventory"
                    )
            
            success = CharacterDB.add_attuned_item(db, character_id, item_name)
            if not success:
                raise HTTPException(status_code=400, detail=f"Failed to attune to {item_name}")
            message = f"Successfully attuned to {item_name}"
        elif action == "unattune":
            success = CharacterDB.remove_attuned_item(db, character_id, item_name)
            if not success:
                raise HTTPException(status_code=400, detail="Item not currently attuned")
            message = f"Unattuned from {item_name}"
        else:
            raise HTTPException(status_code=400, detail="Invalid action, must be 'attune' or 'unattune'")
        
        return InventoryResponse(
            success=True,
            message=message,
            inventory=CharacterDB.get_inventory(db, character_id),
            equipped_items=CharacterDB.get_equipped_items(db, character_id),
            attuned_items=CharacterDB.get_attuned_items(db, character_id)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to attune/unattune item for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Attune/unattune item failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/inventory/attunement", tags=["inventory"])
async def get_attunement_status(character_id: str, db = Depends(get_db)):
    """Get character's attunement status and available slots with D&D 5e rules."""
    try:
        attunement_info = CharacterDB.get_attunement_info(db, character_id)
        
        if "error" in attunement_info:
            raise HTTPException(status_code=404, detail=attunement_info["error"])
        
        return {
            "success": True,
            **attunement_info
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get attunement status for character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Get attunement status failed: {str(e)}")

# ============================================================================
# ITERATIVE REFINEMENT ENDPOINTS - CRITICAL DEV_VISION.MD REQUIREMENT
# ============================================================================

class CharacterRefinementRequest(BaseModel):
    """Request model for iterative character refinement."""
    refinement_prompt: str
    user_preferences: Optional[Dict[str, Any]] = None

class CharacterFeedbackRequest(BaseModel):
    """Request model for structured character feedback."""
    change_type: str  # "modify_ability", "change_class", "add_feat", "modify_equipment", "change_spells"
    target: str       # What to change (ability name, class name, item name, etc.)
    new_value: str    # New value to set
    reason: Optional[str] = None  # User explanation for change

class CharacterLevelUpRequest(BaseModel):
    """Request model for character level-up."""
    new_level: int
    multiclass_option: Optional[str] = None
    journal_entries: Optional[List[str]] = None
    story_reason: Optional[str] = None
    context: Optional[str] = None

@app.post("/api/v2/characters/{character_id}/refine", response_model=FactoryResponse, tags=["iterative-refinement"])
async def refine_character(character_id: str, request: CharacterRefinementRequest, db = Depends(get_db)):
    """
    Apply iterative refinements to a character while maintaining consistency.
    Critical dev_vision.md requirement for collaborative character development.
    """
    import time
    start_time = time.time()
    
    try:
        # Load existing character
        existing_character = CharacterDB.get_character(db, character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Convert to dict format
        character_data = existing_character.to_dict()
        
        logger.info(f"Refining character {character_id}: {request.refinement_prompt[:100]}...")
        
        # Use the factory to refine the character
        factory = app.state.creation_factory
        result = await factory.evolve_existing(
            CreationOptions.CHARACTER,
            character_data,
            request.refinement_prompt,
            evolution_type='refine',
            user_preferences=request.user_preferences or {}
        )
        
        # Save refined character back to database
        warnings = []
        try:
            CharacterDB.save_character_sheet(db, result, character_id)
            logger.info(f"Refined character saved back to database")
        except Exception as e:
            logger.warning(f"Failed to save refined character: {e}")
            warnings.append(f"Refinement completed but not saved: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        logger.info(f"Character refinement completed in {processing_time:.2f}s")
        
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/refine", processing_time, True)
        
        return FactoryResponse(
            success=True,
            creation_type="character",
            object_id=character_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Character refinement failed: {e}")
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/refine", processing_time, False)
        return FactoryResponse(
            success=False,
            creation_type="character",
            data={"error": str(e)},
            processing_time=processing_time
        )

@app.post("/api/v2/characters/{character_id}/feedback", response_model=FactoryResponse, tags=["iterative-refinement"])
async def apply_character_feedback(character_id: str, request: CharacterFeedbackRequest, db = Depends(get_db)):
    """
    Apply structured user feedback to character (targeted changes).
    Supports specific changes like ability scores, class changes, feat additions, etc.
    """
    import time
    start_time = time.time()
    
    try:
        # Load existing character
        existing_character = CharacterDB.get_character(db, character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Convert to dict format
        character_data = existing_character.to_dict()
        
        logger.info(f"Applying feedback to character {character_id}: {request.change_type}")
        
        # Apply feedback using CharacterCreator
        from creation import CharacterCreator
        creator = CharacterCreator(app.state.llm_service)
        
        feedback_data = {
            "change_type": request.change_type,
            "target": request.target,
            "new_value": request.new_value,
            "reason": request.reason or "User requested change"
        }
        
        result = await creator.apply_user_feedback(character_data, feedback_data)
        
        if not result.success:
            raise Exception(result.error)
        
        # Save updated character back to database
        warnings = result.warnings or []
        try:
            CharacterDB.save_character_sheet(db, result.data, character_id)
            logger.info(f"Character feedback applied and saved to database")
        except Exception as e:
            logger.warning(f"Failed to save character with feedback: {e}")
            warnings.append(f"Feedback applied but not saved: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        response_data = result.data.to_dict() if hasattr(result.data, 'to_dict') else result.data
        
        logger.info(f"Character feedback completed in {processing_time:.2f}s")
        
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/feedback", processing_time, True)
        
        return FactoryResponse(
            success=True,
            creation_type="character",
            object_id=character_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Character feedback failed: {e}")
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/feedback", processing_time, False)
        return FactoryResponse(
            success=False,
            creation_type="character",
            data={"error": str(e)},
            processing_time=processing_time
        )

@app.post("/api/v2/characters/{character_id}/level-up", response_model=FactoryResponse, tags=["character-advancement"])
async def level_up_character_with_journal(character_id: str, request: CharacterLevelUpRequest, db = Depends(get_db)):
    """
    Level up character using journal entries as context for advancement decisions.
    Critical dev_vision.md requirement for character advancement based on play experience.
    """
    import time
    start_time = time.time()
    
    try:
        # Load existing character
        existing_character = CharacterDB.get_character(db, character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Convert to dict format
        character_data = existing_character.to_dict()
        current_level = character_data.get('level', 1)
        
        # Validate level progression
        if request.new_level <= current_level:
            raise HTTPException(status_code=400, detail=f"New level ({request.new_level}) must be higher than current level ({current_level})")
        
        if request.new_level > current_level + 1:
            raise HTTPException(status_code=400, detail="Can only level up one level at a time")
        
        logger.info(f"Leveling up character {character_id} from {current_level} to {request.new_level}")
        
        # Use the factory to level up the character
        factory = app.state.creation_factory
        level_info = {
            "new_level": request.new_level,
            "multiclass": request.multiclass_option,
            "journal_entries": request.journal_entries or [],
            "story_reason": request.story_reason,
            "context": request.context
        }
        
        from creation_factory import level_up_character
        result = await level_up_character(character_data, level_info, app.state.llm_service)
        
        # Save leveled character back to database
        warnings = [f"Character leveled up from {current_level} to {request.new_level}"]
        if request.multiclass_option:
            warnings.append(f"Added multiclass: {request.multiclass_option}")
        
        try:
            CharacterDB.save_character_sheet(db, result, character_id)
            logger.info(f"Leveled character saved back to database")
        except Exception as e:
            logger.warning(f"Failed to save leveled character: {e}")
            warnings.append(f"Level-up completed but not saved: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        response_data = result.to_dict() if hasattr(result, 'to_dict') else result
        
        logger.info(f"Character level-up completed in {processing_time:.2f}s")
        
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/level-up", processing_time, True)
        
        return FactoryResponse(
            success=True,
            creation_type="character",
            object_id=character_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Character level-up failed: {e}")
        # Track metrics for this request
        track_request_metrics("/api/v2/characters/{character_id}/level-up", processing_time, False)
        return FactoryResponse(
            success=False,
            creation_type="character",
            data={"error": str(e)},
            processing_time=processing_time
        )

@app.get("/api/v2/characters/{character_id}/level-up/suggestions", tags=["character-advancement"])
async def get_level_up_suggestions(character_id: str, journal_entries: List[str] = Query(default=[]), db = Depends(get_db)):
    """
    Get level-up suggestions based on character
    """
