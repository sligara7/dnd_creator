"""Validation rule chain executor."""
import asyncio
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from character_service.core.exceptions import ValidationError
from character_service.core.validation.interfaces import (
    RuleCategory,
    ValidationResult,
    ValidationRule,
    ValidationSummary,
)
from character_service.domain.models import Character


@dataclass
class ValidationChain:
    """Chain of validation rules with dependency management."""

    rules: List[ValidationRule]
    category_filters: Optional[List[RuleCategory]] = None
    auto_fix: bool = False

    def __post_init__(self) -> None:
        """Initialize internal state."""
        # Build rule dependency graph
        self._rule_map: Dict[str, ValidationRule] = {r.rule_id: r for r in self.rules}
        self._execution_levels = self._build_execution_levels()

    def _build_execution_levels(self) -> List[List[ValidationRule]]:
        """Group rules into levels based on dependencies.

        Returns:
            List of lists of rules that can be executed in parallel
        """
        # Start with all rules
        rules = self.rules
        if self.category_filters:
            rules = [r for r in rules if r.category in self.category_filters]

        # Track remaining rules and their dependencies
        remaining = {r.rule_id for r in rules}
        deps = {r.rule_id: set(r.dependencies) for r in rules}
        levels: List[List[ValidationRule]] = []

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

            # Create level with ready rules
            level = [self._rule_map[rid] for rid in sorted(ready)]
            levels.append(level)

            # Update remaining rules and dependencies
            for rule_id in ready:
                remaining.remove(rule_id)
                for other_deps in deps.values():
                    other_deps.discard(rule_id)

        return levels

    async def execute(self, character: Character) -> ValidationSummary:
        """Execute the validation chain.

        Args:
            character: Character to validate

        Returns:
            Validation summary with results
        """
        all_results: List[ValidationResult] = []
        revalidate_needed: Set[str] = set()  # Rules needing revalidation after fixes

        # Process each level
        for level in self._execution_levels:
            # Execute rules in parallel
            level_results = await asyncio.gather(
                *[rule.validate(character) for rule in level]
            )
            all_results.extend(level_results)

            # Apply fixes if requested
            if self.auto_fix:
                fixed = False
                for result in level_results:
                    if not result.passed and result.issues:
                        rule = self._rule_map[result.rule_id]
                        fix_result = await rule.fix(character)
                        if fix_result:
                            # Replace original result with fix result
                            all_results.remove(result)
                            all_results.append(fix_result)
                            fixed = True

                            # Track rules that need revalidation
                            revalidate_needed.update(
                                self._get_dependent_rules(result.rule_id)
                            )

                # If fixes were applied, revalidate affected rules
                if fixed and revalidate_needed:
                    revalidate_results = await asyncio.gather(
                        *[
                            self._rule_map[rid].validate(character)
                            for rid in sorted(revalidate_needed)
                            if rid in self._rule_map
                        ]
                    )
                    # Replace old results with new ones
                    revalidated_ids = {r.rule_id for r in revalidate_results}
                    all_results = [
                        r for r in all_results if r.rule_id not in revalidated_ids
                    ]
                    all_results.extend(revalidate_results)

        # Build summary
        error_count = sum(
            1 for r in all_results for i in r.issues if i.severity == "error"
        )
        warning_count = sum(
            1 for r in all_results for i in r.issues if i.severity == "warning"
        )
        info_count = sum(1 for r in all_results for i in r.issues if i.severity == "info")
        fixes_available = sum(
            1 for r in all_results for i in r.issues if i.fix_available
        )
        fixes_applied = sum(1 for r in all_results if r.fix_applied)

        return ValidationSummary(
            character_id=character.id,
            passed=error_count == 0,
            results=all_results,
            error_count=error_count,
            warning_count=warning_count,
            info_count=info_count,
            fixes_available=fixes_available,
            fixes_applied=fixes_applied,
        )

    def _get_dependent_rules(self, rule_id: str) -> Set[str]:
        """Get all rules that depend on the given rule.

        Args:
            rule_id: ID of the rule to check

        Returns:
            Set of rule IDs that depend on the given rule
        """
        dependents: Set[str] = set()
        for rule in self.rules:
            if rule_id in rule.dependencies:
                dependents.add(rule.rule_id)
                # Also add rules that depend on this one
                dependents.update(self._get_dependent_rules(rule.rule_id))
        return dependents
