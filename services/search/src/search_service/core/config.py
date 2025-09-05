from typing import Dict, List, Optional
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field, PostgresDsn, RedisDsn


class Settings(BaseSettings):
    """Search Service settings"""
    model_config = SettingsConfigDict(env_file=".env", case_sensitive=True)

    # Service config
    SERVICE_NAME: str = "search_service"
    VERSION: str = "0.1.0"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # API config
    HOST: str = "0.0.0.0"
    PORT: int = 8600
    WORKERS: int = 8  # Higher worker count for search operations
    CORS_ORIGINS: List[str] = Field(default_factory=list)

    # Database config
    POSTGRES_HOST: str = "search_db"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "search_db"
    POSTGRES_USER: str = "search_user"
    POSTGRES_PASSWORD: str = "search_pass"
    DATABASE_URL: PostgresDsn | None = None

    # Redis config
    REDIS_HOST: str = "search_cache"
    REDIS_PORT: int = 6379
    REDIS_PASSWORD: str | None = None
    REDIS_DB: int = 0
    REDIS_URL: RedisDsn | None = None

    # Elasticsearch config
    ELASTICSEARCH_HOST: str = "search_cluster"
    ELASTICSEARCH_PORT: int = 9200
    ELASTICSEARCH_USER: str | None = None
    ELASTICSEARCH_PASSWORD: str | None = None
    ELASTICSEARCH_VERIFY_CERTS: bool = False
    ES_CLUSTER_NAME: str = "dnd-search"
    ES_NUMBER_OF_SHARDS: int = 5
    ES_NUMBER_OF_REPLICAS: int = 1
    
    # Search config
    INDEX_PREFIX: str = "dnd-"
    DEFAULT_PAGE_SIZE: int = 20
    MAX_PAGE_SIZE: int = 100
    MAX_SEARCH_WINDOW: int = 10000
    DEFAULT_SEARCH_TIMEOUT: int = 30
    MINIMUM_SHOULD_MATCH: str = "75%"
    MAX_QUERY_LENGTH: int = 1000
    
    # Index mappings
    INDEX_MAPPINGS: Dict[str, Dict] = {
        "characters": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "class": {"type": "keyword"},
                "race": {"type": "keyword"},
                "level": {"type": "integer"},
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "abilities": {"type": "object"},
                "inventory": {"type": "nested"},
                "spells": {"type": "nested"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "campaigns": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "theme": {"type": "keyword"},
                "players": {"type": "keyword"},
                "dm": {"type": "keyword"},
                "status": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "items": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "type": {"type": "keyword"},
                "rarity": {"type": "keyword"},
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "properties": {"type": "object"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "spells": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "level": {"type": "integer"},
                "school": {"type": "keyword"},
                "casting_time": {"type": "keyword"},
                "range": {"type": "keyword"},
                "components": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "duration": {"type": "keyword"},
                "classes": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "higher_levels": {"type": "text", "analyzer": "dnd_analyzer"},
                "source": {"type": "keyword"},
                "ritual": {"type": "boolean"},
                "concentration": {"type": "boolean"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "monsters": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "size": {"type": "keyword"},
                "type": {"type": "keyword"},
                "alignment": {"type": "keyword"},
                "challenge_rating": {"type": "float"},
                "hit_points": {"type": "integer"},
                "armor_class": {"type": "integer"},
                "speed": {"type": "object"},
                "abilities": {
                    "properties": {
                        "strength": {"type": "integer"},
                        "dexterity": {"type": "integer"},
                        "constitution": {"type": "integer"},
                        "intelligence": {"type": "integer"},
                        "wisdom": {"type": "integer"},
                        "charisma": {"type": "integer"},
                    }
                },
                "saving_throws": {"type": "object"},
                "skills": {"type": "object"},
                "senses": {"type": "object"},
                "languages": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "traits": {"type": "text", "analyzer": "dnd_analyzer"},
                "actions": {"type": "text", "analyzer": "dnd_analyzer"},
                "reactions": {"type": "text", "analyzer": "dnd_analyzer"},
                "legendary_actions": {"type": "text", "analyzer": "dnd_analyzer"},
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "source": {"type": "keyword"},
                "environment": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "maps": {
            "properties": {
                "name": {"type": "text", "analyzer": "dnd_analyzer"},
                "type": {"type": "keyword"},
                "environment": {"type": "keyword"},
                "size": {"type": "keyword"},
                "grid": {"type": "boolean"},
                "features": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "description": {"type": "text", "analyzer": "dnd_analyzer"},
                "tags": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "campaign": {"type": "keyword"},
                "image_url": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
        "documentation": {
            "properties": {
                "title": {"type": "text", "analyzer": "dnd_analyzer"},
                "path": {"type": "keyword"},
                "type": {"type": "keyword"},
                "content": {"type": "text", "analyzer": "dnd_analyzer"},
                "tags": {
                    "type": "keyword",
                    "index_options": "docs",
                },
                "version": {"type": "keyword"},
                "author": {"type": "keyword"},
                "created_at": {"type": "date"},
                "updated_at": {"type": "date"},
            }
        },
    }
    
    # Message Hub config
    MESSAGE_HUB_URL: str = "http://message-hub:8200"
    SERVICE_TTL: int = 30
    HEALTH_CHECK_INTERVAL: int = 10

    # Performance config
    MAX_CONNECTIONS: int = 100
    CONNECTION_TIMEOUT: int = 5
    READ_TIMEOUT: int = 30
    WRITE_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    RETRY_ON_TIMEOUT: bool = True
    
    # Analysis config
    ANALYZER_NAME: str = "dnd_analyzer"
    MINIMUM_SHOULD_MATCH_PERCENTAGE: int = 75
    FUZZINESS: str = "AUTO"
    MAX_EXPANSIONS: int = 50
    
    # Cache config
    CACHE_TTL: int = 300  # 5 minutes
    CACHE_PREFIX: str = "search:"
    CACHE_ENABLED: bool = True
    
    # Monitoring config
    METRICS_PORT: int = 8601
    METRICS_PATH: str = "/metrics"
    SLOW_QUERY_THRESHOLD: float = 1.0  # seconds
    
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
    
    def get_index_name(self, index_type: str) -> str:
        """Get full index name with prefix"""
        return f"{self.INDEX_PREFIX}{index_type}"


# Create global settings instance
settings = Settings()
