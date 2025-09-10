# Integration Tests

This directory contains service-to-service integration tests based on the Interface Control Documents (ICDs). The test structure follows the architecture layers and validates service interactions through the Message Hub.

## Directory Structure

```
tests/
├── conftest.py                # Shared test fixtures and configuration
├── edge/                      # Edge layer integration tests
│   ├── gateway_auth/         # API Gateway <-> Auth Service integration
│   ├── gateway_metrics/      # API Gateway <-> Metrics Service integration
│   └── auth_metrics/         # Auth Service <-> Metrics Service integration
├── communication/            # Communication layer integration tests
│   ├── message_hub/         # Message Hub integration with all services
│   ├── cache_service/       # Cache Service integration tests
│   └── storage_service/     # Storage Service integration tests
├── core/                    # Core services integration tests
│   ├── character_campaign/  # Character <-> Campaign Service integration
│   ├── character_image/     # Character <-> Image Service integration
│   ├── character_llm/       # Character <-> LLM Service integration
│   ├── campaign_image/      # Campaign <-> Image Service integration
│   ├── campaign_llm/        # Campaign <-> LLM Service integration
│   └── catalog/            # Catalog Service integration tests
└── support/                # Support services integration tests
    ├── search/            # Search Service integration tests
    └── audit/            # Audit Service integration tests

## Test Categories

### L2: Service Integration Tests
Tests that verify service-to-service communication and integration without LLM dependencies.

Run with:
```bash
pytest tests/edge tests/communication tests/core tests/support -v
```

### L3: LLM-Dependent Integration Tests
Tests requiring actual LLM service interaction.

Run with:
```bash
pytest tests/core/character_llm tests/core/campaign_llm -v
```

## Writing Integration Tests

1. Tests should validate against ICDs
2. Use test fixtures from conftest.py
3. Mock external dependencies
4. Follow AAA (Arrange, Act, Assert) pattern
5. Include error cases and edge conditions

Example:
```python
@pytest.mark.integration
async def test_character_campaign_integration(
    character_service,
    campaign_service,
    message_hub
):
    # Arrange
    character_data = {...}
    campaign_data = {...}
    
    # Act
    character = await character_service.create_character(character_data)
    campaign = await campaign_service.create_campaign(campaign_data)
    result = await campaign_service.add_character(campaign.id, character.id)
    
    # Assert
    assert result.status == "success"
    assert len(result.characters) == 1
```

## Test Coverage Requirements

- Edge Layer Tests: 85% coverage
- Communication Layer Tests: 85% coverage
- Core Services Tests: 85% coverage
- Support Services Tests: 85% coverage

Track coverage using:
```bash
pytest --cov=src --cov-report=term-missing
```
