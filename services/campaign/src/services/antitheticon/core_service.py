"""Core service for managing Antitheticon mechanics."""
from datetime import datetime
from typing import Dict, List, Optional, Any
from uuid import UUID

from ...core.ai import AIClient
from ...core.logging import get_logger
from ...models.antitheticon import (
    DisguisedForm,
    RealityPair,
    ManipulationEvent,
    ProgressionState
)
from ..character_service import CharacterService
from ..world_service import WorldService
from ..event_service import EventService

logger = get_logger(__name__)


class AntithericonService:
    """Service for managing Antitheticon mechanics."""

    def __init__(
        self,
        ai_client: AIClient,
        character_service: CharacterService,
        world_service: WorldService,
        event_service: EventService,
    ):
        self.ai_client = ai_client
        self.character_service = character_service
        self.world_service = world_service
        self.event_service = event_service

    async def initialize_antitheticon(
        self,
        campaign_id: UUID,
        initial_theme: str,
        party_level: int
    ) -> Dict[str, Any]:
        """Initialize Antitheticon for a campaign."""
        try:
            # Create initial disguised form
            helper_form = await self._create_helper_form(
                theme=initial_theme,
                party_level=party_level
            )

            # Generate reality pair
            reality_pair = await self._create_reality_pair(initial_theme)

            # Initialize progression state
            progression = await self._initialize_progression(
                campaign_id,
                party_level
            )

            return {
                "helper_form": helper_form,
                "reality_pair": reality_pair,
                "progression": progression
            }

        except Exception as e:
            logger.error("Failed to initialize Antitheticon", error=str(e))
            raise ValueError(f"Antitheticon initialization failed: {e}")

    async def _create_helper_form(
        self,
        theme: str,
        party_level: int
    ) -> DisguisedForm:
        """Create initial helper NPC form."""
        try:
            # Generate personality and background
            context = {
                "theme": theme,
                "party_level": party_level,
                "archetype": "disabled_informant",
                "role": "quest_giver"
            }
            
            # Use LLM to create consistent personality
            personality = await self.ai_client.generate_personality(context)

            # Create NPC stats
            npc_stats = await self.character_service.create_npc(
                level=party_level - 1,  # Appear slightly weaker
                role="informant",
                limitations=personality.limitations,
                special_abilities=personality.abilities
            )

            # Create themed knowledge base
            knowledge = await self.ai_client.generate_knowledge_base({
                "theme": theme,
                "depth": "extensive",
                "truth_ratio": 0.7,
                "special_insights": personality.insights
            })

            return DisguisedForm(
                personality=personality,
                stats=npc_stats,
                knowledge=knowledge
            )

        except Exception as e:
            logger.error("Failed to create helper form", error=str(e))
            raise

    async def _create_reality_pair(
        self,
        base_theme: str
    ) -> RealityPair:
        """Create paired normal and inverted realities."""
        try:
            # Generate inverted theme concept
            inversion = await self.ai_client.generate_theme_inversion({
                "base_theme": base_theme,
                "corruption_level": "unsettling",
                "reality_rules": "twisted_mirror"
            })

            # Create normal world
            normal_world = await self.world_service.create_world(
                theme=base_theme,
                type="normal",
                rules=inversion.normal_rules
            )

            # Create inverted world
            inverted_world = await self.world_service.create_world(
                theme=inversion.inverted_theme,
                type="inverted",
                rules=inversion.inverted_rules
            )

            # Generate transition mechanics
            transitions = await self.ai_client.generate_transition_rules({
                "normal_world": normal_world.dict(),
                "inverted_world": inverted_world.dict(),
                "corruption_rules": inversion.corruption_rules
            })

            return RealityPair(
                normal=normal_world,
                inverted=inverted_world,
                transitions=transitions
            )

        except Exception as e:
            logger.error("Failed to create reality pair", error=str(e))
            raise

    async def evolve_antitheticon(
        self,
        campaign_id: UUID,
        new_theme: str,
        party_level: int,
        party_actions: List[Dict],
        current_knowledge: float
    ) -> Dict[str, Any]:
        """Evolve Antitheticon for theme transition."""
        try:
            # Analyze party capabilities
            analysis = await self.ai_client.analyze_party({
                "actions": party_actions,
                "level": party_level,
                "theme": new_theme
            })

            # Generate evolved form
            evolved_form = await self._evolve_helper_form(
                current_theme=new_theme,
                party_level=party_level,
                party_analysis=analysis
            )

            # Create new reality pair
            new_reality = await self._create_reality_pair(new_theme)

            # Generate transition events
            transition = await self.event_service.create_transition_sequence({
                "old_theme": evolved_form.current_theme,
                "new_theme": new_theme,
                "knowledge_level": current_knowledge,
                "party_level": party_level
            })

            return {
                "evolved_form": evolved_form,
                "new_reality": new_reality,
                "transition_events": transition
            }

        except Exception as e:
            logger.error("Failed to evolve Antitheticon", error=str(e))
            raise

    async def _evolve_helper_form(
        self,
        current_theme: str,
        party_level: int,
        party_analysis: Dict
    ) -> DisguisedForm:
        """Evolve helper NPC form."""
        try:
            # Generate evolved personality
            evolution_context = {
                "theme": current_theme,
                "party_level": party_level,
                "party_capabilities": party_analysis,
                "maintain_traits": ["helpful", "knowledgeable", "seemingly_weak"]
            }

            evolved = await self.ai_client.evolve_personality(evolution_context)

            # Update NPC stats
            new_stats = await self.character_service.update_npc(
                level=party_level - 1,
                new_role=evolved.role,
                new_limitations=evolved.limitations,
                new_abilities=evolved.abilities
            )

            # Update knowledge for new theme
            new_knowledge = await self.ai_client.evolve_knowledge_base({
                "theme": current_theme,
                "previous_knowledge": evolved.previous_knowledge,
                "truth_ratio": 0.7,
                "new_insights": evolved.insights
            })

            return DisguisedForm(
                personality=evolved.personality,
                stats=new_stats,
                knowledge=new_knowledge
            )

        except Exception as e:
            logger.error("Failed to evolve helper form", error=str(e))
            raise

    async def create_reality_bleed(
        self,
        location_id: UUID,
        intensity: float,
        current_phase: str
    ) -> Dict[str, Any]:
        """Create reality bleed effect at location."""
        try:
            # Generate bleed effects
            effects = await self.ai_client.generate_reality_effects({
                "location_id": str(location_id),
                "intensity": intensity,
                "phase": current_phase
            })

            # Apply to location in both realities
            normal_effects = await self.world_service.apply_effects(
                location_id=location_id,
                reality_type="normal",
                effects=effects.normal
            )

            inverted_effects = await self.world_service.apply_effects(
                location_id=location_id,
                reality_type="inverted",
                effects=effects.inverted
            )

            # Create manifestation events
            events = await self.event_service.create_bleed_events({
                "location": str(location_id),
                "normal_effects": normal_effects,
                "inverted_effects": inverted_effects,
                "intensity": intensity
            })

            return {
                "effects": {
                    "normal": normal_effects,
                    "inverted": inverted_effects
                },
                "events": events
            }

        except Exception as e:
            logger.error("Failed to create reality bleed", error=str(e))
            raise

    async def orchestrate_revelation(
        self,
        campaign_id: UUID,
        current_knowledge: float,
        story_phase: str,
        party_actions: List[Dict]
    ) -> Dict[str, Any]:
        """Orchestrate revelation of Antitheticon's nature."""
        try:
            # Calculate appropriate revelation
            revelation = await self.ai_client.calculate_revelation({
                "current_knowledge": current_knowledge,
                "story_phase": story_phase,
                "party_actions": party_actions
            })

            # Generate revelation events
            events = await self.event_service.create_revelation_sequence({
                "campaign_id": str(campaign_id),
                "revelation_type": revelation.type,
                "knowledge_gain": revelation.knowledge,
                "phase": story_phase
            })

            # Update progression state
            progression = await self._update_progression(
                campaign_id=campaign_id,
                revelation=revelation,
                events=events
            )

            return {
                "revelation": revelation,
                "events": events,
                "progression": progression
            }

        except Exception as e:
            logger.error("Failed to orchestrate revelation", error=str(e))
            raise

    async def _update_progression(
        self,
        campaign_id: UUID,
        revelation: Dict,
        events: List[Dict]
    ) -> ProgressionState:
        """Update Antitheticon progression state."""
        try:
            # Calculate new state
            new_state = await self.ai_client.calculate_progression({
                "campaign_id": str(campaign_id),
                "revelation": revelation,
                "events": events
            })

            # Update progression
            progression = await self.event_service.update_progression(
                campaign_id=campaign_id,
                new_state=new_state
            )

            return progression

        except Exception as e:
            logger.error("Failed to update progression", error=str(e))
            raise
