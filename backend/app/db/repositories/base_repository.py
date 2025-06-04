from typing import Dict, List, Any, Optional, TypeVar, Generic
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import PyMongoError
import logging

from backend.app.db.mongodb import get_database

T = TypeVar('T', bound=Dict[str, Any])
ID = TypeVar('ID')

logger = logging.getLogger(__name__)

class BaseRepository(Generic[T, ID]):
    """
    Base repository class providing common database operations.
    Implements the repository pattern for MongoDB.
    """
    
    def __init__(self, collection_name: str):
        """
        Initialize the repository with a collection name.
        
        Args:
            collection_name: Name of the MongoDB collection
        """
        self.collection_name = collection_name
    
    async def _get_collection(self):
        """Get the database collection"""
        db = await get_database()
        return db[self.collection_name]
    
    async def find_by_id(self, id: ID) -> Optional[T]:
        """
        Find an entity by its ID.
        
        Args:
            id: The entity ID
            
        Returns:
            The entity or None if not found
        """
        try:
            # Convert string ID to ObjectId if needed
            query_id = ObjectId(id) if isinstance(id, str) else id
            collection = await self._get_collection()
            result = await collection.find_one({"_id": query_id})
            return result
        except PyMongoError as e:
            logger.error(f"Database error in find_by_id: {str(e)}")
            raise
    
    async def find_all(self, 
                      filter_query: Dict[str, Any] = None, 
                      skip: int = 0, 
                      limit: int = 0,
                      sort: List[tuple] = None) -> List[T]:
        """
        Find all entities matching a filter.
        
        Args:
            filter_query: MongoDB filter query
            skip: Number of documents to skip
            limit: Maximum number of documents to return
            sort: List of (field, direction) tuples for sorting
            
        Returns:
            List of matching entities
        """
        try:
            collection = await self._get_collection()
            cursor = collection.find(filter_query or {})
            
            if skip > 0:
                cursor = cursor.skip(skip)
            if limit > 0:
                cursor = cursor.limit(limit)
            if sort:
                cursor = cursor.sort(sort)
                
            return await cursor.to_list(length=None)
        except PyMongoError as e:
            logger.error(f"Database error in find_all: {str(e)}")
            raise
    
    async def create(self, entity: Dict[str, Any]) -> ID:
        """
        Create a new entity.
        
        Args:
            entity: Entity data
            
        Returns:
            ID of the created entity
        """
        try:
            collection = await self._get_collection()
            result = await collection.insert_one(entity)
            return result.inserted_id
        except PyMongoError as e:
            logger.error(f"Database error in create: {str(e)}")
            raise
    
    async def update(self, id: ID, update_data: Dict[str, Any]) -> bool:
        """
        Update an entity by ID.
        
        Args:
            id: Entity ID
            update_data: Fields to update
            
        Returns:
            True if updated, False if not found
        """
        try:
            # Convert string ID to ObjectId if needed
            query_id = ObjectId(id) if isinstance(id, str) else id
            collection = await self._get_collection()
            result = await collection.update_one(
                {"_id": query_id}, 
                {"$set": update_data}
            )
            return result.modified_count > 0
        except PyMongoError as e:
            logger.error(f"Database error in update: {str(e)}")
            raise
    
    async def delete(self, id: ID) -> bool:
        """
        Delete an entity by ID.
        
        Args:
            id: Entity ID
            
        Returns:
            True if deleted, False if not found
        """
        try:
            # Convert string ID to ObjectId if needed
            query_id = ObjectId(id) if isinstance(id, str) else id
            collection = await self._get_collection()
            result = await collection.delete_one({"_id": query_id})
            return result.deleted_count > 0
        except PyMongoError as e:
            logger.error(f"Database error in delete: {str(e)}")
            raise
    
    async def count(self, filter_query: Dict[str, Any] = None) -> int:
        """
        Count entities matching a filter.
        
        Args:
            filter_query: MongoDB filter query
            
        Returns:
            Count of matching entities
        """
        try:
            collection = await self._get_collection()
            return await collection.count_documents(filter_query or {})
        except PyMongoError as e:
            logger.error(f"Database error in count: {str(e)}")
            raise