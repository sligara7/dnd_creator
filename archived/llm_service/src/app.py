"""
LLM Service - Main Application

This service provides centralized LLM operations for text and image generation
across the D&D Character Creator application.
"""

import structlog
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from .config import Settings
from .providers import LLMProvider
from .models import TextGenerationRequest, ImageGenerationRequest
from .monitoring import PrometheusMetrics

# Initialize logging
logger = structlog.get_logger()

# Load configuration
settings = Settings()

# Initialize FastAPI app
app = FastAPI(
    title="D&D Character Creator LLM Service",
    description="Centralized LLM operations for text and image generation",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize metrics
metrics = PrometheusMetrics(app)

# Initialize LLM provider
llm_provider = LLMProvider(settings)

@app.post("/v1/generate/text")
async def generate_text(request: TextGenerationRequest):
    """Generate text using the appropriate LLM model."""
    try:
        logger.info("text_generation_request", 
                   service=request.service,
                   model=request.model)
        
        result = await llm_provider.generate_text(
            prompt=request.prompt,
            context=request.context,
            model=request.model
        )
        
        metrics.record_generation_success("text", request.service)
        return result
        
    except Exception as e:
        metrics.record_generation_failure("text", request.service)
        logger.error("text_generation_failed",
                    service=request.service,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/v1/generate/image")
async def generate_image(request: ImageGenerationRequest):
    """Generate an image using Stable Diffusion."""
    try:
        logger.info("image_generation_request",
                   service=request.service,
                   style=request.style)
        
        result = await llm_provider.generate_image(
            prompt=request.prompt,
            style=request.style
        )
        
        metrics.record_generation_success("image", request.service)
        return result
        
    except Exception as e:
        metrics.record_generation_failure("image", request.service)
        logger.error("image_generation_failed",
                    service=request.service,
                    error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Service health check endpoint."""
    try:
        # Verify LLM providers are accessible
        await llm_provider.check_health()
        return {"status": "healthy"}
    except Exception as e:
        logger.error("health_check_failed", error=str(e))
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return metrics.get_metrics()
