"""
Configuration settings for the D&D Character Creator API.
"""
from typing import Optional
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # API Configuration
    api_title: str = "D&D Character Creator API"
    api_version: str = "1.0.0"
    api_description: str = "RESTful API for D&D 5e character creation and management"
    
    # Server Configuration
    host: str = "0.0.0.0"
    port: int = 8000
    debug: bool = False
    
    # Database Configuration
    database_url: Optional[str] = None  # Set to use PostgreSQL, leave None for SQLite
    database_echo: bool = False  # Set to True for SQL query logging
    db_password: Optional[str] = None  # Additional database password field
    
    # SQLite Configuration (used when database_url is None)
    sqlite_path: str = "dnd_characters.db"  # Path to SQLite database file
    
    @property
    def is_sqlite(self) -> bool:
        """Check if using SQLite database."""
        return self.database_url is None
    
    @property
    def effective_database_url(self) -> str:
        """Get the effective database URL for SQLAlchemy."""
        if self.database_url:
            return self.database_url
        return f"sqlite:///{self.sqlite_path}"
    
    # External LLM Service Configuration
    llm_provider: str = "openai"  # "openai", "anthropic", "cohere", etc.
    openai_api_key: Optional[str] = None
    openai_model: Optional[str] = None  # Allow OpenAI model override
    anthropic_api_key: Optional[str] = None
    
    # LLM Request Configuration
    llm_model: str = "gpt-3.5-turbo"  # Default model
    llm_timeout: int = 30  # Request timeout in seconds
    llm_max_retries: int = 3
    llm_temperature: float = 0.7
    
    # Security Configuration
    secret_key: str = "your-secret-key-change-this-in-production"
    access_token_expire_minutes: int = 30
    
    # CORS Configuration
    cors_origins: str = "http://localhost:3000,http://localhost:8080"
    
    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        if isinstance(self.cors_origins, str):
            return [origin.strip() for origin in self.cors_origins.split(",")]
        return self.cors_origins
    
    # Logging Configuration
    log_level: str = "INFO"
    log_format: str = "json"  # "json" or "text"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from .env


# Global settings instance
settings = Settings()
