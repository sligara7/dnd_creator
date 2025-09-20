# Audit Service Documentation Update Plan

## Core Changes Required
- Remove direct API endpoints and replace with Message Hub events
- Move all data persistence to storage service
- Update client libraries for Message Hub integration
- Ensure proper event correlation and tracking via Message Hub
- Update analysis and reporting patterns

## ICD Updates Required

### 1. Remove Direct API Endpoints
1. Replace REST endpoints with event patterns:
   ```markdown
   ## 2. Service Events

   ### 2.1 Audit Event Collection
   ```json
   {
     "type": "audit.event.record",
     "data": {
       "event": {
         "id": "uuid",
         "timestamp": "datetime",
         "service": "string",
         "type": "string",
         "action": "string",
         "actor": {
           "id": "string",
           "type": "user|service|system"
         },
         "target": {
           "id": "string",
           "type": "string"
         },
         "context": {},
         "data": {}
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.2 Audit Query Events
   ```json
   {
     "type": "audit.query.execute",
     "data": {
       "query": {
         "time_range": {
           "start": "timestamp",
           "end": "timestamp"
         },
         "filters": [],
         "aggregations": []
       },
       "correlation_id": "uuid"
     }
   }
   ```

   ### 2.3 Report Generation Events
   ```json
   {
     "type": "audit.report.generate",
     "data": {
       "report": {
         "name": "string",
         "type": "security|compliance|usage",
         "format": "pdf|csv|json",
         "time_range": {},
         "filters": []
       },
       "correlation_id": "uuid"
     }
   }
   ```
   ```

### 2. Update Storage Integration
1. Add storage service schema:
   ```markdown
   ## 3. Storage Integration

   ### 3.1 Event Storage
   ```json
   {
     "operation": "write",
     "database": "audit_db",
     "table": "events",
     "data": {
       "id": "uuid",
       "timestamp": "datetime",
       "service": "string",
       "event_type": "string",
       "action": "string",
       "actor": "jsonb",
       "target": "jsonb",
       "context": "jsonb",
       "data": "jsonb",
       "severity": "string",
       "outcome": "string",
       "retention_policy": "string"
     }
   }
   ```

   ### 3.2 Report Storage
   ```json
   {
     "operation": "write",
     "database": "audit_db",
     "table": "reports",
     "data": {
       "id": "uuid",
       "name": "string",
       "type": "string",
       "format": "string",
       "parameters": "jsonb",
       "generated_at": "datetime",
       "data": "jsonb"
     }
   }
   ```

   ### 3.3 Analysis Storage
   ```json
   {
     "operation": "write",
     "database": "audit_db",
     "table": "analysis",
     "data": {
       "id": "uuid",
       "type": "pattern|anomaly|trend",
       "timestamp": "datetime",
       "parameters": "jsonb",
       "results": "jsonb"
     }
   }
   ```
   ```

### 3. Update Client Libraries
1. Update Python client:
   ```python
   from dnd_audit import AuditClient

   # Initialize with message hub
   client = AuditClient(
       service_id="character_service",
       message_hub=message_hub,  # Message Hub client required
       options={
           "batch_size": 100,
           "flush_interval": "5s"
       }
   )

   # Record audit events
   await client.record_event(
       type="character.created",
       action="create",
       actor_id="user123",
       target_id="char456",
       data={"changes": ["name"]}
   )

   # Query audit events
   results = await client.query_events(
       time_range={"start": "-1h"},
       filters={"service": "character"}
   )
   ```

2. Update Go client:
   ```go
   package main

   import "dnd/audit"

   func main() {
       client := audit.NewClient(&audit.Config{
           ServiceID: "campaign_service",
           MessageHub: messageHub,  # Message Hub client required
           Options: audit.Options{
               BatchSize: 100,
               FlushInterval: "5s",
           },
       })

       // Record audit events
       err := client.RecordEvent(ctx, &audit.Event{
           Type: "campaign.created",
           Action: "create",
           ActorID: "user123",
           TargetID: "camp456",
       })
   }
   ```

## SRD Updates Required

### 1. Update Core Responsibilities
1. Strengthen integration requirements:
   ```markdown
   ### 1. Core Responsibilities

   #### 1.1 Message Hub Integration
   - ALL events via Message Hub
   - Event correlation tracking
   - Event delivery guarantee
   - Event ordering preservation
   - Circuit breaking pattern

   #### 1.2 Storage Integration
   - ALL persistence via storage service
   - Data versioning support
   - Retention policy enforcement
   - Backup coordination
   - Archive management
   ```

### 2. Update Technical Requirements
1. Replace direct storage section:
   ```markdown
   ### Storage Requirements
   - All event data in storage service
   - All report data in storage service
   - All analysis results in storage service
   - Proper data partitioning
   - Retention policy support
   ```

2. Add event processing requirements:
   ```markdown
   ### Event Processing
   - Event latency: < 10ms
   - Batch processing: < 1s
   - Query latency: < 100ms
   - Event correlation required
   - Exactly-once delivery
   ```

### 3. Update Integration Model
1. Revise integration patterns:
   ```markdown
   ## Integration Model

   ### 1. Message Hub Events
   Published Events:
   - audit.event.recorded
   - audit.report.generated
   - audit.analysis.completed
   - audit.alert.triggered

   Subscribed Events:
   - *.service.event
   - *.security.event
   - *.system.event
   - *.user.event

   ### 2. Storage Integration
   ```yaml
   storage:
     schema: audit_db
     tables:
       events:
         ttl: 
           hot: 30d
           warm: 90d
           cold: 365d
         backup: true
         archive: true
       reports:
         ttl: 90d
         backup: true
       analysis:
         ttl: 30d
         backup: false
   ```
   ```

## Implementation Changes Required

### 1. Update Event Collection
```python
# Remove direct endpoints
@app.post("/api/v2/events")  # REMOVE
async def record_event(event: dict):
    pass

# Add event handlers
async def handle_audit_event(event):
    # Store via storage service
    await storage.write(
        "audit_db",
        "events",
        {
            "id": uuid4(),
            "timestamp": datetime.utcnow(),
            **event.data["event"]
        }
    )
    
    # Process for analysis
    analysis_result = await analyze_event(event.data["event"])
    
    if analysis_result.alerts:
        # Publish alert event
        await message_hub.publish(
            "audit.alert.triggered",
            {
                "alert": analysis_result.alerts,
                "correlation_id": event.correlation_id
            }
        )
```

### 2. Update Report Generation
```python
# Remove direct endpoints
@app.post("/api/v2/reports")  # REMOVE
async def generate_report(request: dict):
    pass

# Add event handler
async def handle_report_event(event):
    # Get events via storage service
    events = await storage.read(
        "audit_db",
        "events",
        {
            "timestamp": {
                "between": [
                    event.data["report"]["time_range"]["start"],
                    event.data["report"]["time_range"]["end"]
                ]
            }
        }
    )
    
    # Generate report
    report = await generate_report(
        events,
        event.data["report"]
    )
    
    # Store report
    await storage.write(
        "audit_db",
        "reports",
        {
            "id": uuid4(),
            "generated_at": datetime.utcnow(),
            **report
        }
    )
    
    # Publish completion event
    await message_hub.publish(
        "audit.report.generated",
        {
            "report_id": report.id,
            "correlation_id": event.correlation_id
        }
    )
```

### 3. Update Analysis Processing
```python
# Remove direct endpoints
@app.post("/api/v2/analysis/patterns")  # REMOVE
async def analyze_patterns(request: dict):
    pass

# Add event handler
async def handle_analysis_event(event):
    # Get data via storage service
    events = await storage.read(
        "audit_db",
        "events",
        event.data["query"]
    )
    
    # Perform analysis
    results = await analyze_patterns(
        events,
        event.data["parameters"]
    )
    
    # Store results
    await storage.write(
        "audit_db",
        "analysis",
        {
            "id": uuid4(),
            "timestamp": datetime.utcnow(),
            "type": "pattern",
            "parameters": event.data["parameters"],
            "results": results
        }
    )
    
    # Publish completion event
    await message_hub.publish(
        "audit.analysis.completed",
        {
            "type": "pattern",
            "results": results,
            "correlation_id": event.correlation_id
        }
    )
```