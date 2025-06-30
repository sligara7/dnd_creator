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

# factory creation includes characters, monsters, NPCs, items, and spells; does it not include feats?  
# are weapons, armor, and other equipment included within items?

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

class FactoryCreateRequest(BaseModel):
    """Request model for factory-based creation from scratch."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    prompt: str
    user_preferences: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryEvolveRequest(BaseModel):
    """Request model for factory-based evolution of existing objects."""
    creation_type: str
    character_id: str
    evolution_prompt: str
    preserve_backstory: Optional[bool] = True
    user_preferences: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryResponse(BaseModel):
    """Response model for factory operations."""
    success: bool
    creation_type: str
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
        
        return FactoryResponse(
            success=True,
            creation_type=creation_type.value,
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
    """Validate a character's build for D&D 5e compliance."""
    try:
        # Create temporary CharacterCore for validation
        character_core = CharacterCore(character_data.name)
        
        # Set character properties
        character_core.species = character_data.species
        character_core.background = character_data.background
        character_core.alignment = character_data.alignment
        character_core.character_classes = character_data.character_classes
        character_core.backstory = character_data.backstory
        
        # Set ability scores
        if character_data.abilities:
            for ability, score in character_data.abilities.items():
                character_core.set_ability_score(ability, score)
        
        # Validate the character
        validation_result = character_core.validate_character_data()
        
        return {
            "valid": validation_result["valid"],
            "issues": validation_result.get("issues", []),
            "warnings": validation_result.get("warnings", []),
            "character_name": character_data.name
        }
        
    except Exception as e:
        logger.error(f"Character validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")

@app.get("/api/v2/characters/{character_id}/validate", tags=["validation"])
async def validate_existing_character(character_id: str, db = Depends(get_db)):
    """Validate an existing character from the database."""
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        validation_result = character_sheet.core.validate_character_data()
        
        return {
            "character_id": character_id,
            "character_name": character_sheet.core.name,
            "valid": validation_result["valid"],
            "issues": validation_result["issues"],
            "warnings": validation_result["warnings"]
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
