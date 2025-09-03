# Antitheticon Implementation Specification

## Service Architecture

### 1. Core Components
```python
# Key services that enable Antitheticon mechanics
services/
    antitheticon/
        disguise_service.py       # Manages NPC facade
        reality_service.py        # Handles reality pairs
        manipulation_service.py   # Controls story/events
        progression_service.py    # Manages evolution
```

### 2. Data Models
```python
models/
    antitheticon/
        disguise_forms.py      # NPC appearances
        reality_states.py      # World states
        theme_mappings.py      # Reality transitions
        event_orchestration.py # Manipulation tracking
```

## Disguise System Implementation

### 1. NPC Generation
```python
class DisguiseService:
    async def generate_helper_form(self, theme: str, party_level: int):
        """Creates themed helper NPC form."""
        context = {
            "theme": theme,
            "party_level": party_level,
            "archetype": "disabled_informant",
            "knowledge_level": "suspiciously_helpful"
        }
        
        # Use LLM to generate consistent personality
        personality = await self.ai_client.generate_personality(context)
        
        # Create NPC stats and abilities
        stats = await self.npc_service.create_npc(
            level=party_level-1,  # Appear slightly weaker
            limitations=personality.limitations,
            special_knowledge=personality.insights
        )
        
        return DisguisedForm(personality=personality, stats=stats)
```

### 2. Information Management
```python
class InformationController:
    async def craft_revelation(
        self,
        truth_ratio: float,
        story_phase: str,
        party_knowledge: Dict
    ):
        """Crafts partially true information to advance story."""
        # Determine what truth to reveal
        reveal_context = {
            "known_facts": party_knowledge,
            "truth_ratio": truth_ratio,
            "story_phase": story_phase
        }
        
        # Use LLM to craft information
        revelation = await self.ai_client.craft_information(reveal_context)
        
        # Track what's been revealed
        await self.knowledge_tracker.update(revelation)
        
        return revelation
```

## Reality System Implementation

### 1. Theme Pair Generation
```python
class RealityService:
    async def create_reality_pair(self, base_theme: str):
        """Creates normal and inverted versions of a theme."""
        # Generate inverted theme
        inversion_context = {
            "base_theme": base_theme,
            "corruption_level": "unsettling",
            "reality_rules": "twisted_mirror"
        }
        
        inverted = await self.ai_client.generate_inverted_theme(
            inversion_context
        )
        
        # Create paired realities
        reality_pair = RealityPair(
            normal=await self.world_service.create_world(base_theme),
            inverted=await self.world_service.create_world(inverted)
        )
        
        return reality_pair
```

### 2. Reality Transition System
```python
class RealityTransitionController:
    async def create_reality_bleed(
        self,
        location: Location,
        intensity: float,
        phase: str
    ):
        """Creates reality bleeding effects between pairs."""
        # Generate transition effects
        effects = await self.ai_client.generate_reality_effects({
            "location": location,
            "intensity": intensity,
            "phase": phase
        })
        
        # Apply to both realities
        await self.world_service.apply_effects(effects)
        
        return RealityBleedEvent(location, effects)
```

## Manipulation System Implementation

### 1. Event Orchestration
```python
class ManipulationService:
    async def orchestrate_event(
        self,
        phase: str,
        party_actions: List[Action],
        story_goals: Dict
    ):
        """Orchestrates events to appear natural but serve purpose."""
        # Analyze party actions
        analysis = await self.ai_client.analyze_party_behavior(party_actions)
        
        # Generate appropriate response
        event = await self.event_generator.create_event({
            "phase": phase,
            "party_analysis": analysis,
            "goals": story_goals
        })
        
        # Track manipulation
        await self.manipulation_tracker.record(event)
        
        return OrchestrationEvent(event)
```

### 2. Story Weaving
```python
class StoryController:
    async def weave_narrative(
        self,
        true_events: List[Event],
        false_events: List[Event],
        revelation_timing: float
    ):
        """Weaves true and false events into coherent narrative."""
        narrative = await self.ai_client.generate_narrative({
            "truth": true_events,
            "fiction": false_events,
            "timing": revelation_timing
        })
        
        return NarrativeSequence(narrative)
```

## Progression System Implementation

### 1. Evolution Tracking
```python
class ProgressionService:
    async def evolve_antitheticon(
        self,
        party_level: int,
        revealed_knowledge: float,
        story_phase: str
    ):
        """Evolves Antitheticon based on party progress."""
        evolution = await self.ai_client.generate_evolution({
            "current_level": party_level + 1,
            "knowledge_revealed": revealed_knowledge,
            "phase": story_phase
        })
        
        return EvolutionState(evolution)
```

### 2. Revelation Management
```python
class RevelationController:
    async def manage_discovery(
        self,
        current_knowledge: float,
        story_progress: float,
        party_actions: List[Action]
    ):
        """Manages the gradual revelation of truth."""
        revelation = await self.ai_client.calculate_revelation({
            "known": current_knowledge,
            "progress": story_progress,
            "party_behavior": party_actions
        })
        
        return RevelationState(revelation)
```

## Integration Points

### 1. Character Service Integration
```python
async def integrate_with_character_service(self):
    """Integrates with character service for NPC management."""
    # Register NPC forms
    await self.character_service.register_templates({
        "helper_forms": self.disguise_service.get_templates(),
        "transformation_rules": self.evolution_service.get_rules()
    })
```

### 2. World Service Integration
```python
async def integrate_with_world_service(self):
    """Integrates with world service for reality management."""
    # Register reality pairs
    await self.world_service.register_realities({
        "normal_themes": self.reality_service.get_normal_themes(),
        "inverted_themes": self.reality_service.get_inverted_themes(),
        "transition_rules": self.reality_service.get_transition_rules()
    })
```

### 3. Event Service Integration
```python
async def integrate_with_event_service(self):
    """Integrates with event service for story manipulation."""
    # Register event handlers
    await self.event_service.register_handlers({
        "orchestration": self.manipulation_service.get_handlers(),
        "revelation": self.progression_service.get_handlers()
    })
```

## Example Usage

### 1. Creating a Disguised Form
```python
# Create helper NPC for cyberpunk theme
helper = await disguise_service.generate_helper_form(
    theme="cyberpunk",
    party_level=5
)

# Generate appropriate information
info = await information_controller.craft_revelation(
    truth_ratio=0.7,
    story_phase="early_game",
    party_knowledge=current_knowledge
)
```

### 2. Managing Reality Transitions
```python
# Create reality pair for theme
reality_pair = await reality_service.create_reality_pair(
    base_theme="cyberpunk"
)

# Create reality bleed effect
bleed = await transition_controller.create_reality_bleed(
    location=current_location,
    intensity=0.3,
    phase="mid_game"
)
```

### 3. Orchestrating Events
```python
# Create manipulated event
event = await manipulation_service.orchestrate_event(
    phase="early_game",
    party_actions=recent_actions,
    story_goals=campaign_goals
)

# Manage revelation timing
revelation = await revelation_controller.manage_discovery(
    current_knowledge=known_truth,
    story_progress=progress,
    party_actions=recent_actions
)
```

This implementation provides the technical foundation to create a dynamic, evolving Antitheticon that:
1. Maintains consistent disguises across themes
2. Manages paired realities effectively
3. Orchestrates events and manipulations
4. Controls the pace of revelations
5. Evolves alongside the party
