"""Monster creation service extending base character creation."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum
from .creation import CharacterCreationService
from .theme_manager import ThemeManager

class MonsterType(Enum):
    """D&D 5e monster types."""
    ABERRATION = "aberration"
    BEAST = "beast"
    CELESTIAL = "celestial"
    CONSTRUCT = "construct"
    DRAGON = "dragon"
    ELEMENTAL = "elemental"
    FEY = "fey"
    FIEND = "fiend"
    GIANT = "giant"
    HUMANOID = "humanoid"
    MONSTROSITY = "monstrosity"
    OOZE = "ooze"
    PLANT = "plant"
    UNDEAD = "undead"

class MonsterSize(Enum):
    """D&D 5e creature sizes."""
    TINY = "tiny"
    SMALL = "small"
    MEDIUM = "medium"
    LARGE = "large"
    HUGE = "huge"
    GARGANTUAN = "gargantuan"

@dataclass
class MonsterTemplate:
    """Monster template definition."""
    type: MonsterType
    size: MonsterSize
    challenge_rating: float
    is_legendary: bool = False
    is_unique: bool = False
    role: str = "combat"  # combat, social, puzzle, etc.

class MonsterCreator(CharacterCreationService):
    """Creates monsters as specialized characters.
    
    Monsters are built using the full character framework but with:
    1. Monster-specific traits and abilities
    2. Challenge rating appropriate features
    3. Optional full character sheet for playability
    4. Support for legendary creatures
    """

    async def create_monster_from_concept(self, concept: str,
                                        template: MonsterTemplate,
                                        theme: Optional[str] = None) -> Dict[str, Any]:
        """Create a monster from a concept description."""
        try:
            # Generate monster-specific prompt
            monster_prompt = self._build_monster_prompt(concept, template, theme)
            
            # Generate character data with monster focus
            monster_data = await self._generate_monster_data(monster_prompt, template)
            
            # Create full character sheet but mark as monster
            character = await self.create_character(monster_data)
            character.is_monster = True
            character.monster_type = template.type.value
            character.size = template.size.value
            character.challenge_rating = template.challenge_rating
            
            # Add monster-specific features
            await self._add_monster_features(character, template)
            
            # Add legendary actions if applicable
            if template.is_legendary:
                await self._add_legendary_actions(character, template)
            
            self.db.commit()
            return character
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"Monster creation failed: {e}")
            raise

    def _build_monster_prompt(self, concept: str, template: MonsterTemplate,
                            theme: Optional[str]) -> str:
        """Build monster-specific prompt."""
        prompt_parts = [
            f"Create a D&D 5e monster based on this concept: {concept}\n",
            f"TYPE: {template.type.value}",
            f"SIZE: {template.size.value}",
            f"CHALLENGE RATING: {template.challenge_rating}",
            "REQUIREMENTS:",
            "1. Create distinctive monster abilities",
            "2. Include combat tactics",
            "3. Define behavior patterns",
            "4. Provide environmental preferences"
        ]

        if theme:
            prompt_parts.extend([
                f"\nTHEME: {theme}",
                "All elements should fit the theme while maintaining D&D 5e rules."
            ])

        if template.is_legendary:
            prompt_parts.extend([
                "\nLEGENDARY CREATURE:",
                "- Include legendary actions",
                "- Add lair actions",
                "- Create regional effects"
            ])

        if template.is_unique:
            prompt_parts.extend([
                "\nUNIQUE MONSTER:",
                "- Add distinguishing features",
                "- Include personal history",
                "- Create special abilities"
            ])

        return "\n".join(prompt_parts)

    async def _generate_monster_data(self, prompt: str,
                                   template: MonsterTemplate) -> Dict[str, Any]:
        """Generate monster-specific character data."""
        # Get base character data
        monster_data = await self.theme_manager.generate_character_data(prompt)
        
        # Add monster-specific data
        monster_data.update(await self._generate_monster_traits(template))
        monster_data.update(await self._generate_monster_abilities(template))
        monster_data.update(await self._generate_monster_behavior(template))
        
        if template.is_legendary:
            monster_data.update(await self._generate_legendary_content(template))
        
        return monster_data

    async def _generate_monster_traits(self, template: MonsterTemplate) -> Dict[str, Any]:
        """Generate monster-specific traits."""
        prompt = f"""Generate D&D 5e monster traits. Return ONLY JSON:

        TYPE: {template.type.value}
        SIZE: {template.size.value}
        CR: {template.challenge_rating}

        Generate traits that:
        1. Match the monster type
        2. Fit the size category
        3. Are appropriate for the CR
        4. Define unique characteristics

        Return JSON with monster traits."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _generate_monster_abilities(self, template: MonsterTemplate) -> Dict[str, Any]:
        """Generate monster abilities and actions."""
        prompt = f"""Generate D&D 5e monster abilities. Return ONLY JSON:

        TYPE: {template.type.value}
        SIZE: {template.size.value}
        CR: {template.challenge_rating}
        ROLE: {template.role}

        Generate abilities that:
        1. Provide appropriate challenge (CR {template.challenge_rating})
        2. Include both offensive and defensive options
        3. Create interesting tactical choices
        4. Fit the monster's intended role

        Return JSON with monster abilities."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _generate_monster_behavior(self, template: MonsterTemplate) -> Dict[str, Any]:
        """Generate monster behavior patterns."""
        prompt = f"""Generate D&D 5e monster behavior. Return ONLY JSON:

        TYPE: {template.type.value}
        SIZE: {template.size.value}
        CR: {template.challenge_rating}

        Generate behavior that:
        1. Defines typical patterns
        2. Includes combat tactics
        3. Describes social interactions
        4. Specifies environmental preferences

        Return JSON with monster behavior."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _generate_legendary_content(self, template: MonsterTemplate) -> Dict[str, Any]:
        """Generate legendary actions and effects."""
        prompt = f"""Generate D&D 5e legendary monster content. Return ONLY JSON:

        TYPE: {template.type.value}
        CR: {template.challenge_rating}

        Generate content that includes:
        1. 3 Legendary actions
        2. 3 Lair actions
        3. 3 Regional effects
        4. Special legendary behaviors

        Return JSON with legendary content."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _add_monster_features(self, character: Any,
                                  template: MonsterTemplate) -> None:
        """Add monster-specific features to character."""
        # Add type-specific features
        type_features = {
            MonsterType.DRAGON: ["Breath Weapon", "Frightful Presence"],
            MonsterType.UNDEAD: ["Undead Nature", "Negative Energy Affinity"],
            MonsterType.FIEND: ["Magic Resistance", "Evil Alignment"],
            MonsterType.FEY: ["Fey Ancestry", "Magic Affinity"],
            MonsterType.CONSTRUCT: ["Constructed Nature", "Immutable Form"]
        }
        
        if template.type in type_features:
            character.features.extend(type_features[template.type])

        # Add size-based features
        size_features = {
            MonsterSize.TINY: ["Naturally Stealthy"],
            MonsterSize.LARGE: ["Powerful Build"],
            MonsterSize.HUGE: ["Siege Monster"],
            MonsterSize.GARGANTUAN: ["Titanic Might"]
        }
        
        if template.size in size_features:
            character.features.extend(size_features[template.size])

        # Add CR-appropriate features
        if template.challenge_rating >= 1:
            character.features.append("Multiattack")
        if template.challenge_rating >= 5:
            character.features.append("Magic Resistance")
        if template.challenge_rating >= 10:
            character.features.append("Legendary Resistance")

    async def _add_legendary_actions(self, character: Any,
                                   template: MonsterTemplate) -> None:
        """Add legendary actions to a legendary creature."""
        # Generate legendary actions based on type and CR
        legendary_actions = await self._generate_legendary_actions(template)
        
        # Add to character
        character.legendary_actions = legendary_actions.get("actions", [])
        character.lair_actions = legendary_actions.get("lair_actions", [])
        character.regional_effects = legendary_actions.get("regional_effects", [])

    async def _generate_legendary_actions(self, template: MonsterTemplate) -> Dict[str, Any]:
        """Generate appropriate legendary actions."""
        prompt = f"""Generate D&D 5e legendary actions. Return ONLY JSON:

        TYPE: {template.type.value}
        CR: {template.challenge_rating}

        Generate legendary content appropriate for:
        1. Monster type and theme
        2. Challenge rating
        3. Tactical gameplay
        4. Narrative significance

        Return JSON with legendary actions, lair actions, and regional effects."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def generate_monster_variants(self, base_monster_id: str,
                                     count: int = 3) -> List[Dict[str, Any]]:
        """Generate variants of an existing monster."""
        base_monster = await self.get_character(base_monster_id)
        if not base_monster or not base_monster.is_monster:
            raise ValueError(f"Not a valid monster: {base_monster_id}")

        prompt = f"""Generate {count} D&D 5e monster variants. Return ONLY JSON:

        BASE MONSTER:
        {base_monster.to_dict()}

        Generate variants that:
        1. Keep the same basic type
        2. Modify abilities and traits
        3. Maintain CR-appropriate challenge
        4. Provide distinct tactical options

        Return JSON array with {count} monster variants."""

        variants = await self.theme_manager.generate_with_llm(prompt)
        return variants.get("variants", [])
