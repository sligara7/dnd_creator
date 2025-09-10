# Campaign Service Test Plan (SERVICE_TESTS.md)

Version: 1.1
Status: Active
Last Updated: 2025-09-10

> **Note**: This document is linked with /dnd_char_creator/TEST_STRATEGY.md. Updates to either document should be synchronized to maintain consistency.

## Test Categories

This document outlines the service-level test requirements for the Campaign Service, based on the SRD requirements. Tests are organized into functional categories aligned with the service's core responsibilities.

### 1. Campaign Generation Tests

#### 1.1 Core Campaign Generation
```python
@pytest.mark.asyncio
class TestCampaignGeneration:
    async def test_campaign_concept_to_skeleton(self):
        """Test basic campaign creation from concept"""
        
    async def test_multi_layer_plot_generation(self):
        """Verify complex plot generation with multiple layers"""
        
    async def test_moral_scenario_generation(self):
        """Test creation of morally complex scenarios"""
        
    async def test_multi_genre_support(self):
        """Verify campaign generation across different genres"""
        
    async def test_campaign_refinement(self):
        """Test iterative campaign refinement process"""
```

#### 1.2 Campaign Structure Tests
```python
@pytest.mark.asyncio
class TestCampaignStructure:
    async def test_branching_narrative(self):
        """Verify branching narrative structure"""
        
    async def test_story_path_tracking(self):
        """Test tracking of story paths and decisions"""
        
    async def test_campaign_outline_generation(self):
        """Validate high-level campaign outline creation"""
        
    async def test_session_support_scaling(self):
        """Test campaign scaling from 3-20 sessions"""
```

### 2. Version Control Tests

```python
@pytest.mark.asyncio
class TestVersionControl:
    async def test_chapter_versioning(self):
        """Test Git-like chapter versioning"""
        
    async def test_branch_management(self):
        """Verify branch creation and management"""
        
    async def test_version_history_tracking(self):
        """Test version history maintenance"""
        
    async def test_merge_handling(self):
        """Verify merge conflict resolution"""
        
    async def test_session_state_management(self):
        """Test session state tracking"""
```

### 3. Theme System Tests

```python
@pytest.mark.asyncio
class TestThemeSystem:
    async def test_core_theme_implementation(self):
        """Test core theme implementation"""
        
    async def test_setting_theme_implementation(self):
        """Verify setting theme implementation"""
        
    async def test_theme_transitions(self):
        """Test theme transition handling"""
        
    async def test_multi_theme_blending(self):
        """Verify multiple theme integration"""
        
    async def test_theme_consistency(self):
        """Test theme consistency across campaign elements"""
```

### 4. Chapter System Tests

```python
@pytest.mark.asyncio
class TestChapterSystem:
    async def test_chapter_organization(self):
        """Test chapter structure and organization"""
        
    async def test_objective_management(self):
        """Verify chapter objectives and conflicts"""
        
    async def test_chapter_dependencies(self):
        """Test chapter dependency management"""
        
    async def test_location_integration(self):
        """Verify location description and map integration"""
        
    async def test_encounter_generation(self):
        """Test encounter and reward generation"""
```

### 5. Content Generation Tests

```python
@pytest.mark.asyncio
class TestContentGeneration:
    async def test_npc_generation(self):
        """Test NPC creation and management"""
        
    async def test_monster_generation(self):
        """Verify monster generation and balancing"""
        
    async def test_location_generation(self):
        """Test location and map generation"""
        
    async def test_equipment_generation(self):
        """Verify equipment and reward generation"""
```

### 6. Integration Tests

```python
@pytest.mark.asyncio
class TestMessageHubIntegration:
    async def test_character_service_events(self):
        """Test Character Service event handling"""
        
    async def test_llm_service_events(self):
        """Verify LLM Service integration"""
        
    async def test_image_service_events(self):
        """Test Image Service integration"""
        
    async def test_message_delivery_guarantees(self):
        """Verify message delivery and retry handling"""
```

## Test Implementation Guidelines

### Test Organization
- Group tests by functional area
- Use descriptive test names
- Include positive and negative test cases
- Test edge cases and error conditions

### Repository Layer Testing
- ✅ Entity creation and validation
- ✅ Basic CRUD operations
- ✅ Soft delete behavior:
  - Flag and timestamp setting
  - Default query filtering
  - Update blocking when deleted
  - Chapter preservation on parent delete
- ✅ Advanced operations:
  - Completed: Batch operations
  - Completed: Pagination with filtering
  - Completed: Complex filtering (state, type, owner, date range)
  - Completed: Sorting

### Test Coverage Requirements

| Component              | Target | Current | Status | Notes |
|-----------------------|--------|---------|--------|-------|--------|
| Campaign Generation    | 95%    | 45%     | 🚧 | Basic CRUD, soft delete, and policy enforcement complete |
| Repository Layer       | 100%   | 80%     | 🚧 | Base repo and soft delete constraints implemented |
| Database Layer         | 100%   | 100%    | ✅ | Schema, migrations, and constraints complete |
| Version Control        | 100%   | 15%     | 🚧 | Base models and core tests implemented |
| Theme System          | 90%    | 0%      | ⏳ |
| Chapter System        | 95%    | 0%      | ⏳ |
| Content Generation    | 90%    | 0%      | ⏳ |
| Message Hub Integration| 100%   | 0%      | ⏳ |

### Test Data
```python
@pytest.fixture
def test_campaign_data():
    return {
        "name": "Test Campaign",
        "concept": "A heroic fantasy adventure",
        "theme": {
            "primary": "High Fantasy",
            "secondary": "Political Intrigue"
        },
        "target_sessions": 5,
        "target_level_range": {
            "start": 1,
            "end": 5
        }
    }

@pytest.fixture
def test_chapter_data():
    return {
        "title": "The Beginning",
        "summary": "Players discover a hidden threat",
        "objectives": [
            "Investigate the mysterious disappearances",
            "Find the hidden cultist lair"
        ],
        "encounters": [],
        "npcs": [],
        "locations": []
    }
```

### Mocking
```python
@pytest.fixture
def mock_message_hub():
    with patch("campaign_service.external.message_hub.MessageHub") as mock:
        yield mock

@pytest.fixture
def mock_llm_service():
    with patch("campaign_service.external.llm.LLMService") as mock:
        yield mock

@pytest.fixture
def mock_image_service():
    with patch("campaign_service.external.image.ImageService") as mock:
        yield mock
```

## Test Execution

### Running Tests
```bash
# Run all campaign service tests
poetry run pytest tests/ -v

# Run specific test categories
poetry run pytest tests/unit/test_campaign_generation.py -v
poetry run pytest tests/unit/test_version_control.py -v
poetry run pytest tests/integration/test_message_hub.py -v

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

### Pre-Test Requirements

✅ = Completed | 🚧 = In Progress | ⏳ = Pending

✅ 1. Test database setup and migrations
   - PostgreSQL test database created
   - Alembic migrations setup
   - Base model with proper fields (UUID, timestamps, soft delete)
   - Schema validated and working

🚧 2. Mock Message Hub configuration
   - Basic mock structure created
   - Event handling pending

⏳ 3. Mock LLM service configuration

⏳ 4. Mock Image service configuration

✅ 5. Test environment variables
   - Database connection working
   - Test fixtures operational

⏳ 6. Seed test data

### Post-Test Cleanup

Last cleanup: 2025-09-10 02:42 UTC

> Note: All repository layer tests passing, including advanced operations (batch, pagination, filtering).
> Added PaginationResult model for standardized pagination support.
> Version control models (Branch, Commit, Change) implemented with core tests passing.

1. Test Database:
   - [x] Cleaned test data (via transaction rollback)
   - [x] Schema intact and verified
   - [x] Migrations in sync

2. Mock Services:
   - [x] Message Hub mocks reset
   - [ ] LLM service mocks (not used yet)
   - [ ] Image service mocks (not used yet)

3. Cache and Files:
   - [x] No cached test data
   - [x] No temporary files created
   - [x] Coverage data preserved in reports/

4. Environment:
   - [x] Test variables reset
   - [x] Database connections closed
   - [x] No lingering transactions
