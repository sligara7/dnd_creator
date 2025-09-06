"""Character validation service."""
import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.exceptions import ValidationError
from character_service.core.validation import (
    RuleCategory,
    ValidationEngine,
    ValidationResult,
    ValidationRule,
    ValidationSummary,
)
from character_service.core.validation.engine import DefaultValidationEngine
from character_service.core.validation.rules.dnd5e import (
    AbilityScoreRule,
    ClassProgressionRule,
    FeatsRule,
    ProficiencyRule,
)
from character_service.core.validation.rules.theme import (
    ThemeCompatibilityRule,
    ThemeTransitionRule,
)
from character_service.core.validation.rules.campaign import (
    CampaignContextRule,
    AntithenticonRule,
)
from character_service.domain.models import Character, ValidationState
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.validation import ValidationStateRepository


logger = logging.getLogger(__name__)


class ValidationService:
    """Service for managing character validation."""

    def __init__(
        self,
        db: AsyncSession,
        char_repository: CharacterRepository,
        validation_repository: ValidationStateRepository,
        validation_engine: Optional[ValidationEngine] = None,
        cache_ttl: int = 300,  # 5 minutes
    ) -> None:
        """Initialize service.

        Args:
            db: Database session
            char_repository: Character repository
            validation_repository: Validation state repository
            validation_engine: Optional validation engine to use
            cache_ttl: Time in seconds to cache validation results
        """
        self._db = db
        self._char_repo = char_repository
        self._validation_repo = validation_repository
        self._engine = validation_engine or self._create_default_engine()
        self._cache_ttl = timedelta(seconds=cache_ttl)
        self._result_cache: Dict[Tuple[UUID, str], Tuple[datetime, ValidationSummary]] = {}

    def _create_default_engine(self) -> ValidationEngine:
        """Create default validation engine with standard rules."""
        engine = DefaultValidationEngine()
        
        # Add core D&D rules
        engine.add_rule(AbilityScoreRule())
        engine.add_rule(ClassProgressionRule())
        engine.add_rule(FeatsRule())
        engine.add_rule(ProficiencyRule())

        # Add theme rules
        engine.add_rule(ThemeCompatibilityRule())
        engine.add_rule(ThemeTransitionRule())

        # Add campaign rules
        engine.add_rule(CampaignContextRule())
        engine.add_rule(AntithenticonRule())

        return engine

    async def add_rule(self, rule: ValidationRule) -> None:
        """Add a custom validation rule.

        Args:
            rule: Rule to add
        """
        await self._engine.add_rule(rule)
        self._clear_cache()  # Invalidate cache when rules change

    async def validate_character(
        self,
        character_id: UUID,
        categories: Optional[List[RuleCategory]] = None,
        auto_fix: bool = False,
        force_revalidate: bool = False,
    ) -> ValidationSummary:
        """Validate a character.

        Args:
            character_id: Character to validate
            categories: Optional list of rule categories to check
            auto_fix: Whether to attempt automatic fixes
            force_revalidate: Whether to ignore cached results

        Returns:
            Validation summary

        Raises:
            ValidationError: If validation fails
            CharacterNotFoundError: If character not found
        """
        # Try cache first
        cache_key = (character_id, self._get_cache_key(categories))
        if not force_revalidate:
            if cached := self._get_cached_result(cache_key):
                logger.debug("Using cached validation result for %s", character_id)
                return cached

        # Get character
        character = await self._char_repo.get(character_id)
        if not character:
            raise ValidationError(f"Character {character_id} not found")

        # Run validation
        summary = await self._engine.validate(character, categories, auto_fix)

        # Cache result
        self._cache_result(cache_key, summary)

        # Store validation state
        await self._store_validation_state(character, summary)

        return summary

    async def bulk_validate(
        self,
        character_ids: List[UUID],
        categories: Optional[List[RuleCategory]] = None,
        auto_fix: bool = False,
    ) -> Dict[UUID, ValidationSummary]:
        """Validate multiple characters in parallel.

        Args:
            character_ids: Characters to validate
            categories: Optional list of rule categories to check
            auto_fix: Whether to attempt automatic fixes

        Returns:
            Dict mapping character IDs to validation results
        """
        results = await asyncio.gather(
            *[
                self.validate_character(
                    char_id,
                    categories=categories,
                    auto_fix=auto_fix,
                    force_revalidate=False,
                )
                for char_id in character_ids
            ],
            return_exceptions=True,
        )

        return {
            char_id: result
            for char_id, result in zip(character_ids, results)
            if not isinstance(result, Exception)
        }

    async def get_validation_state(
        self,
        character_id: UUID,
    ) -> Optional[ValidationState]:
        """Get stored validation state for a character.

        Args:
            character_id: Character to check

        Returns:
            ValidationState if found, None otherwise
        """
        return await self._validation_repo.get(character_id)

    def _get_cache_key(self, categories: Optional[List[RuleCategory]]) -> str:
        """Get cache key for validation parameters."""
        if not categories:
            return "all"
        return ",".join(sorted(c.value for c in categories))

    def _get_cached_result(
        self, cache_key: Tuple[UUID, str]
    ) -> Optional[ValidationSummary]:
        """Get cached validation result if valid."""
        if cache_key not in self._result_cache:
            return None

        timestamp, result = self._result_cache[cache_key]
        if datetime.utcnow() - timestamp > self._cache_ttl:
            del self._result_cache[cache_key]
            return None

        return result

    def _cache_result(
        self, cache_key: Tuple[UUID, str], result: ValidationSummary
    ) -> None:
        """Cache a validation result."""
        self._result_cache[cache_key] = (datetime.utcnow(), result)

    def _clear_cache(self) -> None:
        """Clear the validation cache."""
        self._result_cache.clear()

    async def _store_validation_state(
        self,
        character: Character,
        summary: ValidationSummary,
    ) -> None:
        """Store validation state for tracking."""
        state = ValidationState(
            character_id=character.id,
            timestamp=datetime.utcnow(),
            passed=summary.passed,
            error_count=summary.error_count,
            warning_count=summary.warning_count,
            info_count=summary.info_count,
            details=[
                {
                    "rule_id": result.rule_id,
                    "passed": result.passed,
                    "issues": [
                        {
                            "severity": issue.severity,
                            "message": issue.message,
                            "field": issue.field,
                            "metadata": issue.metadata,
                        }
                        for issue in result.issues
                    ],
                }
                for result in summary.results
            ],
        )
        await self._validation_repo.create(state)
