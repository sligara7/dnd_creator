"""Deep background generation for characters that evolves with their experiences."""

from typing import Dict, List, Optional, Any, Set
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

@dataclass
class PersonalityTraits:
    """Character's core personality traits."""
    virtues: List[Dict[str, str]]  # trait -> description/example
    flaws: List[Dict[str, str]]
    beliefs: List[Dict[str, str]]
    fears: List[Dict[str, str]]
    regrets: List[Dict[str, str]]
    hopes: List[Dict[str, str]]
    motivations: List[Dict[str, str]]

@dataclass
class Relationship:
    """Character's relationship with another entity."""
    entity_id: str
    relationship_type: str  # friend, mentor, rival, enemy, etc.
    history: List[Dict[str, Any]]  # chronological events
    current_status: str
    emotional_impact: str
    influence_on_character: str
    potential_future: str

@dataclass
class LifeEvent:
    """Significant event in character's life."""
    timestamp: datetime
    event_type: str
    description: str
    location: str
    involved_entities: List[str]  # entity IDs
    emotional_impact: str
    lasting_effects: List[str]
    related_events: List[str]  # event IDs

@dataclass
class Background:
    """Complete character background."""
    early_life: Dict[str, Any]
    formative_events: List[LifeEvent]
    relationships: Dict[str, Relationship]
    personality: PersonalityTraits
    cultural_influences: List[Dict[str, str]]
    professional_history: List[Dict[str, Any]]
    personal_growth: List[Dict[str, Any]]
    current_goals: List[Dict[str, str]]
    unresolved_conflicts: List[Dict[str, str]]
    secrets: List[Dict[str, str]]

class BackgroundGenerator:
    """Generates and evolves character backgrounds."""

    def __init__(self, llm_service):
        self.llm_service = llm_service

    async def generate_initial_background(self,
                                       character_data: Dict[str, Any],
                                       species_lore: Dict[str, Any],
                                       class_lore: Dict[str, Any]) -> Background:
        """Generate initial background considering species and class."""
        prompt = f"""Generate a deep, nuanced background for this character. Return ONLY JSON:

        CHARACTER:
        {character_data}

        SPECIES LORE:
        {species_lore}

        CLASS LORE:
        {class_lore}

        Create a background that:
        1. Fits species cultural norms and tendencies
        2. Aligns with class training and philosophies
        3. Includes both triumphs and failures
        4. Features complex relationships
        5. Contains inner conflicts
        6. Has unresolved issues
        7. Shows clear motivations
        8. Explains current abilities
        9. Sets up future growth
        10. Includes secrets and regrets

        Consider how their species and class would shape their:
        - Early experiences
        - Cultural values
        - Training methods
        - Relationships
        - Life choices
        - Personal conflicts
        - Current outlook

        Make them feel like a real person who has:
        - Made mistakes
        - Learned hard lessons
        - Lost something important
        - Achieved meaningful goals
        - Built relationships
        - Grown and changed
        - Developed beliefs
        - Acquired regrets
        - Maintained hopes

        Return complete JSON with detailed background."""

        background_data = await self.llm_service.generate_content(prompt)
        return Background(**background_data)

    async def evolve_background(self,
                              current_background: Background,
                              campaign_notes: List[Dict[str, Any]],
                              journal_entries: List[Dict[str, Any]],
                              level_up_data: Optional[Dict[str, Any]] = None,
                              theme_change: Optional[Dict[str, Any]] = None) -> Background:
        """Evolve background based on experiences and changes."""
        prompt = f"""Evolve this character's background based on recent experiences. Return ONLY JSON:

        CURRENT BACKGROUND:
        {current_background}

        CAMPAIGN NOTES:
        {campaign_notes}

        JOURNAL ENTRIES:
        {journal_entries}

        LEVEL UP DATA:
        {level_up_data}

        THEME CHANGE:
        {theme_change}

        Evolve the background by:
        1. Incorporating recent experiences
        2. Developing existing relationships
        3. Adding new relationships
        4. Evolving personality traits
        5. Updating goals and motivations
        6. Adding new regrets or fears
        7. Resolving or complicating conflicts
        8. Deepening existing themes
        9. Adding new layers of complexity
        10. Maintaining consistency with past

        Show how they've changed through:
        - Lessons learned
        - Relationships affected
        - New perspectives gained
        - Skills developed
        - Fears confronted
        - Beliefs challenged
        - Goals adjusted
        - Regrets processed

        Return complete JSON with evolved background."""

        evolved_data = await self.llm_service.generate_content(prompt)
        return Background(**evolved_data)

    async def generate_nemesis(self,
                             character_background: Background,
                             campaign_notes: List[Dict[str, Any]],
                             journal_entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate or evolve a nemesis based on character's history."""
        prompt = f"""Create/evolve a compelling nemesis for this character. Return ONLY JSON:

        CHARACTER BACKGROUND:
        {character_background}

        CAMPAIGN NOTES:
        {campaign_notes}

        JOURNAL ENTRIES:
        {journal_entries}

        Create a nemesis that:
        1. Has personal history with character
        2. Represents opposing ideals
        3. Has legitimate grievances
        4. Matches character's capabilities
        5. Has their own complex background
        6. Shows signs of evolution
        7. Has understandable motivations
        8. Creates meaningful conflict
        9. Challenges character's beliefs
        10. Has potential for development

        Include:
        - Shared history
        - Personal grudges
        - Philosophical conflicts
        - Future plans
        - Potential allies
        - Resources and capabilities
        - Psychological profile
        - Long-term goals

        Return complete JSON with nemesis details."""

        return await self.llm_service.generate_content(prompt)

    async def generate_relationship_development(self,
                                             relationship: Relationship,
                                             recent_events: List[Dict[str, Any]]) -> Relationship:
        """Develop a specific relationship based on recent events."""
        prompt = f"""Evolve this relationship based on recent events. Return ONLY JSON:

        CURRENT RELATIONSHIP:
        {relationship}

        RECENT EVENTS:
        {recent_events}

        Develop the relationship by:
        1. Processing recent interactions
        2. Evolving dynamics
        3. Adding complications
        4. Deepening connections
        5. Creating new tensions
        6. Resolving old issues
        7. Setting up future developments
        8. Maintaining consistency

        Consider impact on:
        - Trust levels
        - Emotional bonds
        - Shared experiences
        - Future expectations
        - Unresolved issues
        - Mutual understanding
        - Power dynamics
        - Personal growth

        Return complete JSON with evolved relationship."""

        relationship_data = await self.llm_service.generate_content(prompt)
        return Relationship(**relationship_data)

    async def suggest_background_hooks(self,
                                    background: Background,
                                    campaign_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest plot hooks based on character background."""
        prompt = f"""Suggest plot hooks from this character's background. Return ONLY JSON:

        BACKGROUND:
        {background}

        CAMPAIGN CONTEXT:
        {campaign_context}

        Generate hooks involving:
        1. Unresolved conflicts
        2. Past relationships
        3. Secret histories
        4. Personal regrets
        5. Future goals
        6. Cultural ties
        7. Professional connections
        8. Inner struggles
        9. Missed opportunities
        10. Potential developments

        Each hook should:
        - Connect to background
        - Fit campaign context
        - Enable character growth
        - Create meaningful conflict
        - Involve key relationships
        - Challenge beliefs
        - Offer choices
        - Have consequences

        Return complete JSON with hook suggestions."""

        hooks_data = await self.llm_service.generate_content(prompt)
        return hooks_data["hooks"]

    async def generate_internal_monologue(self,
                                       background: Background,
                                       recent_event: Dict[str, Any]) -> str:
        """Generate character's internal thoughts about an event."""
        prompt = f"""Create internal monologue for this character about a recent event. Return ONLY JSON:

        BACKGROUND:
        {background}

        EVENT:
        {recent_event}

        Generate thoughts that:
        1. Reflect personality
        2. Show inner conflicts
        3. Reference past experiences
        4. Connect to relationships
        5. Reveal emotions
        6. Question motives
        7. Consider consequences
        8. Show growth

        Format as stream-of-consciousness that:
        - Feels natural
        - Shows complexity
        - Reveals character
        - Maintains voice
        - Adds depth

        Return JSON with internal monologue."""

        monologue_data = await self.llm_service.generate_content(prompt)
        return monologue_data["monologue"]
