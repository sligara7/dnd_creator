# Test Strategy

Version: 1.0
Status: Active
Last Updated: 2025-09-07

## Overview

This document outlines our testing strategy and tracks test outcomes, root causes, and fixes. The testing approach follows a layered strategy:

1. Individual Service Testing (L1)
2. Service Integration Testing (L2) 
3. LLM-Dependent Integration Testing (L3)

## Test Categories

### L1: Individual Service Testing

Service-specific tests focusing on core functionality without external dependencies.

#### Character Service Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| CHAR-001 | Basic CRUD operations | - | - | - | - |
| CHAR-002 | Character sheet validation | - | - | - | - |
| CHAR-003 | Character evolution tracking | - | - | - | - |
| CHAR-004 | Journal system | - | - | - | - |
| CHAR-005 | Resource management | - | - | - | - |
| CHAR-API-001 | API endpoints import and DI wiring | FAILING | ImportError during FastAPI route wiring in tests/api/test_endpoints.py | FastAPI tried to treat repository class as a Pydantic field due to Depends() directly on EventImpactService; DI not provided | Provide dependency factory get_event_impact_service injecting required repositories; update router to use Depends(get_event_impact_service) |

##### Incident Log: CHAR-API-001

- Layer: L1 (Character Service)
- Repro command:

```bash path=null start=null
PYTHONPATH=src pytest tests/api/test_endpoints.py -q
```

- Error summary:

```text path=null start=null
E   fastapi.exceptions.FastAPIError: Invalid args for response field! ... check that <class 'character_service.infrastructure.repositories.event.CampaignEventRepository'> is a valid Pydantic field type ... The root cause ... FastAPI's default behavior for Depends() is to instantiate the class directly, which requires constructor args to be valid Pydantic types. EventImpactService requires repository instances, which FastAPI cannot resolve automatically.
```

- Root cause details:
  - progress.py uses EventImpactService directly in Depends(), causing FastAPI to parse its __init__ signature.
  - Constructor params are repository classes (not Pydantic types), so FastAPI raises during dependency graph analysis at import time.

- Planned fix:
  1) Create a dependency provider in character_service/api/v2/dependencies.py:
     - get_event_impact_service(...) that constructs EventImpactService with required repositories (resolved from the app container/session).
  2) In progress.py, change endpoint params to:
     - event_service: EventImpactService = Depends(get_event_impact_service)
  3) Ensure repository instances are created with the current AsyncSession and follow the Repository Pattern from WARP.md (UUIDs, soft delete defaults, etc.).

- Acceptance criteria:
  - tests/api/test_endpoints.py imports succeed.
  - App startup creates routes without FastAPIError.
  - Unit tests for progress endpoints run and can mock get_event_impact_service.

#### Campaign Service Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| CAMP-001 | Campaign CRUD operations | - | - | - | - |
| CAMP-002 | Theme system validation | - | - | - | - |
| CAMP-003 | Chapter organization | - | - | - | - |
| CAMP-004 | NPC management | - | - | - | - |
| CAMP-005 | World building features | - | - | - | - |

#### Image Service Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| IMG-001 | Basic image operations | - | - | - | - |
| IMG-002 | Portrait generation mocks | - | - | - | - |
| IMG-003 | Map creation validation | - | - | - | - |
| IMG-004 | Asset management | - | - | - | - |
| IMG-005 | Style transfer validation | - | - | - | - |

#### Message Hub Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| HUB-001 | Message routing | - | - | - | - |
| HUB-002 | Event management | - | - | - | - |
| HUB-003 | Service discovery | - | - | - | - |
| HUB-004 | Health monitoring | - | - | - | - |
| HUB-005 | Circuit breaker functionality | - | - | - | - |

### L2: Service Integration Testing

Tests focusing on service-to-service communication and integration.

#### Character-Campaign Integration

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| CC-INT-001 | Character assignment to campaign | - | - | - | - |
| CC-INT-002 | Campaign event processing | - | - | - | - |
| CC-INT-003 | Character evolution in campaign | - | - | - | - |
| CC-INT-004 | Resource tracking across services | - | - | - | - |

#### Image Service Integration

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| IMG-INT-001 | Character portrait linking | - | - | - | - |
| IMG-INT-002 | Campaign map integration | - | - | - | - |
| IMG-INT-003 | Asset version tracking | - | - | - | - |

#### Message Hub Integration

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| HUB-INT-001 | Cross-service event propagation | - | - | - | - |
| HUB-INT-002 | Service discovery integration | - | - | - | - |
| HUB-INT-003 | Health monitoring integration | - | - | - | - |

### L3: LLM-Dependent Integration Testing

Tests requiring actual LLM service interaction.

#### LLM Service Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| LLM-001 | Character backstory generation | - | - | - | - |
| LLM-002 | Campaign narrative generation | - | - | - | - |
| LLM-003 | NPC dialogue generation | - | - | - | - |
| LLM-004 | Theme-aware content adaptation | - | - | - | - |
| LLM-005 | Token usage tracking | - | - | - | - |

## Test Implementation Guidelines

### Individual Service Testing (L1)

1. **Test Independence**
   - Each service must be testable in isolation
   - Use mocks for external service dependencies
   - Maintain separate test databases per service

2. **Database Testing**
   ```python
   @pytest.fixture(scope="function")
   async def test_db(db_manager):
       async with db_manager.begin_nested() as session:
           yield session
   ```

3. **Mock External Services**
   ```python
   @pytest.fixture
   def mock_message_hub():
       with patch("service.external.message_hub.MessageHub") as mock:
           yield mock
   ```

### Service Integration Testing (L2)

1. **Message Hub Testing**
   - Test message routing between services
   - Validate event propagation
   - Check circuit breaker functionality

2. **Cross-Service Operations**
   ```python
   @pytest.mark.integration
   async def test_character_campaign_integration(
       character_service,
       campaign_service,
       message_hub
   ):
       # Test implementation
   ```

### LLM-Dependent Testing (L3)

1. **Token Management**
   - Track token usage in tests
   - Use test API keys
   - Implement rate limiting

2. **Content Generation**
   ```python
   @pytest.mark.llm
   async def test_character_backstory_generation(
       character_service,
       llm_service
   ):
       # Test implementation
   ```

## Test Execution Order

1. Run L1 tests during development:
   ```bash
   pytest tests/unit/ -v
   ```

2. Run L2 tests in CI/CD:
   ```bash
   pytest tests/integration/ -v
   ```

3. Run L3 tests in staging:
   ```bash
   pytest tests/llm/ -v
   ```

## Writing Test Cases

### Example Test Case Structure
```python
@pytest.mark.asyncio
async def test_character_creation():
    """
    Test ID: CHAR-001
    Description: Verify basic character creation
    """
    # Arrange
    character_data = {
        "name": "Test Character",
        "class": "Fighter",
        "level": 1
    }
    
    # Act
    result = await character_service.create_character(character_data)
    
    # Assert
    assert result.name == character_data["name"]
    assert result.class_ == character_data["class"]
    assert result.level == character_data["level"]
```

### Updating Test Results

When a test fails:
1. Document the failure in the appropriate table
2. Investigate and document the root cause
3. Implement and document the fix
4. Update the status in the table

Example update:
```markdown
| CHAR-001 | Basic CRUD operations | FIXED | Character creation failed | Missing UUID generation | Added UUID default in model |
```

## Test Coverage Requirements

- L1 Tests: Minimum 90% coverage
- L2 Tests: Minimum 85% coverage
- L3 Tests: Minimum 80% coverage

Track coverage using:
```bash
pytest --cov=src --cov-report=term-missing
```
