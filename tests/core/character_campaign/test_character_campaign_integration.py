"""
Character-Campaign Service Integration Tests

These tests verify the integration between the Character and Campaign services,
ensuring proper event handling and state synchronization via the Message Hub.
"""

import pytest
from uuid import UUID

@pytest.mark.asyncio
class TestCharacterCampaignIntegration:
    async def test_character_assignment_to_campaign(
        self,
        mock_character_service,
        mock_campaign_service,
        mock_message_hub,
        test_character_data,
        test_campaign_data,
        event_history
    ):
        """Test character assignment to campaign and related event handling"""
        # Setup test data
        character_id = test_character_data["id"]
        campaign_id = test_campaign_data["id"]
        
        # Configure mock responses
        mock_character_service.get_character.return_value = test_character_data
        mock_campaign_service.get_campaign.return_value = test_campaign_data
        
        # Simulate character assignment to campaign
        await mock_campaign_service.add_character(campaign_id, character_id)
        
        # Verify event publication
        assert len(event_history) == 1
        event = event_history[0]
        assert event["type"] == "character.assigned_to_campaign"
        assert event["data"]["character_id"] == str(character_id)
        assert event["data"]["campaign_id"] == str(campaign_id)
        
        # Verify campaign update
        mock_campaign_service.update_campaign.assert_called_once()
        
        # Verify character service notification
        mock_character_service.update_character.assert_called_once()

    async def test_campaign_theme_change_notification(
        self,
        mock_character_service,
        mock_campaign_service,
        mock_message_hub,
        test_character_data,
        test_campaign_data,
        event_history
    ):
        """Test campaign theme change notification handling"""
        # Setup test data
        character_id = test_character_data["id"]
        campaign_id = test_campaign_data["id"]
        
        new_theme = {
            "primary": "Cyberpunk",
            "secondary": "Horror"
        }
        
        # Configure mock responses
        mock_character_service.get_character.return_value = test_character_data
        mock_campaign_service.get_campaign.return_value = test_campaign_data
        
        # Simulate theme change
        await mock_campaign_service.update_theme(campaign_id, new_theme)
        
        # Verify theme change event
        assert len(event_history) == 1
        event = event_history[0]
        assert event["type"] == "campaign.theme_changed"
        assert event["data"]["campaign_id"] == str(campaign_id)
        assert event["data"]["theme"] == new_theme
        
        # Verify character service is notified
        mock_character_service.update_character_theme.assert_called_once_with(
            character_id,
            new_theme
        )

    async def test_character_evolution_in_campaign(
        self,
        mock_character_service,
        mock_campaign_service,
        mock_message_hub,
        test_character_data,
        test_campaign_data,
        event_history
    ):
        """Test character evolution tracking in campaign context"""
        # Setup test data
        character_id = test_character_data["id"]
        campaign_id = test_campaign_data["id"]
        
        evolution_data = {
            "xp_gained": 1000,
            "milestones": ["Defeated boss", "Found artifact"],
            "journal_entry": "Epic battle against the dragon"
        }
        
        # Configure mock responses
        mock_character_service.get_character.return_value = test_character_data
        mock_campaign_service.get_campaign.return_value = test_campaign_data
        
        # Simulate character evolution
        await mock_character_service.record_evolution(character_id, evolution_data)
        
        # Verify evolution event
        assert len(event_history) == 1
        event = event_history[0]
        assert event["type"] == "character.evolved"
        assert event["data"]["character_id"] == str(character_id)
        assert event["data"]["campaign_id"] == str(campaign_id)
        assert event["data"]["evolution"] == evolution_data
        
        # Verify campaign service is updated
        mock_campaign_service.update_character_progress.assert_called_once_with(
            campaign_id,
            character_id,
            evolution_data
        )

    async def test_resource_tracking_across_services(
        self,
        mock_character_service,
        mock_campaign_service,
        mock_message_hub,
        test_character_data,
        test_campaign_data,
        event_history
    ):
        """Test resource tracking synchronization between services"""
        # Setup test data
        character_id = test_character_data["id"]
        campaign_id = test_campaign_data["id"]
        
        resource_update = {
            "hit_points": 45,
            "spell_slots": {
                "1st": 3,
                "2nd": 2
            },
            "conditions": ["poisoned"]
        }
        
        # Configure mock responses
        mock_character_service.get_character.return_value = test_character_data
        mock_campaign_service.get_campaign.return_value = test_campaign_data
        
        # Simulate resource update
        await mock_character_service.update_resources(character_id, resource_update)
        
        # Verify resource update event
        assert len(event_history) == 1
        event = event_history[0]
        assert event["type"] == "character.resources_updated"
        assert event["data"]["character_id"] == str(character_id)
        assert event["data"]["campaign_id"] == str(campaign_id)
        assert event["data"]["resources"] == resource_update
        
        # Verify campaign service is notified
        mock_campaign_service.update_character_state.assert_called_once_with(
            campaign_id,
            character_id,
            resource_update
        )
