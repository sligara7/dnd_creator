# D&D Image Support Service - Requirements Specification

## 1. Overview

The D&D Image Support Service is a containerized microservice that provides AI-generated visual content for D&D campaigns, including maps, character portraits, and item images. It integrates with the GetImg.AI service and serves as a visual content provider for both the Campaign Creator and Character Creator services.

## 2. Core Requirements

### 2.1 Service Architecture
- **REQ-001**: Service MUST be containerized using Podman
- **REQ-002**: Service MUST provide RESTful API endpoints
- **REQ-003**: Service MUST integrate with GetImg.AI API for image generation
- **REQ-004**: Service MUST maintain its own database for image storage and metadata
- **REQ-005**: Service MUST support UUID-based image identification

### 2.2 External Integrations
- **REQ-006**: Service MUST accept inputs from Campaign Creator service (`/backend_campaign/app.py`)
- **REQ-007**: Service MUST accept inputs from Character Creator service (`/backend/app.py`)
- **REQ-008**: Service MUST link generated images to content in the backend database
- **REQ-009**: Service MUST support theme-based image generation suggestions

## 3. Map Generation Requirements

### 3.1 Campaign Maps (Operational Level)
- **REQ-010**: Service MUST generate campaign-level maps with regional scope
- **REQ-011**: Campaign maps MUST support marking party positions
- **REQ-012**: Campaign maps MUST support marking ruins, cities, and landmarks
- **REQ-013**: Campaign maps MUST include geographical features (mountains, rivers, forests)
- **REQ-014**: Campaign maps MUST support multiple scales (kingdom, region, local area)

### 3.2 Encounter Maps (Tactical Level)
- **REQ-015**: Service MUST generate tactical battle maps
- **REQ-016**: Encounter maps MUST include distance measurement grids
- **REQ-017**: Encounter maps MUST support character position overlays
- **REQ-018**: Encounter maps MUST support NPC and monster position overlays
- **REQ-019**: Encounter maps MUST support spell and ability range overlays
- **REQ-020**: Encounter maps MUST be suitable for in-game tactical play

### 3.3 Map Features and Functionality
- **REQ-021**: All maps MUST have grid overlays for distance measurement
- **REQ-022**: Maps MUST support standard D&D 5e grid scales (5-foot squares)
- **REQ-023**: Maps MUST be generated based on campaign theme context
- **REQ-024**: Maps MUST support various terrain types (dungeon, forest, city, etc.)
- **REQ-025**: Map generation MUST accept descriptive prompts from campaign service

## 4. Character and Content Image Requirements

### 4.1 Character Images
- **REQ-026**: Service MUST generate character portrait images
- **REQ-027**: Service MUST generate images for NPCs
- **REQ-028**: Service MUST generate images for monsters/creatures
- **REQ-029**: Character images MUST reflect character attributes (race, class, equipment)
- **REQ-030**: Character images MUST support campaign theme styling

### 4.2 Item Images
- **REQ-031**: Service MUST generate images for weapons
- **REQ-032**: Service MUST generate images for armor
- **REQ-033**: Service MUST generate images for other equipment and items
- **REQ-034**: Item images MUST reflect item properties and magical effects
- **REQ-035**: Item images MUST support campaign theme styling

### 4.3 Content Association
- **REQ-036**: Generated images MUST be associated with source content IDs
- **REQ-037**: Service MUST maintain references to backend database content
- **REQ-038**: Image metadata MUST include source service and content type
- **REQ-039**: Service MUST support image retrieval by content ID

## 5. Data Management Requirements

### 5.1 Database Requirements
- **REQ-040**: Service MUST maintain a dedicated image database
- **REQ-041**: Database MUST store image metadata and file references
- **REQ-042**: Database MUST support UUID primary keys for all images
- **REQ-043**: Database MUST track image generation parameters and prompts
- **REQ-044**: Database MUST maintain associations to source content

### 5.2 Image Storage
- **REQ-045**: Service MUST store generated images persistently
- **REQ-046**: Images MUST be accessible via unique URLs
- **REQ-047**: Service MUST support multiple image formats (PNG, JPEG)
- **REQ-048**: Service MUST implement image caching mechanisms
- **REQ-049**: Service MUST support image versioning for updated content

### 5.3 Data Retention
- **REQ-050**: Service MUST retain images for future reference
- **REQ-051**: Service MUST support image archival and cleanup
- **REQ-052**: Service MUST maintain audit trail of image generation

## 6. API Requirements

### 6.1 Map Generation Endpoints
- **REQ-053**: API MUST provide `/maps/campaign` endpoint for campaign map generation
- **REQ-054**: API MUST provide `/maps/encounter` endpoint for tactical map generation
- **REQ-055**: Map endpoints MUST accept theme and descriptive parameters
- **REQ-056**: Map endpoints MUST return map URLs and metadata
- **REQ-057**: Map endpoints MUST support grid configuration options

### 6.2 Character Image Endpoints
- **REQ-058**: API MUST provide `/images/character` endpoint
- **REQ-059**: API MUST provide `/images/npc` endpoint
- **REQ-060**: API MUST provide `/images/monster` endpoint
- **REQ-061**: Character endpoints MUST accept character data from backend service
- **REQ-062**: Character endpoints MUST support theme-based styling

### 6.3 Item Image Endpoints
- **REQ-063**: API MUST provide `/images/weapon` endpoint
- **REQ-064**: API MUST provide `/images/armor` endpoint
- **REQ-065**: API MUST provide `/images/item` endpoint
- **REQ-066**: Item endpoints MUST accept item data from backend service
- **REQ-067**: Item endpoints MUST support magical effect visualization

### 6.4 Utility Endpoints
- **REQ-068**: API MUST provide `/images/{uuid}` endpoint for image retrieval
- **REQ-069**: API MUST provide `/images/{uuid}/metadata` endpoint
- **REQ-070**: API MUST provide health check and status endpoints
- **REQ-071**: API MUST support batch image generation requests

## 7. Theme and Styling Requirements

### 7.1 Theme Support
- **REQ-072**: Service MUST support campaign theme-based image generation
- **REQ-073**: Service MUST provide theme suggestions for prompts
- **REQ-074**: Supported themes MUST include: western, steampunk, gothic, high fantasy, nature
- **REQ-075**: Theme application MUST be configurable and optional
- **REQ-076**: Service MUST maintain theme consistency across related images

### 7.2 Style Consistency
- **REQ-077**: Images for the same campaign MUST maintain visual consistency
- **REQ-078**: Service MUST support style templates for different content types
- **REQ-079**: Service MUST allow custom styling parameters
- **REQ-080**: Service MUST support art style preferences (realistic, cartoon, etc.)

## 8. Integration Requirements

### 8.1 GetImg.AI Integration
- **REQ-081**: Service MUST integrate with GetImg.AI API
- **REQ-082**: Service MUST handle GetImg.AI rate limits and errors
- **REQ-083**: Service MUST support GetImg.AI request IDs for tracking
- **REQ-084**: Service MUST implement proper error handling for API failures
- **REQ-085**: Service MUST optimize prompt engineering for best results

### 8.2 Backend Service Integration
- **REQ-086**: Service MUST authenticate with Campaign Creator service
- **REQ-087**: Service MUST authenticate with Character Creator service
- **REQ-088**: Service MUST handle content updates and regeneration requests
- **REQ-089**: Service MUST support webhook notifications for content changes

## 9. Performance Requirements

### 9.1 Response Times
- **REQ-090**: Image generation requests MUST respond within 30 seconds
- **REQ-091**: Image retrieval MUST respond within 2 seconds
- **REQ-092**: Metadata queries MUST respond within 1 second
- **REQ-093**: Service MUST support concurrent image generation requests

### 9.2 Scalability
- **REQ-094**: Service MUST support horizontal scaling
- **REQ-095**: Service MUST handle peak loads during campaign sessions
- **REQ-096**: Service MUST implement request queuing for high demand
- **REQ-097**: Service MUST support load balancing across instances

## 10. Security Requirements

### 10.1 Authentication and Authorization
- **REQ-098**: Service MUST implement API key authentication
- **REQ-099**: Service MUST validate requests from authorized services only
- **REQ-100**: Service MUST implement request rate limiting
- **REQ-101**: Service MUST log all image generation requests

### 10.2 Data Protection
- **REQ-102**: Service MUST protect sensitive campaign and character data
- **REQ-103**: Service MUST implement secure image storage
- **REQ-104**: Service MUST support HTTPS for all communications
- **REQ-105**: Service MUST implement data encryption at rest

## 11. Deployment Requirements

### 11.1 Containerization
- **REQ-106**: Service MUST be packaged as a Podman container
- **REQ-107**: Container MUST include all necessary dependencies
- **REQ-108**: Container MUST support environment-based configuration
- **REQ-109**: Container MUST implement health checks
- **REQ-110**: Container MUST support graceful shutdown

### 11.2 Configuration
- **REQ-111**: Service MUST support configuration via environment variables
- **REQ-112**: Service MUST support database connection configuration
- **REQ-113**: Service MUST support GetImg.AI API key configuration
- **REQ-114**: Service MUST support logging level configuration

## 12. Monitoring and Logging Requirements

### 12.1 Logging
- **REQ-115**: Service MUST log all image generation requests and responses
- **REQ-116**: Service MUST log API errors and failures
- **REQ-117**: Service MUST implement structured logging
- **REQ-118**: Service MUST support log level configuration

### 12.2 Metrics
- **REQ-119**: Service MUST expose metrics for monitoring
- **REQ-120**: Service MUST track image generation success rates
- **REQ-121**: Service MUST track API response times
- **REQ-122**: Service MUST track resource utilization

## 13. Reference Documentation

### 13.1 GetImg.AI API References
- GetImg.AI Introduction: https://docs.getimg.ai/reference/introduction
- GetImg.AI API Reference: https://docs.getimg.ai/reference/introduction-1
- Pricing Information: https://docs.getimg.ai/reference/pricing
- Image Responses: https://docs.getimg.ai/reference/image-responses
- Error Handling: https://docs.getimg.ai/reference/errors
- Rate Limits: https://docs.getimg.ai/reference/rate-limits
- Request IDs: https://docs.getimg.ai/reference/request-ids

### 13.2 Integration Points
- Character Creator endpoints: `/backend/app.py`
- Campaign Creator endpoints: `/backend_campaign/app.py`
- Map generation use case: https://getimg.ai/use-cases/ai-dnd-map-maker

## 14. Acceptance Criteria

### 14.1 Map Generation
- ✅ Campaign maps generated with appropriate scale and features
- ✅ Encounter maps generated with grids and tactical layout
- ✅ Maps support overlay features for gameplay
- ✅ Theme-appropriate map styling applied

### 14.2 Character and Item Images
- ✅ Character images reflect attributes and equipment
- ✅ Item images show appropriate details and effects
- ✅ Images maintain campaign theme consistency
- ✅ Images properly associated with source content

### 14.3 System Integration
- ✅ Service integrates successfully with Campaign Creator
- ✅ Service integrates successfully with Character Creator
- ✅ Images stored and retrievable via UUID
- ✅ Service operates reliably in container environment

### 14.4 Performance and Reliability
- ✅ Image generation completes within time limits
- ✅ Service handles concurrent requests effectively
- ✅ Error handling works correctly for API failures
- ✅ Service maintains high availability during operation
