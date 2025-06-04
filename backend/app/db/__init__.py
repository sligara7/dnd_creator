"""
Database package for D&D Character Creator application.
Provides database connections and repositories for data storage.
"""

from backend.app.db.mongodb import (
    mongodb_client, 
    get_database, 
    connect_to_mongo, 
    close_mongo_connection
)

# Export the database client and connection functions
__all__ = [
    "mongodb_client",
    "get_database",
    "connect_to_mongo",
    "close_mongo_connection"
]

# Repository imports (assuming you'll implement these)
from backend.app.db.repositories.character_repository import CharacterRepository
from backend.app.db.repositories.user_repository import UserRepository
from backend.app.db.repositories.campaign_repository import CampaignRepository

# Export repositories
repositories = {
    "character": CharacterRepository(),
    "user": UserRepository(),
    "campaign": CampaignRepository()
}

# Add specialized repositories to exports
__all__.extend(["repositories"])