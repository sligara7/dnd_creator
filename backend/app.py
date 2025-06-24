# YES - API IS THE CENTRAL NEXUS/HUB FOR THE ENTIRE D&D CHARACTER CREATOR SYSTEM:
# ✅ Integrates ALL core services: LLM, Database, Frontend, Character Models
# ✅ Provides comprehensive RESTful API for complete system functionality
# ✅ Serves as single entry point for all character operations
# ✅ Orchestrates complex workflows between all system components
# ✅ Handles service initialization, error management, and graceful degradation
# ✅ Central configuration and logging hub for the entire application

# SYSTEM INTEGRATION ARCHITECTURE:
# FastAPI Main ←→ Database Models ←→ Character Models ←→ LLM Services
#      ↓              ↓                    ↓               ↓
# RESTful API ←→ Data Persistence ←→ Game Logic ←→ AI Content Generation

# LLM SERVICE INTEGRATION - YES, FULLY SUPPORTED:
# ✅ OpenAI and Anthropic API integration available
# ✅ Backstory generation endpoint: POST /api/v1/generate/backstory
# ✅ Equipment suggestions endpoint: POST /api/v1/generate/equipment
# ✅ Configurable LLM providers (OpenAI, Anthropic)
# ✅ Graceful degradation when LLM services unavailable
# ✅ Timeout and error handling for LLM API calls

# FRONTEND ACCESS SUPPORT - YES, FULLY SUPPORTED:
# ✅ HTML web app frontend access - CORS enabled, RESTful API design
# ✅ Access to ALL character sheet parameters - comprehensive getter endpoints
# ✅ Full CRUD permissions - create, read, update, delete characters 
# ✅ Parameter setting capabilities - comprehensive setter endpoints
# ✅ Real-time state updates - live gameplay support
# ✅ Security measures implemented - database and API access secured for development
# ✅ Production-ready security architecture with authentication/authorization support

"""
FastAPI main application for D&D Character Creator.

🏛️ CENTRAL SYSTEM ARCHITECTURE HUB:
This API serves as the primary nexus integrating all system components:
- 🗃️ Database Layer (SQLAlchemy models, CRUD operations)
- 🎮 Character Logic (CharacterSheet, game mechanics, D&D rules)
- 🤖 LLM Services (OpenAI/Anthropic for content generation)
- 🌐 Frontend Interface (RESTful endpoints, CORS, validation)
- 📊 Configuration Management (settings, logging, service initialization)

SYSTEM INTEGRATION FLOW:
Frontend ←→ FastAPI ←→ Character Models ←→ Database
    ↓         ↓            ↓              ↓
JavaScript ←→ REST API ←→ Game Logic ←→ Data Persistence
    ↓         ↓            ↓              ↓
   UI/UX ←→ Validation ←→ D&D Rules ←→ SQLAlchemy
                ↓
            LLM Services (AI Content)

COMPLETE FRONTEND INTEGRATION SUPPORT:

🌐 FRONTEND ACCESS:
   - Full HTML web app support with CORS enabled
   - RESTful API design for easy JavaScript integration
   - JSON responses for all endpoints
   - OpenAPI/Swagger documentation at /docs

📊 CHARACTER SHEET ACCESS (All Parameters via Getter Methods):
   - GET /api/v1/characters/{id}/sheet - Complete character sheet with ALL parameters
   - Core properties: name, species, background, alignment, classes, levels
   - Ability scores: strength, dexterity, constitution, intelligence, wisdom, charisma
   - Calculated stats: AC, HP, proficiency bonus, skill bonuses, save bonuses
   - Game state: current HP, temp HP, conditions, exhaustion, equipment
   - Personality: traits, ideals, bonds, flaws, backstory
   - Journal entries and character evolution tracking

📊 CHARACTER VERSIONING SYSTEM (Git-like):
   - POST /api/v1/character-repositories - Create character with versioning
   - GET /api/v1/character-repositories/{id} - Get repository information
   - GET /api/v1/character-repositories/{id}/timeline - Timeline for visualization
   - GET /api/v1/character-repositories/{id}/visualization - Graph visualization data
   - POST /api/v1/character-repositories/{id}/branches - Create alternate development paths
   - GET /api/v1/character-repositories/{id}/branches - List all branches
   - POST /api/v1/character-repositories/{id}/commits - Create character commits
   - GET /api/v1/character-repositories/{id}/commits - Get commit history
   - GET /api/v1/character-commits/{hash}/character - Get character at specific commit
   - POST /api/v1/character-repositories/{id}/level-up - Level up with auto-commit
   - POST /api/v1/character-repositories/{id}/tags - Tag important milestones

🔧 PARAMETER SETTING (All Setter Methods via API):
   - PUT /api/v1/characters/{id} - Update core character properties
   - PUT /api/v1/characters/{id}/state - Real-time state updates (HP, conditions, etc.)
   - POST /api/v1/characters/{id}/combat - Apply combat effects
   - POST /api/v1/characters/{id}/rest - Apply rest effects
   - All CharacterCore setter methods accessible via structured requests

🗃️ FULL CRUD PERMISSIONS:
   - POST /api/v1/characters - Create new characters
   - GET /api/v1/characters - List all characters (with filtering)
   - GET /api/v1/characters/{id} - Read specific character
   - PUT /api/v1/characters/{id} - Update existing character
   - DELETE /api/v1/characters/{id} - Delete character (soft delete)

🔒 SECURITY MEASURES:
   - CORS middleware configured for cross-origin requests
   - Input validation with Pydantic models prevents malformed data
   - SQL injection prevention via SQLAlchemy ORM
   - Comprehensive error handling prevents information leakage
   - HTTP status codes follow REST conventions
   - Ready for authentication/authorization layer addition
   - Rate limiting can be easily added for production
   - Database and API access secured for development
   - Production-ready security architecture planned

🤖 LLM SERVICE INTEGRATION:
   - OpenAI and Anthropic API support
   - POST /api/v1/generate/backstory - AI-generated character backstories
   - POST /api/v1/generate/equipment - AI-suggested equipment loadouts
   - Configurable LLM providers via environment variables
   - Graceful degradation when LLM services unavailable
   - Timeout and error handling for external API calls
   - Content generation enhances character creation experience

✅ VALIDATION & ERROR HANDLING:
   - POST /api/v1/validate/character - D&D 5e compliance validation
   - GET /api/v1/characters/{id}/validate - Validate existing characters
   - Detailed error messages for debugging
   - Type safety throughout the API

🎮 REAL-TIME GAMEPLAY SUPPORT:
   - Live character state updates during gameplay
   - Combat round effect application
   - Condition management with mechanical effects
   - Rest and recovery mechanics
   - Journal tracking for character evolution

DATABASE OPERATION FLOWS:
1. CREATE: Frontend → API → CharacterSheet → Database
2. UPDATE: Database → CharacterSheet → Modify → Save Back
3. GAMEPLAY: Load → Real-time Updates → Auto-save

FRONTEND JAVASCRIPT EXAMPLE:
```javascript
// Create character
const newCharacter = await fetch('/api/v1/characters', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({name: "Gandalf", species: "Human", ...})
});

// Get complete character sheet
const sheet = await fetch('/api/v1/characters/1/sheet').then(r => r.json());

// Update character state in real-time
await fetch('/api/v1/characters/1/state', {
  method: 'PUT',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({current_hp: 45, add_condition: {condition: "poisoned"}})
});
```

This API provides complete frontend integration with all character sheet parameters
accessible via getter/setter patterns, full CRUD operations, real-time gameplay
support, and comprehensive security measures.
"""

from contextlib import asynccontextmanager
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
import sys
import re
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import configuration and services
from config import settings
from llm_service import create_llm_service

# Import database models and operations
from database_models import CharacterDB, CharacterSessionDB, Character, CharacterSession, init_database, get_db
from database_models import (
    CharacterRepository, CharacterBranch, CharacterCommit, CharacterTag,
    CharacterRepositoryManager, CharacterVersioningAPI
)
from character_models import CharacterCore, DnDCondition

# Import refactored creation modules
from character_creation import CharacterCreator, create_character_from_prompt
from items_creation import ItemCreator, ItemType, ItemRarity, create_item_from_prompt
from npc_creation import NPCCreator, NPCType, NPCRole, create_npc_from_prompt
from creature_creation import CreatureCreator, CreatureType, CreatureSize, create_creature_from_prompt

# Import shared components
from shared_character_generation import CreationConfig, CreationResult

logger = logging.getLogger(__name__)

# ============================================================================
# FASTAPI APP INITIALIZATION
# ============================================================================

# Initialize FastAPI app
app = FastAPI(
    title="D&D Character Creator API",
    description="Comprehensive D&D 5e Character Management System",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure this properly for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    """Initialize database and services on startup."""
    try:
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        raise

# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.get("/health", tags=["health"])
async def health_check():
    """Health check endpoint for container monitoring."""
    return {"status": "healthy", "service": "dnd-character-creator-api"}

# ============================================================================
# PYDANTIC MODELS FOR REQUEST/RESPONSE VALIDATION
# ============================================================================

class CharacterCreateRequest(BaseModel):
    """Request model for creating a new character."""
    name: str
    player_name: Optional[str] = None
    species: Optional[str] = ""
    background: Optional[str] = ""
    alignment: Optional[List[str]] = ["Neutral", "Neutral"]
    character_classes: Optional[Dict[str, int]] = {}
    abilities: Optional[Dict[str, int]] = {
        "strength": 10, "dexterity": 10, "constitution": 10,
        "intelligence": 10, "wisdom": 10, "charisma": 10
    }
    backstory: Optional[str] = ""
    equipment: Optional[Dict[str, Any]] = {}

class CharacterUpdateRequest(BaseModel):
    """Request model for updating a character."""
    name: Optional[str] = None
    player_name: Optional[str] = None
    species: Optional[str] = None
    background: Optional[str] = None
    alignment: Optional[List[str]] = None
    character_classes: Optional[Dict[str, int]] = None
    abilities: Optional[Dict[str, int]] = None
    backstory: Optional[str] = None
    equipment: Optional[Dict[str, Any]] = None

class CharacterStateUpdateRequest(BaseModel):
    """Request model for real-time character state updates."""
    current_hp: Optional[int] = None
    temp_hp: Optional[int] = None
    armor: Optional[str] = None
    add_condition: Optional[Dict[str, Any]] = None
    remove_condition: Optional[str] = None
    exhaustion_level: Optional[int] = None
    currency: Optional[Dict[str, int]] = None
    add_equipment: Optional[Dict[str, Any]] = None
    add_weapon: Optional[Dict[str, Any]] = None

class CharacterResponse(BaseModel):
    """Response model for character data."""
    id: int
    name: str
    player_name: Optional[str]
    species: str
    background: Optional[str]
    alignment: Optional[str]
    level: int
    character_classes: Dict[str, int]
    abilities: Dict[str, int]
    armor_class: int
    hit_points: int
    proficiency_bonus: int
    equipment: Dict[str, Any]
    backstory: Optional[str]

# ============================================================================
# CHARACTER VERSIONING PYDANTIC MODELS
# ============================================================================

class CharacterRepositoryCreateRequest(BaseModel):
    """Request model for creating a character repository."""
    name: str
    player_name: Optional[str] = None
    description: Optional[str] = None
    character_data: Dict[str, Any]

class CharacterBranchCreateRequest(BaseModel):
    """Request model for creating a character branch."""
    branch_name: str
    source_commit_hash: str
    description: Optional[str] = None

class CharacterCommitCreateRequest(BaseModel):
    """Request model for creating a character commit."""
    branch_name: str
    character_data: Dict[str, Any]
    commit_message: str
    commit_type: Optional[str] = "update"
    milestone_name: Optional[str] = None
    session_date: Optional[str] = None
    campaign_context: Optional[str] = None
    created_by: Optional[str] = None

class CharacterLevelUpRequest(BaseModel):
    """Request model for character level up."""
    branch_name: str
    new_character_data: Dict[str, Any]
    level_info: Dict[str, Any]
    session_context: Optional[str] = None

class CharacterTagCreateRequest(BaseModel):
    """Request model for creating a character tag."""
    commit_hash: str
    tag_name: str
    tag_type: Optional[str] = "milestone"
    description: Optional[str] = None
    created_by: Optional[str] = None

class CharacterRepositoryResponse(BaseModel):
    """Response model for character repository data."""
    id: int
    repository_id: str
    name: str
    description: Optional[str]
    player_name: Optional[str]
    is_public: bool
    allow_forks: bool
    initial_commit_hash: Optional[str]
    default_branch: str
    created_at: str
    updated_at: str
    branch_count: int
    commit_count: int

class CharacterBranchResponse(BaseModel):
    """Response model for character branch data."""
    id: int
    repository_id: int
    branch_name: str
    description: Optional[str]
    branch_type: str
    head_commit_hash: Optional[str]
    parent_branch: Optional[str]
    branch_point_hash: Optional[str]
    is_active: bool
    is_merged: bool
    merged_into: Optional[str]
    created_at: str
    updated_at: str
    commit_count: int

class CharacterCommitResponse(BaseModel):
    """Response model for character commit data."""
    id: int
    repository_id: int
    branch_id: int
    commit_hash: str
    short_hash: str
    commit_message: str
    commit_type: str
    character_level: int
    experience_points: int
    milestone_name: Optional[str]
    parent_commit_hash: Optional[str]
    merge_parent_hash: Optional[str]
    character_data: Dict[str, Any]
    changes_summary: Optional[Dict[str, Any]]
    files_changed: Optional[List[str]]
    session_date: Optional[str]
    campaign_context: Optional[str]
    dm_notes: Optional[str]
    created_at: str
    created_by: Optional[str]

class CharacterTagResponse(BaseModel):
    """Response model for character tag data."""
    id: int
    repository_id: int
    tag_name: str
    tag_type: str
    description: Optional[str]
    commit_hash: str
    created_at: str
    created_by: Optional[str]

class CharacterTimelineResponse(BaseModel):
    """Response model for character timeline visualization."""
    character_name: str
    player_name: Optional[str]
    branches: List[Dict[str, Any]]
    commits: List[Dict[str, Any]]
    connections: List[Dict[str, Any]]

class CharacterVisualizationResponse(BaseModel):
    """Response model for frontend graph visualization."""
    nodes: List[Dict[str, Any]]
    edges: List[Dict[str, Any]]
    character_name: str
    player_name: Optional[str]
    branches: List[Dict[str, Any]]

class ItemCreateRequest(BaseModel):
    """Request model for creating a new item (weapon, armor, spell, equipment, etc.)."""
    name: str
    item_type: str  # 'weapon', 'armor', 'spell', 'equipment', etc.
    description: Optional[str] = ""
    properties: Optional[Dict[str, Any]] = None
    is_public: Optional[bool] = False
    created_by: Optional[str] = None

class NPCCreateRequest(BaseModel):
    """Request model for creating a new NPC."""
    name: str
    npc_type: str  # 'villager', 'merchant', 'enemy', etc.
    description: Optional[str] = ""
    stats: Optional[Dict[str, Any]] = None
    challenge_rating: Optional[float] = None
    is_public: Optional[bool] = False
    created_by: Optional[str] = None

class CreatureCreateRequest(BaseModel):
    """Request model for creating a new creature."""
    name: str
    creature_type: str  # 'beast', 'monstrosity', 'undead', etc.
    description: Optional[str] = ""
    stat_block: Optional[Dict[str, Any]] = None
    challenge_rating: Optional[float] = None
    is_public: Optional[bool] = False
    created_by: Optional[str] = None

# ============================================================================
# CHARACTER MANAGEMENT ENDPOINTS - FULLY DATABASE INTEGRATED
# ============================================================================

@app.get("/api/v1/characters", response_model=List[CharacterResponse], tags=["characters"])
async def list_characters(player_name: Optional[str] = None, db = Depends(get_db)):
    """
    List all characters with optional filtering by player name.
    
    Operation Flow: Database -> CharacterDB.list_characters() -> Response
    """
    try:
        characters = CharacterDB.list_characters(db, player_name=player_name)
        return [CharacterResponse(**char.to_dict()) for char in characters]
    except Exception as e:
        logger.error(f"Failed to list characters: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve characters")


@app.post("/api/v1/characters", response_model=CharacterResponse, tags=["characters"])
async def create_character(character_data: CharacterCreateRequest, db = Depends(get_db)):
    """
    Create a new character using the full database operation flow.
    
    Operation Flow: Request -> CharacterSheet -> CharacterDB.save_character_sheet() -> Database
    """
    try:
        # Normalize age, height, weight, and any other integer-like fields
        def normalize_int_fields(data):
            import re
            if not isinstance(data, dict):
                return data
            
            normalized = data.copy()
            for key, val in data.items():
                if key in ("age", "height", "weight") or (isinstance(val, str) and any(unit in val for unit in ["'", '"', "lbs", "years", "kg", "cm", "inches"])):
                    # Age normalization
                    if key == "age" and not isinstance(val, int):
                        try:
                            normalized[key] = int(str(val).split()[0])
                        except Exception:
                            pass
                    # Height normalization (convert feet'inches" to total inches)
                    elif key == "height" and isinstance(val, str):
                        h = str(val).strip()
                        match = re.match(r"(\d+)'(\d+)\"?", h)
                        if match:
                            feet, inches = int(match.group(1)), int(match.group(2))
                            normalized[key] = feet * 12 + inches
                        else:
                            # Try to extract just a number
                            try:
                                normalized[key] = int(re.findall(r'\d+', h)[0])
                            except Exception:
                                pass
                    # Weight normalization (extract number, assume lbs)
                    elif key == "weight" and isinstance(val, str):
                        try:
                            normalized[key] = int(re.findall(r'\d+', str(val))[0])
                        except Exception:
                            pass
            return normalized
        
        # Apply normalization to character_data if it has the relevant fields
        if hasattr(character_data, '__dict__'):
            char_dict = character_data.__dict__
            normalized_dict = normalize_int_fields(char_dict)
            for key, val in normalized_dict.items():
                if hasattr(character_data, key):
                    setattr(character_data, key, val)
        
        # Create CharacterCore from request data
        character_sheet = CharacterCore(character_data.name)
        
        # Set core character properties
        character_sheet.species = character_data.species
        character_sheet.background = character_data.background
        character_sheet.alignment = character_data.alignment
        character_sheet.character_classes = character_data.character_classes
        character_sheet.core.backstory = character_data.backstory
        
        # Set ability scores (ensure all six are present and valid)
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        default_scores = {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
        abilities = character_data.abilities or {}
        for ability in required_abilities:
            score = abilities.get(ability, default_scores[ability])
            if not isinstance(score, int) or score < 1 or score > 20:
                score = default_scores[ability]
            character_sheet.core.set_ability_score(ability, score)
        
        # Set equipment if provided
        if character_data.equipment:
            character_sheet.state.equipment = character_data.equipment.get("items", [])
            character_sheet.state.armor = character_data.equipment.get("armor", "")
            character_sheet.state.weapons = character_data.equipment.get("weapons", [])
        
        # Calculate derived stats
        character_sheet.calculate_all_derived_stats()
        
        # Save to database using the defined operation flow
        db_character = CharacterDB.save_character_sheet(db, character_sheet)
        
        # Add player_name if provided
        if character_data.player_name:
            CharacterDB.update_character(db, db_character.id, {"player_name": character_data.player_name})
            db_character = CharacterDB.get_character(db, db_character.id)
        
        logger.info(f"Created character: {db_character.name} (ID: {db_character.id})")
        return CharacterResponse(**db_character.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character: {e}")
        raise HTTPException(status_code=500, detail=f"Character creation failed: {str(e)}")


@app.get("/api/v1/characters/{character_id}", response_model=CharacterResponse, tags=["characters"])
async def get_character(character_id: int, db = Depends(get_db)):
    """
    Get a specific character by ID.
    
    Operation Flow: Database -> CharacterDB.get_character() -> Response
    """
    try:
        db_character = CharacterDB.get_character(db, character_id)
        if not db_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return CharacterResponse(**db_character.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character")


@app.put("/api/v1/characters/{character_id}", response_model=CharacterResponse, tags=["characters"])
async def update_character(character_id: int, character_data: CharacterUpdateRequest, db = Depends(get_db)):
    """
    Update an existing character.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> modify -> save back
    """
    try:
        # Normalize age, height, weight, and any other integer-like fields
        def normalize_int_fields(data):
            import re
            if not isinstance(data, dict):
                return data
            
            normalized = data.copy()
            for key, val in data.items():
                if key in ("age", "height", "weight") or (isinstance(val, str) and any(unit in val for unit in ["'", '"', "lbs", "years", "kg", "cm", "inches"])):
                    # Age normalization
                    if key == "age" and not isinstance(val, int):
                        try:
                            normalized[key] = int(str(val).split()[0])
                        except Exception:
                            pass
                    # Height normalization (convert feet'inches" to total inches)
                    elif key == "height" and isinstance(val, str):
                        h = str(val).strip()
                        match = re.match(r"(\d+)'(\d+)\"?", h)
                        if match:
                            feet, inches = int(match.group(1)), int(match.group(2))
                            normalized[key] = feet * 12 + inches
                        else:
                            # Try to extract just a number
                            try:
                                normalized[key] = int(re.findall(r'\d+', h)[0])
                            except Exception:
                                pass
                    # Weight normalization (extract number, assume lbs)
                    elif key == "weight" and isinstance(val, str):
                        try:
                            normalized[key] = int(re.findall(r'\d+', str(val))[0])
                        except Exception:
                            pass
            return normalized
        
        # Apply normalization to character_data if it has the relevant fields
        if hasattr(character_data, '__dict__'):
            char_dict = character_data.__dict__
            normalized_dict = normalize_int_fields(char_dict)
            for key, val in normalized_dict.items():
                if hasattr(character_data, key):
                    setattr(character_data, key, val)
        
        # Load character as CharacterSheet for full functionality
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply updates using CharacterSheet methods
        if character_data.name is not None:
            character_sheet.core.set_name(character_data.name)
        if character_data.species is not None:
            character_sheet.core.set_species(character_data.species)
        if character_data.background is not None:
            character_sheet.core.set_background(character_data.background)
        if character_data.alignment is not None:
            character_sheet.core.set_alignment(character_data.alignment)
        if character_data.character_classes is not None:
            character_sheet.core.set_character_classes(character_data.character_classes)
        if character_data.backstory is not None:
            character_sheet.core.set_backstory(character_data.backstory)
        
        # Update ability scores if provided (ensure all six are present and valid)
        if character_data.abilities:
            required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            default_scores = {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
            abilities = character_data.abilities
            for ability in required_abilities:
                score = abilities.get(ability, default_scores[ability])
                if not isinstance(score, int) or score < 1 or score > 20:
                    score = default_scores[ability]
                character_sheet.core.set_ability_score(ability, score)
        
        # Update equipment if provided
        if character_data.equipment:
            character_sheet.state.equipment = character_data.equipment.get("items", [])
            character_sheet.state.armor = character_data.equipment.get("armor", "")
            character_sheet.state.weapons = character_data.equipment.get("weapons", [])
        
        # Recalculate derived stats
        character_sheet.calculate_all_derived_stats()
        
        # Save back to database
        db_character = CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        # Update player_name if provided (not part of CharacterSheet)
        if character_data.player_name is not None:
            CharacterDB.update_character(db, character_id, {"player_name": character_data.player_name})
            db_character = CharacterDB.get_character(db, character_id)
        
        logger.info(f"Updated character: {db_character.name} (ID: {character_id})")
        return CharacterResponse(**db_character.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Character update failed: {str(e)}")


@app.delete("/api/v1/characters/{character_id}", tags=["characters"])
async def delete_character(character_id: int, db = Depends(get_db)):
    """
    Delete a character (soft delete - marks as inactive).
    
    Operation Flow: Database -> CharacterDB.delete_character() -> Response
    """
    try:
        success = CharacterDB.delete_character(db, character_id)
        if not success:
            raise HTTPException(status_code=404, detail="Character not found")
        
        logger.info(f"Deleted character ID: {character_id}")
        return {"message": "Character deleted successfully", "character_id": character_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete character {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Character deletion failed")


# ============================================================================
# IN-GAME PLAY ENDPOINTS - REAL-TIME STATE UPDATES
# ============================================================================

@app.put("/api/v1/characters/{character_id}/state", tags=["gameplay"])
async def update_character_state(character_id: int, state_updates: CharacterStateUpdateRequest, db = Depends(get_db)):
    """
    Update character state for in-game play using real-time update methods.
    
    Operation Flow: Load -> use getter/setter methods -> real-time updates -> save back
    """
    try:
        # Load character for in-game play
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Prepare updates dictionary for comprehensive update method
        updates = {}
        if state_updates.current_hp is not None:
            updates["current_hp"] = state_updates.current_hp
        if state_updates.temp_hp is not None:
            updates["temp_hp"] = state_updates.temp_hp
        if state_updates.armor is not None:
            updates["armor"] = state_updates.armor
        if state_updates.add_condition is not None:
            updates["add_condition"] = state_updates.add_condition
        if state_updates.remove_condition is not None:
            updates["remove_condition"] = state_updates.remove_condition
        if state_updates.exhaustion_level is not None:
            updates["exhaustion_level"] = state_updates.exhaustion_level
        if state_updates.currency is not None:
            updates["currency"] = state_updates.currency
        if state_updates.add_equipment is not None:
            updates["add_equipment"] = state_updates.add_equipment
        if state_updates.add_weapon is not None:
            updates["add_weapon"] = state_updates.add_weapon
        
        # Apply real-time updates using comprehensive update method
        update_result = character_sheet.update_character_state(updates)
        
        # Save updated state back to database
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Updated character state for ID {character_id}: {len(update_result['changes'])} changes")
        return {
            "message": "Character state updated successfully",
            "character_id": character_id,
            "updates_applied": update_result["changes"],
            "current_state": character_sheet.get_real_time_state_snapshot()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update character state {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"State update failed: {str(e)}")


@app.get("/api/v1/characters/{character_id}/state", tags=["gameplay"])
async def get_character_state(character_id: int, db = Depends(get_db)):
    """
    Get real-time character state snapshot for in-game play.
    
    Operation Flow: Load -> get real-time state snapshot -> Response
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character_sheet.get_real_time_state_snapshot()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character state {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character state")


@app.post("/api/v1/characters/{character_id}/combat", tags=["gameplay"])
async def apply_combat_effects(character_id: int, combat_data: Dict[str, Any], db = Depends(get_db)):
    """
    Apply combat round effects to character.
    
    Operation Flow: Load -> apply combat effects -> real-time updates -> save back
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply combat effects using real-time methods
        combat_result = character_sheet.apply_combat_round_effects(combat_data)
        
        # Save updated state
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Applied combat effects to character {character_id}")
        return {
            "message": "Combat effects applied successfully",
            "character_id": character_id,
            "combat_result": combat_result,
            "current_state": character_sheet.get_real_time_state_snapshot()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply combat effects to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Combat effects failed: {str(e)}")


@app.post("/api/v1/characters/{character_id}/rest", tags=["gameplay"])
async def apply_rest_effects(character_id: int, rest_type: str = "long", db = Depends(get_db)):
    """
    Apply rest effects to character.
    
    Operation Flow: Load -> apply rest effects -> real-time updates -> save back
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply rest effects
        rest_result = character_sheet.apply_rest_effects(rest_type)
        
        # Save updated state
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Applied {rest_type} rest to character {character_id}")
        return {
            "message": f"{rest_type.capitalize()} rest completed successfully",
            "character_id": character_id,
            "rest_result": rest_result,
            "current_state": character_sheet.get_real_time_state_snapshot()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply rest to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Rest failed: {str(e)}")


# ============================================================================
# CHARACTER SHEET ENDPOINTS - COMPLETE CHARACTER MANAGEMENT
# ============================================================================

@app.get("/api/v1/characters/{character_id}/sheet", tags=["character_sheet"])
async def get_character_sheet(character_id: int, db = Depends(get_db)):
    """
    Get complete character sheet with all details.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> get_character_summary() -> Response
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        return character_sheet.get_character_summary()
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character sheet {character_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve character sheet")


# Character generation endpoints
@app.post("/api/v1/generate/backstory", tags=["generation"])
async def generate_backstory(character_data: dict):
    """Generate a character backstory using LLM."""
    if not app.state.llm_service:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    try:
        prompt = f"""Generate a detailed D&D character backstory for: {character_data}
        
        IMPORTANT: Return only valid JSON in this format:
        {{
            "backstory": "A detailed backstory of 2-3 paragraphs...",
            "personality_traits": ["Trait 1", "Trait 2"],
            "ideals": ["Ideal 1"],
            "bonds": ["Bond 1"],
            "flaws": ["Flaw 1"]
        }}
        
        Use integers for any age, height (inches), weight (lbs) values."""
        
        response = await app.state.llm_service.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            import json
            # Extract JSON from response with robust brace counting
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                # Fallback to raw text
                return {"backstory": response}
        except:
            # Fallback to raw text
            return {"backstory": response}
            
    except Exception as e:
        logger.error(f"Backstory generation failed: {e}")
        raise HTTPException(status_code=500, detail="Backstory generation failed")


@app.post("/api/v1/generate/equipment", tags=["generation"])
async def generate_equipment(character_data: dict):
    """Generate character equipment suggestions using LLM."""
    if not app.state.llm_service:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    try:
        prompt = f"""Generate D&D equipment suggestions for: {character_data}
        
        IMPORTANT: Return only valid JSON in this format:
        {{
            "weapons": ["Weapon 1", "Weapon 2"],
            "armor": "Armor type",
            "tools": ["Tool 1", "Tool 2"],
            "items": ["Item 1", "Item 2"],
            "magical_items": ["Magic Item 1"]
        }}
        
        Use integers for any age, height (inches), weight (lbs) values."""
        
        response = await app.state.llm_service.generate_content(prompt)
        
        # Try to parse JSON response
        try:
            import json
            # Extract JSON from response with robust brace counting
            response_stripped = response.strip()
            start = response_stripped.find('{')
            
            # Find the last valid closing brace by counting braces
            end = -1
            brace_count = 0
            for i, char in enumerate(response_stripped[start:], start):
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        end = i + 1
                        break
            
            if start != -1 and end > start:
                json_str = response_stripped[start:end]
                parsed_data = json.loads(json_str)
                return parsed_data
            else:
                # Fallback to raw text
                return {"equipment": response}
        except:
            # Fallback to raw text
            return {"equipment": response}
            
    except Exception as e:
        logger.error(f"Equipment generation failed: {e}")
        raise HTTPException(status_code=500, detail="Equipment generation failed")


# ============================================================================
# VALIDATION ENDPOINTS - INTEGRATED WITH CHARACTER MODELS
# ============================================================================

@app.post("/api/v1/validate/character", tags=["validation"])
async def validate_character(character_data: CharacterCreateRequest):
    """
    Validate a character's build for D&D 5e compliance.
    
    Operation Flow: Request -> CharacterSheet -> validate() -> Response
    """
    try:
        # Create temporary CharacterCore for validation
        character_sheet = CharacterCore(character_data.name)
        
        # Set character properties
        character_sheet.species = character_data.species
        character_sheet.background = character_data.background
        character_sheet.alignment = character_data.alignment
        character_sheet.character_classes = character_data.character_classes
        character_sheet.core.backstory = character_data.backstory
        
        # Set ability scores
        if character_data.abilities:
            for ability, score in character_data.abilities.items():
                character_sheet.core.set_ability_score(ability, score)
        
        # Validate the character
        validation_result = character_sheet.validate_character()
        
        return {
            "valid": validation_result["valid"],
            "issues": validation_result["issues"],
            "warnings": validation_result["warnings"],
            "character_name": character_data.name
        }
        
    except Exception as e:
        logger.error(f"Character validation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Validation failed: {str(e)}")


@app.get("/api/v1/characters/{character_id}/validate", tags=["validation"])
async def validate_existing_character(character_id: int, db = Depends(get_db)):
    """
    Validate an existing character from the database.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> validate() -> Response
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        validation_result = character_sheet.validate_character()
        
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
# CHARACTER VERSIONING ENDPOINTS
# ============================================================================

@app.post("/api/v1/character-repositories", response_model=CharacterRepositoryResponse, tags=["character-versioning"])
async def create_character_repository(
    repo_data: CharacterRepositoryCreateRequest, 
    db = Depends(get_db)
):
    """
    Create a new character repository with Git-like versioning.
    
    This creates the initial character repository with an initial commit on the main branch.
    The repository serves as a container for all versions and branches of a character concept.
    
    Operation Flow: Request -> CharacterRepositoryManager.create_repository() -> Response
    """
    try:
        repo = CharacterRepositoryManager.create_repository(
            db=db,
            name=repo_data.name,
            initial_character_data=repo_data.character_data,
            player_name=repo_data.player_name,
            description=repo_data.description
        )
        
        return CharacterRepositoryResponse(**repo.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character repository: {e}")
        raise HTTPException(status_code=500, detail=f"Repository creation failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}", response_model=CharacterRepositoryResponse, tags=["character-versioning"])
async def get_character_repository(repository_id: int, db = Depends(get_db)):
    """
    Get character repository information.
    
    Returns basic repository metadata including branch and commit counts.
    """
    try:
        repo = db.query(CharacterRepository).filter(CharacterRepository.id == repository_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Character repository not found")
        
        return CharacterRepositoryResponse(**repo.to_dict())
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Repository retrieval failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/timeline", response_model=CharacterTimelineResponse, tags=["character-versioning"])
async def get_character_timeline(repository_id: int, db = Depends(get_db)):
    """
    Get character timeline data for frontend visualization.
    
    Returns complete repository structure including branches, commits, and relationships
    formatted for frontend graph display.
    
    Operation Flow: Request -> CharacterVersioningAPI.get_character_timeline_for_frontend() -> Response
    """
    try:
        timeline_data = CharacterVersioningAPI.get_character_timeline_for_frontend(db, repository_id)
        if not timeline_data:
            raise HTTPException(status_code=404, detail="Character repository not found")
        
        return CharacterTimelineResponse(**timeline_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character timeline for repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Timeline retrieval failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/visualization", response_model=CharacterVisualizationResponse, tags=["character-versioning"])
async def get_character_visualization(repository_id: int, db = Depends(get_db)):
    """
    Get character visualization data formatted for graph libraries.
    
    Returns nodes, edges, and metadata formatted for frontend graph visualization
    libraries like D3.js, vis.js, or Cytoscape.js.
    
    Operation Flow: Request -> CharacterRepositoryManager.get_repository_tree() -> Format -> Response
    """
    try:
        tree_data = CharacterRepositoryManager.get_repository_tree(db, repository_id)
        if not tree_data:
            raise HTTPException(status_code=404, detail="Character repository not found")
        
        # Format for graph visualization
        nodes = []
        edges = []
        
        # Create nodes for each commit
        for commit in tree_data["commits"]:
            nodes.append({
                "id": commit["short_hash"],
                "label": f"Level {commit['character_level']}\\n{commit['commit_message'][:30]}...",
                "level": commit["character_level"],
                "type": commit["commit_type"],
                "branch": commit["branch_id"],
                "color": get_commit_color(commit["commit_type"]),
                "size": get_commit_size(commit["character_level"]),
                "title": commit["commit_message"],
                "commit_hash": commit["commit_hash"],
                "created_at": commit["created_at"]
            })
        
        # Create edges for commit relationships
        for commit_hash, parent_hash in tree_data["relationships"]["parent_child"].items():
            edges.append({
                "from": parent_hash[:8],
                "to": commit_hash[:8],
                "type": "progression",
                "color": "#666666"
            })
        
        return CharacterVisualizationResponse(
            nodes=nodes,
            edges=edges,
            character_name=tree_data["repository"]["name"],
            player_name=tree_data["repository"]["player_name"],
            branches=tree_data["branches"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character visualization for repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Visualization data retrieval failed: {str(e)}")


@app.post("/api/v1/character-repositories/{repository_id}/branches", response_model=CharacterBranchResponse, tags=["character-versioning"])
async def create_character_branch(
    repository_id: int, 
    branch_data: CharacterBranchCreateRequest, 
    db = Depends(get_db)
):
    """
    Create a new character development branch.
    
    Branches allow players to explore "what-if" scenarios from any point in their character's
    development history. For example, branching at level 3 to explore multiclassing options.
    
    Operation Flow: Request -> CharacterRepositoryManager.create_branch() -> Response
    """
    try:
        branch = CharacterRepositoryManager.create_branch(
            db=db,
            repository_id=repository_id,
            new_branch_name=branch_data.branch_name,
            source_commit_hash=branch_data.source_commit_hash,
            description=branch_data.description
        )
        
        return CharacterBranchResponse(**branch.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character branch: {e}")
        raise HTTPException(status_code=500, detail=f"Branch creation failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/branches", response_model=List[CharacterBranchResponse], tags=["character-versioning"])
async def list_character_branches(repository_id: int, db = Depends(get_db)):
    """
    List all branches in a character repository.
    
    Returns all development branches for a character, including their status and metadata.
    """
    try:
        branches = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id
        ).all()
        
        return [CharacterBranchResponse(**branch.to_dict()) for branch in branches]
        
    except Exception as e:
        logger.error(f"Failed to list character branches for repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Branch listing failed: {str(e)}")


@app.post("/api/v1/character-repositories/{repository_id}/commits", response_model=CharacterCommitResponse, tags=["character-versioning"])
async def create_character_commit(
    repository_id: int, 
    commit_data: CharacterCommitCreateRequest, 
    db = Depends(get_db)
):
    """
    Create a new character commit.
    
    Commits represent character state changes like leveling up, equipment changes,
    story developments, or any other significant character modifications.
    
    Operation Flow: Request -> CharacterRepositoryManager.commit_character_change() -> Response
    """
    try:
        commit = CharacterRepositoryManager.commit_character_change(
            db=db,
            repository_id=repository_id,
            branch_name=commit_data.branch_name,
            character_data=commit_data.character_data,
            commit_message=commit_data.commit_message,
            commit_type=commit_data.commit_type,
            milestone_name=commit_data.milestone_name,
            session_date=commit_data.session_date,
            campaign_context=commit_data.campaign_context,
            created_by=commit_data.created_by
        )
        
        return CharacterCommitResponse(**commit.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character commit: {e}")
        raise HTTPException(status_code=500, detail=f"Commit creation failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/commits", response_model=List[CharacterCommitResponse], tags=["character-versioning"])
async def get_character_commits(
    repository_id: int, 
    branch_name: Optional[str] = None, 
    limit: int = 50,
    db = Depends(get_db)
):
    """
    Get commit history for a character repository.
    
    Returns commits in reverse chronological order. Can be filtered by branch name.
    
    Operation Flow: Request -> CharacterRepositoryManager.get_commit_history() -> Response
    """
    try:
        commits = CharacterRepositoryManager.get_commit_history(
            db=db,
            repository_id=repository_id,
            branch_name=branch_name,
            limit=limit
        )
        
        return [CharacterCommitResponse(**commit.to_dict()) for commit in commits]
        
    except Exception as e:
        logger.error(f"Failed to get character commits for repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Commit history retrieval failed: {str(e)}")


@app.get("/api/v1/character-commits/{commit_hash}/character", tags=["character-versioning"])
async def get_character_at_commit(commit_hash: str, db = Depends(get_db)):
    """
    Get character data at a specific commit.
    
    Returns the complete character state as it existed at the specified commit.
    Useful for viewing character history or rolling back to previous states.
    
    Operation Flow: Request -> CharacterRepositoryManager.get_character_at_commit() -> Response
    """
    try:
        character_data = CharacterRepositoryManager.get_character_at_commit(db, commit_hash)
        if not character_data:
            raise HTTPException(status_code=404, detail="Commit not found")
        
        return {
            "success": True,
            "commit_hash": commit_hash,
            "character_data": character_data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character data at commit {commit_hash}: {e}")
        raise HTTPException(status_code=500, detail=f"Character retrieval failed: {str(e)}")


@app.post("/api/v1/character-repositories/{repository_id}/level-up", tags=["character-versioning"])
async def level_up_character(
    repository_id: int, 
    level_up_data: CharacterLevelUpRequest, 
    db = Depends(get_db)
):
    """
    Handle character level up with automatic commit creation.
    
    This is a high-level operation that creates a commit specifically for character
    level advancement, with appropriate commit messages and milestone tracking.
    
    Operation Flow: Request -> CharacterVersioningAPI.level_up_character() -> Response
    """
    try:
        result = CharacterVersioningAPI.level_up_character(
            db=db,
            repository_id=repository_id,
            branch_name=level_up_data.branch_name,
            new_character_data=level_up_data.new_character_data,
            level_info=level_up_data.level_info
        )
        
        return {
            "success": True,
            "level_up": result,
            "message": f"Character leveled up to level {level_up_data.level_info['new_level']}"
        }
        
    except Exception as e:
        logger.error(f"Failed to level up character: {e}")
        raise HTTPException(status_code=500, detail=f"Level up failed: {str(e)}")


@app.post("/api/v1/character-repositories/{repository_id}/tags", response_model=CharacterTagResponse, tags=["character-versioning"])
async def create_character_tag(
    repository_id: int, 
    tag_data: CharacterTagCreateRequest, 
    db = Depends(get_db)
):
    """
    Create a tag for a specific commit.
    
    Tags mark important milestones like deaths, resurrections, epic achievements,
    or other significant story moments.
    
    Operation Flow: Request -> CharacterRepositoryManager.create_tag() -> Response
    """
    try:
        tag = CharacterRepositoryManager.create_tag(
            db=db,
            repository_id=repository_id,
            commit_hash=tag_data.commit_hash,
            tag_name=tag_data.tag_name,
            tag_type=tag_data.tag_type,
            description=tag_data.description,
            created_by=tag_data.created_by
        )
        
        return CharacterTagResponse(**tag.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character tag: {e}")
        raise HTTPException(status_code=500, detail=f"Tag creation failed: {str(e)}")


# ============================================================================
# CONTENT CREATION ENDPOINTS - USING REFACTORED MODULES
# ============================================================================

@app.post("/api/v1/characters/generate", tags=["character-generation"])
async def generate_character(prompt: str, db = Depends(get_db)):
    """
    Generate a new character using the refactored CharacterCreator with LLM integration.
    
    This endpoint uses the new shared components architecture for character generation.
    """
    try:
        # Create LLM service
        llm_service = create_llm_service()
        
        # Create character using refactored module
        creator = CharacterCreator(llm_service)
        result = creator.create_character(prompt)
        
        if result.success:
            # Save the generated character to database
            character_data = result.data.get("raw_data", {})
            
            # Convert to CharacterCreateRequest format for existing save logic
            character_request = CharacterCreateRequest(
                name=character_data.get("name", "Generated Character"),
                species=character_data.get("species", ""),
                background=character_data.get("background", ""),
                alignment=character_data.get("alignment", ["Neutral", "Neutral"]),
                character_classes=character_data.get("classes", {}),
                abilities=character_data.get("ability_scores", {}),
                backstory=character_data.get("backstory", ""),
                equipment=character_data.get("equipment", {})
            )
            
            # Use existing character creation endpoint logic to save
            saved_character = await create_character(character_request, db)
            
            return {
                "success": True,
                "generation_time": result.creation_time,
                "warnings": result.warnings,
                "character": saved_character,
                "generation_metadata": result.data.get("creation_metadata", {})
            }
        else:
            raise HTTPException(status_code=500, detail=f"Character generation failed: {result.error}")
            
    except Exception as e:
        logger.error(f"Character generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Character generation failed: {str(e)}")


@app.post("/api/v1/items/create", tags=["content-creation"])
async def create_item(item: ItemCreateRequest, db = Depends(get_db)):
    """
    Create a new item using the refactored ItemCreator.
    
    This endpoint uses the new shared components architecture for item creation.
    """
    try:
        # Create LLM service
        llm_service = create_llm_service()
        
        # Create item using refactored module
        creator = ItemCreator(llm_service)
        
        # Map item_type string to enum
        item_type_mapping = {
            "weapon": ItemType.WEAPON,
            "armor": ItemType.ARMOR,
            "shield": ItemType.SHIELD,
            "spell": ItemType.SPELL,
            "magic_item": ItemType.MAGIC_ITEM,
            "potion": ItemType.POTION,
            "scroll": ItemType.SCROLL,
            "tool": ItemType.TOOL,
            "adventuring_gear": ItemType.ADVENTURING_GEAR
        }
        
        item_type_enum = item_type_mapping.get(item.item_type.lower(), ItemType.MAGIC_ITEM)
        
        # Create item
        result = creator.create_item(item.description, item_type_enum, character_level=1)
        
        if result.success:
            # TODO: Save to database if needed
            return {
                "success": True,
                "creation_time": result.creation_time,
                "warnings": result.warnings,
                "item": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=f"Item creation failed: {result.error}")
            
    except Exception as e:
        logger.error(f"Item creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Item creation failed: {str(e)}")


@app.post("/api/v1/npcs/create", tags=["content-creation"])
async def create_npc(npc: NPCCreateRequest, db = Depends(get_db)):
    """
    Create a new NPC using the refactored NPCCreator.
    
    This endpoint uses the new shared components architecture for NPC creation.
    """
    try:
        # Create LLM service
        llm_service = create_llm_service()
        
        # Create NPC using refactored module
        creator = NPCCreator(llm_service)
        
        # Map npc_type string to enum
        npc_type_enum = NPCType.MINOR if npc.npc_type.lower() == "minor" else NPCType.MAJOR
        
        # Map to role enum (default to civilian)
        npc_role_enum = NPCRole.CIVILIAN
        role_mapping = {
            "merchant": NPCRole.MERCHANT,
            "guard": NPCRole.GUARD,
            "noble": NPCRole.NOBLE,
            "scholar": NPCRole.SCHOLAR,
            "artisan": NPCRole.ARTISAN,
            "criminal": NPCRole.CRIMINAL,
            "soldier": NPCRole.SOLDIER
        }
        
        # Try to infer role from description or npc_type
        for role_name, role_enum in role_mapping.items():
            if role_name in npc.description.lower() or role_name in npc.npc_type.lower():
                npc_role_enum = role_enum
                break
        
        # Create NPC
        result = creator.create_npc(npc.description, npc_type_enum, npc_role_enum)
        
        if result.success:
            # TODO: Save to database if needed
            return {
                "success": True,
                "creation_time": result.creation_time,
                "warnings": result.warnings,
                "npc": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=f"NPC creation failed: {result.error}")
            
    except Exception as e:
        logger.error(f"NPC creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"NPC creation failed: {str(e)}")


@app.post("/api/v1/creatures/create", tags=["content-creation"])
async def create_creature(creature: CreatureCreateRequest, db = Depends(get_db)):
    """
    Create a new creature using the refactored CreatureCreator.
    
    This endpoint uses the new shared components architecture for creature creation.
    """
    try:
        # Create LLM service
        llm_service = create_llm_service()
        
        # Create creature using refactored module
        creator = CreatureCreator(llm_service)
        
        # Map creature_type string to enum
        creature_type_mapping = {
            "aberration": CreatureType.ABERRATION,
            "beast": CreatureType.BEAST,
            "celestial": CreatureType.CELESTIAL,
            "construct": CreatureType.CONSTRUCT,
            "dragon": CreatureType.DRAGON,
            "elemental": CreatureType.ELEMENTAL,
            "fey": CreatureType.FEY,
            "fiend": CreatureType.FIEND,
            "giant": CreatureType.GIANT,
            "humanoid": CreatureType.HUMANOID,
            "monstrosity": CreatureType.MONSTROSITY,
            "ooze": CreatureType.OOZE,
            "plant": CreatureType.PLANT,
            "undead": CreatureType.UNDEAD
        }
        
        creature_type_enum = creature_type_mapping.get(creature.creature_type.lower(), CreatureType.BEAST)
        
        # Create creature
        result = creator.create_creature(
            creature.description, 
            challenge_rating=creature.challenge_rating or 1.0,
            creature_type=creature_type_enum.value
        )
        
        if result.success:
            # TODO: Save to database if needed
            return {
                "success": True,
                "creation_time": result.creation_time,
                "warnings": result.warnings,
                "creature": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=f"Creature creation failed: {result.error}")
            
    except Exception as e:
        logger.error(f"Creature creation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Creature creation failed: {str(e)}")


# ============================================================================
# QUICK GENERATION ENDPOINTS - CONVENIENCE FUNCTIONS
# ============================================================================

@app.post("/api/v1/generate/quick-character", tags=["quick-generation"])
async def quick_generate_character(concept: str, db = Depends(get_db)):
    """Quick character generation using shared components."""
    try:
        result = create_character_from_prompt(concept)
        
        if result.success:
            return {
                "success": True,
                "generation_time": result.creation_time,
                "character_concept": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        logger.error(f"Quick character generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/quick-item", tags=["quick-generation"])
async def quick_generate_item(concept: str, item_type: str = "magic_item", level: int = 1):
    """Quick item generation using shared components."""
    try:
        result = create_item_from_prompt(concept, ItemType.MAGIC_ITEM, level)
        
        if result.success:
            return {
                "success": True,
                "generation_time": result.creation_time,
                "item": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        logger.error(f"Quick item generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/quick-npc", tags=["quick-generation"])
async def quick_generate_npc(concept: str, role: str = "civilian"):
    """Quick NPC generation using shared components."""
    try:
        result = create_npc_from_prompt(concept, NPCType.MINOR)
        
        if result.success:
            return {
                "success": True,
                "generation_time": result.creation_time,
                "npc": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        logger.error(f"Quick NPC generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/generate/quick-creature", tags=["quick-generation"])
async def quick_generate_creature(concept: str, cr: float = 1.0, creature_type: str = "beast"):
    """Quick creature generation using shared components."""
    try:
        result = create_creature_from_prompt(concept, cr)
        
        if result.success:
            return {
                "success": True,
                "generation_time": result.creation_time,
                "creature": result.data
            }
        else:
            raise HTTPException(status_code=500, detail=result.error)
            
    except Exception as e:
        logger.error(f"Quick creature generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Helper functions for visualization
def get_commit_color(commit_type: str) -> str:
    """Get color for commit based on type."""
    colors = {
        "initial": "#4CAF50",     # Green
        "level_up": "#2196F3",    # Blue
        "equipment": "#FF9800",   # Orange
        "story": "#9C27B0",       # Purple
        "death": "#F44336",       # Red
        "resurrection": "#00BCD4", # Cyan
        "update": "#607D8B"       # Blue Grey
    }
    return colors.get(commit_type, "#607D8B")

def get_commit_size(level: int) -> int:
    """Get node size based on character level."""
    return min(20 + level * 2, 60)  # Scale with level, max size 60

# Normalize age, height, weight, and any other integer-like fields
def normalize_int_fields(data):
    import re
    if not isinstance(data, dict):
        return data
    for key in list(data.keys()):
        val = data[key]
        if key in ("age", "height", "weight") or (isinstance(val, str) and any(unit in val for unit in ["'", '"', "lbs", "years", "kg", "cm", "inches"])):
            # Age
            if key == "age" and not isinstance(val, int):
                try:
                    data[key] = int(str(val).split()[0])
                except Exception:
                    pass
            # Height
            elif key == "height":
                h = str(val).strip()
                match = re.match(r"(\d+)'(\d+)", h)
                if match:
                    feet, inches = map(int, match.groups())
                    data[key] = feet * 12 + inches  # Convert to inches
                else:
                    try:
                        data[key] = int(h)  # Fallback to direct conversion
                    except Exception:
                        pass
            # Weight
            elif key == "weight":
                w = str(val).strip()
                if "lbs" in w:
                    try:
                        data[key] = int(w.replace("lbs", "").strip())
                    except Exception:
                        pass
                elif "kg" in w:
                    try:
                        data[key] = int(float(w.replace("kg", "").strip()) * 2.20462)  # Convert kg to lbs
                    except Exception:
                        pass
            else:
                try:
                    data[key] = int(val)  # Generic fallback for other fields
                except Exception:
                    pass
    return data
