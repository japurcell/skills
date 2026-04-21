# Data Model: Billing Disputes Workflow

## Core entities

### 1. Dispute

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Primary identifier for API/detail routes. |
| `invoice_id` | text | yes | External invoice reference supplied at creation time. |
| `customer_id` | text | yes | External customer reference supplied at creation time. |
| `reason_code` | text/enum | yes | Controlled set of billing dispute reasons. |
| `notes` | text | yes | Initial agent-supplied context; later comments live in activity history. |
| `status` | enum | yes | One of `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`. |
| `assignee_user_id` | UUID/null | no | Current owner; may start null or default to creator per portal policy. |
| `created_by_user_id` | UUID | yes | Existing authenticated agent who opened the dispute. |
| `manager_override_user_id` | UUID/null | no | Set when a manager overrides the final outcome. |
| `created_at` | timestamptz | yes | Immutable creation timestamp; SLA clock origin. |
| `updated_at` | timestamptz | yes | Updated on any state-changing mutation. |
| `resolved_at` | timestamptz/null | no | Timestamp when status enters a terminal state. |
| `sla_warn_at` | timestamptz | yes | `created_at + 24h`; can be materialized or derived for filtering. |
| `sla_breach_at` | timestamptz | yes | `created_at + 48h`; can be materialized or derived for filtering. |
| `last_commented_at` | timestamptz/null | no | Supports sorting or dashboard badges. |

Validation rules:
- Only users with role `agent` may create a dispute.
- `invoice_id`, `customer_id`, `reason_code`, and `notes` are required on creation.
- `status` must always be one of the five spec-defined values.
- `resolved_at` must be null for non-terminal states and populated for `resolved`/`rejected`.
- `manager_override_user_id` is required when a manager changes a final outcome after the original resolution decision.

Indexes/performance-sensitive access paths:
- Composite index on `(status, assignee_user_id, created_at DESC)` for filtered list queries.
- Index on `created_at` (or `sla_breach_at`) for SLA escalation dashboards.
- Supporting indexes on `invoice_id` and `customer_id` if customer service searches by either identifier.

### 2. DisputeActivity

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Primary identifier for timeline events. |
| `dispute_id` | UUID | yes | FK to `Dispute.id`. |
| `actor_user_id` | UUID | yes | User who performed the action. |
| `activity_type` | enum | yes | `created`, `comment_added`, `status_changed`, `assignment_changed`, `outcome_overridden`. |
| `from_status` | enum/null | no | Previous status for transition records. |
| `to_status` | enum/null | no | New status for transition/override records. |
| `from_assignee_user_id` | UUID/null | no | Previous assignee for assignment changes. |
| `to_assignee_user_id` | UUID/null | no | New assignee for assignment changes. |
| `comment` | text/null | no | Free-form note associated with the event. |
| `metadata` | jsonb/null | no | Extra structured detail such as reason-code snapshots or override metadata. |
| `created_at` | timestamptz | yes | Immutable event timestamp. |

Validation rules:
- Every status change, comment, assignment change, and manager override must create a new activity row.
- Activity rows are append-only; updates/deletes are prohibited outside break-glass admin tooling.
- `from_status`/`to_status` are required for status-changing activities.
- `from_assignee_user_id`/`to_assignee_user_id` are required for assignment changes.

### 3. Existing User / Role reference

The billing portal already has authenticated users. This feature depends on an existing user identity model with at least these role values:

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Referenced by `created_by_user_id`, `assignee_user_id`, and `actor_user_id`. |
| `role` | enum | Must distinguish `agent` and `manager`. |
| `display_name` | text | Used in timeline and assignment displays. |

## Relationships

- One `User` creates many `Dispute` records.
- One `User` may currently own many `Dispute` records via `assignee_user_id`.
- One `Dispute` has many `DisputeActivity` rows ordered by `created_at`.
- One `User` authors many `DisputeActivity` rows.

## State transitions

### Status lifecycle

```text
open
├──> investigating
├──> waiting_on_customer
├──> resolved
└──> rejected

investigating
├──> waiting_on_customer
├──> resolved
└──> rejected

waiting_on_customer
├──> investigating
├──> resolved
└──> rejected

resolved <── manager override ──> rejected
```

Transition rules:
- `open` is the initial state at creation.
- `resolved` and `rejected` are terminal for agents.
- Managers may override a terminal outcome, but each override must capture actor, previous outcome, new outcome, and justification in `DisputeActivity`.
- Assignment changes do not change status automatically.
- SLA timers continue from `created_at`; the spec does not define pause semantics while waiting on the customer.

## Derived views and invariants

- Timeline/detail view reads `Dispute` plus ordered `DisputeActivity` rows.
- SLA state is derived from the current time relative to `sla_warn_at` and `sla_breach_at` (`healthy`, `warning`, `breached`).
- Monthly CSV export reads terminal disputes (`resolved`, `rejected`) filtered by resolution month.
- The current dispute row is the source of truth for list views; `DisputeActivity` is the immutable audit trail.
- Every externally visible mutation must be transactionally coupled with an appended activity row so the current state and timeline cannot diverge.
