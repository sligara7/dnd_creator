"""
Application Settings

Main configuration using Pydantic for validation and environment variable loading.
Provides centralized configuration management with proper validation and type safety.
"""

from typing import Optional, List, Union
from pydantic import BaseSettings, validator, Field, SecretStr
from pathlib import Path
import os
import secrets

# Import enums from core domain
from core.enums import (
    Environment,
    LogLevel, 
    SecurityAlgorithm,
    CacheBackend,
    DatabaseType
)
from .environment import get_environment_config


class DatabaseSettings(BaseSettings):
    """Database-specific configuration settings."""
    
    # Database connection
    database_url: str = Field("sqlite:///./dnd_creator.db", env='DATABASE_URL')
    database_echo: bool = Field(False, env='DATABASE_ECHO')
    
    # Connection pool settings (for PostgreSQL/MySQL)
    db_pool_size: int = Field(5, env='DB_POOL_SIZE')
    db_max_overflow: int = Field(10, env='DB_MAX_OVERFLOW')
    db_pool_timeout: int = Field(30, env='DB_POOL_TIMEOUT')
    db_pool_recycle: int = Field(3600, env='DB_POOL_RECYCLE')
    
    # Database maintenance
    auto_migrate: bool = Field(True, env='AUTO_MIGRATE')
    backup_enabled: bool = Field(True, env='BACKUP_ENABLED')
    backup_interval_hours: int = Field(24, env='BACKUP_INTERVAL_HOURS')
    
    @property
    def database_type(self) -> DatabaseType:
        """Get database type from URL."""
        if self.database_url.startswith('sqlite'):
            return DatabaseType.SQLITE
        elif self.database_url.startswith('postgresql'):
            return DatabaseType.POSTGRESQL
        elif self.database_url.startswith('mysql'):
            return DatabaseType.MYSQL
        else:
            return DatabaseType.SQLITE  # Default fallback
    
    @validator('database_url')
    def validate_database_url(cls, v):
        """Validate database URL format."""
        if not v or not isinstance(v, str):
            raise ValueError("Database URL must be a non-empty string")
        
        valid_prefixes = ['sqlite://', 'postgresql://', 'mysql://']
        if not any(v.startswith(prefix) for prefix in valid_prefixes):
            raise ValueError(f"Database URL must start with one of: {valid_prefixes}")
        
        return v


class CacheSettings(BaseSettings):
    """Cache-specific configuration settings."""
    
    # Redis configuration
    redis_url: str = Field("redis://localhost:6379", env='REDIS_URL')
    redis_password: Optional[SecretStr] = Field(None, env='REDIS_PASSWORD')
    redis_db: int = Field(0, env='REDIS_DB')
    redis_timeout: int = Field(5, env='REDIS_TIMEOUT')
    
    # Cache behavior
    cache_backend: CacheBackend = Field(CacheBackend.REDIS, env='CACHE_BACKEND')
    cache_ttl: int = Field(3600, env='CACHE_TTL')  # 1 hour default
    cache_prefix: str = Field("dnd_creator", env='CACHE_PREFIX')
    
    # Cache policies
    enable_caching: bool = Field(True, env='ENABLE_CACHING')
    cache_generation_results: bool = Field(True, env='CACHE_GENERATION_RESULTS')
    cache_validation_results: bool = Field(True, env='CACHE_VALIDATION_RESULTS')
    
    @validator('cache_backend', pre=True)
    def validate_cache_backend(cls, v):
        """Validate cache backend."""
        if isinstance(v, str):
            try:
                return CacheBackend(v.lower())
            except ValueError:
                raise ValueError(f"Invalid cache backend: {v}")
        return v


class SecuritySettings(BaseSettings):
    """Security-specific configuration settings."""
    
    # JWT configuration
    secret_key: SecretStr = Field(default_factory=lambda: secrets.token_urlsafe(32), env='SECRET_KEY')
    algorithm: SecurityAlgorithm = Field(SecurityAlgorithm.HS256, env='JWT_ALGORITHM')
    access_token_expire_minutes: int = Field(30, env='ACCESS_TOKEN_EXPIRE_MINUTES')
    refresh_token_expire_days: int = Field(30, env='REFRESH_TOKEN_EXPIRE_DAYS')
    
    # Password requirements
    min_password_length: int = Field(8, env='MIN_PASSWORD_LENGTH')
    require_special_chars: bool = Field(True, env='REQUIRE_SPECIAL_CHARS')
    
    # Rate limiting
    rate_limit_enabled: bool = Field(True, env='RATE_LIMIT_ENABLED')
    requests_per_minute: int = Field(60, env='REQUESTS_PER_MINUTE')
    
    # CORS
    allowed_origins: List[str] = Field(["http://localhost:3000"], env='ALLOWED_ORIGINS')
    allow_credentials: bool = Field(True, env='ALLOW_CREDENTIALS')
    
    @validator('algorithm', pre=True)
    def validate_algorithm(cls, v):
        """Validate JWT algorithm."""
        if isinstance(v, str):
            try:
                return SecurityAlgorithm(v.upper())
            except ValueError:
                raise ValueError(f"Invalid JWT algorithm: {v}")
        return v
    
    @validator('secret_key')
    def validate_secret_key(cls, v):
        """Validate secret key strength."""
        if isinstance(v, SecretStr):
            key = v.get_secret_value()
        else:
            key = str(v)
            
        if len(key) < 32:
            raise ValueError("Secret key must be at least 32 characters long")
        
        if key == "your-secret-key-here":
            raise ValueError("Must change default secret key in production")
        
        return v if isinstance(v, SecretStr) else SecretStr(key)


class GenerationSettings(BaseSettings):
    """Content generation-specific settings."""
    
    # Generation limits
    generation_timeout: int = Field(300, env='GENERATION_TIMEOUT')  # 5 minutes
    max_concurrent_generations: int = Field(5, env='MAX_CONCURRENT_GENERATIONS')
    max_generation_queue_size: int = Field(100, env='MAX_GENERATION_QUEUE_SIZE')
    
    # Quality control
    default_quality_threshold: float = Field(0.8, env='DEFAULT_QUALITY_THRESHOLD')
    min_quality_threshold: float = Field(0.6, env='MIN_QUALITY_THRESHOLD')
    max_generation_attempts: int = Field(3, env='MAX_GENERATION_ATTEMPTS')
    
    # Content limits
    max_content_length: int = Field(10000, env='MAX_CONTENT_LENGTH')
    max_batch_size: int = Field(10, env='MAX_BATCH_SIZE')
    
    @validator('default_quality_threshold', 'min_quality_threshold')
    def validate_quality_threshold(cls, v):
        """Validate quality threshold is between 0 and 1."""
        if not 0.0 <= v <= 1.0:
            raise ValueError("Quality threshold must be between 0.0 and 1.0")
        return v


class Settings(BaseSettings):
    """
    Main application settings.
    
    Aggregates all configuration categories and provides environment-specific
    overrides and validation.
    """
    
    # Application metadata
    app_name: str = Field("D&D Character Creator", env='APP_NAME')
    app_version: str = Field("1.0.0", env='APP_VERSION')
    app_description: str = Field("AI-powered D&D content creation tool", env='APP_DESCRIPTION')
    
    # Environment and debugging
    environment: Environment = Field(Environment.DEVELOPMENT, env='ENVIRONMENT')
    debug: bool = Field(False, env='DEBUG')
    log_level: LogLevel = Field(LogLevel.INFO, env='LOG_LEVEL')
    
    # Server configuration
    host: str = Field("localhost", env='HOST')
    port: int = Field(8000, env='PORT')
    reload: bool = Field(False, env='RELOAD')
    
    # Nested configuration objects
    database: DatabaseSettings = DatabaseSettings()
    cache: CacheSettings = CacheSettings()
    security: SecuritySettings = SecuritySettings()
    generation: GenerationSettings = GenerationSettings()
    
    # Feature flags
    enable_metrics: bool = Field(True, env='ENABLE_METRICS')
    enable_health_checks: bool = Field(True, env='ENABLE_HEALTH_CHECKS')
    enable_api_docs: bool = Field(True, env='ENABLE_API_DOCS')
    
    @validator('environment', pre=True)
    def validate_environment(cls, v):
        """Validate environment value."""
        if isinstance(v, str):
            try:
                return Environment(v.lower())
            except ValueError:
                raise ValueError(f"Invalid environment: {v}")
        return v
    
    @validator('log_level', pre=True)
    def validate_log_level(cls, v):
        """Validate log level value."""
        if isinstance(v, str):
            try:
                return LogLevel(v.upper())
            except ValueError:
                raise ValueError(f"Invalid log level: {v}")
        return v
    
    @validator('port')
    def validate_port(cls, v):
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    def model_post_init(self, __context) -> None:
        """Apply environment-specific configuration after initialization."""
        self._apply_environment_overrides()
    
    def _apply_environment_overrides(self):
        """Apply environment-specific configuration overrides."""
        env_config = get_environment_config()
        
        # Apply overrides based on environment
        if env_config.is_development:
            self.debug = True
            self.log_level = LogLevel.DEBUG
            self.database.database_echo = True
            self.reload = True
            self.security.allowed_origins = [
                "http://localhost:3000",
                "http://localhost:3001", 
                "http://127.0.0.1:3000"
            ]
            
        elif env_config.is_testing:
            self.debug = False
            self.log_level = LogLevel.WARNING
            self.database.database_url = "sqlite:///:memory:"
            self.cache.enable_caching = False
            self.generation.generation_timeout = 30
            
        elif env_config.is_production:
            self.debug = False
            self.log_level = LogLevel.WARNING
            self.database.database_echo = False
            self.enable_api_docs = False
            self.reload = False
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.environment.is_development_like
    
    @property
    def is_production(self) -> bool:
        """Check if running in production mode."""
        return self.environment == Environment.PRODUCTION
    
    def get_database_url(self) -> str:
        """Get database URL with environment-specific modifications."""
        env_config = get_environment_config()
        return env_config.get_database_url(self.database.database_url)
    
    def get_cors_origins(self) -> List[str]:
        """Get CORS origins with environment-specific additions."""
        env_config = get_environment_config()
        return env_config.get_cors_origins(self.security.allowed_origins)
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        use_enum_values = True


# Singleton settings instance with proper initialization
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """
    Get application settings (singleton pattern).
    
    Returns:
        Settings: Global application settings instance
    """
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings


def reload_settings() -> Settings:
    """
    Force reload of settings (useful for testing).
    
    Returns:
        Settings: New settings instance
    """
    global _settings
    _settings = Settings()
    return _settings


def validate_settings() -> List[str]:
    """
    Validate current settings configuration.
    
    Returns:
        List of validation errors (empty if valid)
    """
    errors = []
    settings = get_settings()
    
    try:
        # Validate database connection
        if settings.database.database_type == DatabaseType.SQLITE:
            db_path = settings.database.database_url.replace('sqlite:///', '')
            if db_path != ':memory:' and db_path:
                db_dir = Path(db_path).parent
                if not db_dir.exists():
                    errors.append(f"Database directory does not exist: {db_dir}")
        
        # Validate cache configuration
        if settings.cache.cache_backend == CacheBackend.REDIS:
            if not settings.cache.redis_url:
                errors.append("Redis URL is required when using Redis cache backend")
        
        # Validate security in production
        if settings.is_production:
            if settings.debug:
                errors.append("Debug mode should be disabled in production")
            
            secret_key = settings.security.secret_key.get_secret_value()
            if secret_key == "your-secret-key-here":
                errors.append("Default secret key must be changed in production")
                
            if "localhost" in settings.security.allowed_origins:
                errors.append("Localhost should not be in allowed origins for production")
    
    except Exception as e:
        errors.append(f"Settings validation error: {e}")
    
    return errors


def get_settings_summary() -> dict:
    """
    Get a summary of current settings (excluding sensitive data).
    
    Returns:
        Dictionary containing settings summary
    """
    settings = get_settings()
    
    return {
        'application': {
            'name': settings.app_name,
            'version': settings.app_version,
            'environment': settings.environment.value,
            'debug': settings.debug,
            'log_level': settings.log_level.value
        },
        'database': {
            'type': settings.database.database_type.value,
            'echo': settings.database.database_echo,
            'pool_size': settings.database.db_pool_size
        },
        'cache': {
            'backend': settings.cache.cache_backend.value,
            'enabled': settings.cache.enable_caching,
            'ttl': settings.cache.cache_ttl
        },
        'security': {
            'algorithm': settings.security.algorithm.value,
            'rate_limiting': settings.security.rate_limit_enabled,
            'cors_origins_count': len(settings.security.allowed_origins)
        },
        'generation': {
            'timeout': settings.generation.generation_timeout,
            'max_concurrent': settings.generation.max_concurrent_generations,
            'quality_threshold': settings.generation.default_quality_threshold
        },
        'features': {
            'metrics': settings.enable_metrics,
            'health_checks': settings.enable_health_checks,
            'api_docs': settings.enable_api_docs
        }
    }