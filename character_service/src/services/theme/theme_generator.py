"""Dynamic theme generation using LLM."""

from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum

@dataclass
class ThemeDefinition:
    """Complete definition of a theme."""
    name: str
    description: str
    key_concepts: List[str]
    equipment_style: Dict[str, str]  # type -> style description
    magic_style: Dict[str, str]  # school -> style description
    architectural_style: str
    clothing_style: str
    cultural_elements: List[str]
    technology_level: str
    common_materials: List[str]
    combat_style: str
    sample_names: List[str]

@dataclass
class ThemeMapping:
    """Mapping between D&D concepts and themed equivalents."""
    weapons: Dict[str, Dict[str, Any]]  # D&D weapon -> themed version
    armor: Dict[str, Dict[str, Any]]  # D&D armor -> themed version
    spells: Dict[str, Dict[str, Any]]  # D&D spell -> themed version
    classes: Dict[str, Dict[str, Any]]  # D&D class -> themed version
    abilities: Dict[str, Dict[str, Any]]  # D&D ability -> themed version
    skills: Dict[str, Dict[str, Any]]  # D&D skill -> themed version

class ThemeGenerator:
    """Generates complete theme definitions from descriptions."""

    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def generate_theme(self, description: str) -> ThemeDefinition:
        """Generate a complete theme definition from a description."""
        prompt = f"""Create a comprehensive D&D theme based on this description: {description}

        Generate a complete theme that includes:
        1. Key concepts and motifs
        2. Equipment and technology style
        3. Magic manifestation
        4. Cultural elements
        5. Visual aesthetics
        6. Material preferences
        7. Combat approaches

        Return ONLY JSON with complete theme definition."""

        theme_data = await self.llm_service.generate_content(prompt)
        return ThemeDefinition(**theme_data)

    async def generate_theme_mappings(self, theme: ThemeDefinition) -> ThemeMapping:
        """Generate mappings from D&D elements to themed versions."""
        prompt = f"""Create D&D 5e conversion mappings for this theme:

        THEME:
        {theme.description}

        KEY CONCEPTS:
        {', '.join(theme.key_concepts)}

        TECHNOLOGY LEVEL:
        {theme.technology_level}

        Create mappings for:
        1. Common D&D weapons -> themed equivalents
        2. Standard armor types -> themed protection
        3. Basic spells -> themed manifestations
        4. Character classes -> themed archetypes
        5. Abilities and skills -> themed applications

        Each mapping should preserve D&D 5e mechanics while reflecting:
        - Technology level: {theme.technology_level}
        - Common materials: {', '.join(theme.common_materials)}
        - Combat style: {theme.combat_style}

        Return ONLY JSON with complete mappings."""

        mapping_data = await self.llm_service.generate_content(prompt)
        return ThemeMapping(**mapping_data)

    async def generate_themed_entity(self, 
                                   entity_type: str,
                                   base_entity: Dict[str, Any],
                                   theme: ThemeDefinition) -> Dict[str, Any]:
        """Generate a themed version of a D&D entity."""
        prompt = f"""Create a themed version of this D&D {entity_type}:

        ORIGINAL ENTITY:
        {base_entity}

        THEME:
        {theme.description}

        STYLE ELEMENTS:
        - Equipment: {theme.equipment_style}
        - Magic: {theme.magic_style}
        - Materials: {', '.join(theme.common_materials)}
        - Combat: {theme.combat_style}

        Create a themed version that:
        1. Maintains core D&D mechanics
        2. Reflects theme aesthetics
        3. Uses appropriate materials
        4. Matches technology level
        5. Fits combat style

        Return ONLY JSON with themed entity."""

        return await self.llm_service.generate_content(prompt)

    async def generate_themed_character_concept(self,
                                              base_concept: str,
                                              theme: ThemeDefinition) -> str:
        """Generate a themed character concept."""
        prompt = f"""Transform this D&D character concept for this theme:

        ORIGINAL CONCEPT:
        {base_concept}

        THEME:
        {theme.description}

        CULTURAL ELEMENTS:
        {theme.cultural_elements}

        Create a themed character concept that:
        1. Maintains core character motivation
        2. Fits theme's culture
        3. Uses theme-appropriate equipment
        4. Has themed abilities
        5. Reflects theme's aesthetic

        Return ONLY JSON with themed concept."""

        concept_data = await self.llm_service.generate_content(prompt)
        return concept_data["concept"]

    async def generate_themed_location(self,
                                     location_type: str,
                                     theme: ThemeDefinition) -> Dict[str, Any]:
        """Generate a themed location."""
        prompt = f"""Create a {location_type} for this theme:

        THEME:
        {theme.description}

        ARCHITECTURE:
        {theme.architectural_style}

        CULTURAL ELEMENTS:
        {theme.cultural_elements}

        Create a location that:
        1. Serves D&D gameplay needs
        2. Matches theme's architecture
        3. Reflects cultural elements
        4. Uses appropriate materials
        5. Fits technology level

        Return ONLY JSON with location details."""

        return await self.llm_service.generate_content(prompt)

class DynamicThemeConverter:
    """Converts D&D elements to any theme dynamically."""

    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def convert_to_theme(self,
                             element: Dict[str, Any],
                             element_type: str,
                             theme_description: str) -> Dict[str, Any]:
        """Convert any D&D element to any theme."""
        prompt = f"""Convert this D&D {element_type} to match this theme description:

        ELEMENT:
        {element}

        THEME:
        {theme_description}

        Create a conversion that:
        1. Preserves core D&D mechanics
        2. Matches theme aesthetics
        3. Maintains game balance
        4. Keeps original purpose
        5. Fits theme's context

        For example, if converting to WW2 theme:
        - Longsword -> Combat Knife
        - Chain Mail -> Flak Jacket
        - Fireball -> Hand Grenade
        - Wizard -> Field Scientist
        - Magic Missile -> Burst Fire

        Return ONLY JSON with themed version."""

        return await self.llm_service.generate_content(prompt)

    async def describe_themed_action(self,
                                   action: str,
                                   theme_description: str) -> str:
        """Generate themed description of an action."""
        prompt = f"""Describe how this action manifests in this theme:

        ACTION:
        {action}

        THEME:
        {theme_description}

        Create a description that:
        1. Maintains action's effect
        2. Uses theme's aesthetics
        3. Fits theme's technology
        4. Makes narrative sense

        For example, in WW2 theme:
        - "Cast Fireball" -> "Lob an experimental phosphorus grenade"
        - "Divine Smite" -> "Unleash righteous machine gun fire"

        Return ONLY JSON with themed description."""

        description_data = await self.llm_service.generate_content(prompt)
        return description_data["description"]

    async def suggest_theme_elements(self,
                                   theme_description: str,
                                   element_type: str) -> List[Dict[str, Any]]:
        """Suggest new elements that would exist in this theme."""
        prompt = f"""Suggest new {element_type}s that would exist in this theme:

        THEME:
        {theme_description}

        ELEMENT TYPE:
        {element_type}

        Create suggestions that:
        1. Fit D&D mechanics
        2. Match theme perfectly
        3. Add unique flavor
        4. Maintain balance
        5. Feel authentic

        For example, in WW2 theme weapons:
        - "Thompson SMG" (functions like shortbow)
        - "Bayonet" (functions like spear)
        - "Combat Knife" (functions like dagger)

        Return ONLY JSON with suggested elements."""

        suggestions = await self.llm_service.generate_content(prompt)
        return suggestions["elements"]
