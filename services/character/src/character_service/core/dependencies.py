"""Service dependencies."""
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.database import get_session
from character_service.services.inventory import InventoryService
from character_service.services.magic_items import MagicItemService


async def get_inventory_service(
    session: AsyncSession = Depends(get_session),
) -> InventoryService:
    """Get inventory service dependency.

    Args:
        session: Database session

    Returns:
        Inventory service
    """
    return InventoryService(session)


async def get_magic_item_service(
    session: AsyncSession = Depends(get_session),
) -> MagicItemService:
    """Get magic item service dependency.

    Args:
        session: Database session

    Returns:
        Magic item service
    """
    return MagicItemService(session)
