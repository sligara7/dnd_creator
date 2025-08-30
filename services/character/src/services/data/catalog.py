"""
Unified catalog service for managing game content.

This service provides a central repository for all game content including:
- Official D&D content
- Custom content
- Character-specific content
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID, uuid4
import logging
from sqlalchemy.orm import Session

from src.models.database_models import (
    UnifiedCatalogItem,
    ItemAccess,
    ItemType,
    AccessType
)

logger = logging.getLogger(__name__)

class UnifiedCatalogService:
    """Service for managing the unified content catalog."""
    
    def __init__(self, db: Session):
        self.db = db
    
    async def create_custom_item(self,
                               name: str,
                               item_type: str,
                               content_data: Dict[str, Any],
                               source_type: str = "custom",
                               source_info: str = None,
                               created_by: str = None) -> str:
        """
        Create a new custom item in the catalog.
        
        Args:
            name: Name of the item
            item_type: Type of item (weapon, spell, feature, etc.)
            content_data: Item-specific data
            source_type: Origin of the item (custom, official, etc.)
            source_info: Additional source information
            created_by: ID of the creating entity
            
        Returns:
            UUID of the created item
        """
        try:
            item_id = str(uuid4())
            item = UnifiedCatalogItem(
                id=item_id,
                name=name,
                item_type=item_type,
                content=content_data,
                source_type=source_type,
                source_info=source_info,
                created_by=created_by,
                created_at=datetime.utcnow()
            )
            
            self.db.add(item)
            self.db.commit()
            
            logger.info(
                "created_catalog_item",
                item_id=item_id,
                name=name,
                type=item_type,
                source=source_type
            )
            
            return item_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "catalog_item_creation_failed",
                name=name,
                type=item_type,
                error=str(e)
            )
            raise
    
    async def grant_item_access(self,
                              character_id: str,
                              item_id: str,
                              access_type: str,
                              quantity: int = 1) -> str:
        """
        Grant a character access to a catalog item.
        
        Args:
            character_id: ID of the character
            item_id: ID of the catalog item
            access_type: How the character accesses the item
            quantity: Number of items
            
        Returns:
            UUID of the access grant
        """
        try:
            access_id = str(uuid4())
            access = ItemAccess(
                id=access_id,
                character_id=character_id,
                item_id=item_id,
                access_type=access_type,
                quantity=quantity,
                granted_at=datetime.utcnow()
            )
            
            self.db.add(access)
            self.db.commit()
            
            logger.info(
                "granted_item_access",
                access_id=access_id,
                character_id=character_id,
                item_id=item_id,
                type=access_type
            )
            
            return access_id
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "item_access_grant_failed",
                character_id=character_id,
                item_id=item_id,
                error=str(e)
            )
            raise
    
    async def revoke_item_access(self,
                                character_id: str,
                                item_id: str,
                                access_type: str) -> bool:
        """
        Revoke a character's access to a catalog item.
        
        Args:
            character_id: ID of the character
            item_id: ID of the catalog item
            access_type: Access type to revoke
            
        Returns:
            True if access was revoked
        """
        try:
            access = self.db.query(ItemAccess).filter(
                ItemAccess.character_id == character_id,
                ItemAccess.item_id == item_id,
                ItemAccess.access_type == access_type
            ).first()
            
            if not access:
                return False
            
            self.db.delete(access)
            self.db.commit()
            
            logger.info(
                "revoked_item_access",
                character_id=character_id,
                item_id=item_id,
                type=access_type
            )
            
            return True
            
        except Exception as e:
            self.db.rollback()
            logger.error(
                "item_access_revoke_failed",
                character_id=character_id,
                item_id=item_id,
                error=str(e)
            )
            raise
    
    async def get_character_equipment(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all equipment accessible to a character.
        
        Args:
            character_id: ID of the character
            
        Returns:
            Dictionary of equipment by access type
        """
        try:
            accesses = self.db.query(ItemAccess).filter(
                ItemAccess.character_id == character_id,
                ItemAccess.access_type.in_(["equipped", "inventory"])
            ).all()
            
            equipment = {
                "equipped": [],
                "inventory": []
            }
            
            for access in accesses:
                item = self.db.query(UnifiedCatalogItem).get(access.item_id)
                if not item:
                    continue
                    
                item_data = item.content
                item_data.update({
                    "id": str(item.id),
                    "access_id": str(access.id),
                    "quantity": access.quantity
                })
                
                equipment[access.access_type].append(item_data)
            
            return equipment
            
        except Exception as e:
            logger.error(
                "character_equipment_fetch_failed",
                character_id=character_id,
                error=str(e)
            )
            raise
    
    async def get_access_by_id(self, access_id: str) -> Optional[ItemAccess]:
        """Get an item access record by ID."""
        return self.db.query(ItemAccess).filter(ItemAccess.id == access_id).first()
    
    def search_catalog(self,
                      query: str,
                      item_type: Optional[str] = None,
                      source_type: Optional[str] = None,
                      limit: int = 10) -> List[Dict[str, Any]]:
        """
        Search the catalog for items matching criteria.
        
        Args:
            query: Search query
            item_type: Filter by item type
            source_type: Filter by source type
            limit: Maximum number of results
            
        Returns:
            List of matching catalog items
        """
        try:
            q = self.db.query(UnifiedCatalogItem)
            
            if query:
                q = q.filter(UnifiedCatalogItem.name.ilike(f"%{query}%"))
            
            if item_type:
                q = q.filter(UnifiedCatalogItem.item_type == item_type)
            
            if source_type:
                q = q.filter(UnifiedCatalogItem.source_type == source_type)
            
            items = q.limit(limit).all()
            
            return [
                {
                    "id": str(item.id),
                    "name": item.name,
                    "type": item.item_type,
                    "source": item.source_type,
                    "content": item.content
                }
                for item in items
            ]
            
        except Exception as e:
            logger.error(
                "catalog_search_failed",
                query=query,
                error=str(e)
            )
            raise
