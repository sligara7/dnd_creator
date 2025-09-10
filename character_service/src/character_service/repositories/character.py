"""Character repository."""
from datetime import UTC, datetime
from enum import Enum
from typing import Optional, List, Dict, Any, Tuple, Union, Sequence
from uuid import UUID

from sqlalchemy import select, update, and_, desc, asc, delete

from sqlalchemy import select, update, and_, desc, asc
from sqlalchemy.ext.asyncio import AsyncSession

from character_service.models.character import Character


class SortOrder(Enum):
    """Enumeration for sort order."""
    ASC = "asc"
    DESC = "desc"

class CharacterRepository:
    """Repository for character operations."""
    
    def __init__(self, session: AsyncSession):
        """Initialize the repository.
        
        Args:
            session: The database session
        """
        self.db = session

    async def create(self, character: Character) -> Character:
        """Create a new character.
        
        Args:
            character: The character to create
            
        Returns:
            The created character
        """
        self.db.add(character)
        await self.db.flush()
        return character

    async def get(self, character_id: UUID) -> Optional[Character]:
        """Get a character by ID.
        
        Args:
            character_id: The character ID
            
        Returns:
            The character if found, None otherwise
        """
        query = select(Character).where(
            Character.id == character_id,
            Character.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_all(self) -> List[Character]:
        """Get all non-deleted characters.
        
        Returns:
            List of characters
        """
        query = select(Character).where(Character.is_deleted == False)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def filter_by_level(self, min_level: int, max_level: Optional[int] = None) -> List[Character]:
        """Filter characters by level range.
        
        Args:
            min_level: Minimum level (inclusive)
            max_level: Maximum level (inclusive), if None, only min_level is used
            
        Returns:
            List of filtered characters
        """
        conditions = [Character.is_deleted == False, Character.level >= min_level]
        if max_level is not None:
            conditions.append(Character.level <= max_level)
        
        query = select(Character).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def filter_by_class(self, character_class: str) -> List[Character]:
        """Filter characters by character class.
        
        Args:
            character_class: The character class to filter by
            
        Returns:
            List of filtered characters
        """
        query = select(Character).where(
            and_(
                Character.is_deleted == False,
                Character.character_class == character_class
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def filter_by_race(self, race: str) -> List[Character]:
        """Filter characters by race.
        
        Args:
            race: The race to filter by
            
        Returns:
            List of filtered characters
        """
        query = select(Character).where(
            and_(
                Character.is_deleted == False,
                Character.race == race
            )
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def filter_by_criteria(self, criteria: Dict[str, Any]) -> List[Character]:
        """Filter characters by multiple criteria.
        
        Args:
            criteria: Dictionary of field names and values to filter by
            
        Returns:
            List of filtered characters
        """
        conditions = [Character.is_deleted == False]
        
        for field, value in criteria.items():
            if hasattr(Character, field):
                conditions.append(getattr(Character, field) == value)
        
        query = select(Character).where(and_(*conditions))
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    async def get_sorted(self, sort_by: Union[str, List[Tuple[str, SortOrder]]], 
                        order: Optional[SortOrder] = SortOrder.ASC) -> List[Character]:
        """Get all non-deleted characters sorted by specified criteria.
        
        Args:
            sort_by: Field name(s) to sort by. Can be a string for single field or
                    list of (field, order) tuples for multiple fields
            order: Sort order for single field sort (ignored for multiple fields)
            
        Returns:
            List of sorted characters
        """
        query = select(Character).where(Character.is_deleted == False)
        
        if isinstance(sort_by, str):
            # Single field sort
            if not hasattr(Character, sort_by):
                raise ValueError(f"Invalid sort field: {sort_by}")
            sort_field = getattr(Character, sort_by)
            query = query.order_by(desc(sort_field) if order == SortOrder.DESC else asc(sort_field))
        else:
            # Multiple field sort
            order_clauses = []
            for field_name, field_order in sort_by:
                if not hasattr(Character, field_name):
                    raise ValueError(f"Invalid sort field: {field_name}")
                sort_field = getattr(Character, field_name)
                order_clauses.append(desc(sort_field) if field_order == SortOrder.DESC else asc(sort_field))
            query = query.order_by(*order_clauses)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def batch_create(self, characters: List[Character]) -> List[Character]:
        """Create multiple characters in a single operation.
        
        Args:
            characters: List of characters to create
            
        Returns:
            List of created characters
        
        Raises:
            ValueError: If characters list is empty
        """
        if not characters:
            raise ValueError("Cannot create empty list of characters")
        
        self.db.add_all(characters)
        await self.db.flush()
        return characters
    
    async def batch_update(self, characters: List[Character]) -> List[Character]:
        """Update multiple characters in a single operation.
        
        Args:
            characters: List of characters to update
            
        Returns:
            List of updated characters
            
        Raises:
            ValueError: If characters list is empty
        """
        if not characters:
            raise ValueError("Cannot update empty list of characters")
        
        for character in characters:
            await self.db.merge(character)
        await self.db.flush()
        return characters
    
    async def batch_delete(self, character_ids: List[UUID]) -> int:
        """Soft delete multiple characters in a single operation.
        
        Args:
            character_ids: List of character IDs to delete
            
        Returns:
            Number of characters deleted
            
        Raises:
            ValueError: If character_ids list is empty
        """
        if not character_ids:
            raise ValueError("Cannot delete empty list of characters")
        
        # Soft delete all specified characters
        query = update(Character).where(
            and_(
                Character.id.in_(character_ids),
                Character.is_deleted == False
            )
        ).values(
            is_deleted=True,
            deleted_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        
        result = await self.db.execute(query)
        return result.rowcount

    async def update(self, character: Character) -> Character:
        """Update a character.
        
        Args:
            character: The character to update
            
        Returns:
            The updated character
        """
        await self.db.merge(character)
        await self.db.flush()
        return character

    async def delete(self, character_id: UUID) -> bool:
        """Soft delete a character.
        
        Args:
            character_id: The character ID
            
        Returns:
            True if deleted, False if not found
        """
        query = update(Character).where(
            Character.id == character_id,
            Character.is_deleted == False
        ).values(
            is_deleted=True,
            deleted_at=datetime.now(UTC),
            updated_at=datetime.now(UTC)
        )
        result = await self.db.execute(query)
        return result.rowcount > 0
