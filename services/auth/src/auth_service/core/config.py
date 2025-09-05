from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn, SecretStr


class Settings(BaseSettings):
    """Auth Service settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Service config
    SERVICE_NAME: str = "auth_service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API config
    HOST: str = "0.0.0.0"
    PORT: int = 8300
    WORKERS: int = 4
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Database config
    POSTGRES_HOST: str = "auth_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "auth_db"
    POSTGRES_USER: str = "auth_user"
    POSTGRES_PASSWORD: str = "auth_pass"
    DATABASE_URL: PostgresDsn | None = None

    # Redis config
    REDIS_HOST: str = "auth_cache"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None

    # JWT config
    JWT_SECRET_KEY: SecretStr
    JWT_ALGORITHM: str = "RS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Security config
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 60
    MFA_TOKEN_EXPIRE_MINUTES: int = 5
    ARGON2_TIME_COST: int = 2
    ARGON2_MEMORY_COST: int = 102400
    ARGON2_PARALLELISM: int = 8
    MINIMUM_PASSWORD_LENGTH: int = 12
    MAXIMUM_LOGIN_ATTEMPTS: int = 5
    LOCKOUT_DURATION_MINUTES: int = 30
    API_KEY_LENGTH: int = 32
    
    # MFA config
    MFA_ISSUER: str = "dndcreator.com"
    MFA_DIGITS: int = 6
    MFA_INTERVAL: int = 30
    
    # Service config
    MESSAGE_HUB_URL: str = "http://message-hub:8200"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10
    
    # File paths
    PRIVATE_KEY_PATH: str = "/app/keys/private.pem"
    PUBLIC_KEY_PATH: str = "/app/keys/public.pem"
    
    # Metrics config
    METRICS_PORT: int = 8301
    
    # Cache config
    TOKEN_CACHE_TTL: int = 3600  # 1 hour
    SESSION_CACHE_TTL: int = 86400  # 1 day
    ROLE_CACHE_TTL: int = 300  # 5 minutes
    
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
