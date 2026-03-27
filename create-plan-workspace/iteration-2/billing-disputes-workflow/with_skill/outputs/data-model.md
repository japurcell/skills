# Data Model: Billing Disputes Workflow

## Entity: Dispute

- Fields:
  - `id` (UUID, PK)
  - `invoice_id` (string, required, indexed)
  - `customer_id` (string, required, indexed)
  - `reason_code` (enum/string, required)
  - `notes` (text, optional)
  - `status` (enum: `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`)
  - `outcome` (enum/string, nullable; set on terminal states)
  - `created_by_user_id` (string, required)
  - `assignee_user_id` (string, nullable, indexed)
  - `manager_override` (boolean, default false)
  - `sla_warn_at` (timestamp, required)
  - `sla_breach_at` (timestamp, required)
  - `sla_state` (enum: `healthy`, `warning`, `breached`)
  - `created_at` (timestamp, required)
  - `updated_at` (timestamp, required)
- Invariants:
  - `status` must be one of the allowed workflow states.
  - `sla_warn_at = created_at + 24h`; `sla_breach_at = created_at + 48h`.
  - Terminal statuses (`resolved`, `rejected`) require an `outcome` value.

## Entity: DisputeComment

- Fields:
  - `id` (UUID, PK)
  - `dispute_id` (UUID, FK -> Dispute.id, indexed)
  - `author_user_id` (string, required)
  - `body` (text, required)
  - `created_at` (timestamp, required)
- Invariants:
  - Comments are append-only.

## Entity: DisputeAssignmentHistory

- Fields:
  - `id` (UUID, PK)
  - `dispute_id` (UUID, FK -> Dispute.id, indexed)
  - `from_user_id` (string, nullable)
  - `to_user_id` (string, required)
  - `changed_by_user_id` (string, required)
  - `changed_at` (timestamp, required)
- Invariants:
  - Every assignment change produces exactly one history row.

## Entity: DisputeEvent (Audit Timeline)

- Fields:
  - `id` (UUID, PK)
  - `dispute_id` (UUID, FK -> Dispute.id, indexed)
  - `event_type` (enum: `created`, `status_changed`, `comment_added`, `assigned`, `manager_override`, `sla_warning`, `sla_breach`, `exported`)
  - `actor_user_id` (string, nullable for system events)
  - `from_status` (enum, nullable)
  - `to_status` (enum, nullable)
  - `metadata` (JSONB, required, default `{}`)
  - `created_at` (timestamp, required)
- Invariants:
  - Append-only (no updates/deletes outside retention policy exceptions approved by compliance).
  - `status_changed` events must include `from_status` and `to_status`.

## Relationships

- `Dispute 1 -> many DisputeComment`
- `Dispute 1 -> many DisputeAssignmentHistory`
- `Dispute 1 -> many DisputeEvent`

## State Transitions

- Allowed standard transitions:
  - `open -> investigating`
  - `open -> rejected`
  - `investigating -> waiting_on_customer`
  - `investigating -> resolved`
  - `investigating -> rejected`
  - `waiting_on_customer -> investigating`
  - `waiting_on_customer -> resolved`
  - `waiting_on_customer -> rejected`
- Manager override:
  - `manager` role may force transition to `resolved` or `rejected` from any non-terminal state.
  - Override action must emit `manager_override` audit event.

## Indexing and Performance Notes

- Required indexes:
  - `disputes(status, assignee_user_id, created_at desc, id desc)`
  - `disputes(customer_id)`
  - `disputes(invoice_id)`
  - `dispute_events(dispute_id, created_at desc)`
- Query strategy:
  - Keyset pagination on `(created_at, id)` for list endpoint.
