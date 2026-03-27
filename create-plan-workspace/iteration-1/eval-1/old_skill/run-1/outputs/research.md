# Research: Audit Log Export Service

## Research Tasks Completed

### 1. CSV/JSON Export Libraries

**Decision**: Use `pandas` for CSV generation, `json` standard library for JSON
**Rationale**: 
- Pandas handles large datasets efficiently with streaming capabilities for 5M+ records
- Built-in standard library JSON avoids additional dependencies
- Both support chunked writing to prevent memory overflow

**Alternatives Considered**:
- `csvwriter` alone - too low-level for 5M row exports
- Third-party JSON libraries (simplejson, orjson) - std library sufficient unless streaming JSON needed
- Arrow/Parquet - overkill for compliance export use case

### 2. Job Queue Implementation with Redis

**Decision**: Use existing Redis + worker service; implement using Redis Streams or RQ (Redis Queue)
**Rationale**:
- Existing system already uses Redis, leverages known infrastructure
- RQ provides job tracking, retry, and state management without new dependencies
- Supports job cancellation (requirement #6) natively

**Alternatives Considered**:
- Celery - more heavyweight, requires separate message broker
- Bull queue - JavaScript/Node only
- Direct Redis pub/sub - would require custom job state tracking

### 3. PII Field Filtering Strategy

**Decision**: Whitelist approach - define allowed fields per log type, redact by default
**Rationale**:
- More secure than blacklist (deny specific fields)
- Compliance-friendly - explicit control over what exports
- Can be centralized in schema validation layer

**Alternatives Considered**:
- Blacklist PII patterns (SSN, email regex) - prone to gaps
- Query-level filtering (SQL WHERE) - less maintainable

### 4. Signed URL Expiration & Security

**Decision**: Use object storage native signed URLs with 24h TTL; validate in API before distributing
**Rationale**:
- Object storage (S3/GCS) provides cryptographically secure URLs natively
- 24h TTL satisfies requirement - longer than typical user session
- Validation ensures permissions match original requester

**Alternatives Considered**:
- JWT-style tokens - duplicates object storage capabilities
- Database-backed URL tracking - unnecessary overhead

### 5. Async Initiation & 500ms Goal

**Decision**: Enqueue job immediately, return job ID before processing starts
**Rationale**:
- Job enqueue to Redis is <10ms operation
- Avoids backend blocking on data scan
- Meets <500ms requirement even with database queries

**Alternatives Considered**:
- Pre-scan data before returning - violates 500ms constraint
- Async/await with timeout - risky, may appear to succeed incorrectly

## Unresolved Clarifications from Spec

✅ All clarifications from spec have been resolved through research above. Technical approach is clear.

## Related Best Practices

- **Async job pattern**: Use queue timestamp + request context for audit trail (req #5)
- **Rate limiting**: Implement per-user export limit (e.g., 3 concurrent) to control resource usage
- **Error handling**: Job failures logged immediately with reason code for troubleshooting
