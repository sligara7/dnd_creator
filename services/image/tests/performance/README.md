# Image Service Performance Tests

This directory contains the performance testing framework for the Image Service, ensuring that the service meets the performance requirements specified in the SRD.

## Performance Requirements

As specified in the Service Requirements Document (SRD), the Image Service must meet the following performance targets:

### Image Generation
- Portrait Generation: < 15 seconds (P95)
- Tactical Map Generation: < 30 seconds (P95)
- Item Illustration Generation: < 10 seconds (P95)

### API Performance
- Health Check Endpoint: < 100ms (P95)
- Cache Hit Rate: > 90%
- API Success Rate: > 95%

### Concurrent Operation Performance
- Portrait Generation: < 20 seconds (P95)
- Tactical Map Generation: < 35 seconds (P95)
- Item Generation: < 15 seconds (P95)

## Test Framework Components

1. **Core Performance Tests** (`test_performance.py`)
   - Generation pipeline benchmarks
   - API endpoint performance tests
   - Cache performance verification
   - Concurrent operation testing

2. **Load Testing** (`locustfile.py`)
   - Simulated user behavior
   - Realistic request patterns
   - Concurrent user load testing

3. **Performance Check Script** (`check_srd_requirements.py`)
   - Validates test results against SRD requirements
   - Generates comprehensive performance reports
   - Tracks performance trends

4. **Test Runner** (`run_performance_tests.sh`)
   - Executes all performance tests
   - Collects and aggregates results
   - Generates summary reports

## Running the Tests

### Prerequisites
```bash
# Install required dependencies
poetry install

# Ensure the service is running
poetry run uvicorn src.main:app --reload
```

### Execute Tests
```bash
# Run all performance tests
./run_performance_tests.sh

# Run specific test categories
poetry run pytest tests/performance/test_performance.py -v -k "test_generation"
poetry run pytest tests/performance/test_performance.py -v -k "test_api"
poetry run pytest tests/performance/test_performance.py -v -k "test_cache"

# Run load tests
poetry run locust -f tests/performance/locustfile.py --headless
```

### View Results
- Performance logs are stored in `./performance_logs/`
- Each test run creates a timestamped JSON results file
- Summary report is generated at the end of each run

## Test Categories

### 1. Generation Pipeline Tests
- Portrait generation performance
- Tactical map generation performance
- Item illustration generation performance
- Tests both individual and batch operations

### 2. API Performance Tests
- Endpoint response times
- Request success rates
- Error rates and types
- Header validation

### 3. Cache Performance Tests
- Cache hit rates
- Cache operation latency
- Cache effectiveness under load
- Cache consistency checks

### 4. Load Tests
- Concurrent user simulation
- Mixed operation patterns
- Resource utilization
- System stability under load

## Performance Metrics

The test framework collects and analyzes:
- Response times (min, max, mean, p95)
- Error rates and types
- Cache hit rates
- Resource utilization
- Concurrent operation performance
- API endpoint latency

## Troubleshooting

If tests fail:
1. Check service logs for errors
2. Verify service configuration
3. Ensure sufficient system resources
4. Check for rate limiting issues
5. Validate cache configuration

## Contributing

When adding new tests:
1. Follow existing patterns in `test_performance.py`
2. Add appropriate fixtures in `conftest.py`
3. Update SRD requirements checker
4. Document new test cases in this README

## Performance Regression Prevention

- All performance tests run in CI/CD pipeline
- Results are tracked and compared against baseline
- Alerts on performance regression
- Trend analysis for optimization opportunities