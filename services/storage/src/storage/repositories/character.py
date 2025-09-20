from typing import Dict, List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ..models.character import Character, CharacterVersion, CharacterProgress

class CharacterRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_character(self, character_id: UUID) -> Optional[Character]:
        query = select(Character).where(
            Character.id == character_id,
            Character.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create_character(self, character_data: Dict) -> Character:
        character = Character(**character_data)
        self.db.add(character)
        await self.db.commit()
        return character

    async def update_character(self, character_id: UUID, character_data: Dict) -> Optional[Character]:
        query = update(Character).where(
            Character.id == character_id,
            Character.is_deleted == False
        ).values(**character_data)
        result = await self.db.execute(query)
        if result.rowcount > 0:
            await self.db.commit()
            return await self.get_character(character_id)
        return None

    async def delete_character(self, character_id: UUID) -> bool:
        query = update(Character).where(
            Character.id == character_id,
            Character.is_deleted == False
        ).values(
            is_deleted=True
        )
        result = await self.db.execute(query)
        if result.rowcount > 0:
            await self.db.commit()
            return True
        return False

    async def list_characters(self, limit: int = 100, offset: int = 0) -> List[Character]:
        query = select(Character).where(
            Character.is_deleted == False
        ).limit(limit).offset(offset)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def get_character_versions(self, character_id: UUID) -> List[CharacterVersion]:
        query = select(CharacterVersion).where(
            CharacterVersion.character_id == character_id,
            CharacterVersion.is_deleted == False
        ).order_by(CharacterVersion.version_number)
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_character_version(self, version_data: Dict) -> CharacterVersion:
        version = CharacterVersion(**version_data)
        self.db.add(version)
        await self.db.commit()
        return version

    async def get_character_progress(self, character_id: UUID) -> List[CharacterProgress]:
        query = select(CharacterProgress).where(
            CharacterProgress.character_id == character_id,
            CharacterProgress.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalars().all()

    async def create_progress_entry(self, progress_data: Dict) -> CharacterProgress:
        progress = CharacterProgress(**progress_data)
        self.db.add(progress)
        await self.db.commit()
        return progress

    async def update_progress_entry(self, progress_id: UUID, progress_data: Dict) -> Optional[CharacterProgress]:
        query = update(CharacterProgress).where(
            CharacterProgress.id == progress_id,
            CharacterProgress.is_deleted == False
        ).values(**progress_data)
        result = await self.db.execute(query)
        if result.rowcount > 0:
            await self.db.commit()
            return await self.get_progress_entry(progress_id)
        return None

    async def get_progress_entry(self, progress_id: UUID) -> Optional[CharacterProgress]:
        query = select(CharacterProgress).where(
            CharacterProgress.id == progress_id,
            CharacterProgress.is_deleted == False
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()