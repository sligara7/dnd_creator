"""
Item Allocation Service

This service provides a clean interface for validating and managing character-item allocations
with proper session management to avoid session isolation issues.
"""

import logging
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models.database_models import Character, UnifiedItem, CharacterItemAccess
from src.services.creation_validation import validate_item_allocation, CreationResult

logger = logging.getLogger(__name__)


class AllocationService:
    def swap_equipment(
        self,
        character_id: str,
        from_item_id: str,
        to_item_id: str,
        slot: Optional[str] = None,
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Atomically unequip one item and equip another for a character.
        Args:
            character_id: UUID of the character
            from_item_id: UUID of the item to unequip
            to_item_id: UUID of the item to equip
            slot: Equipment slot (optional)
            skip_validation: Skip validation checks
        Returns:
            Dict with swap result
        Raises:
            ValueError: If validation fails or swap is not possible
        """
        try:
            # Load character and both items
            character = self.db.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            from_item = self.db.query(UnifiedItem).filter(UnifiedItem.id == from_item_id).first()
            if not from_item:
                raise ValueError(f"Item to unequip not found: {from_item_id}")
            to_item = self.db.query(UnifiedItem).filter(UnifiedItem.id == to_item_id).first()
            if not to_item:
                raise ValueError(f"Item to equip not found: {to_item_id}")

            # Find the equipped allocation for from_item
            from_access = self.db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == from_item_id,
                CharacterItemAccess.access_type == "equipped",
                CharacterItemAccess.access_subtype == slot
            ).first()
            if not from_access:
                raise ValueError(f"Item {from_item.name} is not currently equipped in slot '{slot or 'any'}'")

            # Validate the new item can be equipped
            if not skip_validation:
                validation_result = self._validate_allocation(character, to_item, "equipped")
                if not validation_result.success:
                    raise ValueError(f"Cannot equip {to_item.name}: {validation_result.error}")

            # Check if the slot is already occupied by another allocation for to_item
            to_access = self.db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == to_item_id,
                CharacterItemAccess.access_type == "equipped",
                CharacterItemAccess.access_subtype == slot
            ).first()
            if to_access:
                raise ValueError(f"{to_item.name} is already equipped in slot '{slot or 'any'}'")

            # Unequip from_item (delete allocation)
            self.db.delete(from_access)

            # Equip to_item (create allocation)
            new_access = CharacterItemAccess(
                character_id=character_id,
                item_id=to_item_id,
                access_type="equipped",
                access_subtype=slot,
                quantity=1,
                acquired_method="swap",
                custom_properties={}
            )
            self.db.add(new_access)
            self.db.commit()

            return {
                "success": True,
                "message": f"Swapped {from_item.name} for {to_item.name} in slot '{slot or 'any'}'",
                "unequipped": from_item.name,
                "equipped": to_item.name,
                "slot": slot
            }
        except (ValueError, RuntimeError) as e:
            self.db.rollback()
            logger.error(f"Equipment swap failed: {e}")
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during equipment swap: {e}")
            raise RuntimeError(f"Database operation failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during equipment swap: {e}")
            raise RuntimeError(f"Equipment swap failed: {str(e)}")
    """Service for managing character-item allocations with validation."""
    
    def __init__(self, db_session: Session):
        """Initialize with a database session."""
        self.db = db_session
    
    def allocate_item_to_character(
        self,
        character_id: str,
        item_id: str,
        access_type: str = "inventory",
        access_subtype: Optional[str] = None,
        quantity: int = 1,
        acquired_method: Optional[str] = None,
        custom_properties: Optional[Dict[str, Any]] = None,
        skip_validation: bool = False
    ) -> Dict[str, Any]:
        """
        Allocate an item to a character with validation.
        
        Args:
            character_id: UUID of the character
            item_id: UUID of the item
            access_type: Type of access (inventory, equipped, spells_known, etc.)
            access_subtype: Subtype of access if applicable
            quantity: Quantity to allocate
            acquired_method: How the item was acquired
            custom_properties: Additional properties
            skip_validation: Skip validation checks
        
        Returns:
            Dict with success status and allocation details
        
        Raises:
            ValueError: If validation fails
            RuntimeError: If database operation fails
        """
        try:
            # Load character and item in the same session
            character = self.db.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            item = self.db.query(UnifiedItem).filter(UnifiedItem.id == item_id).first()
            if not item:
                raise ValueError(f"Item not found: {item_id}")
            
            # Validate allocation if not skipped
            if not skip_validation:
                validation_result = self._validate_allocation(character, item, access_type)
                if not validation_result.success:
                    raise ValueError(f"Allocation validation failed: {validation_result.error}")
            
            # Check if allocation already exists
            existing_access = self.db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == item_id,
                CharacterItemAccess.access_type == access_type,
                CharacterItemAccess.access_subtype == access_subtype
            ).first()
            
            if existing_access:
                # Update existing allocation
                existing_access.quantity += quantity
                existing_access.updated_at = None  # Will be set automatically
                access_id = existing_access.id
                logger.info(f"Updated existing allocation: {access_id}")
            else:
                # Create new allocation
                new_access = CharacterItemAccess(
                    character_id=character_id,
                    item_id=item_id,
                    access_type=access_type,
                    access_subtype=access_subtype,
                    quantity=quantity,
                    acquired_method=acquired_method or "Unknown",
                    custom_properties=custom_properties or {}
                )
                
                self.db.add(new_access)
                self.db.flush()  # Get the ID
                access_id = new_access.id
                logger.info(f"Created new allocation: {access_id}")
            
            # Commit the transaction
            self.db.commit()
            
            return {
                "success": True,
                "access_id": access_id,
                "character_id": character_id,
                "item_id": item_id,
                "access_type": access_type,
                "quantity": quantity,
                "message": "Item allocated successfully"
            }
            
        except (ValueError, RuntimeError) as e:
            self.db.rollback()
            logger.error(f"Allocation failed: {e}")
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during allocation: {e}")
            raise RuntimeError(f"Database operation failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during allocation: {e}")
            raise RuntimeError(f"Allocation failed: {str(e)}")
    
    def deallocate_item_from_character(
        self,
        character_id: str,
        item_id: str,
        access_type: str,
        access_subtype: Optional[str] = None,
        quantity: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Deallocate an item from a character.
        
        Args:
            character_id: UUID of the character
            item_id: UUID of the item
            access_type: Type of access to remove
            access_subtype: Subtype of access if applicable
            quantity: Quantity to remove (None = remove all)
        
        Returns:
            Dict with success status and deallocation details
        
        Raises:
            ValueError: If allocation not found
            RuntimeError: If database operation fails
        """
        try:
            # Find the allocation
            allocation = self.db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id,
                CharacterItemAccess.item_id == item_id,
                CharacterItemAccess.access_type == access_type,
                CharacterItemAccess.access_subtype == access_subtype
            ).first()
            
            if not allocation:
                raise ValueError(f"Allocation not found for character {character_id}, item {item_id}")
            
            if quantity is None or quantity >= allocation.quantity:
                # Remove entire allocation
                self.db.delete(allocation)
                removed_quantity = allocation.quantity
                logger.info(f"Removed entire allocation: {allocation.id}")
            else:
                # Reduce quantity
                allocation.quantity -= quantity
                allocation.updated_at = None  # Will be set automatically
                removed_quantity = quantity
                logger.info(f"Reduced allocation quantity: {allocation.id}")
            
            # Commit the transaction
            self.db.commit()
            
            return {
                "success": True,
                "character_id": character_id,
                "item_id": item_id,
                "access_type": access_type,
                "removed_quantity": removed_quantity,
                "message": "Item deallocated successfully"
            }
            
        except (ValueError, RuntimeError) as e:
            self.db.rollback()
            logger.error(f"Deallocation failed: {e}")
            raise
        except SQLAlchemyError as e:
            self.db.rollback()
            logger.error(f"Database error during deallocation: {e}")
            raise RuntimeError(f"Database operation failed: {str(e)}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Unexpected error during deallocation: {e}")
            raise RuntimeError(f"Deallocation failed: {str(e)}")
    
    def get_character_allocations(
        self,
        character_id: str,
        access_type: Optional[str] = None,
        item_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get all item allocations for a character.
        
        Args:
            character_id: UUID of the character
            access_type: Filter by access type
            item_type: Filter by item type
        
        Returns:
            Dict with character allocations
        """
        try:
            # Verify character exists
            character = self.db.query(Character).filter(Character.id == character_id).first()
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Build query
            query = self.db.query(CharacterItemAccess).filter(
                CharacterItemAccess.character_id == character_id
            )
            
            if access_type:
                query = query.filter(CharacterItemAccess.access_type == access_type)
            
            allocations = query.all()
            
            # Group by access type
            grouped_allocations = {}
            for allocation in allocations:
                access_key = allocation.access_type
                if access_key not in grouped_allocations:
                    grouped_allocations[access_key] = []
                
                # Load item details
                item = self.db.query(UnifiedItem).filter(UnifiedItem.id == allocation.item_id).first()
                
                if item and (not item_type or item.item_type == item_type):
                    allocation_data = {
                        "access_id": allocation.id,
                        "item_id": allocation.item_id,
                        "item_name": item.name,
                        "item_type": item.item_type,
                        "item_subtype": item.item_subtype,
                        "quantity": allocation.quantity,
                        "access_subtype": allocation.access_subtype,
                        "acquired_method": allocation.acquired_method,
                        "acquired_at": allocation.created_at.isoformat() if allocation.created_at else None,
                        "custom_properties": allocation.custom_properties,
                        # Provenance fields
                        "source_type": item.source_type,
                        "source_info": item.source_info,
                        "llm_metadata": item.llm_metadata
                    }
                    grouped_allocations[access_key].append(allocation_data)
            
            return {
                "success": True,
                "character_id": character_id,
                "character_name": character.name,
                "allocations": grouped_allocations,
                "total_allocations": len(allocations)
            }
            
        except ValueError as e:
            logger.error(f"Failed to get allocations: {e}")
            raise
        except SQLAlchemyError as e:
            logger.error(f"Database error getting allocations: {e}")
            raise RuntimeError(f"Database operation failed: {str(e)}")
        except Exception as e:
            logger.error(f"Unexpected error getting allocations: {e}")
            raise RuntimeError(f"Failed to get allocations: {str(e)}")
    
    def _validate_allocation(
        self,
        character: Character,
        item: UnifiedItem,
        access_type: str
    ) -> CreationResult:
        """
        Validate that a character can be allocated an item.
        
        Args:
            character: Character model instance
            item: UnifiedItem model instance
            access_type: Type of access being granted
        
        Returns:
            CreationResult with validation outcome
        """
        try:
            # Convert character to validation format
            character_data = {
                "character_classes": character.character_classes or {},
                "abilities": getattr(character, 'ability_scores', {}) or getattr(character, 'abilities', {}),
                "level": character.level or 1,
                "weapon_proficiencies": getattr(character, 'weapon_proficiencies', []),
                "armor_proficiencies": getattr(character, 'armor_proficiencies', []),
                "tool_proficiencies": getattr(character, 'tool_proficiencies', {})
            }
            
            # Convert item to validation format
            item_data = {
                "name": item.name,
                "item_type": item.item_type,
                "item_subtype": item.item_subtype,
                "spell_level": item.spell_level,
                "spell_school": item.spell_school,
                "class_restrictions": item.class_restrictions or [],
                "content_data": item.content_data or {}
            }
            
            # Use the validation service
            return validate_item_allocation(character_data, item_data, access_type)
            
        except Exception as e:
            logger.error(f"Validation error: {e}")
            result = CreationResult(success=False)
            result.error = f"Validation failed: {str(e)}"
            return result
