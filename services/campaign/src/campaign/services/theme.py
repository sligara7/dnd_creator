"""Service layer for theme management."""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from uuid import UUID

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.api.theme import (ThemeCreate, ThemeUpdate, ThemeValidationRequest,
                            ThemeValidationResponse)
from ..models.theme import Theme, ThemeCombination, theme_combinations


class ThemeService:
    """Service for managing campaign themes."""

    def __init__(self, db: AsyncSession, llm_service=None):
        """Initialize the theme service.

        Args:
            db: Database session
            llm_service: Optional LLM service for content generation
        """
        self.db = db
        self.llm_service = llm_service

    async def create_theme(self, theme_data: ThemeCreate) -> Theme:
        """Create a new theme.

        Args:
            theme_data: Theme creation data

        Returns:
            The created theme
        """
        theme = Theme(**theme_data.dict())
        self.db.add(theme)
        await self.db.flush()
        await self.db.refresh(theme)
        return theme

    async def get_theme(self, theme_id: UUID) -> Optional[Theme]:
        """Get a theme by ID.

        Args:
            theme_id: Theme ID

        Returns:
            The theme if found, None otherwise
        """
        query = select(Theme).where(
            and_(Theme.id == theme_id, Theme.is_deleted == False)
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def list_themes(
        self,
        type_filter: Optional[str] = None,
        tone_filter: Optional[str] = None,
    ) -> List[Theme]:
        """List all themes, optionally filtered.

        Args:
            type_filter: Optional theme type to filter by
            tone_filter: Optional theme tone to filter by

        Returns:
            List of matching themes
        """
        query = select(Theme).where(Theme.is_deleted == False)
        
        if type_filter:
            query = query.where(Theme.type == type_filter)
        if tone_filter:
            query = query.where(Theme.tone == tone_filter)

        result = await self.db.execute(query)
        return result.scalars().all()

    async def update_theme(
        self, theme_id: UUID, theme_data: ThemeUpdate
    ) -> Optional[Theme]:
        """Update a theme.

        Args:
            theme_id: Theme ID
            theme_data: Theme update data

        Returns:
            The updated theme if found, None otherwise
        """
        theme = await self.get_theme(theme_id)
        if not theme:
            return None

        for key, value in theme_data.dict(exclude_unset=True).items():
            setattr(theme, key, value)
        theme.updated_at = datetime.utcnow()
        
        await self.db.flush()
        await self.db.refresh(theme)
        return theme

    async def delete_theme(self, theme_id: UUID) -> bool:
        """Soft delete a theme.

        Args:
            theme_id: Theme ID

        Returns:
            True if theme was deleted, False if not found
        """
        theme = await self.get_theme(theme_id)
        if not theme:
            return False

        theme.is_deleted = True
        theme.deleted_at = datetime.utcnow()
        theme.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return True

    async def combine_themes(
        self,
        primary_theme_id: UUID,
        secondary_theme_id: UUID,
        weight: float = 1.0,
    ) -> bool:
        """Combine two themes.

        Args:
            primary_theme_id: Primary theme ID
            secondary_theme_id: Secondary theme ID
            weight: Combination weight (0.0 to 1.0)

        Returns:
            True if combination was created, False if themes not found
        """
        # Verify both themes exist
        primary = await self.get_theme(primary_theme_id)
        secondary = await self.get_theme(secondary_theme_id)
        if not primary or not secondary:
            return False

        # Check if combination already exists
        query = select(theme_combinations).where(
            and_(
                theme_combinations.c.primary_theme_id == primary_theme_id,
                theme_combinations.c.secondary_theme_id == secondary_theme_id,
            )
        )
        result = await self.db.execute(query)
        if result.first():
            # Update weight if combination exists
            await self.db.execute(
                theme_combinations.update()
                .where(
                    and_(
                        theme_combinations.c.primary_theme_id == primary_theme_id,
                        theme_combinations.c.secondary_theme_id == secondary_theme_id,
                    )
                )
                .values(weight=weight)
            )
        else:
            # Create new combination
            await self.db.execute(
                theme_combinations.insert().values(
                    primary_theme_id=primary_theme_id,
                    secondary_theme_id=secondary_theme_id,
                    weight=weight,
                )
            )

        await self.db.flush()
        return True

    async def get_theme_combinations(
        self, theme_id: UUID
    ) -> List[Tuple[Theme, float]]:
        """Get all themes combined with the given theme.

        Args:
            theme_id: Theme ID

        Returns:
            List of tuples containing combined themes and their weights
        """
        # Get combinations where theme is primary
        primary_query = (
            select(Theme, theme_combinations.c.weight)
            .join(
                theme_combinations,
                Theme.id == theme_combinations.c.secondary_theme_id,
            )
            .where(
                and_(
                    theme_combinations.c.primary_theme_id == theme_id,
                    Theme.is_deleted == False,
                )
            )
        )

        # Get combinations where theme is secondary
        secondary_query = (
            select(Theme, theme_combinations.c.weight)
            .join(
                theme_combinations,
                Theme.id == theme_combinations.c.primary_theme_id,
            )
            .where(
                and_(
                    theme_combinations.c.secondary_theme_id == theme_id,
                    Theme.is_deleted == False,
                )
            )
        )

        # Combine results
        primary_result = await self.db.execute(primary_query)
        secondary_result = await self.db.execute(secondary_query)
        
        combinations = []
        combinations.extend(primary_result.all())
        combinations.extend(secondary_result.all())
        return combinations

    async def validate_theme_compatibility(
        self, theme_id_1: UUID, theme_id_2: UUID
    ) -> ThemeValidationResponse:
        """Validate if two themes are compatible.

        Args:
            theme_id_1: First theme ID
            theme_id_2: Second theme ID

        Returns:
            Validation response with compatibility score and issues
        """
        theme1 = await self.get_theme(theme_id_1)
        theme2 = await self.get_theme(theme_id_2)
        if not theme1 or not theme2:
            return ThemeValidationResponse(
                is_valid=False,
                score=0.0,
                issues=["One or both themes not found"],
            )

        # Check basic compatibility rules
        issues = []
        if theme1.type == theme2.type and theme1.tone != theme2.tone:
            issues.append(
                f"Themes of same type ({theme1.type}) "
                f"should have compatible tones"
            )

        if theme1.intensity == "overwhelming" and theme2.intensity == "overwhelming":
            issues.append(
                "Cannot combine two overwhelming themes"
            )

        # Use LLM service for deeper compatibility analysis if available
        score = 0.8  # Default score
        if self.llm_service:
            analysis = await self.llm_service.analyze_theme_compatibility(
                theme1, theme2
            )
            score = analysis.score
            issues.extend(analysis.issues)

        return ThemeValidationResponse(
            is_valid=len(issues) == 0,
            score=score,
            issues=issues,
            suggestions=[
                "Consider adjusting theme intensities",
                "Try combining with a different tone",
            ] if issues else [],
        )

    async def validate_theme_content(
        self, request: ThemeValidationRequest
    ) -> ThemeValidationResponse:
        """Validate if content matches a theme.

        Args:
            request: Validation request with theme ID and content

        Returns:
            Validation response with matching score and issues
        """
        theme = await self.get_theme(request.theme_id)
        if not theme:
            return ThemeValidationResponse(
                is_valid=False,
                score=0.0,
                issues=["Theme not found"],
            )

        # Check content against theme's validation rules
        issues = []
        for rule_name, rule in theme.validation_rules.items():
            if not self._check_validation_rule(rule, request.content):
                issues.append(f"Content does not satisfy rule: {rule_name}")

        # Use LLM service for semantic validation if available
        score = 0.7  # Default score
        if self.llm_service:
            analysis = await self.llm_service.validate_theme_content(
                theme, request.content, request.context
            )
            score = analysis.score
            issues.extend(analysis.issues)

        return ThemeValidationResponse(
            is_valid=len(issues) == 0,
            score=score,
            issues=issues,
            suggestions=self._generate_theme_suggestions(theme, issues)
            if issues else [],
        )

    def _check_validation_rule(self, rule: Dict, content: Dict) -> bool:
        """Check if content satisfies a validation rule.

        Args:
            rule: Validation rule definition
            content: Content to validate

        Returns:
            True if content satisfies the rule, False otherwise
        """
        # Rule checking logic - would be more sophisticated in real impl
        rule_type = rule.get("type", "")
        if rule_type == "required_elements":
            return all(
                element in content
                for element in rule.get("elements", [])
            )
        elif rule_type == "forbidden_elements":
            return not any(
                element in content
                for element in rule.get("elements", [])
            )
        elif rule_type == "value_range":
            value = content.get(rule.get("field"))
            if value is None:
                return False
            min_val = rule.get("min")
            max_val = rule.get("max")
            return (
                (min_val is None or value >= min_val)
                and (max_val is None or value <= max_val)
            )
        return True

    def _generate_theme_suggestions(
        self, theme: Theme, issues: List[str]
    ) -> List[str]:
        """Generate suggestions for fixing theme issues.

        Args:
            theme: Theme that was validated
            issues: List of validation issues

        Returns:
            List of suggestions for fixing the issues
        """
        suggestions = []
        
        for issue in issues:
            if "required_elements" in issue:
                suggestions.append(
                    f"Add elements that reflect {theme.type} themes"
                )
            elif "forbidden_elements" in issue:
                suggestions.append(
                    f"Remove elements that conflict with {theme.type} themes"
                )
            elif "value_range" in issue:
                suggestions.append(
                    f"Adjust values to match {theme.type} theme intensity"
                )

        # Add theme-specific suggestions
        suggestions.extend(theme.style_guide.get("suggestions", []))
        
        return suggestions
