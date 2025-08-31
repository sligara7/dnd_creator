"""Character repository module."""

from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from character_service.models.models import Character
from character_service.schemas.schemas import CharacterCreate, CharacterUpdate

class CharacterRepository:
    """Character repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Character]:
        """Get all characters with pagination."""
        query = select(Character).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get(self, character_id: int) -> Optional[Character]:
        """Get a character by ID"""
        query = select(Character).where(Character.id == character_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, character: CharacterCreate) -> Character:
        """Create a new character"""
        payload = character.dict()
        db_character = Character(**payload)
        self.db.add(db_character)
        await self.db.flush()
        await self.db.refresh(db_character)
        return db_character

    async def update(self, character_id: int, character: CharacterUpdate) -> Optional[Character]:
        """Update a character"""
        db_character = await self.get(character_id)
        if not db_character:
            return None
        
        for key, value in character.dict(exclude_unset=True).items():
            setattr(db_character, key, value)
        
        await self.db.flush()
        await self.db.refresh(db_character)
        return db_character

    async def delete(self, character_id: int) -> bool:
        """Delete a character"""
        db_character = await self.get(character_id)
        if not db_character:
            return False
        
        await self.db.delete(db_character)
        await self.db.flush()
        return True

    async def update_evolution(self, character_id: int, evolution_data: dict) -> Optional[Character]:
        """Update a character's evolution data"""
        db_character = await self.get(character_id)
        if not db_character:
            return None
        
        # Merge evolution data with existing character data
        current = dict(db_character.data or {})
        current.update(evolution_data)
        db_character.data = current
        
        await self.db.flush()
        await self.db.refresh(db_character)
        return db_character
