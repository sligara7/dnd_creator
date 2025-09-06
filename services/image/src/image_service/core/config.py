"""Configuration management for the image service."""

from functools import lru_cache
from typing import Optional

from pydantic import AnyHttpUrl, ConfigDict, PostgresDsn, RedisDsn, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuration settings for the image service."""
    
    model_config = SettingsConfigDict(env_prefix='IMAGE_', env_file='.env', case_sensitive=True)
    
    # Service configuration
    SERVICE_NAME: str = "image-service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # FastAPI configuration
    API_V2_PREFIX: str = "/api/v2"
    PROJECT_NAME: str = "D&D Image Service"
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list[AnyHttpUrl] = []
    
    @field_validator("BACKEND_CORS_ORIGINS")
    def validate_cors_origins(cls, v: list[str]) -> list[AnyHttpUrl]:
        """Validate and transform CORS origins."""
        if isinstance(v, str):
            return [AnyHttpUrl(origin.strip()) for origin in v.split(",")]
        return [AnyHttpUrl(origin.strip()) for origin in v]
    
    # Database configuration
    POSTGRES_SERVER: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_PORT: str = "5432"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None
    
    @field_validator("SQLALCHEMY_DATABASE_URI", mode='before')
    def assemble_db_connection(cls, v: Optional[str], values) -> PostgresDsn:
        """Construct database URI."""
        if v:
            return PostgresDsn(v)
        
        return PostgresDsn(
            f"postgresql+asyncpg://{values.data['POSTGRES_USER']}:{values.data['POSTGRES_PASSWORD']}"
            f"@{values.data['POSTGRES_SERVER']}:{values.data['POSTGRES_PORT']}/{values.data['POSTGRES_DB']}"
        )
    
    # Redis configuration
    REDIS_HOST: str
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: Optional[str] = None
    REDIS_URI: Optional[RedisDsn] = None
    
    @field_validator("REDIS_URI", mode='before')
    def assemble_redis_connection(cls, v: Optional[str], values) -> RedisDsn:
        """Construct Redis URI."""
        if v:
            return RedisDsn(v)
            
        auth = f":{values.data['REDIS_PASSWORD']}@" if values.data.get('REDIS_PASSWORD') else "@"
        return RedisDsn(f"redis://{auth}{values.data['REDIS_HOST']}:{values.data['REDIS_PORT']}")
    
    # Message Hub configuration
    MESSAGE_HUB_URL: AnyHttpUrl
    MESSAGE_HUB_TIMEOUT: int = 60
    
    # GetImg.AI configuration
    GETIMG_API_KEY: str
    GETIMG_API_URL: AnyHttpUrl = AnyHttpUrl("https://api.getimg.ai/v1")
    
    # Storage configuration
    STORAGE_SERVICE_URL: AnyHttpUrl
    
    # Cache configuration
    CACHE_TTL: int = 3600  # 1 hour default TTL
    CACHE_PREFIX: str = "image_service:"
    
    # Generation configuration
    MAX_CONCURRENT_GENERATIONS: int = 10
    GENERATION_TIMEOUT: int = 300  # 5 minutes
    BATCH_SIZE: int = 5
    
    # Queue configuration
    QUEUE_MAX_SIZE: int = 1000
    QUEUE_TIMEOUT: int = 600  # 10 minutes
    RETRY_LIMIT: int = 3
    RETRY_DELAY: int = 5  # seconds
    
    
@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
