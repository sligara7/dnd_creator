from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from auth_service.core.config import settings
from auth_service.api.routes import api_router
from auth_service.core.exceptions import AuthServiceError
from auth_service.core.monitoring import setup_monitoring
from auth_service.security.key_manager import KeyManager
from auth_service.security.token_service import TokenService

app = FastAPI(
    title="Auth Service",
    description="Authentication and Authorization Service for D&D Character Creator",
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
key_manager = KeyManager(
    private_key_path=settings.PRIVATE_KEY_PATH,
    public_key_path=settings.PUBLIC_KEY_PATH,
)
token_service = TokenService(key_manager)

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await key_manager.setup()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    await key_manager.cleanup()

@app.exception_handler(AuthServiceError)
async def auth_service_exception_handler(request: Request, exc: AuthServiceError):
    """Handle Auth Service specific errors"""
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
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Service health check endpoint"""
    # Check health of all dependencies
    key_status = await key_manager.health_check()
    token_status = await token_service.health_check()
    
    # Determine overall health
    all_healthy = all([key_status, token_status])
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "version": settings.VERSION,
        "components": {
            "key_manager": "healthy" if key_status else "degraded",
            "token_service": "healthy" if token_status else "degraded",
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
        "auth_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        workers=settings.WORKERS,
        log_config=None,  # Use structlog configuration
    )

def dev() -> None:
    """Entry point for running in development"""
    import uvicorn
    uvicorn.run(
        "auth_service.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True,
        log_config=None,  # Use structlog configuration
    )

if __name__ == "__main__":
    dev()
