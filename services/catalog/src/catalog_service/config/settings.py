"""Service configuration settings."""

import os
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Service configuration settings."""
    
    VERSION: str = "0.1.0"
    
    # Application settings
    APP_NAME: str = "Catalog Service"
    APP_DESCRIPTION: str = "D&D Content Catalog and Management Service"
    
    # API settings
    API_PREFIX: str = "/api/v2"
    
    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]  # Update for production
    
    # Message Hub settings
    MESSAGE_HUB_URL: str = os.getenv("MESSAGE_HUB_URL", "amqp://guest:guest@message-hub:5672/")
    
    # Application Performance
    MAX_WORKERS: int = 4  # Number of worker processes
    
    # Service URLs
    STORAGE_SERVICE_URL: str = os.getenv("STORAGE_SERVICE_URL", "http://storage-service:8010")
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_MAX_FAILURES: int = 5
    CIRCUIT_BREAKER_RESET_TIMEOUT: int = 60
    
    # Logging settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

settings = Settings()