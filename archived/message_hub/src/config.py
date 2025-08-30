"""
Message Hub Configuration

Configuration settings for the message hub service.
"""

from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Service configuration settings."""
    
    # API Configuration
    host: str = "0.0.0.0"
    port: int = 8200
    debug: bool = False
    
    # CORS Configuration
    cors_origins: List[str] = ["*"]
    
    # Circuit Breaker Configuration
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_reset_timeout: int = 60
    
    # Message Queue Configuration
    redis_url: str = "redis://localhost:6379"
    message_timeout: int = 30
    
    # Service Discovery
    service_check_interval: int = 30
    service_timeout: int = 10
    
    # Event Store
    database_url: str = "postgresql://msg_hub_user:password@localhost:5432/msg_hub"
    event_batch_size: int = 100
    event_retention_days: int = 30
    
    # Subscription Settings
    subscription_batch_size: int = 100
    subscription_poll_interval: int = 5  # seconds
    
    # Transaction Settings
    transaction_timeout: int = 30  # seconds
    max_completed_transactions: int = 1000
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
