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
    MESSAGE_HUB_URL: str = "http://message-hub:8200"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10

    # OpenAI config
    OPENAI_API_KEY: str
    OPENAI_MAX_RETRIES: int = 3
    OPENAI_TIMEOUT: int = 60
    OPENAI_MODEL: str = "gpt-4-1106-preview"
    OPENAI_MAX_TOKENS: int = 2048
    OPENAI_TEMPERATURE: float = 0.8

    # GetImg config
    GETIMG_API_KEY: str
    GETIMG_API_URL: str = "https://api.getimg.ai/v1"
    GETIMG_MAX_RETRIES: int = 3
    GETIMG_TIMEOUT: int = 60

    # LLM generation settings
    CACHE_TTL: int = 3600  # 1 hour
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_PERIOD: int = 60  # 1 minute
    MAX_REQUEST_SIZE: int = 16384  # 16KB
    
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
