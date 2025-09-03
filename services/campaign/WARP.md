# Campaign Service Documentation

The Campaign Service is a microservice designed to manage D&D campaign data, including chapters, notes, and LLM-powered features for enhancing gameplay.

## Key Features

1. Campaign Management
   - Create and manage campaigns
   - Organize campaigns into chapters
   - Track campaign progress and state
   - Version control for campaign content

2. Session Note Taking
   - Record session narratives
   - Track character interactions
   - Log significant events
   - Document plot decisions

3. AI-Powered Features
   - Generate scene descriptions for DMs
   - Process session notes for updates
   - Analyze character development
   - Provide dynamic feedback

4. Character Tracking
   - Monitor character progression
   - Track character interactions
   - Record character history
   - Link to character service

## API Endpoints

### Session Notes

#### Create Session Note
```http
POST /sessions/notes
Content-Type: application/json

{
  "campaign_id": "uuid",
  "chapter_id": "uuid",
  "session_number": 1,
  "title": "string",
  "narrative": "string",
  "dm_id": "string",
  "players_present": ["string"],
  "objectives_completed": [{}],
  "significant_events": [{
    "event_type": "string",
    "description": "string"
  }],
  "character_interactions": [{
    "source_character": "string",
    "target_character": "string",
    "interaction_type": "string",
    "description": "string"
  }],
  "plot_decisions": [{
    "decision_type": "string",
    "description": "string"
  }]
}
```

#### Generate Scene Setter
```http
POST /sessions/scene-setter
Content-Type: application/json

{
  "campaign_id": "uuid",
  "chapter_id": "uuid",
  "encounter_id": "string",
  "custom_rules": {}
}
```

Response:
```json
{
  "narrative": "string",
  "dm_notes": "string",
  "encounter_details": {},
  "interactive_elements": {},
  "npc_details": {},
  "recommended_music": {}
}
```

#### Update Campaign from Notes
```http
POST /sessions/notes/{note_id}/update
Content-Type: application/json

{
  "update_type": "comprehensive",
  "custom_rules": {}
}
```

Response:
```json
{
  "campaign_updates": [],
  "chapter_updates": [],
  "world_state_changes": [],
  "quest_updates": [],
  "notes": []
}
```

## Features in Detail

### Scene Setter Generation

The scene setter feature helps DMs prepare for game sessions by providing rich, contextual descriptions:

1. Campaign Context
   - World state
   - Ongoing plots
   - Active quests
   - Major NPCs

2. Chapter Details
   - Current objectives
   - Key locations
   - Relevant NPCs
   - Plot threads

3. Encounter Information
   - Environment description
   - Enemy details
   - NPC motivations
   - Interactive elements
   - Puzzles and clues
   - Recommended music/ambiance

### Campaign Updates from Notes

After each session, the service can analyze notes to update the campaign state:

1. Comprehensive Updates
   - Campaign progression
   - Chapter developments
   - World state changes
   - Quest modifications

2. Character Development
   - Player character growth
   - NPC evolution
   - Relationship changes
   - Skill improvements

3. World State
   - Location changes
   - Faction developments
   - Event consequences
   - Timeline updates

## Usage Examples

### Generating a Scene Description

```python
from campaign_service import CampaignService

# Initialize service
campaign_service = CampaignService()

# Generate scene description
scene = await campaign_service.generate_scene_setter(
    campaign_id="uuid",
    chapter_id="uuid",
    encounter_id="forest_ambush"
)

print("Narrative:", scene.narrative)
print("DM Notes:", scene.dm_notes)
print("Enemies:", scene.encounter_details.get("enemies"))
print("Puzzles:", scene.interactive_elements.get("puzzles"))
```

### Updating Campaign from Session

```python
# Process session notes
updates = await campaign_service.update_campaign_from_notes(
    note_id="uuid",
    update_type="comprehensive"
)

print("Campaign Updates:", updates.campaign_updates)
print("World Changes:", updates.world_state_changes)
print("Quest Updates:", updates.quest_updates)
```

## Configuration

### Environment Variables

```bash
# Core Settings
CAMPAIGN_SERVICE_PORT=8000
CAMPAIGN_DATABASE_URL=postgresql://user:pass@host:5432/db

# AI Integration
OPENAI_API_KEY=sk-...
AI_MODEL_NAME=gpt-4

# Message Queue
RABBITMQ_HOST=localhost
RABBITMQ_PORT=5672

# Monitoring
PROMETHEUS_PORT=9090
GRAFANA_PORT=3000
```

### Custom Rules

The service supports custom rules for both scene generation and campaign updates:

```json
{
  "scene_rules": {
    "tone": "dark_fantasy",
    "detail_level": "high",
    "include_music": true
  },
  "update_rules": {
    "progression_rate": "normal",
    "character_focus": "high",
    "world_complexity": "medium"
  }
}
```

## Integration Notes

The Campaign Service integrates with:

1. Character Service
   - Character data
   - Progression tracking
   - Relationship management

2. Content Service
   - Asset management
   - Media integration
   - Resource linking

3. Auth Service
   - DM authentication
   - Permission management
   - Access control

4. Analytics Service
   - Usage tracking
   - Performance monitoring
   - Feature analytics
