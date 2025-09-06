# Character Service Operational Guide

## Overview

The Character Service is a core component of the D&D Character Creator system, responsible for character creation, validation, and management. This guide covers deployment, configuration, monitoring, and maintenance of the service.

## Table of Contents
1. [Deployment](#deployment)
2. [Configuration](#configuration)
3. [Scaling](#scaling)
4. [Monitoring](#monitoring)
5. [Troubleshooting](#troubleshooting)
6. [Maintenance](#maintenance)

## Deployment

### Prerequisites
- Python 3.11+
- Poetry 1.5+
- PostgreSQL 15+
- Redis 7+ (for caching)
- Docker/Podman

### Container Deployment

```bash
# Build container
podman build -t dnd-character-service .

# Run with required environment variables
podman run -d \
  --name dnd-character-service \
  -p 8000:8000 \
  -e POSTGRES_DSN="postgresql://user:pass@host:5432/db" \
  -e REDIS_DSN="redis://host:6379/0" \
  -e MESSAGE_HUB_URL="http://message-hub:8200" \
  -e SECRET_KEY="${SECRET_KEY}" \
  dnd-character-service
```

### Docker Compose Setup

```yaml
version: '3.8'
services:
  character-service:
    build: .
    ports:
      - "8000:8000"
    environment:
      - POSTGRES_DSN=postgresql://user:pass@postgres:5432/character_db
      - REDIS_DSN=redis://redis:6379/0
      - MESSAGE_HUB_URL=http://message-hub:8200
      - SECRET_KEY=${SECRET_KEY}
    depends_on:
      - postgres
      - redis
      - message-hub
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
```

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| POSTGRES_DSN | PostgreSQL connection string | - | Yes |
| REDIS_DSN | Redis connection string | - | Yes |
| MESSAGE_HUB_URL | Message Hub service URL | - | Yes |
| SECRET_KEY | Service encryption key | - | Yes |
| LOG_LEVEL | Logging level | INFO | No |
| MAX_WORKERS | Max parallel validation workers | 4 | No |
| CACHE_TTL | Cache entry TTL in seconds | 3600 | No |
| VALIDATION_TIMEOUT | Validation timeout in seconds | 30 | No |

### Feature Flags

Located in `config/features.yaml`:

```yaml
features:
  # Enable incremental validation
  incremental_validation: true
  
  # Enable validation result caching
  validation_caching: true
  
  # Enable parallel rule execution
  parallel_validation: true
  
  # Enable custom content validation
  custom_content: true
```

## Scaling

### Horizontal Scaling

The service is stateless and can be scaled horizontally. Use container orchestration like Kubernetes for automated scaling.

```bash
# Scale to 3 replicas
kubectl scale deployment character-service --replicas=3
```

### Resource Requirements

Minimum per instance:
- CPU: 1 core
- Memory: 512MB
- Disk: 1GB

Recommended per instance:
- CPU: 2 cores
- Memory: 1GB
- Disk: 2GB

### Performance Tuning

1. Database Connection Pool:
```python
pool_size = min(32, cpu_count * 4)
max_overflow = min(64, cpu_count * 8)
```

2. Redis Cache Settings:
```python
max_connections = min(100, cpu_count * 10)
socket_timeout = 2  # seconds
```

3. Validation Engine:
```python
max_parallel_rules = min(8, cpu_count)
cache_ttl = 3600  # 1 hour
```

## Monitoring

### Health Checks

Endpoint: `/health`
```json
{
  "status": "healthy",
  "version": "2.0.0",
  "checks": {
    "database": "ok",
    "redis": "ok",
    "message_hub": "ok"
  }
}
```

### Metrics

Prometheus metrics at `/metrics`:
- Request latency histograms
- Validation success/failure rates
- Cache hit/miss ratios
- Rule execution times
- Database connection pool stats
- Memory usage

Example Grafana dashboard config provided in `monitoring/dashboards/character-service.json`.

### Logging

Structured JSON logs with standard fields:
```json
{
  "timestamp": "2025-09-06T13:00:00Z",
  "level": "INFO",
  "event": "character_validation",
  "character_id": "uuid",
  "duration_ms": 150,
  "validation_rules": 12,
  "issues_found": 2
}
```

Log levels:
- ERROR: Service errors requiring attention
- WARN: Potential issues or degraded service
- INFO: Normal operations
- DEBUG: Detailed debugging information

### Alerts

Prometheus alerting rules in `monitoring/alerts/character-service.yaml`:
```yaml
groups:
  - name: character-service
    rules:
      - alert: HighErrorRate
        expr: rate(character_validation_errors[5m]) > 0.1
        labels:
          severity: warning
        annotations:
          description: "High validation error rate detected"
```

## Troubleshooting

### Common Issues

1. High Validation Times
   - Check validation rule execution times in metrics
   - Verify cache hit rates
   - Check database connection pool usage
   - Monitor parallel execution stats

2. Database Connection Issues
   - Verify connection pool settings
   - Check max_connections in PostgreSQL
   - Monitor connection timeout errors
   - Check network latency

3. Cache Performance
   - Monitor Redis memory usage
   - Check cache eviction rates
   - Verify connection pool settings
   - Monitor cache hit ratios

### Debug Mode

Enable debug logging:
```bash
export LOG_LEVEL=DEBUG
```

Debug endpoints (dev/staging only):
- `/debug/cache/stats`: Cache statistics
- `/debug/validation/timing`: Rule execution times
- `/debug/connections`: Connection pool status

## Maintenance

### Database Migrations

Using Alembic for schema migrations:
```bash
# Create migration
poetry run alembic revision --autogenerate -m "description"

# Apply migrations
poetry run alembic upgrade head

# Rollback if needed
poetry run alembic downgrade -1
```

### Cache Management

Redis cache commands:
```bash
# Clear validation cache
redis-cli -n 0 KEYS "validation:*" | xargs redis-cli -n 0 DEL

# Monitor cache size
redis-cli -n 0 INFO | grep used_memory_human

# Check cache hits/misses
redis-cli -n 0 INFO stats | grep keyspace
```

### Backup and Recovery

1. Database Backups:
```bash
# Full backup
pg_dump -Fc character_db > backup.dump

# Restore from backup
pg_restore -d character_db backup.dump
```

2. Configuration Backups:
```bash
# Backup configs
tar -czf configs.tar.gz config/

# Restore configs
tar -xzf configs.tar.gz
```

### Version Updates

1. Prepare Update:
   - Review changelog
   - Backup database
   - Backup configurations
   - Schedule maintenance window

2. Deploy Update:
```bash
# Pull new version
podman pull dnd-character-service:new

# Rolling update
kubectl set image deployment/character-service \
  character-service=dnd-character-service:new
```

3. Verify Update:
   - Check health endpoints
   - Monitor error rates
   - Verify metrics
   - Test core functionality
