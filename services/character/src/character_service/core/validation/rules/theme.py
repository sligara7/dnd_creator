"""Theme-specific validation rules."""
from typing import Dict, List, Optional, Set

from character_service.core.exceptions import ValidationError
from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationResult,
    ValidationSeverity,
)
from character_service.domain.models import Character


class ThemeCompatibilityRule(BaseValidationRule):
    """Validate theme compatibility with character."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="theme.compatibility",
            category=RuleCategory.THEME,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate theme compatibility.

        Checks:
        - Theme requirements are met
        - Theme restrictions are not violated
        - Theme features are properly applied
        """
        issues = []
        data = character.character_data
        theme = data.get("theme")
        if not theme:
            return self.create_result(character, passed=True)

        # Validate theme requirements
        if not self._check_theme_requirements(theme, character):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Character does not meet requirements for theme: {theme['name']}",
                    field="theme",
                    fix_available=False,
                )
            )

        # Validate theme restrictions
        if restrictions := self._check_theme_restrictions(theme, character):
            for restriction in restrictions:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Theme restriction violated: {restriction}",
                        field="theme",
                        fix_available=False,
                    )
                )

        # Validate theme features
        if feature_issues := self._validate_theme_features(theme, character):
            issues.extend(feature_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_theme_requirements(self, theme: Dict, character: Character) -> bool:
        """Check if character meets theme requirements."""
        requirements = theme.get("requirements", {})

        # Check level requirement
        if min_level := requirements.get("minimum_level"):
            if character.character_data.get("level", 1) < min_level:
                return False

        # Check ability score requirements
        if ability_reqs := requirements.get("ability_scores", {}):
            scores = character.character_data.get("ability_scores", {})
            for ability, min_score in ability_reqs.items():
                if scores.get(ability, 0) < min_score:
                    return False

        # Check class/subclass requirements
        if class_reqs := requirements.get("classes", []):
            char_class = character.character_data.get("character_class")
            char_subclass = character.character_data.get("subclass")
            if not any(
                (req["class"] == char_class and (not req.get("subclass") or req["subclass"] == char_subclass))
                for req in class_reqs
            ):
                return False

        return True

    def _check_theme_restrictions(self, theme: Dict, character: Character) -> List[str]:
        """Check theme restrictions and return any violations."""
        restrictions = []
        theme_restrictions = theme.get("restrictions", {})

        # Check class restrictions
        if forbidden_classes := theme_restrictions.get("forbidden_classes", []):
            char_class = character.character_data.get("character_class")
            if char_class in forbidden_classes:
                restrictions.append(f"Class {char_class} is not allowed with this theme")

        # Check alignment restrictions
        if forbidden_alignments := theme_restrictions.get("forbidden_alignments", []):
            alignment = character.character_data.get("alignment")
            if alignment in forbidden_alignments:
                restrictions.append(f"Alignment {alignment} is not allowed with this theme")

        return restrictions

    def _validate_theme_features(self, theme: Dict, character: Character) -> List[ValidationIssue]:
        """Validate theme features are properly applied."""
        issues = []
        features = theme.get("features", [])
        char_features = character.character_data.get("theme_features", [])

        # Check all theme features are applied
        applied_features = {f["name"] for f in char_features}
        for feature in features:
            if feature["name"] not in applied_features:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Missing theme feature: {feature['name']}",
                        field="theme_features",
                        fix_available=True,
                        metadata={"feature": feature},
                    )
                )

        return issues


class ThemeTransitionRule(BaseValidationRule):
    """Validate theme transitions."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="theme.transition",
            category=RuleCategory.THEME,
            dependencies=["theme.compatibility"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate theme transitions.

        Checks:
        - Transition requirements are met
        - Previous theme state is preserved
        - Transition costs are paid
        """
        issues = []
        data = character.character_data
        transition = data.get("theme_transition")
        if not transition:
            return self.create_result(character, passed=True)

        # Check transition is valid
        if not self._is_valid_transition(transition, character):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Invalid theme transition path",
                    field="theme_transition",
                    fix_available=False,
                )
            )

        # Validate transition requirements
        if requirement_issues := self._check_transition_requirements(transition, character):
            issues.extend(requirement_issues)

        # Verify transition costs
        if cost_issues := self._verify_transition_costs(transition, character):
            issues.extend(cost_issues)

        # Check state preservation
        if state_issues := self._check_state_preservation(transition, character):
            issues.extend(state_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _is_valid_transition(self, transition: Dict, character: Character) -> bool:
        """Check if theme transition path is valid."""
        current_theme = character.character_data.get("theme", {}).get("name")
        target_theme = transition.get("target_theme")

        # Get valid transitions for current theme
        VALID_TRANSITIONS = {
            "none": {"novice", "veteran", "hero"},  # Initial theme choices
            "novice": {"veteran", "hero", "legend"},
            "veteran": {"hero", "legend", "myth"},
            "hero": {"legend", "myth"},
            "legend": {"myth"},
            # Add other theme paths
        }

        valid_targets = VALID_TRANSITIONS.get(current_theme or "none", set())
        return target_theme in valid_targets

    def _check_transition_requirements(
        self, transition: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Check theme transition requirements."""
        issues = []
        requirements = transition.get("requirements", {})

        # Level requirements
        level = character.character_data.get("level", 1)
        if min_level := requirements.get("minimum_level"):
            if level < min_level:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Character level {level} below required level {min_level}",
                        field="theme_transition.requirements",
                        fix_available=False,
                    )
                )

        # Milestone requirements
        if required_milestones := requirements.get("milestones", []):
            char_milestones = {
                m["id"] for m in character.character_data.get("milestones", [])
            }
            missing = set(required_milestones) - char_milestones
            if missing:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Missing required milestones for transition",
                        field="theme_transition.requirements",
                        fix_available=False,
                        metadata={"missing_milestones": list(missing)},
                    )
                )

        return issues

    def _verify_transition_costs(
        self, transition: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Verify transition costs are properly paid."""
        issues = []
        costs = transition.get("costs", {})

        # Resource costs
        if resource_costs := costs.get("resources", {}):
            for resource, amount in resource_costs.items():
                current = character.character_data.get("resources", {}).get(resource, 0)
                if current < amount:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Insufficient {resource} for transition",
                            field=f"resources.{resource}",
                            fix_available=False,
                            metadata={
                                "required": amount,
                                "current": current,
                            },
                        )
                    )

        # Feature costs (features that must be given up)
        if feature_costs := costs.get("features", []):
            char_features = {
                f["name"] for f in character.character_data.get("features", [])
            }
            for feature in feature_costs:
                if feature in char_features:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Must remove feature: {feature}",
                            field="features",
                            fix_available=True,
                            metadata={"feature": feature},
                        )
                    )

        return issues

    def _check_state_preservation(
        self, transition: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Check previous theme state is properly preserved."""
        issues = []
        previous_state = transition.get("previous_state", {})

        # Check preserved features
        if preserved_features := previous_state.get("preserved_features", []):
            char_features = {
                f["name"] for f in character.character_data.get("features", [])
            }
            missing = set(preserved_features) - char_features
            if missing:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Missing preserved features from previous theme",
                        field="features",
                        fix_available=True,
                        metadata={"missing_features": list(missing)},
                    )
                )

        # Check preserved relationships
        if preserved_relations := previous_state.get("preserved_relations", []):
            char_relations = {
                r["id"] for r in character.character_data.get("relationships", [])
            }
            missing = set(preserved_relations) - char_relations
            if missing:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Missing preserved relationships from previous theme",
                        field="relationships",
                        fix_available=True,
                        metadata={"missing_relations": list(missing)},
                    )
                )

        return issues
