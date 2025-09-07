from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from auth_service.core.config import settings
from auth_service.core.exceptions import AuthServiceError
from auth_service.core.monitoring import setup_monitoring
from auth_service.core.database import init_db

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

# Import API routes
from auth_service.api.v2.auth import router as auth_router

@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    await setup_monitoring()
    await init_db()

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    pass

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
app.include_router(auth_router)

@app.get("/health")
async def health_check():
    """Service health check endpoint"""
    return {
        "status": "healthy",
        "version": "2.0.0",
        "service": "auth-service"
    }

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint"""
    from auth_service.core.monitoring import get_metrics
    return await get_metrics()

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
