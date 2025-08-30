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
    sqlite_path: str = "data/dnd_characters.db"  # Path to SQLite database file in data directory
    
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
    
    # External Service Configuration
    message_hub_url: str = "http://message_hub:8200"
    message_hub_timeout: int = 30
    
    # Security Configuration - MUST be provided via environment variables
    secret_key: Optional[str] = None  # Must be set via SECRET_KEY environment variable
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
        # Do not load from .env files - all secrets must come from host environment
        env_file = None
        env_file_encoding = "utf-8"
        extra = "ignore"  # Ignore extra fields from environment
    
    def validate_required_settings(self) -> None:
        """Validate that all required environment variables are set."""
        missing_vars = []
        
        if not self.secret_key:
            missing_vars.append("SECRET_KEY")
        
        if missing_vars:
            raise ValueError(
                f"Missing required environment variables: {', '.join(missing_vars)}. "
                "These must be provided via host environment variables."
            )


# Global settings instance
settings = Settings()

# Validate required settings on import
settings.validate_required_settings()
