# System Requirements Document: LLM Service (SRD-LLM-001)

Version: 1.0
Status: Active
Last Updated: 2025-08-30

## 1. System Overview

### 1.1 Purpose
The LLM Service provides AI-powered text and image generation for the D&D Character Creator system, utilizing OpenAI for narrative content and GetImg.AI for visual content.

### 1.2 Core Principles
- Provide service-specific functionality
- All inter-service communication MUST go through Message Hub
- No direct service-to-service communication allowed
- Service isolation and independence
- Event-driven architecture

### 1.3 Scope
- Text generation (OpenAI)
- Image generation (GetImg.AI)
- Theme management
- Model coordination
- Content validation
- Cross-service integration

## 2. Text Generation (OpenAI)

### 2.1 Character Content Generation
- Character backstories
- Personality traits
- Combat strategies
- Character development arcs
- NPC interactions
- Equipment narratives

### 2.2 Campaign Content Generation
- Campaign plots
- Location descriptions
- Quest narratives
- NPC dialogues
- Event sequences
- Environmental descriptions

### 2.3 Narrative Enhancement
- Dialogue expansion
- Scene descriptions
- Combat narration
- Equipment descriptions
- Spell effects narration
- Character interactions

## 3. Image Generation (GetImg.AI)

### 3.1 Text-to-Image Generation
- Character portraits
- Item illustrations
- Location visuals
- Map backgrounds
- Environmental scenes
- Magical effects

### 3.2 Image-to-Image Generation
- Map modifications
- Portrait refinements
- Item enhancements
- Theme adaptations
- Style transfers
- Visual corrections

### 3.3 Image Enhancement
- Resolution upscaling
- Face improvements
- Detail enhancement
- Style consistency
- Theme alignment
- Visual quality

## 4. Technical Requirements

### 4.1 OpenAI Integration
- API authentication
- Multiple model support:
  * GPT-4 (primary model)
  * GPT-3.5-turbo (fallback model)
  * Claude 3 (alternative model)
- Context management
- Response processing
- Error handling
- Token usage tracking
- Model-specific optimizations

### 4.2 Caching and Rate Limiting
- Redis-based caching system
- Configurable cache TTL
- Service-specific rate limits:
  * Text generation: 100 requests/minute
  * Image generation: 10 requests/minute
- Token usage tracking and quotas
- Circuit breaker implementation
- Request prioritization

### 4.3 GetImg.AI Integration
- API authentication
- Model management
- Image processing
- Response handling
- Error recovery
- Rate control

### 4.3 Content Management
- Prompt templates
- Style guides
- Theme configurations
- Quality parameters
- Output validation
- Content filtering

## 5. Integration Requirements

### 5.1 Character Service Integration
- Character backstory generation
- Portrait creation requests
- Equipment visualization
- Personality generation
- Combat description generation
- NPC interaction generation

### 5.2 Campaign Service Integration
- Map generation requests
- Location descriptions
- Quest narratives
- NPC dialogues
- Environment descriptions
- Event narrations

### 5.3 Message Hub Integration
- Event handling
- State management
- Service coordination
- Health monitoring
- Error reporting
- Queue management

## 6. Theme Management

### 6.1 Text Theme Control
- Genre adaptation
- Style consistency
- Tone management
- Narrative alignment
- Language patterns
- Descriptive elements

### 6.2 Visual Theme Control
- Art style management
- Color schemes
- Visual elements
- Lighting effects
- Environmental consistency
- Detail levels

## 7. Performance Requirements

### 7.1 Response Times
- Text generation: < 5 seconds
- Image generation: < 30 seconds
- Image modification: < 20 seconds
- Theme application: < 15 seconds
- Content validation: < 2 seconds
- Queue processing: < 1 second

### 7.2 Quality Metrics
- Text coherence: > 95%
- Image quality: > 90%
- Theme consistency: > 95%
- Response success: > 99%
- Error handling: < 1% failure
- Queue efficiency: > 95%

## 8. Security Requirements

### 8.1 API Security
- Key management
- Request validation
- Response verification
- Content filtering
- Access control
- Rate limiting

### 8.2 Content Security
- Input sanitization
- Output validation
- Content filtering
- PII protection
- Data encryption
- Access logging

## 9. Monitoring Requirements

### 9.1 Performance Monitoring
- Response times
- Queue lengths
- Error rates
- API quotas
- Resource usage
- Service health

### 9.2 Quality Monitoring
- Content coherence
- Image quality
- Theme consistency
- Error patterns
- Usage patterns
- Service reliability

## 10. Data Models

### 10.1 Text Generation Request
```json
{
  "type": "character|campaign|narrative",
  "context": {
    "prompt": "string",
    "parameters": {},
    "theme": "string"
  },
  "model": {
    "name": "string",
    "temperature": "float",
    "max_tokens": "integer"
  },
  "metadata": {
    "request_id": "uuid",
    "source_service": "string"
  }
}
```

### 10.2 Image Generation Request
```json
{
  "type": "text_to_image|image_to_image",
  "content": {
    "prompt": "string",
    "source_image": "string",
    "parameters": {
      "model": "string",
      "style": "string",
      "size": {
        "width": "integer",
        "height": "integer"
      },
      "cfg_scale": "float",
      "steps": "integer"
    }
  },
  "metadata": {
    "request_id": "uuid",
    "source_service": "string"
  }
}
```
