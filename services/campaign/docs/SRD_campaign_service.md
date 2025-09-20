# System Requirements Document: Campaign Service (SRD-CP-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The Campaign Service provides AI-powered D&D 5e 2024 campaign creation and management, enabling DMs to create and run dynamic campaigns with branching storylines, theme-aware content, and deep narrative integration.

### 1.2 Core Principles
- Provide service-specific functionality
- All inter-service communication MUST go through Message Hub
- No direct service-to-service communication allowed
- Service isolation and independence
- Event-driven architecture

### 1.3 Communication Requirements
- **Service Isolation**: Campaign Service MUST NOT communicate directly with other services
- **Message Hub**: ALL inter-service communication MUST be routed through the Message Hub service
- **Asynchronous Communication**: Service must handle asynchronous message-based interactions
- **Event-Driven Architecture**: Service must publish and subscribe to events via Message Hub

### 1.3 Scope
- Campaign creation and management
- Theme and setting management
- Chapter organization
- NPC and monster management
- Map generation
- Plot branching and tracking
- Character integration
- Resource management
- Real-time campaign adaptation

## 2. Functional Requirements

### 2.1 AI-Driven Campaign Generation
- User-provided campaign concepts (50-500 words)
- Complete storyline generation
- Multi-layered plots with intrigue
- Morally complex scenarios
- Multi-genre support (fantasy, sci-fi, horror, etc.)
- Iterative refinement capability

### 2.3 Version Control System
- Git-like chapter versioning
- Branch management (main, alternate, player choice)
- Version history tracking
- Merge handling
- Session state management
- Choice tracking

### 2.4 Campaign Content Coordination
- Campaign-level orchestration
- Batch chapter generation
- Cross-chapter validation
- Narrative flow management
- Content consistency
- Theme propagation

### 2.5 D&D Mechanics Integration
- Challenge Rating system
- Encounter balancing
- Character statistics
- Campaign balance utilities
- Session XP budgeting
- Encounter mix suggestions

### 2.6 Campaign Structure
- Choose Your Own Adventure framework
- Branching narrative structure
- Story path tracking
- Decision points with meaningful choices
- High-level campaign outlines
- 3-20 session support

### 2.3 Chapter System
- Discrete chapter organization
- Clear objectives and conflicts
- Chapter summaries (100-300 words)
- Dependencies and prerequisites
- Location descriptions and maps
- NPC integration
- Encounter generation
- Treasure/rewards system

### 2.4 Theme System
#### Core Themes
- Puzzle Solving
- Mystery Investigation
- Tactical Combat
- Character Interaction
- Political Intrigue
- Exploration
- Horror/Survival
- Psychological Drama
- Heist/Infiltration
- Resource Management
- Time Travel
- Moral Philosophy
- Educational Historical

#### Setting Themes
- Western
- Steampunk
- Cyberpunk
- Horror
- Space Fantasy
- Post-Apocalyptic
- Noir/Detective
- High/Low Fantasy
- Historical Period-Specific

### 2.5 Plot Management
- Dynamic story branching
- Choice tracking
- Major/minor branch management
- Plot fork visualization
- Branch consequence tracking
- Fork exploration tracking

### 2.6 Campaign Adaptation
- Real-time updates based on play
- Player choice analysis
- Difficulty adjustment
- NPC reaction management
- Story consistency maintenance

### 2.7 Historical/Fictional Integration
- Historical event adaptation
- Period templates
- Fantasy/historical blending
- Fictional universe adaptation
- Source material integration
- Legal compliance management

## 3. Technical Requirements

### 3.1 Performance Standards
- Campaign skeleton: < 30 seconds
- Chapter generation: < 60 seconds
- Support 50+ chapters
- Refinement time: < 45 seconds
- 10+ concurrent generations
- 8+ player characters
- 1000+ saved campaigns per user

### 3.2 Integration Requirements

#### Message Hub (Required Gateway)
- ALL service-to-service communication MUST go through Message Hub
- NO direct service-to-service calls are permitted
- Event publication/subscription for all integrations
- Service discovery and health monitoring
- State synchronization and transaction management

#### Character Service Integration (via Message Hub)
- Party composition import
- Character progression tracking
- Real-time updates
- Journal integration
- Experience tracking

#### LLM Service Integration (via Message Hub)
- Content generation
- Story refinement
- Theme adaptation
- NPC personality generation

#### Image Service Integration (via Message Hub)
- Map generation
- Location visualization
- NPC portraits
- Item illustrations

### 3.3 Message Hub Protocol Compliance
- Must implement standard message formats
- Must handle message delivery guarantees
- Must implement proper error handling and retries
- Must maintain message ordering where required
- Must support distributed tracing

## 4. Content Generation

### 4.1 NPC Generation
- Names and descriptions
- Motivations and goals
- Basic statistics
- Species diversity
- Personality traits
- Recurring vs one-time NPCs

### 4.2 Monster Generation
- Challenge rating appropriate monsters
- Theme-appropriate creatures
- Balanced encounters
- Environment integration
- Tactical positioning

### 4.3 Location Generation
- World maps
- Regional maps
- Dungeon layouts
- Building floor plans
- Theme-appropriate styling
- Geographic features

### 4.4 Equipment Generation
- Theme-appropriate items
- Magical artifacts
- Custom weapons/armor
- Quest rewards
- Environmental items

## 5. Theme Implementation

### 5.1 Theme Frameworks
- Campaign-level themes
- Chapter-specific themes
- Theme transitions
- Multi-theme blending
- Custom theme creation

### 5.2 Theme Elements
- Naming conventions
- Cultural elements
- Equipment adaptation
- Location styling
- Plot elements

### 5.3 Theme Consistency
- Cross-chapter consistency
- NPC theme alignment
- Equipment appropriateness
- Location theming
- Plot integration

## 6. Data Models

### 6.1 Campaign Model
```json
{
  "id": "uuid",
  "name": "string",
  "concept": "string",
  "theme": {
    "primary": "string",
    "secondary": "string"
  },
  "chapters": [],
  "npcs": [],
  "locations": [],
  "plot_branches": [],
  "version_history": []
}
```

### 6.2 Chapter Model
```json
{
  "id": "uuid",
  "campaign_id": "uuid",
  "title": "string",
  "summary": "string",
  "objectives": [],
  "encounters": [],
  "npcs": [],
  "locations": [],
  "rewards": [],
  "dependencies": []
}
```

### 6.3 Plot Branch Model
```json
{
  "id": "uuid",
  "chapter_id": "uuid",
  "trigger_condition": "string",
  "choices": [],
  "consequences": [],
  "explored": "boolean"
}
```

## 7. Security Requirements

### 7.1 Authentication & Authorization
- DM role verification
- Player access control
- Content sharing permissions
- Campaign privacy settings

### 7.2 Data Protection
- Campaign data encryption
- Version history protection
- Backup management
- Access logging

## 8. Monitoring Requirements

### 8.1 Performance Metrics
- Generation times
- Request latency
- Resource usage
- Concurrent operations

### 8.2 Campaign Metrics
- Active campaigns
- Chapter completion
- Branch exploration
- Theme usage
- Player engagement
