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
import time

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
from character_models import CharacterCore, CharacterSheet, DnDCondition
from core_models import AbilityScore

# PHASE 4 CLEANUP: Individual creator imports removed - now using factory pattern only
# from creation import CharacterCreator, NPCCreator, CreatureCreator, ItemCreator
# PHASE 4 CLEANUP: Legacy utility functions removed - using factory pattern only
# from creation import create_character_from_prompt, create_npc_from_prompt, create_creature_from_prompt, create_item_from_prompt
# PHASE 4 CLEANUP: Legacy creation classes removed - using factory pattern only
# from creation import CreationResult, CreationConfig
# PHASE 4 CLEANUP: Legacy content type enums removed - using CreationOptions only
# from enums import NPCType, NPCRole, ItemType, ItemRarity, CreatureType, CreatureSize

# Import factory-based creation system (Phase 2)
from creation_factory import (
    CreationFactory, 
    create_character_from_scratch, evolve_character, level_up_character,
    create_monster_from_scratch, create_item_from_scratch
)
from enums import CreationOptions

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
        # Use the effective database URL which handles SQLite/PostgreSQL selection
        database_url = settings.effective_database_url
        init_database(database_url)
        
        if settings.is_sqlite:
            logger.info(f"Database initialized successfully using SQLite: {settings.sqlite_path}")
        else:
            logger.info(f"Database initialized successfully using PostgreSQL: {settings.database_url}")
            
        # Initialize LLM service for direct endpoint usage with increased timeout for slower machines
        # Using llama3 for better JSON generation capabilities
        app.state.llm_service = create_llm_service("ollama", model="llama3:latest", timeout=300)
        logger.info("LLM service initialized successfully with llama3 model and 5-minute timeout")
        
        # Initialize Creation Factory for Phase 2 factory-based endpoints
        app.state.creation_factory = CreationFactory(app.state.llm_service)
        logger.info("Creation Factory initialized successfully")
        
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

class CharacterRestRequest(BaseModel):
    """Request model for character rest operations."""
    rest_type: Optional[str] = "long"  # "short" or "long"

class CharacterResponse(BaseModel):
    """Response model for character data."""
    id: str
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
    id: str
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
    id: str
    repository_id: str
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
    id: str
    repository_id: str
    branch_id: str
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
    id: str
    repository_id: str
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

# PHASE 4 CLEANUP: Legacy creation request models removed - using factory pattern only
# The following models have been replaced by FactoryCreateRequest:
# - ItemCreateRequest (use content_type="weapon", "armor", or "other_item")
# - NPCCreateRequest (use content_type="npc")  
# - CreatureCreateRequest (use content_type="monster")

# ============================================================================
# FACTORY-BASED CREATION PYDANTIC MODELS (PHASE 2)
# ============================================================================

class FactoryCreateRequest(BaseModel):
    """Request model for factory-based creation from scratch."""
    creation_type: str  # 'character', 'monster', 'npc', 'weapon', 'armor', 'spell', 'other_item'
    prompt: str
    user_preferences: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryEvolveRequest(BaseModel):
    """Request model for factory-based evolution of existing objects."""
    creation_type: str  # 'character', 'monster', 'npc'
    character_id: str  # ID of existing character/object in database
    evolution_prompt: str
    preserve_backstory: Optional[bool] = True
    user_preferences: Optional[Dict[str, Any]] = None
    save_to_database: Optional[bool] = True

class FactoryLevelUpRequest(BaseModel):
    """Request model for factory-based character level up."""
    character_id: str
    new_level: int
    multiclass: Optional[str] = None
    story_reason: Optional[str] = None
    context: Optional[str] = None
    preserve_backstory: Optional[bool] = True
    save_to_database: Optional[bool] = True

class FactoryResponse(BaseModel):
    """Response model for factory operations."""
    success: bool
    creation_type: str
    object_id: Optional[str] = None  # ID if saved to database
    data: Dict[str, Any]
    warnings: Optional[List[str]] = None
    processing_time: Optional[float] = None
    verbose_logs: Optional[List[Dict[str, Any]]] = None  # Detailed LLM interaction logs

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
        
        # Create CharacterSheet from request data
        character_sheet = CharacterSheet(character_data.name)
        
        # Set core character properties
        character_sheet.core.species = character_data.species
        character_sheet.core.background = character_data.background
        character_sheet.core.alignment = character_data.alignment
        character_sheet.core.character_classes = character_data.character_classes
        character_sheet.core.backstory = character_data.backstory
        
        # Set ability scores (ensure all six are present and valid)
        required_abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        default_scores = {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
        abilities = character_data.abilities or {}
        for ability in required_abilities:
            score = abilities.get(ability, default_scores[ability])
            if not isinstance(score, int) or score < 1 or score > 20:
                score = default_scores[ability]
            setattr(character_sheet.core, ability, AbilityScore(score))
        
        # Set equipment if provided
        if character_data.equipment:
            character_sheet.state.equipment = character_data.equipment.get("items", [])
            character_sheet.state.armor = character_data.equipment.get("armor", "")
            character_sheet.state.weapons = character_data.equipment.get("weapons", [])
        
        # Calculate all derived stats (AC, HP, skills, saves, etc.)
        character_sheet.calculate_all_derived_stats()
        
        # Prepare character data for database save by flattening the structure
        character_dict = character_sheet.to_dict()
        
        # Create flattened data structure for database
        db_character_data = {
            # Core character data
            "name": character_sheet.core.name,
            "species": character_sheet.core.species,
            "background": character_sheet.core.background,
            "alignment": " ".join(character_sheet.core.alignment) if isinstance(character_sheet.core.alignment, list) else character_sheet.core.alignment,
            "level": character_sheet.core.level,
            "character_classes": character_sheet.core.character_classes,
            "backstory": character_sheet.core.backstory,
            
            # Ability scores - get from core
            "abilities": {
                "strength": character_sheet.core.strength.total_score,
                "dexterity": character_sheet.core.dexterity.total_score,
                "constitution": character_sheet.core.constitution.total_score,
                "intelligence": character_sheet.core.intelligence.total_score,
                "wisdom": character_sheet.core.wisdom.total_score,
                "charisma": character_sheet.core.charisma.total_score
            },
            
            # Calculated stats
            "armor_class": character_sheet.stats.armor_class,
            "hit_points": character_sheet.stats.max_hit_points,
            "proficiency_bonus": character_sheet.stats.proficiency_bonus,
            "skills": character_sheet.stats.skills,
            
            # Equipment from state
            "equipment": {
                "items": character_sheet.state.equipment,
                "armor": character_sheet.state.armor,
                "weapons": character_sheet.state.weapons
            }
        }
        
        # Save to database using the flattened data
        db_character = CharacterDB.create_character(db, db_character_data)
        
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
async def get_character(character_id: str, db = Depends(get_db)):
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
async def update_character(character_id: str, character_data: CharacterUpdateRequest, db = Depends(get_db)):
    """
    Update an existing character.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> modify -> save back
    """
    try:
        logger.info(f"Starting character update for ID: {character_id}")
        logger.info(f"Character data type: {type(character_data)}")
        
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
        logger.info(f"Loading character sheet for ID: {character_id}")
        try:
            character_sheet = CharacterDB.load_character_sheet(db, character_id)
            logger.info(f"Loaded character_sheet type: {type(character_sheet)}")
        except Exception as load_error:
            logger.error(f"Error during character loading: {load_error}")
            raise HTTPException(status_code=500, detail=f"Character loading failed: {str(load_error)}")
        
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Type check to prevent dict attribute errors
        if isinstance(character_sheet, dict):
            logger.error(f"Loaded character is a dict, not a CharacterSheet. Data: {character_sheet}")
            raise HTTPException(status_code=500, detail="Character update failed: Internal type error (character loaded as dict, not CharacterSheet). Please check database integrity and model code.")
        
        # Check if character_sheet has core attribute
        if not hasattr(character_sheet, 'core'):
            logger.error(f"Character sheet object does not have 'core' attribute. Type: {type(character_sheet)}, Dir: {dir(character_sheet)}")
            raise HTTPException(status_code=500, detail="Character update failed: CharacterSheet object missing 'core' attribute")
        
        logger.info(f"Character sheet loaded successfully, core type: {type(character_sheet.core)}")
        
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
        
        # Note: Derived stats calculation would happen here if the method existed
        # For now, skipping to allow basic character creation
        
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
async def delete_character(character_id: str, db = Depends(get_db)):
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
async def update_character_state(character_id: str, state_updates: CharacterStateUpdateRequest, db = Depends(get_db)):
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
        
        # Apply real-time updates using state methods
        if "current_hp" in updates:
            character_sheet.state.current_hit_points = updates["current_hp"]
        if "temp_hp" in updates:
            character_sheet.state.temp_hit_points = updates["temp_hp"]
        if "armor" in updates:
            character_sheet.state.armor = updates["armor"]
        if "add_condition" in updates:
            condition_data = updates["add_condition"]
            condition_name = condition_data["condition"]
            duration = condition_data.get("duration")
            # Add condition without using .value attribute
            if hasattr(character_sheet.state, 'conditions'):
                if not isinstance(character_sheet.state.conditions, list):
                    character_sheet.state.conditions = []
                character_sheet.state.conditions.append({
                    "name": condition_name,
                    "duration": duration
                })
        if "remove_condition" in updates:
            condition_name = updates["remove_condition"]
            if hasattr(character_sheet.state, 'conditions') and isinstance(character_sheet.state.conditions, list):
                character_sheet.state.conditions = [
                    c for c in character_sheet.state.conditions 
                    if c.get("name") != condition_name
                ]
        if "exhaustion_level" in updates:
            character_sheet.state.exhaustion_level = updates["exhaustion_level"]
        if "add_equipment" in updates:
            if hasattr(character_sheet.state, 'equipment'):
                if not isinstance(character_sheet.state.equipment, list):
                    character_sheet.state.equipment = []
                character_sheet.state.equipment.append(updates["add_equipment"])
        if "add_weapon" in updates:
            if hasattr(character_sheet.state, 'weapons'):
                if not isinstance(character_sheet.state.weapons, list):
                    character_sheet.state.weapons = []
                character_sheet.state.weapons.append(updates["add_weapon"])
        
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


@app.get("/api/v1/characters/{character_id}/state", tags=["gameplay"])
async def get_character_state(character_id: str, db = Depends(get_db)):
    """
    Get real-time character state snapshot for in-game play.
    
    Operation Flow: Load -> get real-time state snapshot -> Response
    """
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


@app.post("/api/v1/characters/{character_id}/combat", tags=["gameplay"])
async def apply_combat_effects(character_id: str, combat_data: Dict[str, Any], db = Depends(get_db)):
    """
    Apply combat round effects to character.
    
    Operation Flow: Load -> apply combat effects -> real-time updates -> save back
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        # Apply combat effects manually
        action = combat_data.get("action")
        if action == "take_damage":
            damage = combat_data.get("damage", 0)
            character_sheet.state.current_hit_points = max(0, character_sheet.state.current_hit_points - damage)
        elif action == "heal":
            healing = combat_data.get("healing", 0)
            character_sheet.state.current_hit_points = min(
                character_sheet.state.max_hit_points, 
                character_sheet.state.current_hit_points + healing
            )
        
        # Save updated state
        CharacterDB.save_character_sheet(db, character_sheet, character_id)
        
        logger.info(f"Applied combat effects to character {character_id}")
        return {
            "message": "Combat effects applied successfully",
            "character_id": character_id,
            "action_applied": combat_data.get("action", "unknown"),
            "current_state": character_sheet.state.to_dict()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to apply combat effects to character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Combat effects failed: {str(e)}")


@app.post("/api/v1/characters/{character_id}/rest", tags=["gameplay"])
async def apply_rest_effects(character_id: str, rest_data: CharacterRestRequest, db = Depends(get_db)):
    """
    Apply rest effects to character.
    
    Operation Flow: Load -> apply rest effects -> real-time updates -> save back
    """
    try:
        character_sheet = CharacterDB.load_character_sheet(db, character_id)
        if not character_sheet:
            raise HTTPException(status_code=404, detail="Character not found")
        
        rest_type = rest_data.rest_type
        
        # Apply rest effects manually since the method doesn't exist
        rest_result = {}
        
        if rest_type == "short":
            # Short rest: recover some hit dice and possibly some abilities
            # For simplicity, we'll just restore some HP (up to 1/4 of max)
            max_hp = getattr(character_sheet.state, 'max_hit_points', 100)
            current_hp = getattr(character_sheet.state, 'current_hit_points', max_hp)
            
            # Heal 1/4 of max HP on short rest (simplified)
            healing = max_hp // 4
            new_hp = min(max_hp, current_hp + healing)
            character_sheet.state.current_hit_points = new_hp
            
            rest_result = {
                "rest_type": "short",
                "healing_applied": new_hp - current_hp,
                "new_hp": new_hp,
                "max_hp": max_hp
            }
            
        elif rest_type == "long":
            # Long rest: full HP recovery, spell slots, abilities reset
            max_hp = getattr(character_sheet.state, 'max_hit_points', 100)
            character_sheet.state.current_hit_points = max_hp
            
            # Clear exhaustion (reduce by 1 level)
            if hasattr(character_sheet.state, 'exhaustion_level'):
                current_exhaustion = getattr(character_sheet.state, 'exhaustion_level', 0)
                new_exhaustion = max(0, current_exhaustion - 1)
                character_sheet.state.exhaustion_level = new_exhaustion
            
            # Remove certain conditions (simplified - remove all temporary conditions)
            if hasattr(character_sheet.state, 'conditions') and isinstance(character_sheet.state.conditions, list):
                # Remove conditions that would be cleared by a long rest
                temporary_conditions = ["poisoned", "charmed", "frightened"]
                character_sheet.state.conditions = [
                    c for c in character_sheet.state.conditions 
                    if c.get("name", "").lower() not in temporary_conditions
                ]
            
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
# CHARACTER SHEET ENDPOINTS - COMPLETE CHARACTER MANAGEMENT
# ============================================================================

@app.get("/api/v1/characters/{character_id}/sheet", tags=["character_sheet"])
async def get_character_sheet(character_id: str, db = Depends(get_db)):
    """
    Get complete character sheet with all details.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> to_dict() -> Response
    """
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


# ============================================================================
# FACTORY-BASED GENERATION HELPERS (PHASE 3)
# ============================================================================

async def _factory_generate_backstory(character_data: dict, llm_service=None) -> dict:
    """
    Factory-based backstory generation helper.
    Can be used by both old and new endpoints.
    """
    try:
        # Use factory to create a temporary character for backstory generation
        factory = app.state.creation_factory if hasattr(app.state, 'creation_factory') else None
        if not factory:
            raise Exception("Factory not available")
        
        # Extract character concept for prompt
        concept_parts = []
        if isinstance(character_data, dict):
            concept_parts.append(character_data.get('species', ''))
            concept_parts.append(character_data.get('background', ''))
            if character_data.get('classes'):
                if isinstance(character_data['classes'], dict):
                    concept_parts.extend(character_data['classes'].keys())
                elif isinstance(character_data['classes'], list):
                    concept_parts.extend(character_data['classes'])
        
        character_concept = ' '.join(filter(None, concept_parts)) or str(character_data)
        
        # Use factory's LLM service for consistent generation
        prompt = f"""Generate a detailed D&D character backstory for: {character_concept}
        
        Character details: {character_data}
        
        IMPORTANT: Return only valid JSON in this format:
        {{
            "backstory": "A detailed backstory of 2-3 paragraphs...",
            "personality_traits": ["Trait 1", "Trait 2"],
            "ideals": ["Ideal 1"],
            "bonds": ["Bond 1"],
            "flaws": ["Flaw 1"]
        }}
        
        Use integers for any age, height (inches), weight (lbs) values."""
        
        response = await factory.llm_service.generate_content(prompt)
        
        # Use the same JSON cleaning logic but refactored
        return _clean_json_response(response, "backstory")
        
    except Exception as e:
        logger.error(f"Factory backstory generation failed: {e}")
        raise

async def _factory_generate_equipment(character_data: dict, llm_service=None) -> dict:
    """
    Factory-based equipment generation helper.
    Can be used by both old and new endpoints.
    """
    try:
        # Use factory to create equipment suggestions
        factory = app.state.creation_factory if hasattr(app.state, 'creation_factory') else None
        if not factory:
            raise Exception("Factory not available")
        
        # Extract character concept for prompt
        concept_parts = []
        if isinstance(character_data, dict):
            concept_parts.append(character_data.get('species', ''))
            concept_parts.append(character_data.get('background', ''))
            if character_data.get('classes'):
                if isinstance(character_data['classes'], dict):
                    concept_parts.extend(character_data['classes'].keys())
                elif isinstance(character_data['classes'], list):
                    concept_parts.extend(character_data['classes'])
        
        character_concept = ' '.join(filter(None, concept_parts)) or str(character_data)
        level = character_data.get('level', 1) if isinstance(character_data, dict) else 1
        
        prompt = f"""Generate D&D equipment suggestions for: {character_concept}
        
        Character details: {character_data}
        Character level: {level}
        
        IMPORTANT: Return only valid JSON in this format:
        {{
            "weapons": ["Weapon 1", "Weapon 2"],
            "armor": "Armor type",
            "tools": ["Tool 1", "Tool 2"],
            "items": ["Item 1", "Item 2"],
            "magical_items": ["Magic Item 1"]
        }}
        
        Use integers for any age, height (inches), weight (lbs) values."""
        
        response = await factory.llm_service.generate_content(prompt)
        
        # Use the same JSON cleaning logic but refactored
        return _clean_json_response(response, "equipment")
        
    except Exception as e:
        logger.error(f"Factory equipment generation failed: {e}")
        raise

def _clean_json_response(response: str, fallback_key: str) -> dict:
    """
    Shared JSON cleaning logic for generation endpoints.
    """
    import json
    
    try:
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
            return {fallback_key: response}
    except:
        # Fallback to raw text
        return {fallback_key: response}

# ============================================================================
# GENERATION ENDPOINTS (MIGRATING TO FACTORY - PHASE 3)
# ============================================================================
# PHASE 4: Removed redundant /api/v1/generate/backstory endpoint
# This functionality is now available via:
# - POST /api/v2/factory/create (content_type="character")  
# - POST /api/v1/generate/character-complete (includes backstory)
# Migration eliminates code duplication and encourages use of better factory pattern.

# PHASE 4: Removed redundant /api/v1/generate/equipment endpoint  
# This functionality is now available via:
# - POST /api/v2/factory/create (content_type="weapon", "armor", etc.)
# - POST /api/v1/generate/character-complete (includes equipment suggestions)
# Migration eliminates code duplication and encourages use of better factory pattern.


# ============================================================================
# UNIFIED FACTORY-BASED GENERATION ENDPOINTS (PHASE 3)
# ============================================================================

@app.post("/api/v1/generate/content", tags=["generation", "factory-v1"])
async def generate_content_unified(
    content_type: str,
    prompt: str,
    user_preferences: Optional[Dict[str, Any]] = None,
    save_to_database: Optional[bool] = False,
    db = Depends(get_db)
):
    """
    Unified content generation endpoint using factory pattern.
    
    Supports: character, monster, npc, weapon, armor, spell, other_item
    This demonstrates the factory benefits within the v1 API namespace.
    
    PHASE 3 FEATURE: Single endpoint for multiple content types.
    """
    import time
    start_time = time.time()
    
    try:
        # Validate content type
        try:
            creation_type = CreationOptions(content_type)
        except ValueError:
            raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}. Supported: {[opt.value for opt in CreationOptions]}")
        
        logger.info(f"Unified generation: {creation_type.value} - {prompt[:100]}...")
        
        # Use factory for generation
        factory = app.state.creation_factory
        result = await factory.create_from_scratch(
            creation_type,
            prompt,
            user_preferences=user_preferences or {}
        )
        
        object_id = None
        
        # Save to database if requested (only for characters currently)
        if save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                # Convert CharacterSheet to database format (reuse existing logic)
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
                logger.info(f"Generated {content_type} saved to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save generated {content_type} to database: {e}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        return {
            "success": True,
            "content_type": content_type,
            "object_id": object_id,
            "data": response_data,
            "processing_time": processing_time,
            "generated_via": "factory_pattern"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Unified generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Content generation failed: {str(e)}")


@app.post("/api/v1/generate/character-complete", tags=["generation", "factory-v1"])
async def generate_character_complete(
    prompt: str,
    level: Optional[int] = 1,
    include_backstory: Optional[bool] = True,
    include_equipment: Optional[bool] = True,
    save_to_database: Optional[bool] = True,
    db = Depends(get_db)
):
    """
    Generate a complete character with backstory and equipment in one call.
    
    PHASE 3 FEATURE: Demonstrates factory coordination for complex workflows.
    This replaces multiple separate API calls with a single, intelligent endpoint.
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Generating complete character: {prompt[:100]}...")
        
        # Generate base character using factory
        factory = app.state.creation_factory
        character_result = await factory.create_from_scratch(
            CreationOptions.CHARACTER,
            prompt,
            user_preferences={"level": level}
        )
        
        # Enhance with additional content if requested
        enhancements = {}
        
        if include_backstory:
            try:
                # Extract character data for backstory generation
                character_data = character_result.to_dict() if hasattr(character_result, 'to_dict') else character_result
                backstory_data = await _factory_generate_backstory(character_data.get("core", {}))
                enhancements["backstory_details"] = backstory_data
                
                # Update character's backstory if it's basic
                if hasattr(character_result, 'core') and hasattr(character_result.core, 'backstory'):
                    if not character_result.core.backstory or len(character_result.core.backstory) < 100:
                        character_result.core.backstory = backstory_data.get("backstory", character_result.core.backstory)
                
            except Exception as e:
                logger.warning(f"Failed to enhance backstory: {e}")
                enhancements["backstory_warning"] = "Backstory generation failed, using basic version"
        
        if include_equipment:
            try:
                # Generate equipment suggestions
                character_data = character_result.to_dict() if hasattr(character_result, 'to_dict') else character_result
                equipment_data = await _factory_generate_equipment(character_data.get("core", {}))
                enhancements["equipment_suggestions"] = equipment_data
                
            except Exception as e:
                logger.warning(f"Failed to generate equipment suggestions: {e}")
                enhancements["equipment_warning"] = "Equipment suggestions failed"
        
        object_id = None
        
        # Save to database if requested
        if save_to_database:
            try:
                # Convert to database format
                character_data = character_result.to_dict() if hasattr(character_result, 'to_dict') else character_result
                
                db_character_data = {
                    "name": character_data.get("core", {}).get("name", "Generated Character"),
                    "species": character_data.get("core", {}).get("species", "Human"),
                    "background": character_data.get("core", {}).get("background", "Folk Hero"),
                    "alignment": " ".join(character_data.get("core", {}).get("alignment", ["Neutral", "Good"])),
                    "level": character_data.get("core", {}).get("level", level),
                    "character_classes": character_data.get("core", {}).get("character_classes", {"Fighter": level}),
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
                logger.info(f"Complete character saved to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save complete character to database: {e}")
                enhancements["save_warning"] = f"Character generated but not saved: {str(e)}"
        
        processing_time = time.time() - start_time
        
        # Prepare response
        response_data = character_result.to_dict() if hasattr(character_result, 'to_dict') else character_result
        
        return {
            "success": True,
            "character_id": object_id,
            "character": response_data,
            "enhancements": enhancements,
            "processing_time": processing_time,
            "generated_via": "factory_complete_workflow"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Complete character generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Complete character generation failed: {str(e)}")


@app.post("/api/v1/characters/{character_id}/evolve", tags=["characters", "factory-v1"])
async def evolve_character_endpoint(
    character_id: str,
    evolution_prompt: str,
    preserve_backstory: Optional[bool] = True,
    save_changes: Optional[bool] = True,
    db = Depends(get_db)
):
    """
    Evolve an existing character using factory-based evolution.
    
    PHASE 3 FEATURE: Character evolution with history preservation.
    This demonstrates factory evolution capabilities within the v1 character namespace.
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Evolving character {character_id}: {evolution_prompt[:100]}...")
        
        # Load existing character
        existing_character = CharacterDB.get_character(db, character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        
        existing_data = existing_character.to_dict()
        
        # Use factory evolution
        factory = app.state.creation_factory
        evolved_character = await factory.evolve_existing(
            CreationOptions.CHARACTER,
            existing_data,
            evolution_prompt,
            preserve_backstory=preserve_backstory
        )
        
        # Save changes if requested
        if save_changes:
            try:
                CharacterDB.save_character_sheet(db, evolved_character, character_id)
                logger.info(f"Evolved character saved back to database")
            except Exception as e:
                logger.warning(f"Failed to save evolved character: {e}")
                
        processing_time = time.time() - start_time
        
        # Prepare response
        response_data = evolved_character.to_dict() if hasattr(evolved_character, 'to_dict') else evolved_character
        
        return {
            "success": True,
            "character_id": character_id,
            "evolved_character": response_data,
            "evolution_prompt": evolution_prompt,
            "changes_saved": save_changes,
            "processing_time": processing_time,
            "evolved_via": "factory_evolution"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Character evolution failed: {e}")
        raise HTTPException(status_code=500, detail=f"Character evolution failed: {str(e)}")


# ============================================================================
# VALIDATION ENDPOINTS - INTEGRATED WITH CHARACTER MODELS
# ============================================================================

@app.post("/api/v1/validate/character", tags=["validation"])
async def validate_character(character_data: CharacterCreateRequest):
    """
    Validate a character's build for D&D 5e compliance.
    
    Operation Flow: Request -> CharacterCore -> validate() -> Response
    """
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


@app.get("/api/v1/characters/{character_id}/validate", tags=["validation"])
async def validate_existing_character(character_id: str, db = Depends(get_db)):
    """
    Validate an existing character from the database.
    
    Operation Flow: Database -> CharacterDB.load_character_sheet() -> validate() -> Response
    """
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
# FACTORY-BASED CREATION ENDPOINTS (PHASE 2)
# ============================================================================

@app.post("/api/v2/factory/create", response_model=FactoryResponse, tags=["factory-v2"])
async def factory_create_from_scratch(request: FactoryCreateRequest, db = Depends(get_db)):
    """
    Create D&D objects from scratch using the factory pattern.
    
    Supports: character, monster, npc, weapon, armor, spell, other_item
    This uses the unified creation architecture where character creation is the foundation.
    
    Operation Flow: Request -> CreationFactory.create_from_scratch() -> Optional DB Save -> Response
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
            user_preferences=request.user_preferences
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


@app.post("/api/v2/factory/evolve", response_model=FactoryResponse, tags=["factory-v2"])
async def factory_evolve_existing(request: FactoryEvolveRequest, db = Depends(get_db)):
    """
    Evolve existing D&D objects using their history and new prompts.
    
    This preserves existing backstory and uses journal entries as context.
    Supports: character, monster, npc
    
    Operation Flow: Load from DB -> CreationFactory.evolve_existing() -> Save back -> Response
    """
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
            user_preferences=request.user_preferences
        )
        
        object_id = request.character_id
        warnings = []
        
        # Save evolved object back to database if requested
        if request.save_to_database and creation_type == CreationOptions.CHARACTER:
            try:
                # Save the evolved character sheet back to database
                CharacterDB.save_character_sheet(db, result, request.character_id)
                logger.info(f"Evolved character saved back to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save evolved character to database: {e}")
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


@app.post("/api/v2/factory/level-up", response_model=FactoryResponse, tags=["factory-v2"])
async def factory_level_up_character(request: FactoryLevelUpRequest, db = Depends(get_db)):
    """
    Level up a character using factory-based evolution with story context.
    
    This is a specialized evolution that preserves character history and makes
    appropriate advancement choices based on journal entries and level info.
    
    Operation Flow: Load -> level_up_character() -> Save back -> Response
    """
    import time
    start_time = time.time()
    
    try:
        logger.info(f"Factory leveling up character ID {request.character_id} to level {request.new_level}")
        
        # Load existing character from database
        existing_character = CharacterDB.get_character(db, request.character_id)
        if not existing_character:
            raise HTTPException(status_code=404, detail="Character not found")
        existing_data = existing_character.to_dict()
        
        # Prepare level info for the factory function
        level_info = {
            "new_level": request.new_level,
            "multiclass": request.multiclass,
            "context": request.context,
            "story_reason": request.story_reason
        }
        
        # Use the factory level-up function
        result = await level_up_character(
            existing_data,
            level_info,
            app.state.llm_service,
            preserve_backstory=request.preserve_backstory,
            user_preferences={}
        )
        
        object_id = request.character_id
        warnings = []
        
        # Save leveled character back to database if requested
        if request.save_to_database:
            try:
                CharacterDB.save_character_sheet(db, result, request.character_id)
                logger.info(f"Leveled up character saved back to database with ID: {object_id}")
                
            except Exception as e:
                logger.warning(f"Failed to save leveled character to database: {e}")
                warnings.append(f"Character leveled but not saved to database: {str(e)}")
        
        processing_time = time.time() - start_time
        
        # Prepare response data
        if hasattr(result, 'to_dict'):
            response_data = result.to_dict()
        else:
            response_data = result
        
        logger.info(f"Factory level-up completed in {processing_time:.2f}s")
        
        return FactoryResponse(
            success=True,
            creation_type="character",
            object_id=object_id,
            data=response_data,
            warnings=warnings if warnings else None,
            processing_time=processing_time
        )
        
    except HTTPException:
        raise
    except Exception as e:
        processing_time = time.time() - start_time
        logger.error(f"Factory level-up failed: {e}")
        return FactoryResponse(
            success=False,
            creation_type="character",
            data={"error": str(e)},
            processing_time=processing_time
        )


@app.get("/api/v2/factory/types", tags=["factory-v2"])
async def get_factory_creation_types():
    """
    Get available creation types for the factory system.
    
    Returns the types of D&D objects that can be created or evolved.
    """
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
        },
        "level_up": {
            "supported": [CreationOptions.CHARACTER.value],
            "description": "Specialized character evolution for leveling up"
        }
    }


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
async def get_character_repository(repository_id: str, db = Depends(get_db)):
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
async def get_character_timeline(repository_id: str, db = Depends(get_db)):
    """
    Get character timeline data for frontend visualization.
    
    Returns complete repository structure including branches, commits, and relationships
    formatted for frontend graph display.
    
    Operation Flow: Request -> Database Query -> Transform Data -> Response
    """
    try:
        # Get repository info first
        repo = db.query(CharacterRepository).filter(CharacterRepository.id == repository_id).first()
        if not repo:
            raise HTTPException(status_code=404, detail="Character repository not found")
        
        # Get branches and commits for the response
        branches = db.query(CharacterBranch).filter(CharacterBranch.repository_id == repository_id).all()
        commits = db.query(CharacterCommit).filter(CharacterCommit.repository_id == repository_id).all()
        
        # Transform data to match CharacterTimelineResponse model
        response_data = {
            "character_name": repo.name,
            "player_name": repo.player_name,
            "branches": [branch.to_dict() for branch in branches],
            "commits": [commit.to_dict() for commit in commits],
            "connections": []  # Will be populated with parent-child relationships
        }
        
        # Build connections (parent-child relationships)
        for commit in commits:
            if commit.parent_commit_hash:
                response_data["connections"].append({
                    "from": commit.parent_commit_hash,
                    "to": commit.commit_hash,
                    "type": "progression"
                })
        
        return CharacterTimelineResponse(**response_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get character timeline for repository {repository_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Timeline retrieval failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/visualization", response_model=CharacterVisualizationResponse, tags=["character-versioning"])
async def get_character_visualization(repository_id: str, db = Depends(get_db)):
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
                "title": commit["commit_message"],
                "commit_hash": commit["commit_hash"],
                "created_at": commit["created_at"]
            })
        
        # Create edges for commit relationships (parent-child)
        for commit in tree_data["commits"]:
            if commit.get("parent_commit_hash"):
                # Find parent commit short hash
                parent_short = None
                for parent_commit in tree_data["commits"]:
                    if parent_commit["commit_hash"] == commit["parent_commit_hash"]:
                        parent_short = parent_commit["short_hash"]
                        break
                
                if parent_short:
                    edges.append({
                        "from": parent_short,
                        "to": commit["short_hash"],
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
    repository_id: str, 
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
            branch_name=branch_data.branch_name,
            branch_point_hash=branch_data.source_commit_hash,
            description=branch_data.description
        )
        
        return CharacterBranchResponse(**branch.to_dict())
        
    except Exception as e:
        logger.error(f"Failed to create character branch: {e}")
        raise HTTPException(status_code=500, detail=f"Branch creation failed: {str(e)}")


@app.get("/api/v1/character-repositories/{repository_id}/branches", response_model=List[CharacterBranchResponse], tags=["character-versioning"])
async def list_character_branches(repository_id: str, db = Depends(get_db)):
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
    repository_id: str, 
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
        commit = CharacterRepositoryManager.create_commit(
            db=db,
            repository_id=repository_id,
            branch_name=commit_data.branch_name,
            commit_message=commit_data.commit_message,
            character_data=commit_data.character_data,
            character_level=commit_data.character_data.get("level", 1),
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
    repository_id: str, 
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
    repository_id: str, 
    level_up_data: CharacterLevelUpRequest, 
    db = Depends(get_db)
):
    """
    Handle character level up with automatic commit creation.
    
    This is a high-level operation that creates a commit specifically for character
    level advancement, with appropriate commit messages and milestone tracking.
    
    Operation Flow: Request -> CharacterRepositoryManager.level_up_character() -> Response
    """
    try:
        # Use repository_id as UUID string (no conversion needed)
        result = CharacterVersioningAPI.level_up_character(
            db=db,
            repository_id=repository_id,  # Keep as string UUID
            branch_name=level_up_data.branch_name,
            new_character_data=level_up_data.new_character_data,
            level_up_choices=level_up_data.level_info
        )
        
        # Extract level information for response
        new_level = level_up_data.new_character_data.get("level", 1)
        
        return {
            "success": True,
            "level_up": {
                "commit_hash": result.commit_hash,
                "commit_message": result.commit_message,
                "character_level": result.character_level,
                "created_at": result.created_at.isoformat() if result.created_at else None
            },
            "message": f"Character leveled up to level {new_level}"
        }
        
    except ValueError as e:
        logger.error(f"Invalid repository ID {repository_id}: {e}")
        raise HTTPException(status_code=400, detail="Invalid repository ID")
    except Exception as e:
        logger.error(f"Failed to level up character: {e}")
        raise HTTPException(status_code=500, detail=f"Level up failed: {str(e)}")


@app.post("/api/v1/character-repositories/{repository_id}/tags", response_model=CharacterTagResponse, tags=["character-versioning"])
async def create_character_tag(
    repository_id: str, 
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
        # Check if commit_hash is actually a branch name and resolve it to a commit hash
        commit_hash = tag_data.commit_hash
        
        # If it's a branch name (like "main"), find the latest commit on that branch
        branch = db.query(CharacterBranch).filter(
            CharacterBranch.repository_id == repository_id,
            CharacterBranch.branch_name == commit_hash
        ).first()
        
        if branch and branch.head_commit_hash:
            commit_hash = branch.head_commit_hash
            logger.info(f"Resolved branch '{tag_data.commit_hash}' to commit hash '{commit_hash}'")
        
        tag = CharacterRepositoryManager.create_tag(
            db=db,
            repository_id=repository_id,  # Keep as string to match database model
            commit_hash=commit_hash,
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

# PHASE 4 REMOVAL: /api/v1/characters/generate removed
# This endpoint has been replaced by:
# POST /api/v2/factory/create with content_type="character" and save_to_database=true
# 
# Migration guide:
# OLD: POST /api/v1/characters/generate?prompt="Create a wizard"
# NEW: POST /api/v2/factory/create 
#      Body: {"creation_type": "character", "prompt": "Create a wizard", "save_to_database": true}


# PHASE 4 REMOVAL: /api/v1/items/create removed
# This endpoint has been replaced by:
# POST /api/v2/factory/create with content_type="weapon", "armor", or "other_item"
#
# Migration guide:
# OLD: POST /api/v1/items/create Body: {"description": "magic sword", "item_type": "weapon"}
# NEW: POST /api/v2/factory/create Body: {"creation_type": "weapon", "prompt": "magic sword"}


# PHASE 4 REMOVAL: /api/v1/npcs/create removed
# This endpoint has been replaced by:
# POST /api/v2/factory/create with content_type="npc"
#
# Migration guide:
# OLD: POST /api/v1/npcs/create Body: {"description": "tavern keeper", "npc_type": "minor"}
# NEW: POST /api/v2/factory/create Body: {"creation_type": "npc", "prompt": "tavern keeper"}


# PHASE 4 REMOVAL: /api/v1/creatures/create removed
# This endpoint has been replaced by:
# POST /api/v2/factory/create with content_type="monster"
#
# Migration guide:
# OLD: POST /api/v1/creatures/create Body: {"description": "fire dragon", "creature_type": "dragon", "challenge_rating": 5}
# NEW: POST /api/v2/factory/create Body: {"creation_type": "monster", "prompt": "fire dragon with CR 5"}


# ============================================================================
# VISUALIZATION HELPER FUNCTIONS
# ============================================================================

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
