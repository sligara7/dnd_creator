"""Antitheticon service for generating and evolving perfect party nemeses."""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from enum import Enum
from datetime import datetime

@dataclass
class PartyMember:
    """Information about a party member for opposition."""
    character_id: str
    archetype: str  # role in party
    beliefs: List[str]
    methods: List[str]
    key_traits: List[str]
    strengths: List[str]
    weaknesses: List[str]
    relationships: List[Dict[str, Any]]
    personal_conflicts: List[str]

@dataclass
class PartyProfile:
    """Complete analysis of party for opposition."""
    members: List[PartyMember]
    group_dynamics: Dict[str, Any]
    shared_beliefs: List[str]
    collective_methods: List[str]
    group_strengths: List[str]
    group_weaknesses: List[str]
    unresolved_conflicts: List[str]
    shared_goals: List[str]
    moral_alignment: str

@dataclass
class AntithesisMember:
    """Member of the antithetical group."""
    character_id: str
    opposes: str  # ID of party member they counter
    antithetical_traits: Dict[str, str]  # trait -> opposite
    personal_grudge: str
    evolution_path: List[Dict[str, Any]]
    current_level: int
    specialized_counters: List[Dict[str, Any]]
    psychological_profile: Dict[str, Any]

@dataclass
class Antitheticon:
    """Complete antithetical force to the party."""
    group_id: str
    leader: AntithesisMember
    core_members: List[AntithesisMember]
    henchmen: List[Dict[str, Any]]
    group_theme: str
    opposition_strategy: Dict[str, Any]
    evolution_stage: int
    current_plans: List[Dict[str, Any]]
    base_of_operations: Dict[str, Any]
    resources: Dict[str, Any]

class AntithesisDevelopment(Enum):
    """How the antithesis develops in response to party."""
    REACTIVE = "reactive"  # Develops directly counter to party
    PROACTIVE = "proactive"  # Develops to prevent party strengths
    PARALLEL = "parallel"  # Develops along opposite path
    CORRUPTED = "corrupted"  # Twisted version of party's path
    NEGATION = "negation"  # Exists to negate party's efforts

class AntithesisFocus(Enum):
    """What aspect of the party they primarily oppose."""
    MORAL = "moral"  # Opposes their ethical stance
    METHODOLOGICAL = "methodological"  # Opposes their methods
    PHILOSOPHICAL = "philosophical"  # Opposes their beliefs
    PERSONAL = "personal"  # Opposes them personally
    EXISTENTIAL = "existential"  # Opposes their very existence

class AntithesiconService:
    """Generates and evolves antithetical forces to counter the party."""

    def __init__(self, llm_service, background_generator):
        self.llm_service = llm_service
        self.background_generator = background_generator

    async def analyze_party(self,
                          party_data: List[Dict[str, Any]],
                          campaign_notes: List[Dict[str, Any]]) -> PartyProfile:
        """Analyze party to understand what to oppose."""
        prompt = f"""Analyze this party to generate opposition. Return ONLY JSON:

        PARTY:
        {party_data}

        CAMPAIGN NOTES:
        {campaign_notes}

        Create a complete analysis including:
        1. Individual member profiles
        2. Group dynamics
        3. Shared beliefs and methods
        4. Collective strengths/weaknesses
        5. Unresolved conflicts
        6. Moral/ethical stances
        7. Operating methods
        8. Long-term goals

        Focus on elements that can be opposed:
        - Core beliefs
        - Preferred methods
        - Moral choices
        - Group dynamics
        - Individual traits
        - Shared history

        Return complete JSON with party analysis."""

        analysis_data = await self.llm_service.generate_content(prompt)
        return PartyProfile(**analysis_data)

    async def generate_antitheticon(self,
                                  party_profile: PartyProfile,
                                  dm_notes: Dict[str, Any],
                                  focus: AntithesisFocus,
                                  development: AntithesisDevelopment) -> Antitheticon:
        """Generate a complete antithetical force."""
        prompt = f"""Generate an antithetical force to oppose this party. Return ONLY JSON:

        PARTY PROFILE:
        {party_profile}

        DM NOTES:
        {dm_notes}

        FOCUS: {focus.value}
        DEVELOPMENT: {development.value}

        Create an antithetical force that:
        1. Perfectly opposes party traits
        2. Has compelling motivations
        3. Matches party's power level
        4. Has specific counters to each member
        5. Works as coherent group
        6. Has room for growth
        7. Connects to campaign themes
        8. Creates meaningful conflict

        Include:
        - Leadership structure
        - Individual roles
        - Opposition strategy
        - Resource base
        - Current plans
        - Evolution path
        - Personal grudges
        - Specialized counters

        Return complete JSON with antithetical force details."""

        antitheticon_data = await self.llm_service.generate_content(prompt)
        return Antitheticon(**antitheticon_data)

    async def evolve_antitheticon(self,
                                current: Antitheticon,
                                party_changes: List[Dict[str, Any]],
                                dm_notes: Dict[str, Any],
                                campaign_events: List[Dict[str, Any]]) -> Antitheticon:
        """Evolve the antithetical force in response to party development."""
        prompt = f"""Evolve this antithetical force to counter party changes. Return ONLY JSON:

        CURRENT ANTITHETICON:
        {current}

        PARTY CHANGES:
        {party_changes}

        DM NOTES:
        {dm_notes}

        CAMPAIGN EVENTS:
        {campaign_events}

        Evolve the group by:
        1. Countering party growth
        2. Developing new strategies
        3. Acquiring new resources
        4. Evolving relationships
        5. Updating methods
        6. Deepening opposition
        7. Expanding influence
        8. Adapting to failures

        Maintain:
        - Perfect opposition
        - Power balance
        - Compelling narrative
        - Individual counters
        - Group cohesion
        - Strategic depth
        - Growth potential

        Return complete JSON with evolved antithetical force."""

        evolved_data = await self.llm_service.generate_content(prompt)
        return Antitheticon(**evolved_data)

    async def generate_encounter_plan(self,
                                    antitheticon: Antitheticon,
                                    party_profile: PartyProfile,
                                    encounter_type: str,
                                    location: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a tactical plan for an encounter."""
        prompt = f"""Create an encounter plan for this antithetical force. Return ONLY JSON:

        ANTITHETICON:
        {antitheticon}

        PARTY PROFILE:
        {party_profile}

        ENCOUNTER TYPE:
        {encounter_type}

        LOCATION:
        {location}

        Create a plan that:
        1. Exploits party weaknesses
        2. Counters party strengths
        3. Uses environment
        4. Coordinates group actions
        5. Has backup plans
        6. Creates dramatic moments
        7. Advances larger goals
        8. Feels challenging but fair

        Include:
        - Initial setup
        - Key objectives
        - Individual roles
        - Tactical moves
        - Contingency plans
        - Victory conditions
        - Escape routes
        - Dramatic elements

        Return complete JSON with encounter plan."""

        return await self.llm_service.generate_content(prompt)

    async def generate_henchman_group(self,
                                    antitheticon: Antitheticon,
                                    party_profile: PartyProfile,
                                    group_size: int,
                                    theme: str) -> List[Dict[str, Any]]:
        """Generate a group of themed henchmen."""
        prompt = f"""Create themed henchmen for this antithetical force. Return ONLY JSON:

        ANTITHETICON:
        {antitheticon}

        PARTY PROFILE:
        {party_profile}

        GROUP SIZE: {group_size}
        THEME: {theme}

        Create henchmen that:
        1. Support antitheticon's goals
        2. Match the theme
        3. Work together effectively
        4. Have distinct roles
        5. Present appropriate challenge
        6. Feel memorable
        7. Can evolve
        8. Have personality

        For each henchman include:
        - Role in group
        - Special abilities
        - Personality traits
        - Combat tactics
        - Growth potential
        - Loyalty source
        - Distinctive features
        - Personal goals

        Return complete JSON with henchman details."""

        henchmen_data = await self.llm_service.generate_content(prompt)
        return henchmen_data["henchmen"]

    async def evolve_relationship(self,
                                antitheticon: Antitheticon,
                                party_member_id: str,
                                recent_events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Evolve the relationship between an antitheticon member and party member."""
        prompt = f"""Evolve the nemesis relationship. Return ONLY JSON:

        ANTITHETICON:
        {antitheticon}

        PARTY MEMBER ID:
        {party_member_id}

        RECENT EVENTS:
        {recent_events}

        Develop relationship through:
        1. Recent interactions
        2. Deepening conflict
        3. Shifting dynamics
        4. New understanding
        5. Growing hatred
        6. Personal insights
        7. Tactical adaptation
        8. Emotional impact

        Consider:
        - Past encounters
        - Personal grudges
        - Shared experiences
        - Growing opposition
        - Mutual influence
        - Future potential
        - Dramatic moments
        - Character growth

        Return complete JSON with evolved relationship."""

        return await self.llm_service.generate_content(prompt)

    async def suggest_plot_developments(self,
                                     antitheticon: Antitheticon,
                                     party_profile: PartyProfile,
                                     campaign_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest ways to develop the antitheticon's story."""
        prompt = f"""Suggest plot developments for this antithetical force. Return ONLY JSON:

        ANTITHETICON:
        {antitheticon}

        PARTY PROFILE:
        {party_profile}

        CAMPAIGN CONTEXT:
        {campaign_context}

        Generate developments that:
        1. Deepen the conflict
        2. Challenge the party
        3. Reveal new layers
        4. Create moral dilemmas
        5. Force difficult choices
        6. Show character growth
        7. Advance the story
        8. Feel meaningful

        Each suggestion should:
        - Connect to history
        - Involve relationships
        - Use established elements
        - Create tension
        - Offer resolution
        - Enable growth
        - Feel personal
        - Have consequences

        Return complete JSON with plot suggestions."""

        suggestions_data = await self.llm_service.generate_content(prompt)
        return suggestions_data["suggestions"]
