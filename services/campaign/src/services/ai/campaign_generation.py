"""AI service for campaign generation."""
from typing import Dict, List, Optional, Tuple

from src.api.schemas.campaign import (
    CampaignComplexity,
    CampaignTheme,
    Campaign,
    ChapterSummary,
    NPCSummary,
    LocationSummary,
    PlotBranch,
)
from src.api.schemas.theme import ThemeProfile
from src.core.ai import AIClient


class CampaignGenerator:
    """AI-powered campaign generator."""

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def generate_campaign_structure(
        self,
        concept: str,
        theme: CampaignTheme,
        theme_profile: ThemeProfile,
        complexity: CampaignComplexity,
        num_sessions: Tuple[int, int],
    ) -> Campaign:
        """Generate high-level campaign structure."""
        prompt = self._build_campaign_prompt(
            concept,
            theme,
            theme_profile,
            complexity,
            num_sessions,
        )
        response = await self.ai_client.generate_campaign(prompt)
        return self._process_campaign_response(response)

    def _build_campaign_prompt(
        self,
        concept: str,
        theme: CampaignTheme,
        theme_profile: ThemeProfile,
        complexity: CampaignComplexity,
        num_sessions: Tuple[int, int],
    ) -> Dict:
        """Build campaign generation prompt."""
        return {
            "concept": concept,
            "theme": theme.dict(),
            "theme_profile": theme_profile.dict(),
            "complexity": complexity.value,
            "min_sessions": num_sessions[0],
            "max_sessions": num_sessions[1],
            "requirements": {
                "needs_introduction": True,
                "needs_conclusion": True,
                "allow_side_quests": complexity != CampaignComplexity.SIMPLE,
            },
        }

    def _process_campaign_response(self, response: Dict) -> Campaign:
        """Process AI response into Campaign model."""
        return Campaign(
            name=response["name"],
            concept=response["concept"],
            theme=CampaignTheme(**response["theme"]),
            chapters=[
                ChapterSummary(**chapter)
                for chapter in response["chapters"]
            ],
            npcs=[
                NPCSummary(**npc)
                for npc in response["npcs"]
            ],
            locations=[
                LocationSummary(**location)
                for location in response["locations"]
            ],
            plot_branches=[
                PlotBranch(**branch)
                for branch in response["plot_branches"]
            ],
        )

    async def generate_story_arc(
        self,
        campaign: Campaign,
        arc_type: str,
        num_chapters: int,
    ) -> List[Dict]:
        """Generate a story arc with multiple chapters."""
        prompt = self._build_arc_prompt(campaign, arc_type, num_chapters)
        response = await self.ai_client.generate_story_arc(prompt)
        return response["chapters"]

    def _build_arc_prompt(
        self,
        campaign: Campaign,
        arc_type: str,
        num_chapters: int,
    ) -> Dict:
        """Build story arc generation prompt."""
        return {
            "campaign": campaign.dict(),
            "arc_type": arc_type,
            "num_chapters": num_chapters,
            "requirements": {
                "must_advance_plot": True,
                "must_use_existing_npcs": True,
                "must_connect_to_theme": True,
            },
        }

    async def generate_plot_branches(
        self,
        campaign: Campaign,
        trigger_points: List[str],
        complexity: CampaignComplexity,
    ) -> List[PlotBranch]:
        """Generate plot branches at specified trigger points."""
        prompt = self._build_branch_prompt(
            campaign,
            trigger_points,
            complexity,
        )
        response = await self.ai_client.generate_plot_branches(prompt)
        return [PlotBranch(**branch) for branch in response["branches"]]

    def _build_branch_prompt(
        self,
        campaign: Campaign,
        trigger_points: List[str],
        complexity: CampaignComplexity,
    ) -> Dict:
        """Build plot branch generation prompt."""
        return {
            "campaign": campaign.dict(),
            "trigger_points": trigger_points,
            "complexity": complexity.value,
            "requirements": {
                "min_choices": 2,
                "max_choices": 4,
                "must_have_consequences": True,
                "allow_dead_ends": complexity in [
                    CampaignComplexity.COMPLEX,
                    CampaignComplexity.EPIC,
                ],
            },
        }

    async def generate_theme_integration(
        self,
        campaign: Campaign,
        theme_profile: ThemeProfile,
    ) -> Dict:
        """Generate theme integration suggestions."""
        prompt = self._build_theme_prompt(campaign, theme_profile)
        response = await self.ai_client.generate_theme_integration(prompt)
        return {
            "elements": response["theme_elements"],
            "progression": response["theme_progression"],
            "key_moments": response["key_moments"],
        }

    def _build_theme_prompt(
        self,
        campaign: Campaign,
        theme_profile: ThemeProfile,
    ) -> Dict:
        """Build theme integration prompt."""
        return {
            "campaign": campaign.dict(),
            "theme_profile": theme_profile.dict(),
            "requirements": {
                "must_use_style_guide": True,
                "must_follow_intensity_curve": True,
                "must_respect_exclusions": True,
            },
        }
