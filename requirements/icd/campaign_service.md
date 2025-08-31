# Campaign Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-31

## Service Interface Overview

The Campaign Service provides APIs for managing campaigns, character relationships, and interactions. It serves as the central authority for character-to-character relationship data and campaign progression.

## API Endpoints

### Campaign Management

#### Create Campaign
```http
POST /api/v2/campaigns
Content-Type: application/json

{
  "name": "string",
  "description": "string",
  "theme": "string",
  "campaign_type": "string",
  "dm_id": "string",
  "settings": {
    "additional": "properties"
  }
}
```

#### Get Campaign
```http
GET /api/v2/campaigns/{campaign_id}
```

### Character Relationships

#### Record Character Interaction
```http
POST /api/v2/campaigns/{campaign_id}/interactions
Content-Type: application/json

{
  "source_character_id": "string",
  "target_character_id": "string",
  "interaction_type": "string",
  "interaction_data": {
    "context": "string",
    "location": "string",
    "outcome": "string",
    "additional": "properties"
  }
}
```

#### Get Character Relationships
```http
GET /api/v2/campaigns/{campaign_id}/characters/{character_id}/relationships
```

#### Update Relationship Status
```http
PUT /api/v2/campaigns/{campaign_id}/relationships/{relationship_id}
Content-Type: application/json

{
  "relationship_type": "string",
  "relationship_data": {
    "status": "string",
    "trust_level": "integer",
    "notes": "string"
  }
}
```

### Social Network Analysis

#### Get Character Social Graph
```http
GET /api/v2/campaigns/{campaign_id}/social-graph
Query Parameters:
- depth: integer (default: 2)
- include_npcs: boolean (default: true)
```

#### Get Relationship Timeline
```http
GET /api/v2/campaigns/{campaign_id}/characters/{character_id}/timeline
Query Parameters:
- start_date: string (ISO 8601)
- end_date: string (ISO 8601)
```

## Event Subscriptions

### Character Service Events
```json
{
  "topic": "character.lifecycle",
  "events": [
    "character.created",
    "character.updated",
    "character.deleted",
    "character.restored"
  ],
  "payload": {
    "character_id": "string",
    "event_type": "string",
    "timestamp": "string",
    "data": {}
  }
}
```

### Campaign Events
```json
{
  "topic": "campaign.relationships",
  "events": [
    "relationship.created",
    "relationship.updated",
    "relationship.deleted",
    "interaction.recorded"
  ],
  "payload": {
    "campaign_id": "string",
    "event_type": "string",
    "source_character_id": "string",
    "target_character_id": "string",
    "timestamp": "string",
    "data": {}
  }
}
```

## Data Models

### Campaign Model
```typescript
interface Campaign {
  id: string;
  name: string;
  description: string;
  theme: string;
  campaign_type: string;
  dm_id: string;
  settings: Record<string, any>;
  created_at: string;
  updated_at: string;
}
```

### Character Interaction Model
```typescript
interface CharacterInteraction {
  id: string;
  campaign_id: string;
  source_character_id: string;
  target_character_id: string;
  interaction_type: string;
  interaction_data: {
    context: string;
    location: string;
    outcome: string;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}
```

### Character Relationship Model
```typescript
interface CharacterRelationship {
  id: string;
  campaign_id: string;
  character_id_1: string;
  character_id_2: string;
  relationship_type: string;
  relationship_score: number;
  relationship_data: {
    status: string;
    trust_level: number;
    notes: string;
    [key: string]: any;
  };
  created_at: string;
  updated_at: string;
}
```

## Integration Patterns

### Character Service Integration
1. Subscribe to character lifecycle events
2. Maintain character reference integrity
3. Handle soft deletions and restorations
4. Support character merging

### Message Hub Integration
1. Publish relationship events
2. Subscribe to character events
3. Handle event ordering
4. Manage event retries

### LLM Service Integration
1. Generate interaction narratives
2. Get relationship insights
3. Handle content generation
4. Manage context windows

## Error Handling

### HTTP Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 409: Conflict
- 422: Unprocessable Entity
- 500: Internal Server Error

### Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {}
  }
}
```

## Rate Limits

### API Endpoints
- Standard: 1000 requests/minute
- Batch operations: 100 requests/minute
- Social graph: 10 requests/minute

### Event Processing
- Character events: 1000/minute
- Relationship events: 500/minute
- Interaction events: 200/minute

## Security

### Authentication
- JWT-based authentication
- API key support
- Role-based access control

### Authorization
- Campaign-level permissions
- Character-level permissions
- Action-based permissions

## Metrics

### Business Metrics
- Active campaigns
- Relationship counts
- Interaction frequency
- Character connections

### Technical Metrics
- Request latency
- Event processing time
- Error rates
- Cache hit rates

## Dependencies

### Required Services
- Character Service: v2.0+
- Message Hub: v1.5+
- LLM Service: v1.0+
- Cache Service: v1.0+
- Auth Service: v2.0+

### Optional Services
- Search Service: v1.0+
- Audit Service: v1.0+
- Metrics Service: v1.0+
