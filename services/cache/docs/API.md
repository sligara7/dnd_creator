# Cache Service API Documentation

## Overview
The Cache Service provides a distributed caching layer with Redis backend and local memory caching. It supports key-value operations, pattern matching, and service-based isolation.

## Base URL
```
http://localhost:8000/api/v1
```

## Authentication
All requests must include the service authentication header:
```
X-Service-Auth: <service-auth-key>
```

## Common Headers
| Header | Description |
|--------|-------------|
| `X-Service-Auth` | Service authentication key |
| `X-Request-ID` | Optional request ID for tracing |
| `X-Service-Name` | Service namespace for key isolation |

## Error Responses
All error responses follow this format:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Human readable error message",
        "details": {
            "additional": "error specific details"
        }
    }
}
```

Common error codes:
- `INVALID_AUTH`: Invalid or missing authentication
- `INVALID_REQUEST`: Malformed request
- `KEY_ERROR`: Key-related error (not found, invalid format)
- `CACHE_ERROR`: Redis or cache operation error
- `TIMEOUT`: Operation timeout
- `CIRCUIT_OPEN`: Circuit breaker is open

## Endpoints

### GET /health
Health check endpoint.

**Response**
```json
{
    "status": "healthy",
    "version": "1.0.0",
    "redis_connected": true,
    "message_hub_connected": true
}
```

### GET /metrics
Prometheus metrics endpoint.

**Response**
Prometheus formatted metrics including:
- Cache hit/miss rates
- Operation latencies
- Memory usage
- Circuit breaker status

### GET /cache/{key}
Get a cached value by key.

**Parameters**
- `key` (path): Cache key

**Response**
```json
{
    "key": "service:key",
    "value": "cached value",
    "ttl": 3600
}
```

### PUT /cache/{key}
Set a cache value.

**Parameters**
- `key` (path): Cache key
- `ttl` (query, optional): Time to live in seconds

**Request Body**
```json
{
    "value": "any json value"
}
```

**Response**
```json
{
    "key": "service:key",
    "ttl": 3600
}
```

### DELETE /cache/{key}
Delete a cached value.

**Parameters**
- `key` (path): Cache key

**Response**
```json
{
    "key": "service:key",
    "deleted": true
}
```

### GET /cache/pattern/{pattern}
Get all keys matching a pattern.

**Parameters**
- `pattern` (path): Redis glob pattern
- `limit` (query, optional): Maximum number of keys to return
- `cursor` (query, optional): Scan cursor for pagination

**Response**
```json
{
    "pattern": "service:*",
    "cursor": "0",
    "keys": [
        {
            "key": "service:key1",
            "value": "value1",
            "ttl": 3600
        },
        {
            "key": "service:key2",
            "value": "value2",
            "ttl": 7200
        }
    ]
}
```

### DELETE /cache/pattern/{pattern}
Delete all keys matching a pattern.

**Parameters**
- `pattern` (path): Redis glob pattern

**Response**
```json
{
    "pattern": "service:*",
    "deleted_count": 10
}
```

### POST /cache/batch
Batch set operation.

**Request Body**
```json
{
    "items": [
        {
            "key": "key1",
            "value": "value1",
            "ttl": 3600
        },
        {
            "key": "key2",
            "value": "value2",
            "ttl": 7200
        }
    ]
}
```

**Response**
```json
{
    "success_count": 2,
    "failed_keys": []
}
```

### GET /cache/batch
Batch get operation.

**Request Body**
```json
{
    "keys": ["key1", "key2", "key3"]
}
```

**Response**
```json
{
    "items": {
        "key1": {
            "value": "value1",
            "ttl": 3600
        },
        "key2": {
            "value": "value2",
            "ttl": 7200
        }
    },
    "missing_keys": ["key3"]
}
```

### POST /cache/increment/{key}
Increment a counter.

**Parameters**
- `key` (path): Counter key
- `amount` (query, optional): Amount to increment by (default: 1)

**Response**
```json
{
    "key": "counter:key",
    "value": 42
}
```

### POST /cache/decrement/{key}
Decrement a counter.

**Parameters**
- `key` (path): Counter key
- `amount` (query, optional): Amount to decrement by (default: 1)

**Response**
```json
{
    "key": "counter:key",
    "value": 41
}
```

### POST /cache/clear
Clear all keys in a service namespace.

**Response**
```json
{
    "cleared_count": 100
}
```

### GET /cache/stats
Get cache statistics.

**Response**
```json
{
    "hits": 1000,
    "misses": 100,
    "hit_rate": 0.91,
    "memory_used": 1048576,
    "keys_count": 500,
    "operations_per_second": 1000
}
```

## Message Hub Events

The cache service publishes and handles the following events:

### Published Events
- `cache.set`: When a key is set
- `cache.delete`: When a key is deleted
- `cache.clear`: When a namespace is cleared
- `cache.invalidated`: When a pattern is invalidated
- `service.health_status`: Periodic health status updates

### Handled Events
- `cache.invalidate`: Request to invalidate keys
- `cache.clear`: Request to clear namespace
- `cache.preload`: Request to preload cache data
- `cache.status_request`: Request for cache status

## Rate Limits
- Standard operations: 1000/second per service
- Pattern operations: 10/second per service
- Batch operations: 100 items per request
- Health checks: 10/second
- Metrics: 10/second

## Circuit Breaker
The service uses circuit breakers for both Redis and Message Hub connections:
- Failure threshold: 5 errors
- Reset timeout: 60 seconds
- Half-open timeout: 30 seconds
- Operation timeout: 5 seconds

## Performance Considerations
1. **Key Design**
   - Use colon-separated namespaced keys
   - Keep keys short but meaningful
   - Example: `service:entity:id`

2. **Value Size**
   - Optimal value size: < 100KB
   - Maximum value size: 512MB
   - Large values are automatically compressed

3. **Pattern Matching**
   - Use specific patterns to minimize scan range
   - Avoid leading wildcards
   - Consider pagination for large result sets

4. **Batch Operations**
   - Use batch operations for multiple keys
   - Maximum 100 items per batch
   - Consider key locality for better performance

## Examples

### Basic Operations
```python
# Set a value
curl -X PUT http://localhost:8000/api/v1/cache/user:123 \
    -H "X-Service-Auth: service-key" \
    -H "Content-Type: application/json" \
    -d '{"value": {"name": "test"}}'

# Get a value
curl http://localhost:8000/api/v1/cache/user:123 \
    -H "X-Service-Auth: service-key"

# Delete a value
curl -X DELETE http://localhost:8000/api/v1/cache/user:123 \
    -H "X-Service-Auth: service-key"
```

### Pattern Operations
```python
# Get all user keys
curl http://localhost:8000/api/v1/cache/pattern/user:* \
    -H "X-Service-Auth: service-key"

# Delete all user keys
curl -X DELETE http://localhost:8000/api/v1/cache/pattern/user:* \
    -H "X-Service-Auth: service-key"
```

### Batch Operations
```python
# Batch set
curl -X POST http://localhost:8000/api/v1/cache/batch \
    -H "X-Service-Auth: service-key" \
    -H "Content-Type: application/json" \
    -d '{
        "items": [
            {"key": "user:1", "value": {"name": "user1"}},
            {"key": "user:2", "value": {"name": "user2"}}
        ]
    }'

# Batch get
curl -X GET http://localhost:8000/api/v1/cache/batch \
    -H "X-Service-Auth: service-key" \
    -H "Content-Type: application/json" \
    -d '{"keys": ["user:1", "user:2"]}'
```