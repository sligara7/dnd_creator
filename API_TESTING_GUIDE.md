# D&D Character Creator API Testing System

## Overview
The API testing system has been completely refactored to provide systematic, organized testing of all 34 endpoints from the backend/app.py file. The system is organized by test complexity and execution speed.

## Test Scripts

### 1. `test_api_endpoints.sh` - Main Hub Script
**Usage:** `./test_api_endpoints.sh [BASE_URL] [TEST_TYPE]`

The main entry point that routes to different test suites:
- `quick` (default) - Fast core functionality tests (7 tests, ~5 seconds)
- `full` - Comprehensive all-endpoint tests (35 tests, ~30 seconds)

**Examples:**
```bash
./test_api_endpoints.sh                              # Quick tests on localhost:8000
./test_api_endpoints.sh http://localhost:8001 quick  # Quick tests on port 8001
./test_api_endpoints.sh http://localhost:8000 full   # Full comprehensive tests
```

### 2. `test_api_quick.sh` - Fast Development Tests
**Usage:** `./test_api_quick.sh [BASE_URL]`

Rapid iteration testing for development:
- ✅ Health Check
- ✅ List/Create/Get/Delete Characters
- ✅ Repository Creation & Retrieval
- **Result:** 7/7 tests pass (31% success rate shows core functionality works)

### 3. `test_api_endpoints_refactored.sh` - Comprehensive Suite
**Usage:** `./test_api_endpoints_refactored.sh [BASE_URL]`

Complete systematic testing of all 34 endpoints organized by performance tiers:

## Test Organization by Performance Tiers

### 🏃‍♂️ **Tier 1: FASTEST (Basic Health)**
- Health check endpoint
- **Speed:** <1 second

### 🏃‍♂️ **Tier 2: FAST (Basic CRUD)**
- Character list/create/read operations
- **Speed:** 1-3 seconds

### 🚶‍♂️ **Tier 3: MEDIUM (Character Management)**
- Character updates and validation
- **Speed:** 3-10 seconds

### 🚶‍♂️ **Tier 4: MEDIUM (Versioning System)**
- Repository, branch, commit, tag operations
- **Speed:** 5-15 seconds

### 🚶‍♂️ **Tier 5: SLOWER (Advanced Features)**
- Character sheets, state, combat, rest, level-up
- **Speed:** 10-20 seconds

### 🐌 **Tier 6: SLOW (Content Creation)**
- Item/NPC/Creature creation
- **Speed:** 15-25 seconds

### 🐌 **Tier 7: SLOW (Quick Generation)**
- Non-LLM generation endpoints
- **Speed:** 20-30 seconds

### 🐢 **Tier 8: SLOWEST (LLM Generation)**
- AI-powered content generation (requires LLM service)
- **Speed:** 30+ seconds (depends on LLM response time)

## Current API Status

### ✅ **Working Endpoints (11/35 - 31%)**
1. `GET /health` - Health check
2. `GET /api/v1/characters` - List characters
3. `POST /api/v1/characters` - Create character
4. `GET /api/v1/characters/{id}` - Get character
5. `DELETE /api/v1/characters/{id}` - Delete character
6. `POST /api/v1/character-repositories` - Create repository
7. `GET /api/v1/character-repositories/{id}` - Get repository
8. `GET /api/v1/character-repositories/{id}/branches` - List branches
9. `GET /api/v1/character-repositories/{id}/commits` - List commits
10. `POST /api/v1/generate/quick-creature` - Quick creature generation
11. Various other basic operations

### ❌ **Failing Endpoints (24/35 - 69%)**
**Common Error Patterns:**
1. **Missing method implementations:** `'dict' object has no attribute 'core'`
2. **Constructor issues:** `missing 1 required positional argument: 'character_core'`
3. **Schema mismatches:** Request validation errors
4. **Database constraints:** `NOT NULL constraint failed`

## Development Workflow

### For Quick Development Iteration:
```bash
# Make code changes
./test_api_endpoints.sh  # Run quick tests (7 tests, ~5 seconds)
```

### For Comprehensive Testing:
```bash
# Before major releases or after significant changes
./test_api_endpoints.sh http://localhost:8000 full  # Full test suite
```

### For Debugging Specific Issues:
```bash
# Run specific endpoint tests manually
curl -X GET http://localhost:8000/api/v1/characters
curl -X POST http://localhost:8000/api/v1/characters -H "Content-Type: application/json" -d '{...}'
```

## Features

### Smart ID Management
- Automatically extracts and stores resource IDs (CHARACTER_ID, REPOSITORY_ID, etc.)
- Uses stored IDs for dependent tests
- Graceful handling when IDs aren't available

### Color-Coded Output
- 🟢 Fast tests - Green
- 🔵 Medium tests - Cyan  
- 🟡 Slow tests - Yellow
- 🔴 LLM tests - Red

### Comprehensive Error Reporting
- HTTP status codes
- Response body snippets
- Performance analysis by tier
- Success rate calculations

### Conditional Testing
- Skips tests that depend on unavailable resources
- Maintains accurate test counts
- Clear messaging about skipped tests

## Next Steps for Backend Development

Based on test results, focus on:

1. **Character Core Implementation** - Fix `'dict' object has no attribute 'core'` errors
2. **Constructor Dependencies** - Resolve missing required arguments in generators
3. **Character State Management** - Implement missing methods for sheets/state/combat
4. **Validation System** - Fix character validation implementations
5. **Content Generation** - Resolve CustomContentGenerator and related class issues

The testing system will help track progress as these backend issues are resolved.
