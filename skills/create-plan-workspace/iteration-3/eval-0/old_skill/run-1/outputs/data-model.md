# Data Model: Billing Disputes Workflow

## Entity: Dispute

Purpose: Canonical workflow record for a customer billing dispute.

Fields:

- `id` (UUID, primary key)
- `invoice_id` (string, required, indexed)
- `customer_id` (string, required, indexed)
- `reason_code` (string/enum, required, constrained to the billing dispute reason catalog)
- `notes` (text, required on create)
- `status` (enum: `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`)
- `assigned_to_user_id` (nullable UUID/string)
- `created_by_user_id` (UUID/string, required)
- `manager_override_outcome` (nullable string/enum)
- `sla_warn_at` (timestamp with timezone, required)
- `sla_breach_at` (timestamp with timezone, required)
- `resolved_at` (nullable timestamp with timezone)
- `created_at` (timestamp with timezone, immutable)
- `updated_at` (timestamp with timezone)

Validation rules and invariants:

- `invoice_id`, `customer_id`, `reason_code`, and `notes` are mandatory when creating a dispute.
- `status` must follow the allowed transition map below.
- `resolved_at` must be set when a dispute enters `resolved` or `rejected`.
- `manager_override_outcome` may be written only by a `manager` action and must emit an audit event.
- `sla_warn_at = created_at + 24h`; `sla_breach_at = created_at + 48h`.
- Terminal states are `resolved` and `rejected`, except for explicit manager override flows that remain terminal while updating the final recorded outcome.

State transitions:

- `open -> investigating`
- `open -> waiting_on_customer`
- `open -> resolved`
- `open -> rejected`
- `investigating -> waiting_on_customer`
- `investigating -> resolved`
- `investigating -> rejected`
- `waiting_on_customer -> investigating`
- `waiting_on_customer -> resolved`
- `waiting_on_customer -> rejected`
- `resolved -> resolved` only for manager outcome override metadata updates logged as dedicated override events
- `rejected -> rejected` only for manager outcome override metadata updates logged as dedicated override events

## Entity: DisputeActivity

Purpose: Immutable timeline entry for every meaningful dispute action.

Fields:

- `id` (UUID, primary key)
- `dispute_id` (UUID, foreign key to `Dispute.id`, indexed)
- `event_type` (enum: `created`, `status_changed`, `comment_added`, `assignment_changed`, `sla_warning`, `sla_breached`, `outcome_overridden`)
- `actor_user_id` (UUID/string, required)
- `actor_role` (enum: `agent`, `manager`, `system`)
- `from_status` (nullable enum)
- `to_status` (nullable enum)
- `from_assignee_user_id` (nullable UUID/string)
- `to_assignee_user_id` (nullable UUID/string)
- `comment_text` (nullable text)
- `metadata` (jsonb, optional)
- `created_at` (timestamp with timezone, immutable, indexed)

Validation rules and invariants:

- Rows are append-only; update and delete paths are disallowed in application code and restricted at the database permission layer.
- `status_changed` events require both `from_status` and `to_status`.
- `assignment_changed` events require either a new assignee or an explicit unassignment marker.
- `comment_added` events require non-empty `comment_text`.
- `outcome_overridden` events require a `manager` actor role and carry previous/new outcome values in `metadata`.

## Entity: MonthlyDisputeOutcomeExport

Purpose: Query/result shape for CSV export of monthly dispute outcomes.

Fields:

- `month` (`YYYY-MM`, request parameter)
- `dispute_id`
- `invoice_id`
- `customer_id`
- `reason_code`
- `final_status`
- `final_outcome` (derived from status + override metadata)
- `assigned_to_user_id`
- `resolved_at`
- `sla_met` (boolean)
- `last_actor_user_id`

Validation rules and invariants:

- Export rows include only disputes finalized in the requested month.
- `sla_met` is `true` when `resolved_at <= sla_breach_at`; otherwise `false`.
- CSV generation must use the same source of truth as dispute detail views to avoid reconciliation drift.

## Relationships

- One `Dispute` has many `DisputeActivity` records.
- One `Dispute` contributes zero or one row to a given `MonthlyDisputeOutcomeExport` request.
- Assignment history is fully derivable from ordered `DisputeActivity` rows; a separate history table is optional only if required for operational reporting.

## Query and indexing notes

- Index `Dispute(status, created_at, id)` for list pagination.
- Index `Dispute(assigned_to_user_id, status)` for manager work queues.
- Index `Dispute(sla_warn_at)` and `Dispute(sla_breach_at)` to support warning/breach filters.
- Index `DisputeActivity(dispute_id, created_at)` for efficient timeline retrieval.
- Use cursor or seek pagination on `created_at, id` rather than deep offsets for the 50k-dispute list target.
