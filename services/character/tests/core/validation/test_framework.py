"""Tests for validation framework components."""
import pytest
from datetime import datetime
from uuid import uuid4

from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationResult,
    ValidationSeverity,
)
from character_service.core.validation.engine import DefaultValidationEngine
from character_service.core.validation.chain import ValidationChain
from character_service.domain.models import Character


class SimpleTestRule(BaseValidationRule):
    """Simple test rule for validation."""

    def __init__(self, rule_id: str, dependencies: list[str] = None) -> None:
        """Initialize rule."""
        super().__init__(rule_id, RuleCategory.BASE, dependencies)

    async def validate(self, character: Character) -> ValidationResult:
        """Simple validation that always passes."""
        return self.create_result(character, passed=True)


class FailingTestRule(BaseValidationRule):
    """Test rule that always fails."""

    def __init__(self, rule_id: str, dependencies: list[str] = None) -> None:
        """Initialize rule."""
        super().__init__(rule_id, RuleCategory.BASE, dependencies)

    async def validate(self, character: Character) -> ValidationResult:
        """Simple validation that always fails."""
        return self.create_result(
            character,
            passed=False,
            issues=[
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Test failure",
                    field="test",
                    fix_available=True,
                )
            ],
        )

    async def fix(self, character: Character) -> ValidationResult:
        """Simple fix that always succeeds."""
        return self.create_result(character, passed=True, fix_applied=True)


@pytest.fixture
def character() -> Character:
    """Create a test character."""
    return Character(
        id=uuid4(),
        character_data={
            "name": "Test Character",
            "level": 1,
            "character_class": "fighter",
            "ability_scores": {
                "strength": 16,
                "dexterity": 14,
                "constitution": 13,
                "intelligence": 12,
                "wisdom": 11,
                "charisma": 10,
            },
        },
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def engine() -> DefaultValidationEngine:
    """Create a test validation engine."""
    return DefaultValidationEngine()


@pytest.mark.asyncio
async def test_rule_registration(engine: DefaultValidationEngine):
    """Test rule registration."""
    rule = SimpleTestRule("test.simple")
    await engine.add_rule(rule)
    assert rule.rule_id in engine._rule_map

    # Test duplicate rule
    with pytest.raises(ValidationError):
        await engine.add_rule(rule)


@pytest.mark.asyncio
async def test_rule_dependencies(engine: DefaultValidationEngine):
    """Test rule dependency handling."""
    # Add base rule
    base_rule = SimpleTestRule("test.base")
    await engine.add_rule(base_rule)

    # Add dependent rule
    dependent_rule = SimpleTestRule("test.dependent", dependencies=["test.base"])
    await engine.add_rule(dependent_rule)

    # Try to add rule with missing dependency
    with pytest.raises(ValidationError):
        invalid_rule = SimpleTestRule("test.invalid", dependencies=["test.missing"])
        await engine.add_rule(invalid_rule)


@pytest.mark.asyncio
async def test_validation_chain():
    """Test validation chain execution."""
    # Create rules
    rules = [
        SimpleTestRule("test.1"),
        SimpleTestRule("test.2", dependencies=["test.1"]),
        SimpleTestRule("test.3", dependencies=["test.2"]),
    ]

    # Create chain
    chain = ValidationChain(rules)
    character = Character(
        id=uuid4(),
        character_data={"name": "Test"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Execute chain
    summary = await chain.execute(character)
    assert summary.passed
    assert len(summary.results) == 3


@pytest.mark.asyncio
async def test_auto_fix():
    """Test automatic fix application."""
    # Create rules with mix of passing and failing
    rules = [
        SimpleTestRule("test.pass"),
        FailingTestRule("test.fail"),
        SimpleTestRule("test.dependent", dependencies=["test.fail"]),
    ]

    # Create chain with auto-fix
    chain = ValidationChain(rules, auto_fix=True)
    character = Character(
        id=uuid4(),
        character_data={"name": "Test"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Execute chain
    summary = await chain.execute(character)
    assert summary.passed
    assert summary.fixes_applied == 1


@pytest.mark.asyncio
async def test_category_filtering(engine: DefaultValidationEngine):
    """Test rule category filtering."""
    # Add rules of different categories
    base_rule = SimpleTestRule("test.base")
    base_rule.category = RuleCategory.BASE
    await engine.add_rule(base_rule)

    theme_rule = SimpleTestRule("test.theme")
    theme_rule.category = RuleCategory.THEME
    await engine.add_rule(theme_rule)

    character = Character(
        id=uuid4(),
        character_data={"name": "Test"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )

    # Test base category only
    results = await engine.validate(character, categories=[RuleCategory.BASE])
    assert len(results) == 1
    assert results[0].rule_id == "test.base"
