"""Style validation and content moderation."""

from typing import Any, Dict, List, Optional, Set, Type
from abc import ABC, abstractmethod

from image_service.api.schemas.style import StyleElement, StyleRequest, Theme
from image_service.core.logging import get_logger

logger = get_logger(__name__)


class StyleValidator(ABC):
    """Base class for style validators."""

    @abstractmethod
    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate style and return any issues."""
        pass


class ThemeCompatibilityValidator(StyleValidator):
    """Validates theme compatibility."""

    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate theme compatibility."""
        issues = []

        # Check if theme supports all required categories
        required_categories = set()
        if context:
            if context.get("is_character"):
                required_categories.add("clothing")
            if context.get("is_map"):
                required_categories.add("environment")
            if context.get("is_item"):
                required_categories.add("technology")

        theme_categories = {e.category for e in theme.elements}
        missing = required_categories - theme_categories
        if missing:
            issues.append(
                f"Theme '{theme.name}' does not support required categories: "
                f"{', '.join(missing)}"
            )

        # Check parent theme compatibility if applicable
        if theme.base_theme:
            if style.theme != theme.base_theme:
                issues.append(
                    f"Theme '{theme.name}' must be used with base theme "
                    f"'{theme.base_theme}'"
                )

        return issues


class StyleElementValidator(StyleValidator):
    """Validates style elements."""

    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate style elements."""
        issues = []

        # Check if all elements exist in theme
        valid_elements = {e.name for e in theme.elements}
        for element in style.elements:
            if element not in valid_elements:
                issues.append(f"Unknown style element: {element}")

        # Check for conflicting elements
        elements = [
            e for e in theme.elements
            if e.name in style.elements
        ]
        categories = {}
        for element in elements:
            if element.category not in categories:
                categories[element.category] = []
            categories[element.category].append(element.name)

        # Flag categories with too many elements
        for category, names in categories.items():
            if len(names) > 2:  # Maximum of 2 elements per category
                issues.append(
                    f"Too many elements in category '{category}': "
                    f"{', '.join(names)}"
                )

        return issues


class StyleStrengthValidator(StyleValidator):
    """Validates style application strength."""

    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate style strength."""
        issues = []

        # Check if strength is in valid range
        if not 0.0 <= style.strength <= 2.0:
            issues.append(
                f"Invalid style strength: {style.strength}. Must be between "
                "0.0 and 2.0"
            )

        # Check strength appropriateness for context
        if context:
            if context.get("is_character") and style.strength > 1.5:
                issues.append(
                    "Style strength too high for character visualization. "
                    "Maximum recommended: 1.5"
                )
            if context.get("is_portrait") and style.strength > 1.2:
                issues.append(
                    "Style strength too high for portraits. "
                    "Maximum recommended: 1.2"
                )

        return issues


class ContentModerationValidator(StyleValidator):
    """Validates content against moderation rules."""

    def __init__(self):
        """Initialize validator."""
        # Keywords that indicate potentially inappropriate content
        self.blocked_keywords = {
            # Violence
            "gore", "blood", "violent", "brutal",
            # Adult content
            "nude", "naked", "explicit", "adult",
            # Offensive content
            "offensive", "hate", "discriminatory",
        }

        # Keywords that require content warnings
        self.warning_keywords = {
            "dark", "scary", "horror", "creepy",
            "intense", "disturbing", "unsettling",
        }

    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate content against moderation rules."""
        issues = []

        # Check properties
        if style.properties:
            props = style.properties.dict()
            for key, value in props.items():
                # Check for blocked keywords
                for keyword in self.blocked_keywords:
                    if keyword in str(value).lower():
                        issues.append(
                            f"Property '{key}' contains blocked content: {keyword}"
                        )

                # Add warnings for concerning keywords
                for keyword in self.warning_keywords:
                    if keyword in str(value).lower():
                        issues.append(
                            f"Warning: Property '{key}' contains sensitive "
                            f"content: {keyword}"
                        )

        # Check theme elements
        for element in theme.elements:
            if element.name in style.elements:
                desc = element.description or ""
                for keyword in self.blocked_keywords:
                    if keyword in desc.lower():
                        issues.append(
                            f"Element '{element.name}' contains blocked "
                            f"content: {keyword}"
                        )

        return issues


class StyleValidationService:
    """Service for style validation."""

    def __init__(self):
        """Initialize validation service."""
        self.validators = [
            ThemeCompatibilityValidator(),
            StyleElementValidator(),
            StyleStrengthValidator(),
            ContentModerationValidator(),
        ]

    def validate(
        self,
        style: StyleRequest,
        theme: Theme,
        context: Optional[Dict[str, Any]] = None,
    ) -> List[str]:
        """Validate style using all validators."""
        issues = []
        context = context or {}

        # Run all validators
        for validator in self.validators:
            try:
                validator_issues = validator.validate(style, theme, context)
                issues.extend(validator_issues)
            except Exception as e:
                logger.error(
                    "Validator failed",
                    validator=validator.__class__.__name__,
                    error=str(e),
                )
                issues.append(f"Validation error: {str(e)}")

        return issues
