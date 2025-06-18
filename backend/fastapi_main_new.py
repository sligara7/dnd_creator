"""
FastAPI main application for D&D Character Creator.
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import sys
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent))

# Import configuration and services
from config_new import settings
from llm_service_new import create_llm_service

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    # Startup
    logger.info(f"Starting {settings.api_title} v{settings.api_version}")
    
    # Initialize services
    try:
        if settings.openai_api_key or settings.anthropic_api_key:
            llm_service = create_llm_service(
                provider=settings.llm_provider,
                api_key=getattr(settings, f"{settings.llm_provider}_api_key"),
                model=settings.llm_model,
                timeout=settings.llm_timeout
            )
            app.state.llm_service = llm_service
            logger.info(f"LLM service initialized: {settings.llm_provider}")
        else:
            logger.warning("No LLM API keys provided - LLM features will be disabled")
            app.state.llm_service = None
    except Exception as e:
        logger.error(f"Failed to initialize LLM service: {e}")
        app.state.llm_service = None
    
    yield
    
    # Shutdown
    logger.info("Shutting down application")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    debug=settings.debug,
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Health check endpoint
@app.get("/health", tags=["system"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "version": settings.api_version,
        "llm_available": app.state.llm_service is not None
    }


# API Information endpoint
@app.get("/", tags=["system"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.api_title,
        "version": settings.api_version,
        "description": settings.api_description,
        "docs_url": "/docs",
        "health_url": "/health"
    }


# Character management endpoints
@app.get("/api/v1/characters", tags=["characters"])
async def list_characters():
    """List all characters."""
    # TODO: Implement database query
    return {"characters": []}


@app.post("/api/v1/characters", tags=["characters"])
async def create_character(character_data: dict):
    """Create a new character."""
    # TODO: Implement character creation with database persistence
    return {"message": "Character creation endpoint - coming soon!", "data": character_data}


@app.get("/api/v1/characters/{character_id}", tags=["characters"])
async def get_character(character_id: int):
    """Get a specific character by ID."""
    # TODO: Implement database query
    return {"character_id": character_id, "message": "Character retrieval - coming soon!"}


@app.put("/api/v1/characters/{character_id}", tags=["characters"])
async def update_character(character_id: int, character_data: dict):
    """Update an existing character."""
    # TODO: Implement character update with database persistence
    return {"character_id": character_id, "message": "Character update - coming soon!", "data": character_data}


@app.delete("/api/v1/characters/{character_id}", tags=["characters"])
async def delete_character(character_id: int):
    """Delete a character."""
    # TODO: Implement character deletion
    return {"character_id": character_id, "message": "Character deletion - coming soon!"}


# Character generation endpoints
@app.post("/api/v1/generate/backstory", tags=["generation"])
async def generate_backstory(character_data: dict):
    """Generate a character backstory using LLM."""
    if not app.state.llm_service:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    try:
        prompt = f"Generate a D&D character backstory for: {character_data}"
        backstory = await app.state.llm_service.generate_content(prompt)
        return {"backstory": backstory}
    except Exception as e:
        logger.error(f"Backstory generation failed: {e}")
        raise HTTPException(status_code=500, detail="Backstory generation failed")


@app.post("/api/v1/generate/equipment", tags=["generation"])
async def generate_equipment(character_data: dict):
    """Generate character equipment suggestions using LLM."""
    if not app.state.llm_service:
        raise HTTPException(status_code=503, detail="LLM service not available")
    
    try:
        prompt = f"Generate D&D equipment suggestions for: {character_data}"
        equipment = await app.state.llm_service.generate_content(prompt)
        return {"equipment": equipment}
    except Exception as e:
        logger.error(f"Equipment generation failed: {e}")
        raise HTTPException(status_code=500, detail="Equipment generation failed")


# Validation endpoints
@app.post("/api/v1/validate/character", tags=["validation"])
async def validate_character(character_data: dict):
    """Validate a character's build for D&D 5e compliance."""
    # TODO: Implement character validation using existing validation module
    return {"valid": True, "message": "Character validation - coming soon!", "data": character_data}


# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"detail": "Endpoint not found"}
    )


@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "fastapi_main_new:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )
