"""FastAPI application for character service."""
from typing import List, Optional
from uuid import UUID

from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel, ConfigDict, constr

from character_service.models.character import Character
from character_service.repositories.character import CharacterRepository
from character_service.services.character import (
    AbilityScores,
    CharacterCreationError,
    CharacterService,
    CharacterValidationError
)


class CharacterCreate(BaseModel):
    """Request model for character creation."""
    name: constr(min_length=1, max_length=100)
    ability_scores: AbilityScores
    race: constr(min_length=1, max_length=50)
    character_class: constr(min_length=1, max_length=50)
    background: constr(min_length=1, max_length=100)
    level: Optional[int] = 1


class CharacterRead(BaseModel):
    """Response model for character data."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    level: int
    strength: int
    dexterity: int
    constitution: int
    intelligence: int
    wisdom: int
    charisma: int
    max_hit_points: int
    current_hit_points: int
    temporary_hit_points: int
    race: str
    character_class: str
    background: str
    classes: Optional[List[dict]] = None


class CharacterUpdate(BaseModel):
    """Request model for character updates."""
    name: Optional[constr(min_length=1, max_length=100)] = None
    current_hit_points: Optional[int] = None
    temporary_hit_points: Optional[int] = None


def create_app(repository: Optional[CharacterRepository] = None) -> FastAPI:
    """Create FastAPI application.
    
    Args:
        repository: Optional repository for testing
        
    Returns:
        FastAPI application
    """
    app = FastAPI(title="Character Service")
    
    async def get_repository() -> CharacterRepository:
        """Get repository instance.
        
        Returns:
            Repository instance
        """
        return repository if repository is not None else CharacterRepository()
    
    async def get_service(repo: CharacterRepository = Depends(get_repository)) -> CharacterService:
        """Get service instance.
        
        Args:
            repo: Repository instance
            
        Returns:
            Service instance
        """
        return CharacterService(repo)

    @app.post("/characters", response_model=CharacterRead, status_code=status.HTTP_201_CREATED)
    async def create_character(
        data: CharacterCreate,
        service: CharacterService = Depends(get_service)
    ) -> Character:
        """Create a new character."""
        try:
            return await service.create_character(
                name=data.name,
                ability_scores=data.ability_scores,
                race=data.race,
                character_class=data.character_class,
                background=data.background,
                level=data.level
            )
        except CharacterCreationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )
        except CharacterValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

    @app.get("/characters/{character_id}", response_model=CharacterRead)
    async def get_character(
        character_id: UUID,
        service: CharacterService = Depends(get_service)
    ) -> Character:
        """Get a character by ID."""
        character = await service.repository.get(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        return character

    @app.get("/characters", response_model=List[CharacterRead])
    async def list_characters(
        service: CharacterService = Depends(get_service)
    ) -> List[Character]:
        """List all characters."""
        return await service.repository.get_all()

    @app.patch("/characters/{character_id}", response_model=CharacterRead)
    async def update_character(
        character_id: UUID,
        data: CharacterUpdate,
        service: CharacterService = Depends(get_service)
    ) -> Character:
        """Update a character."""
        character = await service.repository.get(character_id)
        if not character:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Character not found"
            )
        
        # Begin a savepoint to isolate this update
        tx = await service.repository.db.begin_nested()
        try:
            # Update allowed fields
            if data.name is not None:
                character.name = data.name
            if data.current_hit_points is not None:
                character.current_hit_points = data.current_hit_points
            if data.temporary_hit_points is not None:
                character.temporary_hit_points = data.temporary_hit_points

            # Validate updated character
            service.validate_character_state(character)
            updated = await service.repository.update(character)
            await tx.commit()
            return updated
        except CharacterValidationError as e:
            await tx.rollback()
            # Refresh entity to DB state to discard in-memory changes
            try:
                await service.repository.db.refresh(character)
            except Exception:
                pass
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

    return app
