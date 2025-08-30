# Metrics Service - Interface Control Document (ICD)

Version: 1.0
Status: Draft
Last Updated: 2025-08-30

## 1. Interface Overview

### 1.1 Purpose
This document defines the interfaces for the Metrics Service, including metrics collection endpoints, query interfaces, alerting APIs, and integration patterns for monitoring and observability.

### 1.2 Scope
- Metrics collection endpoints
- Query interfaces
- Alert management APIs
- Dashboard interfaces
- Service integrations

## 2. API Interfaces

### 2.1 REST API

#### 2.1.1 Metric Operations
```http
POST /api/v2/metrics/push
GET /api/v2/metrics/query
GET /api/v2/metrics/query_range
POST /api/v2/metrics/rules
GET /api/v2/metrics/targets
```

#### 2.1.2 Alert Operations
```http
GET /api/v2/alerts
POST /api/v2/alerts
GET /api/v2/alerts/{id}
PUT /api/v2/alerts/{id}
DELETE /api/v2/alerts/{id}
GET /api/v2/alerts/status
```

#### 2.1.3 Dashboard Operations
```http
GET /api/v2/dashboards
POST /api/v2/dashboards
GET /api/v2/dashboards/{id}
PUT /api/v2/dashboards/{id}
DELETE /api/v2/dashboards/{id}
```

### 2.2 Query Format

#### 2.2.1 Query Request
```json
{
  "query_request": {
    "query": "string",
    "start": "timestamp",
    "end": "timestamp",
    "step": "duration",
    "timeout": "duration"
  }
}
```

#### 2.2.2 Query Response
```json
{
  "query_response": {
    "status": "success",
    "data": {
      "resultType": "matrix|vector|scalar|string",
      "result": []
    }
  }
}
```

## 3. Metric Interfaces

### 3.1 Service Metrics

#### 3.1.1 HTTP Metrics
```yaml
metrics:
  http_requests_total:
    type: counter
    labels:
      - method
      - path
      - status
    help: "Total HTTP requests processed"

  http_request_duration_seconds:
    type: histogram
    labels:
      - method
      - path
    buckets: [0.1, 0.5, 1, 2.5, 5, 10]
    help: "HTTP request duration in seconds"
```

#### 3.1.2 System Metrics
```yaml
metrics:
  process_cpu_seconds_total:
    type: counter
    help: "Total user and system CPU time spent in seconds"

  process_resident_memory_bytes:
    type: gauge
    help: "Resident memory size in bytes"

  go_goroutines:
    type: gauge
    help: "Number of goroutines that currently exist"
```

### 3.2 Custom Metrics

#### 3.2.1 Business Metrics
```yaml
metrics:
  dnd_characters_created_total:
    type: counter
    labels:
      - class
      - race
    help: "Total number of characters created"

  dnd_campaigns_active:
    type: gauge
    labels:
      - type
      - status
    help: "Number of currently active campaigns"
```

#### 3.2.2 Performance Metrics
```yaml
metrics:
  dnd_api_latency_seconds:
    type: histogram
    labels:
      - operation
      - service
    buckets: [0.01, 0.05, 0.1, 0.5, 1]
    help: "API operation latency in seconds"

  dnd_cache_hits_total:
    type: counter
    labels:
      - cache
      - operation
    help: "Total number of cache hits"
```

## 4. Service Integration

### 4.1 Character Service
```yaml
metrics:
  character_service:
    - name: character_operations_total
      type: counter
      labels: [operation, status]
    - name: character_creation_duration_seconds
      type: histogram
      labels: [class, race]
    - name: active_characters
      type: gauge
      labels: [status, level]
```

### 4.2 Campaign Service
```yaml
metrics:
  campaign_service:
    - name: campaign_operations_total
      type: counter
      labels: [operation, status]
    - name: active_sessions
      type: gauge
      labels: [type, status]
    - name: player_count
      type: gauge
      labels: [campaign_id, status]
```

### 4.3 Image Service
```yaml
metrics:
  image_service:
    - name: image_processing_duration_seconds
      type: histogram
      labels: [operation, format]
    - name: processed_images_total
      type: counter
      labels: [type, status]
    - name: storage_bytes
      type: gauge
      labels: [type, storage]
```

## 5. Client Libraries

### 5.1 Python Client
```python
from dnd_metrics import MetricsClient

client = MetricsClient(
    service="character_service",
    options={
        "push_gateway": "http://metrics:9091",
        "job_name": "character_metrics"
    }
)

# Counter metrics
client.inc_counter("character_created_total", 
    labels={"class": "wizard", "race": "elf"})

# Gauge metrics
client.set_gauge("active_characters",
    value=42,
    labels={"status": "active"})

# Histogram metrics
client.observe_histogram("character_creation_duration",
    value=1.5,
    labels={"class": "wizard"})
```

### 5.2 Go Client
```go
package main

import "dnd/metrics"

func main() {
    client := metrics.NewClient(&metrics.Config{
        Service: "campaign_service",
        Options: metrics.Options{
            PushGateway: "http://metrics:9091",
            JobName:     "campaign_metrics",
        },
    })

    // Counter metrics
    client.IncCounter("campaign_created_total",
        metrics.Labels{
            "type": "oneshot",
            "status": "active",
        })

    // Gauge metrics
    client.SetGauge("active_players",
        42,
        metrics.Labels{
            "campaign_id": "123",
        })
}
```

## 6. Alert Interface

### 6.1 Alert Rules
```yaml
groups:
  - name: service_alerts
    rules:
      - alert: HighErrorRate
        expr: |
          rate(http_requests_total{status=~"5.."}[5m])
          / rate(http_requests_total[5m]) > 0.1
        for: 5m
        labels:
          severity: critical
        annotations:
          summary: High HTTP error rate
          description: Error rate above 10% for 5m

      - alert: ServiceLatencyHigh
        expr: |
          histogram_quantile(0.95,
            rate(http_request_duration_seconds_bucket[5m])) > 2
        for: 5m
        labels:
          severity: warning
        annotations:
          summary: High service latency
          description: 95th percentile latency above 2s
```

### 6.2 Alert Notifications
```yaml
receivers:
  - name: team-slack
    slack_configs:
      - channel: '#alerts'
        title: '{{ template "slack.title" . }}'
        text: '{{ template "slack.text" . }}'

  - name: ops-pagerduty
    pagerduty_configs:
      - routing_key: <secret>
        description: '{{ template "pagerduty.description" . }}'
        severity: '{{ .CommonLabels.severity }}'
```

## 7. Dashboard Interface

### 7.1 Dashboard Definition
```yaml
dashboard:
  title: "Service Overview"
  refresh: "1m"
  panels:
    - title: "Request Rate"
      type: "graph"
      targets:
        - expr: "rate(http_requests_total[5m])"
          legend: "{{method}} {{status}}"

    - title: "Error Rate"
      type: "graph"
      targets:
        - expr: |
            rate(http_requests_total{status=~"5.."}[5m])
            / rate(http_requests_total[5m])
```

### 7.2 Dashboard Variables
```yaml
variables:
  - name: service
    type: query
    query: "label_values(http_requests_total, service)"
  
  - name: instance
    type: query
    query: "label_values(up{service=\"$service\"}, instance)"
```

## 8. Security Interface

### 8.1 Authentication
```yaml
auth:
  type: "bearer"
  roles:
    - metrics_reader
    - metrics_writer
    - alert_manager
  scope: "metrics:read metrics:write"
```

### 8.2 Authorization
```yaml
permissions:
  read:
    - "metrics:read"
    - "alerts:read"
    - "dashboards:read"
  write:
    - "metrics:write"
    - "alerts:write"
    - "dashboards:write"
  admin:
    - "metrics:admin"
    - "alerts:admin"
    - "dashboards:admin"
```

## 9. Configuration Interface

### 9.1 Service Configuration
```yaml
config:
  global:
    scrape_interval: 15s
    evaluation_interval: 15s
    scrape_timeout: 10s

  scrape_configs:
    - job_name: 'character_service'
      static_configs:
        - targets: ['character:8080']
      metrics_path: '/metrics'
      scheme: 'http'

    - job_name: 'campaign_service'
      static_configs:
        - targets: ['campaign:8080']
      metrics_path: '/metrics'
      scheme: 'http'
```

### 9.2 Storage Configuration
```yaml
storage:
  tsdb:
    retention.time: 15d
    retention.size: 512GB
    wal-compression: true
    min-block-duration: 2h
    max-block-duration: 24h
```
