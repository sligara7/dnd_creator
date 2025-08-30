"""Character factory service.

This service provides character creation and evolution capabilities,
including LLM-guided character generation.
"""

from typing import Dict, Optional, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from ..models.character import Character
from ..schemas.character import (
    CharacterConcept, 
    CharacterEvolution,
    CharacterPreferences,
)
from ..core.logging import get_logger
from ..core.llm import LLMClient
from ..core.messaging import MessageBroker

logger = get_logger(__name__)

class CharacterFactory:
    """Service for creating and evolving characters."""
    
    def __init__(
        self,
        session: AsyncSession,
        llm_client: LLMClient,
        message_broker: MessageBroker,
    ):
        """Initialize with required dependencies.
        
        Args:
            session: SQLAlchemy async session
            llm_client: Client for LLM interactions
            message_broker: Client for async messaging
        """
        self.db = session
        self.llm = llm_client
        self.broker = message_broker
    
    async def create_character(
        self,
        concept: CharacterConcept,
        preferences: Optional[CharacterPreferences] = None,
    ) -> Character:
        """Create a new character based on concept.
        
        Args:
            concept: Description of character concept
            preferences: Optional creation preferences
            
        Returns:
            Created character instance
            
        Raises:
            ValueError: If character creation fails
            SQLAlchemyError: If database operation fails
        """
        try:
            # Generate character from concept
            generation = await self.llm.generate_character(
                concept=concept.dict(),
                preferences=preferences.dict() if preferences else {},
            )
            
            if not generation:
                raise ValueError("Failed to generate character")
            
            # Create character model
            character = Character(**generation)
            self.db.add(character)
            await self.db.flush()
            
            # Generate portrait if enabled
            if preferences and preferences.generate_portrait:
                portrait = await self.llm.generate_portrait(
                    character=character.dict(),
                    style=preferences.portrait_style,
                )
                if portrait:
                    character.portrait_url = portrait["url"]
                    await self.db.flush()
            
            # Publish creation event
            await self.broker.publish(
                "character.created",
                {
                    "character_id": str(character.id),
                    "concept": concept.dict(),
                },
            )
            
            await self.db.commit()
            return character
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Character creation failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during creation: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during creation: {str(e)}")
            raise ValueError(f"Character creation failed: {str(e)}")
    
    async def evolve_character(
        self,
        character_id: UUID,
        evolution: CharacterEvolution,
    ) -> Character:
        """Evolve an existing character with new traits/experiences.
        
        Args:
            character_id: ID of character to evolve
            evolution: Evolution details
            
        Returns:
            Updated character instance
            
        Raises:
            ValueError: If evolution fails or character not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get current character
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Generate evolution
            evolved = await self.llm.evolve_character(
                character=character.dict(),
                evolution=evolution.dict(),
            )
            
            if not evolved:
                raise ValueError("Failed to evolve character")
            
            # Update character model
            for key, value in evolved.items():
                if hasattr(character, key):
                    setattr(character, key, value)
            
            await self.db.flush()
            
            # Publish evolution event 
            await self.broker.publish(
                "character.evolved",
                {
                    "character_id": str(character_id),
                    "evolution": evolution.dict(),
                },
            )
            
            await self.db.commit()
            return character
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Character evolution failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during evolution: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during evolution: {str(e)}")
            raise ValueError(f"Character evolution failed: {str(e)}")
            
    async def generate_portrait(
        self,
        character_id: UUID,
        style: Optional[str] = None,
    ) -> str:
        """Generate a portrait for an existing character.
        
        Args:
            character_id: Character to generate portrait for
            style: Optional style descriptor
            
        Returns:
            URL of generated portrait
            
        Raises:
            ValueError: If generation fails or character not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get current character
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Generate portrait
            portrait = await self.llm.generate_portrait(
                character=character.dict(),
                style=style,
            )
            
            if not portrait or "url" not in portrait:
                raise ValueError("Failed to generate portrait")
            
            # Update character
            character.portrait_url = portrait["url"]
            await self.db.commit()
            
            return portrait["url"]
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Portrait generation failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during portrait generation: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during portrait generation: {str(e)}")
            raise ValueError(f"Portrait generation failed: {str(e)}")
            
    async def validate_character(
        self,
        character_id: UUID,
    ) -> Dict[str, Any]:
        """Validate a character against game rules.
        
        Args:
            character_id: Character to validate
            
        Returns:
            Validation results
            
        Raises:
            ValueError: If validation fails or character not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get current character
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Perform validation
            validation = await self.llm.validate_character(
                character=character.dict(),
            )
            
            if not validation:
                raise ValueError("Failed to validate character")
            
            # Update validation status
            character.validated = validation.get("valid", False)
            character.validation_errors = validation.get("errors", [])
            await self.db.commit()
            
            return validation
            
        except ValueError as e:
            await self.db.rollback()
            logger.error(f"Character validation failed: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            await self.db.rollback()
            logger.error(f"Database error during validation: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            await self.db.rollback()
            logger.error(f"Unexpected error during validation: {str(e)}")
            raise ValueError(f"Character validation failed: {str(e)}")
            
    async def get_character_suggestions(
        self,
        character_id: UUID,
    ) -> Dict[str, Any]:
        """Get suggestions for character improvement.
        
        Args:
            character_id: Character to get suggestions for
            
        Returns:
            Dict of suggestions by category
            
        Raises:
            ValueError: If suggestion fails or character not found
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get current character
            stmt = select(Character).where(Character.id == character_id)
            result = await self.db.execute(stmt)
            character = result.scalar_one_or_none()
            
            if not character:
                raise ValueError(f"Character not found: {character_id}")
            
            # Get suggestions
            suggestions = await self.llm.get_character_suggestions(
                character=character.dict(),
            )
            
            if not suggestions:
                raise ValueError("Failed to get suggestions")
            
            return suggestions
            
        except ValueError as e:
            logger.error(f"Failed to get suggestions: {str(e)}")
            raise
            
        except SQLAlchemyError as e:
            logger.error(f"Database error getting suggestions: {str(e)}")
            raise ValueError(f"Database operation failed: {str(e)}")
            
        except Exception as e:
            logger.error(f"Unexpected error getting suggestions: {str(e)}")
            raise ValueError(f"Failed to get suggestions: {str(e)}")
