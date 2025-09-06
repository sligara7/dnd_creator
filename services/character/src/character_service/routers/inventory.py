"""Inventory router."""
from typing import List, Dict, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import UUID4

from character_service.core.exceptions import (
    ValidationError,
    InventoryError,
    ResourceExhaustedError,
    StateError,
)
from character_service.domain.inventory import (
    InventoryItem,
    ItemLocation,
    ItemType,
    Container,
    MagicItem,
)
from character_service.schemas.inventory import (
    InventoryItemCreate,
    InventoryItemUpdate,
    InventoryItemResponse,
    ContainerCreate,
    ContainerUpdate,
    ContainerResponse,
    MagicItemCreate,
    MagicItemUpdate,
    MagicItemResponse,
    CurrencyResponse,
)
from character_service.services.inventory import InventoryService
from character_service.services.magic_items import MagicItemService
from character_service.core.dependencies import (
    get_inventory_service,
    get_magic_item_service,
)

# Router instance
router = APIRouter()


@router.get(
    "/characters/{character_id}/inventory",
    response_model=List[InventoryItemResponse],
    tags=["inventory"],
)
async def get_inventory(
    character_id: UUID4,
    location: Optional[ItemLocation] = None,
    item_type: Optional[ItemType] = None,
    container_id: Optional[UUID4] = None,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Get a character's inventory."""
    try:
        items = await inventory_service.get_inventory(
            character_id=character_id,
            location=location,
            item_type=item_type,
            container_id=container_id,
        )
        return [InventoryItemResponse.from_orm(item) for item in items]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory",
    response_model=InventoryItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["inventory"],
)
async def add_item(
    character_id: UUID4,
    item: InventoryItemCreate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Add an item to inventory."""
    try:
        created_item = await inventory_service.add_item(
            character_id=character_id,
            item_data=item.dict(),
        )
        return InventoryItemResponse.from_orm(created_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/characters/{character_id}/inventory/{item_id}",
    response_model=InventoryItemResponse,
    tags=["inventory"],
)
async def update_item(
    character_id: UUID4,
    item_id: UUID4,
    item: InventoryItemUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Update an inventory item."""
    try:
        updated_item = await inventory_service.update_quantity(
            character_id=character_id,
            item_id=item_id,
            quantity=item.quantity,
        )
        return InventoryItemResponse.from_orm(updated_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/characters/{character_id}/inventory/{item_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    tags=["inventory"],
)
async def delete_item(
    character_id: UUID4,
    item_id: UUID4,
    permanent: bool = False,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Delete an inventory item."""
    try:
        await inventory_service.delete_item(
            character_id=character_id,
            item_id=item_id,
            permanent=permanent,
        )
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/characters/{character_id}/inventory/{item_id}/move",
    response_model=InventoryItemResponse,
    tags=["inventory"],
)
async def move_item(
    character_id: UUID4,
    item_id: UUID4,
    location: ItemLocation,
    container_id: Optional[UUID4] = None,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Move an item to a new location."""
    try:
        moved_item = await inventory_service.move_item(
            character_id=character_id,
            item_id=item_id,
            location=location,
            container_id=container_id,
        )
        return InventoryItemResponse.from_orm(moved_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/inventory/weight",
    response_model=Dict[str, float],
    tags=["inventory"],
)
async def calculate_weight(
    character_id: UUID4,
    location: Optional[ItemLocation] = None,
    container_id: Optional[UUID4] = None,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Calculate total weight of items."""
    try:
        total_weight = await inventory_service.calculate_weight(
            character_id=character_id,
            location=location,
            container_id=container_id,
        )
        return {"total_weight": total_weight}
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/characters/{character_id}/inventory/currency",
    response_model=CurrencyResponse,
    tags=["inventory"],
)
async def get_currency(
    character_id: UUID4,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Get character currency."""
    try:
        currency = await inventory_service.get_currency(
            character_id=character_id,
        )
        return CurrencyResponse(**currency)
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/currency/{currency_type}",
    response_model=CurrencyResponse,
    tags=["inventory"],
)
async def manage_currency(
    character_id: UUID4,
    currency_type: str,
    amount: int,
    operation: str,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Manage character currency."""
    try:
        currency = await inventory_service.manage_currency(
            character_id=character_id,
            currency_type=currency_type,
            amount=amount,
            operation=operation,
        )
        return CurrencyResponse(**currency)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Container endpoints
@router.get(
    "/characters/{character_id}/inventory/containers",
    response_model=List[ContainerResponse],
    tags=["inventory"],
)
async def get_containers(
    character_id: UUID4,
    include_contents: bool = False,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Get character containers."""
    try:
        containers = await inventory_service.get_containers(
            character_id=character_id,
            include_contents=include_contents,
        )
        return [ContainerResponse.from_orm(container) for container in containers]
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/containers",
    response_model=ContainerResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["inventory"],
)
async def create_container(
    character_id: UUID4,
    container: ContainerCreate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Create a new container."""
    try:
        created_container = await inventory_service.create_container(
            character_id=character_id,
            container_data=container.dict(),
        )
        return ContainerResponse.from_orm(created_container)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/characters/{character_id}/inventory/containers/{container_id}",
    response_model=ContainerResponse,
    tags=["inventory"],
)
async def update_container(
    character_id: UUID4,
    container_id: UUID4,
    container: ContainerUpdate,
    inventory_service: InventoryService = Depends(get_inventory_service),
):
    """Update a container."""
    try:
        updated_container = await inventory_service.update_container(
            character_id=character_id,
            container_id=container_id,
            container_data=container.dict(exclude_unset=True),
        )
        return ContainerResponse.from_orm(updated_container)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


# Magic item endpoints
@router.get(
    "/characters/{character_id}/inventory/magic-items",
    response_model=List[MagicItemResponse],
    tags=["inventory"],
)
async def get_magic_items(
    character_id: UUID4,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Get character magic items."""
    try:
        items = await magic_item_service.get_character_magic_items(
            character_id=character_id,
        )
        return [MagicItemResponse.from_orm(item) for item in items]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/magic-items",
    response_model=MagicItemResponse,
    status_code=status.HTTP_201_CREATED,
    tags=["inventory"],
)
async def create_magic_item(
    character_id: UUID4,
    item: MagicItemCreate,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Create a new magic item."""
    try:
        created_item = await magic_item_service.create_magic_item(
            character_id=character_id,
            item_data=item.dict(),
        )
        return MagicItemResponse.from_orm(created_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.put(
    "/characters/{character_id}/inventory/magic-items/{item_id}",
    response_model=MagicItemResponse,
    tags=["inventory"],
)
async def update_magic_item(
    character_id: UUID4,
    item_id: UUID4,
    item: MagicItemUpdate,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Update a magic item."""
    try:
        updated_item = await magic_item_service.update_magic_item(
            character_id=character_id,
            item_id=item_id,
            item_data=item.dict(exclude_unset=True),
        )
        return MagicItemResponse.from_orm(updated_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/magic-items/{item_id}/attune",
    response_model=MagicItemResponse,
    tags=["inventory"],
)
async def begin_attunement(
    character_id: UUID4,
    item_id: UUID4,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Begin attunement with a magic item."""
    try:
        attuning_item = await magic_item_service.begin_attunement(
            character_id=character_id,
            item_id=item_id,
        )
        return MagicItemResponse.from_orm(attuning_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except ResourceExhaustedError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/magic-items/{item_id}/complete-attunement",
    response_model=MagicItemResponse,
    tags=["inventory"],
)
async def complete_attunement(
    character_id: UUID4,
    item_id: UUID4,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Complete attunement with a magic item."""
    try:
        attuned_item = await magic_item_service.complete_attunement(
            character_id=character_id,
            item_id=item_id,
        )
        return MagicItemResponse.from_orm(attuned_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/magic-items/{item_id}/break-attunement",
    response_model=MagicItemResponse,
    tags=["inventory"],
)
async def break_attunement(
    character_id: UUID4,
    item_id: UUID4,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Break attunement with a magic item."""
    try:
        broken_item = await magic_item_service.break_attunement(
            character_id=character_id,
            item_id=item_id,
        )
        return MagicItemResponse.from_orm(broken_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post(
    "/characters/{character_id}/inventory/magic-items/{item_id}/use",
    response_model=MagicItemResponse,
    tags=["inventory"],
)
async def use_charges(
    character_id: UUID4,
    item_id: UUID4,
    charges: int,
    magic_item_service: MagicItemService = Depends(get_magic_item_service),
):
    """Use charges from a magic item."""
    try:
        used_item = await magic_item_service.use_charges(
            character_id=character_id,
            item_id=item_id,
            charges=charges,
        )
        return MagicItemResponse.from_orm(used_item)
    except ValidationError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    except StateError as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except InventoryError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
