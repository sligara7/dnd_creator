# Service Documentation Index

Version: 1.0
Status: Active
Last Updated: 2025-08-30

This document serves as the master index for all service documentation, providing cross-references between Service Requirements Documents (SRDs) and Interface Control Documents (ICDs).

## Document Organization

### Core Documents
- [WARP.md](../WARP.md) - Web Application Requirements & Planning
  * System overview
  * Architecture principles
  * Service organization
  * Development guidelines

### Service Requirements Documents (SRDs)
Located in `/requirements/srd/`, these documents define the requirements, capabilities, and responsibilities of each service.

### Interface Control Documents (ICDs)
Located in `/requirements/icd/`, these documents define the interfaces, APIs, and integration patterns for each service.

## Service Documentation Matrix

### Edge Services
| Service      | SRD Status | ICD Status | WARP Section | Description |
|--------------|------------|------------|--------------|-------------|
| API Gateway  | ✓          | ✓          | [Edge Layer] | Entry point for all client requests |
| Auth Service | ✓          | ✓          | [Edge Layer] | Authentication and authorization |
| Metrics Service | ✓       | ✓          | [Edge Layer] | System-wide metrics and monitoring |

### Communication Layer
| Service      | SRD Status | ICD Status | WARP Section | Description |
|--------------|------------|------------|--------------|-------------|
| Message Hub  | ✓          | ✓          | [Communication Layer] | Inter-service communication |
| Cache Service| ✓          | ✓          | [Communication Layer] | Distributed caching |
| Storage Service| ✓        | ✓          | [Communication Layer] | Asset storage and management |

### Core Services
| Service      | SRD Status | ICD Status | WARP Section | Description |
|--------------|------------|------------|--------------|-------------|
| Character Service | ✓     | ✓          | [Core Services] | Character management |
| Campaign Service | ✓      | ✓          | [Core Services] | Campaign management |
| Image Service | ✓         | ✓          | [Core Services] | Image generation and processing |
| LLM Service  | ✓         | ✓          | [Core Services] | AI text generation |
| Catalog Service | ✓       | ✓          | [Core Services] | Game content management |

### Support Services
| Service      | SRD Status | ICD Status | WARP Section | Description |
|--------------|------------|------------|--------------|-------------|
| Search Service | ✓        | ✓          | [Support Services] | Full-text and semantic search |
| Audit Service | ✓         | ✓          | [Support Services] | Security auditing and logging |

## Service Dependencies

### Character Service Dependencies
- Message Hub (event communication)
- Cache Service (performance optimization)
- Storage Service (asset management)
- LLM Service (content generation)
- Search Service (character search)
- Auth Service (access control)

### Campaign Service Dependencies
- Message Hub (event communication)
- Cache Service (state management)
- Storage Service (asset management)
- LLM Service (narrative generation)
- Search Service (campaign search)
- Auth Service (access control)

### Image Service Dependencies
- Message Hub (event communication)
- Cache Service (result caching)
- Storage Service (image storage)
- LLM Service (prompt enhancement)
- Auth Service (access control)

### LLM Service Dependencies
- Message Hub (event communication)
- Cache Service (result caching)
- Storage Service (model storage)
- Search Service (context search)
- Auth Service (access control)

### Catalog Service Dependencies
- Message Hub (event communication)
- Cache Service (content caching)
- Storage Service (content storage)
- Search Service (content search)
- Auth Service (access control)

## Data Ownership

### Primary Data Stores
| Service      | Data Store | Data Type | Backup Requirements |
|--------------|------------|-----------|---------------------|
| Character Service | PostgreSQL | Character data | Daily + WAL |
| Campaign Service | PostgreSQL | Campaign data | Daily + WAL |
| Image Service | S3 + PostgreSQL | Images + metadata | Daily |
| Catalog Service | PostgreSQL | Game content | Daily + WAL |
| Search Service | Elasticsearch | Search indices | Daily |
| Audit Service | Elasticsearch | Audit logs | Daily |
| Auth Service | PostgreSQL | Auth data | Daily + WAL |

### Caching Layers
| Service      | Cache Type | TTL | Invalidation |
|--------------|------------|-----|--------------|
| Character Service | Redis | 1h | Event-based |
| Campaign Service | Redis | 1h | Event-based |
| Image Service | Redis | 24h | Event-based |
| Catalog Service | Redis | 12h | Event-based |
| Search Service | Redis | 1h | Event-based |

## Service Boundaries

### Data Flow Rules
1. All service-to-service communication must go through Message Hub
2. Services can only access their own databases directly
3. All external data access must use defined interfaces
4. Services must handle their own data validation
5. Cross-service transactions must use event sourcing

### Interface Guidelines
1. All services must implement health check endpoints
2. All services must expose metrics endpoints
3. All services must validate incoming requests
4. All services must handle partial failures
5. All services must implement circuit breakers

## Version Control

### Document Versioning
- All SRDs and ICDs use semantic versioning
- Changes require PR review
- Major versions need architecture review
- Backward compatibility required

### Service Versioning
- API versions in URL (/api/v2/...)
- Services deployed independently
- Interface changes need ICD update
- Breaking changes need migration plan

## Implementation Guidelines

### Code Organization
- Clean Architecture principles
- Separation of concerns
- Domain-driven design
- Test-driven development

### Testing Requirements
- Unit tests > 80% coverage
- Integration tests for interfaces
- End-to-end tests for flows
- Performance test suite

### Monitoring Requirements
- Service metrics
- Business metrics
- SLA monitoring
- Error tracking

### Security Requirements
- Input validation
- Output encoding
- Authentication
- Authorization
- Audit logging
