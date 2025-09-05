from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn, AmqpDsn


class Settings(BaseSettings):
    """Message Hub settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)
    
    # Service config
    SERVICE_NAME: str = "message_hub"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"
    
    # API config
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8200
    CORS_ORIGINS: List[str] = Field(default_factory=list)
    
    # Database config
    POSTGRES_HOST: str = "message_hub_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "message_hub"
    POSTGRES_USER: str = "message_hub_user"
    POSTGRES_PASSWORD: str = "message_hub_pass"
    DATABASE_URL: PostgresDsn | None = None
    
    # Redis config
    REDIS_HOST: str = "message_hub_cache"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None
    
    # RabbitMQ config
    RABBITMQ_HOST: str = "message_hub_queue"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "message_hub_user"
    RABBITMQ_PASSWORD: str = "message_hub_pass"
    RABBITMQ_VHOST: str = "/"
    RABBITMQ_URL: AmqpDsn | None = None
    
    # Service configuration
    EVENT_STORE_TTL: int = 86400  # 24 hours
    EVENT_BATCH_SIZE: int = 100
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    
    # Circuit breaker settings
    CIRCUIT_BREAKER_THRESHOLD: int = 5
    CIRCUIT_BREAKER_TIMEOUT: int = 60  # seconds
    CIRCUIT_BREAKER_HALF_OPEN_REQUESTS: int = 3
    
    # Service discovery settings
    SERVICE_TTL: int = 30  # seconds
    HEALTH_CHECK_INTERVAL: int = 10  # seconds
    
    @property
    def get_database_url(self) -> str:
        """Get database URL"""
        if self.DATABASE_URL:
            return str(self.DATABASE_URL)
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    @property
    def get_redis_url(self) -> str:
        """Get Redis URL"""
        if self.REDIS_URL:
            return str(self.REDIS_URL)
        auth = f":{self.REDIS_PASSWORD}@" if self.REDIS_PASSWORD else "@"
        return f"redis://{auth}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def get_rabbitmq_url(self) -> str:
        """Get RabbitMQ URL"""
        if self.RABBITMQ_URL:
            return str(self.RABBITMQ_URL)
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"


# Create global settings instance
settings = Settings()
