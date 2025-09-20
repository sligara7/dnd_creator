# Cache Service Configuration Guide

## Overview
This guide covers all configuration options for the Cache Service, including environment variables, Redis configuration, Message Hub settings, and various operational parameters.

## Environment Variables

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379` | `redis://cache-redis:6379` |
| `MESSAGE_HUB_URL` | Message Hub connection string | `amqp://localhost:5672` | `amqp://rabbitmq:5672` |
| `SERVICE_AUTH_KEY` | Authentication key for service | None | `your-auth-key` |

### Redis Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `REDIS_POOL_SIZE` | Connection pool size | `10` | `50` |
| `REDIS_MAX_RETRIES` | Max retry attempts | `3` | `5` |
| `REDIS_RETRY_INTERVAL` | Retry interval (seconds) | `1` | `2` |
| `REDIS_TIMEOUT` | Operation timeout (seconds) | `5` | `10` |
| `REDIS_SSL_ENABLED` | Enable SSL for Redis | `false` | `true` |
| `REDIS_PASSWORD` | Redis password | None | `your-password` |
| `REDIS_DB` | Redis database number | `0` | `1` |

### Message Hub Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `MESSAGE_HUB_POOL_SIZE` | Connection pool size | `5` | `10` |
| `MESSAGE_HUB_HEARTBEAT` | Heartbeat interval (seconds) | `30` | `60` |
| `MESSAGE_HUB_QUEUE_NAME` | Service queue name | `cache-service` | `cache-service-prod` |
| `MESSAGE_HUB_EXCHANGE` | Message exchange name | `cache-events` | `cache-events-prod` |
| `MESSAGE_HUB_SSL_ENABLED` | Enable SSL for Message Hub | `false` | `true` |
| `MESSAGE_HUB_USER` | Message Hub username | None | `your-username` |
| `MESSAGE_HUB_PASSWORD` | Message Hub password | None | `your-password` |

### Cache Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CACHE_TTL_DEFAULT` | Default TTL (seconds) | `3600` | `7200` |
| `CACHE_TTL_MAX` | Maximum TTL (seconds) | `86400` | `172800` |
| `CACHE_KEY_MAX_LENGTH` | Maximum key length | `256` | `512` |
| `CACHE_VALUE_MAX_SIZE` | Maximum value size (bytes) | `1048576` | `5242880` |
| `CACHE_COMPRESSION_ENABLED` | Enable value compression | `true` | `false` |
| `CACHE_COMPRESSION_MIN_SIZE` | Min size for compression (bytes) | `1024` | `2048` |
| `CACHE_NAMESPACING_ENABLED` | Enable service namespacing | `true` | `false` |

### Circuit Breaker Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `CIRCUIT_BREAKER_THRESHOLD` | Failure threshold | `5` | `10` |
| `CIRCUIT_BREAKER_TIMEOUT` | Reset timeout (seconds) | `60` | `120` |
| `CIRCUIT_BREAKER_HALF_OPEN` | Half-open timeout (seconds) | `30` | `60` |

### Rate Limiting

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` | `false` |
| `RATE_LIMIT_REQUESTS` | Requests per window | `1000` | `2000` |
| `RATE_LIMIT_WINDOW` | Time window (seconds) | `60` | `120` |
| `RATE_LIMIT_PATTERN_REQUESTS` | Pattern operation requests | `10` | `20` |
| `RATE_LIMIT_PATTERN_WINDOW` | Pattern operation window | `60` | `120` |

### Metrics and Monitoring

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `METRICS_ENABLED` | Enable Prometheus metrics | `true` | `false` |
| `METRICS_PORT` | Metrics port | `8001` | `9090` |
| `METRICS_PATH` | Metrics endpoint path | `/metrics` | `/stats` |
| `METRICS_LABELS` | Additional metric labels | None | `env=prod,region=us-east` |

### Logging Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `LOG_FORMAT` | Log format (json/text) | `json` | `text` |
| `LOG_FILE` | Log file path | None | `/var/log/cache.log` |
| `LOG_MAX_SIZE` | Max log file size (MB) | `100` | `500` |
| `LOG_BACKUP_COUNT` | Number of backup files | `5` | `10` |

### Service Configuration

| Variable | Description | Default | Example |
|----------|-------------|---------|---------|
| `SERVICE_NAME` | Service name | `cache-service` | `cache-service-prod` |
| `SERVICE_PORT` | Service port | `8000` | `8080` |
| `SERVICE_HOST` | Service host | `0.0.0.0` | `localhost` |
| `SERVICE_VERSION` | Service version | `1.0.0` | `1.1.0` |

## Configuration Files

### Service Configuration (config.yaml)

```yaml
service:
  name: cache-service
  version: 1.0.0
  port: 8000
  host: 0.0.0.0

redis:
  url: redis://cache-redis:6379
  pool_size: 50
  max_retries: 3
  retry_interval: 1
  timeout: 5
  ssl_enabled: false
  db: 0

message_hub:
  url: amqp://rabbitmq:5672
  pool_size: 5
  heartbeat: 30
  queue_name: cache-service
  exchange: cache-events
  ssl_enabled: false

cache:
  ttl:
    default: 3600
    max: 86400
  key:
    max_length: 256
  value:
    max_size: 1048576
  compression:
    enabled: true
    min_size: 1024
  namespacing:
    enabled: true

circuit_breaker:
  threshold: 5
  timeout: 60
  half_open: 30

rate_limit:
  enabled: true
  standard:
    requests: 1000
    window: 60
  pattern:
    requests: 10
    window: 60

metrics:
  enabled: true
  port: 8001
  path: /metrics
  labels:
    env: prod
    region: us-east

logging:
  level: INFO
  format: json
  file:
    path: /var/log/cache.log
    max_size: 100
    backup_count: 5
```

### Environment-Specific Configurations

#### Development (dev-config.yaml)

```yaml
redis:
  url: redis://localhost:6379
  pool_size: 10
  max_retries: 3

message_hub:
  url: amqp://localhost:5672
  pool_size: 2

logging:
  level: DEBUG
  format: text
```

#### Production (prod-config.yaml)

```yaml
redis:
  url: redis://cache-redis:6379
  pool_size: 50
  max_retries: 5
  ssl_enabled: true

message_hub:
  url: amqp://rabbitmq:5672
  pool_size: 10
  ssl_enabled: true

cache:
  ttl:
    default: 7200
    max: 172800
  value:
    max_size: 5242880

circuit_breaker:
  threshold: 10
  timeout: 120

rate_limit:
  standard:
    requests: 2000
    window: 60

logging:
  level: INFO
  format: json
  file:
    enabled: true
```

## Configuration Examples

### Basic Development Setup

```bash
# Essential configuration
export REDIS_URL=redis://localhost:6379
export MESSAGE_HUB_URL=amqp://localhost:5672
export SERVICE_AUTH_KEY=dev-key

# Development settings
export LOG_LEVEL=DEBUG
export METRICS_ENABLED=false
export RATE_LIMIT_ENABLED=false
```

### Production Setup

```bash
# Core configuration
export REDIS_URL=redis://cache-redis:6379
export MESSAGE_HUB_URL=amqp://rabbitmq:5672
export SERVICE_AUTH_KEY=prod-key-xxxx

# Redis pool settings
export REDIS_POOL_SIZE=50
export REDIS_MAX_RETRIES=5
export REDIS_SSL_ENABLED=true

# Message Hub settings
export MESSAGE_HUB_POOL_SIZE=10
export MESSAGE_HUB_SSL_ENABLED=true

# Cache settings
export CACHE_TTL_DEFAULT=7200
export CACHE_TTL_MAX=172800
export CACHE_COMPRESSION_ENABLED=true

# Circuit breaker
export CIRCUIT_BREAKER_THRESHOLD=10
export CIRCUIT_BREAKER_TIMEOUT=120

# Rate limiting
export RATE_LIMIT_REQUESTS=2000
export RATE_LIMIT_WINDOW=60

# Metrics
export METRICS_ENABLED=true
export METRICS_LABELS="env=prod,region=us-east"

# Logging
export LOG_LEVEL=INFO
export LOG_FORMAT=json
export LOG_FILE=/var/log/cache.log
```

### High-Performance Setup

```bash
# Redis configuration
export REDIS_POOL_SIZE=100
export REDIS_MAX_RETRIES=3
export REDIS_TIMEOUT=3

# Cache settings
export CACHE_TTL_DEFAULT=3600
export CACHE_COMPRESSION_MIN_SIZE=4096
export CACHE_VALUE_MAX_SIZE=10485760

# Rate limits
export RATE_LIMIT_REQUESTS=5000
export RATE_LIMIT_WINDOW=60
export RATE_LIMIT_PATTERN_REQUESTS=20
```

### Minimal Setup

```bash
# Minimal required configuration
export REDIS_URL=redis://localhost:6379
export MESSAGE_HUB_URL=amqp://localhost:5672
export SERVICE_AUTH_KEY=minimal-key

# Basic settings
export SERVICE_PORT=8000
export LOG_LEVEL=INFO
```

## Common Configurations

### Local Development

```yaml
redis:
  url: redis://localhost:6379
  pool_size: 5
  max_retries: 3

message_hub:
  url: amqp://localhost:5672
  pool_size: 2

logging:
  level: DEBUG
  format: text

metrics:
  enabled: false

rate_limit:
  enabled: false
```

### Testing Environment

```yaml
redis:
  url: redis://test-redis:6379
  pool_size: 10
  max_retries: 3

message_hub:
  url: amqp://test-rabbitmq:5672
  pool_size: 3

logging:
  level: DEBUG
  format: json

metrics:
  enabled: true
  labels:
    env: test
```

### Production Environment

```yaml
redis:
  url: redis://prod-redis:6379
  pool_size: 50
  max_retries: 5
  ssl_enabled: true

message_hub:
  url: amqp://prod-rabbitmq:5672
  pool_size: 10
  ssl_enabled: true

logging:
  level: INFO
  format: json
  file:
    enabled: true
    path: /var/log/cache.log

metrics:
  enabled: true
  labels:
    env: prod
```

## Best Practices

### Redis Configuration

1. **Connection Pool Size**
   - Development: 5-10 connections
   - Production: 20-50 connections
   - High load: 50-100 connections

2. **Timeouts**
   - Connection timeout: 5 seconds
   - Operation timeout: 1-3 seconds
   - Keep-alive: 30 seconds

3. **SSL/Security**
   - Enable SSL in production
   - Use strong passwords
   - Configure ACLs

### Message Hub Configuration

1. **Connection Management**
   - Enable heartbeats
   - Configure reconnection strategy
   - Use separate channels for different event types

2. **Queue Settings**
   - Set appropriate prefetch counts
   - Configure dead letter exchanges
   - Enable persistent messages

3. **Security**
   - Enable SSL in production
   - Use virtual hosts
   - Configure access controls

### Cache Settings

1. **TTL Strategy**
   - Short TTL (< 1 hour) for frequently changing data
   - Medium TTL (1-24 hours) for stable data
   - Long TTL (> 24 hours) for static data

2. **Key Design**
   - Use consistent naming conventions
   - Include version in keys if needed
   - Keep keys short but meaningful

3. **Value Management**
   - Enable compression for large values
   - Set appropriate size limits
   - Monitor memory usage

### Circuit Breaker Configuration

1. **Failure Thresholds**
   - Development: 3-5 failures
   - Production: 5-10 failures
   - Critical systems: 2-3 failures

2. **Timeouts**
   - Reset: 30-120 seconds
   - Half-open: 15-60 seconds

3. **Monitoring**
   - Track state changes
   - Monitor failure rates
   - Alert on extended open states

### Rate Limiting

1. **Request Limits**
   - Standard operations: 1000-5000/minute
   - Pattern operations: 10-50/minute
   - Batch operations: 100-500/minute

2. **Window Sizes**
   - Standard: 60 seconds
   - Pattern: 300 seconds
   - Batch: 60 seconds

### Metrics Configuration

1. **Collection**
   - Enable in all environments
   - Set appropriate scrape intervals
   - Configure retention periods

2. **Labeling**
   - Include environment
   - Add service version
   - Include region/zone

### Logging Configuration

1. **Log Levels**
   - Development: DEBUG
   - Testing: DEBUG/INFO
   - Production: INFO

2. **Format**
   - Development: text
   - Production: JSON
   - Include correlation IDs

## Troubleshooting

### Common Issues

1. **Connection Problems**
```yaml
redis:
  max_retries: 5
  retry_interval: 2
  timeout: 10

message_hub:
  heartbeat: 30
  reconnect_delay: 5
```

2. **Memory Issues**
```yaml
cache:
  value:
    max_size: 1048576
  compression:
    enabled: true
    min_size: 2048
```

3. **Performance Problems**
```yaml
redis:
  pool_size: 50
  timeout: 3

rate_limit:
  enabled: true
  requests: 2000
  window: 60
```