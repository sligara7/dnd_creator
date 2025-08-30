"""Core service for generating and managing Antitheticons."""

from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

from .antitheticon_storyline import (
    AntithesiconStorylineService,
    StoryFocus,
    StorylineDevelopment,
    StoryThread,
    CharacterArc,
    BackstoryElement,
    MinionGroup
)

class AntithesisFocus(Enum):
    """Primary focus for the Antitheticon."""
    MORAL = "moral"  # Moral/ethical opposition
    TACTICAL = "tactical"  # Combat/strategy opposition
    PERSONAL = "personal"  # Character history opposition
    THEMATIC = "thematic"  # Theme/story opposition
    COMPOSITE = "composite"  # Mix of multiple focuses

class AntithesisDevelopment(Enum):
    """How the Antitheticon develops over time."""
    CORRUPTED = "corrupted"  # Fall from grace
    PARALLEL = "parallel"  # Dark mirror
    INVERTED = "inverted"  # Opposite path
    TWISTED = "twisted"  # Perversion of ideals
    REACTIVE = "reactive"  # Shaped by party actions

@dataclass
class Antitheticon:
    """A perfect nemesis for the party."""
    id: str
    name: str
    focus: AntithesisFocus
    development: AntithesisDevelopment
    leader: Dict[str, Any]  # Main antagonist
    core_members: List[Dict[str, Any]]  # Key supporters
    minions: List[MinionGroup]  # Groups of lesser followers
    base: Dict[str, Any]  # Base of operations
    resources: Dict[str, Any]  # Available assets
    story_threads: List[StoryThread]  # Active narrative elements
    character_arcs: Dict[str, CharacterArc]  # Development tracks
    backstory: List[BackstoryElement]  # History elements
    tactics: Dict[str, Any]  # Combat/conflict approaches
    relationships: Dict[str, Dict[str, Any]]  # Links to party

class AntithesiconService:
    """Service for generating and managing Antitheticons."""

    def __init__(self, llm_service, campaign_service, background_generator):
        self.llm_service = llm_service
        self.campaign_service = campaign_service
        self.storyline_service = AntithesiconStorylineService(
            llm_service, background_generator)
        self.active_antitheticons: Dict[str, Antitheticon] = {}

    async def analyze_party(self,
                         party_data: List[Dict[str, Any]],
                         campaign_notes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze party for opposition generation."""
        prompt = f"""Analyze this party for nemesis creation. Return ONLY JSON:

        PARTY:
        {party_data}

        CAMPAIGN NOTES:
        {campaign_notes}

        Analyze for:
        1. Individual character traits
        2. Group dynamics
        3. Moral/ethical stances
        4. Combat/tactical approaches
        5. Key relationships
        6. Shared beliefs
        7. Potential weaknesses
        8. Growth patterns

        Return complete JSON analysis."""

        return await self.llm_service.generate_content(prompt)

    async def generate_antitheticon(self,
                                 party_profile: Dict[str, Any],
                                 dm_notes: Dict[str, Any],
                                 focus: AntithesisFocus,
                                 development: AntithesisDevelopment) -> Antitheticon:
        """Generate a new Antitheticon."""
        prompt = f"""Generate perfect nemesis group. Return ONLY JSON:

        PARTY PROFILE:
        {party_profile}

        DM NOTES:
        {dm_notes}

        FOCUS: {focus.value}
        DEVELOPMENT: {development.value}

        Generate complete opposition:
        1. Perfect counter to party
        2. Deep motivations
        3. Rich backstory
        4. Tactical capabilities
        5. Growth potential
        6. Personal connections
        7. Resource network
        8. Future implications

        Return complete JSON for nemesis group."""

        antitheticon_data = await self.llm_service.generate_content(prompt)
        
        # Generate initial story threads
        story_threads = await self.storyline_service.suggest_story_developments(
            antitheticon_data,
            StoryFocus.THEMATIC,
            StorylineDevelopment.PLANNED
        )

        # Create character arcs
        character_arcs = {}
        for member in [antitheticon_data["leader"]] + antitheticon_data["core_members"]:
            arc = await self.storyline_service.evolve_character_arc(
                None,  # New arc
                [],  # No events yet
                dm_notes
            )
            character_arcs[member["id"]] = arc

        # Initialize minion groups
        minions = []
        for group_data in antitheticon_data.get("minion_groups", []):
            group = await self.storyline_service.generate_linked_minion_group(
                antitheticon_data,
                party_profile["members"],
                group_data["theme"],
                group_data["size"]
            )
            minions.append(group)

        antitheticon = Antitheticon(
            id=antitheticon_data["id"],
            name=antitheticon_data["name"],
            focus=focus,
            development=development,
            leader=antitheticon_data["leader"],
            core_members=antitheticon_data["core_members"],
            minions=minions,
            base=antitheticon_data["base"],
            resources=antitheticon_data["resources"],
            story_threads=story_threads,
            character_arcs=character_arcs,
            backstory=antitheticon_data["backstory"],
            tactics=antitheticon_data["tactics"],
            relationships=antitheticon_data["relationships"]
        )

        self.active_antitheticons[antitheticon.id] = antitheticon
        return antitheticon

    async def evolve_antitheticon(self,
                               antitheticon: Antitheticon,
                               party_changes: List[Dict[str, Any]],
                               dm_notes: List[Dict[str, Any]],
                               campaign_events: List[Dict[str, Any]]) -> Antitheticon:
        """Evolve an Antitheticon based on recent developments."""
        # Process all incoming changes
        changes = await self.storyline_service.process_stream_event(
            {
                "party_changes": party_changes,
                "dm_notes": dm_notes,
                "campaign_events": campaign_events
            },
            antitheticon.story_threads,
            list(antitheticon.character_arcs.values())
        )

        # Update story threads
        for thread_update in changes.get("thread_updates", []):
            thread_id = thread_update["thread_id"]
            for thread in antitheticon.story_threads:
                if thread.thread_id == thread_id:
                    # Apply updates to thread
                    for key, value in thread_update.items():
                        if hasattr(thread, key):
                            setattr(thread, key, value)

        # Evolve character arcs
        for arc_update in changes.get("arc_updates", []):
            char_id = arc_update["character_id"]
            if char_id in antitheticon.character_arcs:
                arc = await self.storyline_service.evolve_character_arc(
                    antitheticon.character_arcs[char_id],
                    party_changes,
                    dm_notes
                )
                antitheticon.character_arcs[char_id] = arc

        # Update tactics and resources
        antitheticon.tactics.update(changes.get("tactical_changes", {}))
        antitheticon.resources.update(changes.get("resource_changes", {}))

        # Evolve relationships
        for rel_update in changes.get("relationship_updates", []):
            char_id = rel_update["character_id"]
            if char_id in antitheticon.relationships:
                relationship = await self.storyline_service.evolve_relationship(
                    antitheticon,
                    char_id,
                    campaign_events
                )
                antitheticon.relationships[char_id] = relationship

        # Update minions if needed
        for minion_update in changes.get("minion_updates", []):
            group_id = minion_update["group_id"]
            for group in antitheticon.minions:
                if group.group_id == group_id:
                    # Apply updates to minion group
                    for key, value in minion_update.items():
                        if hasattr(group, key):
                            setattr(group, key, value)

        self.active_antitheticons[antitheticon.id] = antitheticon
        return antitheticon

    async def generate_encounter_plan(self,
                                   antitheticon: Antitheticon,
                                   party_profile: Dict[str, Any],
                                   encounter_type: str,
                                   location: Dict[str, Any]) -> Dict[str, Any]:
        """Generate tactical encounter plan."""
        prompt = f"""Create encounter plan for Antitheticon. Return ONLY JSON:

        ANTITHETICON:
        {antitheticon}

        PARTY:
        {party_profile}

        TYPE: {encounter_type}
        LOCATION: {location}

        Plan should include:
        1. Initial setup
        2. Combat tactics
        3. Character counters
        4. Environmental use
        5. Special abilities
        6. Contingencies
        7. Victory conditions
        8. Escape plans

        Return complete JSON plan."""

        return await self.llm_service.generate_content(prompt)

    async def suggest_developments(self,
                                antitheticon: Antitheticon,
                                party_profile: Dict[str, Any],
                                campaign_context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Suggest potential story developments."""
        return await self.storyline_service.suggest_story_developments(
            {
                "antitheticon": antitheticon,
                "party": party_profile,
                "context": campaign_context
            },
            StoryFocus.COMPOSITE,
            StorylineDevelopment.HYBRID
        )

    async def process_journal_entry(self,
                                 entry: Dict[str, Any],
                                 antitheticon_id: str) -> Dict[str, Any]:
        """Process a new journal entry."""
        antitheticon = self.active_antitheticons.get(antitheticon_id)
        if not antitheticon:
            raise ValueError(f"No active Antitheticon with ID: {antitheticon_id}")

        updates = await self.storyline_service.integrate_journal_entries(
            [entry],
            antitheticon.story_threads,
            list(antitheticon.character_arcs.values())
        )

        # Apply updates to Antitheticon
        for update_type, update_data in updates.items():
            if update_type == "story_threads":
                antitheticon.story_threads = update_data
            elif update_type == "character_arcs":
                antitheticon.character_arcs.update(update_data)
            elif update_type == "backstory":
                antitheticon.backstory.extend(update_data)
            # Add other update types as needed

        self.active_antitheticons[antitheticon_id] = antitheticon
        return updates
