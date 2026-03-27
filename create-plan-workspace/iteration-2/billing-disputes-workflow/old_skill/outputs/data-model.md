# Data Model: Billing Disputes Workflow

## Entity: Dispute

Purpose: Canonical record for a customer invoice dispute.

Fields:

- `id` (UUID, PK)
- `invoice_id` (string, indexed, required)
- `customer_id` (string, indexed, required)
- `reason_code` (enum/string, required)
- `notes` (text, required on create)
- `status` (enum: `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`)
- `outcome` (nullable enum/string; manager override may set final outcome)
- `assigned_to_user_id` (nullable string/UUID)
- `created_by_user_id` (string/UUID, required)
- `created_at` (timestamp with timezone, immutable)
- `updated_at` (timestamp with timezone)
- `sla_warn_at` (timestamp with timezone, required)
- `sla_breach_at` (timestamp with timezone, required)
- `resolved_at` (nullable timestamp with timezone)

Validation rules:

- `invoice_id`, `customer_id`, `reason_code`, and `notes` are required on creation.
- `status` must follow allowed transition map.
- `resolved_at` is required when status transitions to `resolved` or `rejected`.
- `sla_warn_at = created_at + 24h`; `sla_breach_at = created_at + 48h`.

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
- `resolved` and `rejected` are terminal except manager override action (logged as explicit override event and resulting terminal state).

## Entity: DisputeActivity

Purpose: Immutable audit timeline for dispute actions.

Fields:

- `id` (UUID, PK)
- `dispute_id` (UUID, FK -> Dispute.id, indexed)
- `event_type` (enum: `created`, `status_changed`, `comment_added`, `assignment_changed`, `outcome_overridden`)
- `from_status` (nullable enum)
- `to_status` (nullable enum)
- `from_assignee_user_id` (nullable string/UUID)
- `to_assignee_user_id` (nullable string/UUID)
- `comment_text` (nullable text)
- `actor_user_id` (string/UUID, required)
- `actor_role` (enum: `agent`, `manager`)
- `metadata` (jsonb, optional)
- `created_at` (timestamp with timezone, immutable, indexed)

Validation rules:

- Rows are append-only; update/delete is disallowed at application layer and restricted in DB permissions.
- Required field combinations depend on `event_type` (for example, `status_changed` requires `from_status` and `to_status`).

## Entity: DisputeAssignment (optional normalized history table)

Purpose: Query-friendly assignment history if required beyond timeline events.

Fields:

- `id` (UUID, PK)
- `dispute_id` (UUID, FK)
- `assigned_to_user_id` (string/UUID)
- `assigned_by_user_id` (string/UUID)
- `assigned_at` (timestamp with timezone)
- `unassigned_at` (nullable timestamp with timezone)

Note:

- If this table is omitted, equivalent information must remain fully derivable from `DisputeActivity` events.

## Relationships

- One `Dispute` to many `DisputeActivity` events.
- One `Dispute` to many `DisputeAssignment` records (if table enabled).

## Indexing and Performance Notes

- Index `Dispute(status, created_at)` for dashboard/list access.
- Index `Dispute(sla_breach_at)` and optionally partial index for non-terminal statuses.
- Index `DisputeActivity(dispute_id, created_at)` for timeline retrieval.
- Add pagination key strategy (`created_at`, `id`) to support p95 <250ms at 50k records.
