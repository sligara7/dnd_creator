# Interface Control Document: Image Service (ICD-IM-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. Service Interface

### 1.1 Base URL
```
http://image-service:8002
```

### 1.2 Common Headers
```
X-Request-ID: <uuid>
Content-Type: application/json
Authorization: Bearer <token>
```

## 2. Map Generation API

### 2.1 Create Tactical Map
```http
POST /api/v2/maps/tactical
```

#### Request Body
```json
{
  "size": {
    "width": "integer",
    "height": "integer"
  },
  "grid": {
    "enabled": "boolean",
    "size": "integer",
    "color": "string"
  },
  "theme": "string",
  "features": ["string"],
  "terrain": {
    "type": "string",
    "properties": {}
  }
}
```

### 2.2 Create Campaign Map
```http
POST /api/v2/maps/campaign
```

#### Request Body
```json
{
  "size": {
    "width": "integer",
    "height": "integer"
  },
  "scale": {
    "unit": "string",
    "value": "integer"
  },
  "theme": "string",
  "features": ["string"],
  "points_of_interest": [
    {
      "type": "string",
      "location": {
        "x": "integer",
        "y": "integer"
      },
      "name": "string",
      "icon": "string"
    }
  ]
}
```

### 2.3 Map Operations
```http
GET /api/v2/maps/{id}
PUT /api/v2/maps/{id}/overlay
DELETE /api/v2/maps/{id}
```

## 3. Character Visualization API

### 3.1 Generate Portrait
```http
POST /api/v2/portraits
```

#### Request Body
```json
{
  "character_id": "uuid",
  "theme": "string",
  "style": {
    "pose": "string",
    "background": "string",
    "lighting": "string"
  },
  "equipment": {
    "visible": "boolean",
    "items": ["uuid"]
  }
}
```

### 3.2 Portrait Operations
```http
GET /api/v2/portraits/{id}
PUT /api/v2/portraits/{id}
DELETE /api/v2/portraits/{id}
```

## 4. Item Illustration API

### 4.1 Generate Item Image
```http
POST /api/v2/items
```

#### Request Body
```json
{
  "item_id": "uuid",
  "type": "weapon|armor|other",
  "theme": "string",
  "style": {
    "angle": "string",
    "lighting": "string",
    "detail_level": "string"
  },
  "properties": {
    "material": "string",
    "magical_effects": ["string"],
    "wear_state": "string"
  }
}
```

### 4.2 Item Operations
```http
GET /api/v2/items/{id}
PUT /api/v2/items/{id}
DELETE /api/v2/items/{id}
```

## 5. Overlay API

### 5.1 Add Tactical Overlay
```http
POST /api/v2/maps/{id}/overlay/tactical
```

#### Request Body
```json
{
  "type": "position|range|effect",
  "elements": [
    {
      "id": "uuid",
      "position": {
        "x": "integer",
        "y": "integer"
      },
      "properties": {
        "color": "string",
        "opacity": "float",
        "radius": "integer"
      }
    }
  ]
}
```

### 5.2 Add Campaign Overlay
```http
POST /api/v2/maps/{id}/overlay/campaign
```

#### Request Body
```json
{
  "type": "party|territory|route",
  "elements": [
    {
      "id": "uuid",
      "coordinates": [
        {
          "x": "integer",
          "y": "integer"
        }
      ],
      "properties": {
        "color": "string",
        "style": "string",
        "label": "string"
      }
    }
  ]
}
```

## 6. Theme API

### 6.1 Available Themes
```http
GET /api/v2/themes
```

#### Response
```json
{
  "visual_themes": [
    "fantasy",
    "western",
    "cyberpunk",
    "steampunk",
    "horror",
    "space_fantasy"
  ],
  "style_elements": {
    "architecture": ["string"],
    "clothing": ["string"],
    "technology": ["string"],
    "environment": ["string"]
  }
}
```

### 6.2 Apply Theme
```http
PUT /api/v2/images/{id}/theme
```

#### Request Body
```json
{
  "theme": "string",
  "strength": "float",
  "elements": ["string"],
  "style": {
    "color_scheme": "string",
    "lighting": "string",
    "atmosphere": "string"
  }
}
```

## 7. Integration Endpoints

### 7.1 Character Service Integration
```http
POST /api/v2/characters/{id}/images
GET /api/v2/characters/{id}/gallery
POST /api/v2/characters/{id}/portrait/update
```

### 7.2 Campaign Service Integration
```http
POST /api/v2/campaigns/{id}/maps
GET /api/v2/campaigns/{id}/assets
PUT /api/v2/campaigns/{id}/theme/sync
```

## 8. Message Hub Integration

### 8.1 Events Published
```json
{
  "image_generated": {
    "image_id": "uuid",
    "type": "string",
    "source_id": "uuid",
    "timestamp": "string"
  },
  "overlay_updated": {
    "map_id": "uuid",
    "overlay_id": "uuid",
    "changes": []
  },
  "theme_applied": {
    "image_id": "uuid",
    "theme": "string",
    "elements": []
  }
}
```

### 8.2 Events Subscribed
```json
{
  "character_updated": {
    "character_id": "uuid",
    "changes": []
  },
  "campaign_theme_changed": {
    "campaign_id": "uuid",
    "new_theme": "string"
  },
  "map_state_changed": {
    "map_id": "uuid",
    "overlay_updates": []
  }
}
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
    "getimg_api": "healthy",
    "storage": "healthy",
    "cache": "healthy"
  },
  "metrics": {
    "images_generated": "integer",
    "generation_queue": "integer",
    "error_rate": "float",
    "cache_hit_rate": "float"
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
- `IMAGE_NOT_FOUND`: Image ID not found
- `INVALID_THEME`: Theme not supported
- `GENERATION_ERROR`: Image generation failed
- `OVERLAY_ERROR`: Overlay application failed
- `STORAGE_ERROR`: Image storage/retrieval failed
- `API_ERROR`: External API error
- `THEME_ERROR`: Theme application error
- `PERMISSION_DENIED`: User lacks required permissions
