"""Game Session Service Configuration.

This module handles all configuration for the Game Session Service, loading from
environment variables and providing strongly typed settings via Pydantic.
"""
from functools import lru_cache
from typing import List, Optional

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Service configuration settings."""

    # Basic Service Configuration
    APP_NAME: str = "game-session-service"
    APP_VERSION: str = "0.1.0"
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8400
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"

    # CORS Configuration
    CORS_ORIGINS: List[str] = Field(default_factory=lambda: ["*"])

    # Redis Configuration
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_SSL: bool = False
    REDIS_POOL_SIZE: int = 10
    REDIS_POOL_TIMEOUT: int = 30

    # Message Hub Configuration
    MESSAGE_HUB_HOST: str = "localhost"
    MESSAGE_HUB_PORT: int = 5672
    MESSAGE_HUB_USER: str = "guest"
    MESSAGE_HUB_PASSWORD: str = "guest"
    MESSAGE_HUB_VHOST: str = "/"
    MESSAGE_HUB_SSL: bool = False

    # Storage Service Configuration
    STORAGE_SERVICE_URL: str = "http://localhost:8500"
    STORAGE_SERVICE_TOKEN: Optional[str] = None

    # Security Configuration
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "RS256"
    JWT_TOKEN_EXPIRE_MINUTES: int = 60

    # WebSocket Configuration
    WS_HEARTBEAT_INTERVAL: int = 30
    WS_CONNECTION_TIMEOUT: int = 60
    WS_MAX_MESSAGE_SIZE: int = 65536  # 64KB

    # Rate Limiting
    RATE_LIMIT_WS_CONNECTIONS: str = "10/minute"
    RATE_LIMIT_WS_MESSAGES: str = "100/minute"
    RATE_LIMIT_COMBAT_ACTIONS: str = "20/minute"

    @field_validator("LOG_LEVEL")
    def validate_log_level(cls, v: str) -> str:
        """Validate log level is a valid value."""
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in valid_levels:
            raise ValueError(f"Log level must be one of {valid_levels}")
        return v.upper()

    @field_validator("LOG_FORMAT")
    def validate_log_format(cls, v: str) -> str:
        """Validate log format is a valid value."""
        valid_formats = ["json", "console"]
        if v.lower() not in valid_formats:
            raise ValueError(f"Log format must be one of {valid_formats}")
        return v.lower()

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()