import motor.motor_asyncio
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
import os
import logging
from typing import Optional, Dict, Any, List, Union
from pymongo.errors import ServerSelectionTimeoutError, PyMongoError

logger = logging.getLogger(__name__)

class MongoDBClient:
    """MongoDB client for the DnD Character Creator application"""
    
    def __init__(self, connection_uri: Optional[str] = None):
        """Initialize MongoDB client"""
        self.client: Optional[AsyncIOMotorClient] = None
        self.db: Optional[AsyncIOMotorDatabase] = None
        self.connection_uri = connection_uri or os.environ.get("MONGODB_URI", "mongodb://localhost:27017/")
        self.db_name = os.environ.get("MONGODB_DB", "dnd_character_creator")

    async def connect(self) -> None:
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(self.connection_uri, serverSelectionTimeoutMS=5000)
            await self.client.server_info()  # Verify connection works
            self.db = self.client[self.db_name]
            logger.info(f"Connected to MongoDB database: {self.db_name}")
        except ServerSelectionTimeoutError as e:
            logger.error(f"Failed to connect to MongoDB: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {str(e)}")
            raise

    async def close(self) -> None:
        """Close MongoDB connection"""
        if self.client:
            self.client.close()
            logger.info("Closed MongoDB connection")
            self.client = None
            self.db = None
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Get the database instance"""
        if not self.db:
            raise RuntimeError("Database connection not established. Call connect() first.")
        return self.db
    
    # Helper methods for common operations
    async def find_one(self, collection: str, query: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Find a single document"""
        if not self.db:
            await self.connect()
        try:
            return await self.db[collection].find_one(query)
        except PyMongoError as e:
            logger.error(f"Error finding document in {collection}: {str(e)}")
            raise

    async def find_many(self, 
                      collection: str, 
                      query: Dict[str, Any], 
                      limit: int = 0, 
                      skip: int = 0,
                      sort: Optional[List[tuple]] = None) -> List[Dict[str, Any]]:
        """Find multiple documents"""
        if not self.db:
            await self.connect()
        try:
            cursor = self.db[collection].find(query)
            
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            if sort:
                cursor = cursor.sort(sort)
                
            return await cursor.to_list(length=None)
        except PyMongoError as e:
            logger.error(f"Error finding documents in {collection}: {str(e)}")
            raise

    async def insert_one(self, collection: str, document: Dict[str, Any]) -> str:
        """Insert a document and return the inserted ID"""
        if not self.db:
            await self.connect()
        try:
            result = await self.db[collection].insert_one(document)
            return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error inserting document into {collection}: {str(e)}")
            raise

    async def update_one(self, collection: str, filter_query: Dict[str, Any], update_data: Dict[str, Any]) -> int:
        """Update a document and return the count of modified documents"""
        if not self.db:
            await self.connect()
        try:
            result = await self.db[collection].update_one(filter_query, {"$set": update_data})
            return result.modified_count
        except PyMongoError as e:
            logger.error(f"Error updating document in {collection}: {str(e)}")
            raise

    async def delete_one(self, collection: str, filter_query: Dict[str, Any]) -> int:
        """Delete a document and return the count of deleted documents"""
        if not self.db:
            await self.connect()
        try:
            result = await self.db[collection].delete_one(filter_query)
            return result.deleted_count
        except PyMongoError as e:
            logger.error(f"Error deleting document from {collection}: {str(e)}")
            raise


# Create a singleton instance for the application to use
mongodb_client = MongoDBClient()

# Dependency for FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """FastAPI dependency to get database connection"""
    if not mongodb_client.db:
        await mongodb_client.connect()
    return mongodb_client.get_database()

# Event handlers for the FastAPI app
async def connect_to_mongo():
    """Connect to MongoDB at application startup"""
    await mongodb_client.connect()

async def close_mongo_connection():
    """Close MongoDB connection at application shutdown"""
    await mongodb_client.close()