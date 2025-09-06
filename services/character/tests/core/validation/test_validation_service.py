"""Tests for validation service."""
import pytest
from datetime import datetime
from unittest.mock import MagicMock
from uuid import uuid4

from sqlalchemy.ext.asyncio import AsyncSession

from character_service.core.validation import (
    BaseValidationRule,
    RuleCategory,
    ValidationResult,
    ValidationSeverity,
)
from character_service.domain.models import Character, ValidationState
from character_service.domain.validation import ValidationService
from character_service.infrastructure.repositories.character import CharacterRepository
from character_service.infrastructure.repositories.validation import ValidationStateRepository


class MockRule(BaseValidationRule):
    """Mock validation rule for testing."""

    def __init__(self, rule_id: str, should_pass: bool = True) -> None:
        """Initialize rule."""
        super().__init__(rule_id, RuleCategory.BASE)
        self.should_pass = should_pass
        self.validate_called = False
        self.fix_called = False

    async def validate(self, character: Character) -> ValidationResult:
        """Mock validation."""
        self.validate_called = True
        issues = []
        if not self.should_pass:
            issues.append(
                self.create_issue(
                    severity=ValidationSeverity.ERROR,
                    message="Test failure",
                    field="test",
                    fix_available=True,
                )
            )
        return self.create_result(character, passed=self.should_pass, issues=issues)

    async def fix(self, character: Character) -> ValidationResult:
        """Mock fix."""
        self.fix_called = True
        return self.create_result(character, passed=True, fix_applied=True)


@pytest.fixture
def character() -> Character:
    """Create a test character."""
    return Character(
        id=uuid4(),
        character_data={"name": "Test"},
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )


@pytest.fixture
def db() -> AsyncSession:
    """Create mock database session."""
    return MagicMock(spec=AsyncSession)


@pytest.fixture
def char_repo(character: Character) -> CharacterRepository:
    """Create mock character repository."""
    repo = MagicMock(spec=CharacterRepository)
    repo.get.return_value = character
    return repo


@pytest.fixture
def validation_repo() -> ValidationStateRepository:
    """Create mock validation repository."""
    return MagicMock(spec=ValidationStateRepository)


@pytest.fixture
def validation_service(
    db: AsyncSession,
    char_repo: CharacterRepository,
    validation_repo: ValidationStateRepository,
) -> ValidationService:
    """Create validation service."""
    return ValidationService(
        db=db,
        char_repository=char_repo,
        validation_repository=validation_repo,
        cache_ttl=1,  # Short TTL for testing
    )


@pytest.mark.asyncio
async def test_validate_character(
    validation_service: ValidationService,
    character: Character,
):
    """Test basic character validation."""
    # Add test rule
    rule = MockRule("test.rule")
    await validation_service.add_rule(rule)

    # Test validation
    result = await validation_service.validate_character(character.id)
    assert result.passed
    assert rule.validate_called

    # Test cache
    rule.validate_called = False
    result = await validation_service.validate_character(character.id)
    assert result.passed
    assert not rule.validate_called  # Should use cache

    # Test force revalidate
    result = await validation_service.validate_character(
        character.id, force_revalidate=True
    )
    assert result.passed
    assert rule.validate_called  # Should bypass cache


@pytest.mark.asyncio
async def test_category_filtering(
    validation_service: ValidationService,
    character: Character,
):
    """Test rule category filtering."""
    # Add rules of different categories
    base_rule = MockRule("test.base")
    base_rule.category = RuleCategory.BASE
    await validation_service.add_rule(base_rule)

    theme_rule = MockRule("test.theme")
    theme_rule.category = RuleCategory.THEME
    await validation_service.add_rule(theme_rule)

    # Test base category only
    result = await validation_service.validate_character(
        character.id, categories=[RuleCategory.BASE]
    )
    assert base_rule.validate_called
    assert not theme_rule.validate_called

    # Test theme category only
    base_rule.validate_called = False
    result = await validation_service.validate_character(
        character.id, categories=[RuleCategory.THEME]
    )
    assert not base_rule.validate_called
    assert theme_rule.validate_called


@pytest.mark.asyncio
async def test_auto_fix(
    validation_service: ValidationService,
    character: Character,
):
    """Test automatic fix application."""
    # Add failing rule with fix
    rule = MockRule("test.rule", should_pass=False)
    await validation_service.add_rule(rule)

    # Test without auto-fix
    result = await validation_service.validate_character(character.id)
    assert not result.passed
    assert not rule.fix_called

    # Test with auto-fix
    result = await validation_service.validate_character(character.id, auto_fix=True)
    assert result.passed
    assert rule.fix_called


@pytest.mark.asyncio
async def test_bulk_validation(
    validation_service: ValidationService,
    character: Character,
):
    """Test bulk validation."""
    # Add test rule
    rule = MockRule("test.rule")
    await validation_service.add_rule(rule)

    # Test bulk validation
    char_ids = [uuid4(), uuid4(), uuid4()]
    results = await validation_service.bulk_validate(char_ids)

    # Should have results for each character
    assert len(results) == 3
    for result in results.values():
        assert result.passed


@pytest.mark.asyncio
async def test_validation_state_tracking(
    validation_service: ValidationService,
    validation_repo: ValidationStateRepository,
    character: Character,
):
    """Test validation state tracking."""
    # Add test rule
    rule = MockRule("test.rule", should_pass=False)
    await validation_service.add_rule(rule)

    # Run validation
    result = await validation_service.validate_character(character.id)

    # Check state was stored
    validation_repo.create.assert_called_once()
    state: ValidationState = validation_repo.create.call_args[0][0]
    assert state.character_id == character.id
    assert not state.passed
    assert state.error_count == 1
    assert len(state.details) == 1
    assert state.details[0]["rule_id"] == "test.rule"
