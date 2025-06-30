"""
DEMONSTRATION: How to integrate the Creation Factory into existing endpoints

This file shows how the current app.py endpoints could be refactored to use
the new Creation Factory pattern for cleaner, more maintainable code.

CURRENT APPROACH (in app.py):
- Each endpoint manually creates LLM service
- Each endpoint manually creates specific creator (CharacterCreator, ItemCreator, etc.)
- Lots of repetitive code for LLM service initialization
- Endpoint-specific mapping logic scattered throughout

IMPROVED APPROACH WITH FACTORY:
- Single factory instance manages all creation types
- Centralized LLM service management
- Unified API across all creation types
- Easier testing and maintenance
"""

from fastapi import HTTPException, Depends
from creation_factory import CreationFactory, create_character, create_item
from content_coordinator import ContentCoordinator
from enums import CreationOptions
from llm_service import create_llm_service


# EXAMPLE 1: Current character generation endpoint vs Factory approach

# CURRENT (from app.py lines 1650-1698):
@app.post("/api/v1/characters/generate", tags=["character-generation"])
async def generate_character_current(prompt: str, db = Depends(get_db)):
    """Current approach - lots of boilerplate"""
    try:
        # Manual LLM service creation
        llm_service = create_llm_service("ollama", model="tinyllama:latest", timeout=300)
        
        # Manual creator instantiation
        creator = CharacterCreator(llm_service)
        result = await creator.create_character(prompt)
        
        # Manual result processing...
        if result.success:
            character_data = result.data.get("raw_data", {})
            # ... lots of mapping logic ...
        
    except Exception as e:
        # Error handling...
        pass


# IMPROVED WITH FACTORY:
@app.post("/api/v1/characters/generate", tags=["character-generation"])
async def generate_character_factory(prompt: str, db = Depends(get_db)):
    """Factory approach - clean and simple"""
    try:
        # Use convenience function (handles LLM service internally)
        character = await create_character(
            prompt=prompt,
            llm_service=None  # Uses default Ollama/tinyllama
        )
        
        # Save to database using existing logic
        saved_character = await save_character_to_db(character, db)
        
        return {
            "success": True,
            "character": saved_character
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# EXAMPLE 2: Unified creation endpoint using factory

@app.post("/api/v1/content/create", tags=["unified-creation"])
async def create_content_unified(
    content_type: str,  # "character", "monster", "weapon", etc.
    prompt: str,
    additional_params: dict = None,
    db = Depends(get_db)
):
    """
    Unified creation endpoint that can create any type of D&D content.
    
    This replaces multiple separate endpoints with a single, flexible one.
    """
    try:
        # Convert string to enum
        creation_type = CreationOptions(content_type)
        
        # Create factory instance (could be dependency-injected)
        llm_service = create_llm_service("ollama", model="tinyllama:latest", timeout=300)
        factory = CreationFactory(llm_service, db)
        
        # Create content using factory
        params = {"prompt": prompt}
        if additional_params:
            params.update(additional_params)
            
        content = await factory.create(creation_type, **params)
        
        # Save to database (factory could handle this internally)
        saved_content = await save_content_to_db(content, creation_type, db)
        
        return {
            "success": True,
            "content_type": content_type,
            "content": saved_content
        }
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid content type: {content_type}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# EXAMPLE 3: Complex content generation using ContentCoordinator

@app.post("/api/v1/adventures/generate", tags=["adventure-generation"])
async def generate_adventure(
    theme: str,
    min_level: int = 1,
    max_level: int = 5,
    party_size: int = 4,
    db = Depends(get_db)
):
    """
    Generate a complete adventure with NPCs, monsters, and items.
    
    This demonstrates the ContentCoordinator for complex workflows.
    """
    try:
        llm_service = create_llm_service("ollama", model="tinyllama:latest", timeout=300)
        coordinator = ContentCoordinator(llm_service, db)
        
        # Generate complete adventure content
        adventure = await coordinator.generate_adventure_content(
            theme=theme,
            level_range=(min_level, max_level),
            party_size=party_size
        )
        
        return {
            "success": True,
            "adventure": adventure
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# EXAMPLE 4: Character with custom equipment

@app.post("/api/v1/characters/generate-with-equipment", tags=["character-generation"])
async def generate_character_with_equipment(
    character_prompt: str,
    custom_equipment: bool = True,
    db = Depends(get_db)
):
    """
    Generate a character with optionally custom equipment.
    
    Demonstrates ContentCoordinator for related content generation.
    """
    try:
        llm_service = create_llm_service("ollama", model="tinyllama:latest", timeout=300)
        coordinator = ContentCoordinator(llm_service, db)
        
        # Generate character with equipment
        result = await coordinator.generate_character_with_equipment(
            character_params={"prompt": character_prompt},
            custom_equipment=custom_equipment
        )
        
        return {
            "success": True,
            "character": result["character"],
            "custom_equipment": result.get("custom_equipment", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# BENEFITS OF THIS APPROACH:

# 1. REDUCED BOILERPLATE:
#    - No more manual LLM service creation in every endpoint
#    - No more manual creator instantiation
#    - Consistent error handling

# 2. UNIFIED API:
#    - Single endpoint can handle multiple content types
#    - Consistent parameter passing
#    - Easier for frontend to consume

# 3. COMPLEX WORKFLOWS:
#    - ContentCoordinator handles multi-step generation
#    - Automatic dependency management
#    - Thematic consistency across related content

# 4. EASIER TESTING:
#    - Mock the factory instead of individual creators
#    - Test creation configs independently
#    - Centralized validation logic

# 5. MAINTAINABILITY:
#    - Changes to LLM service affect only the factory
#    - New content types only require factory config updates
#    - Clear separation of concerns


# MIGRATION STRATEGY:

# Phase 1: Create factory and coordinator classes (✅ DONE)
# Phase 2: Add factory-based endpoints alongside existing ones (✅ DONE)  
# Phase 3: Gradually migrate existing endpoints to use factory (✅ DONE)
# Phase 4: Remove old endpoints and creators (✅ DONE)
# Phase 5: Add new content types easily through factory config (📋 PLANNED)

# PHASE 4 COMPLETION SUMMARY:
# ✅ Removed /api/v1/characters/generate → Use /api/v2/factory/create
# ✅ Removed /api/v1/items/create → Use /api/v2/factory/create  
# ✅ Removed /api/v1/npcs/create → Use /api/v2/factory/create
# ✅ Removed /api/v1/creatures/create → Use /api/v2/factory/create
# ✅ Cleaned up unused imports and Pydantic models
# ✅ Unified architecture under factory pattern
# 
# See PHASE_4_CLEANUP_COMPLETE.md for detailed migration guide.
