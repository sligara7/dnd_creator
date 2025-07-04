"""
Unified Item Catalog Service

This service provides a high-level interface for managing the unified item catalog
and character-item relationships using UUIDs instead of names.
"""

import uuid
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from src.models.database_models import UnifiedItem, CharacterItemAccess, Character, CharacterDB, get_db
from src.services.creation_validation import validate_item_allocation, CreationResult

logger = logging.getLogger(__name__)

class UnifiedCatalogService:
    """Service for managing the unified item catalog and character relationships."""
    
    def __init__(self, session: Session):
        self.session = session
    
    # =========================================================================
    # CATALOG MANAGEMENT
    # =========================================================================
    
    def search_items(self, 
                     item_type: Optional[str] = None,
                     item_subtype: Optional[str] = None,
                     spell_level: Optional[int] = None,
                     spell_school: Optional[str] = None,
                     class_restrictions: Optional[List[str]] = None,
                     source_type: Optional[str] = None,
                     name_filter: Optional[str] = None,
                     limit: int = 100) -> List[Dict[str, Any]]:
        """Search the unified item catalog with various filters."""
        
        query = self.session.query(UnifiedItem).filter(UnifiedItem.is_active == True)
        
        # Apply filters
        if item_type:
            query = query.filter(UnifiedItem.item_type == item_type)
        if item_subtype:
            query = query.filter(UnifiedItem.item_subtype == item_subtype)
        if spell_level is not None:
            query = query.filter(UnifiedItem.spell_level == spell_level)
        if spell_school:
            query = query.filter(UnifiedItem.spell_school == spell_school)
        if source_type:
            query = query.filter(UnifiedItem.source_type == source_type)
        if name_filter:
            query = query.filter(UnifiedItem.name.ilike(f"%{name_filter}%"))
        if class_restrictions:
            # Check if any of the specified classes can use this item
            for class_name in class_restrictions:
                query = query.filter(UnifiedItem.class_restrictions.contains([class_name]))
        
        # Limit results
        items = query.limit(limit).all()
        
        return [item.to_dict() for item in items]
    
    def get_item_by_id(self, item_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific item by UUID."""
        item = self.session.query(UnifiedItem).filter(
            UnifiedItem.id == uuid.UUID(item_id),
            UnifiedItem.is_active == True
        ).first()
        
        return item.to_dict() if item else None
    
    def get_item_by_name(self, name: str, item_type: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """Get a specific item by name (for backward compatibility)."""
        query = self.session.query(UnifiedItem).filter(
            UnifiedItem.name == name,
            UnifiedItem.is_active == True
        )
        
        if item_type:
            query = query.filter(UnifiedItem.item_type == item_type)
        
        item = query.first()
        return item.to_dict() if item else None
    
    def create_custom_item(self, 
                          name: str,
                          item_type: str,
                          content_data: Dict[str, Any],
                          item_subtype: Optional[str] = None,
                          short_description: Optional[str] = None,
                          created_by: Optional[str] = None,
                          source_type: Optional[str] = None,
                          source_info: Optional[str] = None,
                          llm_metadata: Optional[dict] = None,
                          **kwargs) -> str:
        """Create a new custom or LLM-generated item and return its UUID."""
        # Determine source_type
        stype = source_type or "custom"
        if stype not in ("official", "custom", "llm_generated"):
            stype = "custom"
        item = UnifiedItem(
            id=uuid.uuid4(),
            name=name,
            item_type=item_type,
            item_subtype=item_subtype,
            source_type=stype,
            source_info=source_info,
            llm_metadata=llm_metadata,
            content_data=content_data,
            short_description=short_description or f"Custom {item_type}",
            created_by=created_by,
            source_book="Custom Creation" if stype != "official" else None,
            is_public=kwargs.get("is_public", False),
            spell_level=kwargs.get("spell_level"),
            spell_school=kwargs.get("spell_school"),
            class_restrictions=kwargs.get("class_restrictions"),
            rarity=kwargs.get("rarity"),
            requires_attunement=kwargs.get("requires_attunement", False),
            value_gp=kwargs.get("value_gp"),
            weight_lbs=kwargs.get("weight_lbs"),
            created_at=datetime.now(timezone.utc)
        )
        self.session.add(item)
        self.session.commit()
        logger.info(f"Created {stype} item: {name} (ID: {item.id})")
        return str(item.id)
    
    # =========================================================================
    # CHARACTER-ITEM RELATIONSHIPS
    # =========================================================================
    
    def grant_item_access(self,
                         character_id: str,
                         item_id: str,
                         access_type: str,
                         access_subtype: Optional[str] = None,
                         quantity: int = 1,
                         acquired_method: str = "character_creation",
                         custom_properties: Optional[Dict[str, Any]] = None,
                         skip_validation: bool = False) -> str:
        """Grant a character access to an item with validation."""
        
        # Validate the allocation unless explicitly skipped
        if not skip_validation:
            # Get character data (Character.id is stored as string, not UUID)
            character = self.session.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Get item data
            item = self.session.query(UnifiedItem).filter(UnifiedItem.id == uuid.UUID(item_id)).first()
            if not item:
                raise ValueError(f"Item not found: {item_id}")
            
            # Debug logging
            logger.info(f"VALIDATION DEBUG: Character {character.name}, Item {item.name}")
            logger.info(f"VALIDATION DEBUG: Character classes: {character.character_classes}")
            logger.info(f"VALIDATION DEBUG: Item class restrictions: {item.class_restrictions}")
            
            # Prepare character data for validation
            character_data = {
                "character_classes": character.character_classes or {},
                "weapon_proficiencies": getattr(character, 'weapon_proficiencies', []),
                "armor_proficiencies": getattr(character, 'armor_proficiencies', []),
                "tool_proficiencies": getattr(character, 'tool_proficiencies', {}),
                "level": sum((character.character_classes or {}).values()) or 1
            }
            
            # Prepare item data for validation
            item_data = item.to_dict()
            
            # Debug logging
            logger.info(f"VALIDATION DEBUG: Prepared character data: {character_data}")
            logger.info(f"VALIDATION DEBUG: Item data item_type: {item_data.get('item_type')}")
            
            # Validate the allocation
            validation = validate_item_allocation(character_data, item_data, access_type)
            
            logger.info(f"VALIDATION DEBUG: Validation result - Success: {validation.success}, Error: {validation.error}")
            
            if not validation.success:
                raise ValueError(f"Item allocation failed validation: {validation.error}")
            
            # Log warnings if any
            if validation.warnings:
                logger.warning(f"Item allocation warnings for character {character_id}, item {item_id}: {validation.warnings}")
        
        # Check if access already exists
        existing = self.session.query(CharacterItemAccess).filter(
            and_(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == uuid.UUID(item_id),
                CharacterItemAccess.access_type == access_type,
                CharacterItemAccess.access_subtype == access_subtype
            )
        ).first()
        
        if existing:
            # Update existing access
            existing.quantity += quantity
            existing.is_active = True
            self.session.commit()
            return str(existing.id)
        else:
            # Create new access
            access = CharacterItemAccess(
                id=uuid.uuid4(),
                character_id=character_id,
                item_id=uuid.UUID(item_id),
                access_type=access_type,
                access_subtype=access_subtype,
                quantity=quantity,
                acquired_method=acquired_method,
                custom_properties=custom_properties,
                acquired_at=datetime.now(timezone.utc)
            )
            
            self.session.add(access)
            self.session.commit()
            
            logger.info(f"Granted {access_type} access to item {item_id} for character {character_id}")
            return str(access.id)
    
    def revoke_item_access(self, character_id: str, item_id: str, access_type: str, access_subtype: Optional[str] = None):
        """Revoke a character's access to an item."""
        
        access = self.session.query(CharacterItemAccess).filter(
            and_(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == uuid.UUID(item_id),
                CharacterItemAccess.access_type == access_type,
                CharacterItemAccess.access_subtype == access_subtype
            )
        ).first()
        
        if access:
            access.is_active = False
            self.session.commit()
            logger.info(f"Revoked {access_type} access to item {item_id} for character {character_id}")
    
    def get_character_items(self, 
                           character_id: str, 
                           access_type: Optional[str] = None,
                           include_item_details: bool = True) -> List[Dict[str, Any]]:
        """Get all items a character has access to."""
        
        query = self.session.query(CharacterItemAccess).filter(
            and_(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.is_active == True
            )
        )
        
        if access_type:
            query = query.filter(CharacterItemAccess.access_type == access_type)
        
        access_records = query.all()
        
        result = []
        for access in access_records:
            access_dict = access.to_dict()
            
            if include_item_details:
                item = self.session.query(UnifiedItem).filter(
                    UnifiedItem.id == access.item_id
                ).first()
                if item:
                    access_dict["item_details"] = item.to_dict()
            
            result.append(access_dict)
        
        return result

    def get_character_allocations(self, character_id: str) -> List[Dict[str, Any]]:
        """Get all allocations for a character (alias for get_character_items)."""
        return self.get_character_items(character_id, include_item_details=True)
    
    def get_character_spells(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all spells a character knows or has prepared, organized by type."""
        
        spell_access = self.get_character_items(
            character_id=character_id,
            access_type="spells_known",
            include_item_details=True
        )
        
        prepared_access = self.get_character_items(
            character_id=character_id,
            access_type="spells_prepared", 
            include_item_details=True
        )
        
        return {
            "spells_known": spell_access,
            "spells_prepared": prepared_access
        }
    
    def get_character_equipment(self, character_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """Get all equipment a character owns, organized by type."""
        
        inventory = self.get_character_items(
            character_id=character_id,
            access_type="inventory",
            include_item_details=True
        )
        
        equipped = self.get_character_items(
            character_id=character_id,
            access_type="equipped",
            include_item_details=True
        )
        
        return {
            "inventory": inventory,
            "equipped": equipped
        }
    
    # =========================================================================
    # MIGRATION AND UTILITIES
    # =========================================================================
    
    def migrate_character_to_uuid_system(self, character_id: str, character_data: Dict[str, Any]) -> Dict[str, Any]:
        """Migrate a character's item lists from names to UUID-based system."""
        
        migrated_items = {
            "spells_known": [],
            "spells_prepared": [],
            "inventory": [],
            "equipped": []
        }
        
        # Migrate spells known
        if "spells_known" in character_data and isinstance(character_data["spells_known"], list):
            for spell_name in character_data["spells_known"]:
                item = self.get_item_by_name(spell_name, item_type="spell")
                if item:
                    access_id = self.grant_item_access(
                        character_id=character_id,
                        item_id=item["id"],
                        access_type="spells_known",
                        acquired_method="character_creation"
                    )
                    migrated_items["spells_known"].append(access_id)
        
        # Migrate weapons
        if "weapons" in character_data and isinstance(character_data["weapons"], list):
            for weapon_name in character_data["weapons"]:
                item = self.get_item_by_name(weapon_name, item_type="weapon")
                if item:
                    access_id = self.grant_item_access(
                        character_id=character_id,
                        item_id=item["id"],
                        access_type="inventory",
                        acquired_method="character_creation"
                    )
                    migrated_items["inventory"].append(access_id)
        
        # Migrate armor
        if "armor" in character_data and isinstance(character_data["armor"], list):
            for armor_name in character_data["armor"]:
                item = self.get_item_by_name(armor_name, item_type="armor")
                if item:
                    access_id = self.grant_item_access(
                        character_id=character_id,
                        item_id=item["id"],
                        access_type="equipped",
                        access_subtype="armor",
                        acquired_method="character_creation"
                    )
                    migrated_items["equipped"].append(access_id)
        
        return migrated_items
    
    def resolve_names_to_uuids(self, item_names: List[str], item_type: Optional[str] = None) -> List[str]:
        """Convert a list of item names to UUIDs (for backward compatibility)."""
        uuids = []
        
        for name in item_names:
            item = self.get_item_by_name(name, item_type)
            if item:
                uuids.append(item["id"])
            else:
                logger.warning(f"Could not find item '{name}' of type '{item_type}'")
        
        return uuids
    
    def get_catalog_stats(self) -> Dict[str, Any]:
        """Get statistics about the unified item catalog."""
        
        total_items = self.session.query(UnifiedItem).filter(UnifiedItem.is_active == True).count()
        
        official_items = self.session.query(UnifiedItem).filter(
            and_(UnifiedItem.is_active == True, UnifiedItem.source_type == "official")
        ).count()
        
        custom_items = self.session.query(UnifiedItem).filter(
            and_(UnifiedItem.is_active == True, UnifiedItem.source_type == "custom")
        ).count()
        
        # Count by type
        type_counts = {}
        for item_type in ["spell", "weapon", "armor", "equipment", "tool"]:
            count = self.session.query(UnifiedItem).filter(
                and_(UnifiedItem.is_active == True, UnifiedItem.item_type == item_type)
            ).count()
            type_counts[item_type] = count
        
        return {
            "total_items": total_items,
            "official_items": official_items,
            "custom_items": custom_items,
            "by_type": type_counts
        }
    
    # Validation methods for item allocation are now handled by creation_validation.py only.

    # =========================================================================
