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

# Import repositories from the new repository package
from backend.app.db.repositories import repositories as repo_instances

# Export repositories - now from the centralized repository package
repositories = repo_instances

# Add specialized repositories to exports
__all__.extend(["repositories"])