# Character Service Integration Documentation

## Overview

The campaign service now integrates with the D&D character creation backend service to automatically generate NPCs and monsters for campaigns and chapters. This integration ensures that generated characters are consistent with the campaign's genre and theme while supporting custom species/classes beyond traditional D&D types.

## Key Features

### 1. Automatic Quantity Determination
- **NPC Quantities**: Automatically determines 2-4 major NPCs and 3-8 minor NPCs per chapter based on:
  - Campaign complexity (simple/medium/complex)
  - Chapter narrative requirements
  - Party size and level
  - Session time constraints

- **Monster Quantities**: Generates 1-4 different monster types with 1-8 creatures each based on:
  - Party level and challenge rating calculations
  - Chapter encounter balance requirements
  - Narrative pacing needs

### 2. Challenge Rating Calculation
- NPCs receive social complexity ratings equivalent to challenge ratings
- Monsters get appropriate CRs based on party level and encounter difficulty curves
- Automatic balancing to create easy/medium/hard/deadly encounter distributions

### 3. Genre and Theme Consistency
- **Genre Filtering**: Characters are generated to fit campaign genres:
  - `fantasy` → Traditional D&D races, medieval settings
  - `sci_fi` → Aliens, androids, space-age technology
  - `cyberpunk` → Cyborgs, hackers, corporate agents
  - `horror` → Undead, cultists, aberrations
  - `western` → Outlaws, sheriffs, frontier folk
  - `steampunk` → Inventors, automata, Victorian-era characters

- **Theme Adaptation**: Characters reflect campaign themes:
  - `CYBERPUNK` → Corporate terminology, hacking skills, cyber-enhanced abilities
  - `WESTERN` → Gunslinger classes, frontier backgrounds, lawman roles
  - `HORROR` → Psychological traits, supernatural elements, moral ambiguity

### 4. Custom Species and Classes
- System supports generation of non-traditional D&D character types
- Custom species examples:
  - **Sci-Fi**: `AI_construct`, `genetically_modified_human`, `crystalline_being`
  - **Cyberpunk**: `cyborg`, `neural_interface_enhanced`, `bio_android`
  - **Steampunk**: `clockwork_automaton`, `aether_touched`, `steam_powered_construct`
  - **Horror**: `shadow_touched`, `possessed_human`, `eldritch_hybrid`

- Custom classes adapt existing mechanics:
  - `netrunner` (cyberpunk hacker using wizard mechanics)
  - `gunslinger` (western fighter with firearm specialization)
  - `mad_scientist` (steampunk artificer with experimental focus)
  - `occult_investigator` (horror-themed knowledge cleric)

## Service Integration Architecture

### CharacterServiceClient
- HTTP client for communicating with `/backend` character creation service
- Handles request/response formatting and error handling
- Provides fallback character generation when backend is unavailable
- Supports batch character generation for efficiency

### CampaignCharacterIntegrator
- Analyzes campaign context to determine character requirements
- Uses LLM to assess chapter needs and generate appropriate character specifications
- Coordinates between campaign service and character creation service
- Ensures narrative consistency across generated characters

### Integration Points

#### 1. Chapter Generation
```python
# Enhanced chapter generation with character service
chapter_data = await chapter_generator.generate_chapter_content(
    campaign_title=campaign_title,
    campaign_description=campaign_description,
    chapter_title=chapter_title,
    chapter_summary=chapter_summary,
    themes=themes,
    campaign_context=campaign_context,  # ← NEW: Campaign context
    use_character_service=True          # ← NEW: Enable integration
)
```

#### 2. Campaign Factory
```python
# Campaign creation with character integration
campaign_result = await factory.create_from_scratch(
    CampaignCreationOptions.CHAPTER_CONTENT,
    "chapter concept...",
    genre=CampaignGenre.CYBERPUNK,
    setting_theme=SettingTheme.CYBERPUNK,
    party_level=5,
    use_character_service=True
)
```

## API Communication

### Request Format
```json
{
  "creation_type": "npc",
  "options": {
    "genre": "cyberpunk",
    "theme": "cyberpunk",
    "complexity": "medium",
    "challenge_rating": 2,
    "party_level": 3,
    "narrative_role": "major",
    "custom_species": ["cyborg", "AI_enhanced_human"],
    "custom_classes": ["netrunner", "corpo_operative"],
    "cultural_background": "corporate_dystopia",
    "motivations": ["profit", "survival", "revenge"],
    "relationships": ["ally_to_party", "rival_corporation"]
  }
}
```

### Response Format
```json
{
  "id": "npc_cyberpunk_001",
  "creation_type": "npc",
  "name": "Zara Blacknet",
  "description": "A skilled netrunner with chrome-enhanced neural interfaces",
  "stats": {
    "strength": 8, "dexterity": 16, "constitution": 12,
    "intelligence": 18, "wisdom": 14, "charisma": 13
  },
  "traits": ["Cybernetic Enhancement", "Corporate Contacts"],
  "motivations": ["Escape corporate control", "Protect data integrity"],
  "challenge_rating": 2,
  "species": "cyborg",
  "class": "netrunner",
  "background": "corporate_hacker"
}
```

## Configuration Options

### Backend URL Configuration
```python
# Default local development
character_client = CharacterServiceClient("http://localhost:8001")

# Production environment
character_client = CharacterServiceClient("https://api.dndtools.com/backend")
```

### Integration Control
```python
# Enable/disable character service integration
campaign_context = {
    "use_character_service": True,  # Default: True
    "backend_timeout": 30,          # Default: 30 seconds
    "fallback_on_failure": True     # Default: True
}
```

## Error Handling and Fallbacks

### 1. Service Unavailable
- If backend character service is unavailable, system falls back to LLM-only generation
- Fallback characters maintain genre/theme consistency through prompt engineering
- Users are notified when fallback mode is used

### 2. Invalid Responses
- Malformed responses from character service trigger fallback generation
- System logs errors for debugging while maintaining functionality
- Graceful degradation ensures campaign generation continues

### 3. Timeout Handling
- 30-second default timeout for character service requests
- Timeout failures trigger immediate fallback to LLM generation
- Configurable timeout settings for different deployment environments

## Testing

### Test Script: `test_character_service_integration.py`
- Tests basic character service client functionality
- Validates campaign-character integration logic
- Checks genre/theme consistency
- Demonstrates enhanced chapter generation

### Running Tests
```bash
cd /home/ajs7/dnd_tools/dnd_char_creator/backend_campaign
python test_character_service_integration.py
```

## Requirements Compliance

The integration fulfills the following enhanced requirements:

- **REQ-CAM-074-078**: Automatic quantity determination based on campaign context
- **REQ-CAM-079-083**: Genre and theme consistency for all generated characters
- **REQ-CAM-084-088**: Custom species and class support beyond traditional D&D
- **REQ-CAM-094-099**: Campaign-character service integration via HTTP API

## Future Enhancements

### 1. Batch Character Generation
- Generate multiple characters in a single API call for efficiency
- Reduce API overhead for complex chapters with many NPCs

### 2. Character Relationship Mapping
- Automatically generate relationships between NPCs within chapters
- Create social networks and faction dynamics

### 3. Progressive Character Development
- Track character changes across campaign chapters
- Support character evolution and relationship development

### 4. Advanced Challenge Rating
- Dynamic CR adjustment based on party composition and tactics
- Machine learning-based encounter difficulty prediction
