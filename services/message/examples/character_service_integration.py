"""Example integration of the Character Service with MessageHub.

This example demonstrates how a service like the Character Service should integrate
with MessageHub for event publishing and subscription.
"""

from typing import Dict, Any
import asyncio
import json
import logging
from uuid import UUID

from message_hub.client import MessageHubClient, CircuitBreakerConfig

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CharacterServiceIntegration:
    """Example integration class for Character Service."""
    
    def __init__(self, service_config: Dict[str, Any]):
        """Initialize the integration.
        
        Args:
            service_config: Configuration including Message Hub connection details
        """
        self.config = service_config
        self.message_hub = MessageHubClient(
            service_name="character-service",
            rabbitmq_url=service_config["message_hub_url"],
            auth_key=service_config["service_auth_key"],
            circuit_breaker_config=CircuitBreakerConfig(
                failure_threshold=5,
                reset_timeout=60,
                half_open_timeout=30
            )
        )
        self.subscribed_events = []
        
    async def start(self):
        """Start the integration."""
        await self.message_hub.connect()
        await self.setup_subscriptions()
        logger.info("Character Service integration started")
        
    async def stop(self):
        """Stop the integration."""
        await self.message_hub.close()
        logger.info("Character Service integration stopped")
        
    async def setup_subscriptions(self):
        """Set up event subscriptions."""
        # Subscribe to relevant campaign events
        campaign_events = [
            "campaign.theme_changed",
            "campaign.validated",
            "campaign.character_approved"
        ]
        await self.message_hub.subscribe(
            campaign_events,
            self.handle_campaign_event
        )
        self.subscribed_events.extend(campaign_events)
        
        # Subscribe to LLM events
        llm_events = [
            "llm.content_generated",
            "llm.refinement_suggested"
        ]
        await self.message_hub.subscribe(
            llm_events,
            self.handle_llm_event
        )
        self.subscribed_events.extend(llm_events)
        
        logger.info("Subscribed to events: %s", self.subscribed_events)
        
    async def handle_campaign_event(self, event_data: str):
        """Handle campaign-related events.
        
        Args:
            event_data: JSON string containing event data
        """
        try:
            event = json.loads(event_data)
            event_type = event.get("event_type")
            
            if event_type == "campaign.theme_changed":
                await self.handle_theme_change(event)
            elif event_type == "campaign.validated":
                await self.handle_campaign_validation(event)
            elif event_type == "campaign.character_approved":
                await self.handle_character_approval(event)
                
        except Exception as e:
            logger.exception("Error handling campaign event: %s", str(e))
            
    async def handle_llm_event(self, event_data: str):
        """Handle LLM-related events.
        
        Args:
            event_data: JSON string containing event data
        """
        try:
            event = json.loads(event_data)
            event_type = event.get("event_type")
            
            if event_type == "llm.content_generated":
                await self.handle_content_generation(event)
            elif event_type == "llm.refinement_suggested":
                await self.handle_refinement_suggestion(event)
                
        except Exception as e:
            logger.exception("Error handling LLM event: %s", str(e))
            
    async def notify_character_created(
        self,
        character_id: UUID,
        character_data: Dict[str, Any]
    ):
        """Publish character creation event.
        
        Args:
            character_id: UUID of the created character
            character_data: Character details
        """
        try:
            await self.message_hub.publish_event(
                "character.created",
                {
                    "character_id": str(character_id),
                    "data": character_data
                }
            )
            logger.info("Published character.created event for %s", character_id)
            
        except Exception as e:
            logger.exception(
                "Error publishing character.created event: %s",
                str(e)
            )
            
    async def notify_character_updated(
        self,
        character_id: UUID,
        changes: Dict[str, Any]
    ):
        """Publish character update event.
        
        Args:
            character_id: UUID of the updated character
            changes: Changed fields and values
        """
        try:
            await self.message_hub.publish_event(
                "character.updated",
                {
                    "character_id": str(character_id),
                    "changes": changes
                }
            )
            logger.info("Published character.updated event for %s", character_id)
            
        except Exception as e:
            logger.exception(
                "Error publishing character.updated event: %s",
                str(e)
            )
            
    async def handle_theme_change(self, event: Dict[str, Any]):
        """Handle campaign theme change event.
        
        Args:
            event: Theme change event data
        """
        try:
            campaign_id = event["payload"]["campaign_id"]
            theme_data = event["payload"]["theme_data"]
            
            # Process theme change for all characters in campaign
            # Implementation details would go here
            
            logger.info(
                "Processed theme change for campaign %s",
                campaign_id
            )
            
        except Exception as e:
            logger.exception(
                "Error handling theme change: %s",
                str(e)
            )
            
    async def handle_campaign_validation(self, event: Dict[str, Any]):
        """Handle campaign validation event.
        
        Args:
            event: Campaign validation event data
        """
        try:
            campaign_id = event["payload"]["campaign_id"]
            validation_data = event["payload"]["validation_data"]
            
            # Process campaign validation
            # Implementation details would go here
            
            logger.info(
                "Processed campaign validation for %s",
                campaign_id
            )
            
        except Exception as e:
            logger.exception(
                "Error handling campaign validation: %s",
                str(e)
            )
            
    async def handle_character_approval(self, event: Dict[str, Any]):
        """Handle character approval event.
        
        Args:
            event: Character approval event data
        """
        try:
            character_id = event["payload"]["character_id"]
            campaign_id = event["payload"]["campaign_id"]
            approval_data = event["payload"]["approval_data"]
            
            # Process character approval
            # Implementation details would go here
            
            logger.info(
                "Processed character approval for %s in campaign %s",
                character_id,
                campaign_id
            )
            
        except Exception as e:
            logger.exception(
                "Error handling character approval: %s",
                str(e)
            )
            
    async def handle_content_generation(self, event: Dict[str, Any]):
        """Handle LLM content generation event.
        
        Args:
            event: Content generation event data
        """
        try:
            character_id = event["payload"]["character_id"]
            content_data = event["payload"]["content_data"]
            
            # Process generated content
            # Implementation details would go here
            
            logger.info(
                "Processed generated content for character %s",
                character_id
            )
            
        except Exception as e:
            logger.exception(
                "Error handling content generation: %s",
                str(e)
            )
            
    async def handle_refinement_suggestion(self, event: Dict[str, Any]):
        """Handle LLM refinement suggestion event.
        
        Args:
            event: Refinement suggestion event data
        """
        try:
            character_id = event["payload"]["character_id"]
            suggestions = event["payload"]["suggestions"]
            
            # Process refinement suggestions
            # Implementation details would go here
            
            logger.info(
                "Processed refinement suggestions for character %s",
                character_id
            )
            
        except Exception as e:
            logger.exception(
                "Error handling refinement suggestion: %s",
                str(e)
            )

async def main():
    """Example usage of CharacterServiceIntegration."""
    # Example configuration
    config = {
        "message_hub_url": "amqp://localhost:5672",
        "service_auth_key": "character-service-key"
    }
    
    # Create and start integration
    integration = CharacterServiceIntegration(config)
    await integration.start()
    
    try:
        # Example: Create character and publish event
        character_data = {
            "name": "Thorin",
            "race": "Dwarf",
            "class": "Fighter",
            "level": 1
        }
        await integration.notify_character_created(
            UUID("12345678-1234-5678-1234-567812345678"),
            character_data
        )
        
        # Keep the integration running
        while True:
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        await integration.stop()

if __name__ == "__main__":
    asyncio.run(main())