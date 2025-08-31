# Campaign Service - Service Requirements Document (SRD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-31

## Service Overview

The Campaign Service manages campaign organization, story progression, and most importantly, character relationships and interactions within the game world. It serves as the central coordinator for all character-to-character relationships, whether they are player characters, NPCs, or monsters.

## Core Responsibilities

### 1. Campaign Management
- Campaign creation and configuration
- Theme and setting management
- Chapter/session organization
- Story arc tracking
- World state management

### 2. Character Relationship Management
- Track all character-to-character interactions
- Maintain a social graph of relationships
- Record interaction history and evolution
- Handle relationship status changes
- Support for both PC-PC and PC-NPC relationships

### 3. Party Management
- Party composition tracking
- Inter-party relationships
- Party history and achievements
- Group dynamics management

### 4. Plot and Story Tracking
- Story progression tracking
- Quest and objective management
- Plot thread organization
- Event timeline management

### 5. Character Interaction System
- Record and manage character interactions
- Track relationship states and changes
- Handle interaction history
- Support for:
  * Direct interactions (conversations, trades, battles)
  * Indirect interactions (shared events, mutual contacts)
  * Long-term relationship development
  * Social network visualization

## Data Model

### Character Interaction Model
```sql
CREATE TABLE character_interactions (
    id UUID PRIMARY KEY,
    source_character_id VARCHAR NOT NULL,
    target_character_id VARCHAR NOT NULL,
    interaction_type VARCHAR NOT NULL,
    campaign_id VARCHAR NOT NULL,
    interaction_data JSONB NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    deleted_at TIMESTAMP,
    UNIQUE(campaign_id, source_character_id, target_character_id)
);

CREATE TABLE character_relationships (
    id UUID PRIMARY KEY,
    character_id_1 VARCHAR NOT NULL,
    character_id_2 VARCHAR NOT NULL,
    campaign_id VARCHAR NOT NULL,
    relationship_type VARCHAR NOT NULL,
    relationship_data JSONB NOT NULL,
    relationship_score INT NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,
    UNIQUE(campaign_id, character_id_1, character_id_2)
);
```

## Interface Requirements

### 1. Character Service Integration
- Subscribe to character creation/update/deletion events
- Maintain character reference integrity
- Handle character state changes
- Track character evolution impact on relationships

### 2. Message Hub Integration
- Event publication for relationship changes
- Subscription to character events
- Campaign state synchronization
- Interaction event processing

### 3. LLM Service Integration
- Generate interaction narratives
- Provide relationship insights
- Suggest relationship development
- Create interaction summaries

## Functional Requirements

### 1. Character Relationship Management
- Add/update/view character relationships
- Track relationship history
- Calculate relationship scores
- Generate relationship reports

### 2. Interaction Recording
- Record new character interactions
- Update existing interactions
- Query interaction history
- Generate interaction timelines

### 3. Social Network Analysis
- Generate social graphs
- Calculate relationship metrics
- Identify key relationships
- Track relationship changes

### 4. Campaign Integration
- Link relationships to campaign events
- Track relationship impact on story
- Manage campaign-specific relationships
- Handle campaign transitions

## Technical Requirements

### 1. Data Storage
- PostgreSQL for structured data
- JSONB for flexible interaction data
- Graph database capabilities for relationship querying
- Efficient indexing for relationship lookups

### 2. API Design
- RESTful endpoints for relationship management
- WebSocket support for real-time updates
- GraphQL interface for complex queries
- Batch operation support

### 3. Performance Requirements
- Sub-100ms response time for relationship queries
- Support for 1000+ characters per campaign
- Handle 100+ concurrent users
- Manage 10000+ relationships per campaign

### 4. Security Requirements
- Role-based access control
- Campaign-level permissions
- Audit logging for relationship changes
- Data encryption for sensitive information

## Dependencies

### Required Services
- Character Service (character data)
- Message Hub (event communication)
- LLM Service (narrative generation)
- Cache Service (performance)
- Auth Service (security)

### Optional Services
- Search Service (relationship search)
- Audit Service (security logging)
- Metrics Service (monitoring)

## Error Handling

### 1. Character Reference Integrity
- Handle deleted character references
- Maintain relationship history
- Support character restoration
- Handle merged characters

### 2. Relationship Conflicts
- Detect conflicting relationships
- Resolve relationship paradoxes
- Handle duplicate interactions
- Manage relationship cycles

### 3. Data Consistency
- Ensure referential integrity
- Handle partial updates
- Manage concurrent modifications
- Support rollback operations

## Deployment Requirements

### 1. Configuration
- Environment-based configuration
- Feature flags support
- Campaign-level settings
- Performance tuning options

### 2. Monitoring
- Relationship metrics tracking
- Performance monitoring
- Error tracking
- Usage statistics

### 3. Scaling
- Horizontal scaling support
- Campaign-based sharding
- Cache optimization
- Load balancing

## Testing Requirements

### 1. Unit Tests
- Core relationship logic
- Data validation
- Error handling
- Event processing

### 2. Integration Tests
- Service communication
- Database operations
- Cache integration
- Event handling

### 3. Performance Tests
- Load testing
- Stress testing
- Scalability testing
- Concurrency testing

## Documentation Requirements

### 1. API Documentation
- OpenAPI/Swagger specs
- API usage examples
- Error codes and handling
- Rate limits and quotas

### 2. Integration Guide
- Service integration patterns
- Event handling guide
- Error handling guide
- Performance optimization

### 3. Deployment Guide
- Configuration guide
- Scaling guide
- Monitoring guide
- Troubleshooting guide
