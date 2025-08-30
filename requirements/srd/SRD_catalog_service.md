# System Requirements Document: Catalog Service (SRD-CAT-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The Catalog Service provides a unified, centralized catalog system for all D&D content in the system, including items, spells, monsters, and custom content. It ensures consistent access, validation, and discovery of content across all services.

### 1.2 Core Mission
- **Unified Content Management**: Central source for all game content
- **Content Discovery**: Advanced search and filtering capabilities
- **Content Validation**: Ensure consistency and balance
- **Custom Content**: Support user-generated content
- **Theme Integration**: Theme-aware content discovery

### 1.3 Scope
- Item and equipment catalog
- Spell catalog
- Monster catalog
- Custom content management
- Content validation
- Search and discovery
- Theme adaptation
- Content versioning
- Service integration

## 2. Functional Requirements

### 2.1 Content Management

#### 2.1.1 Item Management
- Weapon catalog
- Armor catalog
- Equipment catalog
- Magical items
- Custom items
- Item properties
- Equipment slots
- Attunement rules

#### 2.1.2 Spell Management
- Official spells
- Custom spells
- Spell schools
- Casting requirements
- Level progression
- Component tracking
- Ritual casting

#### 2.1.3 Monster Management
- Official monsters
- Custom monsters
- Challenge ratings
- Environment types
- Behavior patterns
- Combat tactics
- Treasure tables

### 2.2 Content Discovery

#### 2.2.1 Search System
- Full-text search
- Faceted filtering
- Theme-based search
- Property filtering
- Tag-based search
- Semantic search
- Similar content discovery

#### 2.2.2 Recommendation Engine
- Content suggestions
- Theme-based recommendations
- Level-appropriate items
- Class-specific suggestions
- Campaign-appropriate content
- Player preference learning

### 2.3 Content Validation

#### 2.3.1 Balance Checking
- Item balance scoring
- Spell balance validation
- Monster CR verification
- Custom content validation
- Interaction analysis
- Power level assessment

#### 2.3.2 Consistency Validation
- Theme consistency
- Rules compliance
- Version compatibility
- Campaign appropriateness
- Content dependencies
- Reference integrity

### 2.4 Theme Integration

#### 2.4.1 Theme Support
- Theme-based filtering
- Content adaptation
- Visual style matching
- Description adjustment
- Setting integration
- Genre compliance

#### 2.4.2 Theme Management
- Theme definition
- Theme inheritance
- Theme blending
- Theme transitions
- Custom themes
- Theme validation

## 3. Technical Requirements

### 3.1 Integration Requirements

#### 3.1.1 Message Hub Integration
- Event publication/subscription
- Service discovery
- State synchronization
- Health reporting
- Circuit breaker integration

#### 3.1.2 Service Integration (via Message Hub)
- Character Service content requests
- Campaign Service theme coordination
- LLM Service content generation
- Image Service visual assets
- Content validation requests

### 3.2 Performance Requirements
- Search latency < 100ms
- Content retrieval < 50ms
- Validation checks < 200ms
- Support 1000+ concurrent users
- Handle 100,000+ catalog items
- 99.99% uptime

### 3.3 Storage Requirements
- Content versioning
- Full audit trail
- Backup strategy
- Cache management
- Search indexing
- Asset management

## 4. Data Models

### 4.1 Base Content Model
```json
{
  "id": "uuid",
  "type": "item|spell|monster",
  "name": "string",
  "source": "official|custom",
  "description": "string",
  "properties": {},
  "metadata": {
    "version": "string",
    "created_at": "timestamp",
    "updated_at": "timestamp",
    "created_by": "string"
  },
  "theme_data": {
    "themes": ["string"],
    "adaptations": {}
  },
  "validation": {
    "balance_score": "float",
    "consistency_check": "boolean",
    "last_validated": "timestamp"
  }
}
```

### 4.2 Item Model
```json
{
  "type": "item",
  "category": "weapon|armor|equipment|magical",
  "properties": {
    "weight": "float",
    "cost": "integer",
    "rarity": "string",
    "attunement": "boolean",
    "equipment_slot": "string",
    "damage": {
      "dice": "string",
      "type": "string"
    }
  }
}
```

### 4.3 Spell Model
```json
{
  "type": "spell",
  "properties": {
    "level": "integer",
    "school": "string",
    "casting_time": "string",
    "range": "string",
    "components": {
      "verbal": "boolean",
      "somatic": "boolean",
      "material": "string"
    },
    "duration": "string",
    "ritual": "boolean"
  }
}
```

## 5. API Endpoints

### 5.1 Content Management
```http
GET /api/v2/catalog/{type}/{id}
POST /api/v2/catalog/{type}
PUT /api/v2/catalog/{type}/{id}
DELETE /api/v2/catalog/{type}/{id}
```

### 5.2 Search API
```http
GET /api/v2/catalog/search
POST /api/v2/catalog/search/advanced
GET /api/v2/catalog/recommend
```

### 5.3 Validation API
```http
POST /api/v2/catalog/validate
GET /api/v2/catalog/validate/history
```

### 5.4 Theme API
```http
POST /api/v2/catalog/theme/apply
GET /api/v2/catalog/theme/list
```

## 6. Message Hub Events

### 6.1 Published Events
- catalog.item.created
- catalog.item.updated
- catalog.item.deleted
- catalog.item.validated
- catalog.theme.applied
- catalog.search.indexed

### 6.2 Subscribed Events
- character.created (for recommendations)
- campaign.theme_changed
- llm.content_generated
- theme.updated

## 7. Security Requirements

### 7.1 Authentication & Authorization
- Service authentication
- Role-based access
- Content ownership
- Usage tracking
- Rate limiting

### 7.2 Content Security
- Version control
- Access logging
- Content validation
- Data encryption
- Backup strategy

## 8. Monitoring Requirements

### 8.1 Performance Metrics
- Search latency
- API response times
- Cache hit rates
- Index performance
- Resource usage

### 8.2 Content Metrics
- Catalog size
- Usage patterns
- Popular content
- Theme distribution
- Validation stats

## 9. Deployment Requirements

### 9.1 Infrastructure
- Container support
- High availability
- Auto-scaling
- Load balancing
- CDN integration

### 9.2 Dependencies
- Search engine
- Cache service
- Storage service
- Message Hub
- Monitoring service
