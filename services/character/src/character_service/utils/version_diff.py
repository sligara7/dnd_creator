"""Utilities for version comparison and diffing."""
from typing import Dict, List, Optional, Any, Tuple
from enum import Enum

from deepdiff import DeepDiff

from character_service.domain.version import ChangeType


class DiffImpact(str, Enum):
    """Impact level of a diff."""

    NONE = "none"  # No mechanical impact
    LOW = "low"  # Minor mechanical impact
    MEDIUM = "medium"  # Moderate mechanical impact
    HIGH = "high"  # Major mechanical impact
    CRITICAL = "critical"  # Game-changing impact


class DiffCategory(str, Enum):
    """Categories of differences."""

    ABILITY_SCORES = "ability_scores"
    CLASS_FEATURES = "class_features"
    EQUIPMENT = "equipment"
    LEVEL = "level"
    PROFICIENCIES = "proficiencies"
    RESOURCES = "resources"
    SPELLS = "spells"
    THEME = "theme"
    OTHER = "other"


class VersionDiff:
    """Utility class for version comparison."""

    @staticmethod
    def compare_states(
        state_a: Dict[str, Any],
        state_b: Dict[str, Any],
    ) -> DeepDiff:
        """Compare two character states.

        Args:
            state_a: First state
            state_b: Second state

        Returns:
            DeepDiff object containing differences
        """
        return DeepDiff(
            state_a,
            state_b,
            ignore_order=True,
            report_repetition=True,
            verbose_level=2,
        )

    @staticmethod
    def categorize_changes(
        changes: List[Dict[str, Any]],
    ) -> Dict[DiffCategory, List[Dict[str, Any]]]:
        """Categorize changes by type.

        Args:
            changes: List of changes

        Returns:
            Dictionary mapping categories to changes
        """
        categorized = {category: [] for category in DiffCategory}

        for change in changes:
            category = VersionDiff._determine_category(change["path"])
            categorized[category].append(change)

        return categorized

    @staticmethod
    def assess_impact(
        changes: List[Dict[str, Any]],
    ) -> Tuple[DiffImpact, Dict[str, Any]]:
        """Assess the mechanical impact of changes.

        Args:
            changes: List of changes

        Returns:
            Tuple of (impact_level, impact_details)
        """
        categorized = VersionDiff.categorize_changes(changes)
        impact_scores = []
        impact_details = {}

        # Assess ability score changes
        if ability_changes := categorized[DiffCategory.ABILITY_SCORES]:
            score = VersionDiff._assess_ability_impact(ability_changes)
            impact_scores.append(score)
            impact_details["ability_scores"] = {
                "impact": score,
                "changes": len(ability_changes),
                "details": ability_changes,
            }

        # Assess level changes
        if level_changes := categorized[DiffCategory.LEVEL]:
            score = VersionDiff._assess_level_impact(level_changes)
            impact_scores.append(score)
            impact_details["level"] = {
                "impact": score,
                "changes": len(level_changes),
                "details": level_changes,
            }

        # Assess class feature changes
        if feature_changes := categorized[DiffCategory.CLASS_FEATURES]:
            score = VersionDiff._assess_feature_impact(feature_changes)
            impact_scores.append(score)
            impact_details["class_features"] = {
                "impact": score,
                "changes": len(feature_changes),
                "details": feature_changes,
            }

        # Assess equipment changes
        if equipment_changes := categorized[DiffCategory.EQUIPMENT]:
            score = VersionDiff._assess_equipment_impact(equipment_changes)
            impact_scores.append(score)
            impact_details["equipment"] = {
                "impact": score,
                "changes": len(equipment_changes),
                "details": equipment_changes,
            }

        # Assess theme changes
        if theme_changes := categorized[DiffCategory.THEME]:
            score = VersionDiff._assess_theme_impact(theme_changes)
            impact_scores.append(score)
            impact_details["theme"] = {
                "impact": score,
                "changes": len(theme_changes),
                "details": theme_changes,
            }

        # Calculate overall impact
        max_impact = max(impact_scores) if impact_scores else DiffImpact.NONE

        return max_impact, impact_details

    @staticmethod
    def generate_summary(
        changes: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Generate a human-readable summary of changes.

        Args:
            changes: List of changes

        Returns:
            Dictionary containing summary information
        """
        categorized = VersionDiff.categorize_changes(changes)
        impact_level, impact_details = VersionDiff.assess_impact(changes)

        summary = {
            "impact_level": impact_level,
            "total_changes": len(changes),
            "categories": {},
            "details": impact_details,
        }

        for category, category_changes in categorized.items():
            if category_changes:
                summary["categories"][category] = {
                    "count": len(category_changes),
                    "changes": [
                        VersionDiff._summarize_change(change)
                        for change in category_changes
                    ],
                }

        return summary

    @staticmethod
    def _determine_category(path: str) -> DiffCategory:
        """Determine the category of a change based on its path.

        Args:
            path: The attribute path

        Returns:
            Appropriate diff category
        """
        path = path.lower()
        if "ability" in path or "score" in path:
            return DiffCategory.ABILITY_SCORES
        elif "class" in path or "feature" in path:
            return DiffCategory.CLASS_FEATURES
        elif "equipment" in path or "item" in path:
            return DiffCategory.EQUIPMENT
        elif "level" in path:
            return DiffCategory.LEVEL
        elif "proficiency" in path:
            return DiffCategory.PROFICIENCIES
        elif "resource" in path:
            return DiffCategory.RESOURCES
        elif "spell" in path:
            return DiffCategory.SPELLS
        elif "theme" in path:
            return DiffCategory.THEME
        else:
            return DiffCategory.OTHER

    @staticmethod
    def _assess_ability_impact(changes: List[Dict[str, Any]]) -> DiffImpact:
        """Assess impact of ability score changes.

        Args:
            changes: List of ability score changes

        Returns:
            Impact level
        """
        max_change = 0
        for change in changes:
            old_val = change.get("old_value", 0)
            new_val = change.get("new_value", 0)
            max_change = max(max_change, abs(new_val - old_val))

        if max_change == 0:
            return DiffImpact.NONE
        elif max_change <= 1:
            return DiffImpact.LOW
        elif max_change <= 2:
            return DiffImpact.MEDIUM
        elif max_change <= 4:
            return DiffImpact.HIGH
        else:
            return DiffImpact.CRITICAL

    @staticmethod
    def _assess_level_impact(changes: List[Dict[str, Any]]) -> DiffImpact:
        """Assess impact of level changes.

        Args:
            changes: List of level changes

        Returns:
            Impact level
        """
        max_change = 0
        for change in changes:
            old_val = change.get("old_value", 0)
            new_val = change.get("new_value", 0)
            max_change = max(max_change, abs(new_val - old_val))

        if max_change == 0:
            return DiffImpact.NONE
        elif max_change == 1:
            return DiffImpact.MEDIUM
        elif max_change <= 3:
            return DiffImpact.HIGH
        else:
            return DiffImpact.CRITICAL

    @staticmethod
    def _assess_feature_impact(changes: List[Dict[str, Any]]) -> DiffImpact:
        """Assess impact of class feature changes.

        Args:
            changes: List of feature changes

        Returns:
            Impact level
        """
        feature_count = len(changes)
        if feature_count == 0:
            return DiffImpact.NONE
        elif feature_count == 1:
            return DiffImpact.LOW
        elif feature_count <= 3:
            return DiffImpact.MEDIUM
        elif feature_count <= 5:
            return DiffImpact.HIGH
        else:
            return DiffImpact.CRITICAL

    @staticmethod
    def _assess_equipment_impact(changes: List[Dict[str, Any]]) -> DiffImpact:
        """Assess impact of equipment changes.

        Args:
            changes: List of equipment changes

        Returns:
            Impact level
        """
        equipment_count = len(changes)
        if equipment_count == 0:
            return DiffImpact.NONE
        elif equipment_count <= 2:
            return DiffImpact.LOW
        elif equipment_count <= 5:
            return DiffImpact.MEDIUM
        elif equipment_count <= 10:
            return DiffImpact.HIGH
        else:
            return DiffImpact.CRITICAL

    @staticmethod
    def _assess_theme_impact(changes: List[Dict[str, Any]]) -> DiffImpact:
        """Assess impact of theme changes.

        Args:
            changes: List of theme changes

        Returns:
            Impact level
        """
        # Theme changes are always at least medium impact
        theme_count = len(changes)
        if theme_count == 0:
            return DiffImpact.NONE
        elif theme_count == 1:
            return DiffImpact.MEDIUM
        else:
            return DiffImpact.CRITICAL

    @staticmethod
    def _summarize_change(change: Dict[str, Any]) -> Dict[str, Any]:
        """Create a human-readable summary of a change.

        Args:
            change: The change to summarize

        Returns:
            Dictionary containing summary
        """
        path = change["path"]
        old_value = change.get("old_value")
        new_value = change.get("new_value")

        # Format the change description
        if old_value is None and new_value is not None:
            description = f"Added {path}: {new_value}"
        elif old_value is not None and new_value is None:
            description = f"Removed {path}: {old_value}"
        else:
            description = f"Changed {path}: {old_value} → {new_value}"

        return {
            "path": path,
            "type": change.get("type", "unknown"),
            "description": description,
            "old_value": old_value,
            "new_value": new_value,
        }
