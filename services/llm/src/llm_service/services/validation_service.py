"""Content validation service."""
from typing import Any, Dict, List, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.config import Settings
from ..core.exceptions import ValidationError
from ..core.cache import RateLimiter
from ..services.openai import OpenAIService
from .prompts.character import format_template as format_character_prompt
from .prompts.image import (
    get_character_portrait_prompt,
    get_location_prompt,
    get_item_prompt,
    get_style_transfer_prompt,
    get_enhancement_prompt,
)


class ContentValidation:
    """Content validation results."""

    def __init__(
        self,
        content_type: str,
        content_id: UUID,
        is_valid: bool,
        score: float,
        issues: List[Dict[str, Any]],
        suggestions: List[str],
    ):
        self.content_type = content_type
        self.content_id = content_id
        self.is_valid = is_valid
        self.score = score
        self.issues = issues
        self.suggestions = suggestions


class ValidationService:
    """Service for validating generated content."""

    def __init__(
        self,
        settings: Settings,
        openai: OpenAIService,
        rate_limiter: RateLimiter,
        db: AsyncSession,
        logger: Optional[structlog.BoundLogger] = None,
    ):
        self.settings = settings
        self.openai = openai
        self.rate_limiter = rate_limiter
        self.db = db
        self.logger = logger or structlog.get_logger()

    def _create_validation_prompt(
        self, content: str, content_type: str, parameters: Dict[str, Any]
    ) -> str:
        """Create prompt for content validation."""
        prompt = f"""Analyze and validate the following generated {content_type} content.
Please assess the following aspects:

1. Coherence and Quality:
   - Internal consistency
   - Logical flow
   - Writing quality
   - Detail richness
   - Language appropriateness

2. Theme Consistency:
   - Alignment with specified theme
   - Tone appropriateness
   - Style consistency
   - Genre conventions

3. Technical Requirements:
   - Completeness
   - Structure conformance
   - Required elements
   - Format validity

Content Parameters:
{parameters}

Content to Validate:
{content}

Provide a detailed analysis with:
1. Overall validity (true/false)
2. Quality score (0.0 to 1.0)
3. List of issues found
4. Improvement suggestions

Format the response as JSON with the following schema:
{{
    "is_valid": boolean,
    "score": float,
    "issues": [
        {{
            "category": "coherence|theme|technical",
            "severity": "error|warning|info",
            "description": "string",
            "impact": "high|medium|low"
        }}
    ],
    "suggestions": [
        "string"
    ]
}}"""

        return prompt

    async def validate_character_content(
        self,
        content: str,
        content_type: str,
        character_id: UUID,
        parameters: Dict[str, Any],
    ) -> ContentValidation:
        """Validate character content."""
        try:
            # Check rate limit
            await self.rate_limiter.check_text_limit("validation")

            # Create validation prompt
            prompt = self._create_validation_prompt(content, content_type, parameters)
            prompt += "\n\nAdditional Character Content Validation:\n"
            prompt += "4. D&D 5e (2024) Rules:\n"
            prompt += "   - Rule consistency\n"
            prompt += "   - Balance considerations\n"
            prompt += "   - Character appropriateness\n"
            prompt += "   - Level-appropriate content\n"

            # Get validation analysis
            completion = await self.openai.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse validation result
            result = completion.choices[0].text.strip()
            validation = eval(result)  # Safe as we control the input format

            return ContentValidation(
                content_type=content_type,
                content_id=character_id,
                is_valid=validation["is_valid"],
                score=validation["score"],
                issues=validation["issues"],
                suggestions=validation["suggestions"],
            )

        except Exception as e:
            self.logger.error(
                "character_content_validation_failed",
                error=str(e),
                character_id=str(character_id),
                content_type=content_type,
            )
            raise ValidationError(f"Content validation failed: {str(e)}")

    async def validate_theme_consistency(
        self,
        content: str,
        theme_context: Dict[str, Any],
        content_type: str,
        content_id: UUID,
    ) -> ContentValidation:
        """Validate theme consistency."""
        try:
            # Check rate limit
            await self.rate_limiter.check_text_limit("validation")

            # Create theme validation prompt
            prompt = f"""Analyze theme consistency for the following content.

Theme Context:
{theme_context}

Content Type: {content_type}
Content:
{content}

Evaluate:
1. Theme alignment (0.0 to 1.0)
2. Style consistency
3. Tone appropriateness
4. Genre conventions
5. Visual/narrative coherence

Format the response as JSON with:
{{
    "is_valid": boolean,
    "score": float,
    "issues": [
        {{
            "category": "theme|style|tone|genre",
            "severity": "error|warning|info",
            "description": "string",
            "impact": "high|medium|low"
        }}
    ],
    "suggestions": [
        "string"
    ]
}}"""

            # Get theme validation
            completion = await self.openai.generate_text(
                prompt=prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse validation result
            result = completion.choices[0].text.strip()
            validation = eval(result)

            return ContentValidation(
                content_type=content_type,
                content_id=content_id,
                is_valid=validation["is_valid"],
                score=validation["score"],
                issues=validation["issues"],
                suggestions=validation["suggestions"],
            )

        except Exception as e:
            self.logger.error(
                "theme_validation_failed",
                error=str(e),
                content_id=str(content_id),
                content_type=content_type,
            )
            raise ValidationError(f"Theme validation failed: {str(e)}")

    async def validate_image_quality(
        self,
        image_data: str,
        prompt: str,
        parameters: Dict[str, Any],
        image_type: str,
        image_id: UUID,
    ) -> ContentValidation:
        """Validate image generation quality."""
        try:
            # Check rate limit
            await self.rate_limiter.check_text_limit("validation")

            # Create image validation prompt
            validation_prompt = f"""Analyze the quality of the generated image.

Generation Parameters:
- Type: {image_type}
- Prompt: {prompt}
- Model Parameters: {parameters}

Evaluate:
1. Visual quality (0.0 to 1.0)
2. Prompt alignment
3. Style consistency
4. Technical aspects:
   - Resolution
   - Composition
   - Detail level
   - Artifacts

Format the response as JSON with:
{{
    "is_valid": boolean,
    "score": float,
    "issues": [
        {{
            "category": "quality|alignment|style|technical",
            "severity": "error|warning|info",
            "description": "string",
            "impact": "high|medium|low"
        }}
    ],
    "suggestions": [
        "string"
    ]
}}"""

            # Get image validation
            completion = await self.openai.generate_text(
                prompt=validation_prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse validation result
            result = completion.choices[0].text.strip()
            validation = eval(result)

            return ContentValidation(
                content_type=image_type,
                content_id=image_id,
                is_valid=validation["is_valid"],
                score=validation["score"],
                issues=validation["issues"],
                suggestions=validation["suggestions"],
            )

        except Exception as e:
            self.logger.error(
                "image_validation_failed",
                error=str(e),
                image_id=str(image_id),
                image_type=image_type,
            )
            raise ValidationError(f"Image validation failed: {str(e)}")

    async def validate_enhancement_quality(
        self,
        original_image: str,
        enhanced_image: str,
        enhancements: List[str],
        enhancement_params: Dict[str, Any],
        image_id: UUID,
    ) -> ContentValidation:
        """Validate image enhancement quality."""
        try:
            # Check rate limit
            await self.rate_limiter.check_text_limit("validation")

            # Create enhancement validation prompt
            validation_prompt = f"""Compare original and enhanced images.

Enhancements Applied:
{enhancements}

Enhancement Parameters:
{enhancement_params}

Evaluate:
1. Enhancement effectiveness (0.0 to 1.0)
2. Quality improvement
3. Content preservation
4. Technical aspects:
   - Artifact introduction
   - Detail preservation
   - Natural appearance
   - Enhancement balance

Format the response as JSON with:
{{
    "is_valid": boolean,
    "score": float,
    "issues": [
        {{
            "category": "effectiveness|quality|preservation|technical",
            "severity": "error|warning|info",
            "description": "string",
            "impact": "high|medium|low"
        }}
    ],
    "suggestions": [
        "string"
    ]
}}"""

            # Get enhancement validation
            completion = await self.openai.generate_text(
                prompt=validation_prompt,
                max_tokens=1000,
                temperature=0.3,
            )

            # Parse validation result
            result = completion.choices[0].text.strip()
            validation = eval(result)

            return ContentValidation(
                content_type="enhancement",
                content_id=image_id,
                is_valid=validation["is_valid"],
                score=validation["score"],
                issues=validation["issues"],
                suggestions=validation["suggestions"],
            )

        except Exception as e:
            self.logger.error(
                "enhancement_validation_failed",
                error=str(e),
                image_id=str(image_id),
            )
            raise ValidationError(f"Enhancement validation failed: {str(e)}")
