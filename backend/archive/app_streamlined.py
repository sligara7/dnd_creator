"""
FastAPI main application for D&D Character Creator - STREAMLINED VERSION.

🏛️ STREAMLINED FACTORY-BASED ARCHITECTURE:
- Unified v2 factory pattern for all content creation
- Simplified endpoint structure focused on core functionality
- Removed legacy v1 endpoints and redundant code
- Clean separation between factory creation and character management

CORE ENDPOINTS:
- Health check and factory creation types
- Factory-based content creation (v2)
- Essential character CRUD operations
- Real-time character state management for gameplay

This streamlined version removes:
- All v1 generation endpoints (replaced by v2 factory)
- Complex character versioning system (can be re-added later)
- Redundant validation endpoints
- Duplicate functionality between v1/v2
"""

import sys
import json
import logging
from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import configuration and services
from config import settings
from llm_service import create_llm_service

# Import database models and operations
from database_models import CharacterDB, init_database, get_db
from character_models import CharacterCore, CharacterSheet

# Import factory-based creation system
from creation_factory import CreationFactory
from enums import CreationOptions

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize services on startup, cleanup on shutdown."""
    try:
        # Initialize database
        init_database()
        logger.info("Database initialized successfully")
        
        # Initialize LLM service
        llm_service = await create_llm_service()
        app.state.llm_service = llm_service
        logger.info("LLM service initialized successfully")
        
        # Initialize creation factory
        creation_factory = CreationFactory(llm_service)
        app.state.creation_factory = creation_factory
        logger.info("Creation factory initialized successfully")
        
        logger.info("🚀 D&D Character Creator API started successfully!")
        yield
        
    except Exception as e:
        logger.error(f"Failed to initialize services: {e}")
        raise
    finally:
        logger.info("Shutting down D&D Character Creator API")

# Initialize FastAPI app
app = FastAPI(
    title="D&D Character Creator API - Streamlined",
    description="Factory-based D&D 5e Character Management System",
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

class FactoryCreateRequest(BaseModel):
    """Request model for factory-based creation from scratch."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    prompt: str
    user_preferences: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryResponse(BaseModel):
    """Response model for factory operations."""
    success: bool
    creation_type: str
    object_id: Optional[str] = None  # ID if saved to database
    data: Dict[str, Any]
    warnings: Optional[List[str]] = None
    processing_time: Optional[float] = None
    verbose_logs: Optional[List[Dict[str, Any]]] = None

class CharacterCreateRequest(BaseModel):
    """Simple character creation request."""
    name: str
    species: Optional[str] = "Human"
    background: Optional[str] = "Folk Hero"
    character_classes: Optional[Dict[str, int]] = {"Fighter": 1}
    backstory: Optional[str] = ""
    alignment: Optional[List[str]] = ["Neutral", "Good"]
    abilities: Optional[Dict[str, int]] = None

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

class CharacterStateUpdateRequest(BaseModel):
    """Character state update for gameplay."""
    current_hp: Optional[int] = None
    temp_hp: Optional[int] = None
    add_condition: Optional[Dict[str, Any]] = None
    remove_condition: Optional[str] = None
    exhaustion_level: Optional[int] = None

# ============================================================================
# CORE ENDPOINTS
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "message": "D&D Character Creator API - Streamlined Version"
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
        }
    }

@app.post("/api/v2/test/mock", tags=["testing"])
async def test_mock_endpoint():
    """Test endpoint that returns static JSON to verify FastAPI is working."""
    return {
        "success": True,
        "message": "FastAPI backend is working correctly",
        "timestamp": "2025-06-30T12:00:00Z",
        "test_data": {
            "name": "Test Character",
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
        
        # Use the factory to create the object
        factory = app.state.creation_factory
        result = await factory.create_from_scratch(
            creation_type, 
            request.prompt,
            user_preferences=request.user_preferences or {}
        )
        
        object_id = None
        warnings = []
        
        # Save to database if requested (only for characters currently)
        if request.save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                # Convert CharacterSheet to database format
                if hasattr(result, 'to_dict'):
                    character_data = result.to_dict()
                else:
                    character_data = result
                
                # Create flattened data structure for database
                db_character_data = {
                    "name": character_data.get("core", {}).get("name", "Generated Character"),
                    "species": character_data.get("core", {}).get("species", "Human"),
                    "background": character_data.get("core", {}).get("background", "Folk Hero"),
                    "alignment": " ".join(character_data.get("core", {}).get("alignment", ["Neutral", "Good"])),
                    "level": character_data.get("core", {}).get("level", 1),
                    "character_classes": character_data.get("core", {}).get("character_classes", {"Fighter": 1}),
                    "backstory": character_data.get("core", {}).get("backstory", ""),
                    "abilities": character_data.get("core", {}).get("abilities", {
                        "strength": 10, "dexterity": 10, "constitution": 10,
                        "intelligence": 10, "wisdom": 10, "charisma": 10
                    }),
                    "armor_class": character_data.get("stats", {}).get("armor_class", 10),
                    "hit_points": character_data.get("stats", {}).get("max_hit_points", 10),
                    "proficiency_bonus": character_data.get("stats", {}).get("proficiency_bonus", 2),
                    "skills": character_data.get("stats", {}).get("skills", {}),
                    "equipment": character_data.get("state", {}).get("equipment", {})
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
        
        # Get verbose logs if available
        verbose_logs = None
        if hasattr(factory, 'last_verbose_logs') and factory.last_verbose_logs:
            verbose_logs = factory.last_verbose_logs
        
        return FactoryResponse(
            success=True,
            creation_type=creation_type.value,
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
        return FactoryResponse(
            success=False,
            creation_type=request.creation_type,
            data={"error": str(e)},
            processing_time=processing_time
        )

# ============================================================================
# ESSENTIAL CHARACTER MANAGEMENT
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
# REAL-TIME CHARACTER STATE MANAGEMENT
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
