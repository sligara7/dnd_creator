# Cache Service Deployment Guide

## Overview
This guide covers deploying the Cache Service in production environments. The service requires Redis for distributed caching and RabbitMQ for Message Hub communication.

## Prerequisites
- Docker 20.10+
- Docker Compose 2.0+
- Kubernetes 1.24+ (for container orchestration)
- Helm 3.0+ (for Kubernetes deployments)

## System Requirements

### Minimum Requirements
- CPU: 2 cores
- Memory: 4GB RAM
- Disk: 20GB SSD
- Network: 1Gbps

### Recommended Requirements
- CPU: 4+ cores
- Memory: 8GB+ RAM
- Disk: 50GB+ SSD
- Network: 10Gbps

## Architecture

### Components
```
┌─────────────────┐     ┌─────────────────┐
│   API Gateway   │────>│  Cache Service  │
└─────────────────┘     └───────┬─────────┘
                              │
              ┌───────────────┼───────────────┐
              │               │               │
        ┌─────▼─────┐   ┌────▼────┐   ┌─────▼─────┐
        │   Redis    │   │ RabbitMQ │   │  Metrics  │
        │  Cluster   │   │          │   │ (Prom/Graf│
        └───────────┘   └──────────┘   └───────────┘
```

## Deployment Options

### Docker Compose (Development/Testing)
```yaml
# docker-compose.yml
version: '3.8'

services:
  cache:
    image: dnd-cache-service:latest
    environment:
      - REDIS_URL=redis://redis:6379
      - MESSAGE_HUB_URL=amqp://rabbitmq:5672
      - SERVICE_AUTH_KEY=your-auth-key
    ports:
      - "8000:8000"
    depends_on:
      - redis
      - rabbitmq

  redis:
    image: redis:7.0-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis-data:/data

  rabbitmq:
    image: rabbitmq:3.11-management-alpine
    volumes:
      - rabbitmq-data:/var/lib/rabbitmq

volumes:
  redis-data:
  rabbitmq-data:
```

### Kubernetes (Production)

1. **Cache Service Deployment**
```yaml
# cache-deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cache-service
spec:
  replicas: 3
  selector:
    matchLabels:
      app: cache-service
  template:
    metadata:
      labels:
        app: cache-service
    spec:
      containers:
      - name: cache-service
        image: dnd-cache-service:latest
        resources:
          requests:
            cpu: "500m"
            memory: "512Mi"
          limits:
            cpu: "2"
            memory: "2Gi"
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: cache-secrets
              key: redis-url
        - name: MESSAGE_HUB_URL
          valueFrom:
            secretKeyRef:
              name: cache-secrets
              key: message-hub-url
        - name: SERVICE_AUTH_KEY
          valueFrom:
            secretKeyRef:
              name: cache-secrets
              key: service-auth-key
        ports:
        - containerPort: 8000
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

2. **Service Configuration**
```yaml
# cache-service.yaml
apiVersion: v1
kind: Service
metadata:
  name: cache-service
spec:
  selector:
    app: cache-service
  ports:
  - port: 8000
    targetPort: 8000
  type: ClusterIP
```

3. **Redis Configuration (Using Redis Operator)**
```yaml
# redis-cluster.yaml
apiVersion: redis.redis.opstreelabs.in/v1beta1
kind: RedisCluster
metadata:
  name: cache-redis
spec:
  clusterSize: 3
  persistenceEnabled: true
  resources:
    requests:
      cpu: "500m"
      memory: "1Gi"
    limits:
      cpu: "1"
      memory: "2Gi"
```

## Production Deployment Steps

1. **Prepare Environment**
```bash
# Create namespace
kubectl create namespace cache-service

# Create secrets
kubectl create secret generic cache-secrets \
  --from-literal=redis-url=redis://cache-redis:6379 \
  --from-literal=message-hub-url=amqp://rabbitmq:5672 \
  --from-literal=service-auth-key=your-auth-key
```

2. **Deploy Redis Cluster**
```bash
# Install Redis operator
helm repo add ot-redis https://ot-container-kit.github.io/helm-charts
helm install redis-operator ot-redis/redis-operator

# Deploy Redis cluster
kubectl apply -f redis-cluster.yaml
```

3. **Deploy Cache Service**
```bash
# Apply deployments
kubectl apply -f cache-deployment.yaml
kubectl apply -f cache-service.yaml
```

4. **Verify Deployment**
```bash
# Check pods
kubectl get pods -l app=cache-service

# Check service
kubectl get svc cache-service

# Check logs
kubectl logs -l app=cache-service
```

## Scaling

### Horizontal Scaling
The service supports horizontal scaling. Adjust replicas based on load:

```bash
kubectl scale deployment cache-service --replicas=5
```

### Vertical Scaling
Adjust resource limits based on usage patterns:

```yaml
resources:
  requests:
    cpu: "1"
    memory: "1Gi"
  limits:
    cpu: "4"
    memory: "4Gi"
```

### Redis Scaling
Monitor Redis metrics and scale the cluster as needed:

```yaml
spec:
  clusterSize: 6  # Increase Redis nodes
```

## Monitoring

### Prometheus Integration
1. **Service Metrics**
   - Cache hit/miss rates
   - Operation latencies
   - Memory usage
   - Circuit breaker status

2. **Example Grafana Dashboard**
```json
{
  "dashboard": {
    "panels": [
      {
        "title": "Cache Hit Rate",
        "targets": [{
          "expr": "cache_hit_rate"
        }]
      },
      {
        "title": "Operation Latency",
        "targets": [{
          "expr": "cache_operation_latency"
        }]
      }
    ]
  }
}
```

### Alerts

1. **Cache Service Alerts**
```yaml
groups:
- name: cache-service
  rules:
  - alert: HighErrorRate
    expr: cache_error_rate > 0.05
    for: 5m
    labels:
      severity: warning
  - alert: CircuitBreakerOpen
    expr: cache_circuit_breaker_state == 1
    for: 1m
    labels:
      severity: critical
```

2. **Redis Alerts**
```yaml
groups:
- name: redis
  rules:
  - alert: RedisMemoryHigh
    expr: redis_memory_used_bytes / redis_memory_max_bytes > 0.85
    for: 5m
    labels:
      severity: warning
```

## Backup and Recovery

### Redis Backup
1. **Configure Persistence**
```conf
appendonly yes
appendfsync everysec
```

2. **Automated Backups**
```bash
#!/bin/bash
BACKUP_DIR="/backups/redis"
DATE=$(date +%Y%m%d_%H%M%S)
redis-cli SAVE
cp /data/dump.rdb $BACKUP_DIR/dump_$DATE.rdb
```

### Disaster Recovery
1. **Redis Recovery**
```bash
# Stop Redis
kubectl scale deployment cache-redis --replicas=0

# Restore from backup
kubectl cp backup/dump.rdb cache-redis-0:/data/dump.rdb

# Restart Redis
kubectl scale deployment cache-redis --replicas=3
```

2. **Cache Service Recovery**
```bash
# Rolling restart after Redis recovery
kubectl rollout restart deployment cache-service
```

## Security

### Network Security
1. **Network Policies**
```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: cache-service-policy
spec:
  podSelector:
    matchLabels:
      app: cache-service
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: allowed-namespace
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    - podSelector:
        matchLabels:
          app: rabbitmq
```

2. **TLS Configuration**
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: cache-tls
type: kubernetes.io/tls
data:
  tls.crt: base64-encoded-cert
  tls.key: base64-encoded-key
```

### Authentication
1. **Service Authentication**
   - Use strong service auth keys
   - Rotate keys regularly
   - Monitor failed auth attempts

2. **Redis Authentication**
   - Enable Redis AUTH
   - Use strong passwords
   - Configure ACLs

## Performance Tuning

### Cache Service
1. **Environment Variables**
```bash
# Connection Pool
REDIS_POOL_SIZE=50
REDIS_MAX_RETRIES=3

# Circuit Breaker
CIRCUIT_BREAKER_THRESHOLD=5
CIRCUIT_BREAKER_TIMEOUT=60

# Rate Limiting
RATE_LIMIT_REQUESTS=1000
RATE_LIMIT_WINDOW=60
```

2. **JVM Options (if applicable)**
```bash
JAVA_OPTS="-Xms2g -Xmx2g -XX:+UseG1GC"
```

### Redis
1. **Redis Configuration**
```conf
maxmemory 2gb
maxmemory-policy allkeys-lru
activedefrag yes
```

2. **System Settings**
```bash
# System limits
sysctl -w vm.overcommit_memory=1
sysctl -w net.core.somaxconn=1024
```

## Maintenance

### Updates and Patches
1. **Rolling Updates**
```bash
kubectl set image deployment/cache-service \
  cache-service=dnd-cache-service:new-version
```

2. **Rollback Procedure**
```bash
kubectl rollout undo deployment/cache-service
```

### Health Checks
1. **Liveness Probe**
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3
```

2. **Readiness Probe**
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
```

## Troubleshooting

### Common Issues

1. **High Memory Usage**
   - Check Redis memory usage
   - Verify eviction policies
   - Review large keys

2. **High Latency**
   - Monitor network latency
   - Check Redis CPU usage
   - Verify connection pool settings

3. **Circuit Breaker Trips**
   - Check Redis connectivity
   - Verify network policies
   - Review error logs

### Debug Commands

1. **Service Logs**
```bash
# Get service logs
kubectl logs -l app=cache-service

# Get Redis logs
kubectl logs -l app=redis
```

2. **Redis Debug**
```bash
# Connect to Redis CLI
kubectl exec -it redis-0 -- redis-cli

# Monitor commands
redis-cli MONITOR

# Check slow log
redis-cli SLOWLOG GET
```

## Support and Maintenance

### Logging
1. **Log Levels**
   - DEBUG: Detailed debugging
   - INFO: General information
   - WARN: Warning messages
   - ERROR: Error messages

2. **Log Format**
```json
{
  "timestamp": "2025-09-20T21:00:00Z",
  "level": "INFO",
  "service": "cache",
  "event": "cache_hit",
  "data": {
    "key": "user:123",
    "latency_ms": 5
  }
}
```

### Metrics Collection
1. **Service Metrics**
   - Request count
   - Error rate
   - Response time
   - Cache hit/miss

2. **System Metrics**
   - CPU usage
   - Memory usage
   - Network I/O
   - Disk I/O

## Compliance and Auditing

### Data Retention
1. **Cache TTL**
   - Default: 1 hour
   - Maximum: 24 hours
   - Sensitive data: 15 minutes

2. **Audit Logs**
   - Access logs
   - Operation logs
   - Error logs
   - Security events

### Security Compliance
1. **Data Protection**
   - Encryption in transit
   - Authentication required
   - Key rotation policy
   - Access control

2. **Monitoring**
   - Security events
   - Access patterns
   - Error patterns
   - Performance metrics