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
