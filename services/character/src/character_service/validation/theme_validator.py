"""Theme validation system."""
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Protocol, Set, Type
from uuid import UUID

from character_service.domain.theme import (
    Theme,
    ThemeCategory,
    ThemeTransitionType,
    ThemeValidationError,
    ThemeValidationResult,
)


class ValidationContext:
    """Context for theme validation."""

    def __init__(
        self,
        character: Any,  # TODO: Replace with proper Character type
        from_theme: Optional[Theme] = None,
        to_theme: Theme = None,
        transition_type: ThemeTransitionType = None,
        campaign_event: Optional[Dict[str, Any]] = None,
    ):
        self.character = character
        self.from_theme = from_theme
        self.to_theme = to_theme
        self.transition_type = transition_type
        self.campaign_event = campaign_event


class ValidationRule(ABC):
    """Base class for validation rules."""

    @abstractmethod
    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        """Validate the context and return any errors."""
        pass


class LevelRequirementRule(ValidationRule):
    """Validates level requirements."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if context.to_theme.level_requirement > context.character.level:
            errors.append(
                ThemeValidationError(
                    error_type="level_requirement",
                    message=f"Character level {context.character.level} is below theme requirement {context.to_theme.level_requirement}",
                    context={
                        "character_level": context.character.level,
                        "required_level": context.to_theme.level_requirement,
                    },
                )
            )
        return errors


class ClassRestrictionRule(ValidationRule):
    """Validates class restrictions."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if (
            context.to_theme.class_restrictions
            and context.character.class_name not in context.to_theme.class_restrictions
        ):
            errors.append(
                ThemeValidationError(
                    error_type="class_restriction",
                    message=f"Character class {context.character.class_name} not allowed for theme",
                    context={
                        "character_class": context.character.class_name,
                        "allowed_classes": context.to_theme.class_restrictions,
                    },
                )
            )
        return errors


class RaceRestrictionRule(ValidationRule):
    """Validates race restrictions."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if (
            context.to_theme.race_restrictions
            and context.character.race not in context.to_theme.race_restrictions
        ):
            errors.append(
                ThemeValidationError(
                    error_type="race_restriction",
                    message=f"Character race {context.character.race} not allowed for theme",
                    context={
                        "character_race": context.character.race,
                        "allowed_races": context.to_theme.race_restrictions,
                    },
                )
            )
        return errors


class AbilityScoreRule(ValidationRule):
    """Validates ability score changes."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        ability_changes = {}
        
        # Remove adjustments from old theme
        if context.from_theme:
            for ability, adj in context.from_theme.ability_adjustments.items():
                ability_changes[ability] = -adj

        # Add adjustments from new theme
        for ability, adj in context.to_theme.ability_adjustments.items():
            if ability in ability_changes:
                ability_changes[ability] += adj
            else:
                ability_changes[ability] = adj

        # Validate final scores
        for ability, change in ability_changes.items():
            current_score = getattr(context.character, f"{ability.lower()}_score", 0)
            new_score = current_score + change
            if new_score < 3 or new_score > 20:
                errors.append(
                    ThemeValidationError(
                        error_type="ability_score_range",
                        message=f"Invalid {ability} score after transition: {new_score}",
                        context={
                            "ability": ability,
                            "current_score": current_score,
                            "change": change,
                            "new_score": new_score,
                        },
                    )
                )
        return errors


class AntithenticonRule(ValidationRule):
    """Validates Antitheticon-specific requirements."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if context.transition_type == ThemeTransitionType.ANTITHETICON:
            if context.to_theme.category != ThemeCategory.ANTITHETICON:
                errors.append(
                    ThemeValidationError(
                        error_type="antitheticon_category",
                        message="Antitheticon transition requires an Antitheticon theme",
                        context={
                            "theme_category": context.to_theme.category,
                        },
                    )
                )
            # TODO: Add more Antitheticon-specific validation
        return errors


class EquipmentCapacityRule(ValidationRule):
    """Validates equipment capacity after theme transition."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        # TODO: Calculate equipment changes and validate capacity
        return errors


class CampaignContextRule(ValidationRule):
    """Validates campaign context requirements."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if context.campaign_event:
            # TODO: Validate campaign context
            pass
        return errors


class ThemeValidator:
    """Theme validation system."""

    def __init__(self):
        """Initialize validator with default rules."""
        self.rules: List[ValidationRule] = [
            LevelRequirementRule(),
            ClassRestrictionRule(),
            RaceRestrictionRule(),
            AbilityScoreRule(),
            AntithenticonRule(),
            EquipmentCapacityRule(),
            CampaignContextRule(),
        ]

    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)

    async def validate(self, context: ValidationContext) -> ThemeValidationResult:
        """Validate a theme transition."""
        all_errors = []
        warnings = []

        # Run all validation rules
        for rule in self.rules:
            errors = await rule.validate(context)
            if errors:
                all_errors.extend(errors)

        # Special case for Antitheticon warnings
        if context.transition_type == ThemeTransitionType.ANTITHETICON:
            warnings.append(
                ThemeValidationError(
                    error_type="antitheticon_warning",
                    message="Antitheticon transitions may have unforeseen consequences",
                    context={
                        "theme_category": context.to_theme.category,
                    },
                )
            )

        # Generate suggestions
        suggestions = []
        if all_errors:
            # Suggest alternative themes
            suggestions.append(
                f"Consider themes without {context.to_theme.category} restrictions"
            )
            if context.to_theme.level_requirement > context.character.level:
                suggestions.append(
                    f"Level up to {context.to_theme.level_requirement} to qualify for this theme"
                )

        return ThemeValidationResult(
            is_valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=warnings,
            suggestions=suggestions,
        )


class ThemeValidatorFactory:
    """Factory for creating theme validators."""

    _validators: Dict[ThemeCategory, Type[ValidationRule]] = {}

    @classmethod
    def register_validator(cls, category: ThemeCategory, validator: Type[ValidationRule]) -> None:
        """Register a validator for a theme category."""
        cls._validators[category] = validator

    @classmethod
    def create_validator(cls, category: ThemeCategory) -> ThemeValidator:
        """Create a validator for a theme category."""
        validator = ThemeValidator()
        
        # Add category-specific validator if exists
        if category in cls._validators:
            validator.add_rule(cls._validators[category]())
        
        return validator


# Register custom validators for specific theme categories
class PrestigeThemeRule(ValidationRule):
    """Validates prestige theme requirements."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if context.to_theme.category == ThemeCategory.PRESTIGE:
            # TODO: Add prestige-specific validation
            pass
        return errors


class EpicThemeRule(ValidationRule):
    """Validates epic theme requirements."""

    async def validate(self, context: ValidationContext) -> List[ThemeValidationError]:
        errors = []
        if context.to_theme.category == ThemeCategory.EPIC:
            # TODO: Add epic-specific validation
            pass
        return errors


# Register category-specific validators
ThemeValidatorFactory.register_validator(ThemeCategory.PRESTIGE, PrestigeThemeRule)
ThemeValidatorFactory.register_validator(ThemeCategory.EPIC, EpicThemeRule)
