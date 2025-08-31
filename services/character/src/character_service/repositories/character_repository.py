"""Character Repository Implementation"""

from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.future import select

from character_service.models.models import Character
from character_service.schemas.schemas import CharacterCreate, CharacterUpdate

class CharacterRepository:
    """Repository for Character-related operations"""
    
    def __init__(self, db: Session):
        self.db = db

    async def create(self, character: CharacterCreate) -> Character:
        """Create a new character"""
        db_character = Character(
            name=character.name,
            user_id=character.user_id,
            campaign_id=character.campaign_id,
            character_data=character.character_data,
        )
        self.db.add(db_character)
        await self.db.commit()
        await self.db.refresh(db_character)
        return db_character

    async def get(self, character_id: int) -> Optional[Character]:
        """Get a character by ID"""
        query = select(Character).where(Character.id == character_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_by_user(self, user_id: str) -> List[Character]:
        """Get all characters for a user"""
        query = select(Character).where(Character.user_id == user_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_by_campaign(self, campaign_id: str) -> List[Character]:
        """Get all characters in a campaign"""
        query = select(Character).where(Character.campaign_id == campaign_id)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def update(self, character_id: int, character_update: CharacterUpdate) -> Optional[Character]:
        """Update a character"""
        query = select(Character).where(Character.id == character_id)
        result = await self.db.execute(query)
        db_character = result.scalar_one_or_none()
        
        if db_character:
            for field, value in character_update.model_dump().items():
                setattr(db_character, field, value)
            await self.db.commit()
            await self.db.refresh(db_character)
            
        return db_character

    async def delete(self, character_id: int) -> bool:
        """Delete a character"""
        query = select(Character).where(Character.id == character_id)
        result = await self.db.execute(query)
        db_character = result.scalar_one_or_none()
        
        if db_character:
            await self.db.delete(db_character)
            await self.db.commit()
            return True
            
        return False
