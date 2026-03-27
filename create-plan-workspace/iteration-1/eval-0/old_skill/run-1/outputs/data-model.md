# Phase 1: Data Model - Billing Disputes Workflow

**Date**: 2026-03-26

## Entity: Dispute

**Table**: `disputes`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique dispute identifier |
| `invoice_id` | UUID | FK(invoices) | Reference to invoice being disputed |
| `customer_id` | UUID | FK(customers) | Reference to customer initiating dispute |
| `created_by` | UUID | FK(users) | Agent who created dispute |
| `assigned_to` | UUID \| NULL | FK(users) | Manager or agent currently handling |
| `status` | ENUM | open, investigating, waiting_on_customer, resolved, rejected | Current dispute state |
| `reason_code` | VARCHAR | Required | Categorized reason for dispute |
| `notes` | TEXT | | Initial and ongoing notes |
| `manager_override` | BOOLEAN | Default false | Indicates if manager overrode agent decision |
| `override_notes` | TEXT | | Manager's justification for override |
| `created_at` | TIMESTAMP | Server-side | Creation timestamp |
| `updated_at` | TIMESTAMP | Auto-update | Last modification timestamp |
| `resolved_at` | TIMESTAMP | NULL | When dispute was marked resolved/rejected |

**Indexes**:
- UNIQUE(id)
- COMPOSITE(status, created_at DESC) — for list queries
- FK(invoice_id), FK(customer_id), FK(created_by), FK(assigned_to)

**Validations**:
- `reason_code` must be one of: [invoice_error, duplicate_charge, unauthorized, service_quality, other]
- `status` transitions:
  - `open` → `investigating`, `rejected`
  - `investigating` → `waiting_on_customer`, `resolved`, `rejected`
  - `waiting_on_customer` → `investigating`, `resolved`, `rejected`
  - `resolved`, `rejected` → terminal (no further transitions)
- If `manager_override = true`, `status` change requires `override_notes`

---

## Entity: AuditEvent

**Table**: `audit_events` (append-only, no UPDATE/DELETE)

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique audit event ID |
| `dispute_id` | UUID | FK(disputes) NOT NULL | Which dispute this event pertains to |
| `actor_id` | UUID | FK(users) NOT NULL | Who triggered the action |
| `action` | VARCHAR | created, status_changed, assigned, notes_added, override_applied | Action type |
| `old_state` | JSONB | | Previous dispute values (for updates only) |
| `new_state` | JSONB | | New dispute values |
| `reason` | TEXT | | Why this action occurred |
| `created_at` | TIMESTAMP | Server-side, NOT NULL | When action occurred |

**Indexes**:
- PK(id)
- FK(dispute_id) with cluster hint
- (created_at DESC) for chronological audit queries

**Validations**:
- `action` must be from enum above
- `new_state` JSONB must be valid JSON
- Immutable: no UPDATE or DELETE permissions granted to app role

**Trigger**: Before INSERT on disputes table, populate audit_events with initial state

---

## Entity: SLADeadline

**Table**: `sla_deadlines`

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `id` | UUID | PK | Unique deadline event ID |
| `dispute_id` | UUID | FK(disputes) | Reference to dispute |
| `deadline_24h` | TIMESTAMP | NOT NULL | 24-hour warning threshold |
| `deadline_48h` | TIMESTAMP | NOT NULL | 48-hour breach threshold |
| `warned_at` | TIMESTAMP | NULL | When 24h warning was sent (idempotent flag) |
| `breached_at` | TIMESTAMP | NULL | When 48h breach was recorded |
| `status` | ENUM | pending, warned, breached | Current SLA status |

**Indexes**:
- PK(id)
- FK(dispute_id)
- (status, deadline_48h) — for scheduled job queries

**Validations**:
- `deadline_24h` = created_at + 24 hours (calculated on creation)
- `deadline_48h` = created_at + 48 hours (calculated on creation)
- If `status = breached`, dispute should be flagged for escalation

**Scheduled Task**: Every 30 minutes, APScheduler/pg_cron scans sla_deadlines table:
