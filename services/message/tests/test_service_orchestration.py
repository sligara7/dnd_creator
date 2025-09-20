"""Service orchestration tests for MessageHub integration.

These tests validate multi-service coordination through the Message Hub,
focusing on realistic use cases involving multiple services.
"""

import asyncio
import json
import logging
import pytest
import uuid
from unittest.mock import Mock, patch
from typing import Dict, List

from message_hub.testing import MessageHubTestFramework

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@pytest.fixture
async def message_hub_framework():
    """Create and configure test framework."""
    framework = MessageHubTestFramework("amqp://localhost:5672")
    await framework.start()
    yield framework
    await framework.stop()
    
@pytest.mark.asyncio
async def test_character_creation_flow(message_hub_framework):
    """Test the complete character creation flow involving multiple services.
    
    This test validates the coordination between Character, Campaign,
    and LLM services during character creation.
    """
    # Create mock services
    character_service = await message_hub_framework.create_mock_service("character-service")
    campaign_service = await message_hub_framework.create_mock_service("campaign-service")
    llm_service = await message_hub_framework.create_mock_service("llm-service")
    
    # Set up event subscriptions
    await campaign_service.subscribe_to_events(["character.created", "character.updated"])
    await llm_service.subscribe_to_events(["character.created"])
    
    # Generate test data
    character_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    character_data = {
        "id": str(character_id),
        "campaign_id": str(campaign_id),
        "name": "Thorin",
        "race": "Dwarf",
        "class": "Fighter",
        "level": 1
    }
    
    # 1. Publish character creation event
    event_id = await character_service.publish_event(
        "character.created",
        character_data
    )
    
    # Verify campaign service received the event
    success, received_by = await message_hub_framework.verify_event_delivery(
        source="character-service",
        event_type="character.created",
        event_id=event_id,
        subscribers=["campaign-service", "llm-service"]
    )
    assert success, "Character creation event not delivered to all subscribers"
    
    # 2. Campaign service validates and approves character
    approval_id = await campaign_service.publish_event(
        "campaign.character_approved",
        {
            "character_id": str(character_id),
            "campaign_id": str(campaign_id),
            "status": "approved"
        }
    )
    
    # Verify character service received approval
    success, _ = await message_hub_framework.verify_event_delivery(
        source="campaign-service",
        event_type="campaign.character_approved",
        event_id=approval_id,
        subscribers=["character-service"]
    )
    assert success, "Character approval event not delivered"
    
    # 3. LLM service generates character content
    content_id = await llm_service.publish_event(
        "llm.content_generated",
        {
            "character_id": str(character_id),
            "content": {
                "backstory": "Born in the mountains of...",
                "personality": "Stoic and determined...",
                "appearance": "Sturdy build with..."
            }
        }
    )
    
    # Verify character service received generated content
    success, _ = await message_hub_framework.verify_event_delivery(
        source="llm-service",
        event_type="llm.content_generated",
        event_id=content_id,
        subscribers=["character-service"]
    )
    assert success, "Generated content event not delivered"
    
@pytest.mark.asyncio
async def test_theme_change_propagation(message_hub_framework):
    """Test theme change propagation across multiple services.
    
    This test validates that theme changes in a campaign properly
    propagate to affected services.
    """
    # Create mock services
    campaign_service = await message_hub_framework.create_mock_service("campaign-service")
    character_service = await message_hub_framework.create_mock_service("character-service")
    image_service = await message_hub_framework.create_mock_service("image-service")
    llm_service = await message_hub_framework.create_mock_service("llm-service")
    
    # Subscribe to theme change events
    await character_service.subscribe_to_events(["campaign.theme_changed"])
    await image_service.subscribe_to_events(["campaign.theme_changed"])
    await llm_service.subscribe_to_events(["campaign.theme_changed"])
    
    # Generate test data
    campaign_id = uuid.uuid4()
    new_theme = {
        "campaign_id": str(campaign_id),
        "name": "Dark Fantasy",
        "attributes": {
            "tone": "grim",
            "setting": "gothic",
            "magic_level": "low"
        }
    }
    
    # Publish theme change event
    event_id = await campaign_service.publish_event(
        "campaign.theme_changed",
        new_theme
    )
    
    # Verify all services received the theme change
    success, received_by = await message_hub_framework.verify_event_delivery(
        source="campaign-service",
        event_type="campaign.theme_changed",
        event_id=event_id,
        subscribers=["character-service", "image-service", "llm-service"]
    )
    assert success, "Theme change not propagated to all services"
    assert len(received_by) == 3, "Not all services received theme change"
    
    # Verify no cross-talk to unrelated services
    isolation = await message_hub_framework.verify_no_cross_talk(
        services=["character-service", "image-service", "llm-service"]
    )
    assert isolation, "Detected unexpected cross-talk between services"
    
@pytest.mark.asyncio
async def test_error_recovery_scenario(message_hub_framework):
    """Test error recovery in multi-service operations.
    
    This test validates that the system handles failures gracefully
    and maintains consistency across services.
    """
    # Create mock services
    character_service = await message_hub_framework.create_mock_service("character-service")
    campaign_service = await message_hub_framework.create_mock_service("campaign-service")
    
    # Set up subscriptions
    await campaign_service.subscribe_to_events(["character.updated"])
    await character_service.subscribe_to_events(["campaign.validation_failed"])
    
    # Generate test data
    character_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    update_data = {
        "character_id": str(character_id),
        "campaign_id": str(campaign_id),
        "changes": {
            "level": 2,
            "experience": 1000
        }
    }
    
    # 1. Publish character update
    update_id = await character_service.publish_event(
        "character.updated",
        update_data
    )
    
    # Verify campaign service received update
    success, _ = await message_hub_framework.verify_event_delivery(
        source="character-service",
        event_type="character.updated",
        event_id=update_id,
        subscribers=["campaign-service"]
    )
    assert success, "Character update event not delivered"
    
    # 2. Campaign service indicates validation failure
    failure_id = await campaign_service.publish_event(
        "campaign.validation_failed",
        {
            "character_id": str(character_id),
            "campaign_id": str(campaign_id),
            "reason": "Level progression not earned",
            "details": {
                "required_xp": 2000,
                "current_xp": 1000
            }
        }
    )
    
    # Verify character service received failure
    success, _ = await message_hub_framework.verify_event_delivery(
        source="campaign-service",
        event_type="campaign.validation_failed",
        event_id=failure_id,
        subscribers=["character-service"]
    )
    assert success, "Validation failure event not delivered"
    
    # 3. Character service rolls back changes
    rollback_id = await character_service.publish_event(
        "character.updated",
        {
            "character_id": str(character_id),
            "campaign_id": str(campaign_id),
            "changes": {
                "level": 1,
                "experience": 1000
            },
            "rollback": True
        }
    )
    
    # Verify campaign service received rollback
    success, _ = await message_hub_framework.verify_event_delivery(
        source="character-service",
        event_type="character.updated",
        event_id=rollback_id,
        subscribers=["campaign-service"]
    )
    assert success, "Rollback event not delivered"
    
@pytest.mark.asyncio
async def test_service_state_synchronization(message_hub_framework):
    """Test state synchronization between services.
    
    This test validates that services maintain consistent state
    through event-based synchronization.
    """
    # Create mock services
    character_service = await message_hub_framework.create_mock_service("character-service")
    campaign_service = await message_hub_framework.create_mock_service("campaign-service")
    image_service = await message_hub_framework.create_mock_service("image-service")
    
    # Subscribe to relevant events
    await campaign_service.subscribe_to_events([
        "character.created",
        "character.updated",
        "character.deleted"
    ])
    await image_service.subscribe_to_events([
        "character.created",
        "character.updated",
        "character.deleted"
    ])
    
    # Generate test data
    character_id = uuid.uuid4()
    campaign_id = uuid.uuid4()
    
    # Test state transitions
    state_transitions = [
        # 1. Create character
        {
            "event": "character.created",
            "data": {
                "id": str(character_id),
                "campaign_id": str(campaign_id),
                "name": "Thorin",
                "race": "Dwarf"
            }
        },
        # 2. Update character
        {
            "event": "character.updated",
            "data": {
                "id": str(character_id),
                "changes": {
                    "name": "Thorin Stonefist"
                }
            }
        },
        # 3. Delete character
        {
            "event": "character.deleted",
            "data": {
                "id": str(character_id),
                "reason": "player_request"
            }
        }
    ]
    
    # Publish each state transition
    for transition in state_transitions:
        event_id = await character_service.publish_event(
            transition["event"],
            transition["data"]
        )
        
        # Verify all services received the state change
        success, received_by = await message_hub_framework.verify_event_delivery(
            source="character-service",
            event_type=transition["event"],
            event_id=event_id,
            subscribers=["campaign-service", "image-service"]
        )
        assert success, f"{transition['event']} not delivered to all services"
        assert len(received_by) == 2, f"Not all services received {transition['event']}"
        
        # Allow time for processing
        await asyncio.sleep(0.1)
    
    # Verify no unexpected messages
    isolation = await message_hub_framework.verify_no_cross_talk(
        services=["campaign-service", "image-service"]
    )
    assert isolation, "Detected unexpected cross-talk during state sync"
    
@pytest.mark.asyncio
async def test_concurrent_service_operations(message_hub_framework):
    """Test concurrent operations across multiple services.
    
    This test validates that the system handles multiple concurrent
    operations correctly while maintaining consistency.
    """
    # Create mock services
    character_service = await message_hub_framework.create_mock_service("character-service")
    campaign_service = await message_hub_framework.create_mock_service("campaign-service")
    llm_service = await message_hub_framework.create_mock_service("llm-service")
    image_service = await message_hub_framework.create_mock_service("image-service")
    
    # Set up subscriptions
    await campaign_service.subscribe_to_events(["character.*"])
    await character_service.subscribe_to_events(["campaign.*", "llm.*"])
    await image_service.subscribe_to_events(["character.*", "campaign.theme_changed"])
    
    # Generate test data
    num_characters = 5
    operations = []
    
    # Create concurrent character operations
    for i in range(num_characters):
        character_id = uuid.uuid4()
        campaign_id = uuid.uuid4()
        
        operations.extend([
            # Character creation
            {
                "service": character_service,
                "event": "character.created",
                "data": {
                    "id": str(character_id),
                    "campaign_id": str(campaign_id),
                    "name": f"Character {i}",
                    "race": "Human"
                }
            },
            # Campaign response
            {
                "service": campaign_service,
                "event": "campaign.character_approved",
                "data": {
                    "character_id": str(character_id),
                    "campaign_id": str(campaign_id),
                    "status": "approved"
                }
            },
            # LLM content generation
            {
                "service": llm_service,
                "event": "llm.content_generated",
                "data": {
                    "character_id": str(character_id),
                    "content": {
                        "backstory": f"Backstory for Character {i}"
                    }
                }
            }
        ])
    
    # Execute all operations concurrently
    async def execute_operation(op):
        return await op["service"].publish_event(
            op["event"],
            op["data"]
        )
    
    event_ids = await asyncio.gather(
        *[execute_operation(op) for op in operations]
    )
    
    # Verify all events were delivered
    for i, event_id in enumerate(event_ids):
        operation = operations[i]
        subscribers = {
            "character.created": ["campaign-service", "image-service"],
            "campaign.character_approved": ["character-service"],
            "llm.content_generated": ["character-service"]
        }
        
        success, received_by = await message_hub_framework.verify_event_delivery(
            source=operation["service"].name,
            event_type=operation["event"],
            event_id=event_id,
            subscribers=subscribers[operation["event"]]
        )
        assert success, f"Event {operation['event']} not delivered to all subscribers"
        
    # Verify message ordering within each service
    for service in [character_service, campaign_service, llm_service, image_service]:
        events = service.events_received
        
        # Check that character events are processed in order
        character_events = {}
        for event in events:
            character_id = event["payload"].get("id") or event["payload"].get("character_id")
            if character_id:
                if character_id not in character_events:
                    character_events[character_id] = []
                character_events[character_id].append(event)
                
        # Verify event ordering for each character
        for char_id, char_events in character_events.items():
            event_types = [event["headers"]["event_type"] for event in char_events]
            if "character.created" in event_types:
                assert event_types.index("character.created") == 0, \
                    f"character.created not first event for {char_id}"