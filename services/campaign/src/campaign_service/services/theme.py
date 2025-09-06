"""Theme service implementation."""
from typing import Dict, List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from campaign_service.core.config import get_settings
from campaign_service.core.exceptions import ThemeNotFoundError, ThemeValidationError
from campaign_service.core.logging import get_logger

settings = get_settings()
logger = get_logger(__name__)


class ThemeService:
    """Service for managing campaign themes."""

    def __init__(
        self,
        db: AsyncSession,
        message_hub_client: Any,  # type: ignore
    ) -> None:
        """Initialize theme service.

        Args:
            db (AsyncSession): Database session
            message_hub_client (Any): Message hub client
            llm_client (Any): LLM client
        """
        self.db = db
        self.message_hub = message_hub_client

    async def get_theme_profile(
        self,
        primary_theme: str,
        secondary_theme: Optional[str] = None,
    ) -> Dict:
        """Get a theme profile that merges primary and secondary themes.

        Args:
            primary_theme (str): Primary theme name
            secondary_theme (Optional[str], optional): Secondary theme name. Defaults to None.

        Returns:
            Dict: Theme profile with merged theme settings
        
        Raises:
            ThemeNotFoundError: If theme is not found
            ThemeValidationError: If themes are incompatible
        """
        try:
            # Get theme data from catalog
            primary_theme_data = await self.message_hub.request(
                "catalog.get_theme",
                {"theme_id": primary_theme}
            )
            
            if not primary_theme_data:
                raise ThemeNotFoundError(f"Theme not found: {primary_theme}")

            # Start with primary theme as base
            theme_profile = {
                "primary": primary_theme,
                "traits": primary_theme_data["traits"],
                "elements": primary_theme_data["elements"],
                "tone": primary_theme_data["tone"],
                "restrictions": primary_theme_data["restrictions"],
            }

            # Merge secondary theme if provided
            if secondary_theme:
                secondary_theme_data = await self.message_hub.request(
                    "catalog.get_theme",
                    {"theme_id": secondary_theme}
                )
                
                if not secondary_theme_data:
                    raise ThemeNotFoundError(f"Theme not found: {secondary_theme}")

                # Validate compatibility
                compatibility = await self.validate_theme_compatibility(
                    primary_theme_data,
                    secondary_theme_data
                )
                
                if not compatibility["compatible"]:
                    raise ThemeValidationError(
                        f"Themes are incompatible: {compatibility['reason']}"
                    )

                # Merge themes
                theme_profile["secondary"] = secondary_theme
                theme_profile["traits"].extend(secondary_theme_data["traits"])
                theme_profile["elements"].extend(secondary_theme_data["elements"])
                
                # Use LLM to blend tones
                theme_profile["tone"] = await self.blend_theme_tones(
                    primary_theme_data["tone"],
                    secondary_theme_data["tone"]
                )
                
                # Combine restrictions
                theme_profile["restrictions"].extend(secondary_theme_data["restrictions"])

            return theme_profile

        except Exception as e:
            logger.error("Failed to get theme profile", error=str(e))
            raise

    async def validate_theme_compatibility(
        self,
        primary_theme: Dict,
        secondary_theme: Dict,
    ) -> Dict:
        """Validate if two themes can be combined.

        Args:
            primary_theme (Dict): Primary theme data
            secondary_theme (Dict): Secondary theme data

        Returns:
            Dict: Compatibility result with explanation
        """
        try:
            # Check for explicit incompatibilities
            if secondary_theme["id"] in primary_theme.get("incompatible_themes", []):
                return {
                    "compatible": False,
                    "reason": "Themes are explicitly marked as incompatible"
                }

            # Check for conflicting restrictions
            conflicts = []
            for p_restriction in primary_theme["restrictions"]:
                for s_restriction in secondary_theme["restrictions"]:
                    if self._are_restrictions_conflicting(p_restriction, s_restriction):
                        conflicts.append(f"{p_restriction} vs {s_restriction}")

            if conflicts:
                return {
                    "compatible": False,
                    "reason": f"Conflicting restrictions: {', '.join(conflicts)}"
                }

            # Use LLM service to validate thematic compatibility
            llm_validation = await self.message_hub.request(
                "llm.validate_theme_compatibility",
                {
                    "primary_theme": primary_theme,
                    "secondary_theme": secondary_theme,
                    "requirements": {
                        "check_tone_clash": True,
                        "check_narrative_compatibility": True,
                        "check_setting_compatibility": True
                    }
                }
            )

            return llm_validation

        except Exception as e:
            logger.error("Theme compatibility validation failed", error=str(e))
            return {"compatible": False, "reason": str(e)}

    async def blend_theme_tones(self, primary_tone: str, secondary_tone: str) -> str:
        """Blend two theme tones together.

        Args:
            primary_tone (str): Primary theme tone
            secondary_tone (str): Secondary theme tone

        Returns:
            str: Blended tone description
        """
        try:
            # Use LLM service to blend tones
            blended_tone = await self.message_hub.request(
                "llm.blend_theme_tones",
                {
                    "primary_tone": primary_tone,
                    "secondary_tone": secondary_tone,
                    "requirements": {
                        "maintain_primary_dominance": True,
                        "ensure_coherence": True,
                        "preserve_key_elements": True
                    }
                }
            )
            
            return blended_tone["tone"]

        except Exception as e:
            logger.error("Failed to blend theme tones", error=str(e))
            # Fallback to primary tone
            return primary_tone

    def _are_restrictions_conflicting(
        self,
        restriction1: str,
        restriction2: str
    ) -> bool:
        """Check if two restrictions are conflicting.

        Args:
            restriction1 (str): First restriction
            restriction2 (str): Second restriction

        Returns:
            bool: True if restrictions conflict
        """
        # Simple contradiction check
        if restriction1.startswith("no_") and restriction2.startswith("require_"):
            base1 = restriction1[3:]
            base2 = restriction2[8:]
            return base1 == base2
            
        if restriction2.startswith("no_") and restriction1.startswith("require_"):
            base1 = restriction2[3:]
            base2 = restriction1[8:]
            return base1 == base2
            
        return False
