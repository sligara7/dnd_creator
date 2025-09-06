"""Enhanced validation system for bulk operations."""
from typing import Dict, List, Optional, Any, Set
from uuid import UUID
import asyncio
from concurrent.futures import ThreadPoolExecutor

from character_service.validation.character import CharacterValidator
from character_service.validation.theme import ThemeValidator
from character_service.validation.campaign import CampaignValidator
from character_service.api.v2.models.bulk import ValidationResult


class BulkValidator:
    """Enhanced validator for bulk operations."""

    def __init__(self):
        """Initialize the validator."""
        self.character_validator = CharacterValidator()
        self.theme_validator = ThemeValidator()
        self.campaign_validator = CampaignValidator()
        self._max_parallel = 5
        self._executor = ThreadPoolExecutor(max_workers=self._max_parallel)

    async def validate_batch(
        self,
        characters: List[Dict[str, Any]],
        campaign_id: Optional[UUID] = None,
        theme_id: Optional[UUID] = None,
        validation_rules: Optional[List[str]] = None,
    ) -> List[ValidationResult]:
        """Validate a batch of characters.

        Args:
            characters: List of character data
            campaign_id: Optional campaign ID for context
            theme_id: Optional theme ID for context
            validation_rules: Optional specific rules to validate

        Returns:
            List of validation results
        """
        # Create task groups
        basic_validation_tasks = []
        campaign_validation_tasks = []
        theme_validation_tasks = []

        # Create validation context
        context = {
            "campaign_id": campaign_id,
            "theme_id": theme_id,
            "rules": validation_rules or [],
        }

        # Create semaphore for parallel processing
        semaphore = asyncio.Semaphore(self._max_parallel)

        # Create validation tasks
        for idx, character in enumerate(characters):
            # Basic character validation
            task = self._validate_character(
                index=idx,
                data=character,
                context=context,
                semaphore=semaphore,
            )
            basic_validation_tasks.append(task)

            # Campaign validation if needed
            if campaign_id:
                task = self._validate_campaign_context(
                    index=idx,
                    data=character,
                    campaign_id=campaign_id,
                    semaphore=semaphore,
                )
                campaign_validation_tasks.append(task)

            # Theme validation if needed
            if theme_id:
                task = self._validate_theme_context(
                    index=idx,
                    data=character,
                    theme_id=theme_id,
                    semaphore=semaphore,
                )
                theme_validation_tasks.append(task)

        # Run validations in parallel
        basic_results = await asyncio.gather(*basic_validation_tasks)
        campaign_results = (
            await asyncio.gather(*campaign_validation_tasks)
            if campaign_validation_tasks
            else []
        )
        theme_results = (
            await asyncio.gather(*theme_validation_tasks)
            if theme_validation_tasks
            else []
        )

        # Run cross-reference validation
        cross_ref_results = await self._validate_cross_references(characters)

        # Merge all validation results
        final_results = []
        for idx in range(len(characters)):
            # Get all results for this character
            basic = basic_results[idx]
            campaign = next(
                (r for r in campaign_results if r.index == idx),
                None,
            )
            theme = next(
                (r for r in theme_results if r.index == idx),
                None,
            )
            cross_ref = next(
                (r for r in cross_ref_results if r.index == idx),
                None,
            )

            # Combine results
            result = ValidationResult(
                index=idx,
                is_valid=all(
                    r.is_valid
                    for r in [basic, campaign, theme, cross_ref]
                    if r is not None
                ),
                errors=[
                    e
                    for r in [basic, campaign, theme, cross_ref]
                    if r is not None
                    for e in r.errors
                ],
                warnings=[
                    w
                    for r in [basic, campaign, theme, cross_ref]
                    if r is not None
                    for w in r.warnings
                ],
            )
            final_results.append(result)

        return final_results

    async def _validate_character(
        self,
        index: int,
        data: Dict[str, Any],
        context: Dict[str, Any],
        semaphore: asyncio.Semaphore,
    ) -> ValidationResult:
        """Validate a single character.

        Args:
            index: Character index
            data: Character data
            context: Validation context
            semaphore: Semaphore for parallel processing

        Returns:
            Validation result
        """
        async with semaphore:
            try:
                # Perform basic validation
                result = await self.character_validator.validate(data, context["rules"])

                return ValidationResult(
                    index=index,
                    is_valid=result.is_valid,
                    errors=result.errors,
                    warnings=result.warnings,
                )
            except Exception as e:
                return ValidationResult(
                    index=index,
                    is_valid=False,
                    errors=[
                        {
                            "error_type": "validation_error",
                            "message": str(e),
                        }
                    ],
                    warnings=[],
                )

    async def _validate_campaign_context(
        self,
        index: int,
        data: Dict[str, Any],
        campaign_id: UUID,
        semaphore: asyncio.Semaphore,
    ) -> ValidationResult:
        """Validate character against campaign context.

        Args:
            index: Character index
            data: Character data
            campaign_id: Campaign ID
            semaphore: Semaphore for parallel processing

        Returns:
            Validation result
        """
        async with semaphore:
            try:
                # Perform campaign validation
                result = await self.campaign_validator.validate(data, campaign_id)

                return ValidationResult(
                    index=index,
                    is_valid=result.is_valid,
                    errors=result.errors,
                    warnings=result.warnings,
                )
            except Exception as e:
                return ValidationResult(
                    index=index,
                    is_valid=False,
                    errors=[
                        {
                            "error_type": "campaign_validation_error",
                            "message": str(e),
                        }
                    ],
                    warnings=[],
                )

    async def _validate_theme_context(
        self,
        index: int,
        data: Dict[str, Any],
        theme_id: UUID,
        semaphore: asyncio.Semaphore,
    ) -> ValidationResult:
        """Validate character against theme context.

        Args:
            index: Character index
            data: Character data
            theme_id: Theme ID
            semaphore: Semaphore for parallel processing

        Returns:
            Validation result
        """
        async with semaphore:
            try:
                # Perform theme validation
                result = await self.theme_validator.validate(data, theme_id)

                return ValidationResult(
                    index=index,
                    is_valid=result.is_valid,
                    errors=result.errors,
                    warnings=result.warnings,
                )
            except Exception as e:
                return ValidationResult(
                    index=index,
                    is_valid=False,
                    errors=[
                        {
                            "error_type": "theme_validation_error",
                            "message": str(e),
                        }
                    ],
                    warnings=[],
                )

    async def _validate_cross_references(
        self,
        characters: List[Dict[str, Any]],
    ) -> List[ValidationResult]:
        """Validate cross-references between characters.

        This includes checking for:
        - Duplicate names
        - Theme compatibility within party
        - Resource allocation
        - etc.

        Args:
            characters: List of character data

        Returns:
            List of validation results
        """
        results = []
        used_names: Set[str] = set()
        theme_categories: Dict[str, int] = {}
        resource_allocations: Dict[str, List[Any]] = {}

        for idx, char in enumerate(characters):
            errors = []
            warnings = []

            # Check name uniqueness
            name = char.get("name", "").lower().strip()
            if name in used_names:
                errors.append(
                    {
                        "error_type": "duplicate_name",
                        "message": f"Character name '{name}' is already in use",
                    }
                )
            else:
                used_names.add(name)

            # Check theme category distribution
            if theme := char.get("theme"):
                category = theme.get("category")
                theme_categories[category] = theme_categories.get(category, 0) + 1

                # Warn about theme category imbalance
                if theme_categories[category] > len(characters) / 2:
                    warnings.append(
                        {
                            "error_type": "theme_imbalance",
                            "message": f"High concentration of {category} themes in party",
                        }
                    )

            # Check resource allocation
            for resource, value in char.get("resources", {}).items():
                if resource not in resource_allocations:
                    resource_allocations[resource] = []
                resource_allocations[resource].append(value)

                # Check for resource hoarding
                if len(resource_allocations[resource]) >= 2:
                    total = sum(resource_allocations[resource])
                    avg = total / len(resource_allocations[resource])
                    if value > avg * 2:
                        warnings.append(
                            {
                                "error_type": "resource_imbalance",
                                "message": f"Character has high allocation of {resource}",
                            }
                        )

            results.append(
                ValidationResult(
                    index=idx,
                    is_valid=len(errors) == 0,
                    errors=errors,
                    warnings=warnings,
                )
            )

        return results
