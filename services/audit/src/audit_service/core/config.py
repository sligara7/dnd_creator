from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Audit Service settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Service config
    SERVICE_NAME: str = "audit_service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API config
    HOST: str = "0.0.0.0"
    PORT: int = 8400
    WORKERS: int = 8  # Higher worker count for event processing
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Database config
    POSTGRES_HOST: str = "audit_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "audit_db"
    POSTGRES_USER: str = "audit_user"
    POSTGRES_PASSWORD: str = "audit_pass"
    DATABASE_URL: PostgresDsn | None = None

    # Redis config
    REDIS_HOST: str = "audit_cache"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None

    # Elasticsearch config
    ELASTICSEARCH_HOST: str = "audit_search"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_USER: str | None = None
    ELASTICSEARCH_PASSWORD: str | None = None
    ELASTICSEARCH_VERIFY_CERTS: bool = False
    ES_INDEX_PREFIX: str = "audit-"
    ES_RETENTION_DAYS: int = 365  # 1 year retention in ES

    # MinIO config
    MINIO_HOST: str = "audit_storage"
    MINIO_PORT: int = 9000
    MINIO_ROOT_USER: str = "minioadmin"
    MINIO_ROOT_PASSWORD: str = "minioadmin"
    MINIO_BUCKET_NAME: str = "audit-archive"
    ARCHIVE_RETENTION_YEARS: int = 7  # 7 years retention in archive

    # Message Hub config
    MESSAGE_HUB_URL: str = "http://message-hub:8200"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10

    # Event processing config
    BATCH_SIZE: int = 1000
    FLUSH_INTERVAL: int = 60  # seconds
    MAX_RETRIES: int = 3
    RETRY_DELAY: int = 5  # seconds
    
    # Security config
    EVENT_ENCRYPTION_KEY: str | None = None
    FIELD_ENCRYPTION_KEY: str | None = None
    DATA_MASKING_ENABLED: bool = True
    
    # Compliance config
    GDPR_MODE: bool = True
    RETAIN_PII_DAYS: int = 90
    ANONYMIZE_AFTER_DAYS: int = 180
    
    # Analysis config
    ANOMALY_DETECTION_ENABLED: bool = True
    PATTERN_DETECTION_ENABLED: bool = True
    THREAT_DETECTION_ENABLED: bool = True
    ANALYSIS_INTERVAL: int = 300  # 5 minutes
    
    # Metrics config
    METRICS_PORT: int = 8401
    METRICS_PATH: str = "/metrics"
    
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
    def get_elasticsearch_url(self) -> str:
        """Get Elasticsearch URL"""
        auth = ""
        if self.ELASTICSEARCH_USER and self.ELASTICSEARCH_PASSWORD:
            auth = f"{self.ELASTICSEARCH_USER}:{self.ELASTICSEARCH_PASSWORD}@"
        return f"http://{auth}{self.ELASTICSEARCH_HOST}:{self.ELASTICSEARCH_PORT}"
    
    @property
    def get_minio_url(self) -> str:
        """Get MinIO URL"""
        return f"http://{self.MINIO_HOST}:{self.MINIO_PORT}"


# Create global settings instance
settings = Settings()
