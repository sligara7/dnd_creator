# Phase 4: Endpoint Removal Analysis

## Current State Analysis

### Factory v2 Endpoints (Keep - Primary Interface)
- `POST /api/v2/factory/create` - Unified creation for all content types
- `POST /api/v2/factory/evolve` - Evolution with history preservation  
- `POST /api/v2/factory/level-up` - Specialized character leveling
- `GET /api/v2/factory/types` - API discovery

### Generation v1 Endpoints (Analyze for Removal)
- `POST /api/v1/generate/backstory` - **REDUNDANT** (covered by factory/create)
- `POST /api/v1/generate/equipment` - **REDUNDANT** (covered by factory/create)
- `POST /api/v1/generate/content` - **KEEP** (good v1 unified interface)
- `POST /api/v1/generate/character-complete` - **KEEP** (valuable workflow)
- `POST /api/v1/characters/generate` - **REDUNDANT** (covered by factory/create + save)

### Character Management Endpoints (Keep - Core Functionality)
- All CRUD operations remain essential
- Character state management remains essential
- Evolution endpoint added in Phase 3 provides good v1 interface

## Removal Strategy

### Safe to Remove (Redundant Functionality)
1. `POST /api/v1/generate/backstory` → Use `POST /api/v2/factory/create` with content_type="character"
2. `POST /api/v1/generate/equipment` → Use `POST /api/v2/factory/create` with content_type="weapon/armor"  
3. `POST /api/v1/characters/generate` → Use `POST /api/v2/factory/create` with save_to_database=true

### Keep (Unique Value)
1. `POST /api/v1/generate/content` - Good v1 unified interface
2. `POST /api/v1/generate/character-complete` - Valuable one-call workflow
3. `POST /api/v1/characters/{id}/evolve` - Good v1 evolution interface

## Benefits of Removal
- Reduces API surface area
- Eliminates code duplication
- Forces migration to better factory pattern
- Simplifies maintenance
- Clearer API structure
