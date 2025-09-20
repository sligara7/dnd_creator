# Image Service Test Plan

<!-- This document is linked to /TEST_STRATEGY.md. Updates to either document will trigger updates to the other. -->
<test-doc-link>strategy:v1.0</test-doc-link>

## Latest Updates (2025-09-10)

### Completed Tests
✅ Map Generation
- Basic tactical map generation with grid system
- Terrain feature rendering and validation
- Character position and status overlays
- Spell effect visualization
- Campaign map generation with regions
- Party tracking and position management
- Political borders and features

### In Progress
⏳ Map quality metrics validation
⏳ Style consistency checks
⏳ Edge case coverage expansion

### Completed Today (2025-09-10)
✅ Fixed database test infrastructure
- Improved test database configuration with pre-ping
- Added proper error handling in database operations
- Implemented explicit table drop/create for clean state
- Fixed schema versioning issues

✅ Character Visualization Tests
- Portrait generation with metadata
- NPC and monster visualization
- Equipment rendering
- Theme-aware styling
- Batch generation support

✅ Storage Layer Tests
- Version management
- Upload/download operations
- Metadata handling
- Error cases

### Pending
❌ Performance optimization testing
❌ Load testing under high concurrency
❌ Integration tests with Campaign service

Version: 1.0
Status: Active
Last Updated: 2025-09-10

<!-- This document is linked to /TEST_STRATEGY.md. Updates to either document will trigger updates to the other. -->
<test-doc-link>strategy:v1.0</test-doc-link>

## Progress Report

### Completed Tests
✅ Test Environment and Infrastructure
- Database configuration with proper transaction isolation
- Enhanced error handling and logging
- Clean state management with table recreation
- Proper schema versioning support

✅ Map Generation Tests
- Tactical maps with grid system
- Campaign maps with regions
- Character positioning
- Terrain features
- Spell effect visualization

✅ Character Visualization Tests
- Portrait generation with metadata
- NPC and monster visualization
- Equipment rendering in portraits
- Theme-aware styling
- Batch generation support

✅ Storage System Tests
- Complete repository interface
- Upload/download operations
- Version management and tracking
- Error handling and edge cases

✅ GetImg.AI Integration Tests
- API authentication and rate limiting
- Mock response handling
- Error scenarios
- Response validation

### In Progress
⏳ Performance Optimization Tests
- Response time benchmarking
- Memory usage monitoring
- Cache effectiveness measurement

⏳ Load Testing Framework
- Concurrent request handling
- Resource utilization tracking
- Rate limit compliance

### Integration Tests in Planning
❌ Campaign Service Integration
❌ Character Service Integration

## Test Categories

This document outlines the service-level test requirements for the Image Service, based on the SRD requirements. Tests are organized into functional categories aligned with the service's core responsibilities.

### 1. Map Generation Tests

#### 1.1 Tactical Map Tests
```python
@pytest.mark.asyncio
class TestTacticalMapGeneration:
    async def test_grid_system_generation(self):
        """Test tactical grid generation and accuracy"""
        
    async def test_character_position_overlay(self):
        """Verify character position overlay functionality"""
        
    async def test_spell_range_overlay(self):
        """Test spell and ability range overlay system"""
        
    async def test_terrain_feature_generation(self):
        """Verify tactical terrain generation"""
        
    async def test_theme_integration(self):
        """Test theme-aware visual generation"""
```

#### 1.2 Campaign Map Tests
```python
@pytest.mark.asyncio
class TestCampaignMapGeneration:
    async def test_party_position_tracking(self):
        """Test party position visualization"""
        
    async def test_point_of_interest_marking(self):
        """Verify POI marking system"""
        
    async def test_region_scale_visualization(self):
        """Test region-scale map generation"""
        
    async def test_geographic_features(self):
        """Verify geographic feature rendering"""
```

### 2. Character Visualization Tests

```python
@pytest.mark.asyncio
class TestCharacterVisualization:
    async def test_portrait_generation(self):
        """Test character portrait generation"""
        
    async def test_npc_visualization(self):
        """Verify NPC portrait creation"""
        
    async def test_monster_image_generation(self):
        """Test monster visualization"""
        
    async def test_equipment_visualization(self):
        """Verify equipment rendering in portraits"""
        
    async def test_theme_style_application(self):
        """Test theme-based visual styling"""
```

### 3. Item Illustration Tests

```python
@pytest.mark.asyncio
class TestItemIllustration:
    async def test_weapon_visualization(self):
        """Test weapon illustration generation"""
        
    async def test_armor_rendering(self):
        """Verify armor visualization"""
        
    async def test_magical_item_effects(self):
        """Test magical effect visualization"""
        
    async def test_material_representation(self):
        """Verify material and quality visualization"""
```

### 4. Overlay System Tests

```python
@pytest.mark.asyncio
class TestOverlaySystem:
    async def test_tactical_overlay_positioning(self):
        """Test tactical position overlay accuracy"""
        
    async def test_spell_effect_visualization(self):
        """Verify spell effect overlay rendering"""
        
    async def test_movement_range_display(self):
        """Test movement and range overlays"""
        
    async def test_campaign_level_overlays(self):
        """Verify campaign-scale overlay system"""
```

### 5. Theme Integration Tests

```python
@pytest.mark.asyncio
class TestThemeIntegration:
    async def test_ui_theme_generation(self):
        """Test UI theme framework generation"""
        
    async def test_component_system_styling(self):
        """Verify component style application"""
        
    async def test_visual_theme_application(self):
        """Test theme application across assets"""
        
    async def test_style_guide_generation(self):
        """Verify style guide creation"""
```

### 6. GetImg.AI Integration Tests

```python
@pytest.mark.asyncio
class TestGetImgIntegration:
    async def test_api_authentication(self):
        """Test API authentication flow"""
        
    async def test_rate_limit_handling(self):
        """Verify rate limit management"""
        
    async def test_error_handling(self):
        """Test error handling and recovery"""
        
    async def test_response_processing(self):
        """Verify response processing and storage"""
```

## Test Implementation Guidelines

### Test Organization
- Group tests by image generation type
- Use clear, descriptive test names
- Include error cases and edge conditions
- Test both success and failure paths

### Test Coverage Requirements
1. Map Generation: 95% coverage
2. Character Visualization: 95% coverage
3. Item Illustration: 90% coverage
4. Overlay System: 100% coverage
5. Theme Integration: 90% coverage
6. API Integration: 100% coverage

### Test Data
```python
@pytest.fixture
def test_map_request():
    return {
        "type": "tactical",
        "grid_size": {"width": 20, "height": 20},
        "theme": "fantasy",
        "features": ["forest", "river", "cliff"],
        "overlay_data": {
            "characters": [
                {"id": "uuid", "position": {"x": 5, "y": 5}}
            ],
            "spell_effects": [
                {
                    "type": "circle",
                    "radius": 20,
                    "center": {"x": 10, "y": 10}
                }
            ]
        }
    }

@pytest.fixture
def test_portrait_request():
    return {
        "type": "character",
        "character_data": {
            "race": "Human",
            "class": "Fighter",
            "equipment": ["plate armor", "longsword"],
            "theme": "fantasy"
        }
    }
```

### Mocking
```python
@pytest.fixture
def mock_getimg_api():
    with patch("image_service.external.getimg.GetImgAPI") as mock:
        mock.generate_image.return_value = {
            "url": "https://example.com/test.png",
            "metadata": {}
        }
        yield mock

@pytest.fixture
def mock_message_hub():
    with patch("image_service.external.message_hub.MessageHub") as mock:
        yield mock

@pytest.fixture
def mock_storage_service():
    with patch("image_service.external.storage.StorageService") as mock:
        yield mock
```

## Test Execution

### Running Tests
```bash
# Run all image service tests
poetry run pytest tests/ -v

# Run specific test categories
poetry run pytest tests/unit/test_map_generation.py -v
poetry run pytest tests/unit/test_character_visualization.py -v
poetry run pytest tests/integration/test_getimg_api.py -v

# Run with coverage
poetry run pytest --cov=src --cov-report=term-missing
```

### Pre-Test Requirements
1. Test environment configuration
2. Mock GetImg.AI API setup
3. Test storage configuration
4. Mock Message Hub setup
5. Test data preparation
6. Theme templates loaded

### Post-Test Cleanup
1. Remove generated test images
2. Clear API mock data
3. Reset storage state
4. Clear message queue
5. Clean test metadata
6. Reset theme cache
