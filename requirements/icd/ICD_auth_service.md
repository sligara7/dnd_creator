# Auth Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-30

## 1. Interface Overview

### 1.1 Purpose
This document defines the interfaces for the Auth Service, including APIs, events, and integration patterns for authentication, authorization, and security policy management.

### 1.2 Scope
- Authentication API endpoints
- Authorization interfaces
- Security event streams
- Service integrations
- Monitoring interfaces

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Authentication Operations
```http
POST /api/v2/auth/login
POST /api/v2/auth/logout
POST /api/v2/auth/refresh
GET /api/v2/auth/validate
POST /api/v2/auth/mfa/setup
POST /api/v2/auth/mfa/validate
```

#### 2.1.2 User Management
```http
POST /api/v2/users
GET /api/v2/users/{id}
PUT /api/v2/users/{id}
DELETE /api/v2/users/{id}
POST /api/v2/users/{id}/roles
GET /api/v2/users/{id}/permissions
```

#### 2.1.3 Role Management
```http
POST /api/v2/roles
GET /api/v2/roles/{id}
PUT /api/v2/roles/{id}
DELETE /api/v2/roles/{id}
POST /api/v2/roles/{id}/permissions
```

### 2.2 Request/Response Format

#### 2.2.1 Authentication Request
```json
{
  "auth_request": {
    "username": "string",
    "password": "string",
    "mfa_token": "string?",
    "client_id": "string",
    "grant_type": "password|refresh_token"
  }
}
```

#### 2.2.2 Authentication Response
```json
{
  "auth_response": {
    "access_token": "string",
    "refresh_token": "string",
    "token_type": "Bearer",
    "expires_in": "integer",
    "scope": "string"
  }
}
```

## 3. Event Interfaces

### 3.1 Published Events

#### 3.1.1 Authentication Events
```json
{
  "event": "auth.user.authenticated",
  "data": {
    "user_id": "string",
    "timestamp": "datetime",
    "client_id": "string",
    "ip_address": "string"
  }
}
```

#### 3.1.2 Authorization Events
```json
{
  "event": "auth.authorization.decision",
  "data": {
    "user_id": "string",
    "resource": "string",
    "action": "string",
    "decision": "allow|deny",
    "reason": "string"
  }
}
```

### 3.2 Subscribed Events

#### 3.2.1 User Events
```json
{
  "event": "user.profile.updated",
  "data": {
    "user_id": "string",
    "changes": ["array"],
    "timestamp": "datetime"
  }
}
```

#### 3.2.2 System Events
```json
{
  "event": "system.security.policy.updated",
  "data": {
    "policy_id": "string",
    "changes": ["array"],
    "effective_date": "datetime"
  }
}
```

## 4. Service Integration

### 4.1 Character Service Integration
```yaml
integration:
  service: character
  auth_types:
    - character_access:
        roles: ["owner", "viewer", "editor"]
        permissions: ["read", "write", "delete"]
    - character_sharing:
        roles: ["dm", "player"]
        permissions: ["view", "edit"]
```

### 4.2 Campaign Service Integration
```yaml
integration:
  service: campaign
  auth_types:
    - campaign_access:
        roles: ["dm", "player", "observer"]
        permissions: ["manage", "participate", "view"]
    - resource_sharing:
        roles: ["contributor", "viewer"]
        permissions: ["share", "view"]
```

### 4.3 Image Service Integration
```yaml
integration:
  service: image
  auth_types:
    - image_access:
        roles: ["creator", "editor", "viewer"]
        permissions: ["upload", "edit", "view"]
    - gallery_access:
        roles: ["owner", "contributor"]
        permissions: ["manage", "add", "view"]
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_auth import AuthClient

client = AuthClient(
    client_id="service_id",
    client_secret="secret",
    options={
        "mfa_required": True,
        "token_refresh": True
    }
)

# Authentication
token = client.authenticate(username, password)
is_valid = client.validate_token(token)
permissions = client.get_permissions(user_id)

# Authorization
can_access = client.authorize(user_id, resource, action)
roles = client.get_user_roles(user_id)
```

### 5.2 Go Client
```go
package main

import "dnd/auth"

func main() {
    client := auth.NewClient(&auth.Config{
        ClientID: "service_id",
        ClientSecret: "secret",
        Options: auth.Options{
            MFARequired: true,
            TokenRefresh: true,
        },
    })

    // Authentication
    token := client.Authenticate(ctx, username, password)
    isValid := client.ValidateToken(ctx, token)
    permissions := client.GetPermissions(ctx, userID)
}
```

## 6. Security Interface

### 6.1 JWT Format
```json
{
  "jwt_claims": {
    "iss": "auth_service",
    "sub": "user_id",
    "aud": "service_id",
    "exp": "timestamp",
    "iat": "timestamp",
    "auth_time": "timestamp",
    "roles": ["array"],
    "permissions": ["array"],
    "scope": "string"
  }
}
```

### 6.2 Permission Format
```yaml
permissions:
  format: "${resource}:${action}"
  examples:
    - "character:read"
    - "campaign:write"
    - "image:upload"
  wildcards:
    - "character:*"
    - "*:read"
```

## 7. Error Interface

### 7.1 Error Codes
```json
{
  "error_codes": {
    "AUTH_001": "Invalid credentials",
    "AUTH_002": "Token expired",
    "AUTH_003": "Invalid token",
    "AUTH_004": "Insufficient permissions",
    "AUTH_005": "MFA required",
    "AUTH_006": "Account locked",
    "AUTH_007": "Rate limit exceeded"
  }
}
```

### 7.2 Error Responses
```json
{
  "error": {
    "code": "AUTH_001",
    "message": "The provided credentials are invalid",
    "details": {
      "reason": "string",
      "timestamp": "datetime",
      "request_id": "string"
    }
  }
}
```

## 8. Monitoring Interface

### 8.1 Metrics
```yaml
metrics:
  authentication:
    - name: auth_attempts
      type: counter
      labels: [success, failure, mfa]
    - name: auth_latency
      type: histogram
      labels: [operation, client_id]

  authorization:
    - name: auth_decisions
      type: counter
      labels: [allow, deny, error]
    - name: permission_checks
      type: counter
      labels: [resource, action]
```

### 8.2 Health Checks
```http
GET /health/live
GET /health/ready
GET /health/metrics
```

## 9. Configuration Interface

### 9.1 Service Configuration
```yaml
config:
  auth:
    token_lifetime: 900
    refresh_lifetime: 604800
    mfa_enabled: true
    password_policy:
      min_length: 12
      require_special: true
      require_numbers: true
      history: 5

  security:
    rate_limit:
      window: 300
      max_attempts: 5
    session:
      max_concurrent: 5
      absolute_timeout: 86400
```

### 9.2 Integration Configuration
```yaml
integrations:
  character_service:
    roles:
      - name: owner
        permissions: ["read", "write", "delete"]
      - name: viewer
        permissions: ["read"]
    
  campaign_service:
    roles:
      - name: dm
        permissions: ["manage", "read", "write"]
      - name: player
        permissions: ["read", "participate"]
```
