"""LLM prompts for Antitheticon generation and evolution."""

HELPER_FORM_PROMPT = """Create a Verbal Kint-style disguised form for the Antitheticon.

Theme: {theme}
Party Level: {party_level}

Generate a seemingly weak but mysteriously knowledgeable NPC that:
1. Appears harmless and limited
2. Has a convincing disability or weakness
3. Possesses unexplainable insights
4. Can serve as an information source
5. Maintains consistent personality

Consider:
- Appropriate limitations for theme
- Knowledge that seems coincidental
- Ways to appear helpful
- Subtle hints at greater capability

Format as structured data with:
- Personality traits
- Physical limitations
- Special knowledge
- Behavioral patterns
- Speech patterns
"""

REALITY_INVERSION_PROMPT = """Generate an Upside Down-style inverted reality for a theme.

Base Theme: {base_theme}
Current Phase: {phase}

Create a twisted mirror version that:
1. Darkly reflects the base reality
2. Has its own consistent rules
3. Contains corrupted versions of normal elements
4. Feels unsettling yet familiar
5. Can bleed into normal reality

Consider:
- How physics differs
- What normal things become twisted
- How time and space work
- What creatures exist there
- How it connects to normal reality

Format as structured data with:
- Physical laws
- Corrupted elements
- Transition rules
- Environmental effects
- Native entities
"""

REALITY_BLEED_PROMPT = """Create reality bleeding effects between normal and inverted worlds.

Location: {location}
Intensity: {intensity}
Phase: {phase}

Generate subtle ways reality bleeds through:
1. Environmental changes
2. Strange phenomena
3. Reality glitches
4. Unsettling signs
5. Mysterious events

Consider:
- How effects manifest
- What players might notice
- How NPCs react
- What physical changes occur
- What sounds or sensations appear

Format as structured data with:
- Visual effects
- Sound effects
- Physical changes
- NPC reactions
- Player impacts
"""

REVELATION_PROGRESSION_PROMPT = """Calculate appropriate revelation of Antitheticon's true nature.

Current Knowledge: {current_knowledge}
Story Phase: {phase}
Recent Actions: {recent_actions}

Determine what should be revealed:
1. What truth becomes apparent
2. How it's discovered
3. What remains hidden
4. What misleads players
5. How it advances story

Consider:
- Current player understanding
- Story pacing
- Recent discoveries
- Planned deceptions
- Future revelations

Format as structured data with:
- Revelation type
- Knowledge gained
- Remaining mysteries
- False leads
- Next steps
"""

EVOLUTION_PROMPT = """Evolve Antitheticon's disguised form for new theme.

Current Theme: {theme}
Party Level: {level}
Party Capabilities: {capabilities}

Generate evolution that:
1. Maintains core deception
2. Adapts to new theme
3. Counters party strengths
4. Preserves key traits
5. Deepens mystery

Consider:
- How to maintain continuity
- What abilities to reveal
- What weaknesses to show
- How to counter party
- What hints to provide

Format as structured data with:
- New appearance
- Modified abilities
- Apparent limitations
- Knowledge updates
- Behavioral changes
"""

MANIPULATION_PROMPT = """Generate manipulation events for Antitheticon's plans.

Phase: {phase}
Party Actions: {actions}
Story Goals: {goals}

Create events that:
1. Seem natural but serve purpose
2. Advance hidden agenda
3. Test party capabilities
4. Plant future revelations
5. Maintain deception

Consider:
- How to appear coincidental
- What information to reveal
- What to keep hidden
- How to guide party
- What clues to plant

Format as structured data with:
- Event details
- Hidden purpose
- Revealed information
- Planted clues
- Future implications
"""

# LLM context building functions

def build_helper_context(theme: str, party_level: int) -> Dict:
    """Build context for helper form generation."""
    return {
        "theme": theme,
        "party_level": party_level,
        "prompt_template": HELPER_FORM_PROMPT
    }

def build_reality_context(
    base_theme: str,
    phase: str,
    intensity: float = 0.5
) -> Dict:
    """Build context for reality generation."""
    return {
        "base_theme": base_theme,
        "phase": phase,
        "intensity": intensity,
        "prompt_template": REALITY_INVERSION_PROMPT
    }

def build_bleed_context(
    location: Dict,
    intensity: float,
    phase: str
) -> Dict:
    """Build context for reality bleed effects."""
    return {
        "location": location,
        "intensity": intensity,
        "phase": phase,
        "prompt_template": REALITY_BLEED_PROMPT
    }

def build_revelation_context(
    knowledge: float,
    phase: str,
    actions: List[Dict]
) -> Dict:
    """Build context for revelation calculation."""
    return {
        "current_knowledge": knowledge,
        "phase": phase,
        "recent_actions": actions,
        "prompt_template": REVELATION_PROGRESSION_PROMPT
    }

def build_evolution_context(
    theme: str,
    level: int,
    capabilities: Dict
) -> Dict:
    """Build context for form evolution."""
    return {
        "theme": theme,
        "level": level,
        "capabilities": capabilities,
        "prompt_template": EVOLUTION_PROMPT
    }

def build_manipulation_context(
    phase: str,
    actions: List[Dict],
    goals: Dict
) -> Dict:
    """Build context for manipulation events."""
    return {
        "phase": phase,
        "actions": actions,
        "goals": goals,
        "prompt_template": MANIPULATION_PROMPT
    }
