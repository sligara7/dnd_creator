"""D&D 5e (2024) validation rules."""
from typing import Dict, List, Optional, Set

from character_service.core.exceptions import ValidationError
from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationResult,
    ValidationSeverity,
)
from character_service.domain.models import Character


class AbilityScoreRule(BaseValidationRule):
    """Validate ability scores according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.ability_scores",
            category=RuleCategory.BASE,
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate ability scores.

        New in 2024:
        - Standard array: 16,14,13,12,11,10
        - Point buy: 27 points (min 8, max 16)
        - Racial ability score bonuses replaced with background/feat bonuses
        """
        scores = character.character_data.get("ability_scores", {})
        issues = []

        # Check all abilities are present
        required = {"strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"}
        missing = required - set(scores.keys())
        if missing:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing ability scores: {', '.join(missing)}",
                    field="ability_scores",
                    fix_available=False,
                )
            )
            return self.create_result(character, passed=False, issues=issues)

        # Validate each score
        for ability, score in scores.items():
            if not isinstance(score, int):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"{ability} score must be an integer",
                        field=f"ability_scores.{ability}",
                        fix_available=False,
                    )
                )
                continue

            if score < 3 or score > 20:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"{ability} score {score} is outside valid range (3-20)",
                        field=f"ability_scores.{ability}",
                        fix_available=False,
                    )
                )

        # Validate generation method
        method = character.character_data.get("ability_score_method")
        if method == "standard_array":
            standard_array = {16, 14, 13, 12, 11, 10}
            if set(scores.values()) != standard_array:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Standard array scores must be exactly: 16,14,13,12,11,10",
                        field="ability_scores",
                        fix_available=False,
                    )
                )
        elif method == "point_buy":
            if not self._validate_point_buy(scores.values()):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Point buy must use 27 points, scores between 8-16",
                        field="ability_scores",
                        fix_available=False,
                    )
                )

        return self.create_result(character, passed=not issues, issues=issues)

    def _validate_point_buy(self, scores: List[int]) -> bool:
        """Validate point buy scores.

        Args:
            scores: List of ability scores

        Returns:
            Whether scores are valid under point buy
        """
        POINT_COSTS = {
            8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5,
            14: 7, 15: 9, 16: 11
        }
        total_points = 0
        for score in scores:
            if score < 8 or score > 16:
                return False
            total_points += POINT_COSTS[score]
        return total_points == 27


class ClassProgressionRule(BaseValidationRule):
    """Validate class features and progression."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.class_progression",
            category=RuleCategory.BASE,
            dependencies=["core.ability_scores"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate class features and progression.

        2024 changes:
        - Epic Boons at level 20
        - Revised class progression tracks
        - Updated feature timing
        """
        issues = []
        data = character.character_data

        # Validate basic class data
        char_class = data.get("character_class")
        if not char_class:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Character class is required",
                    field="character_class",
                    fix_available=False,
                )
            )
            return self.create_result(character, passed=False, issues=issues)

        level = data.get("level", 1)
        if not isinstance(level, int) or level < 1 or level > 20:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Level must be between 1 and 20",
                    field="level",
                    fix_available=False,
                )
            )
            return self.create_result(character, passed=False, issues=issues)

        # Validate class features
        features = data.get("class_features", [])
        expected_features = self._get_expected_features(char_class, level)
        missing_features = expected_features - set(f["name"] for f in features)
        if missing_features:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing class features: {', '.join(missing_features)}",
                    field="class_features",
                    fix_available=True,
                    metadata={"missing_features": list(missing_features)},
                )
            )

        # Validate subclass
        if level >= 3:
            subclass = data.get("subclass")
            if not subclass:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Subclass required at level 3+",
                        field="subclass",
                        fix_available=False,
                    )
                )

        # Validate Epic Boon at level 20
        if level == 20:
            epic_boon = data.get("epic_boon")
            if not epic_boon:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Epic Boon required at level 20",
                        field="epic_boon",
                        fix_available=False,
                    )
                )

        return self.create_result(character, passed=not issues, issues=issues)

    def _get_expected_features(self, char_class: str, level: int) -> Set[str]:
        """Get expected class features for given class and level."""
        # This would be expanded with all 2024 class features
        FEATURES = {
            "fighter": {
                1: {"Fighting Style", "Second Wind"},
                2: {"Action Surge"},
                3: {"Subclass Feature"},
                4: {"Martial Training"},
                5: {"Extra Attack"},
                6: {"Tactical Training"},
                7: {"Subclass Feature"},
                8: {"Ability Score Improvement"},
                9: {"Indomitable"},
                10: {"Subclass Feature"},
                11: {"Extra Attack (2)"},
                12: {"Ability Score Improvement"},
                13: {"Indomitable (2)"},
                14: {"Tactical Training Improvement"},
                15: {"Subclass Feature"},
                16: {"Ability Score Improvement"},
                17: {"Action Surge (2)", "Indomitable (3)"},
                18: {"Subclass Feature"},
                19: {"Ability Score Improvement"},
                20: {"Epic Boon"},
            },
            # Add other classes...
        }
        
        features = set()
        if char_class in FEATURES:
            for l in range(1, level + 1):
                if l in FEATURES[char_class]:
                    features.update(FEATURES[char_class][l])
        return features


class ProficiencyRule(BaseValidationRule):
    """Validate proficiencies according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.proficiencies",
            category=RuleCategory.BASE,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate proficiencies.

        2024 changes:
        - Updated skill list
        - Tool proficiency changes
        - Expertise rules updates
        """
        issues = []
        data = character.character_data

        # Validate skill proficiencies
        skills = data.get("skills", {})
        VALID_SKILLS = {
            "acrobatics", "animal_handling", "arcana", "athletics",
            "deception", "history", "insight", "intimidation",
            "investigation", "medicine", "nature", "perception",
            "performance", "persuasion", "religion", "sleight_of_hand",
            "stealth", "survival",
        }

        for skill, proficient in skills.items():
            if skill not in VALID_SKILLS:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid skill: {skill}",
                        field=f"skills.{skill}",
                        fix_available=True,
                    )
                )

        # Check number of skill proficiencies
        proficient_count = sum(1 for v in skills.values() if v.get("proficient"))
        expected_count = self._get_expected_skill_count(character)
        if proficient_count > expected_count:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many skill proficiencies ({proficient_count}, expected {expected_count})",
                    field="skills",
                    fix_available=False,
                )
            )

        # Validate expertise
        expertise_count = sum(1 for v in skills.values() if v.get("expertise"))
        expected_expertise = self._get_expected_expertise_count(character)
        if expertise_count > expected_expertise:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many expertise ({expertise_count}, expected {expected_expertise})",
                    field="skills",
                    fix_available=False,
                )
            )

        # Validate saving throw proficiencies
        saves = data.get("saving_throws", {})
        class_saves = self._get_class_saving_throws(data.get("character_class"))
        for ability, proficient in saves.items():
            if proficient and ability not in class_saves:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid saving throw proficiency: {ability}",
                        field=f"saving_throws.{ability}",
                        fix_available=True,
                    )
                )

        return self.create_result(character, passed=not issues, issues=issues)

    def _get_expected_skill_count(self, character: Character) -> int:
        """Get expected number of skill proficiencies."""
        # This would be based on class, background, etc.
        data = character.character_data
        count = 0
        
        # Class skills
        class_skills = {
            "fighter": 2,
            "rogue": 4,
            # Add other classes...
        }
        count += class_skills.get(data.get("character_class", ""), 0)

        # Background skills
        count += 2  # All backgrounds give 2 skills in 2024

        return count

    def _get_expected_expertise_count(self, character: Character) -> int:
        """Get expected number of expertise."""
        # Based on class features, etc.
        data = character.character_data
        char_class = data.get("character_class")
        level = data.get("level", 1)

        if char_class == "rogue":
            if level >= 1:
                return 2
            if level >= 6:
                return 4
        return 0

    def _get_class_saving_throws(self, char_class: str) -> Set[str]:
        """Get saving throw proficiencies for a class."""
        SAVES = {
            "fighter": {"strength", "constitution"},
            "rogue": {"dexterity", "intelligence"},
            # Add other classes...
        }
        return SAVES.get(char_class, set())


class FeatsRule(BaseValidationRule):
    """Validate feats according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.feats",
            category=RuleCategory.BASE,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate feats.

        2024 changes:
        - Level 1 feat from background
        - Heroic feats vs Epic feats distinction
        - Level requirements
        """
        issues = []
        data = character.character_data
        feats = data.get("feats", [])
        level = data.get("level", 1)

        # Check background feat
        background = data.get("background")
        if background and not any(f.get("source") == "background" for f in feats):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Missing background feat",
                    field="feats",
                    fix_available=False,
                )
            )

        # Check ASI/feat levels
        asi_levels = self._get_asi_levels(data.get("character_class"))
        expected_count = sum(1 for l in asi_levels if l <= level)
        actual_count = sum(1 for f in feats if f.get("source") == "asi")
        if actual_count > expected_count:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many ASI/feat selections ({actual_count}, expected {expected_count})",
                    field="feats",
                    fix_available=False,
                )
            )

        # Validate feat requirements
        for feat in feats:
            # Validate heroic vs epic
            if feat.get("epic", False) and level < 10:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Epic feat {feat['name']} requires level 10+",
                        field=f"feats.{feat['name']}",
                        fix_available=False,
                    )
                )

            # Validate prerequisites
            if not self._check_feat_prerequisites(feat, character):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Prerequisites not met for feat: {feat['name']}",
                        field=f"feats.{feat['name']}",
                        fix_available=False,
                    )
                )

        return self.create_result(character, passed=not issues, issues=issues)

    def _get_asi_levels(self, char_class: str) -> List[int]:
        """Get levels where ASI/feats are gained."""
        ASI_LEVELS = {
            "fighter": [4, 6, 8, 12, 14, 16, 19],
            "rogue": [4, 8, 10, 12, 16, 19],
            # Add other classes...
        }
        return ASI_LEVELS.get(char_class, [])


class SpellSystemRule(BaseValidationRule):
    """Validate spell system according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.spell_system",
            category=RuleCategory.BASE,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate spell system configuration.

        2024 changes:
        - Revised spell list organization
        - Updated preparation rules
        - Spell mastery changes
        - Epic boon effects on spellcasting
        """
        issues = []
        data = character.character_data

        # Skip if character has no spellcasting
        if not self._has_spellcasting(data):
            return self.create_result(character, passed=True)

        # Check spell slots
        if slot_issues := self._check_spell_slots(data):
            issues.extend(slot_issues)

        # Check spell list
        if list_issues := self._check_spell_list(data):
            issues.extend(list_issues)

        # Check preparation rules
        if prep_issues := self._check_spell_preparation(data):
            issues.extend(prep_issues)

        # Check concentration
        if concentration_issues := self._check_concentration(data):
            issues.extend(concentration_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _has_spellcasting(self, data: Dict) -> bool:
        """Check if character has spellcasting ability."""
        # Check class-based spellcasting
        char_class = data.get("character_class")
        SPELLCASTING_CLASSES = {
            "bard", "cleric", "druid", "sorcerer", "wizard",
            "artificer", "paladin", "ranger", "warlock"
        }
        if char_class in SPELLCASTING_CLASSES:
            return True

        # Check features granting spellcasting
        features = data.get("features", [])
        for feature in features:
            if "spellcasting" in feature.get("keywords", []):
                return True

        return False

    def _check_spell_slots(self, data: Dict) -> List[ValidationIssue]:
        """Validate spell slot configuration."""
        issues = []
        slots = data.get("spell_slots", {})
        char_class = data.get("character_class")
        level = data.get("level", 1)

        # Get expected slots
        expected_slots = self._get_expected_slots(char_class, level)

        # Check each spell level
        for slot_level, count in slots.items():
            # Validate slot level exists
            if slot_level not in expected_slots:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid spell slot level: {slot_level}",
                        field=f"spell_slots.{slot_level}",
                        fix_available=True,
                    )
                )
                continue

            # Check slot count
            if count > expected_slots[slot_level]:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Too many level {slot_level} spell slots",
                        field=f"spell_slots.{slot_level}",
                        fix_available=True,
                        metadata={
                            "expected": expected_slots[slot_level],
                            "current": count,
                        },
                    )
                )

        return issues

    def _check_spell_list(self, data: Dict) -> List[ValidationIssue]:
        """Validate character's spell list."""
        issues = []
        spells = data.get("spells", [])
        char_class = data.get("character_class")

        # Check each spell
        for spell in spells:
            # Validate spell exists in catalog
            if not self._is_valid_spell(spell["name"]):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid spell: {spell['name']}",
                        field=f"spells.{spell['name']}",
                        fix_available=False,
                    )
                )
                continue

            # Check spell is available to class
            if not self._is_spell_available(spell["name"], char_class):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Spell {spell['name']} not available to {char_class}",
                        field=f"spells.{spell['name']}",
                        fix_available=False,
                    )
                )

            # Check concentration tracking
            if spell.get("concentration") and not spell.get("concentration_target"):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Concentration spell {spell['name']} missing target",
                        field=f"spells.{spell['name']}.concentration_target",
                        fix_available=True,
                    )
                )

        return issues

    def _check_spell_preparation(self, data: Dict) -> List[ValidationIssue]:
        """Validate spell preparation rules."""
        issues = []
        prepared = data.get("prepared_spells", [])
        char_class = data.get("character_class")

        # Skip for classes that don't prepare spells
        if char_class in {"bard", "ranger", "sorcerer", "warlock"}:
            return issues

        # Calculate max prepared spells
        max_prepared = self._get_max_prepared_spells(data)
        if len(prepared) > max_prepared:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many prepared spells ({len(prepared)}, max {max_prepared})",
                    field="prepared_spells",
                    fix_available=True,
                    metadata={
                        "max_prepared": max_prepared,
                        "current": len(prepared),
                    },
                )
            )

        return issues

    def _check_concentration(self, data: Dict) -> List[ValidationIssue]:
        """Validate concentration rules."""
        issues = []
        active_spells = data.get("active_spells", [])

        # Check for multiple concentration
        concentration_spells = [
            s for s in active_spells 
            if s.get("concentration")
        ]
        if len(concentration_spells) > 1:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Multiple concentration spells active",
                    field="active_spells",
                    fix_available=True,
                )
            )

        return issues

    def _get_expected_slots(self, char_class: str, level: int) -> Dict[int, int]:
        """Get expected spell slots for class and level."""
        # This would be expanded with full 2024 spell slot tables
        if char_class == "wizard":
            return {
                1: min(4, level + 1),
                2: 2 if level >= 3 else 0,
                3: 2 if level >= 5 else 0,
                4: 1 if level >= 7 else 0,
                5: 1 if level >= 9 else 0,
                # Add higher levels...
            }
        # Add other classes...
        return {}

    def _get_max_prepared_spells(self, data: Dict) -> int:
        """Calculate maximum number of prepared spells."""
        char_class = data.get("character_class")
        level = data.get("level", 1)
        
        if char_class == "wizard":
            # Level + Intelligence modifier
            intelligence = data.get("ability_scores", {}).get("intelligence", 10)
            return level + ((intelligence - 10) // 2)
        # Add other classes...
        return 0

    def _is_valid_spell(self, spell_name: str) -> bool:
        """Check if spell exists in catalog."""
        # This would check against the spell catalog
        return True

    def _is_spell_available(self, spell_name: str, char_class: str) -> bool:
        """Check if spell is available to class."""
        # This would check against class spell lists
        return True


class MulticlassRule(BaseValidationRule):
    """Validate multiclassing according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.multiclass",
            category=RuleCategory.BASE,
            dependencies=["core.ability_scores", "core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate multiclassing.

        2024 changes:
        - Updated multiclassing prerequisites
        - Feature stacking rules
        - Spellcasting changes
        - Epic boon interactions
        """
        issues = []
        data = character.character_data
        classes = data.get("classes", [])

        # Skip if not multiclassed
        if len(classes) <= 1:
            return self.create_result(character, passed=True)

        # Validate prerequisites
        if prereq_issues := self._check_prerequisites(data):
            issues.extend(prereq_issues)

        # Validate feature stacking
        if feature_issues := self._check_feature_stacking(data):
            issues.extend(feature_issues)

        # Validate spellcasting
        if spell_issues := self._check_spellcasting(data):
            issues.extend(spell_issues)

        # Validate epic boons
        if len(classes) > 0 and sum(c["level"] for c in classes) == 20:
            if boon_issues := self._check_epic_boon(data):
                issues.extend(boon_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_prerequisites(self, data: Dict) -> List[ValidationIssue]:
        """Check multiclassing prerequisites."""
        issues = []
        classes = data.get("classes", [])
        scores = data.get("ability_scores", {})

        for class_info in classes:
            char_class = class_info["class"]
            if not self._meets_prerequisites(char_class, scores):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Ability scores do not meet prerequisites for {char_class}",
                        field=f"classes.{char_class}",
                        fix_available=False,
                    )
                )

        return issues

    def _check_feature_stacking(self, data: Dict) -> List[ValidationIssue]:
        """Check feature stacking rules."""
        issues = []
        classes = data.get("classes", [])
        features = data.get("features", [])

        # Check for duplicate features that don't stack
        NON_STACKING_FEATURES = {"unarmored_defense", "fighting_style"}
        for feature_name in NON_STACKING_FEATURES:
            count = sum(1 for f in features if f["name"] == feature_name)
            if count > 1:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Feature {feature_name} does not stack between classes",
                        field="features",
                        fix_available=True,
                    )
                )

        return issues

    def _check_spellcasting(self, data: Dict) -> List[ValidationIssue]:
        """Check multiclass spellcasting rules."""
        issues = []
        classes = data.get("classes", [])

        # Calculate total caster level
        caster_level = self._get_total_caster_level(classes)
        slots = data.get("spell_slots", {})

        # Check against combined spell slot table
        expected_slots = self._get_multiclass_slots(caster_level)
        for level, expected in expected_slots.items():
            current = slots.get(str(level), 0)
            if current > expected:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Too many level {level} spell slots for multiclass caster",
                        field=f"spell_slots.{level}",
                        fix_available=True,
                        metadata={
                            "expected": expected,
                            "current": current,
                        },
                    )
                )

        return issues

    def _check_epic_boon(self, data: Dict) -> List[ValidationIssue]:
        """Check epic boon validity for multiclass character."""
        issues = []
        epic_boon = data.get("epic_boon")

        # Ensure exactly one epic boon
        if not epic_boon:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Level 20 character must have exactly one epic boon",
                    field="epic_boon",
                    fix_available=False,
                )
            )
        elif len(epic_boon) > 1:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Character cannot have multiple epic boons",
                    field="epic_boon",
                    fix_available=True,
                )
            )

        return issues

    def _meets_prerequisites(self, char_class: str, scores: Dict) -> bool:
        """Check if ability scores meet multiclass prerequisites."""
        PREREQUISITES = {
            "artificer": {"intelligence": 13},
            "barbarian": {"strength": 13},
            "bard": {"charisma": 13},
            "cleric": {"wisdom": 13},
            "druid": {"wisdom": 13},
            "fighter": {"strength": 13, "dexterity": 13},
            "monk": {"dexterity": 13, "wisdom": 13},
            "paladin": {"strength": 13, "charisma": 13},
            "ranger": {"dexterity": 13, "wisdom": 13},
            "rogue": {"dexterity": 13},
            "sorcerer": {"charisma": 13},
            "warlock": {"charisma": 13},
            "wizard": {"intelligence": 13},
        }

        reqs = PREREQUISITES.get(char_class, {})
        return all(scores.get(ability, 0) >= score for ability, score in reqs.items())

    def _get_total_caster_level(self, classes: List[Dict]) -> int:
        """Calculate total caster level for multiclassing."""
        total = 0
        for class_info in classes:
            char_class = class_info["class"]
            level = class_info["level"]

            # Full casters
            if char_class in {"bard", "cleric", "druid", "sorcerer", "wizard"}:
                total += level
            # Half casters
            elif char_class in {"paladin", "ranger"}:
                total += level // 2
            # Third casters
            elif char_class in {"fighter", "rogue"}:  # Eldritch Knight/Arcane Trickster
                total += level // 3
            # Special cases
            elif char_class == "artificer":
                total += (level + 1) // 2
            # Warlocks are handled separately

        return total

    def _get_multiclass_slots(self, caster_level: int) -> Dict[int, int]:
        """Get multiclass spell slots for total caster level."""
        MULTICLASS_SLOTS = {
            1: {1: 2},
            2: {1: 3},
            3: {1: 4, 2: 2},
            4: {1: 4, 2: 3},
            5: {1: 4, 2: 3, 3: 2},
            6: {1: 4, 2: 3, 3: 3},
            7: {1: 4, 2: 3, 3: 3, 4: 1},
            8: {1: 4, 2: 3, 3: 3, 4: 2},
            9: {1: 4, 2: 3, 3: 3, 4: 3, 5: 1},
            10: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2},
            11: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            12: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1},
            13: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            14: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1},
            15: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            16: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1},
            17: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            18: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 1, 7: 1, 8: 1, 9: 1},
            19: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 1, 8: 1, 9: 1},
            20: {1: 4, 2: 3, 3: 3, 4: 3, 5: 2, 6: 2, 7: 2, 8: 1, 9: 1},
        }
        return MULTICLASS_SLOTS.get(caster_level, {})


class EquipmentRule(BaseValidationRule):
    """Validate equipment and armor according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.equipment",
            category=RuleCategory.BASE,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate equipment configuration.

        2024 changes:
        - Updated armor proficiency system
        - Weapon grouping changes
        - Equipment slot system
        - Magic item attunement changes
        """
        issues = []
        data = character.character_data

        # Check equipment slots
        if slot_issues := self._check_equipment_slots(data):
            issues.extend(slot_issues)

        # Validate armor
        if armor_issues := self._check_armor(data):
            issues.extend(armor_issues)

        # Validate weapons
        if weapon_issues := self._check_weapons(data):
            issues.extend(weapon_issues)

        # Check magic item attunement
        if attunement_issues := self._check_attunement(data):
            issues.extend(attunement_issues)

        # Check equipment load
        if load_issues := self._check_equipment_load(data):
            issues.extend(load_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_equipment_slots(self, data: Dict) -> List[ValidationIssue]:
        """Validate equipment slot usage."""
        issues = []
        slots = data.get("equipment_slots", {})
        items = data.get("equipment", [])

        # Check for items without valid slots
        VALID_SLOTS = {
            "head", "neck", "shoulders", "chest", "back", "arms",
            "hands", "waist", "legs", "feet", "ring1", "ring2",
        }

        for item in items:
            if slot := item.get("slot"):
                if slot not in VALID_SLOTS:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Invalid equipment slot: {slot}",
                            field=f"equipment.{item['name']}.slot",
                            fix_available=True,
                        )
                    )

                # Check if slot is already occupied
                if slots.get(slot):
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Equipment slot {slot} already occupied",
                            field=f"equipment.{item['name']}.slot",
                            fix_available=True,
                        )
                    )

        return issues

    def _check_armor(self, data: Dict) -> List[ValidationIssue]:
        """Validate armor usage."""
        issues = []
        armor = data.get("armor", {})
        proficiencies = data.get("proficiencies", {})

        if not armor:
            return issues

        # Check armor proficiency
        armor_type = armor.get("type")
        if armor_type and not self._has_armor_proficiency(armor_type, proficiencies):
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Not proficient with {armor_type} armor",
                    field="armor",
                    fix_available=False,
                )
            )

        # Check strength requirement
        if str_req := armor.get("strength_requirement"):
            strength = data.get("ability_scores", {}).get("strength", 0)
            if strength < str_req:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Strength score {strength} below armor requirement {str_req}",
                        field="armor",
                        fix_available=False,
                    )
                )

        return issues

    def _check_weapons(self, data: Dict) -> List[ValidationIssue]:
        """Validate weapon usage."""
        issues = []
        weapons = data.get("weapons", [])
        proficiencies = data.get("proficiencies", {})

        for weapon in weapons:
            # Check weapon proficiency
            if not self._has_weapon_proficiency(weapon, proficiencies):
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Not proficient with {weapon['name']}",
                        field=f"weapons.{weapon['name']}",
                        fix_available=False,
                    )
                )

            # Check weapon properties
            if properties := weapon.get("properties", []):
                if "two-handed" in properties and "versatile" in properties:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Weapon cannot be both two-handed and versatile",
                            field=f"weapons.{weapon['name']}.properties",
                            fix_available=True,
                        )
                    )

        return issues

    def _check_attunement(self, data: Dict) -> List[ValidationIssue]:
        """Validate magic item attunement."""
        issues = []
        attuned_items = [i for i in data.get("equipment", []) if i.get("attuned")]

        # Check attunement limit (usually 3)
        if len(attuned_items) > 3:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Too many attuned items",
                    field="equipment",
                    fix_available=True,
                    metadata={"max_attunement": 3},
                )
            )

        # Validate each attuned item
        for item in attuned_items:
            # Check attunement requirements
            if reqs := item.get("attunement_requirements", []):
                if not self._meets_attunement_requirements(reqs, data):
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"Does not meet attunement requirements for {item['name']}",
                            field=f"equipment.{item['name']}",
                            fix_available=False,
                        )
                    )

        return issues

    def _check_equipment_load(self, data: Dict) -> List[ValidationIssue]:
        """Check equipment load against carrying capacity."""
        issues = []
        equipment = data.get("equipment", [])
        strength = data.get("ability_scores", {}).get("strength", 10)

        # Calculate total weight
        total_weight = sum(item.get("weight", 0) for item in equipment)
        carrying_capacity = strength * 15  # Basic carrying capacity

        # Apply size adjustments
        size = data.get("size", "medium")
        if size == "tiny":
            carrying_capacity //= 2
        elif size in {"large", "huge", "gargantuan"}:
            carrying_capacity *= 2

        if total_weight > carrying_capacity:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Equipment weight exceeds carrying capacity",
                    field="equipment",
                    fix_available=False,
                    metadata={
                        "current_weight": total_weight,
                        "capacity": carrying_capacity,
                    },
                )
            )

        return issues

    def _has_armor_proficiency(self, armor_type: str, proficiencies: Dict) -> bool:
        """Check if character has required armor proficiency."""
        armor_profs = proficiencies.get("armor", [])
        return armor_type in armor_profs or "all" in armor_profs

    def _has_weapon_proficiency(self, weapon: Dict, proficiencies: Dict) -> bool:
        """Check if character has required weapon proficiency."""
        weapon_profs = proficiencies.get("weapons", [])
        name = weapon["name"]
        group = weapon.get("group", "")

        return (
            name in weapon_profs or
            group in weapon_profs or
            "all" in weapon_profs
        )

    def _meets_attunement_requirements(self, requirements: List[str], data: Dict) -> bool:
        """Check if character meets magic item attunement requirements."""
        for req in requirements:
            if req.startswith("class:"):
                if req[6:] != data.get("character_class"):
                    return False
            elif req.startswith("alignment:"):
                if req[10:] != data.get("alignment"):
                    return False
            elif req.startswith("ability:"):
                ability, score = req[8:].split(":")
                if data.get("ability_scores", {}).get(ability, 0) < int(score):
                    return False
        return True


class LanguageAndToolsRule(BaseValidationRule):
    """Validate languages and tool proficiencies according to 2024 rules."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.languages_tools",
            category=RuleCategory.BASE,
            dependencies=["core.class_progression"],
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate language and tool proficiencies.

        2024 changes:
        - Revised language system
        - Tool expertise system
        - Background integration
        - Cultural language learning
        """
        issues = []
        data = character.character_data

        # Check languages
        if language_issues := self._check_languages(data):
            issues.extend(language_issues)

        # Check tool proficiencies
        if tool_issues := self._check_tools(data):
            issues.extend(tool_issues)

        # Validate cultural languages
        if cultural_issues := self._check_cultural_languages(data):
            issues.extend(cultural_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_languages(self, data: Dict) -> List[ValidationIssue]:
        """Validate character languages."""
        issues = []
        languages = data.get("languages", [])
        char_class = data.get("character_class")
        background = data.get("background")

        # Calculate expected language count
        expected_count = self._get_expected_languages(data)
        if len(languages) > expected_count:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many languages ({len(languages)}, expected {expected_count})",
                    field="languages",
                    fix_available=True,
                    metadata={
                        "expected": expected_count,
                        "current": len(languages),
                    },
                )
            )

        # Validate language format (allow custom languages)
        for lang in languages:
            if not isinstance(lang, str) or not lang.strip():
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid language format: {lang}",
                        field="languages",
                        fix_available=False,
                    )
                )
            elif lang.startswith("custom.") and not lang[7:].strip():
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Custom language needs a name: {lang}",
                        field="languages",
                        fix_available=False,
                    )
                )

        # Check required languages
        required = {"common"}  # Common is always required
        missing = required - set(languages)
        if missing:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Missing required languages: {', '.join(missing)}",
                    field="languages",
                    fix_available=True,
                )
            )

        return issues

    def _check_tools(self, data: Dict) -> List[ValidationIssue]:
        """Validate tool proficiencies and expertise."""
        issues = []
        tools = data.get("tool_proficiencies", [])
        expertise = data.get("tool_expertise", [])
        char_class = data.get("character_class")
        background = data.get("background")

        # Calculate expected tool proficiencies
        expected_count = self._get_expected_tools(data)
        if len(tools) > expected_count:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many tool proficiencies ({len(tools)}, expected {expected_count})",
                    field="tool_proficiencies",
                    fix_available=True,
                    metadata={
                        "expected": expected_count,
                        "current": len(tools),
                    },
                )
            )

        # Validate tool types
        VALID_TOOLS = {
            # Artisan's tools
            "alchemist", "brewer", "calligrapher", "carpenter", "cartographer",
            "cobbler", "cook", "glassblower", "jeweler", "leatherworker",
            "mason", "painter", "potter", "smith", "tinker", "weaver",
            "woodcarver",
            # Gaming sets
            "dice", "dragonchess", "playing_cards", "three_dragon_ante",
            # Musical instruments
            "bagpipes", "drum", "dulcimer", "flute", "lute", "lyre",
            "horn", "pan_flute", "shawm", "viol",
            # Other tools
            "disguise", "forgery", "herbalism", "navigator", "poisoner",
            "thieves", "vehicles_land", "vehicles_water", "vehicles_air",
        }

        for tool in tools:
            if tool not in VALID_TOOLS:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Invalid tool: {tool}",
                        field="tool_proficiencies",
                        fix_available=False,
                    )
                )

        # Check expertise validity
        for tool in expertise:
            if tool not in tools:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message=f"Cannot have expertise in unproficient tool: {tool}",
                        field="tool_expertise",
                        fix_available=True,
                    )
                )

        # Check expertise count
        expected_expertise = self._get_expected_tool_expertise(data)
        if len(expertise) > expected_expertise:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Too many tool expertise ({len(expertise)}, expected {expected_expertise})",
                    field="tool_expertise",
                    fix_available=True,
                    metadata={
                        "expected": expected_expertise,
                        "current": len(expertise),
                    },
                )
            )

        return issues

    def _check_cultural_languages(self, data: Dict) -> List[ValidationIssue]:
        """Validate cultural language choices."""
        issues = []
        languages = data.get("languages", [])
        culture = data.get("culture")

        if not culture:
            return issues

        # Check cultural language requirements
        required_languages = self._get_cultural_languages(culture)
        missing = required_languages - set(languages)
        if missing:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Missing cultural languages: {', '.join(missing)}",
                    field="languages",
                    fix_available=True,
                    metadata={"missing_languages": list(missing)},
                )
            )

        return issues

    def _get_expected_languages(self, data: Dict) -> int:
        """Calculate expected number of languages."""
        count = 1  # Common language

        # Background languages
        count += 1  # All backgrounds give at least one additional language

        # Racial languages
        race = data.get("race")
        if race in {"elf", "dwarf", "gnome"}:
            count += 1

        # Intelligence bonus languages
        intelligence = data.get("ability_scores", {}).get("intelligence", 10)
        if (bonus := (intelligence - 10) // 2) > 0:
            count += bonus

        # Class features
        features = data.get("features", [])
        if "linguist" in {f["name"] for f in features}:
            count += 3

        return count

    def _get_expected_tools(self, data: Dict) -> int:
        """Calculate expected number of tool proficiencies."""
        count = 0

        # Background tools
        count += 1  # All backgrounds give at least one tool

        # Class tools
        char_class = data.get("character_class")
        if char_class == "artificer":
            count += 2
        elif char_class == "rogue":
            count += 1

        # Features granting tools
        features = data.get("features", [])
        for feature in features:
            if "tool_proficiency" in feature.get("grants", []):
                count += 1

        return count

    def _get_expected_tool_expertise(self, data: Dict) -> int:
        """Calculate expected number of tool expertise."""
        count = 0
        char_class = data.get("character_class")
        level = data.get("level", 1)

        # Class-based expertise
        if char_class == "artificer" and level >= 6:
            count += 2
        elif char_class == "rogue" and level >= 6:
            count += 1

        # Features granting expertise
        features = data.get("features", [])
        for feature in features:
            if "tool_expertise" in feature.get("grants", []):
                count += 1

        return count

    def _get_cultural_languages(self, culture: str) -> Set[str]:
        """Get required languages for a culture."""
        # This would be expanded with actual culture/language mappings
        CULTURE_LANGUAGES = {
            "high_elf": {"elvish"},
            "mountain_dwarf": {"dwarvish"},
            "forest_gnome": {"gnomish", "sylvan"},
            # Add other cultures...
        }
        return CULTURE_LANGUAGES.get(culture, set())


class CustomContentRule(BaseValidationRule):
    """Validate custom content while ensuring game balance."""

    def __init__(self) -> None:
        """Initialize rule."""
        super().__init__(
            rule_id="core.custom_content",
            category=RuleCategory.BASE,
            dependencies=[],  # This runs first to validate custom content
        )

    async def validate(self, character: Character) -> ValidationResult:
        """Validate custom content.

        This rule focuses on game balance and mechanical soundness rather than
        strict adherence to D&D canon. It allows for creative new content while
        ensuring the character remains balanced.
        """
        issues = []
        data = character.character_data

        # Validate custom species/race
        if race_issues := self._check_custom_race(data):
            issues.extend(race_issues)

        # Validate custom class
        if class_issues := self._check_custom_class(data):
            issues.extend(class_issues)

        # Validate custom features
        if feature_issues := self._check_custom_features(data):
            issues.extend(feature_issues)

        # Validate custom magic system
        if magic_issues := self._check_custom_magic(data):
            issues.extend(magic_issues)

        return self.create_result(character, passed=not issues, issues=issues)

    def _check_custom_race(self, data: Dict) -> List[ValidationIssue]:
        """Validate custom species/race for mechanical balance."""
        issues = []
        race = data.get("race", {})

        if not race.get("custom"):
            return issues

        # Validate ability score adjustments
        ability_bonuses = race.get("ability_score_increases", {})
        total_bonus = sum(ability_bonuses.values())
        if total_bonus > 3:  # Standard total for 2024 races
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Total ability score bonuses exceed standard amount",
                    field="race.ability_score_increases",
                    fix_available=False,
                    metadata={"max_total": 3, "current_total": total_bonus},
                )
            )

        # Check features for balance
        features = race.get("features", [])
        feature_count = len(features)
        if feature_count > 3:  # Most races have 2-3 major features
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Number of racial features exceeds standard amount",
                    field="race.features",
                    fix_available=False,
                    metadata={"recommended_max": 3, "current": feature_count},
                )
            )

        return issues

    def _check_custom_class(self, data: Dict) -> List[ValidationIssue]:
        """Validate custom class for mechanical balance."""
        issues = []
        char_class = data.get("character_class", {})

        if not char_class.get("custom"):
            return issues

        level = data.get("level", 1)
        features = char_class.get("features", [])

        # Check features per level
        features_by_level = {}
        for feature in features:
            lvl = feature.get("level", 1)
            features_by_level[lvl] = features_by_level.get(lvl, 0) + 1

        # Validate feature distribution
        for lvl in range(1, level + 1):
            count = features_by_level.get(lvl, 0)
            if count > 3:  # Most classes get 1-2 features per level
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Too many class features at level {lvl}",
                        field=f"character_class.features.level_{lvl}",
                        fix_available=False,
                        metadata={"recommended_max": 2, "current": count},
                    )
                )

        # Check combat capabilities
        if self._assess_combat_power(char_class) > 1.5:  # 1.0 is baseline
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Class combat capabilities may be overpowered",
                    field="character_class",
                    fix_available=False,
                )
            )

        # Validate spellcasting if present
        if spellcasting := char_class.get("spellcasting"):
            if spellcasting_issues := self._check_spellcasting_type(spellcasting, char_class):
                issues.extend(spellcasting_issues)

        return issues

    def _check_spellcasting_type(self, spellcasting: Dict, char_class: Dict) -> List[ValidationIssue]:
        """Validate spellcasting configuration for custom classes.

        Ensures custom spellcasting follows D&D's established patterns while allowing
        for creative variations within reasonable bounds.
        """
        issues = []

        # Validate caster type
        caster_type = spellcasting.get("caster_type")
        if not caster_type:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Spellcasting class must specify caster type (full/half/third)",
                    field="character_class.spellcasting.caster_type",
                    fix_available=False,
                )
            )
            return issues

        # Validate spellcasting ability
        ability = spellcasting.get("ability")
        if not ability or ability not in {"intelligence", "wisdom", "charisma"}:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Invalid spellcasting ability (must be intelligence, wisdom, or charisma)",
                    field="character_class.spellcasting.ability",
                    fix_available=False,
                )
            )

        # Validate spell preparation method
        prep_method = spellcasting.get("preparation_method")
        if not prep_method or prep_method not in {"prepared", "known"}:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Must specify preparation method (prepared or known)",
                    field="character_class.spellcasting.preparation_method",
                    fix_available=False,
                )
            )

        # Validate spell slot progression
        if slots := spellcasting.get("spell_slots"):
            slot_issues = self._check_slot_progression(slots, caster_type)
            issues.extend(slot_issues)

        # Validate spells known/prepared
        if spells := spellcasting.get("spells"):
            if prep_method == "known":
                known_issues = self._check_spells_known(spells, caster_type)
                issues.extend(known_issues)

        # Check special casting features
        if special := spellcasting.get("special_features", []):
            special_issues = self._check_special_casting(special, char_class)
            issues.extend(special_issues)

        return issues

    def _check_slot_progression(self, slots: Dict, caster_type: str) -> List[ValidationIssue]:
        """Validate spell slot progression for custom classes."""
        issues = []

        # Maximum spell level by caster type
        MAX_SPELL_LEVEL = {
            "full": 9,
            "half": 5,
            "third": 4,
            "custom": 9  # Allow custom progressions up to 9th level
        }

        max_level = MAX_SPELL_LEVEL.get(caster_type, 9)
        for level, level_slots in slots.items():
            try:
                spell_level = int(level)
                if spell_level > max_level:
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.ERROR,
                            message=f"{caster_type} casters cannot have level {spell_level} slots",
                            field=f"character_class.spellcasting.spell_slots.{level}",
                            fix_available=False,
                        )
                    )
            except ValueError:
                continue

        return issues

    def _check_spells_known(self, spells: Dict, caster_type: str) -> List[ValidationIssue]:
        """Validate spells known progression for known casters."""
        issues = []

        # Baseline spells known at max level
        BASELINE_KNOWN = {
            "full": 15,  # Like Sorcerer
            "half": 11,  # Like Ranger
            "third": 8,  # Like Arcane Trickster
            "custom": 20  # Allow some flexibility
        }

        max_known = spells.get("max_known", 0)
        baseline = BASELINE_KNOWN.get(caster_type, 15)
        if max_known > baseline * 1.5:  # Allow 50% more than baseline
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Number of spells known exceeds typical amount for {caster_type} caster",
                    field="character_class.spellcasting.spells.max_known",
                    fix_available=False,
                    metadata={"recommended_max": baseline, "current": max_known},
                )
            )

        return issues

    def _check_special_casting(self, special_features: List[str], char_class: Dict) -> List[ValidationIssue]:
        """Validate special spellcasting features."""
        issues = []
        power_score = 0

        # Score special features for power level
        FEATURE_SCORES = {
            "ritual_casting": 0.5,
            "bonus_cantrips": 0.3,
            "spell_flexibility": 0.5,  # Ability to swap spells more often
            "enhanced_slots": 1.0,  # Any feature that enhances slot usage
            "unique_resource": 0.8,  # Like Sorcery Points or Pact Magic
            "focus_benefits": 0.4,  # Special focus abilities
        }

        for feature in special_features:
            power_score += FEATURE_SCORES.get(feature, 0.5)

        # Warn if too many powerful features
        if power_score > 2.0:  # Allow 2-3 significant features
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.WARNING,
                    message="Special casting features may be too powerful in combination",
                    field="character_class.spellcasting.special_features",
                    fix_available=False,
                    metadata={"power_score": power_score, "recommended_max": 2.0},
                )
            )

        # Check for Pact Magic compatibility
        if "pact_magic" in special_features:
            other_slots = char_class.get("spellcasting", {}).get("spell_slots", {})
            if other_slots:
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.ERROR,
                        message="Pact Magic cannot be combined with standard spell slots",
                        field="character_class.spellcasting",
                        fix_available=False,
                    )
                )

        return issues

    def _check_custom_features(self, data: Dict) -> List[ValidationIssue]:
        """Validate custom features and abilities."""
        issues = []
        features = [f for f in data.get("features", []) if f.get("custom")]

        for feature in features:
            # Check for stacking bonuses
            if bonuses := feature.get("bonuses", {}):
                for bonus_type, value in bonuses.items():
                    if abs(value) > 5:  # Bounded accuracy protection
                        issues.append(
                            self.create_issue(
                                severity=ValidationSeverity.WARNING,
                                message=f"Large {bonus_type} bonus may break bounded accuracy",
                                field=f"features.{feature['name']}.bonuses",
                                fix_available=False,
                            )
                        )

            # Check for action economy impact
            if feature.get("grants_extra_action") or feature.get("grants_bonus_action"):
                if not feature.get("limited_use"):
                    issues.append(
                        self.create_issue(
                            severity=ValidationSeverity.WARNING,
                            message="Unlimited extra actions may be unbalanced",
                            field=f"features.{feature['name']}",
                            fix_available=False,
                        )
                    )

        return issues

    def _check_custom_magic(self, data: Dict) -> List[ValidationIssue]:
        """Validate custom magic systems and spells."""
        issues = []
        magic_system = data.get("magic_system", {})

        if not magic_system.get("custom"):
            return issues

        # Check resource system
        if resources := magic_system.get("resources", {}):
            # Validate against standard spell point values
            max_points = self._get_equivalent_spell_points(data)
            current_points = resources.get("max_points", 0)
            if current_points > max_points * 1.2:  # Allow 20% variance
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message="Magic resource pool may be too large",
                        field="magic_system.resources",
                        fix_available=False,
                        metadata={
                            "recommended_max": max_points,
                            "current": current_points,
                        },
                    )
                )

        # Check custom spells/abilities
        spells = [s for s in data.get("spells", []) if s.get("custom")]
        for spell in spells:
            if damage_issues := self._check_spell_damage(spell):
                issues.extend(damage_issues)

        return issues

    def _assess_combat_power(self, char_class: Dict) -> float:
        """Assess relative combat power of a class.

        Returns:
            Float representing power level (1.0 is baseline)
        """
        power = 1.0

        # Basic combat capabilities
        hit_die = char_class.get("hit_die", 8)
        power *= hit_die / 8.0

        # Armor and weapon proficiencies
        armor_profs = char_class.get("proficiencies", {}).get("armor", [])
        if "heavy" in armor_profs:
            power *= 1.2

        # Extra attacks
        attacks = char_class.get("extra_attacks", 0)
        power *= (1 + (attacks * 0.5))

        # Magic capability
        if char_class.get("spellcasting"):
            power *= 1.3

        return power

    def _check_spell_damage(self, spell: Dict) -> List[ValidationIssue]:
        """Check custom spell damage balance."""
        issues = []
        level = spell.get("level", 0)
        damage = spell.get("damage", {})

        # Base damage guidelines by spell level
        BASE_DAMAGE = {
            0: 5,   # Cantrip
            1: 12,  # 3d8
            2: 20,  # 5d8
            3: 28,  # 7d8
            4: 36,  # 9d8
            5: 44,  # 11d8
            # Scale appropriately for higher levels
        }

        if average_damage := damage.get("average", 0):
            base = BASE_DAMAGE.get(level, 44 + (level - 5) * 8)
            if average_damage > base * 1.5:  # Allow 50% variance
                issues.append(
                    self.create_issue(
                        severity=ValidationSeverity.WARNING,
                        message=f"Spell damage may be too high for level {level}",
                        field=f"spells.{spell['name']}.damage",
                        fix_available=False,
                        metadata={
                            "recommended_max": base,
                            "current": average_damage,
                        },
                    )
                )

        return issues

    def _get_equivalent_spell_points(self, data: Dict) -> int:
        """Calculate equivalent spell points for level/class."""
        # Standard spell point values by level
        SPELL_POINTS = {
            1: 4, 2: 6, 3: 14, 4: 17, 5: 27,
            6: 32, 7: 38, 8: 44, 9: 57, 10: 64,
            # Scale appropriately for higher levels
        }
        level = data.get("level", 1)
        return SPELL_POINTS.get(level, 64 + (level - 10) * 7)
