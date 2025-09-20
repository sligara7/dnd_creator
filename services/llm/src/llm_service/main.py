from typing import Dict

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from llm_service.core.config import settings
from llm_service.api import text, character, image, theme
from llm_service.core.exceptions import LLMServiceError
from llm_service.core.monitoring import setup_monitoring
from llm_service.core.message_hub import MessageHubClient
from llm_service.providers.openai import OpenAIProvider
from llm_service.providers.getimg import GetImgProvider

app = FastAPI(
    title="LLM Service",
    description="LLM and Image Generation Service for D&D Character Creator",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global dependencies
openai_provider = OpenAIProvider(api_key=settings.OPENAI_API_KEY)
getimg_provider = GetImgProvider(api_key=settings.GETIMG_API_KEY)
message_hub = MessageHubClient(settings=settings)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await openai_provider.setup()
    await getimg_provider.setup()
    await message_hub.setup()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await openai_provider.cleanup()
    await getimg_provider.cleanup()
    await message_hub.cleanup()

@app.exception_handler(LLMServiceError)
async def llm_service_exception_handler(request: Request, exc: LLMServiceError):
    """Handle LLM Service specific errors"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.error_code,
                "message": exc.message,
                "details": {
                    "request_id": request.headers.get("X-Request-ID"),
                    "timestamp": exc.timestamp.isoformat(),
                },
            }
        },
    )

# Include API routes
app.include_router(text.router)
app.include_router(character.router)
app.include_router(image.router)
app.include_router(theme.router)

@app.get("/health")
async def health_check() -> Dict:
    """Service health check endpoint"""
    openai_health = await openai_provider.health_check()
    getimg_health = await getimg_provider.health_check()
    message_hub_health = bool(message_hub._connection and message_hub._connection.is_closed is False)
    
    # Determine overall health
    all_healthy = all([openai_health, getimg_health, message_hub_health])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "openai": "healthy" if openai_health else "degraded",
            "getimg_ai": "healthy" if getimg_health else "degraded",
            "message_hub": "healthy" if message_hub_health else "degraded",
            "queue": "healthy",  # To be implemented with queue metrics
        },
        "metrics": {
            "text_generation_rate": 0.0,  # To be implemented
            "image_generation_rate": 0.0,  # To be implemented
            "error_rate": 0.0,  # To be implemented
            "queue_length": 0,  # To be implemented
        },
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    # Return prometheus metrics
    return await setup_monitoring.get_metrics()

def start() -> None:
    """Entry point for running in production"""
    import uvicorn
    uvicorn.run(
        "llm_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_config=None,  # Use structlog configuration
    )

def dev() -> None:
    """Entry point for running in development"""
    import uvicorn
    uvicorn.run(
        "llm_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None,  # Use structlog configuration
    )

if __name__ == "__main__":
    dev()
