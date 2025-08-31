# Character Service API Documentation

## Table of Contents

1. [Overview](#overview)
2. [Authentication](#authentication)
3. [Character Endpoints](#character-endpoints)
4. [Journal Endpoints](#journal-endpoints)
5. [Inventory Endpoints](#inventory-endpoints)
6. [Evolution Endpoints](#evolution-endpoints)
7. [Antitheticon Endpoints](#antitheticon-endpoints)
8. [Error Handling](#error-handling)

## Overview

The Character Service API provides a RESTful interface for managing D&D 5e characters, including their creation, evolution, journaling, and inventory management. The API follows REST principles and uses JSON for request/response payloads.

### Base URL

```
http://localhost:8000/api/v1
```

### Common Request Headers

```
Content-Type: application/json
Authorization: Bearer <token>
```

## Authentication

Authentication is handled by the Auth Service. All endpoints require a valid JWT token.

```
Authorization: Bearer eyJ0eXA...
```

## Character Endpoints

### List Characters

```
GET /characters
```

Query Parameters:
- `limit` (int, default: 100): Maximum number of characters to return
- `offset` (int, default: 0): Number of characters to skip

Response:
```json
[
  {
    "id": "string",
    "name": "string",
    "species": "string",
    "background": "string",
    "level": 0,
    "character_classes": {},
    "backstory": "string",
    "created_at": "string",
    "user_modified": false
  }
]
```

### Get Character

```
GET /characters/{character_id}
```

Response:
```json
{
  "id": "string",
  "name": "string",
  "species": "string",
  "background": "string",
  "level": 0,
  "character_classes": {},
  "backstory": "string",
  "created_at": "string",
  "user_modified": false
}
```

### Create Character

```
POST /characters
```

Request Body:
```json
{
  "name": "string",
  "species": "string",
  "background": "string",
  "level": 0,
  "character_classes": {},
  "backstory": "string"
}
```

### Update Character

```
PUT /characters/{character_id}
```

Request Body:
```json
{
  "name": "string",
  "species": "string",
  "background": "string",
  "level": 0,
  "character_classes": {},
  "backstory": "string"
}
```

### Delete Character

```
DELETE /characters/{character_id}
```

### Direct Edit Character

```
POST /characters/{character_id}/direct-edit
```

Request Body:
```json
{
  "updates": {
    "field_name": "new_value"
  },
  "notes": "string"
}
```

## Journal Endpoints

### List Journal Entries

```
GET /journals?character_id={character_id}
```

Query Parameters:
- `character_id` (string, required): Character ID
- `limit` (int, default: 100): Maximum number of entries to return
- `offset` (int, default: 0): Number of entries to skip

Response:
```json
[
  {
    "id": "string",
    "character_id": "string",
    "title": "string",
    "content": "string",
    "entry_type": "string",
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### Get Journal Entry

```
GET /journals/{entry_id}?character_id={character_id}
```

### Create Journal Entry

```
POST /journals
```

Request Body:
```json
{
  "character_id": "string",
  "title": "string",
  "content": "string",
  "entry_type": "string"
}
```

### Direct Edit Journal Entry

```
POST /journals/{entry_id}/direct-edit?character_id={character_id}
```

Request Body:
```json
{
  "updates": {
    "field_name": "new_value"
  },
  "notes": "string"
}
```

## Inventory Endpoints

### List Inventory Items

```
GET /inventory?character_id={character_id}
```

Query Parameters:
- `character_id` (string, required): Character ID
- `limit` (int, default: 100): Maximum number of items to return
- `offset` (int, default: 0): Number of items to skip

Response:
```json
[
  {
    "id": "string",
    "character_id": "string",
    "item_data": {},
    "quantity": 0,
    "created_at": "string",
    "updated_at": "string"
  }
]
```

### Get Inventory Item

```
GET /inventory/{item_id}?character_id={character_id}
```

### Create Inventory Item

```
POST /inventory
```

Request Body:
```json
{
  "character_id": "string",
  "item_data": {},
  "quantity": 0
}
```

### Update Inventory Item

```
PUT /inventory/{item_id}?character_id={character_id}
```

Request Body:
```json
{
  "item_data": {},
  "quantity": 0
}
```

### Delete Inventory Item

```
DELETE /inventory/{item_id}?character_id={character_id}
```

### Direct Edit Inventory Item

```
POST /inventory/{item_id}/direct-edit?character_id={character_id}
```

Request Body:
```json
{
  "updates": {
    "field_name": "new_value"
  },
  "notes": "string"
}
```

## Evolution Endpoints

These endpoints handle character evolution, leveling, and progression.

### Get Evolution Options

```
GET /evolution/{character_id}/options
```

Response:
```json
{
  "available_classes": [],
  "available_feats": [],
  "available_spells": [],
  "required_choices": []
}
```

### Apply Evolution

```
POST /evolution/{character_id}/apply
```

Request Body:
```json
{
  "evolution_type": "string",
  "choices": {},
  "notes": "string"
}
```

## Antitheticon Endpoints

These endpoints handle the identity deception system.

### List Identities

```
GET /antitheticon/identities?character_id={character_id}
```

### Create Identity

```
POST /antitheticon/identities
```

Request Body:
```json
{
  "character_id": "string",
  "identity_data": {},
  "activation_triggers": [],
  "deactivation_triggers": []
}
```

## Error Handling

The API uses standard HTTP status codes:

- 200: Success
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 500: Internal Server Error

Error Response Format:
```json
{
  "detail": "string"
}
```

or for validation errors:

```json
{
  "detail": [
    {
      "loc": ["field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```
