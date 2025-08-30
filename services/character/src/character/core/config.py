"""
Character Service Configuration

This module provides centralized configuration management for the character service
using Pydantic settings management.
"""

from functools import lru_cache
from typing import List, Optional

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Character Service Settings."""
    
    # Service Information
    service_name: str = "character"
    version: str = "0.1.0"
    debug: bool = False
    port: int = 8000
    
    # Security
    secret_key: str
    auth_service_url: str = "http://auth:8500"
    token_expire_minutes: int = 15
    
    # CORS
    cors_origins: List[str] = ["*"]
    
    # Database
    database_url: str
    database_pool_size: int = 20
    database_pool_recycle: int = 1800
    database_echo: bool = False
    
    # Message Hub
    message_hub_url: str = "http://message:8200"
    message_hub_timeout: int = 5
    
    # LLM Service
    llm_service_url: str = "http://llm:8100"
    llm_timeout: int = 30
    
    # Redis Cache
    redis_url: Optional[str] = None
    redis_timeout: int = 5
    
    # Prometheus Metrics
    enable_metrics: bool = True
    metrics_port: int = 8001
    
    # Character Validation
    max_level: int = 20
    max_ability_score: int = 30
    max_proficiency_bonus: int = 6
    
    # Content Generation
    enable_custom_content: bool = True
    max_custom_items: int = 100
    content_approval_required: bool = True
    
    # Journal System
    max_journal_entries: int = 1000
    max_entry_length: int = 10000
    
    # Version Control
    max_versions: int = 100
    max_branches: int = 10
    
    # Performance
    request_timeout: int = 60
    max_concurrent_creations: int = 10
    character_cache_ttl: int = 3600
    
    # Logging
    log_level: str = "INFO"
    log_format: str = "json"
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
