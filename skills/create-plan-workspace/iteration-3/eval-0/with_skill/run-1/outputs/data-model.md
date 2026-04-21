# Data Model: Billing Disputes Workflow

## Entity: Dispute

- Purpose: Stores the current authoritative state for each billing dispute.
- Fields:
  - `id` (UUID, primary key)
  - `invoice_id` (string, required, indexed)
  - `customer_id` (string, required, indexed)
  - `reason_code` (string enum/code, required)
  - `notes` (text, optional; initial agent context)
  - `status` (enum: `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`)
  - `current_assignee_user_id` (string, nullable, indexed)
  - `created_by_user_id` (string, required)
  - `manager_override_active` (boolean, required, default `false`)
  - `manager_override_by_user_id` (string, nullable)
  - `resolution_summary` (text, nullable)
  - `sla_warn_at` (timestamptz, required)
  - `sla_breach_at` (timestamptz, required)
  - `sla_state` (enum: `healthy`, `warning`, `breached`)
  - `created_at` (timestamptz, required)
  - `updated_at` (timestamptz, required)
- Validation rules / invariants:
  - `status` must be one of the five spec states.
  - `sla_warn_at = created_at + 24 hours`; `sla_breach_at = created_at + 48 hours`.
  - `sla_breach_at > sla_warn_at > created_at`.
  - `current_assignee_user_id` can be changed only by a manager action.
  - `manager_override_by_user_id` is non-null only when a manager forced an outcome.
  - Terminal statuses (`resolved`, `rejected`) require a non-empty `resolution_summary`.

## Entity: DisputeEvent

- Purpose: Append-only activity timeline covering state transitions, comments, assignments, overrides, SLA milestones, and export actions.
- Fields:
  - `id` (UUID, primary key)
  - `dispute_id` (UUID, foreign key -> `Dispute.id`, indexed)
  - `event_type` (enum: `created`, `status_changed`, `comment_added`, `assignment_changed`, `manager_override`, `sla_warning`, `sla_breach`, `exported`)
  - `actor_user_id` (string, nullable for system-driven events)
  - `actor_role` (enum: `agent`, `manager`, `system`)
  - `from_status` (enum, nullable)
  - `to_status` (enum, nullable)
  - `from_assignee_user_id` (string, nullable)
  - `to_assignee_user_id` (string, nullable)
  - `comment_body` (text, nullable)
  - `metadata` (JSONB, required, default `{}`)
  - `occurred_at` (timestamptz, required)
- Validation rules / invariants:
  - Rows are append-only; updates/deletes are disallowed in normal operation.
  - `comment_added` events require `comment_body`.
  - `status_changed` and `manager_override` events require both `from_status` and `to_status`.
  - `assignment_changed` events require `to_assignee_user_id`.
  - `sla_warning` and `sla_breach` events use `actor_role = system` and a null `actor_user_id`.
  - Timeline rendering sorts by `occurred_at DESC, id DESC`.

## Derived Read Model: DisputeListItem

- Purpose: Optimized API projection for the list endpoint.
- Fields:
  - `id`
  - `invoice_id`
  - `customer_id`
  - `reason_code`
  - `status`
  - `current_assignee_user_id`
  - `sla_state`
  - `sla_warn_at`
  - `sla_breach_at`
  - `created_at`
  - `updated_at`
- Notes:
  - Backed directly by the `Dispute` table.
  - Cursor pagination key is `(created_at, id)`.

## Derived Read Model: MonthlyDisputeOutcomeExportRow

- Purpose: Stable CSV row schema for monthly exports.
- Fields:
  - `month`
  - `dispute_id`
  - `invoice_id`
  - `customer_id`
  - `reason_code`
  - `final_status`
  - `manager_override_active`
  - `current_assignee_user_id`
  - `created_at`
  - `resolved_or_rejected_at`
  - `sla_state`
- Notes:
  - Produced from `Dispute` plus terminal `DisputeEvent` data.
  - Must emit the same column order for every export file.

## Relationships

- `Dispute 1 -> many DisputeEvent`
- `DisputeListItem` is a projection over `Dispute`
- `MonthlyDisputeOutcomeExportRow` is a projection over `Dispute` + terminal `DisputeEvent`

## State Transitions

- Standard transitions:
  - `open -> investigating`
  - `open -> rejected`
  - `investigating -> waiting_on_customer`
  - `investigating -> resolved`
  - `investigating -> rejected`
  - `waiting_on_customer -> investigating`
  - `waiting_on_customer -> resolved`
  - `waiting_on_customer -> rejected`
- Role rules:
  - `agent` can create disputes and execute allowed non-manager transitions.
  - `manager` can change assignee and force a terminal outcome override from any non-terminal state.
- Terminal-state rule:
  - `resolved` and `rejected` are terminal for standard agents.
  - A manager override must emit both a `manager_override` event and a terminal status change on the dispute row.

## Indexing and Performance Notes

- Required indexes:
  - `disputes(status, current_assignee_user_id, created_at DESC, id DESC)`
  - `disputes(invoice_id)`
  - `disputes(customer_id)`
  - `disputes(sla_warn_at)` filtered to active disputes when supported by observed workload
  - `dispute_events(dispute_id, occurred_at DESC, id DESC)`
- Performance assumptions:
  - List filtering stays on dispute-row columns.
  - Timeline rendering is served by the event index.
  - CSV export reads a monthly slice and streams rows rather than buffering the full file in memory.
