# Phase 0 Research: Billing Disputes Workflow

**Date**: 2026-03-26  
**Feature**: Billing Disputes Workflow  
**Purpose**: Resolve technical unknowns and establish design foundations

## Research Questions & Findings

### 1. SLA Timer Implementation
**Unknown**: How to reliably track 24h warning and 48h breach deadlines across service restarts?

**Decision**: Use PostgreSQL scheduled tasks (pg_cron extension) + application-level APScheduler fallback

**Rationale**: 
- PostgreSQL pg_cron is ACID-compliant and survives service restarts
- Scheduled query updates `sla_status` flag on disputes table
- APScheduler provides fallback for local task queues
- Simpler than external queue service (Redis/Kafka) for this scale

**Alternatives Considered**:
- Redis-based TTL: Rejected - requires external infrastructure, not resilient across restarts
- Message queue (RabbitMQ): Rejected - overkill for periodic scanning, adds operational complexity
- Client-side timers: Rejected - unreliable if browser closed

---

### 2. Audit Trail Pattern (Immutable)
**Unknown**: Best practice for immutable audit logs in PostgreSQL?

**Decision**: Separate `audit_events` table with no UPDATE/DELETE permissions; append-only via trigger

**Rationale**:
- PostgreSQL triggers on dispute state changes populate audit_events
- Role-based access control: disputes table has UPDATE, audit_events read-only
- Timestamps are server-side (CURRENT_TIMESTAMP)
- Foreign key to disputes ensures referential integrity

**Alternatives Considered**:
- Event sourcing: Rejected - overkill for billing domain, adds replay complexity
- JSON log in single column: Rejected - loses query performance on audit search
- Bitemporal tables: Rejected - complexity not justified by requirements

---

### 3. Performance Optimization for 50k Disputes
**Unknown**: How to achieve p95 <250ms for listing disputes with 50k records?

**Decision**: Composite index on (status, created_at DESC), pagination with cursor-based nav

**Rationale**:
- Most queries filter by status (requirement 3: 5 statuses)
- CreatedAt DESC supports common "recent disputes first" sorting
- Cursor-based pagination avoids OFFSET scan at high page numbers
- Only fetch essential columns for list view; defer related data to detail endpoint

**Alternatives Considered**:
- Full-text search index: Rejected - not required by spec, adds unnecessary overhead
- Materialized view: Rejected - stale data conflicts with real-time SLA updates
- Redis cache: Rejected - invalidation complexity with audit trail

---

### 4. Role-Based Access Control (Agent vs Manager)
**Unknown**: How to enforce agent/manager permissions in FastAPI?

**Decision**: FastAPI dependency injection with JWT payload role verification + SQLAlchemy row-level filters

**Rationale**:
- Extract role from JWT token in request context
- In dispute_service: agents see only owned disputes, managers see all
- Database-level enforcement via SQL WHERE clauses (defense in depth)
- Supports future audit of "user X accessed dispute Y (manager override)"

**Alternatives Considered**:
- Row-level security (RLS) in PostgreSQL: Rejected - more complex to test, slower than app-level filtering for this scale
- Capability-based tokens: Rejected - JWT role-based simpler for team's existing auth model

---

### 5. CSV Export Implementation
**Unknown**: How to stream large CSV exports without memory bloat (50k+ records)?

**Decision**: FastAPI StreamingResponse with generator pattern; fetch in batches of 1000

**Rationale**:
- Generator yields rows in chunks, avoiding full ResultSet in memory
- HTTP chunked transfer-encoding handles streaming naturally
- Works with existing SQLAlchemy query API
- Browser handles file download automatically

**Alternatives Considered**:
- Load all disputes then CSV: Rejected - 50k records * 50 columns = memory spike
- S3 pre-signed URL: Rejected - adds cloud dependency, spec requires monthly export (batch job acceptable)

---

### 6. Technology Stack Confirmation
**Unknown**: Any additional dependencies needed beyond FastAPI + React?

**Decision**: 
- **Backend**: FastAPI, SQLAlchemy 2.x, alembic (migrations), APScheduler, python-multipart
- **Frontend**: React 18, TypeScript, axios (API client), react-query (caching)
- **Testing**: pytest, pytest-asyncio, unittest.mock (backend); Jest, @testing-library/react (frontend)
- **DevOps**: Docker, docker-compose for local dev

**Rationale**: All proven, minimal-overhead choices; align with team's existing FastAPI + React pattern

---

## Unknowns Resolved: ✅
All technical clarifications addressed. Ready for Phase 1 design.
