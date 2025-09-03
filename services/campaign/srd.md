# D&D Campaign Service API Reference

## Overview

The Campaign Service provides APIs for managing D&D campaigns, including session notes, scene generation, and AI-powered campaign updates. This document describes the service's endpoints and data models.

## Authentication

All API requests must include an authentication token in the `Authorization` header:

```http
Authorization: Bearer {token}
```

## Base URLs

- Development: `http://localhost:8000`
- Staging: `https://api.staging.dnd.local`
- Production: `https://api.dnd.local`

## API Endpoints

### Session Notes

#### Create Session Note

```http
POST /sessions/notes
Content-Type: application/json
Authorization: Bearer {token}

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
    "description": "string",
    "impact": "string",
    "location": "string",
    "involved_characters": ["string"]
  }],
  "character_interactions": [{
    "source_character": "string",
    "target_character": "string",
    "interaction_type": "string",
    "description": "string",
    "outcome": "string"
  }],
  "plot_decisions": [{
    "decision_type": "string",
    "description": "string",
    "impact": "string",
    "alternatives": ["string"],
    "deciding_characters": ["string"]
  }],
  "metadata": {}
}
```

Response (201 Created):
```json
{
  "id": "uuid",
  "campaign_id": "uuid",
  "chapter_id": "uuid",
  "session_number": 1,
  "title": "string",
  "narrative": "string",
  "dm_id": "string",
  "players_present": ["string"],
  "objectives_completed": [{}],
  "significant_events": [...],
  "character_interactions": [...],
  "plot_decisions": [...],
  "metadata": {},
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

#### Generate Scene Setter

Generate rich narrative descriptions and DM notes for campaigns, chapters, or encounters.

```http
POST /sessions/scene-setter
Content-Type: application/json
Authorization: Bearer {token}

{
  "campaign_id": "uuid",
  "chapter_id": "uuid",
  "encounter_id": "string",
  "custom_rules": {
    "tone": "dark_fantasy",
    "detail_level": "high",
    "include_music": true,
    "focus_areas": ["combat", "puzzles", "npc_motivations"]
  }
}
```

Response (200 OK):
```json
{
  "narrative": "string",
  "dm_notes": "string",
  "encounter_details": {
    "enemies": [{
      "name": "string",
      "type": "string",
      "count": "integer",
      "tactics": "string",
      "motivations": "string"
    }],
    "environment": {
      "description": "string",
      "features": ["string"],
      "hazards": ["string"],
      "advantages": ["string"]
    }
  },
  "interactive_elements": {
    "puzzles": [{
      "description": "string",
      "hints": ["string"],
      "solution": "string",
      "alternative_solutions": ["string"]
    }],
    "objects": [{
      "name": "string",
      "description": "string",
      "interactions": ["string"]
    }]
  },
  "npc_details": [{
    "name": "string",
    "role": "string",
    "motivations": ["string"],
    "knowledge": ["string"],
    "reactions": {}
  }],
  "recommended_music": {
    "ambient": ["string"],
    "combat": ["string"],
    "dramatic": ["string"]
  }
}
```

#### Update Campaign from Notes

Process session notes to update campaign and chapter state.

```http
POST /sessions/notes/{note_id}/update
Content-Type: application/json
Authorization: Bearer {token}

{
  "update_type": "comprehensive",
  "custom_rules": {
    "progression_rate": "normal",
    "character_focus": "high",
    "world_complexity": "medium",
    "tone_consistency": "strict"
  }
}
```

Response (200 OK):
```json
{
  "campaign_updates": [{
    "type": "string",
    "description": "string",
    "significance": "string",
    "affected_elements": ["string"]
  }],
  "chapter_updates": [{
    "type": "string",
    "description": "string",
    "plot_implications": ["string"]
  }],
  "world_state_changes": [{
    "location": "string",
    "change_type": "string",
    "description": "string",
    "consequences": ["string"]
  }],
  "quest_updates": [{
    "quest_id": "string",
    "status_change": "string",
    "progress_updates": ["string"],
    "new_objectives": ["string"]
  }],
  "notes": ["string"]
}
```

## Data Models

### Session Note

Core model for recording campaign sessions:

```typescript
interface SessionNote {
  id: UUID;
  campaign_id: UUID;
  chapter_id?: UUID;
  session_number: number;
  title: string;
  narrative: string;
  dm_id: string;
  players_present: string[];
  objectives_completed: any[];
  significant_events: SignificantEvent[];
  character_interactions: CharacterInteraction[];
  plot_decisions: PlotDecision[];
  metadata?: Record<string, any>;
  feedback_status: string;
  feedback_processed_at?: Date;
  created_at: Date;
  updated_at: Date;
}

interface SignificantEvent {
  event_type: string;
  description: string;
  impact?: string;
  location?: string;
  involved_characters: string[];
}

interface CharacterInteraction {
  source_character: string;
  target_character: string;
  interaction_type: string;
  description: string;
  outcome?: string;
}

interface PlotDecision {
  decision_type: string;
  description: string;
  impact?: string;
  alternatives?: string[];
  deciding_characters: string[];
}
```

### Scene Setter

Models for scene generation:

```typescript
interface SceneSetterRequest {
  campaign_id: UUID;
  chapter_id?: UUID;
  encounter_id?: string;
  custom_rules?: {
    tone?: string;
    detail_level?: string;
    include_music?: boolean;
    focus_areas?: string[];
  };
}

interface SceneSetterResponse {
  narrative: string;
  dm_notes: string;
  encounter_details?: {
    enemies?: Enemy[];
    environment?: Environment;
  };
  interactive_elements?: {
    puzzles?: Puzzle[];
    objects?: InteractiveObject[];
  };
  npc_details?: NPCDetail[];
  recommended_music?: {
    ambient?: string[];
    combat?: string[];
    dramatic?: string[];
  };
}
```

### Campaign Updates

Models for campaign state updates:

```typescript
interface CampaignUpdateRequest {
  update_type: "comprehensive" | "campaign-only" | "chapter-only";
  custom_rules?: {
    progression_rate?: string;
    character_focus?: string;
    world_complexity?: string;
    tone_consistency?: string;
  };
}

interface CampaignUpdateResponse {
  campaign_updates: CampaignUpdate[];
  chapter_updates: ChapterUpdate[];
  world_state_changes: WorldStateChange[];
  quest_updates: QuestUpdate[];
  notes: string[];
}
```

## Error Responses

The API uses standard HTTP status codes and returns error details in JSON format:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

Common error codes:
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 422: Unprocessable Entity
- 500: Internal Server Error

## Rate Limiting

The API implements rate limiting based on the client's authentication token:

- Standard tier: 100 requests per minute
- Premium tier: 1000 requests per minute

Rate limit headers are included in all responses:
```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1632368242
```

## Webhook Events

The service emits events that can be consumed via webhooks:

1. Session Events
   - session.created
   - session.updated
   - session.deleted
   - session.feedback_processed

2. Scene Events
   - scene.generated
   - scene.updated

3. Campaign Events
   - campaign.updated
   - campaign.state_changed
   - campaign.quest_updated

Configure webhooks through the developer portal.
