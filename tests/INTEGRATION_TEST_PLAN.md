# Integration Test Plan

Version: 1.0
Status: Active
Last Updated: 2025-09-09

## Overview

This document outlines the integration test strategy for service-to-service communication in the D&D Character Creator system. All service interactions must comply with their respective Interface Control Documents (ICDs) and be coordinated through the Message Hub.

## Core Integration Points

### 1. Character-Campaign Integration

#### 1.1 Integration Tests
- Character assignment to campaign (character.assigned_to_campaign)
- Campaign theme changes (campaign.theme_changed)
- Character evolution in campaign (character.evolved)
- Resource tracking synchronization (character.resources_updated)

#### 1.2 Test Requirements
- Validate event schemas against ICDs
- Verify bidirectional state synchronization
- Test error handling and retries
- Verify data consistency across services

### 2. Character-Image Integration

#### 2.1 Integration Tests
- Portrait generation requests
- Equipment visualization updates
- Theme-based visual changes
- Image version management

#### 2.2 Test Requirements
- Test image request/response flow
- Verify theme consistency
- Test caching mechanisms
- Validate error handling

### 3. Campaign-Image Integration

#### 3.1 Integration Tests
- Map generation coordination
- Location visualization updates
- Theme propagation to visuals
- Asset version control

#### 3.2 Test Requirements
- Test map request/response cycle
- Verify visual theme consistency
- Test asset versioning
- Validate error cases

### 4. Character-LLM Integration

#### 4.1 Integration Tests
- Character backstory generation
- Character evolution suggestions
- Content refinement requests
- Theme-based content adaptation

#### 4.2 Test Requirements
- Test content generation flow
- Verify theme integration
- Test content validation
- Validate rate limiting

### 5. Campaign-LLM Integration

#### 5.1 Integration Tests
- Campaign narrative generation
- NPC dialogue generation
- Plot adaptation requests
- Theme-aware content generation

#### 5.2 Test Requirements
- Test narrative generation
- Verify plot consistency
- Test NPC integration
- Validate content rules

### 6. Edge Service Integration

#### 6.1 Gateway-Auth Integration Tests
- Authentication flow verification
- Authorization checks
- Token validation
- Rate limit enforcement

#### 6.2 Gateway-Metrics Integration Tests
- Request tracking
- Response timing
- Error rate monitoring
- Resource usage tracking

#### 6.3 Auth-Metrics Integration Tests
- Auth event logging
- Security metrics
- Rate limit tracking
- Token usage metrics

## Integration Test Strategies

### 1. Message Hub Testing

#### 1.1 Event Publication Tests
```python
@pytest.mark.asyncio
async def test_event_publication():
    """Test event publication through Message Hub"""
    # Test implementation
```

#### 1.2 Event Subscription Tests
```python
@pytest.mark.asyncio
async def test_event_subscription():
    """Test event subscription and handling"""
    # Test implementation
```

#### 1.3 Circuit Breaker Tests
```python
@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker functionality"""
    # Test implementation
```

### 2. State Synchronization Testing

#### 2.1 Cross-Service State Tests
```python
@pytest.mark.asyncio
async def test_state_synchronization():
    """Test state synchronization between services"""
    # Test implementation
```

#### 2.2 Consistency Tests
```python
@pytest.mark.asyncio
async def test_data_consistency():
    """Test data consistency across services"""
    # Test implementation
```

### 3. Error Handling Testing

#### 3.1 Retry Logic Tests
```python
@pytest.mark.asyncio
async def test_retry_handling():
    """Test retry logic for failed operations"""
    # Test implementation
```

#### 3.2 Error Recovery Tests
```python
@pytest.mark.asyncio
async def test_error_recovery():
    """Test error recovery procedures"""
    # Test implementation
```

## Test Data Requirements

### 1. Character-Campaign Test Data
- Sample characters with full attributes
- Campaign templates with themes
- Evolution scenarios
- Resource update cases

### 2. Image Generation Test Data
- Portrait generation requests
- Map generation requests
- Theme style guides
- Visual asset templates

### 3. LLM Test Data
- Content generation prompts
- Refinement scenarios
- Theme adaptation cases
- Validation rules

## Test Environment Setup

### 1. Service Dependencies
```python
@pytest.fixture(scope="session")
async def setup_test_services():
    """Configure all required services for integration tests"""
    # Implementation
```

### 2. Message Hub Configuration
```python
@pytest.fixture(scope="session")
async def setup_message_hub():
    """Configure Message Hub for testing"""
    # Implementation
```

### 3. Database Setup
```python
@pytest.fixture(scope="function")
async def setup_test_databases():
    """Configure test databases for all services"""
    # Implementation
```

## Test Execution Guidelines

### 1. Test Categories
- L1: Individual service tests
- L2: Service integration tests
- L3: LLM-dependent tests

### 2. Test Order
1. Start with L1 tests during development
2. Run L2 tests in CI/CD
3. Run L3 tests in staging

### 3. Test Commands
```bash
# Run L1 tests
poetry run pytest tests/unit/ -v

# Run L2 tests
poetry run pytest tests/integration/ -v

# Run L3 tests
poetry run pytest tests/llm/ -v
```

## Coverage Requirements

### 1. Service Coverage
- Edge Services: 90%
- Core Services: 95%
- Support Services: 85%

### 2. Integration Coverage
- Message Hub Integration: 100%
- Event Handling: 95%
- Error Handling: 90%

## Test Reports

### 1. Coverage Reports
```bash
pytest --cov=src --cov-report=html
```

### 2. Test Results
```bash
pytest --junitxml=test-results.xml
```

## Integration Test Checklist

### Pre-Test Requirements
1. All services running in test mode
2. Test databases configured
3. Message Hub available
4. Mock external services ready
5. Test data prepared
6. Environment variables set

### During Test Execution
1. Monitor service logs
2. Track event flow
3. Verify state consistency
4. Check error handling
5. Validate responses
6. Record test results

### Post-Test Actions
1. Clean test data
2. Reset service state
3. Clear message queues
4. Export test reports
5. Update test documentation
6. Review coverage reports

## Service Dependencies

### Character Service
- Message Hub (event communication)
- Campaign Service (theme, state)
- Image Service (visualization)
- LLM Service (content)

### Campaign Service
- Message Hub (event communication)
- Character Service (participants)
- Image Service (maps)
- LLM Service (narrative)

### Image Service
- Message Hub (event communication)
- GetImg.AI API
- Storage Service
- Cache Service

### LLM Service
- Message Hub (event communication)
- Cache Service
- Storage Service
- Search Service

## Update Procedures

### 1. Test Plan Updates
- Review monthly
- Update after major changes
- Version control test plans
- Document changes

### 2. Coverage Goals
- Review quarterly
- Adjust as needed
- Track trends
- Report changes

### 3. Test Suite Maintenance
- Clean obsolete tests
- Update dependencies
- Optimize performance
- Enhance documentation
