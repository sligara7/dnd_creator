# API Gateway Operational Guide

## Overview
This guide provides instructions for deploying, maintaining, and troubleshooting the API Gateway service.

## Deployment

### Prerequisites
- Docker and Docker Compose installed
- Access to required services (Message Hub, Auth Service)
- SSL certificates for production deployment
- Prometheus for metrics collection

### Configuration Files
1. **traefik.yml** (Static Configuration)
   ```yaml
   # Example minimal configuration
   api:
     dashboard: false  # Enable only in development
     insecure: false
   
   entryPoints:
     web:
       address: ":80"
     websecure:
       address: ":443"
   ```

2. **dynamic.yml** (Dynamic Configuration)
   ```yaml
   # Example service configuration
   http:
     routers:
       character-service:
         rule: "PathPrefix(`/api/v2/characters`)"
         service: "character-service"
         middlewares:
           - auth
           - rate-limit
   ```

### Environment Variables
Required variables:
```bash
AUTH_SERVICE_URL=http://auth-service:8300
MESSAGE_HUB_URL=http://message-hub:8200
TRAEFIK_PILOT_TOKEN=your-token  # For Traefik Enterprise features
```

### Deployment Steps
1. Configure environment:
   ```bash
   cp .env.example .env
   # Edit .env with your values
   ```

2. Start services:
   ```bash
   docker-compose up -d
   ```

3. Verify deployment:
   ```bash
   # Check service health
   curl http://localhost:8080/health
   
   # Check Prometheus metrics
   curl http://localhost:8080/metrics
   ```

## Monitoring

### Health Checks
Monitor the following endpoints:
- `/health` - Overall gateway health
- `/health/{service}` - Individual service health
- `/monitoring/metrics` - Prometheus metrics

### Key Metrics
1. **Request Metrics**
   - Total requests per service
   - Request latency
   - Error rates

2. **Service Health**
   - Service status
   - Response times
   - Error counts

3. **Security Metrics**
   - Authentication failures
   - Rate limit hits
   - Circuit breaker triggers

### Alerting
Configure alerts for:
- High error rates (>5% of requests)
- Service unhealthy status
- High latency (>500ms)
- Authentication spikes
- Circuit breaker triggers

## Maintenance

### Routine Tasks
1. **SSL Certificate Management**
   ```bash
   # Check certificate status
   docker-compose exec traefik traefik show cert
   
   # Force certificate renewal
   docker-compose exec traefik traefik renew
   ```

2. **Log Rotation**
   - Configure logrotate for container logs
   - Monitor disk usage
   - Archive old logs

3. **Configuration Updates**
   ```bash
   # Test configuration
   docker-compose config
   
   # Apply changes
   docker-compose up -d --force-recreate
   ```

### Backup Procedures
1. **Configuration Backup**
   - Back up all files in /config
   - Store SSL certificates securely
   - Version control configurations

2. **State Backup**
   - Service registry state
   - Metrics data
   - Access logs

## Troubleshooting

### Common Issues

1. **Service Discovery Failures**
   ```bash
   # Check service registration
   curl http://localhost:8080/discovery/services
   
   # Verify service health
   curl http://localhost:8080/health/{service}
   ```

2. **Authentication Issues**
   - Verify Auth Service connection
   - Check token validity
   - Review auth logs

3. **Performance Problems**
   - Monitor resource usage
   - Check rate limits
   - Review circuit breaker status

### Debug Mode
Enable debug logging:
```yaml
# traefik.yml
log:
  level: DEBUG
```

### Recovery Procedures

1. **Service Recovery**
   ```bash
   # Restart specific service
   docker-compose restart service_name
   
   # Full gateway restart
   docker-compose down
   docker-compose up -d
   ```

2. **Configuration Recovery**
   ```bash
   # Restore from backup
   cp /path/to/backup/traefik.yml config/
   docker-compose restart
   ```

## Security

### Access Control
- Use strong API keys
- Rotate secrets regularly
- Monitor authentication logs

### SSL/TLS
- Keep certificates updated
- Use modern cipher suites
- Enable HSTS

### Network Security
- Use internal networks
- Limit exposed ports
- Monitor unusual traffic

## Scaling

### Horizontal Scaling
```bash
# Scale gateway instances
docker-compose up -d --scale api_gateway=3
```

### Load Balancing
- Configure sticky sessions if needed
- Monitor load distribution
- Adjust rate limits

## Disaster Recovery

### Backup Strategy
1. Daily configuration backups
2. Regular state snapshots
3. Secure credential storage

### Recovery Steps
1. Restore configurations
2. Verify service connections
3. Test functionality
4. Monitor recovery

## Performance Tuning

### Configuration Optimization
```yaml
# Example performance settings
providers:
  docker:
    exposedByDefault: false
    network: internal
    swarmMode: false
```

### Resource Allocation
- Monitor CPU/memory usage
- Adjust container limits
- Optimize cache settings

## References

### Documentation
- [Traefik Documentation](https://doc.traefik.io/traefik/)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

### Support
- Open issues on project repository
- Contact system administrators
- Review service logs
