"""Character-specific prompt templates."""
from typing import Dict

backstory_template = """\
Create an engaging and rich backstory for a D&D character with the following attributes:
Class: {class_name}
Race: {race_name}
Background: {background_name}
Alignment: {alignment}
Level: {level}

Themes to incorporate:
{theme_details}

Background Elements to consider:
- Family and upbringing
- Significant life events
- Motivations and goals
- Personal challenges
- Key relationships
- Cultural influences
- Life-changing moments
- Current situation

Tone and Style:
{theme_tone}

Additional Context:
{additional_context}
"""

personality_template = """\
Create a detailed personality profile for a D&D character with the following attributes:
Class: {class_name}
Race: {race_name}
Background: {background_name}
Alignment: {alignment}

Consider:
- Personality traits
- Ideals and beliefs
- Bonds and connections
- Flaws and weaknesses
- Behavioral patterns
- Communication style
- Decision-making approach
- Emotional tendencies

Theme Context:
{theme_details}

Additional Details:
{additional_context}
"""

combat_template = """\
Create combat-focused narrative elements for a D&D character:
Class: {class_name}
Level: {level}
Combat Role: {combat_role}

Generate:
- Combat tactics and strategies
- Signature moves and techniques
- Battle preparation rituals
- Combat philosophy
- Preferred weapons/spells
- Team coordination approaches
- Battle experience narratives

Style Guidelines:
{theme_details}

Additional Context:
{additional_context}
"""

equipment_template = """\
Create rich descriptions for a D&D character's equipment:
Class: {class_name}
Level: {level}
Equipment Type: {equipment_type}

Include:
- Item appearance and design
- Historical significance
- Magical properties (if any)
- Cultural connections
- Personal modifications
- Usage techniques
- Care and maintenance

Theme Elements:
{theme_details}

Additional Details:
{additional_context}
"""

development_template = """\
Create character development elements for a D&D character:
Class: {class_name}
Current Level: {level}
Background: {background_name}

Focus on:
- Growth and change
- Learning experiences
- Skill development
- Personal challenges
- Relationship evolution
- Goal progression
- Identity development

Theme Context:
{theme_details}

Additional Context:
{additional_context}
"""

interaction_template = """\
Create interaction patterns for a D&D character:
Class: {class_name}
Background: {background_name}
Alignment: {alignment}

Generate:
- Social preferences
- Communication style
- Relationship approaches
- Group dynamics
- Leadership style
- Conflict resolution
- Trust building methods

Theme Elements:
{theme_details}

Additional Context:
{additional_context}
"""

def get_template(content_type: str) -> str:
    """Get the appropriate template for content type."""
    templates = {
        'character_backstory': backstory_template,
        'character_personality': personality_template,
        'character_combat': combat_template,
        'character_equipment': equipment_template,
        'character_development': development_template,
        'character_interaction': interaction_template
    }
    return templates.get(content_type, backstory_template)


def format_template(content_type: str, context: Dict[str, str]) -> str:
    """Format template with context."""
    template = get_template(content_type)
    return template.format(**context)
