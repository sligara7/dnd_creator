"""Auth service configuration."""
from functools import lru_cache
from typing import Optional

from pydantic import BaseModel, BaseSettings, Field, HttpUrl, RedisDsn, validator


class Settings(BaseSettings):
    """Auth service settings."""

    # Service name and version
    service_name: str = "auth_service"
    version: str = "2.0.0"

    # Service URLs
    storage_service_url: HttpUrl = Field(
        "http://storage-service:8000",
        description="URL of the storage service"
    )

    # Security
    secret_key: str = Field(
        ...,
        description="Secret key for JWT signing"
    )
    jwt_algorithm: str = Field(
        "RS256",
        description="Algorithm for JWT signing"
    )
    token_expiration: int = Field(
        900,
        description="Access token expiration in seconds"
    )
    refresh_expiration: int = Field(
        604800,
        description="Refresh token expiration in seconds"
    )

    # Redis configuration
    redis_url: RedisDsn = Field(
        "redis://redis:6379/0",
        description="Redis URL for session storage"
    )

    # Service configuration
    max_login_attempts: int = Field(
        5,
        description="Maximum failed login attempts before lockout"
    )
    lockout_duration: int = Field(
        300,
        description="Account lockout duration in seconds"
    )
    password_history: int = Field(
        5,
        description="Number of previous passwords to check"
    )
    min_password_length: int = Field(
        12,
        description="Minimum password length"
    )

    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_prefix = "AUTH_"


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance.

    Returns:
        Settings instance
    """
    return Settings()