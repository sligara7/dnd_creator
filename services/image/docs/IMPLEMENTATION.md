# Image Service Implementation Guide

## Overview
The Image Service is a streamlined service responsible for image storage and retrieval operations. It uses the Message Hub for inter-service communication and delegates all persistent storage to the Storage Service.

## Architecture

### Service Components
1. **FastAPI Application**
   - Main application setup with FastAPI
   - Image upload/download endpoints
   - Health check monitoring

2. **Message Hub Integration**
   - Event-based communication
   - Service discovery
   - Message handling and routing
   - Request/response correlation

3. **Storage Integration**
   - Image file persistence via Storage Service
   - Metadata management
   - Asset versioning support

### Data Flow
```
Client -> Image Service -> Message Hub -> Storage Service
                      <- Message Hub <-
```

## Communication Patterns

### Message Hub Events
1. **Storage Requests**
   ```python
   {
       "operation": "create_image",
       "operation_id": "uuid",
       "data": {
           "type": "portrait",
           "subtype": "character",
           "name": "Portrait Name",
           "url": "image_url",
           "format": "png",
           "width": 512,
           "height": 512,
           "size": 1024,
           "theme": "fantasy"
       }
   }
   ```

2. **Storage Responses**
   ```python
   {
       "operation_id": "uuid",
       "status": "success",
       "data": {
           "id": "image_uuid",
           "type": "portrait",
           "url": "image_url",
           "metadata": {
               "theme": "fantasy",
               "created_at": "timestamp",
               "updated_at": "timestamp"
           }
       }
   }
   ```

### Message Flow
1. Client sends request to Image Service
2. Image Service creates operation ID and publishes event
3. Storage Service processes event and responds
4. Image Service correlates response and returns to client

## API Endpoints

### POST /api/v2/images/
Upload a new image file.

**Request:**
- Method: POST
- Content-Type: multipart/form-data
- Parameters:
  - image: File (required)
  - type: string (required)
  - subtype: string (required)
  - name: string (required)
  - theme: string (required)

**Response:**
```json
{
    "id": "uuid",
    "type": "portrait",
    "subtype": "character",
    "content": {
        "url": "image_url",
        "format": "png",
        "size": {
            "width": 512,
            "height": 512
        }
    },
    "metadata": {
        "theme": "fantasy",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### GET /api/v2/images/{image_id}
Retrieve an image by ID.

**Response:**
```json
{
    "id": "uuid",
    "type": "portrait",
    "subtype": "character",
    "content": {
        "url": "image_url",
        "format": "png",
        "size": {
            "width": 512,
            "height": 512
        }
    },
    "metadata": {
        "theme": "fantasy",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
}
```

### GET /api/v2/images/
List images with optional filters.

**Query Parameters:**
- type: string (optional)
- theme: string (optional)
- skip: integer (optional, default: 0)
- limit: integer (optional, default: 100)

**Response:**
```json
[
    {
        "id": "uuid",
        "type": "portrait",
        "subtype": "character",
        "content": {
            "url": "image_url",
            "format": "png",
            "size": {
                "width": 512,
                "height": 512
            }
        },
        "metadata": {
            "theme": "fantasy",
            "created_at": "timestamp",
            "updated_at": "timestamp"
        }
    }
]
```

### DELETE /api/v2/images/{image_id}
Delete an image by ID.

## Development Setup

1. Install dependencies:
   ```bash
   poetry install
   ```

2. Start Message Hub:
   ```bash
   # In development environment, ensure RabbitMQ is running
   docker run -d --name rabbitmq -p 5672:5672 rabbitmq:3
   ```

3. Configure environment:
   ```bash
   # Required environment variables
   export MESSAGE_HUB_URL=amqp://localhost
   export STORAGE_SERVICE_URL=http://storage:8000
   ```

4. Run service:
   ```bash
   poetry run uvicorn image_service.app:app --reload
   ```

## Testing

1. Run tests:
   ```bash
   poetry run pytest
   ```

2. Run integration tests:
   ```bash
   poetry run pytest tests/integration/
   ```

3. Run API tests:
   ```bash
   poetry run pytest tests/api/
   ```

## Dependencies

- FastAPI: Web framework
- aio-pika: Message Hub client
- httpx: HTTP client
- Pillow: Image processing
- pytest: Testing framework
- python-multipart: File upload support

## Error Handling

All errors follow a standard format:
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error message",
        "details": {
            "additional": "error details"
        }
    }
}
```

Common error codes:
- INVALID_FILE_TYPE: File type not supported
- EMPTY_FILE: No file content provided
- STORAGE_ERROR: Error communicating with storage service
- VALIDATION_ERROR: Invalid request parameters