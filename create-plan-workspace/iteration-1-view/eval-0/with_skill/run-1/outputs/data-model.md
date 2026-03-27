# Data Model: Billing Disputes Workflow

## Entities

### Dispute

Core entity representing a single payment dispute.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | Auto-generated |
| `invoice_id` | String | NOT NULL, FK → invoices | Links to billing invoice |
| `customer_id` | String | NOT NULL, FK → customers | Dispute initiator's context |
| `reason_code` | Enum | NOT NULL | Closed list: billing_error, duplicate, unauthorized, other |
| `notes` | Text | Nullable | Agent's initial description |
| `status` | Enum | NOT NULL, DEFAULT='open' | See State Machine below |
| `assigned_to` | UUID | Nullable, FK → users | Agent or manager handling dispute |
| `created_by` | UUID | NOT NULL, FK → users | Original creator (agent) |
| `created_at` | Timestamp | NOT NULL | Immutable |
| `updated_at` | Timestamp | NOT NULL | Updated on any change |
| `sla_deadline` | Timestamp | NOT NULL | creation_time + 48 hours |
| `resolved_at` | Timestamp | Nullable | Timestamped when moved to resolved/rejected |
| `outcome` | Enum | Nullable | refund, credit, reject, under_investigation after resolved |

### SLAStatus

Denormalized SLA tracking for efficient querying.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `dispute_id` | UUID | NOT NULL, FK → disputes | |
| `deadline` | Timestamp | NOT NULL | Same as dispute.sla_deadline |
| `warned_at` | Timestamp | Nullable | When 24h warning was issued |
| `breached_at` | Timestamp | Nullable | When 48h deadline passed |
| `status` | Enum | DEFAULT='active' | active, breached, resolved |

### DisputeHistory

Immutable audit log of all state transitions and updates.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `dispute_id` | UUID | NOT NULL, FK → disputes | |
| `action` | Enum | NOT NULL | created, transitioned, assigned, commented, outcome_set |
| `actor_id` | UUID | NOT NULL, FK → users | Who performed action |
| `old_value` | JSON | Nullable | Captured state before change |
| `new_value` | JSON | Nullable | New state after change |
| `reason` | Text | Nullable | Why (e.g., manager override rationale) |
| `metadata` | JSON | Nullable | Additional context (e.g., transition_from, transition_to) |
| `created_at` | Timestamp | NOT NULL | Immutable timestamp |

Indexes:
- `(dispute_id, created_at)` - timeline queries
- `(actor_id, created_at)` - user action history
- `(action, created_at)` - audit queries

### DisputeComment

Activity timeline entries for agent/manager notes.

| Field | Type | Constraints | Notes |
|-------|------|-------------|-------|
| `id` | UUID | PK | |
| `dispute_id` | UUID | NOT NULL, FK → disputes | |
| `author_id` | UUID | NOT NULL, FK → users | |
| `body` | Text | NOT NULL | |
| `created_at` | Timestamp | NOT NULL | |
| `updated_at` | Timestamp | Nullable | Soft-edit tracking |

---

## Relations & Invariants

### State Machine
