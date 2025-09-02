"""Inventory Management Endpoints"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID

from character_service.api.v2.dependencies import get_inventory_service
from character_service.api.v2.models import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    ErrorResponse,
)
from character_service.services.interfaces import InventoryService

router = APIRouter()

@router.get(
    "/{character_id}",
    response_model=List[InventoryItemResponse],
    responses={500: {"model": ErrorResponse}},
)
async def get_character_inventory(
    character_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> List[InventoryItemResponse]:
    """Get character inventory."""
    try:
        items = await inventory_service.get_character_items(character_id)
        return [InventoryItemResponse.model_validate(i.model_dump()) for i in items]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.get(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def get_inventory_item(
    item_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemResponse:
    """Get inventory item by ID."""
    item = await inventory_service.get_item(item_id)
    if not item:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found",
        )
    return InventoryItemResponse.model_validate(item.model_dump())

@router.post(
    "/{character_id}/items",
    response_model=InventoryItemResponse,
    responses={500: {"model": ErrorResponse}},
)
async def add_inventory_item(
    character_id: UUID,
    item: InventoryItemCreate,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemResponse:
    """Add item to character inventory."""
    try:
        new_item = await inventory_service.add_item(
            character_id=character_id,
            item_data=item.item_data,
            quantity=item.quantity,
            equipped=item.equipped,
            container=item.container,
            notes=item.notes,
        )
        return InventoryItemResponse.model_validate(new_item.model_dump())
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=str(e),
        )

@router.put(
    "/items/{item_id}",
    response_model=InventoryItemResponse,
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def update_inventory_item(
    item_id: UUID,
    item: InventoryItemUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> InventoryItemResponse:
    """Update inventory item."""
    updated_item = await inventory_service.update_item(
        item_id=item_id,
        quantity=item.quantity,
        equipped=item.equipped,
        container=item.container,
        notes=item.notes,
    )
    if not updated_item:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found",
        )
    return InventoryItemResponse.model_validate(updated_item.model_dump())

@router.delete(
    "/items/{item_id}",
    responses={404: {"model": ErrorResponse}, 500: {"model": ErrorResponse}},
)
async def remove_inventory_item(
    item_id: UUID,
    inventory_service: InventoryService = Depends(get_inventory_service),
) -> None:
    """Remove item from inventory."""
    deleted = await inventory_service.remove_item(item_id)
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Item {item_id} not found",
        )
