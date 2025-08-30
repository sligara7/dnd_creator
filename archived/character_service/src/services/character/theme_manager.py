"""Theme management for character creation and modification."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from src.services.llm_service import LLMService
import logging

logger = logging.getLogger(__name__)

@dataclass
class ThemeConsistency:
    is_consistent: bool
    issues: List[str]
    suggestions: List[Dict[str, Any]]

@dataclass
class ThemeMapping:
    """Mapping between themes for character retheme operations."""
    original_theme: str
    target_theme: str
    # Maps for each component type (preserving mechanical properties)
    weapon_mappings: Dict[str, Dict[str, Any]]  # e.g. "longsword" -> {"name": "lightsaber", "properties": {...}}
    armor_mappings: Dict[str, Dict[str, Any]]
    spell_mappings: Dict[str, Dict[str, Any]]
    equipment_mappings: Dict[str, Dict[str, Any]]
    class_feature_mappings: Dict[str, Dict[str, Any]]

class ThemeManager:
    """Manages theme application and consistency for character data."""

    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service

    async def generate_theme_mapping(self, original_theme: str, target_theme: str,
                                   character: Dict[str, Any]) -> ThemeMapping:
        """Generate mapping between themes for character retheme.

        Args:
            original_theme: Current theme (e.g. 'western')
            target_theme: Desired theme (e.g. 'cyberpunk')
            character: Current character data

        Returns:
            Complete mapping between themes preserving mechanical properties
        """
        prompt = f"""Create a D&D 5e theme mapping that preserves mechanical properties while converting from {original_theme} to {target_theme}. Return ONLY JSON:

        CURRENT CHARACTER:
        {character}

        Create mappings for all character elements that preserve mechanics but update names and descriptions to match new theme.

        Example: Western to Cyberpunk
        - "six-shooter" -> "laser pistol" (keeps same damage/range)
        - "duster coat" -> "armored trenchcoat" (keeps same AC)
        - "trick shot" -> "targeting system" (keeps same mechanical effect)

        Return complete JSON mapping for all character elements."""

        mapping_data = await self._generate_with_llm(prompt, "theme_mapping")
        return ThemeMapping(
            original_theme=original_theme,
            target_theme=target_theme,
            weapon_mappings=mapping_data.get("weapons", {}),
            armor_mappings=mapping_data.get("armor", {}),
            spell_mappings=mapping_data.get("spells", {}),
            equipment_mappings=mapping_data.get("equipment", {}),
            class_feature_mappings=mapping_data.get("class_features", {})
        )

    async def apply_theme_mapping(self, character: Dict[str, Any],
                                theme_mapping: ThemeMapping) -> Dict[str, Any]:
        """Apply theme mapping to character while preserving mechanics."""
        themed_char = character.copy()

        # Apply mappings to each component type
        themed_char["weapons"] = self._apply_component_mapping(
            character.get("weapons", []),
            theme_mapping.weapon_mappings
        )
        themed_char["armor"] = self._apply_component_mapping(
            character.get("armor", []),
            theme_mapping.armor_mappings
        )
        themed_char["spells"] = self._apply_component_mapping(
            character.get("spells", []),
            theme_mapping.spell_mappings
        )
        themed_char["equipment"] = self._apply_component_mapping(
            character.get("equipment", {}),
            theme_mapping.equipment_mappings
        )
        themed_char["class_features"] = self._apply_component_mapping(
            character.get("class_features", []),
            theme_mapping.class_feature_mappings
        )

        return themed_char

    def _apply_component_mapping(self, components: Any,
                               mapping: Dict[str, Dict[str, Any]]) -> Any:
        """Apply theme mapping to a specific component type."""
        if isinstance(components, list):
            return [mapping.get(comp["name"], comp) if isinstance(comp, dict) else comp
                    for comp in components]
        elif isinstance(components, dict):
            return {k: mapping.get(k, v) for k, v in components.items()}
        return components

    async def theme_item(self, item: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Theme a single item while preserving its mechanical properties."""
        prompt = f"""Theme this D&D 5e item for a {theme} setting while preserving mechanics. Return ONLY JSON:

        ORIGINAL ITEM:
        {item}

        Create a themed version that keeps the same mechanical properties but fits the {theme} theme.
        Return complete JSON for themed item."""

        themed_item = await self._generate_with_llm(prompt, "theme_item")
        return themed_item

    async def theme_spell(self, spell: Dict[str, Any], theme: str) -> Dict[str, Any]:
        """Theme a single spell while preserving its mechanical properties."""
        prompt = f"""Theme this D&D 5e spell for a {theme} setting while preserving mechanics. Return ONLY JSON:

        ORIGINAL SPELL:
        {spell}

        Create a themed version that keeps the same mechanical properties but fits the {theme} theme.
        Return complete JSON for themed spell."""

        themed_spell = await self._generate_with_llm(prompt, "theme_spell")
        return themed_spell

    async def validate_consistency(self, character: Dict[str, Any]) -> ThemeConsistency:
        """Validate thematic consistency across all character components."""
        theme = character.get("theme")
        if not theme:
            return ThemeConsistency(True, [], [])

        prompt = f"""Analyze thematic consistency for this D&D 5e character in a {theme} setting. Return ONLY JSON:

        CHARACTER:
        {character}

        Check if all components (weapons, armor, spells, etc.) consistently fit the {theme} theme.
        Identify any inconsistencies and suggest alternatives.
        Return JSON with consistency analysis."""

        analysis = await self._generate_with_llm(prompt, "theme_consistency")
        return ThemeConsistency(
            is_consistent=analysis.get("is_consistent", False),
            issues=analysis.get("issues", []),
            suggestions=analysis.get("suggestions", [])
        )

    async def generate_alternatives(self, character: Dict[str, Any],
                                  aspect: str, theme: str,
                                  count: int) -> List[Dict[str, Any]]:
        """Generate themed alternatives for a character aspect."""
        prompt = f"""Generate {count} themed alternatives for this D&D 5e character aspect. Return ONLY JSON:

        CHARACTER:
        {character}

        ASPECT: {aspect}
        THEME: {theme}

        Generate {count} alternatives that:
        1. Fit the {theme} theme
        2. Maintain mechanical balance
        3. Suit the character concept

        Return JSON array of alternative options."""

        alternatives = await self._generate_with_llm(prompt, "theme_alternatives")
        return alternatives.get("alternatives", [])

    async def _generate_with_llm(self, prompt: str, prompt_type: str) -> Dict[str, Any]:
        """Generate themed content using LLM."""
        try:
            response = await self.llm_service.generate_content(prompt)
            return response
        except Exception as e:
            logger.error(f"Theme generation failed for {prompt_type}: {e}")
            return {}
