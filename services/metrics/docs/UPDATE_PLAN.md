# Metrics Service Documentation Update Plan

## Core Changes Required
- Remove direct service scraping configuration
- Route all metrics collection through Message Hub events
- Move persistent data storage to storage service
- Update client libraries to use Message Hub
- Redefine alert and dashboard storage via storage service

## ICD Updates Required

### 1. Update Communication Architecture
1. Remove direct scraping configuration:
   ```diff
   - scrape_configs:
   -   - job_name: 'character_service'
   -     static_configs:
   -       - targets: ['character:8080']
   
   + message_hub:
   +   subscriptions:
   +     - "*.metrics.push"
   +     - "*.metrics.report"
   ```

### 2. Replace Direct API Endpoints
1. Convert REST endpoints to event patterns:
   ```markdown
   ## 2. Service Events

   ### 2.1 Metric Collection Events
   ```json
   {
     "type": "metrics.push",
     "data": {
       "service": "string",
       "timestamp": "datetime",
       "metrics": [{
         "name": "string",
         "type": "counter|gauge|histogram",
         "value": "number",
         "labels": {"key": "value"}
       }],
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.2 Query Events
   ```json
   {
     "type": "metrics.query",
     "data": {
       "query": "string",
       "start": "timestamp",
       "end": "timestamp",
       "step": "duration",
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.3 Alert Events
   ```json
   {
     "type": "alerts.status",
     "data": {
       "alerts": [{
         "name": "string",
         "status": "firing|resolved",
         "labels": {},
         "annotations": {},
         "started_at": "timestamp"
       }],
       "correlation_id": "uuid"
     }
   }
   ```
   ```

### 3. Update Client Libraries
1. Modify Python client for message hub:
   ```python
   from dnd_metrics import MetricsClient

   client = MetricsClient(
       service_id="character_service",
       message_hub=message_hub,  # Message Hub client required
       options={
           "batch_size": 100,
           "push_interval": "10s"
       }
   )

   # Metrics are pushed via Message Hub
   await client.inc_counter(
       "character_created_total",
       labels={"class": "wizard"}
   )

   # Query metrics via Message Hub
   results = await client.query(
       'rate(character_created_total[5m])'
   )
   ```

2. Update Go client:
   ```go
   package main

   import "dnd/metrics"

   func main() {
       client := metrics.NewClient(&metrics.Config{
           ServiceID: "campaign_service",
           MessageHub: messageHub,  // Message Hub client required
           Options: metrics.Options{
               BatchSize: 100,
               PushInterval: "10s",
           },
       })

       // Metrics are pushed via Message Hub
       client.IncCounter("campaign_created_total",
           metrics.Labels{
               "type": "oneshot",
           })
   }
   ```

## SRD Updates Required

### 1. Update Core Principles
1. Add messaging requirements:
   ```markdown
   ## Core Responsibilities

   ### 1. Message Hub Integration
   - All metric collection via events
   - All metric queries via events
   - Alert notifications via events
   - Dashboard updates via events
   - No direct service communication
   ```

### 2. Update Technical Requirements
1. Replace direct storage with storage service:
   ```markdown
   ### Storage Integration
   - All persistent data in storage service
   - Alert data in storage service
   - Dashboard data in storage service
   - Long-term metrics in storage service
   - Metadata in storage service
   ```

2. Add event processing requirements:
   ```markdown
   ### Event Processing
   - Metric event latency: < 5ms
   - Query event latency: < 100ms
   - Alert event latency: < 1s
   - Event correlation required
   - Event ordering preserved
   ```

### 3. Update Integration Model
1. Revise service integration:
   ```markdown
   ## Integration Model

   ### 1. Message Hub Events
   Published Events:
   - metrics.collected
   - metrics.aggregated
   - alert.triggered
   - alert.resolved
   - dashboard.updated

   Subscribed Events:
   - *.metrics.push
   - *.metrics.query
   - *.alert.status
   - *.dashboard.request

   ### 2. Storage Integration
   ```yaml
   storage:
     schema: metrics_db
     tables:
       metadata:
         ttl: none
         backup: true
       alerts:
         ttl: 180d
         backup: true
       dashboards:
         ttl: none
         backup: true
   ```
   ```

### 4. Update Deployment Requirements
1. Remove direct service access:
   ```markdown
   ### Deployment Requirements
   - Message Hub client required
   - Storage service client required
   - No direct service access
   - Event-based communication
   - Proper correlation IDs
   ```

## Implementation Changes Required

### 1. Update Service Configuration
```yaml
service:
  name: metrics_service
  message_hub:
    required: true
    events:
      - "*.metrics.*"
      - "*.alerts.*"
      - "*.dashboards.*"
  storage:
    schema: metrics_db
    tables:
      - metadata
      - alerts
      - dashboards
```

### 2. Update Metric Collection
```python
# Remove direct metric scraping
@app.post("/metrics/push")  # REMOVE
async def push_metrics(request):
    metrics = request.json["metrics"]
    await store_metrics(metrics)

# Add event handlers
async def handle_metrics_push(event):
    metrics = event.data["metrics"]
    service = event.data["service"]
    
    # Store via storage service
    await storage.write(
        "metrics_db",
        "metrics",
        {
            "service": service,
            "metrics": metrics,
            "timestamp": datetime.utcnow()
        }
    )
    
    # Notify about collection
    await message_hub.publish(
        "metrics.collected",
        {
            "service": service,
            "count": len(metrics),
            "correlation_id": event.correlation_id
        }
    )
```

### 3. Update Alert Processing
```python
# Remove direct alert checks
async def check_alerts():  # REMOVE
    for rule in alert_rules:
        if await evaluate_rule(rule):
            await send_alert(rule)

# Add event-based alert processing
async def handle_alert_check(event):
    rules = await storage.read(
        "metrics_db",
        "alert_rules",
        {"active": True}
    )
    
    for rule in rules:
        if await evaluate_rule(rule):
            # Store alert in storage service
            await storage.write(
                "metrics_db",
                "alerts",
                {
                    "rule": rule.name,
                    "status": "firing",
                    "timestamp": datetime.utcnow()
                }
            )
            
            # Publish alert event
            await message_hub.publish(
                "alert.triggered",
                {
                    "rule": rule.name,
                    "severity": rule.severity,
                    "correlation_id": event.correlation_id
                }
            )
```