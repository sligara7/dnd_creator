"""Character Service - FastAPI Application Entry Point"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from character_service.api.v2.router import router as api_v2_router
from character_service.core import config

app = FastAPI(
    title="D&D Character Service",
    description="Character Creation and Management for D&D 5e 2024",
    version="2.0.0",
)

# CORS middleware configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API router - v2 matches ICD/SRD specifications
app.include_router(api_v2_router, prefix="/api/v2")
