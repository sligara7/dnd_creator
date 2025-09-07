"""Storage Service Configuration."""

from typing import Optional, List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    """Service configuration."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        env_prefix="STORAGE_",
    )

    # Service identification
    service_name: str = "storage-service"
    service_version: str = "0.1.0"
    environment: str = Field(default="development", env="ENVIRONMENT")

    # API settings
    api_prefix: str = "/api/v2"
    debug: bool = Field(default=False, env="DEBUG")
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8005, env="PORT")

    # Database settings
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/storage_db",
        env="DATABASE_URL",
    )
    database_pool_size: int = Field(default=10, env="DATABASE_POOL_SIZE")
    database_max_overflow: int = Field(default=20, env="DATABASE_MAX_OVERFLOW")
    database_echo: bool = Field(default=False, env="DATABASE_ECHO")

    # Redis settings
    redis_url: str = Field(
        default="redis://localhost:6379/0",
        env="REDIS_URL",
    )
    redis_pool_size: int = Field(default=10, env="REDIS_POOL_SIZE")
    redis_ttl: int = Field(default=3600, env="REDIS_TTL")

    # S3/MinIO settings
    s3_endpoint_url: Optional[str] = Field(default="http://localhost:9000", env="S3_ENDPOINT_URL")
    s3_access_key_id: str = Field(default="minioadmin", env="S3_ACCESS_KEY_ID")
    s3_secret_access_key: str = Field(default="minioadmin", env="S3_SECRET_ACCESS_KEY")
    s3_bucket_name: str = Field(default="dnd-storage", env="S3_BUCKET_NAME")
    s3_region: str = Field(default="us-east-1", env="S3_REGION")
    s3_use_ssl: bool = Field(default=False, env="S3_USE_SSL")

    # Storage settings
    max_upload_size: int = Field(default=100 * 1024 * 1024, env="MAX_UPLOAD_SIZE")  # 100MB
    chunk_size: int = Field(default=1024 * 1024, env="CHUNK_SIZE")  # 1MB
    temp_dir: str = Field(default="/tmp/storage", env="TEMP_DIR")
    
    # Version control settings
    max_versions: int = Field(default=10, env="MAX_VERSIONS")
    version_retention_days: int = Field(default=90, env="VERSION_RETENTION_DAYS")
    
    # Backup settings
    backup_enabled: bool = Field(default=True, env="BACKUP_ENABLED")
    backup_schedule: str = Field(default="0 0 * * *", env="BACKUP_SCHEDULE")  # Daily at midnight
    backup_retention_days: int = Field(default=30, env="BACKUP_RETENTION_DAYS")
    backup_bucket: str = Field(default="dnd-backups", env="BACKUP_BUCKET")

    # Lifecycle settings
    lifecycle_enabled: bool = Field(default=True, env="LIFECYCLE_ENABLED")
    archive_after_days: int = Field(default=90, env="ARCHIVE_AFTER_DAYS")
    delete_after_days: int = Field(default=365, env="DELETE_AFTER_DAYS")

    # Supported file types
    supported_image_types: List[str] = Field(
        default=["image/jpeg", "image/png", "image/gif", "image/webp"],
        env="SUPPORTED_IMAGE_TYPES",
    )
    supported_document_types: List[str] = Field(
        default=["application/pdf", "text/markdown", "text/plain"],
        env="SUPPORTED_DOCUMENT_TYPES",
    )

    # Message Hub settings
    message_hub_url: str = Field(
        default="http://message-hub:8200",
        env="MESSAGE_HUB_URL",
    )
    message_hub_timeout: int = Field(default=30, env="MESSAGE_HUB_TIMEOUT")
    message_hub_retries: int = Field(default=3, env="MESSAGE_HUB_RETRIES")

    # Security settings
    encryption_enabled: bool = Field(default=True, env="ENCRYPTION_ENABLED")
    encryption_key: Optional[str] = Field(default=None, env="ENCRYPTION_KEY")
    
    # Monitoring settings
    metrics_enabled: bool = Field(default=True, env="METRICS_ENABLED")
    metrics_port: int = Field(default=9095, env="METRICS_PORT")
    
    # CORS settings
    cors_origins: List[str] = Field(
        default=["http://localhost:3000", "http://localhost:8080"],
        env="CORS_ORIGINS",
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: List[str] = Field(
        default=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        env="CORS_ALLOW_METHODS",
    )
    cors_allow_headers: List[str] = Field(
        default=["*"],
        env="CORS_ALLOW_HEADERS",
    )

    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.lower() in ("development", "dev", "local")

    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment.lower() in ("production", "prod")

    @property
    def is_testing(self) -> bool:
        """Check if running in test mode."""
        return self.environment.lower() in ("testing", "test")


# Global settings instance
settings = Settings()
