"""
LLM Service Configuration

Configuration settings for the LLM service.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Service configuration settings."""
    
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8100
    debug: bool = False
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    
    # OpenAI Configuration
    openai_api_key: str
    openai_model: str = "gpt-4"
    openai_timeout: int = 30
    
    # Stable Diffusion Configuration
    sd_api_url: str = "http://localhost:7860"
    sd_timeout: int = 60
    
    # Rate Limiting
    redis_url: str = "redis://localhost:6379"
    rate_limit_default: int = 100  # requests per minute
    rate_limit_image: int = 10     # image generations per minute
    
    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 8101
    
    # Cache Configuration
    enable_cache: bool = True
    cache_ttl: int = 3600  # 1 hour
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
