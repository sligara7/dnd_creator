# System Requirements Document: Character Service (SRD-CS-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The Character Service provides AI-powered D&D 5e 2024 character creation and management, enabling users to create, evolve, and manage ANY character concept through a combination of official D&D content and AI-generated custom content.

### 1.2 Core Principles
- Provide service-specific functionality
- All inter-service communication MUST go through Message Hub
- No direct service-to-service communication allowed
- Service isolation and independence
- Event-driven architecture

#### Primary Mission
- **Concept to Character**: Transform ANY character concept into a valid D&D character
- **Smart Content Mix**: Blend new and existing D&D content efficiently
- **Gameplay Evolution**: Evolve characters based on actual play style
- **Iterative Refinement**: Continuous character improvement through feedback

#### Key Principles
- Start with user's character concept (even non-D&D concepts like "Yoda")
- Use LLM to understand and translate the concept
- Create custom content when needed (classes, species, etc.)
- Use existing D&D content catalog when appropriate
- Track actual gameplay to inform character evolution
- Allow continuous refinement and iteration

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

### 2.1.1 Character Sheet Fields

The character sheet MUST support all fields defined in the 2024 specification:

#### Independent Variables (Modifiable Fields)

Core Information:
- Character Name (string)
- Class & Level (class string, level 1-20)
- Background (string)
- Player Name (string)
- Race/Species (string)
- Alignment (LG, NG, CG, LN, N, CN, LE, NE, CE)
- Experience Points (0-355,000+)

Ability Scores:
- Base Strength (1-20, max 30 with modifiers)
- Base Dexterity (1-20, max 30 with modifiers)
- Base Constitution (1-20, max 30 with modifiers)
- Base Intelligence (1-20, max 30 with modifiers)
- Base Wisdom (1-20, max 30 with modifiers)
- Base Charisma (1-20, max 30 with modifiers)

Health & Resources:
- Current Hit Points (0 to max)
- Temporary Hit Points (0+)
- Hit Dice (based on class and level)
- Death Save Successes/Failures (0-3 each)
- Exhaustion Level (0-6)
- Inspiration (0 or 1)

Proficiencies:
- Languages (list of strings)
- Tool Proficiencies (list with types)
- Weapon Proficiencies (list of types)
- Armor Proficiencies (list of types)

Equipment & Inventory:
- Weapons (list with properties)
- Armor (list with properties)
- Other Equipment (list with properties)
- Currency (CP, SP, EP, GP, PP)

Character Details:
- Age (number)
- Height (string)
- Weight (string)
- Eye Color (string)
- Skin Color (string)
- Hair Color (string)
- Personality Traits (string list)
- Ideals (string list)
- Bonds (string list)
- Flaws (string list)

Spellcasting (if applicable):
- Spells Known/Prepared (list by level)
- Spell Slots Used (by level)

#### Derived Variables (Read-Only Fields)

Ability Modifiers:
- Strength Modifier ((score - 10) ÷ 2, rounded down)
- Dexterity Modifier ((score - 10) ÷ 2, rounded down)
- Constitution Modifier ((score - 10) ÷ 2, rounded down)
- Intelligence Modifier ((score - 10) ÷ 2, rounded down)
- Wisdom Modifier ((score - 10) ÷ 2, rounded down)
- Charisma Modifier ((score - 10) ÷ 2, rounded down)

Combat Statistics:
- Armor Class (10 + Dex mod + armor/shield bonuses)
- Initiative (Dex modifier + bonuses)
- Speed (base from race + modifiers)
- Hit Point Maximum (class HD max + Con mod at 1st, roll/avg + Con mod per level after)
- Proficiency Bonus (based on level: +2 to +6)

Saving Throws (all ability modifiers + proficiency if proficient):
- Strength Save
- Dexterity Save
- Constitution Save
- Intelligence Save
- Wisdom Save
- Charisma Save

Skill Modifiers (ability modifier + proficiency if proficient):
- Acrobatics (Dex)
- Animal Handling (Wis)
- Arcana (Int)
- Athletics (Str)
- Deception (Cha)
- History (Int)
- Insight (Wis)
- Intimidation (Cha)
- Investigation (Int)
- Medicine (Wis)
- Nature (Int)
- Perception (Wis)
- Performance (Cha)
- Persuasion (Cha)
- Religion (Int)
- Sleight of Hand (Dex)
- Stealth (Dex)
- Survival (Wis)

Passive Scores:
- Passive Perception (10 + Perception bonus)
- Passive Investigation (10 + Investigation bonus)
- Passive Insight (10 + Insight bonus)

Spellcasting (if applicable):
- Spell Save DC (8 + proficiency + spellcasting ability modifier)
- Spell Attack Bonus (proficiency + spellcasting ability modifier)
- Total Spell Slots (by level, based on class/level)

#### Tracked States

Conditions (boolean flags):
- Blinded
- Charmed
- Deafened
- Frightened
- Grappled
- Incapacitated
- Invisible
- Paralyzed
- Petrified
- Poisoned
- Prone
- Restrained
- Stunned
- Unconscious

Concentration:
- Active (boolean)
- Spell Being Concentrated On (string)

### 2.2 Theme Management & Content Strategy

#### 2.2.1 Theme Branching Model
- Characters and their memories branch through themes while maintaining history
- Equipment and content reset to root versions with each theme change
- Each theme change creates new UUIDs for changed entities:
  * New character version gets new UUID but tracks parent version
  * Equipment links back to root theme version UUID
  * Relationships between versions maintained in version graph

Example Flow:
Chapter 1 (Cyberpunk):
```
Yoda-CyberA (UUID-1)
  |-- Lightsaber-CyberA (UUID-2)
```

Chapter 2 (Fantasy):
```
Yoda-FantasyA (UUID-3)
  |-- parent: UUID-1 (Yoda-CyberA)
  |-- Lightsaber-FantasyA (UUID-4)
      |-- root: UUID-2 (Lightsaber-CyberA)
```

Chapter 3 (Return to Cyberpunk):
```
Yoda-CyberB (UUID-5)
  |-- parent: UUID-3 (Yoda-FantasyA)
  |-- Lightsaber-CyberA (UUID-2) # Original cyberpunk version
```

#### 2.2.2 Theme Version Relationships
- Version Graph for Entity Types:
  * Characters: Linear progression with parent links
  * Equipment/Content: Star pattern with root links
  * Theme transitions create new character versions
  * Equipment relinks to original theme versions

#### 2.2.3 Content Reuse Priority
- MUST prioritize using existing D&D content before generating custom content
- Search unified catalog with semantic matching for appropriate content
- Allow minor modifications to existing content for theme alignment
- Only generate custom content when no suitable existing content matches
- Track content origin and modifications for auditing

#### 2.2.2 Content Types
- Primary Content (has memory and evolution):
  * Characters
  * Character relationships
  * Character experiences and development
  * Character narrative arcs
- Reusable Content (resets to root on branching):
  * Items (weapons, armor, tools)
  * Spells
  * Species/races
  * Classes/subclasses
  * Feats
  * Background elements

#### 2.2.3 Custom Content Generation
- Custom species with balanced traits
- Custom classes with progression
- Custom feats
- Custom spells
- Custom weapons and armor
- Balance validation for all custom content
- Tracking of justification for custom vs. reused content

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

### 6.1 Version Control Model
```json
{
  "version_graph": {
    "id": "uuid",
    "type": "character|equipment",
    "versions": [
      {
        "id": "uuid",
        "theme": "string",
        "parent_id": "uuid|null",
        "root_id": "uuid|null",
        "created_at": "timestamp",
        "entity_data": {}
      }
    ],
    "relationships": [
      {
        "version_id": "uuid",
        "related_content": [
          {
            "content_id": "uuid",
            "relationship": "equipped|owned|created",
            "theme_version": "string"
          }
        ]
      }
    ]
  }
}
```

### 6.2 Character Model
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
