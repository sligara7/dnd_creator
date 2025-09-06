"""Request validation for generation pipeline."""
from typing import List, Optional

from pydantic import BaseModel, Field, validator

from ..models.theme import ContentType, GenerationConfig, ThemeContext


class ValidationError(Exception):
    """Validation error with details."""
    def __init__(self, message: str, details: Optional[dict] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class ThemeValidationResult(BaseModel):
    """Result of theme validation."""
    is_valid: bool = Field(description="Whether the theme is valid")
    errors: List[str] = Field(default_factory=list, description="Validation errors")
    warnings: List[str] = Field(default_factory=list, description="Validation warnings")


class RequestValidator:
    """Validator for generation requests."""

    @staticmethod
    def validate_theme_context(theme_context: ThemeContext) -> ThemeValidationResult:
        """Validate theme context for content generation."""
        errors = []
        warnings = []

        # Validate theme elements
        if not theme_context.elements.key_words:
            errors.append("Theme must have at least one key word")
        
        if not theme_context.elements.style_guide:
            errors.append("Theme must have style guidelines")
        
        if len(theme_context.elements.character_traits) < 2:
            warnings.append("Theme should have at least two character traits")
            
        if len(theme_context.elements.world_elements) < 2:
            warnings.append("Theme should have at least two world elements")

        # Validate sub-genres
        if theme_context.sub_genres:
            if len(theme_context.sub_genres) > 3:
                warnings.append("Having more than 3 sub-genres may dilute theme coherence")
            
            if theme_context.genre in theme_context.sub_genres:
                errors.append("Primary genre should not be included in sub-genres")

        return ThemeValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_generation_config(config: GenerationConfig) -> ThemeValidationResult:
        """Validate generation configuration."""
        errors = []
        warnings = []

        # Validate token limits for GPT-5-nano
        if config.max_tokens > 8000:
            errors.append("max_tokens exceeds GPT-5-nano's 8k context window")
        elif config.max_tokens > 6000:
            warnings.append("Large max_tokens may impact performance")

        # Validate temperature
        if config.temperature == 0:
            warnings.append("Zero temperature may result in repetitive output")
        elif config.temperature > 0.9:
            warnings.append("High temperature may result in less coherent output")

        # Validate penalties
        if abs(config.presence_penalty) > 1.5:
            warnings.append("Extreme presence_penalty may impact output quality")
        if abs(config.frequency_penalty) > 1.5:
            warnings.append("Extreme frequency_penalty may impact output quality")

        return ThemeValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @staticmethod
    def validate_content_type_theme_compatibility(
        content_type: ContentType,
        theme_context: ThemeContext
    ) -> ThemeValidationResult:
        """Validate compatibility between content type and theme."""
        errors = []
        warnings = []

        # Content type specific validations
        if content_type == ContentType.CHARACTER_BACKSTORY:
            if not theme_context.elements.character_traits:
                errors.append("Character backstory requires character traits in theme")
                
        elif content_type == ContentType.LOCATION_DESCRIPTION:
            if not theme_context.elements.world_elements:
                errors.append("Location description requires world elements in theme")
                
        elif content_type == ContentType.COMBAT_NARRATIVE:
            if theme_context.tone.value in ["light", "comedic"]:
                warnings.append(f"Combat narrative may not fit well with {theme_context.tone.value} tone")

        # Theme type specific validations
        if theme_context.type.value == "antitheticon":
            if content_type in [ContentType.COMBAT_NARRATIVE, ContentType.ITEM_DESCRIPTION]:
                warnings.append(f"{content_type.value} may need adaptation for Antitheticon themes")

        return ThemeValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )

    @classmethod
    def validate_request(
        cls,
        content_type: ContentType,
        theme_context: Optional[ThemeContext] = None,
        config: Optional[GenerationConfig] = None
    ) -> List[ThemeValidationResult]:
        """Validate complete generation request."""
        results = []

        # Always validate content type
        if not content_type:
            raise ValidationError("Content type must be specified")

        # Validate theme context if provided
        if theme_context:
            theme_result = cls.validate_theme_context(theme_context)
            results.append(theme_result)
            if not theme_result.is_valid:
                raise ValidationError(
                    "Invalid theme context",
                    {"errors": theme_result.errors}
                )

            # Check content type compatibility
            compat_result = cls.validate_content_type_theme_compatibility(
                content_type, theme_context
            )
            results.append(compat_result)
            if not compat_result.is_valid:
                raise ValidationError(
                    "Content type not compatible with theme",
                    {"errors": compat_result.errors}
                )

        # Validate config if provided
        if config:
            config_result = cls.validate_generation_config(config)
            results.append(config_result)
            if not config_result.is_valid:
                raise ValidationError(
                    "Invalid generation configuration",
                    {"errors": config_result.errors}
                )

        return results
