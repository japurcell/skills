# Phase 0 Research: Billing Disputes Workflow

## Decision 1: Enforce dispute lifecycle with an explicit transition map

- Decision: Implement backend transition rules for `open`, `investigating`, `waiting_on_customer`, `resolved`, and `rejected` as a service-layer state machine.
- Rationale: The workflow has a small, auditable set of valid states, and service-layer enforcement keeps authorization, validation, and audit logging in one place.
- Alternatives considered:
  - Allow arbitrary status updates: rejected because it weakens workflow consistency and auditability.
  - Enforce transitions only with database triggers: rejected because role checks and domain-specific error messages still belong in application logic.

## Decision 2: Store audit history as append-only dispute activity events

- Decision: Record every create, transition, assignment change, comment, SLA event, and manager override as a new `DisputeActivity` row linked to the dispute.
- Rationale: An append-only activity log satisfies the immutable audit-trail requirement while giving the UI a direct timeline source.
- Alternatives considered:
  - Store only the latest dispute snapshot: rejected because it loses historical traceability.
  - Keep the timeline as a mutable JSON blob on the dispute row: rejected because it is hard to query, index, and protect against mutation.

## Decision 3: Persist SLA deadlines at creation time and derive live SLA state from indexed timestamps

- Decision: Calculate `sla_warn_at` (`created_at + 24h`) and `sla_breach_at` (`created_at + 48h`) when the dispute is created, then expose live SLA state in list/detail responses.
- Rationale: Persisted deadlines support fast filters/sorts for the 50k-record list endpoint and keep SLA evaluation deterministic.
- Alternatives considered:
  - Recompute deadlines on every read: rejected because repeated timestamp math increases list-query cost.
  - Use only a periodic batch to mark breaches: rejected because agents need up-to-date warning/breach visibility during the day.

## Decision 4: Separate role powers by action and log manager overrides explicitly

- Decision: `agent` users can create disputes, comment, and execute non-override transitions allowed by policy; `manager` users can reassign disputes and apply explicit outcome overrides that generate dedicated audit events.
- Rationale: This matches the requirements and preserves a clean governance boundary between routine handling and supervisory intervention.
- Alternatives considered:
  - Give both roles the same mutation powers: rejected because it blurs accountability.
  - Model overrides as silent edits to resolved disputes: rejected because it would hide a critical supervisory action.

## Decision 5: Use an OpenAPI-first contract for dispute APIs and CSV export

- Decision: Define dispute list/detail/create/transition/assignment/export interfaces in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/contracts/openapi-disputes.yaml` before implementation.
- Rationale: The spec explicitly prefers OpenAPI, and a contract-first artifact reduces backend/frontend drift while clarifying response shapes early.
- Alternatives considered:
  - Rely on code-first documentation generation: rejected because it delays agreement on payloads and error semantics.
  - Document the API informally in prose only: rejected because it is too ambiguous for client integration.

## Decision 6: Optimize list performance with indexed filters, stable pagination, and summarized timeline reads

- Decision: Index disputes by status, assignee, created timestamp, and SLA deadlines; use stable pagination on `created_at, id`; fetch timeline entries via a separate indexed query on `dispute_id, created_at`.
- Rationale: This keeps the main list endpoint under the required p95 budget while preserving full detail in the dispute view.
- Alternatives considered:
  - Join the full activity timeline into every list response: rejected because it adds unnecessary query cost.
  - Depend on offset-only pagination at high page numbers: rejected because it degrades as data volume grows.

## Decision 7: Validate at backend, contract, and UI layers without introducing net-new tooling

- Decision: Cover transition rules, authorization, audit immutability, SLA deadlines, and CSV exports with backend `pytest` suites, then exercise list/detail/action flows in the existing React test runner used by the implementation repository.
- Rationale: The spec already provides the backend/frontend stack, and the benchmark workspace instructions prohibit inventing a repo-wide runner that does not exist.
- Alternatives considered:
  - Use end-to-end tests only: rejected because failures would be slower and less localized.
  - Add a new benchmark-specific test tool: rejected because it would not reflect the target product repository.

## Decision 8: Export monthly outcomes through a dedicated CSV endpoint keyed by month

- Decision: Expose a monthly outcomes export endpoint that accepts `month=YYYY-MM` and streams a CSV of disputes resolved or rejected in that month.
- Rationale: Operations reporting is a first-class requirement, and a dedicated endpoint avoids client-side reassembly of paginated results.
- Alternatives considered:
  - Build CSV exports on the client from list responses: rejected because it is slower and risks inconsistent snapshots.
  - Pre-generate only static monthly files: rejected because support operations need reruns after data corrections.

## Unknowns Closed

All plan-blocking technical unknowns were resolved for this planning package. Remaining implementation-specific details, such as the exact frontend test command in the target billing portal repository, are non-blocking and can be bound during execution without changing the architecture described here.
