"""Theme integration clients."""
from typing import Dict, List, Optional, Any
from datetime import datetime
from uuid import UUID

from aiohttp import ClientSession, ClientTimeout
from redis.asyncio import Redis

from character_service.core.config import settings
from character_service.core.exceptions import IntegrationError
from character_service.domain.theme import Theme, ThemeCategory


class CampaignServiceClient:
    """Client for interacting with Campaign Service."""

    def __init__(self, session: Optional[ClientSession] = None):
        self.base_url = settings.CAMPAIGN_SERVICE_URL
        self.session = session or ClientSession(
            timeout=ClientTimeout(total=settings.REQUEST_TIMEOUT)
        )

    async def close(self) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()

    async def get_campaign_context(
        self,
        campaign_id: UUID,
        event_id: UUID,
    ) -> Dict[str, Any]:
        """Get campaign context for a theme transition.

        Args:
            campaign_id: The campaign ID
            event_id: The campaign event ID

        Returns:
            Dict containing campaign context details
        
        Raises:
            IntegrationError: If there's an error getting campaign context
        """
        try:
            url = f"{self.base_url}/api/v2/campaigns/{campaign_id}/events/{event_id}/context"
            async with self.session.get(url) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise IntegrationError(f"Failed to get campaign context: {str(e)}")


class LLMServiceClient:
    """Client for interacting with LLM Service."""

    def __init__(self, session: Optional[ClientSession] = None):
        self.base_url = settings.LLM_SERVICE_URL
        self.session = session or ClientSession(
            timeout=ClientTimeout(total=settings.REQUEST_TIMEOUT)
        )

    async def close(self) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()

    async def generate_theme_content(
        self,
        character_id: UUID,
        theme_id: UUID,
        theme_category: ThemeCategory,
        prompt_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Generate theme-specific content using LLM.

        Args:
            character_id: The character ID
            theme_id: The theme ID
            theme_category: The theme category
            prompt_context: Additional context for content generation

        Returns:
            Dict containing generated content

        Raises:
            IntegrationError: If there's an error generating content
        """
        try:
            url = f"{self.base_url}/api/v2/generate/theme"
            data = {
                "character_id": str(character_id),
                "theme_id": str(theme_id),
                "theme_category": theme_category,
                "prompt_context": prompt_context,
            }
            async with self.session.post(url, json=data) as response:
                response.raise_for_status()
                return await response.json()
        except Exception as e:
            raise IntegrationError(f"Failed to generate theme content: {str(e)}")


class MessageHubClient:
    """Client for interacting with Message Hub."""

    def __init__(self, session: Optional[ClientSession] = None):
        self.base_url = settings.MESSAGE_HUB_URL
        self.session = session or ClientSession(
            timeout=ClientTimeout(total=settings.REQUEST_TIMEOUT)
        )

    async def close(self) -> None:
        """Close the client session."""
        if self.session:
            await self.session.close()

    async def publish_theme_transition(
        self,
        character_id: UUID,
        from_theme: Optional[Theme],
        to_theme: Theme,
        transition_time: datetime,
        context: Dict[str, Any],
    ) -> None:
        """Publish a theme transition event.

        Args:
            character_id: The character ID
            from_theme: The previous theme (if any)
            to_theme: The new theme
            transition_time: When the transition occurred
            context: Additional context about the transition

        Raises:
            IntegrationError: If there's an error publishing the event
        """
        try:
            url = f"{self.base_url}/api/v2/events"
            data = {
                "event_type": "theme.transition",
                "character_id": str(character_id),
                "from_theme_id": str(from_theme.id) if from_theme else None,
                "to_theme_id": str(to_theme.id),
                "transition_time": transition_time.isoformat(),
                "context": context,
            }
            async with self.session.post(url, json=data) as response:
                response.raise_for_status()
        except Exception as e:
            raise IntegrationError(f"Failed to publish theme transition: {str(e)}")


class ThemeCacheClient:
    """Client for theme caching."""

    def __init__(self, redis: Optional[Redis] = None):
        self.redis = redis or Redis.from_url(settings.REDIS_URL)
        self.key_prefix = "theme:"
        self.default_ttl = 3600  # 1 hour

    async def close(self) -> None:
        """Close the Redis connection."""
        await self.redis.close()

    async def get_theme(self, theme_id: UUID) -> Optional[Dict[str, Any]]:
        """Get a theme from cache.

        Args:
            theme_id: The theme ID

        Returns:
            Cached theme data or None if not found
        """
        key = f"{self.key_prefix}{theme_id}"
        data = await self.redis.get(key)
        return data and data.decode("utf-8")

    async def set_theme(
        self,
        theme_id: UUID,
        theme_data: Dict[str, Any],
        ttl: Optional[int] = None,
    ) -> None:
        """Cache theme data.

        Args:
            theme_id: The theme ID
            theme_data: The theme data to cache
            ttl: Optional TTL in seconds (default: 1 hour)
        """
        key = f"{self.key_prefix}{theme_id}"
        await self.redis.setex(key, ttl or self.default_ttl, theme_data)

    async def invalidate_theme(self, theme_id: UUID) -> None:
        """Remove a theme from cache.

        Args:
            theme_id: The theme ID to remove
        """
        key = f"{self.key_prefix}{theme_id}"
        await self.redis.delete(key)


class ThemeIntegrationManager:
    """Manager for theme integration clients."""

    def __init__(
        self,
        campaign_client: Optional[CampaignServiceClient] = None,
        llm_client: Optional[LLMServiceClient] = None,
        message_hub: Optional[MessageHubClient] = None,
        cache: Optional[ThemeCacheClient] = None,
    ):
        """Initialize the integration manager.

        Args:
            campaign_client: Optional campaign service client
            llm_client: Optional LLM service client
            message_hub: Optional message hub client
            cache: Optional theme cache client
        """
        self.campaign = campaign_client or CampaignServiceClient()
        self.llm = llm_client or LLMServiceClient()
        self.message_hub = message_hub or MessageHubClient()
        self.cache = cache or ThemeCacheClient()

    async def close(self) -> None:
        """Close all client connections."""
        await self.campaign.close()
        await self.llm.close()
        await self.message_hub.close()
        await self.cache.close()

    async def handle_theme_transition(
        self,
        character_id: UUID,
        from_theme: Optional[Theme],
        to_theme: Theme,
        context: Dict[str, Any],
    ) -> None:
        """Handle all integration aspects of a theme transition.

        Args:
            character_id: The character ID
            from_theme: The previous theme (if any)
            to_theme: The new theme
            context: Additional context about the transition

        Raises:
            IntegrationError: If there's an error with any integration
        """
        transition_time = datetime.utcnow()

        try:
            # Generate theme-specific content if needed
            if context.get("generate_content"):
                content = await self.llm.generate_theme_content(
                    character_id,
                    to_theme.id,
                    to_theme.category,
                    context.get("prompt_context", {}),
                )
                context["generated_content"] = content

            # Publish theme transition event
            await self.message_hub.publish_theme_transition(
                character_id,
                from_theme,
                to_theme,
                transition_time,
                context,
            )

            # Update theme cache
            await self.cache.invalidate_theme(character_id)
            if from_theme:
                await self.cache.invalidate_theme(from_theme.id)
            await self.cache.invalidate_theme(to_theme.id)

        except Exception as e:
            raise IntegrationError(f"Theme transition integration failed: {str(e)}")
