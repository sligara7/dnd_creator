from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """LLM Service settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Service config
    SERVICE_NAME: str = "llm_service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API config
    HOST: str = "0.0.0.0"
    PORT: int = 8100
    WORKERS: int = 4
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Database config
    POSTGRES_HOST: str = "llm_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "llm_db"
    POSTGRES_USER: str = "llm_user"
    POSTGRES_PASSWORD: str = "llm_pass"
    DATABASE_URL: PostgresDsn | None = None

    # Redis config
    REDIS_HOST: str = "llm_cache"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None

# Message Hub config
    MESSAGE_HUB_HOST: str = "message-hub"
    MESSAGE_HUB_PORT: int = 5672
    MESSAGE_HUB_USER: str = "llm_service"
    MESSAGE_HUB_PASSWORD: str | None = None
    MESSAGE_HUB_VHOST: str = "/"
    MESSAGE_HUB_EXCHANGE: str = "llm_service"
    MESSAGE_HUB_QUEUE_PREFIX: str = "llm_service"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10

    @property
    def message_hub_url(self) -> str:
        """Get Message Hub URL."""
        auth = f":{self.MESSAGE_HUB_PASSWORD}@" if self.MESSAGE_HUB_PASSWORD else "@"
        return f"amqp://{self.MESSAGE_HUB_USER}{auth}{self.MESSAGE_HUB_HOST}:{self.MESSAGE_HUB_PORT}/{self.MESSAGE_HUB_VHOST}"

    # OpenAI config
    OPENAI_API_KEY: str
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: int = 60
    OPENAI_MODEL: str = "gpt-5-nano"
    OPENAI_MAX_TOKENS: int = 8000  # Nano's 8k context window
    OPENAI_TEMPERATURE: float = 0.7  # Optimized for nano
    OPENAI_TOKEN_BUFFER: int = 1000  # Reserve for system messages
    OPENAI_STREAM_CHUNK_SIZE: int = 100  # Tokens per stream chunk
    OPENAI_MAX_PARALLEL: int = 5  # Max parallel nano requests

    # GetImg config
    GETIMG_API_KEY: str
    GETIMG_API_URL: str = "https://api.getimg.ai/v1"
    GETIMG_MAX_RETRIES: int = 3
    GETIMG_TIMEOUT: int = 60

    # LLM generation settings
    CACHE_TTL: int = 3600  # 1 hour
    RATE_LIMIT_REQUESTS: int = 1000  # Higher for nano
    RATE_LIMIT_PERIOD: int = 60  # 1 minute
    MAX_REQUEST_SIZE: int = 32768  # 32KB for nano's larger context
    
    # Theme generation settings
    THEME_VALIDATION_THRESHOLD: float = 0.8
    THEME_MAX_VALIDATION_RETRIES: int = 3
    THEME_CACHE_TTL: int = 7200  # 2 hours
    THEME_BATCH_SIZE: int = 10
    
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


# Create global settings instance
settings = Settings()
