"""Configuration module."""
from pathlib import Path
from typing import List

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='allow'
    )
    
    # Service settings
    SERVICE_NAME: str = "character-service"
    ENVIRONMENT: str = "development"
    DEBUG: bool = False
    TESTING: bool = False

    # CORS settings
    CORS_ORIGINS: List[str] = ["*"]

    # Database settings
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/character_service"
    DATABASE_MAX_CONNECTIONS: int = 20

    # Redis settings (for caching and cooldowns)
    REDIS_URL: str = "redis://localhost:6379/0"
    REDIS_MAX_CONNECTIONS: int = 10

    # Security settings
    SECRET_KEY: str = "your-secret-key"  # Change in production
    TOKEN_EXPIRE_MINUTES: int = 60
    
    # Game mechanics settings
    MAX_ABILITY_SCORE: int = 20
    BASE_HIT_DIE: int = 8
    MIN_CHARACTER_LEVEL: int = 1
    MAX_CHARACTER_LEVEL: int = 20
    
    # Cooldown settings
    CHARACTER_CREATION_COOLDOWN: int = 300  # seconds
    CHARACTER_DELETION_COOLDOWN: int = 300  # seconds

    # Path settings
    BASE_DIR: Path = Path(__file__).resolve().parent.parent

    # Override in tests
    if TESTING:
        DATABASE_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/character_test"
        REDIS_URL = "redis://localhost:6379/1"
        CHARACTER_CREATION_COOLDOWN = 0
        CHARACTER_DELETION_COOLDOWN = 0


def get_settings() -> Settings:
    """Get application settings."""
    return Settings()
