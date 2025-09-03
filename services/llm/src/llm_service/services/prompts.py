"""Prompt templates for text generation."""
from typing import Dict, List, Optional

from llm_service.schemas.text import CharacterContext, TextType


CHARACTER_BACKSTORY = """Create a rich and compelling backstory for a Dungeons & Dragons character with the following details:

Class: {character_class}
Race: {character_race}
Level: {character_level}
Alignment: {alignment}
Background: {background}

The backstory should:
- Explain their motivations for becoming an adventurer
- Include key events and experiences that shaped them
- Fit their alignment and background
- Connect to their class abilities and skills
- Be approximately {max_length} words long
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Focus on creating a narrative that feels personal and unique while adhering to D&D 5e lore and mechanics."""


CHARACTER_PERSONALITY = """Create a detailed personality description for a Dungeons & Dragons character with the following details:

Class: {character_class}
Race: {character_race}
Level: {character_level}
Alignment: {alignment}
Background: {background}

The personality description should include:
- Mannerisms and quirks
- Core values and beliefs
- Likes and dislikes
- Social tendencies
- Notable personality traits
- Fears and aspirations
- How they typically interact with others
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Make the personality feel unique and memorable while fitting their class, race, and alignment."""


CHARACTER_COMBAT = """Create a detailed description of how this Dungeons & Dragons character approaches combat:

Class: {character_class}
Race: {character_race}
Level: {character_level}
Alignment: {alignment}
Background: {background}

The combat description should include:
- Preferred tactics and strategies
- Signature moves or combinations
- How they work with allies
- Attitude toward different types of enemies
- Use of class features and abilities
- Response to different combat situations
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Focus on creating combat behavior that fits their class mechanics while feeling personal and distinctive."""


CHARACTER_EQUIPMENT = """Create detailed descriptions for this Dungeons & Dragons character's equipment and how they use it:

Class: {character_class}
Race: {character_race}
Level: {character_level}
Alignment: {alignment}
Background: {background}

The equipment descriptions should include:
- Visual descriptions of weapons and armor
- How they maintain their equipment
- Personal modifications or decorations
- Stories behind special items
- How they use equipment in and out of combat
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Make the equipment feel personal and lived-in while remaining practical for their class and role."""


CAMPAIGN_PLOT = """Create a campaign plot outline with the following parameters:

Theme: {campaign_theme}
Party Level: {party_level}
Party Size: {party_size}
Duration: {duration}

The plot should:
- Have a compelling central conflict
- Include multiple interesting plot threads
- Offer various paths for resolution
- Scale appropriately for the party level
- Include appropriate challenges and rewards
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Focus on creating engaging plot hooks that give players meaningful choices while maintaining narrative cohesion."""


CAMPAIGN_LOCATION = """Create a detailed description of a location for this campaign:

Theme: {campaign_theme}
Party Level: {party_level}
Party Size: {party_size}
Duration: {duration}

The location description should include:
- Visual atmosphere and layout
- Notable features and landmarks
- Inhabitants and their activities
- Points of interest
- Potential hooks and secrets
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Make the location feel alive and interesting while providing clear opportunities for player interaction."""


CAMPAIGN_QUEST = """Create a quest suitable for this campaign:

Theme: {campaign_theme}
Party Level: {party_level}
Party Size: {party_size}
Duration: {duration}

The quest should include:
- Clear objectives and motivations
- Interesting challenges and obstacles
- Multiple possible approaches
- Appropriate rewards
- Potential complications
- Connection to larger plot threads
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Design the quest to be engaging while scaling appropriately for the party's capabilities."""


CAMPAIGN_DIALOGUE = """Create dialogue and interaction options for an NPC in this campaign:

Theme: {campaign_theme}
Party Level: {party_level}
Party Size: {party_size}
Duration: {duration}

The dialogue should include:
- Distinct voice and personality
- Key information to convey
- Multiple conversation paths
- Potential hooks and secrets
- Reactions to different approaches
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Make the dialogue feel natural while serving the campaign's narrative needs."""


CAMPAIGN_EVENT = """Create a detailed event or encounter for this campaign:

Theme: {campaign_theme}
Party Level: {party_level}
Party Size: {party_size}
Duration: {duration}

The event should include:
- Clear setup and context
- Multiple participant factions
- Various ways to engage
- Potential outcomes
- Impact on the broader story
- Match the following theme and tone:
  - Genre: {genre}
  - Tone: {tone}
  - Style: {style}

Additional context:
{additional_context}

Design the event to be memorable while providing meaningful choices for the players."""


PROMPT_TEMPLATES = {
    TextType.CHARACTER_BACKSTORY: CHARACTER_BACKSTORY,
    TextType.CHARACTER_PERSONALITY: CHARACTER_PERSONALITY,
    TextType.CHARACTER_COMBAT: CHARACTER_COMBAT,
    TextType.CHARACTER_EQUIPMENT: CHARACTER_EQUIPMENT,
    TextType.CAMPAIGN_PLOT: CAMPAIGN_PLOT,
    TextType.CAMPAIGN_LOCATION: CAMPAIGN_LOCATION,
    TextType.CAMPAIGN_QUEST: CAMPAIGN_QUEST,
    TextType.CAMPAIGN_DIALOGUE: CAMPAIGN_DIALOGUE,
    TextType.CAMPAIGN_EVENT: CAMPAIGN_EVENT,
}


def format_character_prompt(
    template: str,
    context: CharacterContext,
    theme: Dict[str, str],
    max_length: Optional[int] = None,
    additional_context: Optional[Dict[str, str]] = None,
) -> str:
    """Format a character-related prompt template."""
    return template.format(
        character_class=context.character_class,
        character_race=context.character_race,
        character_level=context.character_level,
        alignment=context.alignment,
        background=context.background,
        genre=theme.get("genre", "fantasy"),
        tone=theme.get("tone", "serious"),
        style=theme.get("style", "descriptive"),
        max_length=max_length or 500,
        additional_context="\n".join(
            f"- {k}: {v}" for k, v in (additional_context or {}).items()
        ),
    )


def format_campaign_prompt(
    template: str,
    context: Dict[str, str],
    theme: Dict[str, str],
    additional_context: Optional[Dict[str, str]] = None,
) -> str:
    """Format a campaign-related prompt template."""
    return template.format(
        campaign_theme=context["campaign_theme"],
        party_level=context["party_level"],
        party_size=context["party_size"],
        duration=context["duration"],
        genre=theme.get("genre", "fantasy"),
        tone=theme.get("tone", "serious"),
        style=theme.get("style", "descriptive"),
        additional_context="\n".join(
            f"- {k}: {v}" for k, v in (additional_context or {}).items()
        ),
    )


def create_chat_prompt(prompt: str) -> List[Dict[str, str]]:
    """Convert a text prompt into a chat message format."""
    return [
        {
            "role": "system",
            "content": "You are a creative assistant specializing in D&D 5e content generation. "
                      "Your responses should be richly detailed while remaining true to D&D lore and mechanics."
        },
        {
            "role": "user",
            "content": prompt,
        }
    ]
