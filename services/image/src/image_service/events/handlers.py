"""Event handlers for Message Hub integration."""

from typing import Any, Dict, Optional

from image_service.core.config import get_settings
from image_service.core.constants import (
    EVENT_CHARACTER_UPDATED,
    EVENT_CAMPAIGN_THEME_CHANGED,
    EVENT_MAP_STATE_CHANGED,
)
from image_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


async def handle_character_updated(data: Dict[str, Any]) -> None:
    """Handle character update events."""
    try:
        character_id = data.get("character_id")
        if not character_id:
            logger.warning("Character ID missing from event data")
            return

        # Get relevant changes
        changes = data.get("changes", [])
        portrait_changes = [
            change for change in changes
            if change.get("field", "").startswith("appearance.")
            or change.get("field", "").startswith("equipment.")
        ]

        if not portrait_changes:
            logger.info(
                "No relevant changes for character portrait",
                character_id=character_id
            )
            return

        # TODO: Implement portrait update
        logger.info(
            "Character portrait update needed",
            character_id=character_id,
            changes=portrait_changes
        )

    except Exception as e:
        logger.error(
            "Failed to handle character update",
            error=str(e),
            data=data
        )
        raise


async def handle_campaign_theme_changed(data: Dict[str, Any]) -> None:
    """Handle campaign theme change events."""
    try:
        campaign_id = data.get("campaign_id")
        new_theme = data.get("new_theme")
        if not campaign_id or not new_theme:
            logger.warning("Missing required data in theme change event")
            return

        # TODO: Implement campaign theme update
        logger.info(
            "Campaign theme update needed",
            campaign_id=campaign_id,
            new_theme=new_theme
        )

    except Exception as e:
        logger.error(
            "Failed to handle campaign theme change",
            error=str(e),
            data=data
        )
        raise


async def handle_map_state_changed(data: Dict[str, Any]) -> None:
    """Handle map state change events."""
    try:
        map_id = data.get("map_id")
        overlay_updates = data.get("overlay_updates", [])
        if not map_id:
            logger.warning("Map ID missing from event data")
            return

        if not overlay_updates:
            logger.info(
                "No overlay updates in event data",
                map_id=map_id
            )
            return

        # TODO: Implement map overlay updates
        logger.info(
            "Map overlay update needed",
            map_id=map_id,
            updates=overlay_updates
        )

    except Exception as e:
        logger.error(
            "Failed to handle map state change",
            error=str(e),
            data=data
        )
        raise


# Event handler mapping
EVENT_HANDLERS = {
    EVENT_CHARACTER_UPDATED: handle_character_updated,
    EVENT_CAMPAIGN_THEME_CHANGED: handle_campaign_theme_changed,
    EVENT_MAP_STATE_CHANGED: handle_map_state_changed,
}
