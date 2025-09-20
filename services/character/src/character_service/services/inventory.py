"""Inventory management service."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID, uuid4

from character_service.core.exceptions import (
    ValidationError,
    InventoryError,
    ResourceExhaustedError,
    StateError
)
from character_service.repositories.inventory_repository import InventoryRepository
from character_service.repositories.character_storage_repository import CharacterStorageRepository


class InventoryServiceImpl:
    """Service for managing character inventory."""

    def __init__(self, inventory_repo: InventoryRepository, character_repo: CharacterStorageRepository):
        """Initialize the service.
        
        Args:
            inventory_repo: Repository for inventory operations
            character_repo: Repository for character operations
        """
        self.inventory_repo = inventory_repo
        self.character_repo = character_repo
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
        location: Optional[str] = None,
        item_type: Optional[str] = None,
        container_id: Optional[UUID] = None,
        include_deleted: bool = False,
    ) -> List[Dict[str, Any]]:
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
            # Get items via repository
            items = await self.inventory_repo.list_inventory_items(
                character_id=character_id,
                include_deleted=include_deleted
            )

            # Apply filters in memory
            filtered_items = items
            if location:
                filtered_items = [i for i in filtered_items if i["location"] == location]
            if item_type:
                filtered_items = [i for i in filtered_items if i["item_type"] == item_type]
            if container_id:
                filtered_items = [i for i in filtered_items if i.get("container_id") == str(container_id)]

            return filtered_items

        except Exception as e:
            raise InventoryError(f"Failed to get inventory: {str(e)}") from e

    async def move_item(
        self,
        character_id: UUID,
        item_id: UUID,
        location: str,
        container_id: Optional[UUID] = None,
    ) -> Dict[str, Any]:
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
            if location == "CONTAINER" and not container_id:
                raise ValidationError("Container ID required for container location")

            if container_id:
                container = await self._get_container(container_id, character_id)
                if not container:
                    raise ValidationError("Container not found")

                # Check container capacity
                if not await self._check_container_capacity(
                    container=container,
                    item_data={
                        "weight": item["weight"],
                        "quantity": item["quantity"],
                    },
                ):
                    raise ValidationError("Container capacity exceeded")

            # Update item
            update_data = {
                "location": location,
                "container_id": str(container_id) if container_id else None,
                "updated_at": datetime.utcnow().isoformat()
            }
            updated_item = await self.inventory_repo.update_inventory_item(item_id, update_data)
            return updated_item

        except Exception as e:
            raise InventoryError(f"Failed to move item: {str(e)}") from e

    async def update_quantity(
        self,
        character_id: UUID,
        item_id: UUID,
        quantity: int,
    ) -> Dict[str, Any]:
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

            if container_id := item.get("container_id"):
                # Check container capacity
                container = await self._get_container(UUID(container_id), character_id)
                if not await self._check_container_capacity(
                    container=container,
                    item_data={
                        "weight": item["weight"],
                        "quantity": quantity,
                    },
                    exclude_item_id=item_id,
                ):
                    raise ValidationError("Container capacity exceeded")

            # Update quantity
            update_data = {
                "quantity": quantity,
                "updated_at": datetime.utcnow().isoformat()
            }
            updated_item = await self.inventory_repo.update_inventory_item(item_id, update_data)
            return updated_item

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
                success = await self.inventory_repo.delete_inventory_item(item_id)
                if not success:
                    raise InventoryError("Failed to delete item permanently")
            else:
                update_data = {
                    "is_deleted": True,
                    "deleted_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                await self.inventory_repo.update_inventory_item(item_id, update_data)

        except Exception as e:
            raise InventoryError(f"Failed to delete item: {str(e)}") from e

    async def calculate_weight(
        self,
        character_id: UUID,
        location: Optional[str] = None,
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
                total_weight += item["weight"] * item["quantity"]

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

            # Get current currency items
            items = await self.get_inventory(
                character_id=character_id,
                item_type="CURRENCY",
                include_deleted=False
            )

            # Get or create currency item
            currency_item = next(
                (i for i in items if i.get("metadata", {}).get("type") == currency_type),
                None,
            )

            if not currency_item:
                # Create new currency item
                new_item = {
                    "id": str(uuid4()),
                    "character_id": str(character_id),
                    "name": f"{self._currency_types[currency_type]['name']} Pieces",
                    "item_type": "CURRENCY",
                    "location": "CARRIED",
                    "quantity": 0,
                    "weight": 0.02,  # 50 coins per pound
                    "metadata": {"type": currency_type},
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat()
                }
                currency_item = await self.inventory_repo.create_inventory_item(new_item)
                items.append(currency_item)

            # Update amount
            current_quantity = currency_item["quantity"]
            if operation == "add":
                new_quantity = current_quantity + amount
            elif operation == "remove":
                if current_quantity < amount:
                    raise ValidationError(f"Insufficient {currency_type}")
                new_quantity = current_quantity - amount
            else:
                raise ValidationError(f"Invalid operation: {operation}")

            # Update item
            update_data = {
                "quantity": new_quantity,
                "updated_at": datetime.utcnow().isoformat()
            }
            updated_item = await self.inventory_repo.update_inventory_item(
                UUID(currency_item["id"]),
                update_data
            )

            # Return current amounts for all currencies
            currency_amounts = {}
            for item in items:
                if item_type := item.get("metadata", {}).get("type"):
                    if item["id"] == currency_item["id"]:
                        currency_amounts[item_type] = new_quantity
                    else:
                        currency_amounts[item_type] = item["quantity"]
            return currency_amounts

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

        valid_item_types = [
            "WEAPON", "ARMOR", "POTION", "SCROLL", "RING", "ROD",
            "STAFF", "WAND", "WONDROUS", "AMMUNITION", "CONTAINER",
            "CURRENCY", "OTHER"
        ]
        if item_data["item_type"] not in valid_item_types:
            raise ValidationError(f"Invalid item type: {item_data['item_type']}")

        valid_locations = [
            "EQUIPPED", "CARRIED", "STORED", "CONTAINER",
            "MOUNT", "BANK", "VAULT"
        ]
        if location := item_data.get("location"):
            if location not in valid_locations:
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
    ) -> Optional[Dict[str, Any]]:
        """Get an inventory item.

        Args:
            item_id: The item ID
            character_id: The character ID for validation
            include_deleted: Whether to include deleted items

        Returns:
            The item if found
        """
        # Get item from repository
        item = await self.inventory_repo.get_inventory_item(
            item_id=item_id,
            character_id=character_id
        )
        if not item:
            return None

        # Check deleted status
        if not include_deleted and item.get("is_deleted", False):
            return None

        return item

    async def _get_container(
        self,
        container_id: UUID,
        character_id: UUID,
        include_deleted: bool = False,
    ) -> Optional[Dict[str, Any]]:
        """Get a container.

        Args:
            container_id: The container ID
            character_id: The character ID for validation
            include_deleted: Whether to include deleted containers

        Returns:
            The container if found
        """
        # Get container from repository
        container = await self.inventory_repo.get_inventory_item(
            item_id=container_id,
            character_id=character_id
        )
        if not container or container.get("item_type") != "CONTAINER":
            return None

        # Check deleted status
        if not include_deleted and container.get("is_deleted", False):
            return None

        return container

    async def _check_container_capacity(
        self,
        container: Dict[str, Any],
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
            character_id=UUID(container["character_id"]),
            container_id=UUID(container["id"]),
        )

        # Calculate current usage
        current_usage = 0.0
        for item in contents:
            if exclude_item_id and UUID(item["id"]) == exclude_item_id:
                continue

            capacity_type = container.get("metadata", {}).get("capacity_type", "weight")
            if capacity_type == "weight":
                current_usage += item["weight"] * item["quantity"]
            else:  # item count
                current_usage += item["quantity"]

        # Calculate new usage
        capacity_type = container.get("metadata", {}).get("capacity_type", "weight")
        if capacity_type == "weight":
            new_usage = (
                current_usage
                + item_data.get("weight", 0.0) * item_data.get("quantity", 1)
            )
        else:  # item count
            new_usage = current_usage + item_data.get("quantity", 1)

        capacity = container.get("metadata", {}).get("capacity", float('inf'))
        return new_usage <= capacity
