"""Campaign context validation rules."""
from typing import Dict, List, Optional, Set

from character_service.core.exceptions import ValidationError
from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationResult,
    ValidationSeverity,
)
from character_service.domain.models import Character


class CampaignContextRule(BaseValidationRule):
    """Validate character in campaign context."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="campaign.context",
            category=RuleCategory.CAMPAIGN,
            dependencies=[
                "theme.compatibility",
                "core.class_progression",
                "core.feats",
            ],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate campaign context requirements.

        Checks:
        - Character meets campaign requirements
        - Theme is valid for campaign
        - Character options match campaign restrictions
        """
        issues = []
        data = character.character_data
        campaign = data.get("campaign")
        if not campaign:
            return self.create_result(character, passed=True)

        # Validate campaign requirements
        if requirement_issues := self._check_campaign_requirements(campaign, character):
            issues.extend(requirement_issues)

        # Validate theme compatibility
        if theme_issues := self._check_theme_compatibility(campaign, character):
            issues.extend(theme_issues)

        # Validate character options
        if option_issues := self._check_character_options(campaign, character):
            issues.extend(option_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_campaign_requirements(
        self, campaign: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Check campaign-specific requirements."""
        issues = []
        requirements = campaign.get("requirements", {})

        # Level range
        level = character.character_data.get("level", 1)
        if min_level := requirements.get("minimum_level"):
            if level < min_level:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Character level {level} below campaign minimum {min_level}",
                        field="level",
                        fix_available=False,
                    )
                )
        if max_level := requirements.get("maximum_level"):
            if level > max_level:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Character level {level} above campaign maximum {max_level}",
                        field="level",
                        fix_available=False,
                    )
                )

        # Class restrictions
        if allowed_classes := requirements.get("allowed_classes"):
            char_class = character.character_data.get("character_class")
            if char_class not in allowed_classes:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Class {char_class} not allowed in campaign",
                        field="character_class",
                        fix_available=False,
                    )
                )

        # Ability score requirements
        if score_reqs := requirements.get("ability_scores", {}):
            scores = character.character_data.get("ability_scores", {})
            for ability, requirement in score_reqs.items():
                score = scores.get(ability, 0)
                if requirement.get("minimum") and score < requirement["minimum"]:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"{ability} score below campaign minimum",
                            field=f"ability_scores.{ability}",
                            fix_available=False,
                        )
                    )
                if requirement.get("maximum") and score > requirement["maximum"]:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"{ability} score above campaign maximum",
                            field=f"ability_scores.{ability}",
                            fix_available=False,
                        )
                    )

        return issues

    def _check_theme_compatibility(
        self, campaign: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Check theme compatibility with campaign."""
        issues = []
        theme = character.character_data.get("theme")
        if not theme:
            return issues

        # Check allowed themes
        if allowed_themes := campaign.get("allowed_themes"):
            if theme["name"] not in allowed_themes:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Theme {theme['name']} not allowed in campaign",
                        field="theme",
                        fix_available=False,
                    )
                )

        # Check theme progression limits
        if progression_limits := campaign.get("theme_progression", {}):
            theme_level = theme.get("level", 0)
            if max_level := progression_limits.get("maximum_level"):
                if theme_level > max_level:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Theme level {theme_level} above campaign maximum {max_level}",
                            field="theme.level",
                            fix_available=False,
                        )
                    )

        return issues

    def _check_character_options(
        self, campaign: Dict, character: Character
    ) -> List[ValidationIssue]:
        """Check character options against campaign restrictions."""
        issues = []
        options = campaign.get("character_options", {})

        # Validate feats
        if feat_options := options.get("feats", {}):
            char_feats = character.character_data.get("feats", [])

            # Check banned feats
            if banned_feats := feat_options.get("banned", []):
                for feat in char_feats:
                    if feat["name"] in banned_feats:
                        issues.append(
                            self.create_issue(
                                severity=ValidationSeverity.ERROR,
                                message=f"Feat {feat['name']} is banned in campaign",
                                field=f"feats.{feat['name']}",
                                fix_available=True,
                            )
                        )

            # Check epic feat restrictions
            if epic_feat_min_level := feat_options.get("epic_feat_min_level"):
                level = character.character_data.get("level", 1)
                for feat in char_feats:
                    if feat.get("epic") and level < epic_feat_min_level:
                        issues.append(
                            self.create_issue(
                                severity=ValidationSeverity.ERROR,
                                message=f"Epic feat {feat['name']} requires level {epic_feat_min_level}+",
                                field=f"feats.{feat['name']}",
                                fix_available=False,
                            )
                        )

        # Validate equipment
        if equipment_options := options.get("equipment", {}):
            char_items = character.character_data.get("inventory", {}).get("items", [])

            # Check banned items
            if banned_items := equipment_options.get("banned", []):
                for item in char_items:
                    if item["name"] in banned_items:
                        issues.append(
                            self.create_issue(
                                severity=ValidationSeverity.ERROR,
                                message=f"Item {item['name']} is banned in campaign",
                                field=f"inventory.items.{item['name']}",
                                fix_available=True,
                            )
                        )

            # Check magic item limits
            if magic_item_limits := equipment_options.get("magic_item_limits"):
                magic_items = [i for i in char_items if i.get("magical")]
                if len(magic_items) > magic_item_limits.get("total", float("inf")):
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message="Too many magic items",
                            field="inventory.items",
                            fix_available=True,
                        )
                    )

        return issues


class AntithenticonRule(BaseValidationRule):
    """Validate Antitheticon-specific campaign rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="campaign.antitheticon",
            category=RuleCategory.CAMPAIGN,
            dependencies=["campaign.context"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate Antitheticon campaign rules.

        Checks:
        - Identity network requirements
        - Plot impact validation
        - Deception management
        """
        issues = []
        data = character.character_data
        campaign = data.get("campaign", {})
        if not campaign.get("antitheticon_enabled"):
            return self.create_result(character, passed=True)

        # Validate identity network
        if network_issues := self._check_identity_network(character):
            issues.extend(network_issues)

        # Validate plot impacts
        if plot_issues := self._check_plot_impacts(character):
            issues.extend(plot_issues)

        # Validate deception
        if deception_issues := self._check_deception_management(character):
            issues.extend(deception_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_identity_network(self, character: Character) -> List[ValidationIssue]:
        """Check identity network validity."""
        issues = []
        network = character.character_data.get("identity_network", {})

        # Check required identities
        if not network.get("identities"):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="No identities defined in network",
                    field="identity_network.identities",
                    fix_available=False,
                )
            )
            return issues

        # Validate each identity
        for identity in network.get("identities", []):
            # Check required fields
            if not identity.get("name"):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Identity missing name",
                        field="identity_network.identities",
                        fix_available=False,
                    )
                )

            # Check relationships
            if not identity.get("relationships"):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Identity {identity['name']} has no relationships",
                        field=f"identity_network.identities.{identity['name']}.relationships",
                        fix_available=False,
                    )
                )

        # Check network connectivity
        if not self._is_network_connected(network):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Identity network is not fully connected",
                    field="identity_network",
                    fix_available=False,
                )
            )

        return issues

    def _check_plot_impacts(self, character: Character) -> List[ValidationIssue]:
        """Check plot impact tracking."""
        issues = []
        impacts = character.character_data.get("plot_impacts", [])

        # Check impact resolution
        unresolved = [i for i in impacts if not i.get("resolved")]
        if len(unresolved) > 3:  # Max unresolved impacts
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Too many unresolved plot impacts",
                    field="plot_impacts",
                    fix_available=False,
                )
            )

        # Check impact severity balance
        severity_counts = {
            "minor": sum(1 for i in impacts if i.get("severity") == "minor"),
            "major": sum(1 for i in impacts if i.get("severity") == "major"),
            "critical": sum(1 for i in impacts if i.get("severity") == "critical"),
        }
        if severity_counts["critical"] > 1:  # Max one critical impact
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Too many critical plot impacts",
                    field="plot_impacts",
                    fix_available=False,
                )
            )

        return issues

    def _check_deception_management(self, character: Character) -> List[ValidationIssue]:
        """Check deception management."""
        issues = []
        deceptions = character.character_data.get("deceptions", [])

        # Check active deceptions
        active = [d for d in deceptions if d.get("active")]
        if len(active) > 5:  # Max active deceptions
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Too many active deceptions",
                    field="deceptions",
                    fix_available=False,
                )
            )

        # Check deception maintenance
        for deception in active:
            if not deception.get("last_maintained"):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Deception {deception['name']} has never been maintained",
                        field=f"deceptions.{deception['name']}",
                        fix_available=False,
                    )
                )

        return issues

    def _is_network_connected(self, network: Dict) -> bool:
        """Check if identity network is fully connected."""
        # Implementation would use graph connectivity algorithms
        # Simplified version for example
        identities = network.get("identities", [])
        if not identities:
            return True
        
        # Build adjacency map
        adj = {}
        for identity in identities:
            name = identity["name"]
            adj[name] = set()
            for rel in identity.get("relationships", []):
                adj[name].add(rel["target"])
                
        # Check connectivity with DFS
        visited = set()
        def dfs(node):
            visited.add(node)
            for neighbor in adj[node]:
                if neighbor not in visited:
                    dfs(neighbor)
                    
        dfs(identities[0]["name"])
        return len(visited) == len(identities)
