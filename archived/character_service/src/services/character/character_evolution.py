"""Core character evolution service supporting both traditional and Antitheticon campaigns."""

from typing import Dict, List, Optional, Any, Set, Union
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .antitheticon_evolution import AntithesiconEvolutionService
from .antitheticon_deception import AntithesiconDeceptionService

class CampaignType(Enum):
    """Types of campaigns supported."""
    TRADITIONAL = "traditional"  # Sequential D&D campaign
    ANTITHETICON = "antitheticon"  # Theme-hopping mastermind chase

class CharacterRole(Enum):
    """Character's role in the campaign."""
    PLAYER = "player"  # Player character
    ANTAGONIST = "antagonist"  # Main opponent
    ALLY = "ally"  # Friendly NPC
    NEUTRAL = "neutral"  # Neutral party
    MINION = "minion"  # Subordinate to another
    MASTERMIND = "mastermind"  # Behind-the-scenes player

@dataclass
class CharacterGrowthEvent:
    """A significant moment in character development."""
    event_id: str
    timestamp: datetime
    character_id: str
    growth_type: str  # moral, skill, relationship, belief, etc.
    description: str
    impact: Dict[str, Any]  # Effects on character
    context: Dict[str, Any]  # Situation details
    related_characters: List[str]
    campaign_effects: Dict[str, Any]  # How this affects the story

@dataclass
class RelationshipDynamic:
    """Connection between characters."""
    from_character: str
    to_character: str
    current_state: str
    history: List[Dict[str, Any]]
    tension_points: List[str]
    development_potential: List[Dict[str, Any]]
    story_hooks: List[Dict[str, Any]]

@dataclass
class CharacterArc:
    """A character's development path."""
    character_id: str
    role: CharacterRole
    initial_state: Dict[str, Any]
    current_state: Dict[str, Any]
    growth_points: List[CharacterGrowthEvent]
    relationships: Dict[str, RelationshipDynamic]
    personal_goals: List[Dict[str, Any]]
    inner_conflicts: List[Dict[str, Any]]
    story_hooks: List[Dict[str, Any]]

class CharacterEvolutionService:
    """Manages character evolution for both campaign types."""

    def __init__(self, llm_service, campaign_service):
        self.llm_service = llm_service
        self.campaign_service = campaign_service
        self.antitheticon_service = AntithesiconEvolutionService(
            llm_service, AntithesiconDeceptionService(llm_service))
        self.character_arcs: Dict[str, CharacterArc] = {}

    async def create_character_arc(self,
                                character_id: str,
                                role: CharacterRole,
                                campaign_type: CampaignType,
                                initial_state: Dict[str, Any]) -> CharacterArc:
        """Initialize a character's development arc."""
        prompt = f"""Generate character arc. Return ONLY JSON:

        CHARACTER:
        {initial_state}

        ROLE: {role.value}
        CAMPAIGN TYPE: {campaign_type.value}

        Create arc with:
        1. Growth potential
        2. Personal goals
        3. Inner conflicts
        4. Story hooks
        5. Development paths
        6. Key relationships
        7. Dramatic moments
        8. Campaign impact

        Return complete JSON arc."""

        arc_data = await self.llm_service.generate_content(prompt)
        arc = CharacterArc(**arc_data)
        self.character_arcs[character_id] = arc
        return arc

    async def process_growth_event(self,
                                character_id: str,
                                event: CharacterGrowthEvent,
                                campaign_type: CampaignType) -> Dict[str, Any]:
        """Process character growth event."""
        if campaign_type == CampaignType.ANTITHETICON and \
           self.character_arcs[character_id].role in [CharacterRole.MASTERMIND, CharacterRole.MINION]:
            # Use specialized Antitheticon processing
            return await self.antitheticon_service.process_character_evolution(
                character_id,
                [event],
                {"campaign_type": campaign_type.value}
            )

        prompt = f"""Process character growth. Return ONLY JSON:

        CHARACTER ARC:
        {self.character_arcs[character_id]}

        EVENT:
        {event}

        CAMPAIGN TYPE: {campaign_type.value}

        Process for:
        1. Character impact
        2. Relationship changes
        3. Story implications
        4. New opportunities
        5. Personal growth
        6. Campaign effects
        7. Future hooks
        8. Dramatic potential

        Return complete JSON analysis."""

        growth_data = await self.llm_service.generate_content(prompt)
        
        # Update character arc
        arc = self.character_arcs[character_id]
        arc.growth_points.append(event)
        arc.current_state.update(growth_data.get("state_updates", {}))
        
        return growth_data

    async def evolve_relationship(self,
                               relationship: RelationshipDynamic,
                               recent_events: List[Dict[str, Any]],
                               campaign_type: CampaignType) -> RelationshipDynamic:
        """Evolve a relationship between characters."""
        prompt = f"""Evolve relationship. Return ONLY JSON:

        RELATIONSHIP:
        {relationship}

        EVENTS:
        {recent_events}

        CAMPAIGN TYPE: {campaign_type.value}

        Evolve for:
        1. Current state
        2. Tension points
        3. Future potential
        4. Story hooks
        5. Dramatic moments
        6. Character growth
        7. Campaign impact
        8. Hidden elements

        Return complete JSON evolution."""

        evolution_data = await self.llm_service.generate_content(prompt)
        return RelationshipDynamic(**evolution_data)

    async def generate_growth_opportunities(self,
                                        character_id: str,
                                        campaign_context: Dict[str, Any],
                                        campaign_type: CampaignType) -> List[Dict[str, Any]]:
        """Generate potential growth opportunities."""
        arc = self.character_arcs[character_id]
        
        prompt = f"""Generate growth opportunities. Return ONLY JSON:

        CHARACTER ARC:
        {arc}

        CONTEXT:
        {campaign_context}

        CAMPAIGN TYPE: {campaign_type.value}

        Generate:
        1. Moral choices
        2. Skill challenges
        3. Relationship tests
        4. Personal conflicts
        5. Story moments
        6. Character development
        7. Campaign integration
        8. Dramatic scenes

        Return complete JSON opportunities."""

        return await self.llm_service.generate_content(prompt)

    async def create_traditional_example(self) -> Dict[str, Any]:
        """Example of traditional campaign character evolution."""
        # Create a conflicted paladin's arc
        paladin_initial = {
            "name": "Sir Roland",
            "class": "Paladin",
            "beliefs": ["Justice must be served",
                       "Protect the innocent"],
            "flaws": ["Rigid thinking",
                     "Quick to judge"],
            "background": "Former city guard"
        }

        arc = await self.create_character_arc(
            "roland_id",
            CharacterRole.PLAYER,
            CampaignType.TRADITIONAL,
            paladin_initial
        )

        # Process a moral challenge
        growth_event = CharacterGrowthEvent(
            event_id="event1",
            timestamp=datetime.now(),
            character_id="roland_id",
            growth_type="moral_choice",
            description="Chose mercy for repentant criminal",
            impact={
                "beliefs": "Questions absolute justice",
                "reputation": "More approachable",
                "relationships": "Criminal becomes informant"
            },
            context={
                "location": "City prison",
                "witnesses": ["Party", "Guards", "Criminal family"],
                "consequences": ["Reduced crime in district",
                               "New underground contact"]
            },
            related_characters=["criminal_id", "guard_captain_id"],
            campaign_effects={
                "new_quests": ["Help rehabilitation",
                              "Deal with hardline guards"],
                "world_changes": ["Prison reform movement",
                                "Changes in law enforcement"]
            }
        )

        development = await self.process_growth_event(
            "roland_id",
            growth_event,
            CampaignType.TRADITIONAL
        )

        # Example development data:
        return {
            "character_development": {
                "belief_changes": {
                    "from": "Absolute justice",
                    "to": "Tempered mercy",
                    "impact": "More nuanced decisions"
                },
                "personality_growth": {
                    "new_traits": ["Consideration", "Patience"],
                    "changed_approaches": ["Listens more", "Seeks context"]
                },
                "relationship_updates": {
                    "guard_captain": "Growing tension",
                    "criminal_contact": "Cautious trust",
                    "party_members": "Deeper respect"
                }
            },
            "story_implications": {
                "immediate": [
                    "Guard faction conflict",
                    "Criminal redemption story",
                    "Party reputation change"
                ],
                "future_hooks": [
                    "Prison reform quest",
                    "Corrupt guard investigation",
                    "Criminal family loyalty test"
                ],
                "world_effects": [
                    "Changing city attitudes",
                    "Law enforcement division",
                    "Criminal hierarchy shift"
                ]
            },
            "campaign_integration": {
                "main_plot_connections": [
                    "Criminal knows cult secret",
                    "Guard captain's hidden agenda",
                    "Prison reform politics"
                ],
                "side_quest_opportunities": [
                    "Help reformed criminals",
                    "Investigate guard corruption",
                    "Mediate faction conflicts"
                ],
                "character_arcs": [
                    "Justice vs. Mercy theme",
                    "Leadership growth",
                    "Personal code evolution"
                ]
            }
        }

    async def suggest_character_developments(self,
                                         character_id: str,
                                         campaign_context: Dict[str, Any],
                                         campaign_type: CampaignType) -> List[Dict[str, Any]]:
        """Suggest potential character developments."""
        arc = self.character_arcs[character_id]

        prompt = f"""Suggest character developments. Return ONLY JSON:

        CHARACTER ARC:
        {arc}

        CONTEXT:
        {campaign_context}

        CAMPAIGN TYPE: {campaign_type.value}

        Generate suggestions for:
        1. Personal growth
        2. Relationship evolution
        3. Story opportunities
        4. Dramatic moments
        5. Character challenges
        6. Plot integration
        7. World impact
        8. Future potential

        Return complete JSON suggestions."""

        return await self.llm_service.generate_content(prompt)

    async def process_campaign_event(self,
                                 event: Dict[str, Any],
                                 affected_characters: List[str],
                                 campaign_type: CampaignType) -> Dict[str, Any]:
        """Process how a campaign event affects characters."""
        prompt = f"""Process campaign event effects. Return ONLY JSON:

        EVENT:
        {event}

        AFFECTED CHARACTERS:
        {[self.character_arcs[char_id] for char_id in affected_characters]}

        CAMPAIGN TYPE: {campaign_type.value}

        Analyze effects on:
        1. Individual characters
        2. Relationships
        3. Story developments
        4. Personal growth
        5. Group dynamics
        6. Future implications
        7. Campaign integration
        8. Dramatic potential

        Return complete JSON analysis."""

        effects = await self.llm_service.generate_content(prompt)

        # Update affected character arcs
        for char_id in affected_characters:
            arc = self.character_arcs[char_id]
            # Apply relevant updates from effects
            for update in effects.get("character_updates", {}).get(char_id, []):
                if update["type"] == "growth_event":
                    event = CharacterGrowthEvent(**update["data"])
                    await self.process_growth_event(
                        char_id, event, campaign_type)
                elif update["type"] == "relationship_change":
                    rel = arc.relationships[update["target_id"]]
                    arc.relationships[update["target_id"]] = \
                        await self.evolve_relationship(
                            rel,
                            [event],
                            campaign_type
                        )

        return effects
