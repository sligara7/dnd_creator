# Interface Control Document: Character Service (ICD-CS-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Service Interface

### 1.1 Base URL
```
http://character-service:8000
```

### 1.2 Common Headers
```
X-Request-ID: <uuid>
Content-Type: application/json
Authorization: Bearer <token>
```

## 2. Factory API

### 2.1 Create Character
```http
POST /api/v2/factory/create
```

#### Request Body
```json
{
  "creation_type": "character",
  "prompt": "string",
  "theme": "string",
  "level": "integer",
  "preferences": {
    "use_custom_content": "boolean",
    "prioritize_official": "boolean"
  }
}
```

#### Response
```json
{
  "id": "uuid",
  "character": {
    "name": "string",
    "species": "string",
    "class": "string",
    "level": "integer",
    "ability_scores": {},
    "skills": [],
    "feats": [],
    "equipment": [],
    "spells": [],
    "backstory": "string"
  },
  "custom_content": [],
  "creation_notes": "string",
  "theme_integration": {}
}
```

### 2.2 Evolve Character
```http
POST /api/v2/factory/evolve
```

#### Request Body
```json
{
  "character_id": "uuid",
  "evolution_prompt": "string",
  "preserve_fields": ["string"],
  "theme": "string"
}
```

### 2.3 Get Factory Types
```http
GET /api/v2/factory/types
```

#### Response
```json
{
  "available_types": [
    "character",
    "species",
    "class",
    "feat",
    "spell",
    "weapon",
    "armor"
  ],
  "supported_themes": [
    "western",
    "cyberpunk",
    "steampunk",
    "horror",
    "traditional"
  ]
}
```

## 3. Character Management

### 3.1 Get Character
```http
GET /api/v2/characters/{id}
```

### 3.2 Refine Character
```http
PUT /api/v2/characters/{id}/refine
```

#### Request Body
```json
{
  "refinements": [
    {
      "field": "string",
      "change": "string",
      "reason": "string"
    }
  ],
  "notes": "string"
}
```

### 3.3 Level Up Character
```http
POST /api/v2/characters/{id}/level-up
```

#### Request Body
```json
{
  "new_level": "integer",
  "choices": {
    "ability_score_improvements": [],
    "feat_selections": [],
    "class_features": []
  },
  "use_journal": "boolean"
}
```

### 3.4 Direct Edit Character
```http
PUT /api/v2/characters/{id}/direct-edit
```

#### Request Body
```json
{
  "fields": {
    "field_name": "value"
  },
  "notes": "string",
  "username": "string"
}
```

## 4. Inventory & Equipment

### 4.1 Get Inventory
```http
GET /api/v2/characters/{id}/inventory
```

### 4.2 Add Item
```http
POST /api/v2/characters/{id}/inventory/add
```

#### Request Body
```json
{
  "item": {
    "name": "string",
    "type": "string",
    "properties": {},
    "custom": "boolean"
  },
  "quantity": "integer"
}
```

### 4.3 Swap Equipment
```http
PUT /api/v2/characters/{id}/equipment/swap
```

#### Request Body
```json
{
  "unequip_slots": ["string"],
  "equip_items": [
    {
      "item_id": "uuid",
      "slot": "string"
    }
  ]
}
```

## 5. Spell Management

### 5.1 Prepare Spells
```http
POST /api/v2/characters/{id}/spells/prepare
```

#### Request Body
```json
{
  "prepared_spells": ["string"],
  "unprepared_spells": ["string"],
  "class_name": "string"
}
```

### 5.2 Get Spell Slots
```http
GET /api/v2/characters/{id}/spells/slots
```

#### Response
```json
{
  "available_slots": {
    "1": "integer",
    "2": "integer",
    "3": "integer"
  },
  "used_slots": {
    "1": "integer",
    "2": "integer",
    "3": "integer"
  },
  "ritual_spells": ["string"]
}
```

## 6. Journal System

### 6.1 CRUD Endpoints
```http
POST /api/v2/characters/{id}/journal
GET /api/v2/characters/{id}/journal
PUT /api/v2/characters/{id}/journal/{entry_id}
DELETE /api/v2/characters/{id}/journal/{entry_id}
```

### 6.1 Get Journal
```http
GET /api/v2/characters/{id}/journal
```

### 6.2 Add Entry
```http
POST /api/v2/characters/{id}/journal
```

#### Request Body
```json
{
  "session_date": "date",
  "content": "string",
  "xp_gained": "integer",
  "milestones": [],
  "dm_notes": "string"
}
```

### 6.3 Edit Entry
```http
PUT /api/v2/characters/{id}/journal/{entry_id}
```

## 7. Complete Character Sheets

### 7.1 Retrieval
```http
GET /api/v2/characters/{id}/sheet
GET /api/v2/npcs/{id}/sheet
GET /api/v2/monsters/{id}/sheet
```

## 8. Unified Catalog
```http
GET /api/v2/catalog
GET /api/v2/catalog/search?q={query}
POST /api/v2/catalog
PUT /api/v2/catalog/{item_id}
DELETE /api/v2/catalog/{item_id}
```

## 9. Version Control
```http
POST /api/v2/characters/{id}/branches
GET /api/v2/characters/{id}/branches
POST /api/v2/characters/{id}/branches/{branch_id}/merge
```

## 10. Metrics
```http
GET /api/v2/metrics
```

## 11. Message Hub Integration

### 7.1 Events Published
```json
{
  "character_created": {
    "character_id": "uuid",
    "timestamp": "string",
    "details": {}
  },
  "character_updated": {
    "character_id": "uuid",
    "changes": [],
    "timestamp": "string"
  },
  "custom_content_created": {
    "content_id": "uuid",
    "type": "string",
    "timestamp": "string"
  }
}
```

### 7.2 Events Subscribed
```json
{
  "campaign_theme_updated": {
    "campaign_id": "uuid",
    "new_theme": "string"
  },
  "dm_approval_required": {
    "character_id": "uuid",
    "changes": [],
    "approval_id": "uuid"
  }
}
```

## 12. Health Check

### 8.1 Health Check
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
    "llm_service": "healthy",
    "database": "healthy"
  },
  "metrics": {
    "characters_created": "integer",
    "active_requests": "integer",
    "error_rate": "float"
  }
}
```

## 9. Error Handling

### 9.1 Error Response Format
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

### 9.2 Common Error Codes
- `INVALID_REQUEST`: Request format or parameters invalid
- `CHARACTER_NOT_FOUND`: Character ID not found
- `VALIDATION_ERROR`: Generated content failed validation
- `LLM_ERROR`: Error from LLM service
- `THEME_ERROR`: Error processing campaign theme
- `PERMISSION_DENIED`: User lacks required permissions
