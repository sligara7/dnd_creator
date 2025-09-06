import os
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from api_gateway.middleware.auth import JWTBearer, APIKeyAuth
from api_gateway.middleware.rate_limit import RateLimitMiddleware
from api_gateway.monitoring.logging import RequestLoggingMiddleware
from api_gateway.routers import discovery, monitoring

# Load configuration from environment
AUTH_SERVICE_URL = os.getenv('AUTH_SERVICE_URL', 'http://auth-service:8300')

# Initialize authentication handlers
jwt_auth = JWTBearer(AUTH_SERVICE_URL)
api_key_auth = APIKeyAuth(AUTH_SERVICE_URL)

app = FastAPI(
    title="D&D Character Creator API Gateway",
    description="API Gateway Service for the D&D Character Creator system",
    version="0.1.0",
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # This will be restricted in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add request logging middleware
app.add_middleware(RequestLoggingMiddleware)

# Add rate limiting middleware
app.add_middleware(
    RateLimitMiddleware,
    requests_per_minute=100,
    burst_size=50
)

# Include routers
app.include_router(discovery.router)
app.include_router(monitoring.router)

# Configure security requirements
async def get_token_or_api_key(token: str = Depends(jwt_auth), api_key: bool = Depends(api_key_auth)):
    """Allow either JWT token or API key authentication."""
    return token or api_key

@app.get("/health", dependencies=[Depends(get_token_or_api_key)])
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": "0.1.0",
        "service": "api-gateway"
    }

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint."""
    # TODO: Implement metrics collection
    return {
        "metrics": "Coming soon"
    }
