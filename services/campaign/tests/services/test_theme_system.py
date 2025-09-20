"""Tests for campaign theme system."""
import pytest
from uuid import UUID
from typing import Dict

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.models.campaign import Campaign, CampaignState
from campaign_service.models.theme import Theme, ThemeElement
from campaign_service.services.theme import ThemeService


@pytest.fixture
async def theme_service(test_db: AsyncSession) -> ThemeService:
    """Create theme service instance."""
    return ThemeService(test_db)


@pytest.fixture
async def test_campaign(test_db: AsyncSession) -> Campaign:
    """Create test campaign."""
    campaign = Campaign(
        name="Theme Test Campaign",
        description="A campaign for testing themes",
        creator_id=UUID("00000000-0000-0000-0000-000000000001"),
        owner_id=UUID("00000000-0000-0000-0000-000000000001"),
        state=CampaignState.DRAFT,
        theme_data={},
    )
    test_db.add(campaign)
    await test_db.flush()
    return campaign


@pytest.fixture
async def dark_fantasy_theme(test_db: AsyncSession) -> Theme:
    """Create dark fantasy theme."""
    theme = Theme(
        name="Dark Fantasy",
        description="A gritty, dark fantasy theme",
        elements=[
            ThemeElement(
                name="corruption",
                type="tone",
                weight=1.0,
            ),
            ThemeElement(
                name="moral_ambiguity",
                type="narrative",
                weight=0.8,
            ),
            ThemeElement(
                name="gothic",
                type="visual",
                weight=0.7,
            ),
        ],
        validation_rules={
            "prohibited_elements": [
                "whimsical",
                "lighthearted",
            ],
            "required_elements": [
                "dark_tone",
            ],
            "minimum_darkness": 0.7,
        },
    )
    test_db.add(theme)
    await test_db.flush()
    return theme


@pytest.mark.asyncio
class TestThemeSystem:
    """Test theme system functionality."""
    
    async def test_theme_application(
        self,
        test_db: AsyncSession,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test applying theme to campaign."""
        # Apply theme
        await theme_service.apply_theme(
            campaign_id=test_campaign.id,
            theme_id=dark_fantasy_theme.id,
            strength=0.8,
        )
        
        # Verify campaign theme data
        campaign = await test_db.get(Campaign, test_campaign.id)
        assert campaign.theme_data
        assert campaign.theme_data["primary_theme"] == str(dark_fantasy_theme.id)
        assert campaign.theme_data["theme_strength"] == 0.8
        assert "gothic" in campaign.theme_data["active_elements"]
        
        # Check theme elements are properly weighted
        elements = campaign.theme_data["active_elements"]
        assert elements["corruption"]["weight"] == pytest.approx(0.8)  # Scaled by strength
        assert elements["moral_ambiguity"]["weight"] == pytest.approx(0.64)  # 0.8 * 0.8
    
    async def test_theme_validation(
        self,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test theme validation rules."""
        # Try to add conflicting elements
        with pytest.raises(ValidationError):
            await theme_service.apply_theme_elements(
                campaign_id=test_campaign.id,
                elements=["whimsical", "lighthearted"],  # Prohibited by dark fantasy
            )
        
        # Add valid elements
        await theme_service.apply_theme_elements(
            campaign_id=test_campaign.id,
            elements=["dark_tone", "gothic"],
        )
    
    async def test_theme_inheritance(
        self,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test theme inheritance by campaign elements."""
        # Apply base theme
        await theme_service.apply_theme(
            campaign_id=test_campaign.id,
            theme_id=dark_fantasy_theme.id,
            strength=0.8,
        )
        
        # Create NPC with inherited theme
        npc_data = {
            "name": "Dark Lord",
            "role": "villain",
            "inherit_theme": True,
        }
        npc = await theme_service.create_themed_npc(
            campaign_id=test_campaign.id,
            npc_data=npc_data,
        )
        assert "corruption" in npc.theme_elements
        assert "moral_ambiguity" in npc.theme_elements
        
        # Create location with inherited theme
        location_data = {
            "name": "Cursed Castle",
            "type": "dungeon",
            "inherit_theme": True,
        }
        location = await theme_service.create_themed_location(
            campaign_id=test_campaign.id,
            location_data=location_data,
        )
        assert "gothic" in location.theme_elements
    
    async def test_theme_change_propagation(
        self,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test theme changes propagating to campaign elements."""
        # Create initial themed elements
        await theme_service.apply_theme(
            campaign_id=test_campaign.id,
            theme_id=dark_fantasy_theme.id,
            strength=0.8,
        )
        npc = await theme_service.create_themed_npc(
            campaign_id=test_campaign.id,
            npc_data={"name": "Guard", "inherit_theme": True},
        )
        location = await theme_service.create_themed_location(
            campaign_id=test_campaign.id,
            location_data={"name": "Tower", "inherit_theme": True},
        )
        
        # Change theme strength
        await theme_service.update_theme_strength(
            campaign_id=test_campaign.id,
            strength=0.9,
        )
        
        # Verify propagation
        npc = await theme_service.get_npc(npc.id)
        assert npc.theme_elements["corruption"]["weight"] == pytest.approx(0.9)
        
        location = await theme_service.get_location(location.id)
        assert location.theme_elements["gothic"]["weight"] == pytest.approx(0.63)  # 0.9 * 0.7
    
    async def test_theme_conflict_resolution(
        self,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test resolving conflicts between themes."""
        # Create conflicting theme
        light_theme = Theme(
            name="High Fantasy",
            description="A light and magical theme",
            elements=[
                ThemeElement(
                    name="whimsical",
                    type="tone",
                    weight=1.0,
                ),
                ThemeElement(
                    name="lighthearted",
                    type="narrative",
                    weight=0.8,
                ),
            ],
        )
        test_db.add(light_theme)
        await test_db.flush()
        
        # Apply dark theme
        await theme_service.apply_theme(
            campaign_id=test_campaign.id,
            theme_id=dark_fantasy_theme.id,
            strength=0.8,
        )
        
        # Try to apply conflicting theme - should raise error
        with pytest.raises(ThemeConflictError):
            await theme_service.apply_secondary_theme(
                campaign_id=test_campaign.id,
                theme_id=light_theme.id,
                strength=0.5,
            )
        
        # Apply compatible theme
        neutral_theme = Theme(
            name="Mystery",
            description="A mysterious theme",
            elements=[
                ThemeElement(
                    name="intrigue",
                    type="narrative",
                    weight=1.0,
                ),
            ],
        )
        test_db.add(neutral_theme)
        await test_db.flush()
        
        # Should work with compatible theme
        await theme_service.apply_secondary_theme(
            campaign_id=test_campaign.id,
            theme_id=neutral_theme.id,
            strength=0.5,
        )
        
        campaign = await test_db.get(Campaign, test_campaign.id)
        assert "intrigue" in campaign.theme_data["active_elements"]
    
    async def test_theme_versioning(
        self,
        theme_service: ThemeService,
        test_campaign: Campaign,
        dark_fantasy_theme: Theme,
    ) -> None:
        """Test theme versioning support."""
        # Apply initial theme
        await theme_service.apply_theme(
            campaign_id=test_campaign.id,
            theme_id=dark_fantasy_theme.id,
            strength=0.8,
        )
        
        # Create version
        version_id = await theme_service.create_theme_version(
            campaign_id=test_campaign.id,
            version_name="darker",
            modifications={
                "corruption": 1.0,
                "moral_ambiguity": 0.9,
            },
        )
        
        # Switch to version
        await theme_service.switch_theme_version(
            campaign_id=test_campaign.id,
            version_id=version_id,
        )
        
        # Verify version is active
        campaign = await test_db.get(Campaign, test_campaign.id)
        assert campaign.theme_data["active_version"] == str(version_id)
        assert campaign.theme_data["active_elements"]["corruption"]["weight"] == 1.0
        
        # List versions
        versions = await theme_service.list_theme_versions(test_campaign.id)
        assert len(versions) == 2  # Initial + created version