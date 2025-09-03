"""AI client interface for LLM interactions."""
import json
from typing import Dict, Optional

from httpx import AsyncClient


class AIClient:
    """Client for AI service interactions."""

    def __init__(self, base_url: str, api_key: str):
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.http_client = AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            },
            timeout=60.0,
        )

    async def generate_campaign(self, prompt: Dict) -> Dict:
        """Generate campaign structure."""
        response = await self.http_client.post(
            "/v1/campaign/generate",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_story_arc(self, prompt: Dict) -> Dict:
        """Generate story arc."""
        response = await self.http_client.post(
            "/v1/campaign/arc",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_plot_branches(self, prompt: Dict) -> Dict:
        """Generate plot branches."""
        response = await self.http_client.post(
            "/v1/campaign/branches",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_theme_integration(self, prompt: Dict) -> Dict:
        """Generate theme integration suggestions."""
        response = await self.http_client.post(
            "/v1/campaign/theme",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_npcs(self, prompt: Dict) -> Dict:
        """Generate NPCs."""
        response = await self.http_client.post(
            "/v1/npc/generate",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_locations(self, prompt: Dict) -> Dict:
        """Generate locations."""
        response = await self.http_client.post(
            "/v1/location/generate",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_chapter(self, prompt: Dict) -> Dict:
        """Generate chapter content."""
        response = await self.http_client.post(
            "/v1/chapter/generate",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def generate_encounters(self, prompt: Dict) -> Dict:
        """Generate encounters."""
        response = await self.http_client.post(
            "/v1/encounter/generate",
            json=prompt
        )
        response.raise_for_status()
        return response.json()

    async def refine_content(
        self,
        content_type: str,
        content: Dict,
        refinement: Dict
    ) -> Dict:
        """Refine generated content."""
        response = await self.http_client.post(
            f"/v1/{content_type}/refine",
            json={
                "content": content,
                "refinement": refinement
            }
        )
        response.raise_for_status()
        return response.json()

    async def validate_theme(self, content: Dict, theme: Dict) -> Dict:
        """Validate content against theme."""
        response = await self.http_client.post(
            "/v1/theme/validate",
            json={
                "content": content,
                "theme": theme
            }
        )
        response.raise_for_status()
        return response.json()

    async def generate_prompt(
        self,
        template: str,
        variables: Dict,
        format: Optional[str] = None
    ) -> str:
        """Generate a prompt from template."""
        response = await self.http_client.post(
            "/v1/prompt/generate",
            json={
                "template": template,
                "variables": variables,
                "format": format
            }
        )
        response.raise_for_status()
        return response.json()["prompt"]

    async def close(self):
        """Close HTTP client connection."""
        await self.http_client.aclose()
