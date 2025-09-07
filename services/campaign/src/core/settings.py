"""Campaign Service configuration."""
from typing import Dict, List, Optional
from pydantic import Field, PostgresDsn, SecretStr
from pydantic_settings import BaseSettings


class DatabaseSettings(BaseSettings):
    """Database connection settings."""
    dsn: PostgresDsn = Field(..., description="Database connection string")
    min_pool_size: int = Field(5, description="Minimum DB pool size")
    max_pool_size: int = Field(20, description="Maximum DB pool size")
    echo: bool = Field(False, description="Echo SQL statements")


class LLMServiceSettings(BaseSettings):
    """LLM Service connection settings."""
    url: str = Field(..., description="LLM Service URL")
    token: SecretStr = Field(..., description="LLM Service API token")
    timeout: int = Field(60, description="Request timeout")
    max_retries: int = Field(3, description="Max request retries")


class MessageHubSettings(BaseSettings):
    """Message Hub connection settings."""
    url: str = Field(..., description="Message Hub URL")
    token: SecretStr = Field(..., description="Message Hub API token")
    timeout: int = Field(30, description="Request timeout")
    max_retries: int = Field(3, description="Max request retries")


class VersionControlSettings(BaseSettings):
    """Version control system settings."""
    storage_path: str = Field("/data/campaigns", description="Path to store campaign version data")
    max_branches: int = Field(100, description="Maximum branches per campaign")
    max_history: int = Field(1000, description="Maximum version history per campaign")


class ThemeSettings(BaseSettings):
    """Theme system settings."""
    data_path: str = Field("/data/themes", description="Path to theme data files")
    cache_ttl: int = Field(3600, description="Theme cache TTL in seconds")
    style_presets: List[str] = Field(
        default_factory=lambda: [
            "fantasy", "horror", "mystery", "western",
            "steampunk", "cyberpunk", "historical"
        ]
    )


class Settings(BaseSettings):
    """Application settings."""
    # Service information
    service_name: str = "campaign-service"
    environment: str = Field("development", env="ENV")
    debug: bool = Field(False, env="DEBUG")
    log_level: str = Field("INFO", env="LOG_LEVEL")

    # API configuration
    api_title: str = "Campaign Service API"
    api_version: str = "2.0.0"
    api_description: str = "D&D Campaign Creation and Management Service"
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8001, env="PORT")

    # Security
    api_token: Optional[SecretStr] = Field(None, env="API_TOKEN")
    cors_origins: List[str] = Field(
        default_factory=lambda: ["http://localhost:3000"]
    )

    # Rate limiting
    rate_limit_rpm: int = Field(120, description="Requests per minute per client")
    rate_limit_burst: int = Field(30, description="Burst limit per client")

    # Dependencies with defaults for testing
    database: Optional[DatabaseSettings] = None
    llm_service: Optional[LLMServiceSettings] = None
    message_hub: Optional[MessageHubSettings] = None
    version_control: Optional[VersionControlSettings] = None
    theme: Optional[ThemeSettings] = None

    # Prometheus metrics
    metrics_enabled: bool = True
    metrics_port: int = 9001

    # Service limits
    max_campaigns_per_user: int = 100
    max_chapters_per_campaign: int = 50
    max_npcs_per_campaign: int = 200
    max_locations_per_campaign: int = 100
    content_length_limits: Dict[str, int] = Field(
        default_factory=lambda: {
            "campaign_concept": 5000,
            "chapter_content": 10000,
            "npc_description": 2000,
            "location_description": 3000,
            "plot_branch": 1000,
        }
    )

    class Config:
        """Pydantic model config."""
        case_sensitive = True
        env_prefix = "CAMPAIGN_"
        env_nested_delimiter = "__"

    def validate_service_config(self) -> None:
        """Validate that service configuration is complete and valid."""
        # Add service-specific validation here
        if not self.api_token:
            raise ValueError("API token is required")
        if self.database and not self.database.dsn:
            raise ValueError("Database DSN is required")
        if self.llm_service and not self.llm_service.token:
            raise ValueError("LLM Service token is required")
        if self.message_hub and not self.message_hub.token:
            raise ValueError("Message Hub token is required")


# Global settings instance
settings = Settings()

# Validate settings in non-test environments
import os
if not os.getenv("TESTING", "").lower() == "true":
    settings.validate_service_config()
