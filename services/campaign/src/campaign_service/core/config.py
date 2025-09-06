"""Configuration settings for the campaign service."""
from functools import lru_cache
from typing import Any, Dict, Optional

from pydantic import PostgresDsn, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Application settings
    app_name: str = "Campaign Service"
    app_version: str = "0.1.0"
    api_prefix: str = "/api/v2"
    debug: bool = False

    # Database settings
    postgres_host: str = "localhost"
    postgres_port: int = 5432
    postgres_user: str = "postgres"
    postgres_password: SecretStr
    postgres_db: str = "campaign_service"
    sql_echo: bool = False
    db_pool_size: int = 5
    db_max_overflow: int = 10
    db_pool_timeout: int = 30
    db_pool_recycle: int = 1800

    @property
    def database_url(self) -> PostgresDsn:
        """Get the database URL.

        Returns:
            PostgresDsn: Database URL
        """
        return PostgresDsn.build(
            scheme="postgresql+asyncpg",
            username=self.postgres_user,
            password=self.postgres_password.get_secret_value(),
            host=self.postgres_host,
            port=self.postgres_port,
            path=self.postgres_db,
        )

    # Redis settings
    redis_host: str = "localhost"
    redis_port: int = 6379
    redis_db: int = 0
    redis_password: Optional[SecretStr] = None
    redis_pool_size: int = 10
    redis_pool_timeout: int = 30

    @property
    def redis_url(self) -> str:
        """Get the Redis URL.

        Returns:
            str: Redis URL
        """
        password = f":{self.redis_password.get_secret_value()}@" if self.redis_password else ""
        return f"redis://{password}{self.redis_host}:{self.redis_port}/{self.redis_db}"

    # Service integrations
    character_service_url: str = "http://character-service:8000"
    message_hub_url: str = "http://message-hub:8200"
    llm_service_url: str = "http://llm-service:8100"

    # Auth settings
    auth_secret_key: SecretStr
    auth_algorithm: str = "HS256"
    auth_token_expire_minutes: int = 30

    def dict(self, *args: Any, **kwargs: Any) -> Dict[str, Any]:
        """Override dict to handle SecretStr values.

        Returns:
            Dict[str, Any]: Settings as dictionary
        """
        d = super().dict(*args, **kwargs)
        # Convert SecretStr to string
        for k, v in d.items():
            if isinstance(v, SecretStr):
                d[k] = v.get_secret_value()
        return d


@lru_cache
def get_settings() -> Settings:
    """Get application settings.

    Returns:
        Settings: Application settings
    """
    return Settings()
