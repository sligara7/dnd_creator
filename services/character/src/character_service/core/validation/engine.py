"""Default validation engine implementation."""
import asyncio
import logging
from collections import defaultdict
from typing import DefaultDict, Dict, List, Optional, Set

from character_service.core.exceptions import ValidationError
from character_service.core.validation.interfaces import (
    RuleCategory,
    ValidationEngine,
    ValidationResult,
    ValidationRule,
)
from character_service.domain.models import Character

logger = logging.getLogger(__name__)


class DefaultValidationEngine(ValidationEngine):
    """Default implementation of the validation engine.
    
    Includes optimizations for:
    - Result caching
    - Parallel validation
    - Incremental validation
    - Dependency-aware batching
    """

    def __init__(self) -> None:
        """Initialize engine."""
        self._rules: List[ValidationRule] = []
        self._rule_map: Dict[str, ValidationRule] = {}
        self._rule_deps: DefaultDict[str, Set[str]] = defaultdict(set)
        self._reverse_deps: DefaultDict[str, Set[str]] = defaultdict(set)
        
        # Cache for validation results
        self._result_cache: Dict[str, Dict[str, ValidationResult]] = {}
        self._cache_version = 0  # Increments when rules change
        
        # Character state versioning
        self._char_versions: Dict[str, int] = defaultdict(int)
        
        # Parallel execution settings
        self._max_workers = 4  # Configurable based on system

    async def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule to the engine.

        Args:
            rule: The validation rule to add

        Raises:
            ValidationError: If rule_id already exists or dependency is missing
        """
        if rule.rule_id in self._rule_map:
            raise ValidationError(f"Rule {rule.rule_id} already exists")

        # Verify all dependencies exist
        for dep_id in rule.dependencies:
            if dep_id not in self._rule_map:
                raise ValidationError(
                    f"Rule {rule.rule_id} depends on missing rule {dep_id}"
                )

        # Add rule
        self._rules.append(rule)
        self._rule_map[rule.rule_id] = rule

        # Update dependency graph
        for dep_id in rule.dependencies:
            self._rule_deps[rule.rule_id].add(dep_id)
            self._reverse_deps[dep_id].add(rule.rule_id)
        
        # Invalidate caches when rules change
        self._result_cache.clear()
        self._cache_version += 1

    def _get_execution_order(
        self, categories: Optional[List[RuleCategory]] = None
    ) -> List[ValidationRule]:
        """Get rules in dependency order for given categories.

        Args:
            categories: Optional list of categories to include, or None for all

        Returns:
            List of rules in execution order
        """
        # Filter rules by category if specified
        rules = self._rules
        if categories:
            rules = [r for r in rules if r.category in categories]

        # Build initial dependency sets
        remaining = {r.rule_id for r in rules}
        deps = {r.rule_id: set(r.dependencies) for r in rules}
        ordered = []

        # Keep going until all rules are ordered
        while remaining:
            # Find rules with no remaining dependencies
            ready = {r for r in remaining if not deps[r]}
            if not ready:
                # Cyclic dependency detected
                cycle = remaining.pop()
                path = [cycle]
                current = cycle
                while True:
                    current = next(iter(deps[current]))
                    if current in path:
                        cycle_str = " -> ".join(path[path.index(current) :] + [current])
                        raise ValidationError(f"Cyclic dependency detected: {cycle_str}")
                    path.append(current)

            # Add rules in sorted order for stability
            for rule_id in sorted(ready):
                ordered.append(self._rule_map[rule_id])
                remaining.remove(rule_id)
                # Remove this rule from others' dependency lists
                for other_deps in deps.values():
                    other_deps.discard(rule_id)

        return ordered

    async def validate(
        self,
        character: Character,
        categories: Optional[List[RuleCategory]] = None,
        auto_fix: bool = False,
        incremental: bool = True,
    ) -> List[ValidationResult]:
        """Validate a character against applicable rules.

        Args:
            character: The character to validate
            categories: Optional list of rule categories to run, or None for all
            auto_fix: Whether to attempt automatic fixes for issues
            incremental: Whether to use incremental validation

        Returns:
            List of validation results
        """
        # Check if we can use cached results
        char_id = str(character.id)
        char_version = hash(str(character.character_data))
        cached_version = self._char_versions.get(char_id)

        if (
            incremental
            and char_id in self._result_cache
            and cached_version == char_version
        ):
            # Return cached results for unchanged character
            return list(self._result_cache[char_id].values())

        # Track fields that have changed since last validation
        changed_fields = set()
        if incremental and char_id in self._result_cache:
            changed_fields = self._get_changed_fields(
                character.character_data,
                char_version,
                cached_version,
            )

        # Get rules in dependency order
        rules = self._get_execution_order(categories)

        # Filter rules if doing incremental validation
        if incremental and changed_fields:
            rules = [r for r in rules if self._rule_needs_rerun(r, changed_fields)]

        # Initialize results with cached values for unchanged rules
        results = {}
        if incremental and char_id in self._result_cache:
            results.update(
                {
                    rule_id: result
                    for rule_id, result in self._result_cache[char_id].items()
                    if rule_id not in {r.rule_id for r in rules}
                }
            )

        # Execute rules in parallel batches
        rule_batches = self._create_rule_batches(rules)
        for batch in rule_batches:
            # Execute batch in parallel
            batch_results = await asyncio.gather(
                *[self._execute_rule(rule, character) for rule in batch]
            )
            # Store results
            for rule, result in zip(batch, batch_results):
                results[rule.rule_id] = result

        # Auto-fix if requested
        if auto_fix:
            await self._apply_fixes(character, results)

        # Cache results
        self._result_cache[char_id] = results.copy()
        self._char_versions[char_id] = char_version

        return list(results.values())

    def _create_rule_batches(self, rules: List[ValidationRule]) -> List[List[ValidationRule]]:
        """Create batches of rules that can be executed in parallel.

        Args:
            rules: List of rules in dependency order

        Returns:
            List of rule batches
        """
        batches = []
        current_batch = []
        current_deps = set()

        for rule in rules:
            # If this rule depends on any current rules, start new batch
            if set(rule.dependencies) & current_deps:
                if current_batch:
                    batches.append(current_batch)
                    current_batch = []
                    current_deps = set()

            # Add rule to current batch
            current_batch.append(rule)
            current_deps.add(rule.rule_id)

            # Start new batch if we've reached max workers
            if len(current_batch) >= self._max_workers:
                batches.append(current_batch)
                current_batch = []
                current_deps = set()

        # Add final batch
        if current_batch:
            batches.append(current_batch)

        return batches

    async def _execute_rule(self, rule: ValidationRule, character: Character) -> ValidationResult:
        """Execute a single validation rule with caching.

        Args:
            rule: The rule to execute
            character: The character to validate

        Returns:
            ValidationResult from the rule
        """
        try:
            return await rule.validate(character)
        except Exception as e:
            # Return error result if rule execution fails
            return ValidationResult(
                rule_id=rule.rule_id,
                passed=False,
                issues=[
                    ValidationIssue(
                        rule_id=rule.rule_id,
                        severity=ValidationSeverity.ERROR,
                        message=f"Rule execution failed: {str(e)}",
                        field="",
                        fix_available=False,
                        metadata={"error": str(e)},
                    )
                ],
                character_id=character.id,
            )

    async def _apply_fixes(
        self, character: Character, results: Dict[str, ValidationResult]
    ) -> None:
        """Apply fixes for failed validations.

        Args:
            character: The character to fix
            results: Current validation results
        """
        for rule_id, result in results.items():
            if not result.passed and result.issues:
                rule = self._rule_map[rule_id]
                if fix_result := await rule.fix(character):
                    results[rule_id] = fix_result

    def _get_changed_fields(self, current_data: Dict, current_version: int, cached_version: int) -> Set[str]:
        """Identify which fields have changed since last validation.

        Args:
            current_data: Current character data
            current_version: Current data version
            cached_version: Previously cached version

        Returns:
            Set of field paths that have changed
        """
        if current_version == cached_version:
            return set()

        changed = set()
        # Compare main sections
        for section in [
            "ability_scores",
            "class_features",
            "race_features",
            "spells",
            "equipment",
            "background",
        ]:
            if section in current_data:
                changed.add(section)

        return changed

    def _rule_needs_rerun(self, rule: ValidationRule, changed_fields: Set[str]) -> bool:
        """Check if a rule needs to be re-run based on changed fields.

        Args:
            rule: The rule to check
            changed_fields: Set of fields that have changed

        Returns:
            Whether the rule should be re-run
        """
        # For now, be conservative - if any relevant fields changed, re-run
        rule_fields = self._get_rule_affected_fields(rule)
        return bool(rule_fields & changed_fields)

    def _get_rule_affected_fields(self, rule: ValidationRule) -> Set[str]:
        """Get the set of fields that a rule validates.

        Args:
            rule: The rule to analyze

        Returns:
            Set of field paths that the rule touches
        """
        # This could be enhanced with static analysis of rule implementations
        # For now, use a basic mapping
        RULE_FIELDS = {
            "core.ability_scores": {"ability_scores"},
            "core.class_progression": {"class_features", "level"},
            "core.spell_system": {"spells", "class_features"},
            "core.equipment": {"equipment"},
            "core.languages_tools": {"languages", "tool_proficiencies"},
            # Add more mappings as needed
        }
        return RULE_FIELDS.get(rule.rule_id, set())
