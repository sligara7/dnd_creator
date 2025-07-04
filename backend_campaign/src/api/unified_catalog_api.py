"""
API endpoints for the unified item catalog system.
Provides REST endpoints for searching, managing, and accessing the unified catalog.
"""

from typing import Dict, Any, List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)

# Create router
unified_catalog_router = APIRouter(prefix="/api/v2/catalog", tags=["catalog"])

# Equipment Swap Request Model
class EquipmentSwapRequest(BaseModel):
    character_id: str = Field(..., description="Character UUID")
    from_item_id: str = Field(..., description="UUID of item to unequip")
    to_item_id: str = Field(..., description="UUID of item to equip")
    slot: Optional[str] = Field(None, description="Equipment slot (optional)")
    skip_validation: bool = Field(False, description="Skip validation checks")

# Placeholder endpoint for now
@unified_catalog_router.get("/status")
async def catalog_status():
    """Get catalog status."""
    return {"status": "active", "message": "Unified catalog API is running"}

from src.services.unified_catalog_service import UnifiedCatalogService
from src.services.allocation_service import AllocationService
from src.models.database_models import get_db

logger = logging.getLogger(__name__)

# Create router
unified_catalog_router = APIRouter(prefix="/api/v2/catalog", tags=["unified-catalog"])

# Dependency to get the unified catalog service
def get_catalog_service(db = Depends(get_db)) -> UnifiedCatalogService:
    return UnifiedCatalogService(db)

# Dependency to get the allocation service
def get_allocation_service(db = Depends(get_db)) -> AllocationService:
    return AllocationService(db)

# ============================================================================
# PYDANTIC MODELS
# ============================================================================

class ItemSearchRequest(BaseModel):
    item_type: Optional[str] = Field(None, description="Type of item (spell, weapon, armor, equipment, tool)")
    item_subtype: Optional[str] = Field(None, description="Subtype of item")
    spell_level: Optional[int] = Field(None, description="Spell level (for spells only)")
    spell_school: Optional[str] = Field(None, description="Spell school (for spells only)")
    class_restrictions: Optional[List[str]] = Field(None, description="Classes that can use this item")
    source_type: Optional[str] = Field(None, description="Source type (official, custom, llm_generated)")
    source_info: Optional[str] = Field(None, description="LLM or provenance info (optional)")
    name_filter: Optional[str] = Field(None, description="Filter by name (partial match)")
    limit: int = Field(100, description="Maximum number of results", ge=1, le=500)

class CreateCustomItemRequest(BaseModel):
    source_type: Optional[str] = Field(None, description="Source type (official, custom, llm_generated)")
    source_info: Optional[str] = Field(None, description="LLM or provenance info (optional)")
    llm_metadata: Optional[dict] = Field(None, description="LLM-specific metadata (model, prompt, etc.)")
    name: str = Field(..., description="Name of the item")
    item_type: str = Field(..., description="Type of item (spell, weapon, armor, equipment, tool)")
    content_data: Dict[str, Any] = Field(..., description="Complete item data")
    item_subtype: Optional[str] = Field(None, description="Subtype of item")
    short_description: Optional[str] = Field(None, description="Brief description")
    created_by: Optional[str] = Field(None, description="Creator name")
    spell_level: Optional[int] = Field(None, description="Spell level (for spells)")
    spell_school: Optional[str] = Field(None, description="Spell school (for spells)")
    class_restrictions: Optional[List[str]] = Field(None, description="Classes that can use this item")
    rarity: Optional[str] = Field(None, description="Item rarity")
    requires_attunement: bool = Field(False, description="Whether item requires attunement")
    value_gp: Optional[int] = Field(None, description="Value in gold pieces")
    weight_lbs: Optional[str] = Field(None, description="Weight in pounds")
    is_public: bool = Field(False, description="Whether item is public")

class GrantItemAccessRequest(BaseModel):
    character_id: str = Field(..., description="Character UUID")
    item_id: str = Field(..., description="Item UUID")
    access_type: str = Field(..., description="Type of access (spells_known, inventory, equipped, etc.)")
    access_subtype: Optional[str] = Field(None, description="Subtype of access")
    quantity: int = Field(1, description="Quantity", ge=1)
    acquired_method: str = Field("manual", description="How the item was acquired")
    custom_properties: Optional[Dict[str, Any]] = Field(None, description="Custom properties for this instance")
    skip_validation: bool = Field(False, description="Skip validation checks (admin only)")

class ValidateItemAllocationRequest(BaseModel):
    character_id: str = Field(..., description="Character UUID")
    item_id: str = Field(..., description="Item UUID")
    access_type: str = Field(..., description="Type of access to validate")

class ValidationResponse(BaseModel):
    is_valid: bool = Field(..., description="Whether the allocation is valid")
    reason: str = Field("", description="Reason if invalid")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")

# ============================================================================
# CATALOG ENDPOINTS
# ============================================================================

@unified_catalog_router.get("/stats")
async def get_catalog_stats(catalog: UnifiedCatalogService = Depends(get_catalog_service)):
    """Get statistics about the unified item catalog."""
    try:
        stats = catalog.get_catalog_stats()
        return {
            "status": "success",
            "data": stats
        }
    except Exception as e:
        logger.error(f"Error getting catalog stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.post("/search")
async def search_catalog(
    request: ItemSearchRequest,
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Search the unified item catalog with various filters."""
    try:
        items = catalog.search_items(
            item_type=request.item_type,
            item_subtype=request.item_subtype,
            spell_level=request.spell_level,
            spell_school=request.spell_school,
            class_restrictions=request.class_restrictions,
            source_type=request.source_type,
            name_filter=request.name_filter,
            limit=request.limit
        )
        
        return {
            "status": "success",
            "data": {
                "items": items,
                "count": len(items),
                "filters_applied": request.dict(exclude_none=True)
            }
        }
    except Exception as e:
        logger.error(f"Error searching catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/search")
async def search_catalog_get(
    item_type: Optional[str] = Query(None),
    item_subtype: Optional[str] = Query(None),
    spell_level: Optional[int] = Query(None),
    spell_school: Optional[str] = Query(None),
    source_type: Optional[str] = Query(None),
    name_filter: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=500),
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Search the unified item catalog using GET parameters."""
    try:
        items = catalog.search_items(
            item_type=item_type,
            item_subtype=item_subtype,
            spell_level=spell_level,
            spell_school=spell_school,
            source_type=source_type,
            name_filter=name_filter,
            limit=limit
        )
        
        return {
            "status": "success",
            "data": {
                "items": items,
                "count": len(items)
            }
        }
    except Exception as e:
        logger.error(f"Error searching catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/item/{item_id}")
async def get_item_by_id(
    item_id: str,
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Get a specific item by UUID."""
    try:
        item = catalog.get_item_by_id(item_id)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {
            "status": "success",
            "data": item
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item {item_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/item/by-name/{name}")
async def get_item_by_name(
    name: str,
    item_type: Optional[str] = Query(None),
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Get a specific item by name (for backward compatibility)."""
    try:
        item = catalog.get_item_by_name(name, item_type)
        if not item:
            raise HTTPException(status_code=404, detail="Item not found")
        
        return {
            "status": "success",
            "data": item
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting item by name {name}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.post("/item")
async def create_custom_item(
    request: CreateCustomItemRequest,
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Create a new custom item in the catalog."""
    try:
        item_id = catalog.create_custom_item(
            name=request.name,
            item_type=request.item_type,
            content_data=request.content_data,
            item_subtype=request.item_subtype,
            short_description=request.short_description,
            created_by=request.created_by,
            spell_level=request.spell_level,
            spell_school=request.spell_school,
            class_restrictions=request.class_restrictions,
            rarity=request.rarity,
            requires_attunement=request.requires_attunement,
            value_gp=request.value_gp,
            weight_lbs=request.weight_lbs,
            is_public=request.is_public,
            source_type=request.source_type,
            source_info=request.source_info,
            llm_metadata=request.llm_metadata
        )
        
        return {
            "status": "success",
            "data": {
                "item_id": item_id,
                "message": f"Custom item '{request.name}' created successfully"
            }
        }
    except Exception as e:
        logger.error(f"Error creating custom item: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# CHARACTER-ITEM RELATIONSHIP ENDPOINTS
# ============================================================================

@unified_catalog_router.post("/access")
async def grant_item_access(
    request: GrantItemAccessRequest,
    allocation_service: AllocationService = Depends(get_allocation_service)
):
    """Grant a character access to an item."""
    try:
        result = allocation_service.allocate_item_to_character(
            character_id=request.character_id,
            item_id=request.item_id,
            access_type=request.access_type,
            access_subtype=request.access_subtype,
            quantity=request.quantity,
            acquired_method=request.acquired_method,
            custom_properties=request.custom_properties,
            skip_validation=request.skip_validation
        )
        
        return {
            "status": "success",
            "data": result
        }
    except ValueError as e:
        # Validation errors should be 400 Bad Request
        error_message = str(e)
        if "validation" in error_message.lower() or "cannot use" in error_message.lower() or "not found" in error_message.lower():
            logger.info(f"Item allocation validation failed: {error_message}")
            raise HTTPException(status_code=400, detail=error_message)
        else:
            logger.error(f"Item allocation error: {error_message}")
            raise HTTPException(status_code=500, detail=error_message)
    except RuntimeError as e:
        logger.error(f"Database error granting item access: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error granting item access: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.delete("/access/{character_id}/{item_id}")
async def revoke_item_access(
    character_id: str,
    item_id: str,
    access_type: str = Query(...),
    access_subtype: Optional[str] = Query(None),
    allocation_service: AllocationService = Depends(get_allocation_service)
):
    """Revoke a character's access to an item."""
    try:
        result = allocation_service.deallocate_item_from_character(
            character_id=character_id,
            item_id=item_id,
            access_type=access_type,
            access_subtype=access_subtype
        )
        
        return {
            "status": "success",
            "data": result
        }
    except ValueError as e:
        logger.error(f"Deallocation error: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Database error revoking item access: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error revoking item access: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/character/{character_id}/items")
async def get_character_items(
    character_id: str,
    access_type: Optional[str] = Query(None),
    item_type: Optional[str] = Query(None),
    allocation_service: AllocationService = Depends(get_allocation_service)
):
    """Get all items a character has access to."""
    try:
        result = allocation_service.get_character_allocations(
            character_id=character_id,
            access_type=access_type,
            item_type=item_type
        )
        
        return {
            "status": "success",
            "data": result
        }
    except ValueError as e:
        logger.error(f"Error getting character items: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except RuntimeError as e:
        logger.error(f"Database error getting character items: {e}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting character items: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/character/{character_id}/spells")
async def get_character_spells(
    character_id: str,
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Get all spells a character knows or has prepared."""
    try:
        spells = catalog.get_character_spells(character_id)
        
        return {
            "status": "success",
            "data": {
                "character_id": character_id,
                "spells": spells
            }
        }
    except Exception as e:
        logger.error(f"Error getting character spells: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.get("/character/{character_id}/equipment")
async def get_character_equipment(
    character_id: str,
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Get all equipment a character owns."""
    try:
        equipment = catalog.get_character_equipment(character_id)
        
        return {
            "status": "success",
            "data": {
                "character_id": character_id,
                "equipment": equipment
            }
        }
    except Exception as e:
        logger.error(f"Error getting character equipment: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================================
# MIGRATION ENDPOINTS
# ============================================================================

@unified_catalog_router.post("/migrate/populate")
async def populate_catalog(catalog: UnifiedCatalogService = Depends(get_catalog_service)):
    """Populate the unified catalog with official D&D content."""
    try:
        from src.services.unified_catalog_migration import run_migration
        
        results = run_migration(catalog.db)
        
        return {
            "status": "success",
            "data": {
                "migration_results": results,
                "message": "Catalog populated successfully"
            }
        }
    except Exception as e:
        logger.error(f"Error populating catalog: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@unified_catalog_router.post("/migrate/character/{character_id}")
async def migrate_character_to_uuid(
    character_id: str,
    character_data: Dict[str, Any],
    catalog: UnifiedCatalogService = Depends(get_catalog_service)
):
    """Migrate a character's item lists from names to UUID-based system."""
    try:
        migrated = catalog.migrate_character_to_uuid_system(character_id, character_data)
        
        return {
            "status": "success",
            "data": {
                "character_id": character_id,
                "migrated_items": migrated,
                "message": "Character migrated to UUID system successfully"
            }
        }
    except Exception as e:
        logger.error(f"Error migrating character {character_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
