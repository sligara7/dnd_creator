"""Service for theme integration and content generation."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.api.theme import (ThemeApplicationRequest, ThemeApplicationResponse,
                            ThemeValidationRequest, ThemeValidationResponse)
from ..models.theme import Theme, WorldEffect


class ThemeIntegrationService:
    """Service for integrating themes with content generation."""

    def __init__(self, db: AsyncSession, llm_service=None):
        """Initialize the theme integration service.

        Args:
            db: Database session
            llm_service: Optional LLM service for content generation
        """
        self.db = db
        self.llm_service = llm_service

    async def apply_theme_to_content(
        self,
        request: ThemeApplicationRequest,
    ) -> ThemeApplicationResponse:
        """Apply a theme to content.

        Args:
            request: Theme application request

        Returns:
            Response containing modified content and changes
        """
        theme = await self._get_theme(request.theme_id)
        if not theme:
            raise ValueError("Theme not found")

        # Generate theme-specific prompts
        prompts = self._generate_theme_prompts(theme, request.content)

        # Use LLM service for content modification if available
        if self.llm_service:
            result = await self.llm_service.modify_content_for_theme(
                content=request.content,
                theme=theme,
                prompts=prompts,
                parameters=request.parameters or {},
            )
            return ThemeApplicationResponse(
                modified_content=result.content,
                changes=result.changes,
                theme_elements=result.theme_elements,
                confidence_score=result.confidence_score,
            )

        # Fallback to basic theme application
        modified_content = self._apply_basic_theme_rules(
            theme, request.content
        )
        return ThemeApplicationResponse(
            modified_content=modified_content,
            changes=["Basic theme rules applied"],
            theme_elements=self._extract_theme_elements(theme, modified_content),
            confidence_score=0.7,
        )

    async def validate_theme_consistency(
        self,
        request: ThemeValidationRequest,
    ) -> ThemeValidationResponse:
        """Validate if content is consistent with a theme.

        Args:
            request: Theme validation request

        Returns:
            Validation response with issues and suggestions
        """
        theme = await self._get_theme(request.theme_id)
        if not theme:
            raise ValueError("Theme not found")

        # Use LLM service for sophisticated validation if available
        if self.llm_service:
            result = await self.llm_service.validate_theme_consistency(
                content=request.content,
                theme=theme,
                context=request.context or {},
            )
            return ThemeValidationResponse(
                is_valid=result.is_valid,
                score=result.score,
                issues=result.issues,
                suggestions=result.suggestions,
            )

        # Fallback to basic validation
        issues = []
        for rule_name, rule in theme.validation_rules.items():
            if not self._check_theme_rule(rule, request.content):
                issues.append(f"Content violates theme rule: {rule_name}")

        return ThemeValidationResponse(
            is_valid=len(issues) == 0,
            score=0.8 if len(issues) == 0 else 0.4,
            issues=issues,
            suggestions=self._generate_theme_suggestions(theme, issues),
        )

    async def generate_themed_content(
        self,
        theme_id: UUID,
        content_type: str,
        parameters: Optional[Dict] = None,
    ) -> Dict:
        """Generate new content based on a theme.

        Args:
            theme_id: Theme ID
            content_type: Type of content to generate
            parameters: Optional generation parameters

        Returns:
            Generated content
        """
        theme = await self._get_theme(theme_id)
        if not theme:
            raise ValueError("Theme not found")

        # Use LLM service for content generation if available
        if self.llm_service:
            prompts = self._generate_theme_prompts(
                theme,
                {"content_type": content_type, **parameters or {}}
            )
            return await self.llm_service.generate_themed_content(
                theme=theme,
                content_type=content_type,
                prompts=prompts,
                parameters=parameters or {},
            )

        # Fallback to template-based generation
        return self._generate_from_template(theme, content_type, parameters)

    async def adapt_content_to_theme(
        self,
        content: Dict,
        source_theme_id: UUID,
        target_theme_id: UUID,
    ) -> Dict:
        """Adapt content from one theme to another.

        Args:
            content: Content to adapt
            source_theme_id: Original theme ID
            target_theme_id: Target theme ID

        Returns:
            Adapted content
        """
        source_theme = await self._get_theme(source_theme_id)
        target_theme = await self._get_theme(target_theme_id)
        if not source_theme or not target_theme:
            raise ValueError("One or both themes not found")

        # Use LLM service for sophisticated adaptation if available
        if self.llm_service:
            return await self.llm_service.adapt_content_between_themes(
                content=content,
                source_theme=source_theme,
                target_theme=target_theme,
            )

        # Fallback to basic adaptation
        return self._basic_theme_adaptation(
            content,
            source_theme,
            target_theme,
        )

    async def _get_theme(self, theme_id: UUID) -> Optional[Theme]:
        """Get a theme by ID."""
        query = select(Theme).where(
            and_(Theme.id == theme_id, Theme.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    def _generate_theme_prompts(self, theme: Theme, context: Dict) -> List[str]:
        """Generate theme-specific prompts for content generation/modification."""
        prompts = []
        
        # Add base theme prompts
        prompts.extend(theme.generation_prompts.get("base_prompts", []))
        
        # Add context-specific prompts
        content_type = context.get("content_type")
        if content_type:
            prompts.extend(
                theme.generation_prompts.get(f"{content_type}_prompts", [])
            )

        # Add tone-specific prompts
        prompts.extend(
            theme.generation_prompts.get(f"{theme.tone}_prompts", [])
        )

        # Add intensity modifiers
        intensity_modifiers = {
            "subtle": "with subtle and nuanced theme elements",
            "moderate": "with clear but balanced theme elements",
            "strong": "with prominent theme elements",
            "overwhelming": "with dominant and pervasive theme elements",
        }
        prompts.append(intensity_modifiers[theme.intensity])

        return prompts

    def _apply_basic_theme_rules(self, theme: Theme, content: Dict) -> Dict:
        """Apply basic theme rules to modify content."""
        modified = content.copy()

        # Apply style guide rules
        for element, style in theme.style_guide.items():
            if element in modified:
                if isinstance(style, str):
                    modified[element] = self._apply_style(
                        modified[element],
                        style
                    )
                elif isinstance(style, dict):
                    modified[element] = self._apply_style_dict(
                        modified[element],
                        style
                    )

        # Apply theme-specific transformations
        if "description" in modified:
            modified["description"] = self._enhance_description(
                modified["description"],
                theme
            )

        if "name" in modified:
            modified["name"] = self._theme_name(modified["name"], theme)

        return modified

    def _apply_style(self, text: str, style: str) -> str:
        """Apply a style transformation to text."""
        if style == "dramatic":
            return text.replace(".", "!")
        elif style == "mysterious":
            return text + "..."
        elif style == "formal":
            return text.replace("you", "one").replace("I", "we")
        return text

    def _apply_style_dict(self, value: any, style: Dict) -> any:
        """Apply a dictionary of style rules."""
        if isinstance(value, str):
            for rule, replacement in style.items():
                value = value.replace(rule, replacement)
        elif isinstance(value, dict):
            for key in value:
                if key in style:
                    value[key] = style[key]
        return value

    def _enhance_description(self, description: str, theme: Theme) -> str:
        """Enhance a description with theme elements."""
        theme_words = theme.attributes.get("theme_words", [])
        if theme_words and isinstance(description, str):
            for word in theme_words:
                if word.lower() not in description.lower():
                    description += f" {word}."
        return description

    def _theme_name(self, name: str, theme: Theme) -> str:
        """Add theme elements to a name."""
        prefix = theme.attributes.get("name_prefix", "")
        suffix = theme.attributes.get("name_suffix", "")
        if prefix:
            name = f"{prefix} {name}"
        if suffix:
            name = f"{name} {suffix}"
        return name

    def _check_theme_rule(self, rule: Dict, content: Dict) -> bool:
        """Check if content satisfies a theme rule."""
        rule_type = rule.get("type", "")
        
        if rule_type == "required_words":
            text = self._extract_text(content)
            required_words = rule.get("words", [])
            return all(word.lower() in text.lower() for word in required_words)
        
        elif rule_type == "tone":
            text = self._extract_text(content)
            tone_words = rule.get("tone_words", [])
            word_count = sum(
                1 for word in tone_words
                if word.lower() in text.lower()
            )
            return word_count >= rule.get("minimum_count", 1)
        
        elif rule_type == "style":
            return self._check_style_rules(content, rule.get("style_rules", {}))
        
        return True

    def _extract_text(self, content: Dict) -> str:
        """Extract all text from a content dictionary."""
        text_parts = []
        for value in content.values():
            if isinstance(value, str):
                text_parts.append(value)
            elif isinstance(value, dict):
                text_parts.append(self._extract_text(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        text_parts.append(item)
                    elif isinstance(item, dict):
                        text_parts.append(self._extract_text(item))
        return " ".join(text_parts)

    def _check_style_rules(self, content: Dict, style_rules: Dict) -> bool:
        """Check if content follows style rules."""
        for key, rules in style_rules.items():
            if key in content:
                value = content[key]
                if not self._check_style_value(value, rules):
                    return False
        return True

    def _check_style_value(self, value: any, rules: Dict) -> bool:
        """Check if a value follows style rules."""
        for rule, requirement in rules.items():
            if rule == "max_length" and len(str(value)) > requirement:
                return False
            elif rule == "min_length" and len(str(value)) < requirement:
                return False
            elif rule == "format" and not self._matches_format(str(value), requirement):
                return False
        return True

    def _matches_format(self, value: str, format_spec: str) -> bool:
        """Check if a value matches a format specification."""
        if format_spec == "title_case":
            return value.istitle()
        elif format_spec == "sentence_case":
            return value[0].isupper() if value else False
        elif format_spec == "all_caps":
            return value.isupper()
        return True

    def _extract_theme_elements(self, theme: Theme, content: Dict) -> List[str]:
        """Extract theme elements from content."""
        elements = []
        text = self._extract_text(content)
        
        # Check for theme words
        theme_words = theme.attributes.get("theme_words", [])
        elements.extend(
            word for word in theme_words
            if word.lower() in text.lower()
        )
        
        # Check for tone elements
        tone_words = theme.style_guide.get("tone_words", [])
        elements.extend(
            word for word in tone_words
            if word.lower() in text.lower()
        )
        
        return list(set(elements))

    def _generate_theme_suggestions(
        self,
        theme: Theme,
        issues: List[str],
    ) -> List[str]:
        """Generate suggestions to fix theme consistency issues."""
        suggestions = []
        
        for issue in issues:
            if "required_words" in issue:
                suggestions.append(
                    f"Include more {theme.type}-themed vocabulary"
                )
            elif "tone" in issue:
                suggestions.append(
                    f"Adjust tone to match {theme.tone} theme"
                )
            elif "style" in issue:
                suggestions.append(
                    "Follow theme style guide for formatting"
                )

        # Add theme-specific suggestions
        suggestions.extend(theme.style_guide.get("suggestions", []))
        
        return list(set(suggestions))

    def _generate_from_template(
        self,
        theme: Theme,
        content_type: str,
        parameters: Optional[Dict] = None,
    ) -> Dict:
        """Generate content from templates based on theme."""
        parameters = parameters or {}
        templates = theme.generation_prompts.get(f"{content_type}_templates", [])
        if not templates:
            return {"error": "No templates available for content type"}

        # Select template based on parameters
        template = self._select_template(templates, parameters)
        
        # Fill template with theme attributes and parameters
        content = template.copy()
        for key, value in content.items():
            if isinstance(value, str):
                content[key] = self._fill_template_text(
                    value,
                    theme,
                    parameters
                )
            elif isinstance(value, dict):
                content[key] = self._fill_template_dict(
                    value,
                    theme,
                    parameters
                )

        return content

    def _select_template(
        self,
        templates: List[Dict],
        parameters: Dict,
    ) -> Dict:
        """Select the best matching template based on parameters."""
        # Default to first template
        if not parameters or not templates:
            return templates[0]

        # Score templates based on parameter matches
        scored_templates = [
            (
                template,
                sum(
                    1 for key, value in parameters.items()
                    if template.get(key) == value
                )
            )
            for template in templates
        ]

        # Return template with highest score
        return max(scored_templates, key=lambda x: x[1])[0]

    def _fill_template_text(
        self,
        text: str,
        theme: Theme,
        parameters: Dict,
    ) -> str:
        """Fill a template text with theme and parameter values."""
        # Replace theme attributes
        for key, value in theme.attributes.items():
            text = text.replace(f"{{theme.{key}}}", str(value))

        # Replace parameters
        for key, value in parameters.items():
            text = text.replace(f"{{{key}}}", str(value))

        return text

    def _fill_template_dict(
        self,
        template: Dict,
        theme: Theme,
        parameters: Dict,
    ) -> Dict:
        """Fill a template dictionary with theme and parameter values."""
        filled = {}
        for key, value in template.items():
            if isinstance(value, str):
                filled[key] = self._fill_template_text(
                    value,
                    theme,
                    parameters
                )
            elif isinstance(value, dict):
                filled[key] = self._fill_template_dict(
                    value,
                    theme,
                    parameters
                )
            else:
                filled[key] = value
        return filled

    def _basic_theme_adaptation(
        self,
        content: Dict,
        source_theme: Theme,
        target_theme: Theme,
    ) -> Dict:
        """Perform basic theme adaptation of content."""
        adapted = content.copy()

        # Replace theme-specific vocabulary
        text = self._extract_text(adapted)
        for source_word in source_theme.attributes.get("theme_words", []):
            if source_word.lower() in text.lower():
                target_words = target_theme.attributes.get("theme_words", [])
                if target_words:
                    # Replace with corresponding target theme word
                    target_word = target_words[
                        hash(source_word) % len(target_words)
                    ]
                    text = text.replace(source_word, target_word)

        # Adjust tone
        if source_theme.tone != target_theme.tone:
            text = self._adjust_tone(
                text,
                source_theme.tone,
                target_theme.tone
            )

        # Reconstruct content with adapted text
        if "description" in adapted:
            adapted["description"] = text

        # Apply target theme style guide
        return self._apply_basic_theme_rules(target_theme, adapted)

    def _adjust_tone(
        self,
        text: str,
        source_tone: str,
        target_tone: str,
    ) -> str:
        """Adjust text tone for theme adaptation."""
        tone_adjustments = {
            ("dark", "light"): lambda t: t.replace("!", ".").replace("dark", "bright"),
            ("light", "dark"): lambda t: t.replace("bright", "dark") + "!",
            ("heroic", "gritty"): lambda t: t.replace("triumph", "survive"),
            ("gritty", "heroic"): lambda t: t.replace("survive", "triumph"),
        }

        adjustment = tone_adjustments.get((source_tone, target_tone))
        if adjustment:
            return adjustment(text)
        return text
