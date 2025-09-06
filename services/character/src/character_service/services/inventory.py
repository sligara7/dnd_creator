"""Inventory management service."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import select, and_, or_, not_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from character_service.core.exceptions import (
    ValidationError,
    InventoryError,
    ResourceExhaustedError,
    StateError,
)
from character_service.domain.inventory import (
    InventoryItem,
    MagicItem,
    ItemEffect,
    Container,
    ItemLocation,
    ItemType,
    AttunementState,
)


class InventoryService:
    """Service for managing character inventory."""

    def __init__(self, session: AsyncSession):
        """Initialize the service.

        Args:
            session: Database session
        """
        self.session = session
        self._currency_types = {
            "cp": {"name": "Copper", "value": 1},
            "sp": {"name": "Silver", "value": 10},
            "ep": {"name": "Electrum", "value": 50},
            "gp": {"name": "Gold", "value": 100},
            "pp": {"name": "Platinum", "value": 1000},
        }

    async def get_inventory(
        self,
        character_id: UUID,
        location: Optional[ItemLocation] = None,
        item_type: Optional[ItemType] = None,
        container_id: Optional[UUID] = None,
        include_deleted: bool = False,
    ) -> List[InventoryItem]:
        """Get a character's inventory items.

        Args:
            character_id: The character ID
            location: Optional location filter
            item_type: Optional item type filter
            container_id: Optional container ID filter
            include_deleted: Whether to include deleted items

        Returns:
            List of inventory items
        """
        try:
            # Build query
            query = (
                select(InventoryItem)
                .where(InventoryItem.character_id == character_id)
                .options(
                    joinedload(InventoryItem.container_items),
                )
            )

            # Apply filters
            if not include_deleted:
                query = query.where(not_(InventoryItem.is_deleted))
            if location:
                query = query.where(InventoryItem.location == location)
            if item_type:
                query = query.where(InventoryItem.item_type == item_type)
            if container_id is not None:
                query = query.where(InventoryItem.container_id == container_id)

            # Execute query
            result = await self.session.execute(query)
            return result.scalars().all()

        except Exception as e:
            raise InventoryError(f"Failed to get inventory: {str(e)}") from e

    async def move_item(
        self,
        character_id: UUID,
        item_id: UUID,
        location: ItemLocation,
        container_id: Optional[UUID] = None,
    ) -> InventoryItem:
        """Move an item to a new location.

        Args:
            character_id: The character ID
            item_id: The item ID to move
            location: New location
            container_id: Optional container ID

        Returns:
            The updated item

        Raises:
            ValidationError: If validation fails
            InventoryError: If operation fails
        """
        try:
            # Get item
            item = await self._get_item(item_id, character_id)
            if not item:
                raise ValidationError("Item not found")

            # Validate move
            if location == ItemLocation.CONTAINER and not container_id:
                raise ValidationError("Container ID required for container location")

            if container_id:
                container = await self._get_container(container_id, character_id)
                if not container:
                    raise ValidationError("Container not found")

                # Check container capacity
                if not await self._check_container_capacity(
                    container=container,
                    item_data={
                        "weight": item.weight,
                        "quantity": item.quantity,
                    },
                ):
                    raise ValidationError("Container capacity exceeded")

            # Update item
            item.location = location
            item.container_id = container_id
            item.updated_at = datetime.utcnow()

            await self.session.flush()
            return item

        except Exception as e:
            raise InventoryError(f"Failed to move item: {str(e)}") from e

    async def update_quantity(
        self,
        character_id: UUID,
        item_id: UUID,
        quantity: int,
    ) -> InventoryItem:
        """Update item quantity.

        Args:
            character_id: The character ID
            item_id: The item ID
            quantity: New quantity

        Returns:
            The updated item

        Raises:
            ValidationError: If validation fails
            InventoryError: If operation fails
        """
        try:
            # Get item
            item = await self._get_item(item_id, character_id)
            if not item:
                raise ValidationError("Item not found")

            # Validate quantity
            if quantity < 0:
                raise ValidationError("Quantity cannot be negative")

            if item.container_id:
                # Check container capacity
                container = await self._get_container(item.container_id, character_id)
                if not await self._check_container_capacity(
                    container=container,
                    item_data={
                        "weight": item.weight,
                        "quantity": quantity,
                    },
                    exclude_item_id=item_id,
                ):
                    raise ValidationError("Container capacity exceeded")

            # Update quantity
            item.quantity = quantity
            item.updated_at = datetime.utcnow()

            await self.session.flush()
            return item

        except Exception as e:
            raise InventoryError(f"Failed to update quantity: {str(e)}") from e

    async def delete_item(
        self,
        character_id: UUID,
        item_id: UUID,
        permanent: bool = False,
    ) -> None:
        """Delete an item.

        Args:
            character_id: The character ID
            item_id: The item ID
            permanent: Whether to permanently delete

        Raises:
            ValidationError: If validation fails
            InventoryError: If operation fails
        """
        try:
            # Get item
            item = await self._get_item(item_id, character_id)
            if not item:
                raise ValidationError("Item not found")

            if permanent:
                await self.session.delete(item)
            else:
                item.is_deleted = True
                item.updated_at = datetime.utcnow()

            await self.session.flush()

        except Exception as e:
            raise InventoryError(f"Failed to delete item: {str(e)}") from e

    async def calculate_weight(
        self,
        character_id: UUID,
        location: Optional[ItemLocation] = None,
        container_id: Optional[UUID] = None,
    ) -> float:
        """Calculate total weight of items.

        Args:
            character_id: The character ID
            location: Optional location filter
            container_id: Optional container ID filter

        Returns:
            Total weight
        """
        try:
            # Get items
            items = await self.get_inventory(
                character_id=character_id,
                location=location,
                container_id=container_id,
            )

            # Calculate total weight
            total_weight = 0.0
            for item in items:
                total_weight += item.weight * item.quantity

            return total_weight

        except Exception as e:
            raise InventoryError(f"Failed to calculate weight: {str(e)}") from e

    async def manage_currency(
        self,
        character_id: UUID,
        currency_type: str,
        amount: int,
        operation: str = "add",
    ) -> Dict[str, int]:
        """Manage character currency.

        Args:
            character_id: The character ID
            currency_type: Type of currency (cp, sp, ep, gp, pp)
            amount: Amount to add/remove
            operation: Operation to perform (add/remove)

        Returns:
            Updated currency amounts

        Raises:
            ValidationError: If validation fails
            InventoryError: If operation fails
        """
        try:
            # Validate currency type
            if currency_type not in self._currency_types:
                raise ValidationError(f"Invalid currency type: {currency_type}")

            # Get current currency
            query = select(InventoryItem).where(
                and_(
                    InventoryItem.character_id == character_id,
                    InventoryItem.item_type == ItemType.CURRENCY,
                    not_(InventoryItem.is_deleted),
                )
            )
            result = await self.session.execute(query)
            currency_items = result.scalars().all()

            # Get or create currency item
            currency_item = next(
                (i for i in currency_items if i.metadata.get("type") == currency_type),
                None,
            )

            if not currency_item:
                currency_item = InventoryItem(
                    character_id=character_id,
                    name=f"{self._currency_types[currency_type]['name']} Pieces",
                    item_type=ItemType.CURRENCY,
                    location=ItemLocation.CARRIED,
                    quantity=0,
                    weight=0.02,  # 50 coins per pound
                    metadata={"type": currency_type},
                )
                self.session.add(currency_item)

            # Update amount
            if operation == "add":
                currency_item.quantity += amount
            elif operation == "remove":
                if currency_item.quantity < amount:
                    raise ValidationError(f"Insufficient {currency_type}")
                currency_item.quantity -= amount
            else:
                raise ValidationError(f"Invalid operation: {operation}")

            currency_item.updated_at = datetime.utcnow()

            # Return current amounts
            await self.session.flush()
            return {
                item.metadata["type"]: item.quantity
                for item in currency_items + [currency_item]
            }

        except Exception as e:
            raise InventoryError(f"Failed to manage currency: {str(e)}") from e

    async def _validate_item_data(self, item_data: Dict[str, Any]) -> None:
        """Validate item data.

        Args:
            item_data: Item data to validate

        Raises:
            ValidationError: If validation fails
        """
        required_fields = ["name", "item_type"]
        for field in required_fields:
            if field not in item_data:
                raise ValidationError(f"Missing required field: {field}")

        if not isinstance(item_data["name"], str) or not item_data["name"]:
            raise ValidationError("Name must be a non-empty string")

        if not ItemType.has_value(item_data["item_type"]):
            raise ValidationError(f"Invalid item type: {item_data['item_type']}")

        if location := item_data.get("location"):
            if not ItemLocation.has_value(location):
                raise ValidationError(f"Invalid location: {location}")

        if quantity := item_data.get("quantity"):
            if not isinstance(quantity, int) or quantity < 0:
                raise ValidationError("Quantity must be a non-negative integer")

        if weight := item_data.get("weight"):
            if not isinstance(weight, (int, float)) or weight < 0:
                raise ValidationError("Weight must be a non-negative number")

        if value := item_data.get("value"):
            if not isinstance(value, int) or value < 0:
                raise ValidationError("Value must be a non-negative integer")

    async def _get_item(
        self,
        item_id: UUID,
        character_id: UUID,
        include_deleted: bool = False,
    ) -> Optional[InventoryItem]:
        """Get an inventory item.

        Args:
            item_id: The item ID
            character_id: The character ID for validation
            include_deleted: Whether to include deleted items

        Returns:
            The item if found
        """
        query = select(InventoryItem).where(
            and_(
                InventoryItem.id == item_id,
                InventoryItem.character_id == character_id,
            )
        )

        if not include_deleted:
            query = query.where(not_(InventoryItem.is_deleted))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_container(
        self,
        container_id: UUID,
        character_id: UUID,
        include_deleted: bool = False,
    ) -> Optional[Container]:
        """Get a container.

        Args:
            container_id: The container ID
            character_id: The character ID for validation
            include_deleted: Whether to include deleted containers

        Returns:
            The container if found
        """
        query = select(Container).where(
            and_(
                Container.id == container_id,
                Container.character_id == character_id,
            )
        )

        if not include_deleted:
            query = query.where(not_(Container.is_deleted))

        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _check_container_capacity(
        self,
        container: Container,
        item_data: Dict[str, Any],
        exclude_item_id: Optional[UUID] = None,
    ) -> bool:
        """Check if a container has capacity for an item.

        Args:
            container: The container to check
            item_data: Item data to check
            exclude_item_id: Optional item ID to exclude from calculation

        Returns:
            Whether the container has capacity
        """
        # Get current contents
        contents = await self.get_inventory(
            character_id=container.character_id,
            container_id=container.id,
        )

        # Calculate current usage
        current_usage = 0.0
        for item in contents:
            if exclude_item_id and item.id == exclude_item_id:
                continue

            if container.capacity_type == "weight":
                current_usage += item.weight * item.quantity
            else:  # item count
                current_usage += item.quantity

        # Calculate new usage
        if container.capacity_type == "weight":
            new_usage = (
                current_usage
                + item_data.get("weight", 0.0) * item_data.get("quantity", 1)
            )
        else:  # item count
            new_usage = current_usage + item_data.get("quantity", 1)

        return new_usage <= container.capacity
