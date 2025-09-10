# Test Strategy

Version: 1.0
Status: Active
Last Updated: 2025-09-10

## Linked Documents
- Character Service Tests: `/services/character/SERVICE_TESTS.md`
- Campaign Service Tests: `/services/campaign/SERVICE_TESTS.md`
- Image Service Tests: `/services/image/SERVICE_TESTS.md`
- Message Hub Tests: `/services/message_hub/SERVICE_TESTS.md`

> Note: This document is automatically synchronized with service-level test documents.
> Updates to this file or any service-level test document will automatically update the related documents.

## Overview

This document serves as a high-level test strategy index for all services. Detailed test plans and requirements are maintained in service-specific SERVICE_TESTS.md files, with integration tests documented in the tests/INTEGRATION_TEST_PLAN.md. 

## Rule

Fix issues at their root cause.  Do not create work-arounds.  Treat these tests like this is going into the production phase next, so issues must be fixed properly.

## Test Process Guidelines

### Pre-Test Requirements

Before implementing or running tests, complete these steps:

1. Documentation Review:
   - Review service's SRD (System Requirements Document) for test requirements
   - Review service's ICD (Interface Control Document) for integration points
   - Check DOC_INDEX.md at: /dnd_char_creator/DOC_INDEX.md for all reference docs
   - Review service's SERVICE_TESTS.md for existing test specifications

2. Code Review:
   - Index the service's existing test files
   - Review test coverage reports
   - Identify gaps in test coverage
   - Check for test-specific TODO comments

3. Environment Setup:
   - Verify test database configuration
   - Check Message Hub availability for integration tests
   - Configure mock services as needed
   - Set required environment variables

### Post-Test Requirements

After completing ANY test run, perform these steps IN ORDER:

1. Documentation Updates:
   a. Update SERVICE_TESTS.md:
      - Add test completion timestamp
      - Document key test changes/additions
      - Note any testing patterns or gotchas worth preserving
      - Update coverage statistics
   
   b. Update test reports:
      ```bash
      # Generate coverage report
      pytest --cov=src --cov-report=html
      
      # Generate test results
      pytest --junitxml=test-results.xml
      ```
   
   c. If major test changes were made:
      - Update the service's README.md with new test requirements
      - Update WARP.md if test architecture changes affect the system

2. Test Data Cleanup:
   - Reset test databases to clean state
   - Clear test caches
   - Remove temporary test files
   - Reset mock services

3. Git Updates (REQUIRED):
   a. Stage changes:
      ```bash
      git add .
      ```
   
   b. Create detailed commit:
      ```bash
      git commit -m "[Service Name] Tests: Brief description of changes
      
      - Added tests for feature X
      - Improved coverage for component Y
      - Fixed flaky test Z
      - Updated test documentation
      - References task/issue number if applicable"
      ```
   
   c. Push to remote:
      ```bash
      git push origin main  # or appropriate branch
      ```

4. Test Environment Cleanup:
   - Stop test databases
   - Clear message queues
   - Reset environment variables
   - Clean coverage data

This document outlines our testing strategy and tracks test outcomes, root causes, and fixes. The testing approach follows a layered strategy:

1. Individual Service Testing (L1)
2. Service Integration Testing (L2) 
3. LLM-Dependent Integration Testing (L3)

## Test Categories

### L1: Individual Service Testing

Service-specific tests focusing on core functionality without external dependencies. Each service has its own SERVICE_TESTS.md document that details the specific test requirements for that service.

#### Character Service Tests

##### Completed Tests
- [x] Database Configuration and Setup
- [x] Repository Layer:
  - [x] Base Model Implementation
  - [x] Character Model Implementation
  - [x] Character Creation (CHAR-001-A)
  - [x] Character Retrieval (CHAR-001-B)
  - [x] Character Updates:
    - [x] Basic Field Updates
    - [x] Ability Score Updates
    - [x] Combat Stats Updates
  - [x] Character Listing:
    - [x] Basic List Operations
    - [x] Empty List Handling
    - [x] Soft Delete Filtering

##### Pending Tests
- [ ] Repository Layer:
- [x] Filter Characters
  - [x] Sort Characters
  - [x] Batch Operations
- [x] Service Layer Creation Tests
- [x] Service Layer Evolution Tests (HP, Level)
- [x] Service Layer Evolution Tests (Class Features)
- [x] Service Layer Evolution Tests (Multiclass)
- [x] Service Layer Validation Tests (Combat, Resources, State)
- [x] API Layer Tests (Create, Get, List, Update, Validation)
- [ ] Integration Tests

##### Test Progress Table
| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| CHAR-API-002 | API Endpoints | COMPLETE | Endpoint tests | Create, Get, List, Update, Validation | Implemented FastAPI app with DI, models, and error handling |
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

##### Completed Tests
- [x] Database Configuration and Setup
  - [x] PostgreSQL test database created and configured
  - [x] Alembic migrations with proper schema
  - [x] Base model with UUID, timestamps, soft delete
- [x] Repository Layer - Base Operations:
  - [x] Campaign Creation (CAMP-001-A)
  - [x] Campaign Update (CAMP-001-B)
  - [x] Campaign State Transitions (CAMP-001-C)
- [x] Soft Delete Implementation:
  - [x] Soft delete flags and timestamps
  - [x] Default query filtering
  - [x] Chapter preservation on parent delete
  - [x] Update blocking when deleted

##### In Progress
- [ ] Repository Layer - Advanced Operations:
  - [ ] Batch operations
  - [ ] Complex filtering
  - [ ] Pagination
- [ ] Theme System Implementation
- [ ] Chapter Management

##### Test Progress Table
| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| CAMP-001-A | Basic creation | ✅ | Initial DB setup | Alembic auto-detection | Fixed migration detection |
| CAMP-001-B | Campaign updates | ✅ | Transaction management | Nested transaction cleanup | Implemented proper savepoint handling |
| CAMP-001-C | Soft delete | ✅ | - | - | - |
| CAMP-002 | Theme system validation | - | - | - | - |
| CAMP-003 | Chapter organization | - | - | - | - |
| CAMP-004 | NPC management | - | - | - | - |
| CAMP-005 | World building features | - | - | - | - |

#### Image Service Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| IMG-001 | Basic image operations | ✅ | SQLAlchemy schema mismatch | Test DB not updated with new columns | Improved test DB creation with explicit drop/create and error handling |
| IMG-002 | Portrait generation mocks | ✅ | GetImg.AI API mocking issues | Async mock configuration | Added proper async mock patterns with realistic responses |
| IMG-003 | Map creation validation | ✅ | Map generation tests failing | Missing test fixtures and metadata | Added comprehensive map generation fixtures and metadata handling |
| IMG-004 | Asset management | ✅ | Storage persistence test failures | Improper version handling | Implemented proper version management in mock storage repository |
| IMG-005 | Style transfer validation | ✅ | Theme integration issues | Incomplete style guide data | Added complete theme and style guide test data |

#### Message Hub Tests

| Test ID | Description | Status | Issue/Failure | Root Cause | Fix |
|---------|-------------|--------|---------------|------------|-----|
| HUB-001 | Message routing | - | - | - | - |
| HUB-002 | Event management | - | - | - | - |
| HUB-003 | Service discovery | - | - | - | - |
| HUB-004 | Health monitoring | - | - | - | - |
| HUB-005 | Circuit breaker functionality | - | - | - | - |

### L2: Service Integration Testing

Tests focusing on service-to-service communication and integration. Detailed in INTEGRATION_TEST_PLAN.md, these tests verify proper event handling and state synchronization between services through the Message Hub.

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

2. **Database Test Configuration**
   - Each service uses TestSessionManager with proper error handling
   - Tables are explicitly dropped and recreated for each test run
   - Connection pools use pre-ping and proper isolation levels
   - Nested transactions ensure test isolation

Example test database configuration:
```python
async def init(self) -> None:
    try:
        self.engine = create_async_engine(
            self.database_url,
            echo=False,
            pool_size=5,
            pool_pre_ping=True,  # Verify connections
            isolation_level='READ COMMITTED'
        )
    except Exception as e:
        print(f"Error initializing test database: {e}")
        raise

async def setup_tables(self):
    try:
        async with self.engine.begin() as conn:
            # Drop all tables to ensure clean state
            await conn.run_sync(Base.metadata.drop_all)
            # Create all tables from current models
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Error creating test tables: {e}")
        raise
```

2. **Database Testing**

   Key principles:
   - Use nested transactions for isolation
   - Ensure clean state for each test
   - Handle schema changes properly
   - Robust error handling

   ```python
   # Database manager fixture
   @pytest.fixture
   async def db_manager() -> AsyncGenerator[TestSessionManager, None]:
       manager = TestSessionManager()
       await manager.init()

       # Ensure clean database state
       try:
           async with manager.engine.begin() as conn:
               await conn.run_sync(Base.metadata.drop_all)
               await conn.run_sync(Base.metadata.create_all)
       except Exception as e:
           print(f"Error setting up test database: {e}")
           raise

       yield manager
       await manager.cleanup()

   # Session fixture with transaction isolation
   @pytest.fixture
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

### L2: Service Integration Testing (L2)

Refer to /tests/INTEGRATION_TEST_PLAN.md for detailed integration test specifications. Key areas:

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
