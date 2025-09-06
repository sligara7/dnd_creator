"""Content validation service."""
from uuid import UUID, uuid4
from typing import Dict, List, Optional, Protocol

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from llm_service.core.exceptions import ValidationError
from llm_service.core.cache import RateLimiter
from llm_service.services.openai import OpenAIClient
from llm_service.schemas.validation import (
    ValidationCategory,
    ValidationRequest,
    ValidationResponse,
    ValidationResult,
    ValidationRule,
    ValidationIssue,
)


class ValidationRule(Protocol):
    """Protocol for validation rule implementations."""

    async def validate(
        self,
        content: str,
        parameters: Dict[str, str],
        context: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """Validate content against this rule."""
        ...


class ThemeValidationRule:
    """Theme consistency validation."""

    def __init__(self, openai: OpenAIClient) -> None:
        self.openai = openai

    async def validate(
        self,
        content: str,
        parameters: Dict[str, str],
        context: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """Validate theme consistency."""
        # Create theme validation prompt
        prompt = f"""Analyze the following content for theme consistency:

Content:
{content}

Theme Parameters:
{parameters}

Provide:
1. Theme consistency score (0.0 to 1.0)
2. List of theme inconsistencies
3. Suggestions for improvement"""

        try:
            # Get analysis from LLM
            text, _ = await self.openai.generate_text(prompt)
            
            # TODO: Parse response to extract score and issues
            score = 0.8  # Example score
            issues = []
            if score < 0.9:
                issues.append(
                    ValidationIssue(
                        rule_id=uuid4(),
                        severity="warning",
                        message="Theme inconsistency detected",
                        suggestions=["Suggestion 1", "Suggestion 2"],
                    )
                )

            return ValidationResult(
                rule_id=uuid4(),
                passed=score >= 0.7,
                score=score,
                issues=issues,
            )
        except Exception as e:
            return ValidationResult(
                rule_id=uuid4(),
                passed=False,
                score=0.0,
                issues=[
                    ValidationIssue(
                        rule_id=uuid4(),
                        severity="error",
                        message=f"Theme validation failed: {str(e)}",
                    )
                ],
            )


class QualityValidationRule:
    """Content quality validation."""

    def __init__(self, openai: OpenAIClient) -> None:
        self.openai = openai

    async def validate(
        self,
        content: str,
        parameters: Dict[str, str],
        context: Optional[Dict[str, str]] = None,
    ) -> ValidationResult:
        """Validate content quality."""
        # Create quality validation prompt
        prompt = f"""Analyze the following content for quality:

Content:
{content}

Quality Parameters:
{parameters}

Check for:
1. Grammar and spelling
2. Clarity and readability
3. Completeness
4. Engagement and creativity"""

        try:
            # Get analysis from LLM
            text, _ = await self.openai.generate_text(prompt)
            
            # TODO: Parse response to extract score and issues
            score = 0.85  # Example score
            issues = []
            if score < 0.9:
                issues.append(
                    ValidationIssue(
                        rule_id=uuid4(),
                        severity="info",
                        message="Minor quality improvements suggested",
                        suggestions=["Suggestion 1", "Suggestion 2"],
                    )
                )

            return ValidationResult(
                rule_id=uuid4(),
                passed=score >= 0.7,
                score=score,
                issues=issues,
            )
        except Exception as e:
            return ValidationResult(
                rule_id=uuid4(),
                passed=False,
                score=0.0,
                issues=[
                    ValidationIssue(
                        rule_id=uuid4(),
                        severity="error",
                        message=f"Quality validation failed: {str(e)}",
                    )
                ],
            )


class ValidationService:
    """Service for validating generated content."""

    def __init__(
        self,
        openai: OpenAIClient,
        rate_limiter: RateLimiter,
        db: AsyncSession,
        logger: Optional[structlog.BoundLogger] = None,
    ) -> None:
        self.openai = openai
        self.rate_limiter = rate_limiter
        self.db = db
        self.logger = logger or structlog.get_logger()

        # Initialize rule implementations
        self.rules: Dict[ValidationCategory, ValidationRule] = {
            ValidationCategory.THEME: ThemeValidationRule(openai),
            ValidationCategory.QUALITY: QualityValidationRule(openai),
        }

    async def validate_content(
        self, request: ValidationRequest
    ) -> ValidationResponse:
        """Validate content against specified rules."""
        try:
            # Validate content against each rule
            results: List[ValidationResult] = []
            for rule in request.rules:
                if rule.category not in self.rules:
                    self.logger.warning(
                        "unknown_validation_rule",
                        category=rule.category,
                        rule_name=rule.name,
                    )
                    continue

                result = await self.rules[rule.category].validate(
                    request.content,
                    rule.parameters,
                    request.context,
                )
                results.append(result)

            # Calculate overall score and status
            required_scores = [
                r.score for r, rule in zip(results, request.rules)
                if rule.is_required
            ]
            overall_score = (
                sum(required_scores) / len(required_scores)
                if required_scores else 1.0
            )
            passed = all(
                r.passed for r, rule in zip(results, request.rules)
                if rule.is_required
            )

            # Create summary of validation results
            issues_by_severity = {
                "error": [],
                "warning": [],
                "info": [],
            }
            for result in results:
                for issue in result.issues:
                    issues_by_severity[issue.severity].append(issue)

            summary_parts = []
            if issues_by_severity["error"]:
                summary_parts.append(
                    f"{len(issues_by_severity['error'])} errors found"
                )
            if issues_by_severity["warning"]:
                summary_parts.append(
                    f"{len(issues_by_severity['warning'])} warnings found"
                )
            if issues_by_severity["info"]:
                summary_parts.append(
                    f"{len(issues_by_severity['info'])} suggestions found"
                )
            if not summary_parts:
                summary_parts.append("No issues found")

            summary = ". ".join(summary_parts)

            # Create response
            return ValidationResponse(
                content_id=uuid4(),
                metadata={
                    "content_type": request.content_type,
                    "rule_count": len(request.rules),
                    "content_length": len(request.content),
                },
                overall_score=overall_score,
                passed=passed,
                results=results,
                summary=summary,
            )

        except Exception as e:
            self.logger.error(
                "content_validation_failed",
                error=str(e),
                content_type=request.content_type,
            )
            raise ValidationError(
                message=f"Content validation failed: {str(e)}",
                details={
                    "content_type": request.content_type,
                    "content_length": len(request.content),
                },
            )

    async def initialize(self) -> None:
        """Initialize service resources."""
        pass

    async def cleanup(self) -> None:
        """Clean up service resources."""
        pass
