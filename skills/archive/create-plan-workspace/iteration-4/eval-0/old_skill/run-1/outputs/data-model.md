# Data Model: Billing Disputes Workflow

## 1. `billing_disputes`

**Purpose**: Current-state read model for list/detail views, assignment, SLA tracking, and export selection.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Primary key |
| `invoice_id` | text | yes | External billing reference; indexed |
| `customer_id` | text | yes | External customer reference; indexed |
| `reason_code` | text | yes | Controlled set managed by billing operations |
| `notes` | text | yes | Initial dispute context from agent |
| `status` | enum/text | yes | `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected` |
| `assigned_agent_id` | text | no | Current owner; manager can change |
| `created_by_user_id` | text | yes | Actor who opened the dispute |
| `resolution_code` | text | no | Required when closing or rejecting |
| `resolution_summary` | text | no | Human-readable outcome detail |
| `manager_override_by` | text | no | Manager user ID when outcome is overridden |
| `manager_override_reason` | text | no | Why a terminal outcome changed |
| `warn_at` | timestamptz | yes | `created_at + 24h` |
| `breach_at` | timestamptz | yes | `created_at + 48h` |
| `resolved_at` | timestamptz | no | Set for terminal resolution/rejection |
| `created_at` | timestamptz | yes | Creation timestamp |
| `updated_at` | timestamptz | yes | Last state mutation |

### Invariants

- `invoice_id`, `customer_id`, `reason_code`, `notes`, `created_by_user_id`, `created_at`, `warn_at`, and `breach_at` are non-null.
- `warn_at < breach_at`.
- `resolved_at` is null unless `status IN ('resolved', 'rejected')`.
- `resolution_code` is required for terminal states.
- `manager_override_reason` is required when a manager changes a terminal outcome.
- `status` changes are always accompanied by a new `dispute_activity` event row.

### Indexing expectations

- B-tree: `status`, `assigned_agent_id`, `customer_id`, `invoice_id`, `created_at DESC`.
- Partial indexes: unresolved disputes (`status IN ('open','investigating','waiting_on_customer')`), and unresolved rows by `breach_at` for SLA sweeps.

## 2. `dispute_activity`

**Purpose**: Immutable audit trail and timeline source.

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `id` | UUID | yes | Primary key |
| `dispute_id` | UUID | yes | FK to `billing_disputes.id` |
| `activity_type` | enum/text | yes | `created`, `comment_added`, `status_changed`, `assignment_changed`, `outcome_overridden` |
| `actor_user_id` | text | yes | User that performed the action |
| `from_status` | enum/text | no | Present for status/outcome changes |
| `to_status` | enum/text | no | Present for status/outcome changes |
| `from_assignee_id` | text | no | Present for assignment changes |
| `to_assignee_id` | text | no | Present for assignment changes |
| `comment` | text | no | Timeline note/comment |
| `metadata` | jsonb | no | Structured details like reason code changes or override details |
| `occurred_at` | timestamptz | yes | Immutable event timestamp |

### Invariants

- Rows are append-only; updates/deletes are disallowed outside admin remediation.
- Every mutation to `billing_disputes` creates exactly one matching `dispute_activity` row in the same transaction.
- `metadata` stores additional structured fields rather than overloading free-text comments.

## 3. Referenced existing entities

### `users`

Existing identity/authorization store used by the portal.

- Must expose user ID and role (`agent` or `manager`) to the disputes service.
- Disputes only store stable user identifiers; user profile details are joined at read time.

### `invoices` / `customers`

Existing billing-domain records referenced by `invoice_id` and `customer_id`.

- Validation should verify referenced IDs exist before dispute creation.
- Export joins can enrich outcomes with invoice/customer attributes if already available cheaply.

## 4. Derived read concepts

### `sla_state`

Computed per response, not persisted as a canonical column:

- `on_track`: current time < `warn_at` and status is unresolved
- `warning`: current time >= `warn_at` and < `breach_at` and status is unresolved
- `breached`: current time >= `breach_at` and status is unresolved
- `stopped`: status is `resolved` or `rejected`

### `can_override_outcome`

Derived authorization flag in the API response:

- `true` only for managers and only when the dispute is already terminal
- Enables the frontend to show override controls without relying on frontend-only authorization

## 5. State transitions

### Standard lifecycle

| From | To | Allowed roles | Notes |
| --- | --- | --- | --- |
| _new_ | `open` | `agent` | Created with initial note and SLA timestamps |
| `open` | `investigating` | `agent`, `manager` | Work has started |
| `open` | `waiting_on_customer` | `agent`, `manager` | Additional customer input required |
| `open` | `resolved` / `rejected` | `agent`, `manager` | Terminal close with outcome |
| `investigating` | `waiting_on_customer` | `agent`, `manager` | Blocked on customer response |
| `waiting_on_customer` | `investigating` | `agent`, `manager` | Customer responded |
| `investigating` / `waiting_on_customer` | `resolved` / `rejected` | `agent`, `manager` | Close the dispute |

### Manager-only terminal override

| From | To | Allowed roles | Notes |
| --- | --- | --- | --- |
| `resolved` | `rejected` | `manager` | Requires `manager_override_reason` and timeline entry |
| `rejected` | `resolved` | `manager` | Requires `manager_override_reason` and timeline entry |

### Assignment lifecycle

- Assignment is nullable at creation time.
- Managers can set or change `assigned_agent_id` while the dispute is unresolved.
- Every assignment change appends an `assignment_changed` activity row.

## 6. Export model

Monthly CSV export reads terminal disputes by resolved month and emits one row per dispute:

| Column | Source |
| --- | --- |
| `dispute_id` | `billing_disputes.id` |
| `invoice_id` | `billing_disputes.invoice_id` |
| `customer_id` | `billing_disputes.customer_id` |
| `reason_code` | `billing_disputes.reason_code` |
| `final_status` | `billing_disputes.status` |
| `resolution_code` | `billing_disputes.resolution_code` |
| `assigned_agent_id` | `billing_disputes.assigned_agent_id` |
| `created_at` | `billing_disputes.created_at` |
| `resolved_at` | `billing_disputes.resolved_at` |
| `manager_override_by` | `billing_disputes.manager_override_by` |
