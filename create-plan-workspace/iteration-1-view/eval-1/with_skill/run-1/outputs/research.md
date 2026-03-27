# Research: Audit Log Export Service

## Unknown Resolution

### 1. Backend Language & Framework

**Decision**: Recommend Python 3.10+ with FastAPI for REST API  
**Rationale**:
- FastAPI provides built-in async support for non-blocking export requests
- Strong compatibility with Redis and async job workers (Celery)
- Extensive ORM options for audit log database queries
- Native background task queueing integrations

**Alternatives considered**:
- Node.js/Express: Also viable, but Python more common for data pipeline work
- Django: Feature-rich but heavier for a focused export microservice
- Go: Good performance but less common for compliance automation

### 2. Async Job Queue Technology

**Decision**: Use Celery + Redis for background job processing  
**Rationale**:
- Celery integrates seamlessly with FastAPI/Flask
- Redis provides durable queue with job state tracking
- Requirement states existing Redis queue system already in place
- Celery supports job timeouts, retries, and failure handling to meet <0.5% failure SLA
- Built-in job status queries support progress UI

**Alternatives considered**:
- APScheduler: Works but lacks distributed queue durability
- Huey: Simpler but less feature-complete for SLA requirements

### 3. Storage & Signed URL Strategy

**Decision**: Use cloud object storage (AWS S3 or GCS) with time-limited signed URLs  
**Rationale**:
- Spec requirement: "Signed URLs valid for 24 hours"
- Both S3 and GCS provide native signed URL generation with enforced expiry
- Avoids need to manage temporary file cleanup or serve large files from application
- Spec constraint: "Storage is object storage with signed URLs"

**Alternatives considered**:
- Database BLOB storage: Inefficient for 5M+ record exports
- Local filesystem: Not suitable for distributed systems without shared storage

### 4. CSV/JSON Export Format

**Decision**: Generate exports server-side using pandas + json libraries  
**Rationale**:
- Pandas can efficiently stream large datasets to CSV
- JSON export with selective PII filtering implementable via object mapper
- Both formats can be written to temporary file, then uploaded to object storage
- Avoids sending large payloads through memory

**Alternatives considered**:
- Streaming JSON: Adds complexity, not standard for downloads
- Client-side generation: Cannot scale to 5M records without timeout

### 5. PII Filtering Strategy

**Decision**: Maintain allowlist of exportable audit fields, block PII-sensitive fields by role or explicit exclusion  
**Rationale**:
- Spec constraint: "Must avoid exposing PII fields in exports"
- Audit logs typically contain: timestamp, user_id, action, resource_id, status (safe)
- Audit logs often contain sensitive data: IP addresses, request payloads, user email (must filter)
- Configure exportable columns per actor type (e.g., compliance_admin sees all safe fields only)

**Alternatives considered**:
- Token masking on export: Works but complex to manage
- Role-based column filtering: Simpler and more maintainable

## Design Decisions Locked

1. ✅ Framework: FastAPI with Pydantic for validation
2. ✅ Queue: Celery + Redis (existing system)
3. ✅ Storage: Object store with signed URLs (24hr expiry)
4. ✅ Export formats: CSV (pandas) and JSON (native)
5. ✅ PII filtering: Field-level allowlist by role
6. ✅ Job states: queued → running → completed/failed
7. ✅ Audit trail: Separate audit stream for export requests + downloads (existing audit system)

## Open Items

None blocking implementation.
