"""
Character generation factory.
"""

from typing import Dict, Any, Optional
from uuid import UUID

from ..models.character import Character
from ..core.logging import get_logger

logger = get_logger(__name__)


class CharacterFactory:
    """Factory for creating and evolving characters."""
    
    def __init__(self, message_hub_client):
        """Initialize with required dependencies."""
        self.message_hub = message_hub_client
    
    async def create_character(
        self,
        concept: str,
        preferences: Optional[Dict[str, Any]] = None
    ) -> Character:
        """Create a new character based on concept."""
        try:
            # Get character generation from LLM
            generation = await self.message_hub.request(
                "llm.generate_character",
                {
                    "concept": concept,
                    "preferences": preferences or {}
                }
            )
            
            if not generation:
                raise ValueError("Failed to generate character")
                
            # Create character model
            character = Character(**generation)
            
            # Generate portrait if enabled
            if preferences and preferences.get("generate_portrait"):
                portrait = await self.message_hub.request(
                    "image.generate_portrait",
                    {
                        "character": character.dict(),
                        "style": preferences.get("portrait_style")
                    }
                )
                if portrait:
                    character.portrait_url = portrait["url"]
            
            # Add to catalog
            await self.message_hub.request(
                "catalog.add_character",
                {"character": character.dict()}
            )
            
            # Publish creation event
            await self.message_hub.publish(
                "character.created",
                {"character_id": str(character.id)}
            )
            
            return character
            
        except Exception as e:
            logger.error("Character creation failed", error=str(e))
            raise ValueError(f"Failed to create character: {e}")
            
    async def evolve_character(
        self,
        character_id: UUID,
        changes: Dict[str, Any]
    ) -> Character:
        """Evolve an existing character."""
        try:
            # Get current character
            character_data = await self.message_hub.request(
                "character.get",
                {"character_id": str(character_id)}
            )
            
            if not character_data:
                raise ValueError("Character not found")
                
            # Get evolution from LLM
            evolution = await self.message_hub.request(
                "llm.evolve_character",
                {
                    "character": character_data,
                    "changes": changes
                }
            )
            
            if not evolution:
                raise ValueError("Failed to evolve character")
                
            # Update character model
            character = Character(**evolution)
            
            # Update catalog
            await self.message_hub.request(
                "catalog.update_character",
                {
                    "character_id": str(character_id),
                    "character": character.dict()
                }
            )
            
            # Publish evolution event
            await self.message_hub.publish(
                "character.evolved",
                {
                    "character_id": str(character_id),
                    "changes": list(changes.keys())
                }
            )
            
            return character
            
        except Exception as e:
            logger.error("Character evolution failed", error=str(e))
            raise ValueError(f"Failed to evolve character: {e}")
