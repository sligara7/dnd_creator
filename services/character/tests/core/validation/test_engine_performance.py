"""Tests for validation engine performance optimizations."""
import asyncio
from typing import Dict, List, Optional
from uuid import UUID, uuid4

import pytest

from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationEngine,
    ValidationIssue,
    ValidationResult,
    ValidationSeverity,
)
from character_service.core.validation.engine import DefaultValidationEngine
from character_service.domain.models import Character


class MockRule(BaseValidationRule):
    """Mock validation rule for testing."""

    def __init__(
        self,
        rule_id: str,
        dependencies: Optional[List[str]] = None,
        validation_time: float = 0.1,
    ):
        """Initialize rule.

        Args:
            rule_id: Rule ID
            dependencies: Optional list of dependencies
            validation_time: Time in seconds to simulate validation work
        """
        super().__init__(rule_id, RuleCategory.BASE, dependencies)
        self.validation_time = validation_time
        self.validation_count = 0

    async def validate(self, character: Character) -> ValidationResult:
        """Mock validation that takes specified time."""
        self.validation_count += 1
        await asyncio.sleep(self.validation_time)
        return self.create_result(character, passed=True)


@pytest.fixture
def engine() -> ValidationEngine:
    """Create a validation engine for testing."""
    return DefaultValidationEngine()


@pytest.fixture
async def character() -> Character:
    """Create a test character."""
    return Character(
        id=uuid4(),
        character_data={
            "ability_scores": {"strength": 10, "dexterity": 12},
            "class_features": ["feature1", "feature2"],
        },
    )


@pytest.fixture
async def engine_with_rules(engine: ValidationEngine) -> ValidationEngine:
    """Set up engine with test rules."""
    # Independent rules
    await engine.add_rule(MockRule("rule1"))
    await engine.add_rule(MockRule("rule2"))
    await engine.add_rule(MockRule("rule3"))

    # Rules with dependencies
    await engine.add_rule(MockRule("rule4", dependencies=["rule1"]))
    await engine.add_rule(MockRule("rule5", dependencies=["rule2", "rule3"]))
    await engine.add_rule(MockRule("rule6", dependencies=["rule4", "rule5"]))

    return engine


@pytest.mark.asyncio
async def test_parallel_execution(engine_with_rules: ValidationEngine, character: Character):
    """Test that rules are executed in parallel when possible."""
    start_time = asyncio.get_event_loop().time()

    results = await engine_with_rules.validate(character)

    end_time = asyncio.get_event_loop().time()
    execution_time = end_time - start_time

    # Independent rules should run in parallel
    # If running sequentially, it would take 0.6s (3 rules * 0.2s)
    # In parallel, it should take ~0.2s plus overhead
    assert execution_time < 0.4, "Parallel execution not working efficiently"
    assert len(results) == 6, "Not all rules were executed"


@pytest.mark.asyncio
async def test_result_caching(engine_with_rules: ValidationEngine, character: Character):
    """Test that validation results are cached and reused."""
    # First validation
    await engine_with_rules.validate(character)

    # Change rules to count validations
    rules = [rule for rule in engine_with_rules._rules if isinstance(rule, MockRule)]

    # Second validation without changes
    await engine_with_rules.validate(character, incremental=True)

    # Check that no rules were re-run
    for rule in rules:
        assert rule.validation_count == 1, "Rule was re-run unnecessarily"


@pytest.mark.asyncio
async def test_incremental_validation(engine_with_rules: ValidationEngine, character: Character):
    """Test that only necessary rules are re-run when character changes."""
    # Initial validation
    await engine_with_rules.validate(character)

    # Modify character ability scores
    character.character_data["ability_scores"]["strength"] = 15

    # Get rules for counting validations
    rules = {
        rule.rule_id: rule
        for rule in engine_with_rules._rules
        if isinstance(rule, MockRule)
    }

    # Run incremental validation
    await engine_with_rules.validate(character, incremental=True)

    # Only rules touching ability scores and their dependents should run
    assert rules["rule1"].validation_count <= 2, "Unrelated rule was re-run"
    assert rules["rule2"].validation_count == 1, "Unrelated rule was re-run"


@pytest.mark.asyncio
async def test_dependency_batching(engine: ValidationEngine, character: Character):
    """Test that rules are batched efficiently based on dependencies."""
    # Create rules with various dependency chains
    await engine.add_rule(MockRule("a1", validation_time=0.1))
    await engine.add_rule(MockRule("a2", validation_time=0.1))
    await engine.add_rule(MockRule("b1", dependencies=["a1"], validation_time=0.1))
    await engine.add_rule(MockRule("b2", dependencies=["a2"], validation_time=0.1))
    await engine.add_rule(MockRule("c1", dependencies=["b1", "b2"], validation_time=0.1))

    start_time = asyncio.get_event_loop().time()
    results = await engine.validate(character)
    execution_time = asyncio.get_event_loop().time() - start_time

    # Should execute in 3 batches:
    # 1. a1, a2 (parallel)
    # 2. b1, b2 (parallel)
    # 3. c1
    # Total time should be ~0.3s plus overhead
    assert execution_time < 0.5, "Rules not batched efficiently"
    assert len(results) == 5, "Not all rules executed"


@pytest.mark.asyncio
async def test_error_handling(engine: ValidationEngine, character: Character):
    """Test that rule execution errors are handled gracefully."""

    class ErrorRule(BaseValidationRule):
        async def validate(self, character: Character) -> ValidationResult:
            raise ValueError("Test error")

    await engine.add_rule(ErrorRule("error_rule", RuleCategory.BASE))
    
    # Should not raise exception
    results = await engine.validate(character)
    
    # Should return error result
    assert len(results) == 1
    assert not results[0].passed
    assert "Test error" in results[0].issues[0].message


@pytest.mark.asyncio
async def test_cache_invalidation(engine_with_rules: ValidationEngine, character: Character):
    """Test that cache is invalidated when rules change."""
    # Initial validation
    await engine_with_rules.validate(character)

    # Add new rule
    await engine_with_rules.add_rule(MockRule("new_rule"))

    # Get all rules for counting
    rules = [rule for rule in engine_with_rules._rules if isinstance(rule, MockRule)]

    # Validate again
    await engine_with_rules.validate(character, incremental=True)

    # All rules should run again since cache was invalidated
    for rule in rules:
        assert rule.validation_count == 2, "Rule not re-run after cache invalidation"
