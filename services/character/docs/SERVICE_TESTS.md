# Character Service Test Plan (SERVICE_TESTS.md)

Version: 1.0
Status: Active
Last Updated: 2025-09-10

## Linked Documents
- Main Test Strategy: `/TEST_STRATEGY.md`

> Note: This document is automatically synchronized with the main test strategy document.
> Updates to either document will automatically update the other.

## Test Progress Summary

### Completed Tests (✓)

#### Infrastructure & Models (100% Complete)
- [x] Test database configuration and session management
- [x] Base model with UUID, timestamps, and soft delete
- [x] Character model with all D&D 5e fields
- [x] Proper timezone handling (UTC)
- [x] Transaction isolation in tests

#### Repository Layer (100% Complete)
1. Character Creation
   - [x] Basic character creation
   - [x] Field validation
   - [x] Default values
   - [x] Timestamp handling

2. Character Retrieval
   - [x] Get by ID
   - [x] Handle non-existent characters
   - [x] Handle soft-deleted characters

3. Character Updates
   - [x] Basic field updates
   - [x] Ability score updates
   - [x] Combat stats updates
   - [x] Verify unchanged fields

4. Character Listing
   - [x] List all characters
   - [x] Empty list handling
   - [x] Soft delete filtering

### Pending Tests

#### Repository Layer (30% Remaining)
- [x] Filter characters (by level, class, race, multi-criteria)
- [x] Sort characters (by name, level, multi-field order)
- [x] Batch operations (create, update, delete)

#### Service Layer (85% Complete)
- [x] Character creation business logic
- [x] Level up mechanics (HP scaling)
- [x] Level cap enforcement
- [x] Constitution change HP recalculation
- [x] Class feature acquisition by level (Fighter, Wizard)
- [x] Feature resource reset on rests (short/long)
- [x] Multiclass system implementation
- [x] Ability score prerequisites for multiclassing
- [x] Multiple class feature acquisition
- [x] Combat stats validation
- [x] Resource usage validation
- [x] Character state validation
- [x] Error handling with clear messages
- [ ] Character validation rules
- [ ] Character evolution tracking
- [ ] Resource management
- [ ] Journal system integration

#### API Layer (0% Complete)
- [ ] Route configuration
- [ ] Input validation
- [ ] Response formatting
- [ ] Error handling
- [ ] Authentication/Authorization

#### Integration Layer (0% Complete)
- [ ] Campaign service integration
- [ ] Image service integration
- [ ] Message hub integration
- [ ] Event processing

### Implementation Progress

### Latest Updates (2025-09-10)
- Implemented multiclass system and tests:
  - Multiple class tracking with JSON field
  - Ability score prerequisites (STR 13 for Fighter, INT 13 for Wizard)
  - Level 1 feature acquisition for new classes
  - Validation against duplicate classes
- Service layer progress: 85%

### Completed Setup (2025-09-10)
- [x] Test infrastructure setup with TestSessionManager
- [x] Database session management with transaction isolation
- [x] Custom UTCDateTime type for timezone handling
- [x] Base model with proper UUID and timestamp fields
- [x] First repository test (character creation) passed

### Key Technical Achievements
- Implemented proper timezone handling using custom SQLAlchemy type
- Set up test database with proper transaction isolation
- Created base model with UUID and soft delete support
- Established pattern for async test execution

### Current Test Coverage
- Models: 100% (base model and character model)
- Repositories: 70% (creation + retrieval + update + list operations)
- Services: 0%
- API: 0%

## Next Steps
1. Implement remaining repository tests
2. Set up service layer tests
3. Add API endpoint tests
4. Configure integration tests

## Test Categories

This document outlines the service-level test requirements for the Character Service, based on the SRD requirements. Tests are organized into functional categories aligned with the service's core responsibilities.

### 1. Character Sheet Management Tests

#### 1.1 Independent Variables Tests
```python
@pytest.mark.asyncio
class TestCharacterIndependentVariables:
    async def test_core_information_updates(self):
        """Verify core character information updates correctly"""
        
    async def test_ability_score_limits(self):
        """Validate ability score ranges and limitations"""
        
    async def test_health_resource_management(self):
        """Test HP, temp HP, hit dice, and death save tracking"""
        
    async def test_proficiency_management(self):
        """Verify language and tool proficiency management"""
        
    async def test_equipment_updates(self):
        """Test equipment and inventory management"""
        
    async def test_character_details(self):
        """Validate character physical and personality trait updates"""
        
    async def test_spellcasting_management(self):
        """Test spell preparation and slot management"""
```

#### 1.2 Derived Variables Tests
```python
@pytest.mark.asyncio
class TestCharacterDerivedVariables:
    async def test_ability_modifier_calculation(self):
        """Verify ability modifier calculations"""
        
    async def test_combat_statistics(self):
        """Test AC, initiative, and speed calculations"""
        
    async def test_saving_throw_bonuses(self):
        """Validate saving throw calculations with proficiencies"""
        
    async def test_skill_modifier_calculation(self):
        """Test skill modifier calculations with proficiencies"""
        
    async def test_passive_score_calculation(self):
        """Verify passive perception, investigation, insight"""
        
    async def test_spellcasting_bonuses(self):
        """Test spell save DC and attack bonus calculations"""
```

### 2. Theme Management Tests

#### 2.1 Theme Branching Tests
```python
@pytest.mark.asyncio
class TestThemeBranching:
    async def test_character_theme_branching(self):
        """Test character version creation on theme change"""
        
    async def test_equipment_theme_reset(self):
        """Verify equipment resets to root version on theme change"""
        
    async def test_version_relationship_tracking(self):
        """Test parent-child relationship maintenance"""
        
    async def test_multiple_theme_transitions(self):
        """Validate multiple theme transitions and version history"""
```

#### 2.2 Content Strategy Tests
```python
@pytest.mark.asyncio
class TestContentStrategy:
    async def test_content_reuse_priority(self):
        """Verify existing content is prioritized over generation"""
        
    async def test_content_type_branching(self):
        """Test different branching behavior for content types"""
        
    async def test_custom_content_generation(self):
        """Validate custom content generation workflow"""
```

### 3. Journal System Tests

```python
@pytest.mark.asyncio
class TestJournalSystem:
    async def test_session_tracking(self):
        """Test session creation and management"""
        
    async def test_experience_logging(self):
        """Verify XP tracking and milestone management"""
        
    async def test_development_suggestions(self):
        """Test character development suggestion generation"""
        
    async def test_journal_crud_operations(self):
        """Validate journal entry CRUD operations"""
```

### 4. Character Evolution Tests

```python
@pytest.mark.asyncio
class TestCharacterEvolution:
    async def test_level_up_process(self):
        """Test character level-up workflow"""
        
    async def test_feature_acquisition(self):
        """Verify feature and ability acquisition"""
        
    async def test_multiclass_management(self):
        """Test multiclass handling and requirements"""
```

### 5. API Endpoint Tests

```python
@pytest.mark.asyncio
class TestCharacterAPI:
    async def test_character_creation_endpoint(self):
        """Test /api/v2/factory/create endpoint"""
        
    async def test_character_refinement_endpoint(self):
        """Test /api/v2/characters/{id}/refine endpoint"""
        
    async def test_inventory_management_endpoints(self):
        """Test inventory-related endpoints"""
        
    async def test_spell_management_endpoints(self):
        """Test spell management endpoints"""
        
    async def test_journal_endpoints(self):
        """Test journal CRUD endpoints"""
```

### 6. Event Tests

```python
@pytest.mark.asyncio
class TestEventHandling:
    async def test_published_events(self):
        """Test event publication to Message Hub"""
        
    async def test_subscribed_event_handling(self):
        """Verify handling of subscribed events"""
```

## Test Implementation Guidelines

### Test Organization
- Tests should be organized by feature area
- Each test class should focus on a specific functionality
- Test names should clearly indicate what is being tested
- Use appropriate test markers (unit, integration, e2e)

### Test Dependencies
- Use test fixtures for common setup
- Mock external service dependencies
- Use test databases with transactions
- Clean up test data after each test

### Test Coverage Requirements
1. All Independent Variables: 100% coverage
2. All Derived Variables: 100% coverage
3. State Management: 95% coverage
4. API Endpoints: 90% coverage
5. Event Handling: 90% coverage

### Test Data
```python
@pytest.fixture
def test_character_data():
    return {
        "name": "Test Character",
        "species": "Human",
        "class": "Fighter",
        "level": 1,
        "ability_scores": {
            "strength": 15,
            "dexterity": 14,
            "constitution": 13,
            "intelligence": 12,
            "wisdom": 10,
            "charisma": 8
        }
    }
```

### Database Fixtures
```python
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
async def db_manager():
    """Create a test database session manager."""
    manager = TestSessionManager(TEST_DATABASE_URL)
    await manager.init()
    
    # Create all tables
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    yield manager
    
    # Drop all tables after tests
    async with manager.engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    await manager.close()

@pytest.fixture
async def db_session(db_manager) -> AsyncSession:
    """Create a new database session for a test."""
    async with db_manager as session:
        yield session
```

### Event Mocking
```python
@pytest.fixture
def mock_message_hub():
    with patch("character_service.external.message_hub.MessageHub") as mock:
        yield mock
```

## Test Execution

### Running Tests
```bash
# Run all character service tests
poetry run pytest tests/ -v

# Run specific test categories
poetry run pytest tests/unit/test_character_sheet.py -v
poetry run pytest tests/unit/test_theme_management.py -v
poetry run pytest tests/integration/test_events.py -v

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

### Pre-Test Requirements
1. Test database setup with migrations
2. Mock Message Hub configured
3. Test environment variables set
4. Required test data seeded

### Post-Test Cleanup
1. Test database cleanup
2. Remove temporary test files
3. Reset mocked services
4. Clear any test cache
