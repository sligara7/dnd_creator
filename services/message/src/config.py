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
    
    # Retry Manager Settings
    retry_max_attempts: int = 5
    retry_base_delay: float = 1.0  # seconds
    retry_max_delay: float = 300.0  # 5 minutes
    retry_jitter: float = 0.1
    dead_letter_ttl: int = 86400  # 24 hours
    
    # Priority Queue Settings
    priority_levels: int = 5
    queue_processing_interval: float = 0.1  # seconds
    max_messages_per_service: int = 1000
    queue_quotas_enabled: bool = True
    
    # Enhanced Service Registry Settings
    load_balancing_strategy: str = "round_robin"  # round_robin, least_connections, weighted
    health_check_interval: int = 30  # seconds
    health_check_timeout: int = 5  # seconds
    max_instances_per_service: int = 10
    dependency_check_enabled: bool = True
    
    # Event Store Settings
    wal_enabled: bool = True
    wal_flush_interval: int = 1  # seconds
    snapshot_interval: int = 1000  # events
    compaction_threshold: float = 0.5  # 50% deleted events
    
    # Monitoring
    enable_metrics: bool = True
    enable_tracing: bool = True
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False
    )
