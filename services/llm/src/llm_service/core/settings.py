from functools import lru_cache
from typing import Dict, List, Optional

from typing import Dict
from pydantic import BaseModel, Field

from llm_service.schemas.text import ModelType
from pydantic_settings import BaseSettings, SettingsConfigDict


class OpenAIConfig(BaseModel):
    api_key: SecretStr
    primary_model: str = "gpt-4-turbo"
    fallback_model: str = "gpt-3.5-turbo"
    request_timeout: int = 60
    max_retries: int = 3


class GetImgAIConfig(BaseModel):
    api_key: SecretStr
    model_name: str = "stable-diffusion-v1-5"
    request_timeout: int = 120
    max_retries: int = 3


class DatabaseConfig(BaseModel):
    dsn: PostgresDsn
    min_pool_size: int = 5
    max_pool_size: int = 20
    pool_recycle_seconds: int = 1800


class RedisConfig(BaseModel):
    dsn: RedisDsn
    prefix: str = "llm_service"
    ssl: bool = True
    ssl_cert_reqs: str = "required"
    max_connections: int = 100


class MessageHubConfig(BaseModel):
    url: str
    token: SecretStr
    request_timeout: int = 30
    max_retries: int = 3


class RateLimits(BaseModel):
    """Rate limit configuration."""
    # Model-specific limits (requests per minute)
    model_rpm: Dict[ModelType, int] = Field(
        default={
            ModelType.GPT_4_TURBO: 200,
            ModelType.GPT_4: 200,
            ModelType.GPT_35_TURBO: 500,
        }
    )

    # GetImg.AI limits
    text_to_image_rpm: int = Field(50, description="Text-to-image requests per minute")
    image_to_image_rpm: int = Field(50, description="Image-to-image requests per minute")

    # General limits
    global_rpm: int = Field(1000, description="Global requests per minute")
    user_rpm: int = Field(100, description="Per-user requests per minute")
    text_generation_rpm: int = Field(default=100, gt=0)
    image_generation_rpm: int = Field(default=10, gt=0)
    user_rpm: int = Field(default=50, gt=0)
    global_rpm: int = Field(default=200, gt=0)


class CacheConfig(BaseModel):
    text_ttl_seconds: int = Field(default=3600, gt=0)  # 1 hour
    image_ttl_seconds: int = Field(default=86400, gt=0)  # 24 hours
    theme_ttl_seconds: int = Field(default=43200, gt=0)  # 12 hours


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_", env_nested_delimiter="__")

    # Service information
    service_name: str = "llm-service"
    environment: str = "development"
    log_level: str = "INFO"
    debug: bool = False

    # Server settings
    host: str = "0.0.0.0"
    port: int = 8100
    workers: int = 4
    api_prefix: str = "/api/v2"
    allowed_origins: List[str] = Field(default_factory=list)

    # Authentication
    auth_required: bool = True
    auth_token: SecretStr

    # External service configs
    openai: OpenAIConfig
    getimg_ai: GetImgAIConfig
    database: DatabaseConfig
    redis: RedisConfig
    message_hub: MessageHubConfig

    # Service limits and caching
    rate_limits: RateLimitConfig = Field(default_factory=RateLimitConfig)
    cache: CacheConfig = Field(default_factory=CacheConfig)

    # API keys for service-to-service communication
    service_api_keys: Dict[str, SecretStr] = Field(default_factory=dict)

    # Monitoring
    metrics_enabled: bool = True
    telemetry_enabled: bool = True


@lru_cache()
def get_settings() -> Settings:
    """Get application settings with caching."""
    return Settings()
