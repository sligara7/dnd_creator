# D&D Character Creator Service Architecture

## Overview
This documentation describes the architecture and setup of the D&D Character Creator microservices system. The system consists of multiple services coordinated through a message hub, with Traefik serving as the API gateway.

## System Components

### API Gateway (Traefik)
The system uses Traefik v2.10 as the edge router and API gateway. Traefik handles:
- Route management to microservices
- TLS termination
- Load balancing
- Health checks
- Middleware (CORS, rate limiting, security headers)

#### Development Configuration
```yaml
# docker-compose.yml service definition
traefik:
  image: traefik:v2.10
  command:
    - "--api.insecure=true"  # Dev only
    - "--providers.docker=true"
    - "--providers.docker.exposedbydefault=false"
    - "--entrypoints.web.address=:80"
    - "--entrypoints.websecure.address=:443"
  ports:
    - "80:80"
    - "443:443"
    - "8080:8080"  # Dashboard (dev only)
  volumes:
    - "/var/run/docker.sock:/var/run/docker.sock:ro"
    - "./traefik:/etc/traefik"
```

#### Production Setup
For production, enable:
- HTTPS with Let's Encrypt
- HTTP → HTTPS redirection
- Rate limiting
- Security headers
- Request logging
- Metrics (optional)

### Core Services

#### Character Service
- Path: `/api/character`
- Handles character creation and management
- Integrates with background generation
- Manages character evolution

#### Campaign Service
- Path: `/api/campaign`
- Manages campaign state
- Tracks story progression
- Handles theme transitions

#### World Service
- Path: `/api/world`
- Manages world state and environment
- Handles location generation
- Tracks world changes

#### Theme Service
- Path: `/api/theme`
- Manages theme transitions
- Converts entities between themes
- Maintains theme consistency

#### Message Hub
- Path: `/api/hub`
- Central message broker
- Handles service communication
- Manages event distribution

### Service Communication
Services communicate through the message hub using:
- REST APIs for direct requests
- Event messages for async operations
- WebSocket for real-time updates

## Deployment

### Local Development
```bash
# Start all services
docker-compose up -d

# Access Traefik dashboard
http://localhost:8080

# Service endpoints
http://localhost/api/character
http://localhost/api/campaign
http://localhost/api/world
http://localhost/api/theme
http://localhost/api/hub
```

### Production Deployment
1. Update Traefik configuration:
   ```yaml
   # traefik/traefik.yml
   entryPoints:
     web:
       address: ":80"
       http:
         redirections:
           entryPoint:
             to: websecure
             scheme: https
     websecure:
       address: ":443"
       http:
         tls:
           certResolver: letsencrypt

   certificatesResolvers:
     letsencrypt:
       acme:
         email: your-email@example.com
         storage: /etc/traefik/acme.json
         httpChallenge:
           entryPoint: web
   ```

2. Configure security middlewares:
   ```yaml
   # traefik/dynamic/middlewares.yml
   http:
     middlewares:
       rate-limit:
         rateLimit:
           average: 100
           burst: 50
       secure-headers:
         headers:
           frameDeny: true
           browserXssFilter: true
           contentTypeNosniff: true
           forceSTSHeader: true
           stsSeconds: 15552000
   ```

3. Update service labels for production:
   ```yaml
   labels:
     - "traefik.enable=true"
     - "traefik.http.routers.service.rule=PathPrefix(`/api/service`)"
     - "traefik.http.routers.service.middlewares=rate-limit,secure-headers"
     - "traefik.http.routers.service.tls=true"
     - "traefik.http.routers.service.tls.certresolver=letsencrypt"
   ```

## Security Considerations

### API Authentication
- Use API keys for service-to-service communication
- Implement JWT for user authentication
- Consider OAuth2 for third-party integration

### Data Protection
- Encrypt sensitive data at rest
- Use TLS for all communications
- Implement rate limiting
- Add request size limits
- Configure security headers

### Secrets Management
- Use environment variables
- Consider Docker secrets
- Never commit sensitive data
- Rotate credentials regularly

## Monitoring

### Logs
- Traefik access logs
- Service application logs
- Error tracking
- Request tracing

### Metrics
- Service health checks
- Response times
- Error rates
- Resource usage

## Scaling Considerations

### Horizontal Scaling
- Services can be scaled independently
- Traefik handles load balancing
- Message hub manages distributed events

### Cloud Migration Path
1. Single VM deployment
2. Container orchestration (e.g., Kubernetes)
3. Managed services integration
4. CDN integration

## Development Workflow

### Local Setup
1. Clone repository
2. Copy `.env.example` to `.env`
3. Configure environment variables
4. Run `docker-compose up`

### Testing
- Unit tests per service
- Integration tests
- End-to-end tests
- Load testing

### CI/CD
- Automated builds
- Test automation
- Deployment pipelines
- Environment promotion

## Future Enhancements
- Service mesh integration
- Distributed tracing
- Automated scaling
- Backup/restore procedures
- Disaster recovery planning
