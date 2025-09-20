"""Application configuration."""

from typing import Optional

from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings."""
    APP_NAME: str = "character_service"
    DEBUG: bool = False
    API_PREFIX: str = "/api/v2"
    ENVIRONMENT: str = "development"

    # RabbitMQ Settings
    RABBITMQ_HOST: str = "rabbitmq"
    RABBITMQ_PORT: int = 5672
    RABBITMQ_USER: str = "guest"
    RABBITMQ_PASS: str = "guest"
    RABBITMQ_VHOST: str = "/"

    @property
    def RABBITMQ_URL(self) -> str:
        """Get RabbitMQ connection URL."""
        return f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASS}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}/{self.RABBITMQ_VHOST}"

    # Auth Settings
    SECRET_KEY: str = Field(default="secret", env="SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # CORS Settings
    CORS_ORIGINS: list[str] = ["*"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_ALLOW_METHODS: list[str] = ["*"]
    CORS_ALLOW_HEADERS: list[str] = ["*"]

    # Monitoring Settings
    MONITORING_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()

"""Configuration Settings for Character Service"""

from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "D&D Character Service"
    
    # CORS Configuration
    CORS_ORIGINS: List[str] = ["*"]
    
    # Database Configuration
    DATABASE_URL: str
    
    # Message Hub Configuration
    MESSAGE_HUB_URL: str
    
    # Security Configuration
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Service Integration Configuration
    CAMPAIGN_SERVICE_URL: str
    IMAGE_SERVICE_URL: str
    CATALOG_SERVICE_URL: str
    LLM_SERVICE_URL: str
    
    # Cache Configuration
    REDIS_URL: str
    
    # Logging Configuration
    LOG_LEVEL: str = "INFO"
    
    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
