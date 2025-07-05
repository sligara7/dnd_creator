# Task 3b: Backend-Integrated Campaign Item Endpoints

## Overview

This implements backend-integrated item management endpoints for the campaign service. The campaign service can now:

1. **Standalone Operation**: Work independently without the backend service
2. **Optional Integration**: Use the backend service for enhanced item creation when available  
3. **Graceful Fallback**: Fall back to LLM-based generation when backend is unavailable
4. **Campaign-Specific Metadata**: Track campaign-specific item information locally

## New Endpoints

### Item Management
- `POST /api/v2/campaigns/{campaign_id}/items` - Link or create item via backend
- `GET /api/v2/campaigns/{campaign_id}/items` - List campaign items  
- `GET /api/v2/campaigns/{campaign_id}/items/{item_id}` - Get specific item
- `PUT /api/v2/campaigns/{campaign_id}/items/{item_id}` - Update item metadata
- `DELETE /api/v2/campaigns/{campaign_id}/items/{item_id}` - Remove item from campaign

## Key Features

### 1. Backend Integration with Fallback
```python
# Try backend service first
try:
    backend_item = await backend_service.create_item(item_type, context)
except:
    # Fall back to LLM generation
    backend_item = await fallback_item_generation(item_type, context)
```

### 2. Campaign Theme Support
Items can be created with optional campaign theme/context:
```json
{
  "item_type": "weapon",
  "campaign_context": "A cyberpunk campaign needs futuristic weapons",
  "campaign_metadata": {
    "found_in_chapter": "Chapter 1",
    "assigned_to_character": "Street Samurai"
  }
}
```

### 3. Standalone Architecture
- Campaign service works independently
- Backend service works independently  
- Optional cross-service integration when both are running
- No hard dependencies between services

### 4. Data Storage Strategy
- **Backend Service**: Stores full item data (stats, properties, etc.)
- **Campaign Service**: Stores only campaign-specific metadata and links
- **Link Table**: `CampaignItemLink` tracks relationships

## Database Schema

### CampaignItemLink Table
```sql
- id (UUID, primary key)
- campaign_id (UUID, foreign key)
- backend_item_id (UUID, nullable) 
- item_type (VARCHAR)
- name (VARCHAR)
- campaign_metadata (JSON)
- created_at (TIMESTAMP)
- updated_at (TIMESTAMP)
```

## Testing

Run the campaign service:
```bash
./test_campaign_item_endpoints.sh
```

Test the endpoints:
```bash
python test_campaign_item_endpoints.py
```

## Integration Flow

1. **Item Creation Request** → Campaign Service
2. **Backend Health Check** → If available, use backend factory
3. **Item Generation** → Backend service or LLM fallback
4. **Link Storage** → Campaign service stores link + metadata
5. **Response** → Combined backend data + campaign metadata

## Theme/Context Support

The system supports optional theme application:
- **With Theme**: `"campaign_context": "steampunk setting"`
- **Without Theme**: Standard D&D item generation
- **Character Choice**: Players can still choose items that don't fit theme

This maintains the balance between thematic consistency and player agency.
