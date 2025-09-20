# Storage Service Migration Guide

This document outlines the procedures for migrating from direct database access to the Storage Service.

## Overview

The Character Service is transitioning from direct database access to using the centralized Storage Service for all data persistence. This migration involves several key changes:

1. Moving from direct PostgreSQL access to Storage Service API
2. Converting database models to storage models
3. Implementing new repository patterns
4. Ensuring data consistency during migration
5. Validating storage service integration

## Migration Steps

### 1. Pre-Migration Tasks

- [ ] Backup all character service databases
- [ ] Create test data for validation
- [ ] Document current database state
- [ ] Verify storage service availability
- [ ] Test storage service connectivity

### 2. Storage Service Setup

- [ ] Provision character_db in storage service
- [ ] Configure access controls
- [ ] Set up monitoring
- [ ] Verify backup procedures
- [ ] Test failover mechanisms

### 3. Code Migration

#### Phase 1: Storage Client Implementation
- [ ] Implement StoragePort interface
- [ ] Create storage client with all required methods
- [ ] Add error handling and retries
- [ ] Implement caching layer
- [ ] Add logging and monitoring

#### Phase 2: Repository Updates
- [ ] Update repository classes to use storage client
- [ ] Convert database models to storage models
- [ ] Update dependency injection
- [ ] Add new repository tests
- [ ] Verify all operations

#### Phase 3: API Integration
- [ ] Update API endpoints to use new repositories
- [ ] Add storage service health checks
- [ ] Update API documentation
- [ ] Test all endpoints
- [ ] Validate error handling

### 4. Data Migration

```bash
# Export current data
poetry run python -m character_service.scripts.export_data

# Validate exported data
poetry run python -m character_service.scripts.validate_export

# Import to storage service
poetry run python -m character_service.scripts.import_to_storage

# Verify migration
poetry run python -m character_service.scripts.verify_migration
```

### 5. Validation Steps

1. **Data Integrity**
   ```bash
   # Compare source and destination
   poetry run python -m character_service.scripts.compare_data

   # Verify referential integrity
   poetry run python -m character_service.scripts.check_refs

   # Test all endpoints
   poetry run pytest tests/api/
   ```

2. **Performance Validation**
   ```bash
   # Run load tests
   poetry run locust -f tests/load/locustfile.py

   # Check latency metrics
   poetry run python -m character_service.scripts.check_latency
   ```

3. **Integration Testing**
   ```bash
   # End-to-end tests
   poetry run pytest tests/integration/

   # Campaign integration tests
   poetry run pytest tests/integration/test_campaigns.py
   ```

### 6. Rollback Procedures

If issues are detected during migration:

1. Stop the migration:
   ```bash
   poetry run python -m character_service.scripts.stop_migration
   ```

2. Restore original database:
   ```bash
   poetry run python -m character_service.scripts.restore_db
   ```

3. Clean up storage service:
   ```bash
   poetry run python -m character_service.scripts.cleanup_storage
   ```

## Deployment Strategy

### 1. Development Environment

```bash
# Deploy updated service
podman-compose up -d character_service

# Monitor logs
podman-compose logs -f character_service

# Check health
curl http://localhost:8000/health
```

### 2. Staging Environment

1. Deploy with feature flag:
   ```yaml
   # In deployment.yaml
   env:
     - name: USE_STORAGE_SERVICE
       value: "true"
   ```

2. Validate deployment:
   ```bash
   kubectl get pods -n staging
   kubectl logs -f -n staging character-service
   ```

3. Run validation suite:
   ```bash
   poetry run pytest tests/staging/
   ```

### 3. Production Environment

1. Progressive rollout:
   ```yaml
   # In deployment.yaml
   spec:
     strategy:
       rollingUpdate:
         maxSurge: 1
         maxUnavailable: 0
   ```

2. Monitor metrics:
   ```bash
   # Check error rates
   curl http://metrics:9090/api/v1/query?query=character_service_errors_total

   # Check latency
   curl http://metrics:9090/api/v1/query?query=character_service_request_duration_seconds
   ```

3. Validate production:
   ```bash
   # Health checks
   curl https://api.dndcreator.com/character/health

   # Smoke tests
   poetry run pytest tests/smoke/
   ```

## Monitoring and Alerts

### 1. Key Metrics

- Request latency
- Error rates
- Cache hit/miss rates
- Storage service health
- Data consistency

### 2. Alert Rules

```yaml
# In prometheus/rules.yaml
groups:
  - name: character-service
    rules:
      - alert: HighErrorRate
        expr: rate(character_service_errors_total[5m]) > 0.01
        for: 5m
        labels:
          severity: critical
      - alert: HighLatency
        expr: avg_over_time(character_service_request_duration_seconds[5m]) > 0.5
        for: 5m
        labels:
          severity: warning
```

### 3. Dashboards

Available in Grafana:
- Character Service Overview
- Storage Integration Metrics
- Migration Progress
- Data Consistency

## Troubleshooting

### Common Issues

1. **Connection Failures**
   ```python
   # Check storage service health
   await storage_client.health_check()

   # Verify network connectivity
   curl http://storage-service:8000/health
   ```

2. **Data Inconsistency**
   ```python
   # Run consistency check
   await storage_client.verify_data_consistency()

   # Check specific record
   await storage_client.validate_record(record_id)
   ```

3. **Performance Issues**
   ```python
   # Check cache status
   await cache_client.stats()

   # Monitor request latency
   await metrics_client.get_latency_stats()
   ```

### Recovery Steps

1. **Connection Recovery**
   ```python
   # Reset connection pool
   await storage_client.reset_connections()

   # Clear caches
   await cache_client.clear()
   ```

2. **Data Recovery**
   ```python
   # Sync specific record
   await storage_client.sync_record(record_id)

   # Full sync
   await storage_client.sync_all()
   ```

3. **Performance Recovery**
   ```python
   # Clear caches
   await cache_client.flush()

   # Reset circuit breakers
   await circuit_breaker.reset()
   ```

## Support and Documentation

### Contact Information

- **DevOps Team**: devops@dndcreator.com
- **Storage Service Team**: storage@dndcreator.com
- **On-Call Support**: +1-555-0123

### Related Documentation

- [Storage Service API](docs/api/storage-service.md)
- [Message Hub Integration](docs/message-hub.md)
- [Monitoring Guide](docs/monitoring.md)
- [Incident Response](docs/incidents.md)