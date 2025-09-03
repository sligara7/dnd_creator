import uvicorn
from fastapi import FastAPI

from src.api import campaign, chapter, version_control, theme, content_generation
from src.core.config import settings
from src.core.middleware import setup_middleware


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title=settings.api_title,
        version=settings.api_version,
        description=settings.api_description,
        debug=settings.debug,
    )

    # Setup middleware
    setup_middleware(app, settings)

    # Include API routers
    app.include_router(campaign.router, prefix="/api/v2/campaigns", tags=["campaign"])
    app.include_router(chapter.router, prefix="/api/v2/campaigns/{campaign_id}/chapters", tags=["chapter"])
    app.include_router(version_control.router, prefix="/api/v2/campaigns/{campaign_id}/versions", tags=["version_control"])
    app.include_router(theme.router, prefix="/api/v2/themes", tags=["theme"])
    app.include_router(content_generation.router, prefix="/api/v2/campaigns/{campaign_id}", tags=["content_generation"])

    return app


app = create_app()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )

