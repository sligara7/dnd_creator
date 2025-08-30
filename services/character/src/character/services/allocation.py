"""Allocation service for managing character item allocations.

This service handles allocation and management of items, spells,
and other resources to characters, with validation and transaction
safety.
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.base import Status
from ..models.character import Character, Equipment, Weapon, Armor
from ..models.spellcasting import Spell
from ..schemas.allocation import (
    AllocationResult,
    AllocationRequest,
    DeallocationRequest,
)
from ..core.logging import get_logger

logger = get_logger(__name__)

class AllocationService:
    """Service for managing character-item allocations with validation."""
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session.
        
        Args:
            session: SQLAlchemy async session
        """
        self.db = session
    
    async def allocate_item(
        self,
        request: AllocationRequest,
        character_id: UUID,
    ) -> AllocationResult:
        """Allocate an item to a character with validation.
        
        Args:
            request: Allocation request details
            character_id: ID of character to receive allocation
            
        Returns:
            Result of allocation attempt
            
        Raises:
            ValueError: If validation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Load character in same session
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Load item
            item_model = self._get_model_for_type(request.type)
            if not item_model:
                raise ValueError(f"Unknown item type: {request.type}")
                
            stmt = select(item_model).where(item_model.id == request.item_id)
            result = await self.db.execute(stmt)
            item = result.scalar_one_or_none()
            
            if not item:
                raise ValueError(f"Item not found: {request.item_id}")
            
            # Validate allocation
            if not request.skip_validation:
                result = await self._validate_allocation(character, item, request)
                if not result.is_valid:
                    raise ValueError(f"Allocation validation failed: {result.errors}")
            
            # Check if allocation already exists
            existing = await self._get_existing_allocation(character, item, request)
            
            if existing:
                # Update existing allocation
                existing.quantity += request.quantity
                existing.updated_at = datetime.utcnow()
                allocation_id = existing.id
                logger.info(f"Updated existing allocation: {allocation_id}")
            else:
                # Create new allocation based on type
                allocation = await self._create_allocation(character, item, request)
                await self.db.flush()
                allocation_id = allocation.id
                logger.info(f"Created new allocation: {allocation_id}")
            
            # Commit transaction
            await self.db.commit()
            
            return AllocationResult(
                success=True,
                allocation_id=allocation_id,
                character_id=character_id,
                item_id=request.item_id,
                type=request.type,
                quantity=request.quantity,
                message="Item allocated successfully",
            )
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Allocation failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during allocation: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during allocation: {str(e)}")
            raise ValueError(f"Allocation failed: {str(e)}")
    
    async def deallocate_item(
        self,
        request: DeallocationRequest,
        character_id: UUID,
    ) -> AllocationResult:
        """Remove an item allocation from a character.
        
        Args:
            request: Deallocation request details 
            character_id: Character to remove allocation from
            
        Returns:
            Result of deallocation attempt
            
        Raises:
            ValueError: If allocation not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Find allocation
            allocation = await self._get_allocation(
                character_id, 
                request.item_id,
                request.type
            )
            
            if not allocation:
                raise ValueError(
                    f"Allocation not found for character {character_id}, "
                    f"item {request.item_id}"
                )
            
            if request.quantity is None or request.quantity >= allocation.quantity:
                # Remove entire allocation
                await self.db.delete(allocation)
                removed_quantity = allocation.quantity
                logger.info(f"Removed entire allocation: {allocation.id}")
            else:
                # Reduce quantity
                allocation.quantity -= request.quantity
                allocation.updated_at = datetime.utcnow()
                removed_quantity = request.quantity
                logger.info(f"Reduced allocation quantity: {allocation.id}")
            
            # Commit transaction
            await self.db.commit()
            
            return AllocationResult(
                success=True,
                character_id=character_id,
                item_id=request.item_id,
                type=request.type,
                quantity=removed_quantity,
                message="Item deallocated successfully",
            )
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Deallocation failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during deallocation: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during deallocation: {str(e)}")
            raise ValueError(f"Deallocation failed: {str(e)}")
    
    async def get_character_allocations(
        self,
        character_id: UUID,
        type: Optional[str] = None,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Get all allocations for a character.
        
        Args:
            character_id: Character to get allocations for
            type: Optional filter by allocation type
            
        Returns:
            Dict mapping allocation types to lists of allocations
            
        Raises:
            ValueError: If character not found
            SQLAlchemyError: If database query fails
        """
        try:
            # Verify character exists
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Build base queries
            allocations = {}
            
            # Get equipment allocations
            if not type or type == "equipment":
                stmt = select(Equipment).where(Equipment.character_id == character_id)
                result = await self.db.execute(stmt)
                allocations["equipment"] = []
                for row in result.scalars():
                    allocations["equipment"].append({
                        "id": row.id,
                        "name": row.name,
                        "type": "equipment",
                        "quantity": row.quantity,
                        "equipped": row.equipped,
                        "attuned": row.attuned,
                        "properties": row.properties,
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    })
                    
            # Get weapon allocations
            if not type or type == "weapon":
                stmt = select(Weapon).where(Weapon.character_id == character_id)
                result = await self.db.execute(stmt)
                allocations["weapons"] = []
                for row in result.scalars():
                    allocations["weapons"].append({
                        "id": row.id,
                        "name": row.name,
                        "type": "weapon",
                        "weapon_type": row.weapon_type,
                        "damage": row.damage_dice,
                        "damage_type": row.damage_type,
                        "properties": row.properties,
                        "quantity": row.quantity,
                        "equipped": row.equipped,
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    })
                    
            # Get armor allocations
            if not type or type == "armor":
                stmt = select(Armor).where(Armor.character_id == character_id)
                result = await self.db.execute(stmt)
                allocations["armor"] = []
                for row in result.scalars():
                    allocations["armor"].append({
                        "id": row.id,
                        "name": row.name,
                        "type": "armor",
                        "armor_type": row.armor_type,
                        "ac": row.base_ac,
                        "properties": row.properties,
                        "equipped": row.equipped,
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    })
                    
            # Get spell allocations
            if not type or type == "spell":
                stmt = select(Spell).where(Spell.id.in_(
                    select(Equipment.id)
                    .where(Equipment.character_id == character_id)
                    .where(Equipment.type == "spell")
                ))
                result = await self.db.execute(stmt)
                allocations["spells"] = []
                for row in result.scalars():
                    allocations["spells"].append({
                        "id": row.id,
                        "name": row.name,
                        "type": "spell",
                        "level": row.level,
                        "school": row.school,
                        "prepared": row.prepared if hasattr(row, "prepared") else False,
                        "created_at": row.created_at,
                        "updated_at": row.updated_at,
                    })
            
            return allocations
            
        except ValueError as e:
            logger.error(f"Failed to get allocations: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting allocations: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error getting allocations: {str(e)}")
            raise ValueError(f"Failed to get allocations: {str(e)}")
    
    async def _validate_allocation(
        self,
        character: Character,
        item: Any,
        request: AllocationRequest,
    ) -> bool:
        """Validate a potential allocation.
        
        Args:
            character: Character to receive allocation
            item: Item to allocate
            request: Allocation request details
            
        Returns:
            True if allocation is valid
        """
        # Base validation
        if request.quantity < 1:
            return False
            
        # Type-specific validation
        if isinstance(item, Equipment):
            return await self._validate_equipment(character, item, request)
        elif isinstance(item, Weapon):
            return await self._validate_weapon(character, item, request)
        elif isinstance(item, Armor):
            return await self._validate_armor(character, item, request)
        elif isinstance(item, Spell):
            return await self._validate_spell(character, item, request)
        
        return False
    
    async def _validate_equipment(
        self,
        character: Character,
        item: Equipment,
        request: AllocationRequest,
    ) -> bool:
        """Validate equipment allocation."""
        # Basic equipment has minimal restrictions
        return True
        
    async def _validate_weapon(
        self,
        character: Character,
        item: Weapon,
        request: AllocationRequest,
    ) -> bool:
        """Validate weapon allocation."""
        # Check proficiency
        if item.weapon_type not in character.weapon_proficiencies:
            return False
            
        return True
        
    async def _validate_armor(
        self,
        character: Character,
        item: Armor,
        request: AllocationRequest,
    ) -> bool:
        """Validate armor allocation."""
        # Check proficiency
        if item.armor_type not in character.armor_proficiencies:
            return False
            
        # Check strength requirement
        if (
            item.strength_requirement and
            character.abilities["strength"].score < item.strength_requirement
        ):
            return False
            
        return True
        
    async def _validate_spell(
        self,
        character: Character,
        item: Spell,
        request: AllocationRequest,
    ) -> bool:
        """Validate spell allocation."""
        # Must have spellcasting ability
        if not character.spellcasting_ability:
            return False
            
        # Check spell level against max castable
        max_level = self._get_max_spell_level(character)
        if item.level > max_level:
            return False
            
        return True
    
    def _get_model_for_type(self, type: str) -> Optional[Any]:
        """Get the model class for an allocation type."""
        models = {
            "equipment": Equipment,
            "weapon": Weapon,
            "armor": Armor,
            "spell": Spell,
        }
        return models.get(type)
    
    async def _get_existing_allocation(
        self,
        character: Character,
        item: Any,
        request: AllocationRequest,
    ) -> Optional[Any]:
        """Find existing allocation if any."""
        model = self._get_model_for_type(request.type)
        if not model:
            return None
            
        stmt = (
            select(model)
            .where(model.character_id == character.id)
            .where(model.id == item.id)
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()
    
    async def _create_allocation(
        self,
        character: Character,
        item: Any,
        request: AllocationRequest,
    ) -> Any:
        """Create new allocation based on type."""
        if isinstance(item, Equipment):
            allocation = Equipment(
                character_id=character.id,
                name=item.name,
                type=item.type,
                quantity=request.quantity,
                properties=item.properties,
            )
        elif isinstance(item, Weapon):
            allocation = Weapon(
                character_id=character.id,
                name=item.name,
                weapon_type=item.weapon_type,
                damage_dice=item.damage_dice,
                damage_type=item.damage_type,
                properties=item.properties,
                quantity=request.quantity,
            )
        elif isinstance(item, Armor):
            allocation = Armor(
                character_id=character.id,
                name=item.name,
                armor_type=item.armor_type,
                base_ac=item.base_ac,
                properties=item.properties,
            )
        elif isinstance(item, Spell):
            allocation = Equipment(
                character_id=character.id,
                name=item.name,
                type="spell",
                quantity=1,
                properties={
                    "level": item.level,
                    "school": item.school,
                },
            )
        else:
            raise ValueError(f"Cannot create allocation for type: {type(item)}")
            
        self.db.add(allocation)
        return allocation
    
    def _get_max_spell_level(self, character: Character) -> int:
        """Calculate max spell level for character."""
        if not character.spellcasting_ability:
            return 0
            
        # Simple calculation based on total level
        # In practice would be more complex based on class
        return min(9, (character.total_level + 1) // 2)
