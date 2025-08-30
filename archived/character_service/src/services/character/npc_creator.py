"""NPC creation service extending base character creation."""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from .creation import CharacterCreationService
from .theme_manager import ThemeManager

@dataclass
class NPCType:
    """NPC type definition."""
    name: str
    role: str  # e.g., "quest_giver", "merchant", "villain"
    challenge_rating: float
    is_friendly: bool = True
    is_recurring: bool = False

class NPCCreator(CharacterCreationService):
    """Creates NPCs as specialized characters.
    
    NPCs are built using the full character framework but with:
    1. Simplified generation for quick use
    2. Focus on role-specific traits and abilities
    3. Optional full character sheet for playability
    """

    async def create_npc_from_concept(self, concept: str,
                                    npc_type: NPCType,
                                    theme: Optional[str] = None) -> Dict[str, Any]:
        """Create an NPC from a concept description."""
        try:
            # Generate NPC-specific prompt
            npc_prompt = self._build_npc_prompt(concept, npc_type, theme)
            
            # Generate character data with NPC focus
            npc_data = await self._generate_npc_data(npc_prompt, npc_type)
            
            # Create full character sheet but mark as NPC
            character = await self.create_character(npc_data)
            character.is_npc = True
            character.npc_type = npc_type.name
            character.role = npc_type.role
            character.challenge_rating = npc_type.challenge_rating
            
            # Add NPC-specific features
            await self._add_npc_features(character, npc_type)
            
            self.db.commit()
            return character
            
        except Exception as e:
            self.db.rollback()
            logger.error(f"NPC creation failed: {e}")
            raise

    def _build_npc_prompt(self, concept: str, npc_type: NPCType,
                         theme: Optional[str]) -> str:
        """Build NPC-specific prompt."""
        prompt_parts = [
            f"Create a D&D 5e NPC based on this concept: {concept}\n",
            f"NPC ROLE: {npc_type.role}",
            f"CHALLENGE RATING: {npc_type.challenge_rating}",
            "REQUIREMENTS:",
            "1. Focus on role-specific abilities and traits",
            "2. Include basic combat capabilities",
            "3. Provide social interaction traits",
            "4. Generate memorable characteristics"
        ]

        if theme:
            prompt_parts.extend([
                f"\nTHEME: {theme}",
                "All elements should fit the theme while maintaining D&D 5e rules."
            ])

        if npc_type.is_recurring:
            prompt_parts.extend([
                "\nRECURRING NPC:",
                "- Include character development potential",
                "- Add deeper personality traits",
                "- Create narrative hooks"
            ])

        return "\n".join(prompt_parts)

    async def _generate_npc_data(self, prompt: str,
                               npc_type: NPCType) -> Dict[str, Any]:
        """Generate NPC-specific character data."""
        # Get base character data
        npc_data = await self.theme_manager.generate_character_data(prompt)
        
        # Add NPC-specific data
        npc_data.update(await self._generate_npc_traits(npc_type))
        npc_data.update(await self._generate_npc_abilities(npc_type))
        npc_data.update(await self._generate_social_traits(npc_type))
        
        return npc_data

    async def _generate_npc_traits(self, npc_type: NPCType) -> Dict[str, Any]:
        """Generate NPC-specific traits based on role."""
        prompt = f"""Generate D&D 5e NPC traits. Return ONLY JSON:

        NPC TYPE: {npc_type.name}
        ROLE: {npc_type.role}
        CR: {npc_type.challenge_rating}

        Generate traits that:
        1. Fit the NPC's role
        2. Support their purpose in the story
        3. Make them memorable and distinct
        4. Include both personality and physical traits

        Return JSON with NPC traits."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _generate_npc_abilities(self, npc_type: NPCType) -> Dict[str, Any]:
        """Generate role-appropriate abilities."""
        prompt = f"""Generate D&D 5e NPC abilities. Return ONLY JSON:

        NPC TYPE: {npc_type.name}
        ROLE: {npc_type.role}
        CR: {npc_type.challenge_rating}

        Generate abilities that:
        1. Support their primary role
        2. Provide appropriate challenge (CR {npc_type.challenge_rating})
        3. Include both active and passive abilities
        4. Balance combat and non-combat capabilities

        Return JSON with NPC abilities."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _generate_social_traits(self, npc_type: NPCType) -> Dict[str, Any]:
        """Generate social interaction traits."""
        prompt = f"""Generate D&D 5e NPC social traits. Return ONLY JSON:

        NPC TYPE: {npc_type.name}
        ROLE: {npc_type.role}
        RECURRING: {npc_type.is_recurring}

        Generate social traits that:
        1. Support roleplay interactions
        2. Define their social behavior
        3. Include mannerisms and speech patterns
        4. Provide hooks for character development

        Return JSON with social traits."""

        return await self.theme_manager.generate_with_llm(prompt)

    async def _add_npc_features(self, character: Any,
                              npc_type: NPCType) -> None:
        """Add NPC-specific features to character."""
        # Add role-specific features
        role_features = {
            "quest_giver": ["Quest Knowledge", "Local Connections"],
            "merchant": ["Haggling", "Market Knowledge"],
            "villain": ["Villain Actions", "Minion Control"],
            "ally": ["Aid Action+", "Inspiring Presence"],
            "sage": ["Deep Knowledge", "Wise Counsel"]
        }
        
        if npc_type.role in role_features:
            character.features.extend(role_features[npc_type.role])

        # Add CR-appropriate features
        if npc_type.challenge_rating >= 1:
            character.features.append("Multiattack")
        if npc_type.challenge_rating >= 5:
            character.features.append("Legendary Resistance")

        # Add social features for recurring NPCs
        if npc_type.is_recurring:
            character.features.extend([
                "Character Development",
                "Story Integration",
                "Relationship Building"
            ])

    async def generate_npc_variants(self, base_npc_id: str,
                                  count: int = 3) -> List[Dict[str, Any]]:
        """Generate variants of an existing NPC."""
        base_npc = await self.get_character(base_npc_id)
        if not base_npc or not base_npc.is_npc:
            raise ValueError(f"Not a valid NPC: {base_npc_id}")

        prompt = f"""Generate {count} D&D 5e NPC variants. Return ONLY JSON:

        BASE NPC:
        {base_npc.to_dict()}

        Generate variants that:
        1. Keep the same basic role
        2. Modify abilities and traits
        3. Maintain theme consistency
        4. Provide distinct personalities

        Return JSON array with {count} NPC variants."""

        variants = await self.theme_manager.generate_with_llm(prompt)
        return variants.get("variants", [])
