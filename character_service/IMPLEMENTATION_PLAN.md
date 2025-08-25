# Character Service Implementation Plan

## Phase 2 Implementation Steps

### 1. Performance Monitoring System [COMPLETED]
- [x] Add metrics endpoints for system monitoring:
  - CPU/memory usage tracking
  - Database performance metrics
  - Response time tracking
  - Request counting and error rates
- [x] Implement performance dashboard:
  ```python
  @app.get("/api/v2/metrics")
  async def get_system_metrics():
      return {
          "cpu_usage": await get_cpu_metrics(),
          "memory_usage": await get_memory_metrics(),
          "database_stats": await get_db_metrics(),
          "response_times": await get_timing_metrics(),
          "request_counts": await get_request_metrics()
      }
  ```
- [x] Add prometheus/grafana integration for metrics visualization
- [x] Implement performance logging middleware

Next steps:
1. Create metrics collection service
2. Add system resource monitoring
3. Set up prometheus endpoints
4. Implement request tracking
5. Add database performance monitoring

### 2. Journal Management System [COMPLETED]
- [x] Create journal entry models:
  - Data models for journal entries, sessions, experience
  - Database schema for journal storage
  - Relationship tracking and quest logs
- [x] Create journal entry CRUD endpoints:
  ```python
  @app.post("/api/v2/characters/{character_id}/journal")
  @app.get("/api/v2/characters/{character_id}/journal")
  @app.put("/api/v2/characters/{character_id}/journal/{entry_id}")
  @app.delete("/api/v2/characters/{character_id}/journal/{entry_id}")
  ```
- [x] Add session tracking:
  - Session number
  - Session date
  - Session summary
  - Important events
- [x] Implement experience logging:
  - XP gained per session
  - Milestone achievements
  - Level-up triggers
- [x] Add story integration:
  - Journal-based character development
  - NPC relationship tracking
  - Quest progress tracking

Next steps:
- Completed: Journal service, endpoints, session tracking, experience logging, and story integration are implemented.

### 3. Advanced Version Control
- [ ] Implement Git-like branching:
  ```python
  @app.post("/api/v2/characters/{character_id}/branches")
  @app.get("/api/v2/characters/{character_id}/branches")
  @app.post("/api/v2/characters/{character_id}/branches/{branch_id}/merge")
  ```
- [ ] Add conflict resolution system:
  - Detect conflicting changes
  - Provide merge strategies
  - Keep change history
- [ ] Implement approval workflow:
  - DM review process
  - Change request system
  - Approval tracking

### 4. Optimization Features
- [ ] Add response caching:
  - Character sheet caching
  - Template caching
  - Asset caching
- [ ] Implement query optimization:
  - Indexed searches
  - Query result caching
  - Lazy loading
- [ ] Add concurrent request handling:
  - Request queuing
  - Load balancing
  - Rate limiting

## Complete Character Sheet Implementation

### Core Models Update
Update character models to include all required fields:

```python
class CharacterIdentity(BaseModel):
    name: str
    player_name: str
    species: str
    class_levels: Dict[str, int]  # e.g., {"Fighter": 5, "Wizard": 2}
    background: str
    alignment: str
    xp: int
    heroic_inspiration: bool
    personality: Dict[str, str]
    appearance: Dict[str, str]

class CoreStatistics(BaseModel):
    ability_scores: Dict[str, int]
    ability_modifiers: Dict[str, int]
    proficiency_bonus: int
    saving_throws: Dict[str, bool]  # Proficiencies
    skills: Dict[str, bool]  # Proficiencies
    passive_perception: int
    other_proficiencies: List[str]
    languages: List[str]

class CombatHealth(BaseModel):
    armor_class: int
    initiative: int
    speed: int
    hp_maximum: int
    current_hp: int
    temporary_hp: int
    hit_dice_total: str
    hit_dice_remaining: str
    death_saves: Dict[str, int]
    exhaustion_level: int

class ActionsTraits(BaseModel):
    weapons: List[WeaponAttack]
    weapon_masteries: List[str]
    features: List[Feature]
    traits: List[Trait]

class Equipment(BaseModel):
    inventory: List[Item]
    currency: Dict[str, int]
    magical_items: List[MagicalItem]
    carrying_capacity: int
    current_load: int

class Spellcasting(BaseModel):
    spellcasting_ability: Optional[str]
    spell_save_dc: Optional[int]
    spell_attack_bonus: Optional[int]
    spell_slots: Dict[int, Dict[str, int]]  # Level -> {max: int, current: int}
    spells_known: List[Spell]
    spells_prepared: List[Spell]

class CompleteCharacterSheet(BaseModel):
    identity: CharacterIdentity
    statistics: CoreStatistics
    combat: CombatHealth
    actions: ActionsTraits
    equipment: Equipment
    spellcasting: Optional[Spellcasting]
    conditions: List[Condition]
    notes: str
    version: str
    last_updated: datetime
    audit_trail: List[AuditEntry]
```

### Factory Update
Modify factory to generate complete character sheets:

```python
class CharacterFactory:
    async def create_complete_character(self, prompt: str, **kwargs) -> CompleteCharacterSheet:
        """Create a complete character sheet from a prompt."""
        # Generate base character
        base_character = await self._generate_base_character(prompt)
        
        # Generate full statistics
        statistics = await self._generate_statistics(base_character)
        
        # Generate combat stats and equipment
        combat = await self._generate_combat_stats(base_character)
        equipment = await self._generate_equipment(base_character)
        
        # Generate spellcasting if applicable
        spellcasting = None
        if self._is_spellcaster(base_character):
            spellcasting = await self._generate_spellcasting(base_character)
        
        # Compile complete sheet
        return CompleteCharacterSheet(
            identity=base_character.identity,
            statistics=statistics,
            combat=combat,
            actions=base_character.actions,
            equipment=equipment,
            spellcasting=spellcasting,
            conditions=[],
            notes="",
            version="1.0",
            last_updated=datetime.utcnow(),
            audit_trail=[{"timestamp": datetime.utcnow(), "action": "created"}]
        )
```

### NPC and Monster Integration
Extend complete character sheet support to NPCs and monsters:

```python
class NPCFactory:
    async def create_playable_npc(self, prompt: str, **kwargs) -> CompleteCharacterSheet:
        """Create an NPC with a complete character sheet."""
        # Generate NPC base
        npc_base = await self._generate_npc_base(prompt)
        
        # Convert to full character sheet
        return await self._convert_to_character_sheet(npc_base)

class MonsterFactory:
    async def create_playable_monster(self, prompt: str, **kwargs) -> CompleteCharacterSheet:
        """Create a monster with a complete character sheet."""
        # Generate monster base
        monster_base = await self._generate_monster_base(prompt)
        
        # Convert to full character sheet if requested
        if kwargs.get("make_playable", False):
            return await self._convert_to_character_sheet(monster_base)
        return monster_base
```

### Database Schema Updates
The database schema will need to be updated to store the complete character sheet data:

```sql
-- Add new tables and columns for complete character sheets
ALTER TABLE characters ADD COLUMN complete_sheet JSONB;
ALTER TABLE npcs ADD COLUMN complete_sheet JSONB;
ALTER TABLE monsters ADD COLUMN complete_sheet JSONB;

-- Add indices for commonly queried fields
CREATE INDEX idx_character_name ON characters ((complete_sheet->>'name'));
CREATE INDEX idx_character_level ON characters ((complete_sheet->>'level'));
CREATE INDEX idx_character_class ON characters ((complete_sheet->>'class'));
```

### API Endpoints
Update API endpoints to support complete character sheets:

```python
@app.get("/api/v2/characters/{character_id}/sheet")
async def get_character_sheet(character_id: str) -> CompleteCharacterSheet:
    """Get complete character sheet."""

@app.get("/api/v2/npcs/{npc_id}/sheet")
async def get_npc_sheet(npc_id: str) -> CompleteCharacterSheet:
    """Get complete NPC sheet."""

@app.get("/api/v2/monsters/{monster_id}/sheet")
async def get_monster_sheet(monster_id: str) -> CompleteCharacterSheet:
    """Get complete monster sheet."""
```

## Implementation Order and Progress

### 1. Core Model Updates [COMPLETED]

#### Character Sheet Models
- [x] Implement CharacterIdentity model
  - [x] Add core identity fields (name, player, species, class, etc.)
  - [x] Add background and personality
  - [x] Add appearance details
- [x] Implement CoreStatistics model
  - [x] Add ability scores and modifiers
  - [x] Add proficiency system
  - [x] Add skills and saving throws
  - [x] Add languages and other proficiencies
- [x] Implement CombatHealth model
  - [x] Add HP and AC tracking
  - [x] Add hit dice system
  - [x] Add death save tracking
  - [x] Add condition and exhaustion tracking
- [x] Implement ActionsTraits model
  - [x] Add weapons and attacks
  - [x] Add special abilities
  - [x] Add class features
  - [x] Add racial traits
- [x] Implement Equipment model
  - [x] Add inventory system
  - [x] Add currency tracking
  - [x] Add magical items
  - [x] Add carrying capacity
- [x] Implement Spellcasting model
  - [x] Add spell slots
  - [x] Add known/prepared spells
  - [x] Add casting modifiers
  - [x] Add ritual casting

#### Database Schema Updates
- [x] Create necessary tables for new models
  - [x] Add complete_sheet JSON column
  - [x] Add audit_trail for tracking changes
  - [x] Add indices for common queries
  - [x] Add UUID support for all entities

#### Conversion Utilities
- [x] Create base-to-complete sheet converter
- [x] Create sheet-to-API response converter
- [x] Create validation utilities
- [x] Create migration tools for existing characters

### 2. Factory Updates [COMPLETED]
- [x] Modify character factory for complete sheets
  - [x] Update base character generation
  - [x] Add complete sheet generation
  - [x] Add validation hooks
- [x] Update NPC factory
  - [x] Add NPC-specific generation rules
  - [x] Implement sheet conversion
  - [x] Add validation
- [x] Update monster factory
  - [x] Add monster-specific generation
  - [x] Implement playable conversion
  - [x] Add validation

### 3. Performance Monitoring [COMPLETED]
- [x] Add performance metrics tracking
  - [x] Implement CPU/Memory monitoring
  - [x] Add request timing metrics
  - [x] Track database performance
  - [x] Add error rate monitoring
- [x] Set up monitoring infrastructure
  - [x] Configure prometheus endpoints
  - [x] Set up grafana dashboards
  - [x] Add alert configurations
- [x] Implement optimization features
  - [x] Add response caching
  - [x] Implement query optimization
  - [x] Add request queuing

### 4. Journal System [COMPLETED]
- [x] Implement journal service
  - [x] Create core journal service
  - [x] Add persistence layer
  - [x] Implement CRUD operations
- [x] Add session tracking
  - [x] Add session model
  - [x] Implement session service
  - [x] Add session endpoints
- [x] Add experience logging
  - [x] Create XP tracking system
  - [x] Add milestone tracking
  - [x] Implement level-up triggers
- [x] Implement story integration
  - [x] Add character development tracking
  - [x] Add NPC relationship system
  - [x] Create quest progress tracking

### 5. Version Control [COMPLETED]
- [x] Implement versioning system
  - [x] Add version tracking
  - [x] Implement change history
  - [x] Add rollback support
- [x] Add branching system
  - [x] Implement branch creation
  - [x] Add branch management
  - [x] Support parallel development
- [x] Create merge system
  - [x] Add conflict detection
  - [x] Implement resolution strategies
  - [x] Add validation checks

### 6. Testing & Optimization [COMPLETED]
- [x] Implement testing framework
  - [x] Add unit tests
  - [x] Add integration tests
  - [x] Add end-to-end tests
- [x] Add performance optimization
  - [x] Implement caching layer
  - [x] Add database optimization
  - [x] Optimize API responses
- [x] Create monitoring system
  - [x] Add performance tracking
  - [x] Implement error logging
  - [x] Add system health checks
