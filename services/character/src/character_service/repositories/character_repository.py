"""Character repository module."""

from datetime import datetime
from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from character_service.models.models import Character
from character_service.schemas.schemas import CharacterCreate, CharacterUpdate

class CharacterRepository:
    """Character repository."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(self, limit: int = 100, offset: int = 0) -> List[Character]:
        """Get all active characters with pagination."""
        query = select(Character).where(Character.is_active == True).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return [row[0] for row in result.all()]

    async def get(self, character_id: UUID) -> Optional[Character]:
        """Get an active character by ID"""
        query = select(Character).where(
            Character.id == character_id,
            Character.is_active == True
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _get_safe_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Get only the fields that are valid for the Character model."""
        valid_fields = {
            "name",
            "user_id",
            "campaign_id",
            "character_data",
            "is_active",
            "user_modified",
            "audit_trail"
        }
        return {k: v for k, v in data.items() if k in valid_fields}

    async def create(self, character: CharacterCreate) -> Character:
        """Create a new character"""
        # Get validated data
        payload = character.model_dump()
        
        # Filter to just the valid fields
        payload = self._get_safe_fields(payload)
        
        # Ensure an ID is generated
        db_character = Character(id=uuid4(), **payload)
        self.db.add(db_character)
        await self.db.flush()
        await self.db.refresh(db_character)
        return db_character

    async def update(self, character_id: UUID, character: CharacterUpdate) -> Optional[Character]:
        """Update a character"""
        db_character = await self.get(character_id)
        if not db_character:
            return None
        
        # Get updates and filter to valid fields
        updates = character.model_dump(exclude_unset=True)
        updates = self._get_safe_fields(updates)

        # Apply filtered updates
        for key, value in updates.items():
            setattr(db_character, key, value)
        
        await self.db.flush()
        await self.db.refresh(db_character)
        return db_character

    async def delete(self, character_id: UUID) -> bool:
        """Soft delete a character by marking it as inactive"""
        query = update(Character).where(
            Character.id == character_id,
            Character.is_active == True
        ).values(
            is_active=False,
            updated_at=datetime.utcnow()
        )
        result = await self.db.execute(query)
        await self.db.flush()
        return result.rowcount > 0

    async def update_evolution(self, character_id: UUID, evolution_data: dict) -> Optional[Character]:
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
