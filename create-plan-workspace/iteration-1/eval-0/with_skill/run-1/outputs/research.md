# Research Phase: Billing Disputes Workflow

## Decisions Made

### 1. Dispute State Machine

**Decision**: Implement explicit state machine with 5 states: `open` → `investigating` → `waiting_on_customer` → `resolved` or `rejected`

**Rationale**: 
- Spec defines these explicit statuses with clear semantics
- Support strict transition rules to prevent invalid states
- Enables SLA tracking per state
- Aligns with common dispute/ticket workflow patterns

**Alternatives considered**:
- Flat status list (rejected for lack of transition safety)
- More granular states like "escalated", "on-hold" (rejected; keep simple per spec)

---

### 2. SLA Enforcement Mechanism

**Decision**: Timer-based alerts with database-backed enforcement:
- Create SLA record at dispute creation with deadline = creation_time + 48h
- Query for breaches at 24h (warn) and 48h (breach)
- Background job scans for breached SLAs every 5 minutes

**Rationale**:
- Avoids complex scheduler overhead
- Data-native approach (SLA state in DB) supports audit trail
- Scanning approach scales to 50k disputes with indexed deadline column
- Meets <250ms p95 lationale; list queries use indexed lookups

**Alternatives considered**:
- Redis timers (rejected; adds external dependency, harder to audit)
- Timed jobs at creation (rejected; doesn't handle async breach resolution)

---

### 3. Audit Trail Implementation

**Decision**: Append-only audit log table with immutable records:
- `dispute_history` table: (dispute_id, action, actor_id, timestamp, old_value, new_value, metadata)
- All state transitions and assignments write to history
- Queries reconstruct current state from last history record

**Rationale**:
- Immutable trail non-negotiable per spec
- Supports compliance/investigation
- Single source of truth for audit purposes
- Efficient reconstruction via indexed lookups

**Alternatives considered**:
- Event sourcing (rejected; overengineering for this scope)
- Soft deletes + audit column (rejected; doesn't capture full state transitions)

---

### 4. API Endpoint Design

**Decision**: RESTful OpenAPI 3.1 contract with endpoints:
- `GET /disputes` - list with pagination, filtering by status/assigned_to/created_date
- `GET /disputes/{id}` - detail view
- `POST /disputes` - create new dispute
- `PATCH /disputes/{id}` - update (reassign, override outcome)
- `POST /disputes/{id}/transition` - explicit state transition
- `GET /disputes/{id}/activity` - timeline of actions
- `GET /disputes/export` - CSV export (monthly, filtered by date range)

**Rationale**:
- Matches spec requirements exactly
- Standard REST patterns for familiarity
- Pagination critical for 50k dispute scale
- Explicit transition endpoint prevents invalid state changes
- Activity endpoint isolates timeline fetch

**Alternatives considered**:
- GraphQL (rejected; spec calls for OpenAPI, team preference documented)
- RPC-style endpoints (rejected; REST alignment with team standards)

---

### 5. Role-Based Access Control (RBAC)

**Decision**: Two roles with explicit permissions:
- `agent`: can create disputes, view all, post comments, request reassignment
- `manager`: can do all agent actions + reassign disputes + override outcome
- Admin (implicit): full access

**Rationale**:
- Exactly matches requirements in spec
- Simple two-tier model avoids permission creep
- Reassignment flow: agent can request, manager must approve
- Override audit trail captures manager + rationale

**Alternatives considered**:
- Fine-grained permissions per action (rejected; spec calls for simple role split)
- Customer-visible roles (rejected; internal tool per spec)

---

### 6. CSV Export Implementation

**Decision**: On-demand monthly export via background task:
- Endpoint accepts month/year, spawns Celery task
- Task queries disputes created in that month
- Generates CSV with: dispute_id, customer_id, invoice_id, reason, status, sla_breach, resolution_date, assigned_agent
- Returns signed download URL valid for 1 hour

**Rationale**:
- Monthly batch export matches typical billing cycle
- Async task prevents blocking API on large datasets
- Signed URL allows stateless download distribution
- Preserves PII control (not streamed to client directly)

**Alternatives considered**:
- Streaming CSV directly (rejected; large datasets may timeout)
- Scheduled hourly exports (rejected; overkill for monthly requirement)

---

### 7. Frontend State Management

**Decision**: Redux Toolkit with RTK Query for API integration:
- Redux store: disputes list, detail, filters, export status
- RTK Query: automatic cache invalidation on mutations
- Local form state for dispute creation/edit

**Rationale**:
- Redux ecosystem standard in existing React codebase
- RTK Query handles loading/error states automatically
- Cache invalidation prevents stale dispute data
- Separates server sync from local UI state clearly

**Alternatives considered**:
- TanStack Query/React Query (rejected; Redux already established)
- Zustand (rejected; overkill for complexity level and existing patterns)

---

### 8. Performance Optimization for 50k Disputes

**Decision**: Multi-layer optimization:
1. **Database**: Composite index on (status, assigned_to, created_at) for list queries
2. **API**: Cursor-based pagination (next_token approach) instead of offset
3. **Frontend**: Virtual scrolling for long lists, debounced filters
4. **Cache**: HTTP ETag for GET detail requests, conditional requests

**Rationale**:
- Composite index prevents full table scans on filtered list queries
- Cursor-based avoids O(n) offset cost for deep pages
- Virtual scrolling keeps DOM trim for 1000+ dispute renders
- ETag caching reduces payload on detail re-fetches

**Alternatives considered**:
- Full-text search (Elasticsearch) (rejected; premature for initial 50k scale)
- Read replica (rejected; single postgres instance adequate with indexing)

---

## Open Clarifications Resolved

| Item | Research | Resolution |
|------|----------|-----------|
| SLA timing | How to enforce 24h warn / 48h breach? | Background scanning job every 5 min with indexed deadline column |
| Export scope | Frequency and format? | On-demand monthly CSV with async task |
| Conflict resolution | What if agent and manager transition simultaneously? | Pessimistic locking on dispute row; first write wins |
| Escalation rules | Mentioned in goals; what triggers them? | Auto-escalate at SLA breach (status → "escalated", notify manager) |
| API versioning | OpenAPI version and strategy? | v1 in path; use header versioning for future compatibility |
