"""LLM service integration for theme-aware content generation."""

from typing import Dict, List, Optional, Union
from uuid import UUID

from ..models.theme import Theme, WorldEffect, Location, Faction


class ThemeLLMService:
    """Service for theme-aware content generation using LLM."""

    def __init__(self, llm_client=None):
        """Initialize the theme LLM service.

        Args:
            llm_client: LLM service client for content generation
        """
        self.llm_client = llm_client

    async def modify_content_for_theme(
        self,
        content: Dict,
        theme: Theme,
        prompts: List[str],
        parameters: Optional[Dict] = None,
    ) -> Dict:
        """Modify content to match a theme using LLM.

        Args:
            content: Content to modify
            theme: Theme to apply
            prompts: Theme-specific prompts
            parameters: Optional modification parameters

        Returns:
            Modified content and changes
        """
        system_prompt = self._build_theme_system_prompt(theme)
        modification_prompt = self._build_modification_prompt(
            content, theme, prompts, parameters
        )

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=modification_prompt,
            parameters={
                "temperature": 0.7,
                "max_tokens": 1000,
                "stop": ["###"],
            },
        )

        return self._parse_modification_response(response)

    async def validate_theme_consistency(
        self,
        content: Dict,
        theme: Theme,
        context: Optional[Dict] = None,
    ) -> Dict:
        """Validate content consistency with a theme using LLM.

        Args:
            content: Content to validate
            theme: Theme to validate against
            context: Optional validation context

        Returns:
            Validation results with issues and suggestions
        """
        system_prompt = self._build_validation_system_prompt(theme)
        validation_prompt = self._build_validation_prompt(
            content, theme, context
        )

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=validation_prompt,
            parameters={
                "temperature": 0.3,
                "max_tokens": 500,
                "stop": ["###"],
            },
        )

        return self._parse_validation_response(response)

    async def generate_themed_content(
        self,
        theme: Theme,
        content_type: str,
        prompts: List[str],
        parameters: Optional[Dict] = None,
    ) -> Dict:
        """Generate new content based on a theme.

        Args:
            theme: Theme to use
            content_type: Type of content to generate
            prompts: Generation prompts
            parameters: Optional generation parameters

        Returns:
            Generated content
        """
        system_prompt = self._build_generation_system_prompt(
            theme, content_type
        )
        generation_prompt = self._build_generation_prompt(
            theme, content_type, prompts, parameters
        )

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=generation_prompt,
            parameters={
                "temperature": 0.8,
                "max_tokens": 1500,
                "stop": ["###"],
            },
        )

        return self._parse_generation_response(response, content_type)

    async def adapt_content_between_themes(
        self,
        content: Dict,
        source_theme: Theme,
        target_theme: Theme,
    ) -> Dict:
        """Adapt content from one theme to another.

        Args:
            content: Content to adapt
            source_theme: Original theme
            target_theme: Target theme

        Returns:
            Adapted content
        """
        system_prompt = self._build_adaptation_system_prompt(
            source_theme, target_theme
        )
        adaptation_prompt = self._build_adaptation_prompt(
            content, source_theme, target_theme
        )

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=adaptation_prompt,
            parameters={
                "temperature": 0.7,
                "max_tokens": 1000,
                "stop": ["###"],
            },
        )

        return self._parse_adaptation_response(response)

    async def analyze_theme_compatibility(
        self,
        theme1: Theme,
        theme2: Theme,
    ) -> Dict:
        """Analyze compatibility between two themes.

        Args:
            theme1: First theme
            theme2: Second theme

        Returns:
            Compatibility analysis
        """
        system_prompt = self._build_compatibility_system_prompt()
        analysis_prompt = self._build_compatibility_prompt(theme1, theme2)

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=analysis_prompt,
            parameters={
                "temperature": 0.3,
                "max_tokens": 500,
                "stop": ["###"],
            },
        )

        return self._parse_compatibility_response(response)

    async def generate_theme_effects(
        self,
        theme: Theme,
        locations: List[Location],
        factions: List[Faction],
    ) -> List[WorldEffect]:
        """Generate world effects based on a theme.

        Args:
            theme: Theme to generate effects for
            locations: Available locations
            factions: Available factions

        Returns:
            Generated world effects
        """
        system_prompt = self._build_effects_system_prompt(theme)
        effects_prompt = self._build_effects_prompt(
            theme, locations, factions
        )

        response = await self.llm_client.complete(
            system=system_prompt,
            prompt=effects_prompt,
            parameters={
                "temperature": 0.7,
                "max_tokens": 2000,
                "stop": ["###"],
            },
        )

        return self._parse_effects_response(response)

    def _build_theme_system_prompt(self, theme: Theme) -> str:
        """Build system prompt for theme-aware operations."""
        return f"""You are a D&D campaign theme assistant specialized in {theme.type} themes.
Your task is to modify or validate content to ensure it matches the following theme:

Theme: {theme.name}
Type: {theme.type}
Tone: {theme.tone}
Intensity: {theme.intensity}

Style Guide:
{self._format_dict(theme.style_guide)}

Theme Attributes:
{self._format_dict(theme.attributes)}

Ensure all content:
1. Follows the theme's style guide
2. Maintains consistent tone and intensity
3. Incorporates theme-specific elements naturally
4. Preserves core meaning while enhancing theme
5. Balances theme elements with original content

Format responses as JSON with specified fields.
"""

    def _build_modification_prompt(
        self,
        content: Dict,
        theme: Theme,
        prompts: List[str],
        parameters: Optional[Dict],
    ) -> str:
        """Build prompt for content modification."""
        prompt_text = "\n".join(f"- {prompt}" for prompt in prompts)
        param_text = (
            "\n".join(f"{k}: {v}" for k, v in parameters.items())
            if parameters else "No additional parameters"
        )

        return f"""Modify the following content to match the theme:

Content:
{self._format_dict(content)}

Theme Prompts:
{prompt_text}

Parameters:
{param_text}

Return a JSON object with:
- modified_content: The modified content
- changes: List of changes made
- theme_elements: List of theme elements added/modified
- confidence_score: Float between 0 and 1

###"""

    def _build_validation_prompt(
        self,
        content: Dict,
        theme: Theme,
        context: Optional[Dict],
    ) -> str:
        """Build prompt for theme validation."""
        context_text = (
            self._format_dict(context)
            if context else "No additional context"
        )

        validation_rules = "\n".join(
            f"- {name}: {rule}"
            for name, rule in theme.validation_rules.items()
        )

        return f"""Validate if the following content matches the theme:

Content:
{self._format_dict(content)}

Context:
{context_text}

Validation Rules:
{validation_rules}

Return a JSON object with:
- is_valid: Boolean indicating if content matches theme
- score: Float between 0 and 1
- issues: List of identified issues
- suggestions: List of improvement suggestions

###"""

    def _build_generation_system_prompt(
        self,
        theme: Theme,
        content_type: str,
    ) -> str:
        """Build system prompt for content generation."""
        return f"""You are a D&D content generator specialized in {theme.type} themes.
Generate {content_type} content that matches the following theme:

Theme: {theme.name}
Type: {theme.type}
Tone: {theme.tone}
Intensity: {theme.intensity}

Style Guide:
{self._format_dict(theme.style_guide)}

Content Type Requirements:
{self._get_content_type_requirements(content_type)}

Format responses as JSON with fields matching content type requirements.
"""

    def _build_generation_prompt(
        self,
        theme: Theme,
        content_type: str,
        prompts: List[str],
        parameters: Optional[Dict],
    ) -> str:
        """Build prompt for content generation."""
        prompt_text = "\n".join(f"- {prompt}" for prompt in prompts)
        param_text = (
            "\n".join(f"{k}: {v}" for k, v in parameters.items())
            if parameters else "No additional parameters"
        )

        return f"""Generate {content_type} content with the following specifications:

Generation Prompts:
{prompt_text}

Parameters:
{param_text}

Return content in JSON format matching content type requirements.

###"""

    def _build_adaptation_system_prompt(
        self,
        source_theme: Theme,
        target_theme: Theme,
    ) -> str:
        """Build system prompt for theme adaptation."""
        return f"""You are a D&D theme adaptation specialist.
Adapt content between the following themes:

Source Theme:
- Name: {source_theme.name}
- Type: {source_theme.type}
- Tone: {source_theme.tone}
- Intensity: {source_theme.intensity}

Target Theme:
- Name: {target_theme.name}
- Type: {target_theme.type}
- Tone: {target_theme.tone}
- Intensity: {target_theme.intensity}

Source Style Guide:
{self._format_dict(source_theme.style_guide)}

Target Style Guide:
{self._format_dict(target_theme.style_guide)}

Format responses as JSON with:
- adapted_content: The adapted content
- changes: List of adaptations made
- preserved_elements: List of elements preserved
- new_elements: List of elements added
"""

    def _build_adaptation_prompt(
        self,
        content: Dict,
        source_theme: Theme,
        target_theme: Theme,
    ) -> str:
        """Build prompt for theme adaptation."""
        return f"""Adapt the following content from {source_theme.name} theme to {target_theme.name} theme:

Content:
{self._format_dict(content)}

Follow these guidelines:
1. Preserve core meaning and structure
2. Replace theme-specific elements appropriately
3. Adjust tone and intensity gradually
4. Maintain internal consistency
5. Balance preservation and adaptation

Return adapted content in JSON format.

###"""

    def _build_compatibility_system_prompt(self) -> str:
        """Build system prompt for theme compatibility analysis."""
        return """You are a D&D theme compatibility analyst.
Analyze the compatibility between two themes considering:

1. Theme type synergies and conflicts
2. Tone compatibility and contrast
3. Intensity balance and harmony
4. Style guide alignment
5. Potential combined effects

Format responses as JSON with:
- compatibility_score: Float between 0 and 1
- synergies: List of identified synergies
- conflicts: List of potential conflicts
- recommendations: List of combination suggestions
"""

    def _build_compatibility_prompt(
        self,
        theme1: Theme,
        theme2: Theme,
    ) -> str:
        """Build prompt for theme compatibility analysis."""
        return f"""Analyze compatibility between these themes:

Theme 1:
- Name: {theme1.name}
- Type: {theme1.type}
- Tone: {theme1.tone}
- Intensity: {theme1.intensity}
Style Guide: {self._format_dict(theme1.style_guide)}

Theme 2:
- Name: {theme2.name}
- Type: {theme2.type}
- Tone: {theme2.tone}
- Intensity: {theme2.intensity}
Style Guide: {self._format_dict(theme2.style_guide)}

Return analysis in JSON format.

###"""

    def _build_effects_system_prompt(self, theme: Theme) -> str:
        """Build system prompt for world effect generation."""
        return f"""You are a D&D world effect generator specialized in {theme.type} themes.
Generate world effects that reflect the following theme:

Theme: {theme.name}
Type: {theme.type}
Tone: {theme.tone}
Intensity: {theme.intensity}

Theme Attributes:
{self._format_dict(theme.attributes)}

Generated effects should:
1. Match theme type and tone
2. Scale with theme intensity
3. Impact appropriate targets
4. Have clear conditions
5. Follow logical durations

Format effects as JSON objects with:
- name: Effect name
- description: Effect description
- effect_type: One of [environment, climate, population, faction, economy, politics, culture]
- parameters: Effect parameters
- conditions: Application conditions
- impact_scale: Float between 0 and 1
- duration: Duration in days
"""

    def _build_effects_prompt(
        self,
        theme: Theme,
        locations: List[Location],
        factions: List[Faction],
    ) -> str:
        """Build prompt for world effect generation."""
        location_text = "\n".join(
            f"- {loc.name}: {loc.location_type}"
            for loc in locations
        )
        faction_text = "\n".join(
            f"- {fac.name}: {fac.faction_type}"
            for fac in factions
        )

        return f"""Generate world effects for the theme considering:

Available Locations:
{location_text}

Available Factions:
{faction_text}

Generate at least one effect for each appropriate target.
Return effects in JSON format matching required schema.

###"""

    def _get_content_type_requirements(self, content_type: str) -> str:
        """Get requirements for a content type."""
        requirements = {
            "location": """Required fields:
- name: Location name
- description: Detailed description
- location_type: Type of location
- attributes: Location attributes
- state: Current state""",
            "faction": """Required fields:
- name: Faction name
- description: Detailed description
- faction_type: Type of faction
- attributes: Faction attributes
- state: Current state
- relationships: Relationship map""",
            "npc": """Required fields:
- name: NPC name
- description: Physical and personality description
- role: NPC's role
- motivations: List of motivations
- relationships: Key relationships""",
            "plot": """Required fields:
- title: Plot title
- description: Plot description
- hooks: Entry points
- developments: Key developments
- resolution: Possible resolutions""",
        }
        return requirements.get(
            content_type,
            "Return content in appropriate format for type"
        )

    def _format_dict(self, d: Dict) -> str:
        """Format a dictionary for prompt inclusion."""
        if not d:
            return "None"
        return "\n".join(f"- {k}: {v}" for k, v in d.items())

    def _parse_modification_response(self, response: str) -> Dict:
        """Parse LLM response for content modification."""
        # In real implementation, parse JSON response
        return {
            "modified_content": {},
            "changes": [],
            "theme_elements": [],
            "confidence_score": 0.8,
        }

    def _parse_validation_response(self, response: str) -> Dict:
        """Parse LLM response for theme validation."""
        # In real implementation, parse JSON response
        return {
            "is_valid": True,
            "score": 0.9,
            "issues": [],
            "suggestions": [],
        }

    def _parse_generation_response(
        self,
        response: str,
        content_type: str,
    ) -> Dict:
        """Parse LLM response for content generation."""
        # In real implementation, parse JSON response
        return {}

    def _parse_adaptation_response(self, response: str) -> Dict:
        """Parse LLM response for theme adaptation."""
        # In real implementation, parse JSON response
        return {
            "adapted_content": {},
            "changes": [],
            "preserved_elements": [],
            "new_elements": [],
        }

    def _parse_compatibility_response(self, response: str) -> Dict:
        """Parse LLM response for theme compatibility."""
        # In real implementation, parse JSON response
        return {
            "compatibility_score": 0.8,
            "synergies": [],
            "conflicts": [],
            "recommendations": [],
        }

    def _parse_effects_response(self, response: str) -> List[WorldEffect]:
        """Parse LLM response for world effect generation."""
        # In real implementation, parse JSON response and create WorldEffect objects
        return []
