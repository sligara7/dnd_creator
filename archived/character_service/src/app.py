"""
Character Service FastAPI Application

Main application entry point that configures and runs the character service.
"""

from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from typing import Any, Dict

from src.core.logging_config import get_logger, configure_logging
from src.core.startup import run_startup_tasks
from src.models.database_models import init_database, get_db, CharacterDB
from src.core.config import settings

# Initialize logging first
configure_logging()
logger = get_logger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup and shutdown handler.
    This is called before the application starts and after it stops.
    """
    # Initialize database
    logger.info("initializing_database")
    init_database(settings.effective_database_url)
    
    # Run startup tasks
    logger.info("running_startup_tasks")
    db = CharacterDB()
    session = next(get_db())
    try:
        await run_startup_tasks(db, session)
        logger.info("startup_tasks_complete")
    except Exception as e:
        logger.error(
            "startup_tasks_failed",
            error=str(e),
            error_type=type(e).__name__
        )
        raise
    finally:
        session.close()
    
    # Application is starting up
    logger.info("application_starting")
    yield
    # Application is shutting down
    logger.info("application_stopping")

app = FastAPI(
    title="D&D Character Service",
    description="Service for creating and managing D&D 5e characters",
    version="1.0.0",
    lifespan=lifespan
)

@app.get("/health")
async def health_check() -> Dict[str, Any]:
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": "character",
        "version": "1.0.0"
    }

# Import and wire up metrics
from src.core.metrics_middleware import setup_metrics
from src.api.metrics_api import router as metrics_router

# Set up metrics collection
setup_metrics(app)

# Import and include API routers
from src.api.unified_catalog_api import router as catalog_router
app.include_router(catalog_router, prefix="/api/v1/catalog", tags=["catalog"])
app.include_router(metrics_router, prefix="/api/v2", tags=["metrics"])

# Journal API
from src.api.journal_api import router as journal_router
app.include_router(journal_router, prefix="/api/v2", tags=["journal"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
