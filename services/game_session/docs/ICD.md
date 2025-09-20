# Game Session Service - Interface Control Document (ICD)

Version: 1.0
Status: Active
Last Updated: 2025-09-20

## Service Overview

The Game Session Service acts as the central coordinator for live D&D gameplay sessions, managing real-time state synchronization between players and orchestrating interactions between various services during gameplay. This document defines all interfaces exposed by the service.

## WebSocket Interface

### Connection Management

#### Connection Establishment
```
Endpoint: wss://api.dndcreator.com/api/v2/sessions/{session_id}/ws
Headers:
  Authorization: Bearer {jwt_token}
  X-Session-Token: {session_token}
```

#### Connection Events
```javascript
// Connection Success
{
  "type": "connection_established",
  "data": {
    "session_id": "uuid",
    "player_id": "uuid",
    "timestamp": "ISO8601"
  }
}

// Connection Error
{
  "type": "connection_error",
  "error": {
    "code": "string",
    "message": "string"
  }
}

// Heartbeat (Every 30s)
{
  "type": "heartbeat",
  "data": {
    "timestamp": "ISO8601"
  }
}
```

### Game State Events

#### State Updates
```javascript
// State Change Notification
{
  "type": "state_update",
  "data": {
    "update_id": "uuid",
    "changes": [
      {
        "path": "string",
        "value": "any",
        "previous": "any"
      }
    ],
    "timestamp": "ISO8601"
  }
}

// State Sync Request
{
  "type": "sync_request",
  "data": {
    "paths": ["string"]
  }
}

// State Sync Response
{
  "type": "sync_response",
  "data": {
    "state": {"object"},
    "version": "string"
  }
}
```

### Combat Events

#### Initiative and Turn Management
```javascript
// Initiative Roll
{
  "type": "initiative_roll",
  "data": {
    "character_id": "uuid",
    "roll": "number",
    "modifiers": {"object"}
  }
}

// Turn Change
{
  "type": "turn_change",
  "data": {
    "active_character": "uuid",
    "round": "number",
    "turn_number": "number"
  }
}
```

#### Combat Actions
```javascript
// Action Declaration
{
  "type": "action_declare",
  "data": {
    "action_id": "uuid",
    "character_id": "uuid",
    "action_type": "string",
    "targets": ["uuid"],
    "details": {"object"}
  }
}

// Action Resolution
{
  "type": "action_resolve",
  "data": {
    "action_id": "uuid",
    "outcomes": [
      {
        "target_id": "uuid",
        "effects": ["string"],
        "damage": {"object"},
        "conditions": ["string"]
      }
    ]
  }
}
```

## REST API Interface

### Session Management

#### Create Session
```http
POST /api/v2/sessions
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "campaign_id": "uuid",
  "name": "string",
  "settings": {"object"}
}

Response:
{
  "session_id": "uuid",
  "connection_token": "string",
  "websocket_url": "string"
}
```

#### Join Session
```http
POST /api/v2/sessions/{session_id}/join
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "character_id": "uuid"
}

Response:
{
  "connection_token": "string",
  "websocket_url": "string",
  "session_state": {"object"}
}
```

### State Management

#### Save Session State
```http
POST /api/v2/sessions/{session_id}/state
Content-Type: application/json
Authorization: Bearer {jwt_token}

Request:
{
  "state": {"object"},
  "metadata": {"object"}
}

Response:
{
  "version": "string",
  "timestamp": "ISO8601"
}
```

#### Load Session State
```http
GET /api/v2/sessions/{session_id}/state
Authorization: Bearer {jwt_token}

Response:
{
  "state": {"object"},
  "metadata": {"object"},
  "version": "string",
  "timestamp": "ISO8601"
}
```

## Message Bus Integration

### Published Events

#### Session Events
```javascript
// Session State Change
session.state.changed
{
  "session_id": "uuid",
  "change_type": "string",
  "details": {"object"},
  "timestamp": "ISO8601"
}

// Combat State Change
session.combat.changed
{
  "session_id": "uuid",
  "combat_id": "uuid",
  "change_type": "string",
  "details": {"object"},
  "timestamp": "ISO8601"
}
```

### Subscribed Events

#### Character Events
```javascript
// Character State Change
character.state.changed
{
  "character_id": "uuid",
  "change_type": "string",
  "details": {"object"},
  "timestamp": "ISO8601"
}
```

#### Campaign Events
```javascript
// Campaign State Change
campaign.state.changed
{
  "campaign_id": "uuid",
  "change_type": "string",
  "details": {"object"},
  "timestamp": "ISO8601"
}
```

## Redis Interface

### Key Structures

#### Session State
```
# Session metadata
session:{session_id}:meta -> Hash
  - name
  - campaign_id
  - status
  - created_at
  - updated_at

# Connected players
session:{session_id}:players -> Set
  - {player_id}

# WebSocket connections
session:{session_id}:connections -> Hash
  - {connection_id} -> {player_id}

# Combat state
session:{session_id}:combat -> Hash
  - round
  - turn
  - initiative_order
  - active_effects
```

### TTL Policies
- Session metadata: 24 hours after last access
- Player sets: 1 hour after last update
- Connection maps: 5 minutes after last heartbeat
- Combat state: 1 hour after last update

## Storage Service Interface

### Required Tables in session_db

#### Sessions Table
```sql
CREATE TABLE sessions (
  id UUID PRIMARY KEY,
  campaign_id UUID NOT NULL,
  name VARCHAR(255) NOT NULL,
  status VARCHAR(50) NOT NULL,
  metadata JSONB,
  created_at TIMESTAMP NOT NULL,
  updated_at TIMESTAMP NOT NULL,
  is_deleted BOOLEAN DEFAULT FALSE,
  deleted_at TIMESTAMP
);
```

#### Session States Table
```sql
CREATE TABLE session_states (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL,
  state JSONB NOT NULL,
  version VARCHAR(50) NOT NULL,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

#### Session Events Table
```sql
CREATE TABLE session_events (
  id UUID PRIMARY KEY,
  session_id UUID NOT NULL,
  event_type VARCHAR(100) NOT NULL,
  event_data JSONB NOT NULL,
  created_at TIMESTAMP NOT NULL,
  FOREIGN KEY (session_id) REFERENCES sessions(id)
);
```

## Error Handling

### WebSocket Errors
```javascript
{
  "type": "error",
  "error": {
    "code": "string",
    "message": "string",
    "details": {"object"}
  }
}
```

### HTTP Status Codes
- 200: Success
- 201: Resource created
- 400: Bad request
- 401: Unauthorized
- 403: Forbidden
- 404: Resource not found
- 409: Conflict
- 429: Too many requests
- 500: Internal server error
- 503: Service unavailable

## Rate Limits

### WebSocket Rate Limits
- Connection attempts: 10 per minute per IP
- Messages: 100 per minute per connection
- Combat actions: 20 per minute per player

### REST API Rate Limits
- Session creation: 10 per hour per user
- State updates: 60 per minute per session
- Joins: 30 per minute per session
