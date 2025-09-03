# Campaign Service Integration Control Document

## Overview

This document describes the integration interfaces between the Campaign Service and its dependent services, specifically the Character Service and Image Service.

## Service Dependencies

### Character Service

Interface for NPC and monster generation and management.

#### Messages

1. Character Generation Request
```json
{
  "type": "request",
  "action": "character.batch_generate",
  "payload": {
    "requirements": [{
      "type": "npc | monster",
      "count": "integer",
      "level_range": {
        "min": "integer",
        "max": "integer"
      },
      "role": "string",
      "traits": ["string"],
      "abilities": ["string"],
      "context": {
        "location": "string",
        "purpose": "string",
        "alignment": "string"
      }
    }],
    "context": {
      "campaign_type": "string",
      "setting": "string",
      "current_state": {},
      "custom_rules": {}
    }
  }
}
```

Response:
```json
{
  "type": "response",
  "status": "success",
  "payload": {
    "characters": [{
      "character_id": "string",
      "type": "npc | monster",
      "name": "string",
      "details": {},
      "stats": {},
      "abilities": [],
      "inventory": []
    }]
  }
}
```

2. Character Reference Validation
```json
{
  "type": "request",
  "action": "character.validate_refs",
  "payload": {
    "references": [{
      "id": "string",
      "type": "string",
      "context": "string"
    }]
  }
}
```

Response:
```json
{
  "type": "response",
  "status": "success",
  "payload": {
    "characters": [{
      "id": "string",
      "type": "string",
      "exists": "boolean",
      "details": {}
    }]
  }
}
```

3. Character Feedback
```json
{
  "type": "request",
  "action": "character.apply_feedback",
  "payload": {
    "character_id": "string",
    "feedback": {
      "development": ["string"],
      "relationships": [{
        "target_id": "string",
        "change": "string"
      }],
      "traits": [{
        "name": "string",
        "change": "string"
      }],
      "abilities": [{
        "name": "string",
        "adjustment": "string"
      }]
    }
  }
}
```

#### Events

1. Character Created
```json
{
  "type": "event",
  "name": "character.created",
  "payload": {
    "character_id": "string",
    "type": "npc | monster",
    "campaign_id": "string",
    "chapter_id": "string"
  }
}
```

2. Character Updated
```json
{
  "type": "event",
  "name": "character.updated",
  "payload": {
    "character_id": "string",
    "update_type": "string",
    "changes": {}
  }
}
```

### Image Service

Interface for map generation and management.

#### Messages

1. Map Generation Request
```json
{
  "type": "request",
  "action": "image.generate_map",
  "payload": {
    "prompt": "string",
    "style_params": {
      "style": "string",
      "dimensions": {
        "width": "integer",
        "height": "integer"
      },
      "format": "string",
      "details": {}
    },
    "metadata": {
      "location_id": "string",
      "map_type": "string",
      "campaign_id": "string"
    }
  }
}
```

Response:
```json
{
  "type": "response",
  "status": "success",
  "payload": {
    "image_id": "string",
    "url": "string",
    "metadata": {},
    "dimensions": {
      "width": "integer",
      "height": "integer"
    }
  }
}
```

2. Map Retrieval
```json
{
  "type": "request",
  "action": "image.get_map",
  "payload": {
    "image_id": "string"
  }
}
```

Response:
```json
{
  "type": "response",
  "status": "success",
  "payload": {
    "image_id": "string",
    "url": "string",
    "metadata": {},
    "created_at": "timestamp"
  }
}
```

3. Add Encounter Overlay
```json
{
  "type": "request",
  "action": "image.add_overlay",
  "payload": {
    "image_id": "string",
    "overlay_data": {
      "type": "string",
      "elements": [{
        "type": "marker | area | path",
        "coordinates": {},
        "style": {},
        "metadata": {}
      }]
    }
  }
}
```

#### Events

1. Map Generated
```json
{
  "type": "event",
  "name": "image.map_generated",
  "payload": {
    "image_id": "string",
    "location_id": "string",
    "metadata": {}
  }
}
```

2. Map Updated
```json
{
  "type": "event",
  "name": "image.map_updated",
  "payload": {
    "image_id": "string",
    "update_type": "string",
    "changes": {}
  }
}
```

## Data Models

### Character Models

```typescript
interface CharacterRequirement {
  type: "npc" | "monster";
  count?: number;
  level_range?: {
    min: number;
    max: number;
  };
  role?: string;
  traits?: string[];
  abilities?: string[];
  context?: {
    location?: string;
    purpose?: string;
    alignment?: string;
  };
}

interface CharacterReference {
  id: string;
  type: string;
  context?: string;
}

interface CharacterFeedback {
  development: string[];
  relationships: {
    target_id: string;
    change: string;
  }[];
  traits: {
    name: string;
    change: string;
  }[];
  abilities: {
    name: string;
    adjustment: string;
  }[];
}
```

### Map Models

```typescript
interface MapRequirement {
  type: string;
  style_params?: {
    style?: string;
    dimensions?: {
      width: number;
      height: number;
    };
    format?: string;
    details?: Record<string, any>;
  };
  force_update?: boolean;
}

interface OverlayElement {
  type: "marker" | "area" | "path";
  coordinates: Record<string, any>;
  style?: Record<string, any>;
  metadata?: Record<string, any>;
}

interface MapMetadata {
  location_id: string;
  map_type: string;
  campaign_id: string;
  version?: number;
  parent_map_id?: string;
}
```

## Integration Patterns

### Character Generation Flow

1. Campaign service detects need for characters (from notes/updates)
2. AI generates detailed character requirements
3. Character service creates characters based on requirements
4. Campaign service indexes and links characters
5. Character service maintains state and updates

### Map Generation Flow

1. Campaign service identifies map needs
2. AI generates detailed map prompt
3. Image service creates map based on prompt
4. Campaign service indexes map and location
5. Image service stores and versions maps

## Error Handling

All service interactions should handle these error cases:

1. Service Unavailable
```json
{
  "type": "error",
  "code": "SERVICE_UNAVAILABLE",
  "message": "string",
  "details": {}
}
```

2. Invalid Request
```json
{
  "type": "error",
  "code": "INVALID_REQUEST",
  "message": "string",
  "validation_errors": []
}
```

3. Generation Failed
```json
{
  "type": "error",
  "code": "GENERATION_FAILED",
  "message": "string",
  "reason": "string"
}
```

## Rate Limiting

Services implement the following rate limits:

- Character Service:
  - 100 character generations per minute
  - 1000 reference validations per minute
  - 500 feedback applications per minute

- Image Service:
  - 50 map generations per minute
  - 200 map retrievals per minute
  - 100 overlay additions per minute

## Caching

1. Character References
   - Cache Duration: 5 minutes
   - Invalidated on character updates

2. Maps
   - Cache Duration: 1 hour
   - Versioned storage
   - Invalidated on force updates

## Message Bus Topics

1. Character Service
   - character.generate
   - character.validate
   - character.feedback
   - character.created
   - character.updated

2. Image Service
   - image.generate_map
   - image.get_map
   - image.add_overlay
   - image.map_generated
   - image.map_updated
