"""
Application-level Enumerations

Enums for application configuration, logging, and general application concerns.
"""

from enum import Enum


class LogLevel(Enum):
    """Application logging levels."""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"
    
    @property
    def numeric_level(self) -> int:
        """Get numeric logging level for Python logging module."""
        levels = {
            self.DEBUG: 10,
            self.INFO: 20,
            self.WARNING: 30,
            self.ERROR: 40,
            self.CRITICAL: 50
        }
        return levels[self]


class SecurityAlgorithm(Enum):
    """Security algorithms for token generation."""
    HS256 = "HS256"
    HS384 = "HS384"
    HS512 = "HS512"
    RS256 = "RS256"
    RS384 = "RS384"
    RS512 = "RS512"
    
    @property
    def is_symmetric(self) -> bool:
        """Check if algorithm uses symmetric keys."""
        return self.value.startswith('HS')
    
    @property
    def is_asymmetric(self) -> bool:
        """Check if algorithm uses asymmetric keys."""
        return self.value.startswith('RS')


class CacheBackend(Enum):
    """Cache backend types."""
    REDIS = "redis"
    MEMORY = "memory"
    DATABASE = "database"
    DISABLED = "disabled"
    
    @property
    def is_persistent(self) -> bool:
        """Check if cache backend is persistent."""
        return self in {self.REDIS, self.DATABASE}


class DatabaseType(Enum):
    """Database types supported by the application."""
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    
    @property
    def supports_async(self) -> bool:
        """Check if database type supports async operations."""
        return self in {self.POSTGRESQL, self.MYSQL}
    
    @property
    def default_port(self) -> int:
        """Get default port for database type."""
        ports = {
            self.POSTGRESQL: 5432,
            self.MYSQL: 3306,
            self.SQLITE: 0  # No port for SQLite
        }
        return ports.get(self, 0)