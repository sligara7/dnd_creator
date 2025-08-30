# Interface Control Document: Campaign Service (ICD-CP-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Service Interface

### 1.1 Base URL
```
http://campaign-service:8001
```

### 1.2 Common Headers
```
X-Request-ID: <uuid>
Content-Type: application/json
Authorization: Bearer <token>
```

## 2. Campaign API

### 2.1 Create Campaign
```http
POST /api/v2/factory/create
```

#### Request Body
```json
{
  "name": "string",
  "concept": "string",
  "theme": {
    "primary": "string",
    "secondary": "string"
  },
  "length": {
    "min_sessions": "integer",
    "max_sessions": "integer"
  },
  "preferences": {
    "complexity": "string",
    "moral_tone": "string",
    "violence_level": "string"
  }
}
```

#### Response
```json
{
  "id": "uuid",
  "campaign": {
    "name": "string",
    "concept": "string",
    "theme": {},
    "chapters": [],
    "npcs": [],
    "locations": [],
    "plot_branches": []
  },
  "generation_notes": "string"
}
```

### 2.2 Refine Campaign
```http
POST /api/v2/campaigns/{id}/refine
```

#### Request Body
```json
{
  "refinements": [
    {
      "aspect": "string",
      "change": "string",
      "reason": "string"
    }
  ],
  "preserve": ["string"]
}
```

### 2.3 Campaign Management
```http
GET /api/v2/campaigns/{id}
PUT /api/v2/campaigns/{id}
DELETE /api/v2/campaigns/{id}
```

## 3. Chapter API

### 3.1 Create Chapter
```http
POST /api/v2/campaigns/{id}/chapters
```

#### Request Body
```json
{
  "title": "string",
  "theme": "string",
  "requirements": {
    "level_range": {
      "min": "integer",
      "max": "integer"
    },
    "party_size": {
      "min": "integer",
      "max": "integer"
    }
  },
  "dependencies": ["uuid"]
}
```

### 3.2 Chapter Operations
```http
GET /api/v2/campaigns/{id}/chapters/{chapter_id}
PUT /api/v2/campaigns/{id}/chapters/{chapter_id}
DELETE /api/v2/campaigns/{id}/chapters/{chapter_id}
```

## 4. Version Control API

### 4.1 Chapter Versions
```http
POST /api/v2/campaigns/{id}/versions
GET /api/v2/campaigns/{id}/versions?branch={branch}&type={type}
GET /api/v2/campaigns/{id}/versions/{version_hash}
```

#### Create Version Request
```json
{
  "title": "string",
  "summary": "string",
  "content": {},
  "parent_hashes": ["string"],
  "branch_name": "string",
  "version_type": "skeleton|draft|published|played|branch|merge",
  "commit_message": "string"
}
```

### 4.2 Branch Management
```http
POST /api/v2/campaigns/{id}/branches
GET /api/v2/campaigns/{id}/branches
GET /api/v2/campaigns/{id}/branches/{branch}
PUT /api/v2/campaigns/{id}/branches/{branch}
DELETE /api/v2/campaigns/{id}/branches/{branch}
```

#### Create Branch Request
```json
{
  "name": "string",
  "branch_type": "main|alternate|player_choice|experimental|parallel",
  "description": "string",
  "from_commit": "string"
}
```

### 4.3 Merge API
```http
POST /api/v2/campaigns/{id}/merge
```

#### Request Body
```json
{
  "source_branch": "string",
  "target_branch": "string",
  "strategy": "manual|auto|cherry-pick",
  "message": "string"
}
```

### 4.4 Play Sessions
```http
POST /api/v2/campaigns/{id}/sessions
GET /api/v2/campaigns/{id}/sessions
GET /api/v2/campaigns/{id}/sessions/{session_id}
```

#### Create Session Request
```json
{
  "session_number": "integer",
  "session_title": "string",
  "session_date": "datetime",
  "chapters_played": ["string"],
  "players_present": ["string"],
  "dm_name": "string",
  "major_events": [],
  "player_decisions": {},
  "story_progression": "string"
}
```

### 4.5 Player Choices
```http
POST /api/v2/campaigns/{id}/choices
GET /api/v2/campaigns/{id}/choices
```

#### Create Choice Request
```json
{
  "chapter_version_id": "uuid",
  "choice_description": "string",
  "options_presented": [],
  "choice_made": {},
  "players_involved": ["string"],
  "immediate_consequences": {},
  "long_term_consequences": {}
}
```

### 4.1 Create Branch
```http
POST /api/v2/campaigns/{id}/chapters/{chapter_id}/branches
```

#### Request Body
```json
{
  "trigger_condition": "string",
  "choices": [
    {
      "description": "string",
      "consequences": "string",
      "leads_to": "uuid"
    }
  ]
}
```

### 4.2 Branch Operations
```http
GET /api/v2/campaigns/{id}/branches
PUT /api/v2/campaigns/{id}/branches/{branch_id}
DELETE /api/v2/campaigns/{id}/branches/{branch_id}
```

## 5. Theme Management

### 5.1 Available Themes
```http
GET /api/v2/themes
```

#### Response
```json
{
  "core_themes": [
    "puzzle_solving",
    "mystery",
    "tactical_combat",
    "political_intrigue"
  ],
  "setting_themes": [
    "western",
    "cyberpunk",
    "steampunk",
    "horror"
  ]
}
```

### 5.2 Apply Theme
```http
POST /api/v2/campaigns/{id}/theme
```

#### Request Body
```json
{
  "theme": "string",
  "strength": "float",
  "elements": ["string"],
  "exclusions": ["string"]
}
```

## 6. Content Generation

### 6.1 Generate NPC
```http
POST /api/v2/campaigns/{id}/npcs
```

#### Request Body
```json
{
  "role": "string",
  "importance": "string",
  "theme_alignment": "string",
  "chapters": ["uuid"]
}
```

### 6.2 Generate Location
```http
POST /api/v2/campaigns/{id}/locations
```

#### Request Body
```json
{
  "type": "string",
  "theme": "string",
  "size": "string",
  "requirements": {
    "encounters": "integer",
    "points_of_interest": "integer"
  }
}
```

### 6.3 Generate Map
```http
POST /api/v2/campaigns/{id}/maps
```

#### Request Body
```json
{
  "type": "world|region|dungeon|building",
  "style": "string",
  "size": {
    "width": "integer",
    "height": "integer"
  },
  "features": ["string"]
}
```

## 7. Message Hub Integration

### 7.1 Events Published
```json
{
  "campaign_created": {
    "campaign_id": "uuid",
    "theme": "string",
    "timestamp": "string"
  },
  "chapter_completed": {
    "campaign_id": "uuid",
    "chapter_id": "uuid",
    "outcomes": []
  },
  "theme_updated": {
    "campaign_id": "uuid",
    "old_theme": "string",
    "new_theme": "string"
  }
}
```

### 7.2 Events Subscribed
```json
{
  "character_created": {
    "character_id": "uuid",
    "campaign_id": "uuid"
  },
  "character_leveled": {
    "character_id": "uuid",
    "new_level": "integer"
  },
  "journal_updated": {
    "character_id": "uuid",
    "entry_id": "uuid"
  }
}
```

## 8. Integration Endpoints

### 8.1 Character Service Integration
```http
POST /api/v2/campaigns/{id}/characters
GET /api/v2/campaigns/{id}/characters/{character_id}/status
PUT /api/v2/campaigns/{id}/characters/{character_id}/journal
```

### 8.2 LLM Service Integration
```http
POST /api/v2/campaigns/{id}/generate
POST /api/v2/campaigns/{id}/refine
POST /api/v2/campaigns/{id}/evolve
```

## 9. Health Check

### 9.1 Health Check
```http
GET /health
```

#### Response
```json
{
  "status": "healthy|degraded|unhealthy",
  "version": "string",
  "dependencies": {
    "message_hub": "healthy",
    "character_service": "healthy",
    "llm_service": "healthy",
    "database": "healthy"
  },
  "metrics": {
    "active_campaigns": "integer",
    "generation_queue": "integer",
    "error_rate": "float"
  }
}
```

## 10. Error Handling

### 10.1 Error Response Format
```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "request_id": "string",
      "timestamp": "string",
      "field": "string"
    }
  }
}
```

### 10.2 Common Error Codes
- `CAMPAIGN_NOT_FOUND`: Campaign ID not found
- `INVALID_THEME`: Theme not supported
- `GENERATION_ERROR`: Content generation failed
- `BRANCH_CONFLICT`: Plot branch conflict detected
- `DEPENDENCY_ERROR`: Chapter dependency issue
- `INTEGRATION_ERROR`: Service integration error
- `THEME_ERROR`: Theme application error
- `PERMISSION_DENIED`: User lacks required permissions
