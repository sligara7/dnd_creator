"""Style management service."""

import json
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

from redis.asyncio import Redis
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from image_service.api.schemas.style import (
    StyleElement,
    StylePreset,
    StyleRequest,
    Theme,
    ThemeVariation,
)
from image_service.core.config import get_settings
from image_service.core.constants import (
    THEME_FANTASY,
    THEME_WESTERN,
    THEME_CYBERPUNK,
    THEME_STEAMPUNK,
    THEME_HORROR,
    THEME_SPACE_FANTASY,
    STYLE_CATEGORY_ARCHITECTURE,
    STYLE_CATEGORY_CLOTHING,
    STYLE_CATEGORY_TECHNOLOGY,
    STYLE_CATEGORY_ENVIRONMENT,
)
from image_service.core.logging import get_logger
from image_service.core.metrics import metrics
from image_service.models.theme import Theme as ThemeModel
from image_service.models.theme import ThemeElement as ThemeElementModel
from image_service.models.theme import ThemeVariation as ThemeVariationModel
from image_service.models.theme import StylePreset as StylePresetModel

settings = get_settings()
logger = get_logger(__name__)


class StyleService:
    """Service for managing styles and themes."""

    def __init__(self, db: AsyncSession, redis: Redis):
        """Initialize service."""
        self.db = db
        self.redis = redis
        self.cache_prefix = "style:"
        self.cache_ttl = settings.CACHE_TTL

    async def get_theme(self, theme_name: str) -> Optional[Theme]:
        """Get theme by name."""
        # Check cache first
        cache_key = f"{self.cache_prefix}theme:{theme_name}"
        cached = await self.redis.get(cache_key)
        if cached:
            metrics.track_cache_operation("get_theme", hit=True)
            return Theme.parse_raw(cached)

        metrics.track_cache_operation("get_theme", hit=False)

        # Query database
        result = await self.db.execute(
            select(ThemeModel).where(ThemeModel.name == theme_name)
        )
        theme_model = result.scalar_one_or_none()
        if not theme_model:
            return None

        # Convert to schema
        theme = Theme(
            name=theme_model.name,
            display_name=theme_model.display_name,
            description=theme_model.description,
            base_theme=theme_model.base_theme,
            properties=theme_model.config["properties"],
            elements=theme_model.config["elements"],
        )

        # Cache result
        await self.redis.set(
            cache_key,
            theme.json(),
            ex=self.cache_ttl,
        )

        return theme

    async def list_themes(self) -> List[Theme]:
        """List all available themes."""
        # Check cache first
        cache_key = f"{self.cache_prefix}theme:list"
        cached = await self.redis.get(cache_key)
        if cached:
            metrics.track_cache_operation("list_themes", hit=True)
            return [Theme.parse_raw(t) for t in json.loads(cached)]

        metrics.track_cache_operation("list_themes", hit=False)

        # Query database
        result = await self.db.execute(select(ThemeModel))
        themes = [
            Theme(
                name=t.name,
                display_name=t.display_name,
                description=t.description,
                base_theme=t.base_theme,
                properties=t.config["properties"],
                elements=t.config["elements"],
            )
            for t in result.scalars().all()
        ]

        # Cache result
        await self.redis.set(
            cache_key,
            json.dumps([t.json() for t in themes]),
            ex=self.cache_ttl,
        )

        return themes

    async def get_style_preset(self, preset_name: str) -> Optional[StylePreset]:
        """Get style preset by name."""
        # Check cache first
        cache_key = f"{self.cache_prefix}preset:{preset_name}"
        cached = await self.redis.get(cache_key)
        if cached:
            metrics.track_cache_operation("get_preset", hit=True)
            return StylePreset.parse_raw(cached)

        metrics.track_cache_operation("get_preset", hit=False)

        # Query database
        result = await self.db.execute(
            select(StylePresetModel).where(StylePresetModel.name == preset_name)
        )
        preset_model = result.scalar_one_or_none()
        if not preset_model:
            return None

        # Convert to schema
        preset = StylePreset(
            name=preset_model.name,
            display_name=preset_model.display_name,
            description=preset_model.description,
            category=preset_model.category,
            elements=preset_model.config["elements"],
            compatibility=preset_model.compatibility,
        )

        # Cache result
        await self.redis.set(
            cache_key,
            preset.json(),
            ex=self.cache_ttl,
        )

        return preset

    async def list_style_presets(self) -> List[StylePreset]:
        """List all available style presets."""
        # Check cache first
        cache_key = f"{self.cache_prefix}preset:list"
        cached = await self.redis.get(cache_key)
        if cached:
            metrics.track_cache_operation("list_presets", hit=True)
            return [StylePreset.parse_raw(p) for p in json.loads(cached)]

        metrics.track_cache_operation("list_presets", hit=False)

        # Query database
        result = await self.db.execute(select(StylePresetModel))
        presets = [
            StylePreset(
                name=p.name,
                display_name=p.display_name,
                description=p.description,
                category=p.category,
                elements=p.config["elements"],
                compatibility=p.compatibility,
            )
            for p in result.scalars().all()
        ]

        # Cache result
        await self.redis.set(
            cache_key,
            json.dumps([p.json() for p in presets]),
            ex=self.cache_ttl,
        )

        return presets

    async def validate_style(
        self,
        style: StyleRequest,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate style request and return any issues."""
        issues = []
        context = context or {}

        # Get theme
        theme = await self.get_theme(style.theme)
        if not theme:
            issues.append(f"Unknown theme: {style.theme}")
            return issues

        # Check preset if specified
        if style.style_preset:
            preset = await self.get_style_preset(style.style_preset)
            if not preset:
                issues.append(f"Unknown style preset: {style.style_preset}")
            elif style.theme not in preset.compatibility:
                issues.append(
                    f"Style preset '{style.style_preset}' is not compatible "
                    f"with theme '{style.theme}'"
                )

        # Validate elements
        valid_elements = {e.name for e in theme.elements}
        for element in style.elements:
            if element not in valid_elements:
                issues.append(f"Unknown style element: {element}")

        # Validate properties
        if style.properties:
            # Ensure required properties are present
            for prop in ["color_scheme", "lighting", "atmosphere"]:
                if not hasattr(style.properties, prop):
                    issues.append(f"Missing required property: {prop}")

        # Additional context-specific validation
        if context.get("is_character") and not any(
            e.category == STYLE_CATEGORY_CLOTHING for e in theme.elements
        ):
            issues.append("Theme does not support character styling")

        if context.get("is_map") and not any(
            e.category == STYLE_CATEGORY_ENVIRONMENT for e in theme.elements
        ):
            issues.append("Theme does not support map styling")

        return issues

    async def apply_style(
        self,
        style: StyleRequest,
        original_style: Optional[StyleRequest] = None,
    ) -> Dict[str, Any]:
        """Apply style and return generation parameters."""
        # Get theme
        theme = await self.get_theme(style.theme)
        if not theme:
            raise ValueError(f"Unknown theme: {style.theme}")

        # Base parameters
        params = {
            "theme": style.theme,
            "strength": style.strength,
            "properties": style.properties.dict() if style.properties else theme.properties.dict(),
        }

        # Apply preset if specified
        if style.style_preset:
            preset = await self.get_style_preset(style.style_preset)
            if preset:
                params["elements"] = [e.dict() for e in preset.elements]

        # Add or override elements
        if style.elements:
            theme_elements = {e.name: e for e in theme.elements}
            params["elements"] = [
                theme_elements[e].dict()
                for e in style.elements
                if e in theme_elements
            ]

        # If modifying existing style, merge parameters
        if original_style:
            # Merge properties with priority to new style
            if not style.properties and original_style.properties:
                params["properties"] = original_style.properties.dict()

            # Merge elements with priority to new style
            if not style.elements and original_style.elements:
                params["elements"].extend(original_style.elements)

            # Adjust strength based on existing style
            params["strength"] = min(
                style.strength,
                1.0 + (style.strength - original_style.strength) * 0.5,
            )

        return params

    def get_available_themes(self) -> Dict[str, List[str]]:
        """Get available themes and elements."""
        return {
            "visual_themes": [
                THEME_FANTASY,
                THEME_WESTERN,
                THEME_CYBERPUNK,
                THEME_STEAMPUNK,
                THEME_HORROR,
                THEME_SPACE_FANTASY,
            ],
            "style_elements": {
                STYLE_CATEGORY_ARCHITECTURE: [
                    "medieval",
                    "victorian",
                    "modern",
                    "futuristic",
                    "gothic",
                    "space_station",
                ],
                STYLE_CATEGORY_CLOTHING: [
                    "medieval",
                    "western",
                    "modern",
                    "cyberpunk",
                    "gothic",
                    "space_suit",
                ],
                STYLE_CATEGORY_TECHNOLOGY: [
                    "medieval",
                    "steampunk",
                    "modern",
                    "cyberpunk",
                    "gothic",
                    "space_tech",
                ],
                STYLE_CATEGORY_ENVIRONMENT: [
                    "forest",
                    "desert",
                    "city",
                    "dystopian",
                    "haunted",
                    "space",
                ],
            },
        }
