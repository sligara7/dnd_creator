"""Message handlers for character and image service integration."""
from typing import Dict, Any, List

from .client import MessageHub
from ..logging import get_logger
from ...models.maps import MapLocation, LocationMap, EncounterMap

logger = get_logger(__name__)


class CharacterServiceHandler:
    """Handlers for character service messages."""

    def __init__(self, message_hub: MessageHub):
        self.message_hub = message_hub

    async def replane_character(
        self,
        character_id: str,
        source_plane: Dict[str, Any],
        target_plane: Dict[str, Any],
        transition_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Request character re-planing from character service."""
        try:
            response = await self.message_hub.request(
                "character.replane",
                {
                    "character_id": character_id,
                    "source_plane": source_plane,
                    "target_plane": target_plane,
                    "transition_rules": transition_rules
                }
            )

            if not response or "replaned_character" not in response:
                raise ValueError("Failed to replane character")

            return response["replaned_character"]

        except Exception as e:
            logger.error("Character replane failed", error=str(e))
            raise

    async def generate_characters(
        self,
        requirements: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Generate characters based on requirements."""
        try:
            response = await self.message_hub.request(
                "character.batch_generate",
                {
                    "requirements": requirements,
                    "context": context
                }
            )

            if not response or "characters" not in response:
                raise ValueError("Failed to generate characters")

            return response["characters"]

        except Exception as e:
            logger.error("Character generation failed", error=str(e))
            raise

    async def validate_references(
        self,
        references: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """Validate character references."""
        try:
            response = await self.message_hub.request(
                "character.validate_refs",
                {
                    "references": references
                }
            )

            if not response or "characters" not in response:
                raise ValueError("Failed to validate character references")

            return response

        except Exception as e:
            logger.error("Character reference validation failed", error=str(e))
            raise

    async def apply_feedback(
        self,
        character_id: str,
        feedback: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply feedback to a character."""
        try:
            response = await self.message_hub.request(
                "character.apply_feedback",
                {
                    "character_id": character_id,
                    "feedback": feedback
                }
            )

            if not response:
                raise ValueError("Failed to apply character feedback")

            return response

        except Exception as e:
            logger.error("Character feedback application failed", error=str(e))
            raise


class ImageServiceHandler:
    """Handlers for image service messages."""

    def __init__(self, message_hub: MessageHub):
        self.message_hub = message_hub

    async def generate_plane_map(
        self,
        prompt: str,
        plane_data: Dict[str, Any],
        style_params: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a plane-specific map."""
        try:
            response = await self.message_hub.request(
                "image.generate_plane_map",
                {
                    "prompt": prompt,
                    "plane_data": plane_data,
                    "style_params": style_params,
                    "metadata": metadata
                }
            )

            if not response or "image_id" not in response:
                raise ValueError("Failed to generate plane map")

            return response

        except Exception as e:
            logger.error("Plane map generation failed", error=str(e))
            raise

    async def generate_map(
        self,
        prompt: str,
        style_params: Dict[str, Any],
        metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate a map image."""
        try:
            response = await self.message_hub.request(
                "image.generate_map",
                {
                    "prompt": prompt,
                    "style_params": style_params,
                    "metadata": metadata
                }
            )

            if not response or "image_id" not in response:
                raise ValueError("Failed to generate map")

            return response

        except Exception as e:
            logger.error("Map generation failed", error=str(e))
            raise

    async def get_map_by_id(self, image_id: str) -> Dict[str, Any]:
        """Retrieve a map by its image ID."""
        try:
            response = await self.message_hub.request(
                "image.get_map",
                {
                    "image_id": image_id
                }
            )

            if not response:
                raise ValueError("Failed to retrieve map")

            return response

        except Exception as e:
            logger.error("Map retrieval failed", error=str(e))
            raise

    async def add_encounter_overlay(
        self,
        image_id: str,
        overlay_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Add an encounter overlay to a map."""
        try:
            response = await self.message_hub.request(
                "image.add_overlay",
                {
                    "image_id": image_id,
                    "overlay_data": overlay_data
                }
            )

            if not response or "overlay_id" not in response:
                raise ValueError("Failed to add overlay")

            return response

        except Exception as e:
            logger.error("Overlay addition failed", error=str(e))
            raise


class MessageHandlers:
    """Message handler registration."""

    def __init__(self, message_hub: MessageHub):
        """Initialize handlers."""
        self.character = CharacterServiceHandler(message_hub)
        self.image = ImageServiceHandler(message_hub)


# Event handlers
async def handle_character_created(event: Dict[str, Any]):
    """Handle character.created events."""
    logger.info(
        "Character created",
        character_id=event.get("character_id"),
        type=event.get("type")
    )


async def handle_character_updated(event: Dict[str, Any]):
    """Handle character.updated events."""
    logger.info(
        "Character updated",
        character_id=event.get("character_id"),
        update_type=event.get("update_type")
    )


async def handle_map_generated(event: Dict[str, Any]):
    """Handle image.map_generated events."""
    logger.info(
        "Map generated",
        image_id=event.get("image_id"),
        location_id=event.get("metadata", {}).get("location_id")
    )


async def handle_map_updated(event: Dict[str, Any]):
    """Handle image.map_updated events."""
    logger.info(
        "Map updated",
        image_id=event.get("image_id"),
        update_type=event.get("update_type")
    )


async def handle_character_replaned(event: Dict[str, Any]):
    """Handle character.replaned events."""
    logger.info(
        "Character replaned",
        character_id=event.get("character_id"),
        source_plane=event.get("source_plane"),
        target_plane=event.get("target_plane")
    )


async def handle_plane_transition_completed(event: Dict[str, Any]):
    """Handle campaign.plane_transition_completed events."""
    logger.info(
        "Plane transition completed",
        transition_id=event.get("transition_id"),
        affected_entities=event.get("affected_entities")
    )


# Event subscriptions mapping
# Plane generation handlers
async def handle_plane_generated(event: Dict[str, Any]):
    """Handle planes.generated events."""
    logger.info(
        "New plane generated",
        plane_id=event.get("plane_id"),
        concept=event.get("concept"),
        type=event.get("plane_type")
    )


async def handle_plane_ruleset_generated(event: Dict[str, Any]):
    """Handle planes.ruleset_generated events."""
    logger.info(
        "Plane ruleset generated",
        plane_id=event.get("plane_id"),
        ruleset_type=event.get("ruleset_type")
    )


async def handle_plane_content_generated(event: Dict[str, Any]):
    """Handle planes.content_generated events."""
    logger.info(
        "Plane content generated",
        plane_id=event.get("plane_id"),
        content_type=event.get("content_type")
    )


async def handle_plane_validation_completed(event: Dict[str, Any]):
    """Handle planes.validation_completed events."""
    logger.info(
        "Plane validation completed",
        plane_id=event.get("plane_id"),
        is_valid=event.get("is_valid"),
        issues=event.get("issues", [])
    )


# Event subscriptions mapping
EVENT_SUBSCRIPTIONS = {
    "character.created": handle_character_created,
    "character.updated": handle_character_updated,
    "character.replaned": handle_character_replaned,
    "image.map_generated": handle_map_generated,
    "image.map_updated": handle_map_updated,
    "campaign.plane_transition_completed": handle_plane_transition_completed,
    "planes.generated": handle_plane_generated,
    "planes.ruleset_generated": handle_plane_ruleset_generated,
    "planes.content_generated": handle_plane_content_generated,
    "planes.validation_completed": handle_plane_validation_completed
}
