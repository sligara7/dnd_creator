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

## 7. Character Sheet Management

### 7.1 Complete Sheet Retrieval
```http
GET /api/v2/characters/{id}/sheet
GET /api/v2/npcs/{id}/sheet
GET /api/v2/monsters/{id}/sheet
```

### 7.2 Field Access

#### Get Field Value
```http
GET /api/v2/characters/{id}/fields/{field_name}
```

Response:
```json
{
  "field_name": "string",
  "value": "any",
  "type": "independent|derived",
  "metadata": {
    "min": "number|null",
    "max": "number|null",
    "options": ["array|null"],
    "dependencies": ["array|null"]
  }
}
```

#### Update Field Value (Independent Variables Only)
```http
PUT /api/v2/characters/{id}/fields/{field_name}
```

Request Body:
```json
{
  "value": "any",
  "reason": "string"
}
```

### 7.3 Combat State Management

#### Get Combat State
```http
GET /api/v2/characters/{id}/combat-state
```

Response:
```json
{
  "current_hp": "integer",
  "temp_hp": "integer",
  "conditions": ["string"],
  "death_saves": {
    "successes": "integer",
    "failures": "integer"
  },
  "concentration": {
    "active": "boolean",
    "spell": "string|null"
  },
  "exhaustion": "integer"
}
```

#### Update Combat State
```http
PUT /api/v2/characters/{id}/combat-state
```

Request Body:
```json
{
  "hp_delta": "integer|null",
  "temp_hp": "integer|null",
  "add_conditions": ["string"],
  "remove_conditions": ["string"],
  "death_save_result": {
    "type": "success|failure",
    "natural_20": "boolean",
    "natural_1": "boolean"
  },
  "concentration": {
    "check_dc": "integer",
    "save_result": "integer"
  },
  "exhaustion_delta": "integer|null"
}
```

### 7.4 Resource Management

#### Get Resource State
```http
GET /api/v2/characters/{id}/resources
```

Response:
```json
{
  "hit_dice": {
    "d6": {"total": "integer", "used": "integer"},
    "d8": {"total": "integer", "used": "integer"},
    "d10": {"total": "integer", "used": "integer"},
    "d12": {"total": "integer", "used": "integer"}
  },
  "spell_slots": {
    "1": {"total": "integer", "used": "integer"},
    "2": {"total": "integer", "used": "integer"},
    "3": {"total": "integer", "used": "integer"},
    "4": {"total": "integer", "used": "integer"},
    "5": {"total": "integer", "used": "integer"},
    "6": {"total": "integer", "used": "integer"},
    "7": {"total": "integer", "used": "integer"},
    "8": {"total": "integer", "used": "integer"},
    "9": {"total": "integer", "used": "integer"}
  },
  "class_resources": [
    {
      "name": "string",
      "current": "integer",
      "maximum": "integer",
      "recharge": "short_rest|long_rest|dawn"
    }
  ]
}
```

#### Update Resource Usage
```http
PUT /api/v2/characters/{id}/resources
```

Request Body:
```json
{
  "hit_dice_used": {
    "d6": "integer|null",
    "d8": "integer|null",
    "d10": "integer|null",
    "d12": "integer|null"
  },
  "spell_slots_used": {
    "1": "integer|null",
    "2": "integer|null",
    "3": "integer|null",
    "4": "integer|null",
    "5": "integer|null",
    "6": "integer|null",
    "7": "integer|null",
    "8": "integer|null",
    "9": "integer|null"
  },
  "class_resources": [
    {
      "name": "string",
      "delta": "integer"
    }
  ]
}
```

### 7.5 Rest Management

#### Take Short Rest
```http
POST /api/v2/characters/{id}/rest/short
```

Request Body:
```json
{
  "hit_dice_used": [
    {
      "die_type": "d6|d8|d10|d12",
      "count": "integer",
      "bonus": "integer"
    }
  ]
}
```

#### Take Long Rest
```http
POST /api/v2/characters/{id}/rest/long
```

Response (for both rest types):
```json
{
  "hp_restored": "integer",
  "hit_dice_regained": {
    "d6": "integer",
    "d8": "integer",
    "d10": "integer",
    "d12": "integer"
  },
  "resources_reset": ["string"],
  "conditions_removed": ["string"]
}
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

### 9.1 Theme Branching
```http
POST /api/v2/characters/{id}/theme-transition
```

Request Body:
```json
{
  "new_theme": "string",
  "chapter_id": "uuid",
  "preserve_memory": true,  # Always true for characters
  "equipment_transitions": [
    {
      "equipment_id": "uuid",
      "transition_type": "theme_reset|adapt_new|keep_current"
    }
  ]
}
```

Response:
```json
{
  "character": {
    "id": "uuid",  # New version UUID
    "parent_id": "uuid",  # Previous version
    "theme": "string",
    "data": {}  # Full character data
  },
  "equipment": [
    {
      "id": "uuid",
      "root_id": "uuid",  # Original theme version
      "theme": "string",
      "data": {}
    }
  ],
  "version_graph": {
    "nodes": [
      {
        "id": "uuid",
        "type": "character|equipment",
        "theme": "string",
        "parent_id": "uuid|null",
        "root_id": "uuid|null"
      }
    ],
    "edges": [
      {
        "from": "uuid",
        "to": "uuid",
        "type": "parent|root|equipped"
      }
    ]
  }
}
```

### 9.2 Character Branching
```http
POST /api/v2/characters/{id}/branches
```
Request Body:
```json
{
  "theme": "string",
  "branch_name": "string",
  "parent_branch": "string|null",
  "preserve_memory": "boolean"
}
```

Response:
```json
{
  "branch_id": "uuid",
  "character": {...},  # Full character sheet
  "modified_content": {
    "inherited": ["string"],  # Content IDs that came from parent
    "root_reset": ["string"],  # Content IDs that reset to root
    "new": ["string"]  # Newly generated content IDs
  }
}
```

### 9.2 Content Branching
```http
POST /api/v2/content/{id}/branches
```
Request Body:
```json
{
  "theme": "string",
  "branch_name": "string",
  "adaptation_level": "none|minor|major|complete"
}
```

Response:
```json
{
  "branch_id": "uuid",
  "content": {
    "id": "uuid",
    "type": "string",
    "name": "string",
    "properties": {},
    "root_id": "uuid"  # Original content this was adapted from
  }
}
```

### 9.3 Branch Management
```http
GET /api/v2/characters/{id}/branches  # List character branches
GET /api/v2/content/{id}/branches     # List content branches
POST /api/v2/characters/{id}/branches/{branch_id}/merge  # Merge character branches
POST /api/v2/content/{id}/branches/{branch_id}/merge     # Merge content branches
```

### 9.4 Content Search & Reuse
```http
GET /api/v2/catalog/search/semantic
```
Request Parameters:
```json
{
  "query": "string",        # Semantic search query
  "type": "string",         # Content type to search for
  "theme": "string",        # Theme to consider
  "adaptation_allowed": "boolean"  # Whether content can be modified
}
```

Response:
```json
{
  "matches": [
    {
      "content_id": "uuid",
      "match_score": "float",
      "adaptation_needed": "none|minor|major",
      "theme_alignment": "float"
    }
  ]
}
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
