"""
Character equipment management service.

This service handles all equipment-related operations including:
- Equipment assignment and management
- Item validation and compatibility checks
- Equipment slot management
- Inventory tracking
"""

from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID
import logging
from sqlalchemy.orm import Session

from src.core.logging_config import get_logger
from src.services.data.catalog import UnifiedCatalogService
from src.services.data.rules import (
    get_appropriate_weapons_for_character,
    get_weapon_data,
    is_existing_dnd_weapon
)
from src.models.database_models import Character

logger = get_logger(__name__)

class EquipmentService:
    """Service for managing character equipment."""
    
    def __init__(self, db: Session, catalog_service: Optional[UnifiedCatalogService] = None):
        self.db = db
        self.catalog_service = catalog_service or UnifiedCatalogService(db)
    
    async def assign_equipment(self,
                           character_id: str,
                           equipment_list: List[Dict[str, Any]],
                           access_type: str = "equipped") -> List[str]:
        """
        Assign equipment to a character, preferring official items.
        
        Args:
            character_id: UUID of the character
            equipment_list: List of equipment items to assign
            access_type: How the character accesses the items ("equipped", "inventory", etc.)
            
        Returns:
            List of access UUIDs for the granted items
        """
        # Get character data for context
        character = self.db.query(Character).filter(Character.id == character_id).first()
        if not character:
            logger.error("character_not_found", character_id=character_id)
            raise ValueError(f"Character not found: {character_id}")
        
        character_data = {
            "id": character_id,
            "classes": character.character_classes,
            "level": sum(character.character_classes.values()) if character.character_classes else 1,
            "weapon_proficiencies": getattr(character, "weapon_proficiencies", []),
            "armor_proficiencies": getattr(character, "armor_proficiencies", [])
        }
        
        logger.info(
            "assigning_equipment",
            character_id=character_id,
            item_count=len(equipment_list),
            access_type=access_type
        )
        
        access_ids = []
        for item in equipment_list:
            try:
                # 1. Try to find an official item match
                found_match = False
                item_name = item.get("name", "").strip()
                
                if item.get("type") == "weapon" and is_existing_dnd_weapon(item_name):
                    logger.info("found_official_weapon", weapon_name=item_name)
                    weapon_data = get_weapon_data(item_name)
                    if weapon_data:
                        # Create catalog entry for the official weapon
                        item_id = await self.catalog_service.create_custom_item(
                            name=item_name,
                            item_type="weapon",
                            content_data=weapon_data,
                            source_type="official",
                            source_info="D&D 5e Core"
                        )
                        found_match = True
                        
                if not found_match:
                    logger.info(
                        "creating_custom_item",
                        item_name=item_name,
                        item_type=item.get("type", "equipment")
                    )
                    # Create a custom item in the catalog
                    item_id = await self.catalog_service.create_custom_item(
                        name=item_name,
                        item_type=item.get("type", "equipment"),
                        content_data=item,
                        source_type="custom",
                        created_by=character_id
                    )
                
                # Grant access to the item
                access_id = await self.catalog_service.grant_item_access(
                    character_id=character_id,
                    item_id=item_id,
                    access_type=access_type,
                    quantity=item.get("quantity", 1)
                )
                
                access_ids.append(access_id)
                logger.info(
                    "item_access_granted",
                    character_id=character_id,
                    item_id=item_id,
                    access_id=access_id,
                    access_type=access_type
                )
                
            except Exception as e:
                logger.error(
                    "item_assignment_failed",
                    character_id=character_id,
                    item=item,
                    error=str(e),
                    error_type=type(e).__name__
                )
                # Continue with other items
                continue
        
        return access_ids
    
    async def unassign_equipment(self,
                             character_id: str,
                             access_ids: List[str]) -> None:
        """
        Remove equipment assignments from a character.
        
        Args:
            character_id: UUID of the character
            access_ids: List of access UUIDs to revoke
        """
        logger.info(
            "unassigning_equipment",
            character_id=character_id,
            access_count=len(access_ids)
        )
        
        for access_id in access_ids:
            try:
                # Get access type for logging
                access = await self.catalog_service.get_access_by_id(access_id)
                if not access:
                    logger.warning(
                        "access_not_found",
                        character_id=character_id,
                        access_id=access_id
                    )
                    continue
                
                await self.catalog_service.revoke_item_access(
                    character_id=character_id,
                    item_id=str(access.item_id),
                    access_type=access.access_type
                )
                
                logger.info(
                    "item_access_revoked",
                    character_id=character_id,
                    access_id=access_id,
                    item_id=str(access.item_id)
                )
                
            except Exception as e:
                logger.error(
                    "item_unassignment_failed",
                    character_id=character_id,
                    access_id=access_id,
                    error=str(e),
                    error_type=type(e).__name__
                )
                # Continue with other items
                continue
    
    async def get_character_equipment(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Get all equipment assigned to a character.
        
        Args:
            character_id: UUID of the character
            
        Returns:
            Dictionary of equipment by access type
        """
        logger.info("fetching_character_equipment", character_id=character_id)
        
        try:
            equipment = await self.catalog_service.get_character_equipment(character_id)
            
            logger.info(
                "equipment_fetched",
                character_id=character_id,
                equipped_count=len(equipment["equipped"]),
                inventory_count=len(equipment["inventory"])
            )
            
            return equipment
            
        except Exception as e:
            logger.error(
                "equipment_fetch_failed",
                character_id=character_id,
                error=str(e),
                error_type=type(e).__name__
            )
            raise
