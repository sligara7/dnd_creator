# System Requirements Document: Character Service (SRD-CS-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The Character Service provides AI-powered D&D 5e 2024 character creation and management, enabling users to create, evolve, and manage ANY character concept through a combination of official D&D content and AI-generated custom content.

### 1.2 Core Mission
- **Creative Freedom**: Generate non-traditional characters beyond standard D&D constraints
- **Custom Content Creation**: Create new classes, species, feats, spells, weapons, and armor
- **Deep Storytelling**: Generate compelling backstories aligned with character concepts
- **Iterative Development**: Collaborative character refinement through user feedback
- **Traditional Foundation**: Prioritize existing D&D content when appropriate

### 1.3 Scope
- Character creation and management
- Custom content generation
- Character refinement and evolution
- Journal and experience tracking
- Campaign theme integration
- Inventory management
- Spell management
- Equipment management
- Real-time gameplay support

## 2. Functional Requirements

### 2.1 Character Creation System
- **Input**: User-provided character concept description
- **Output**: Complete D&D 5e 2024 character sheet
- **Process**: LLM concept translation → validation → generation
- **Flexibility**: Support any character concept with custom content
- **Required Components**:
  - Core Attributes (name, species, class, level, background, alignment)
  - Ability Scores (STR, DEX, CON, INT, WIS, CHA)
  - Skills & Proficiencies
  - Feats (origin, general, fighting styles, epic boons)
  - Equipment (weapons, armor, tools)
  - Spells (for spellcasters)
  - Backstory
  - Personality traits

### 2.2 Custom Content Generation
- Custom species with balanced traits
- Custom classes with progression
- Custom feats
- Custom spells
- Custom weapons and armor
- Balance validation for all custom content

### 2.3 Iterative Refinement System
- User-driven character updates
- Version history tracking
- Consistency maintenance
- DM approval workflow

### 2.4 Theme Integration
- Support campaign themes (western, cyberpunk, etc.)
- Theme-aware content generation
- Player agency preservation
- Campaign service integration

### 2.5 Journal System
- Session tracking
- Experience logging
- Character development tracking
- Level-up suggestions based on play history
- Journal CRUD operations (create, read, update, delete)
- Session linkage and milestones
- Session tracking
- Experience logging
- Character development tracking
- Level-up suggestions based on play history

### 2.6 Version Control and Approval
- Git-like branching for character evolution
- Merge and conflict resolution strategies
- Change history and rollback
- DM approval workflow for critical changes

### 2.7 Inventory Management
- Complete inventory CRUD operations
- Equipment slot management
- Attunement system (3-item limit)
- Item properties tracking

### 2.7 Unified Catalog
- Central catalog of items, spells, and equipment
- Cross-character sharing and access control
- Recommendation engine for appropriate items/spells
- Catalog CRUD and search

### 2.8 Spell Management
- Spell preparation tracking
- Spell slot management
- Ritual casting support
- Known vs prepared spell distinction

### 2.8 Complete Character Sheet
- Full D&D 5e sheet structure (identity, statistics, combat, actions, equipment, spellcasting)
- Support for NPCs and monsters as playable sheets
- Conversion utilities and validation

### 2.9 Equipment Management
- Equipment swapping
- Optimization suggestions
- Synergy tracking
- Enchantment management
- Equipment history

## 3. Technical Requirements

### 3.1 System Architecture
- Performance monitoring endpoints and middleware
- Prometheus/Grafana integration
- Request timing and DB metrics
- LLM Integration (OpenAI/Ollama)
- Message Hub integration
- Database persistence
- RESTful API
- Error handling
- Performance monitoring

### 3.2 Performance Standards
- Character creation: < 30 seconds
- Simple updates: < 5 seconds
- Database queries: < 1 second
- Support 10+ concurrent creations

### 3.3 Data Requirements
- UUID tracking for all entities
- Git-like version control
- Audit trails for changes
- Data validation and integrity

### 3.4 Integration Requirements
- Message Hub connectivity
- Campaign service integration
- LLM service integration
- Authentication service support

## 4. API Endpoints

### 4.1 Character Management
```http
POST /api/v2/factory/create
GET /api/v2/characters/{id}
PUT /api/v2/characters/{id}/refine
POST /api/v2/characters/{id}/level-up
PUT /api/v2/characters/{id}/feedback
```

### 4.2 Custom Content
```http
POST /api/v2/factory/create
POST /api/v2/factory/evolve
GET /api/v2/factory/types
```

### 4.3 Inventory & Equipment
```http
GET /api/v2/characters/{id}/inventory
POST /api/v2/characters/{id}/inventory/add
PUT /api/v2/characters/{id}/equipment/swap
GET /api/v2/characters/{id}/equipment/optimize
```

### 4.4 Spells
```http
PUT /api/v2/characters/{id}/spells/swap
POST /api/v2/characters/{id}/spells/prepare
GET /api/v2/characters/{id}/spells/slots
```

### 4.5 Journal
```http
DELETE /api/v2/characters/{id}/journal/{entry_id}
```

### 4.6 Complete Sheets
```http
GET /api/v2/characters/{id}/sheet
GET /api/v2/npcs/{id}/sheet
GET /api/v2/monsters/{id}/sheet
```

### 4.7 Unified Catalog
```http
GET /api/v2/catalog
GET /api/v2/catalog/search
POST /api/v2/catalog
PUT /api/v2/catalog/{item_id}
DELETE /api/v2/catalog/{item_id}
```

### 4.8 Version Control
```http
POST /api/v2/characters/{id}/branches
GET /api/v2/characters/{id}/branches
POST /api/v2/characters/{id}/branches/{branch_id}/merge
```

### 4.9 Metrics
```http
GET /api/v2/metrics
```
```http
GET /api/v2/characters/{id}/journal
POST /api/v2/characters/{id}/journal
PUT /api/v2/characters/{id}/journal/{entry_id}
```

### 4.6 Direct Edit
```http
PUT /api/v2/characters/{id}/direct-edit
PUT /api/v2/characters/{id}/backstory/direct-edit
PUT /api/v2/characters/{id}/journal/{entry_id}/direct-edit
```

## 5. Service Integration

### 5.1 Message Hub Integration (Required)
- All service communication MUST go through Message Hub
- No direct service-to-service communication allowed

#### 5.1.1 Published Events
- character.created
- character.updated
- character.deleted
- character.validated
- character.leveled_up
- character.refined
- character.journal_updated
- character.inventory_changed
- character.spells_changed

#### 5.1.2 Subscribed Events
- campaign.theme_changed
- campaign.validated
- llm.content_generated
- llm.refinement_suggested

### 5.2 Campaign Integration (via Message Hub)
- Theme integration through campaign.theme_changed events
- Campaign context through campaign.context_updated events
- Character validation through campaign.validate_character events
- DM approvals through campaign.character_approved events

### 5.3 LLM Integration (via Message Hub)
- Content generation through llm.generate_content events
- Refinement suggestions through llm.suggest_refinements events
- Character evolution through llm.evolve_character events
- Story enhancement through llm.enhance_story events

## 6. Data Models

### 6.1 Character Model
```json
{
  "id": "uuid",
  "name": "string",
  "species": "string",
  "class": "string",
  "level": "integer",
  "ability_scores": {},
  "skills": [],
  "feats": [],
  "equipment": [],
  "spells": [],
  "backstory": "string",
  "journal": [],
  "versions": [],
  "audit_trail": []
}
```

### 6.2 Journal Entry
```json
{
  "id": "uuid",
  "character_id": "uuid",
  "session_date": "date",
  "content": "string",
  "xp_gained": "integer",
  "milestones": [],
  "dm_notes": "string"
}
```

### 6.3 Custom Content
```json
{
  "id": "uuid",
  "type": "string",
  "name": "string",
  "description": "string",
  "properties": {},
  "balance_score": "float",
  "user_modified": "boolean",
  "audit_trail": []
}
```

## 7. Security Requirements

### 7.1 Authentication & Authorization
- JWT validation
- Role-based access control
- DM approval workflow
- Audit trail tracking

### 7.2 Data Protection
- Secure storage
- Data encryption
- Personal data handling
- Backup strategy

## 8. Monitoring Requirements

### 8.1 Performance Metrics
- Request latency
- Error rates
- Resource usage
- Concurrent operations

### 8.2 Health Checks
- Service health status
- Dependency health
- Resource availability
- Error conditions
