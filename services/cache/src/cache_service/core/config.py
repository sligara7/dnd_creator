from typing import List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, SecretStr


class Settings(BaseSettings):
    """Cache Service settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Service config
    SERVICE_NAME: str = "cache_service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API config
    HOST: str = "0.0.0.0"
    PORT: int = 8500
    WORKERS: int = 8  # Higher worker count for caching operations
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Database config
    POSTGRES_HOST: str = "cache_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "cache_db"
    POSTGRES_USER: str = "cache_user"
    POSTGRES_PASSWORD: str = "cache_pass"
    DATABASE_URL: PostgresDsn | None = None

    # Redis Primary config
    REDIS_PRIMARY_HOST: str = "cache_primary"
    REDIS_PRIMARY_PORT: int = 6379
    REDIS_PASSWORD: SecretStr
    REDIS_DB: int = 0

    # Redis Replica config
    REDIS_REPLICA_HOST: str = "cache_replica"
    REDIS_REPLICA_PORT: int = 6379

    # Cache config
    CACHE_MEMORY_LIMIT: str = "26GB"  # 80% of 32GB
    CACHE_EVICTION_POLICY: str = "volatile-lru"
    CACHE_DEFAULT_TTL: int = 3600  # 1 hour
    CACHE_KEY_PREFIX: str = "dnd:"

    # Message Hub config
    MESSAGE_HUB_URL: str = "http://message-hub:8200"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10

    # Performance config
    MAX_CONNECTIONS: int = 10000
    CONNECTION_TIMEOUT: int = 5
    OPERATION_TIMEOUT: int = 2
    READ_TIMEOUT: int = 1
    WRITE_TIMEOUT: int = 2
    
    # Batch operations
    BATCH_SIZE: int = 100
    PIPELINE_SIZE: int = 1000
    MAX_PIPELINE_COMMANDS: int = 10000
    
    # Replication and HA
    REPLICATION_TIMEOUT: int = 10
    FAILOVER_TIMEOUT: int = 60
    MIN_REPLICAS: int = 1
    
    # Circuit breaker config
    CIRCUIT_BREAKER_THRESHOLD: int = 50
    CIRCUIT_BREAKER_TIMEOUT: int = 30
    CIRCUIT_BREAKER_HALF_OPEN_REQUESTS: int = 3
    
    # Metrics config
    METRICS_ENABLED: bool = True
    METRICS_PORT: int = 8501
    METRICS_PATH: str = "/metrics"
    COLLECT_DETAILED_METRICS: bool = True
    
    # Local cache config
    LOCAL_CACHE_SIZE: int = 10000
    LOCAL_CACHE_TTL: int = 60  # 1 minute
    
    @property
    def get_database_url(self) -> str:
        """Get database URL"""
        if self.DATABASE_URL:
            return str(self.DATABASE_URL)
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def get_redis_primary_url(self) -> str:
        """Get Redis primary URL"""
        return f"redis://:{self.REDIS_PASSWORD.get_secret_value()}@{self.REDIS_PRIMARY_HOST}:{self.REDIS_PRIMARY_PORT}/{self.REDIS_DB}"
    
    @property
    def get_redis_replica_url(self) -> str:
        """Get Redis replica URL"""
        return f"redis://:{self.REDIS_PASSWORD.get_secret_value()}@{self.REDIS_REPLICA_HOST}:{self.REDIS_REPLICA_PORT}/{self.REDIS_DB}"
    
    def get_cache_key(self, service: str, key: str) -> str:
        """Get formatted cache key"""
        return f"{self.CACHE_KEY_PREFIX}{service}:{key}"


# Create global settings instance
settings = Settings()
