"""Integration tests for Message Hub integration."""
import asyncio
import pytest
from datetime import datetime
from typing import Any, Dict
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.exceptions import IntegrationError
from campaign_service.models.campaign import Campaign, CampaignState
from campaign_service.services.theme import ThemeService
from campaign_service.services.story import StoryService
from campaign_service.services.factory import CampaignFactory


@pytest.fixture
def mock_message_hub():
    """Create mock message hub client."""
    return AsyncMock()


@pytest.fixture
async def test_campaign(test_db: AsyncSession) -> Campaign:
    """Create a test campaign."""
    campaign = Campaign(
        name="Integration Test Campaign",
        description="A campaign for testing Message Hub integration",
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
        state=CampaignState.DRAFT,
        theme_data={},
    )
    test_db.add(campaign)
    await test_db.flush()
    return campaign


@pytest.mark.asyncio
class TestMessageHubIntegration:
    """Test Message Hub integration."""
    
    async def test_campaign_factory_events(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test campaign factory event publishing."""
        # Create factory service
        factory = CampaignFactory(
            db=test_db,
            message_hub=mock_message_hub,
        )
        
        # Generate campaign content
        await factory.generate_campaign_content(
            campaign_id=test_campaign.id,
            theme="dark_fantasy",
            complexity="moderate",
            length={"min": 5, "max": 10},
        )
        
        # Verify events published
        assert mock_message_hub.publish.call_count >= 3
        events = [call[0][0] for call in mock_message_hub.publish.call_args_list]
        assert "campaign.generation.started" in events
        assert "campaign.generation.progress" in events
        assert "campaign.generation.completed" in events
        
        # Verify event data format
        for args in mock_message_hub.publish.call_args_list:
            event = args[0][1]  # event data is second argument
            assert "campaign_id" in event
            assert "timestamp" in event
            assert isinstance(event["timestamp"], str)
    
    async def test_story_service_events(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test story service event handling."""
        # Setup story service
        story_service = StoryService(
            db=test_db,
            message_hub=mock_message_hub,
        )
        
        # Subscribe to character events
        mock_message_hub.subscribe.return_value = {
            "subscription_id": str(uuid4()),
        }
        await story_service.start()
        
        # Verify subscriptions
        subscription_calls = mock_message_hub.subscribe.call_args_list
        assert any(
            call[0][0] == "character.creation.completed"
            for call in subscription_calls
        )
        assert any(
            call[0][0] == "character.journal.updated"
            for call in subscription_calls
        )
        
        # Simulate receiving character event
        character_event = {
            "event_type": "character.creation.completed",
            "character_id": str(uuid4()),
            "campaign_id": str(test_campaign.id),
            "details": {
                "name": "Test Character",
                "role": "player",
                "backstory": "A test backstory",
            },
        }
        await story_service._handle_character_event(character_event)
        
        # Verify story updates published
        assert mock_message_hub.publish.call_count >= 1
        assert any(
            call[0][0] == "campaign.story.updated"
            for call in mock_message_hub.publish.call_args_list
        )
    
    async def test_theme_service_event_handling(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test theme service event handling."""
        # Setup theme service
        theme_service = ThemeService(
            db=test_db,
            message_hub_client=mock_message_hub,
        )
        
        # Apply theme
        await theme_service.get_theme_profile(
            "dark_fantasy",
            "mystery",
        )
        
        # Verify catalog service requests
        assert any(
            call[0][0] == "catalog.get_theme"
            for call in mock_message_hub.request.call_args_list
        )
        
        # Verify theme events published
        assert any(
            call[0][0] == "campaign.theme.updated"
            for call in mock_message_hub.publish.call_args_list
        )
    
    async def test_error_handling(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test Message Hub error handling."""
        # Setup services
        story_service = StoryService(
            db=test_db,
            message_hub=mock_message_hub,
        )
        theme_service = ThemeService(
            db=test_db,
            message_hub_client=mock_message_hub,
        )
        
        # Test request failure
        mock_message_hub.request.side_effect = Exception("Connection failed")
        with pytest.raises(IntegrationError):
            await theme_service.get_theme_profile("dark_fantasy")
        
        # Test publish failure
        mock_message_hub.publish.side_effect = Exception("Publish failed")
        with pytest.raises(IntegrationError):
            await story_service._publish_story_update(test_campaign.id, "test update")
        
        # Verify error events published
        assert any(
            call[0][0] == "campaign.error"
            for call in mock_message_hub.publish.call_args_list
        )
    
    async def test_concurrent_events(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test handling concurrent events."""
        # Setup services
        story_service = StoryService(
            db=test_db,
            message_hub=mock_message_hub,
        )
        
        # Simulate concurrent character updates
        character_events = [
            {
                "event_type": "character.journal.updated",
                "character_id": str(uuid4()),
                "campaign_id": str(test_campaign.id),
                "details": {
                    "entry_id": str(uuid4()),
                    "content": f"Journal entry {i}",
                },
            }
            for i in range(5)
        ]
        
        # Process events concurrently
        await asyncio.gather(*(
            story_service._handle_character_event(event)
            for event in character_events
        ))
        
        # Verify all updates processed
        assert mock_message_hub.publish.call_count >= len(character_events)
        
        # Verify updates are ordered
        updates = [
            call[0][1]  # event data
            for call in mock_message_hub.publish.call_args_list
            if call[0][0] == "campaign.story.updated"
        ]
        timestamps = [
            datetime.fromisoformat(update["timestamp"])
            for update in updates
        ]
        assert timestamps == sorted(timestamps)
    
    async def test_reconnection_handling(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test Message Hub reconnection handling."""
        # Setup service
        story_service = StoryService(
            db=test_db,
            message_hub=mock_message_hub,
        )
        
        # Simulate connection drop
        mock_message_hub.subscribe.side_effect = [
            Exception("Connection lost"),  # First attempt fails
            {"subscription_id": str(uuid4())},  # Second attempt succeeds
        ]
        
        # Start service (should handle reconnection)
        await story_service.start()
        
        # Verify reconnection attempted
        assert mock_message_hub.subscribe.call_count == 2
        
        # Verify service is subscribed
        assert story_service._subscribed
    
    async def test_event_validation(
        self,
        test_db: AsyncSession,
        mock_message_hub: AsyncMock,
        test_campaign: Campaign,
    ) -> None:
        """Test event data validation."""
        # Setup service
        story_service = StoryService(
            db=test_db,
            message_hub=mock_message_hub,
        )
        
        # Test invalid event format
        invalid_event = {
            "event_type": "character.creation.completed",
            # Missing required fields
        }
        await story_service._handle_character_event(invalid_event)
        
        # Verify error event published
        assert any(
            call[0][0] == "campaign.error" and
            "validation" in call[0][1]["error_type"].lower()
            for call in mock_message_hub.publish.call_args_list
        )
        
        # Test invalid campaign reference
        invalid_campaign_event = {
            "event_type": "character.creation.completed",
            "character_id": str(uuid4()),
            "campaign_id": str(uuid4()),  # Non-existent campaign
            "details": {},
        }
        await story_service._handle_character_event(invalid_campaign_event)
        
        # Verify error event published
        assert any(
            call[0][0] == "campaign.error" and
            "not found" in call[0][1]["error_message"].lower()
            for call in mock_message_hub.publish.call_args_list
        )