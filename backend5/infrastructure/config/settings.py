"""
Application Settings

Main configuration using Pydantic for validation and environment variable loading.
"""

from typing import Optional, List
from pydantic import BaseSettings, validator
import os

class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "D&D Character Creator"
    app_version: str = "1.0.0"
    debug: bool = False
    log_level: str = "INFO"
    
    # Database
    database_url: str = "sqlite:///./dnd_creator.db"
    database_echo: bool = False
    
    # External APIs
    openai_api_key: Optional[str] = None
    openai_model: str = "gpt-4"
    anthropic_api_key: Optional[str] = None
    
    # Generation settings
    generation_timeout: int = 300
    max_concurrent_generations: int = 5
    default_quality_threshold: float = 0.8
    enable_caching: bool = True
    
    # Cache settings
    redis_url: str = "redis://localhost:6379"
    cache_ttl: int = 3600
    
    # Security
    secret_key: str = "your-secret-key-here"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # CORS
    allowed_origins: List[str] = ["http://localhost:3000"]
    
    @validator('log_level')
    def validate_log_level(cls, v):
        valid_levels = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        if v.upper() not in valid_levels:
            raise ValueError(f'Invalid log level. Must be one of: {valid_levels}')
        return v.upper()
    
    class Config:
        env_file = ".env"
        case_sensitive = False

# Singleton settings instance
_settings: Optional[Settings] = None

def get_settings() -> Settings:
    """Get application settings (singleton pattern)."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings