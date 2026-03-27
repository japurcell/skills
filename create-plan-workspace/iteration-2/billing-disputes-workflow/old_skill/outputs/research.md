# Phase 0 Research: Billing Disputes Workflow

## Decision 1: Represent dispute progression as explicit state transitions with a strict transition map

- Decision: Use an explicit allowed-transition matrix for `open`, `investigating`, `waiting_on_customer`, `resolved`, and `rejected`, enforced in backend service logic.
- Rationale: Prevents invalid status changes, keeps behavior deterministic, and supports auditability.
- Alternatives considered:
  - Free-form status updates: rejected due to high risk of inconsistent workflow states.
  - DB trigger-only enforcement: rejected because business rules also require role checks and richer error messaging.

## Decision 2: Implement immutable audit trail via append-only activity events

- Decision: Store every state transition, assignment change, and comment as append-only timeline events linked to dispute ID.
- Rationale: Satisfies immutable audit requirement and enables chronological reconstruction of decisions/actions.
- Alternatives considered:
  - Mutable activity rows: rejected because edits/deletes violate immutability.
  - Denormalized JSON blob timeline on dispute row: rejected due to query/performance limitations and poor integrity guarantees.

## Decision 3: Compute SLA warning and breach timestamps at creation and persist both

- Decision: At dispute creation, persist `sla_warn_at` (+24h) and `sla_breach_at` (+48h) plus current SLA state for indexed querying.
- Rationale: Enables efficient list filtering/sorting and low-latency dashboard indicators without repeated runtime math.
- Alternatives considered:
  - Compute SLA at read time only: rejected due to performance overhead for large list queries.
  - Cron-updated derived fields only: rejected because immediate consistency is needed at creation time.

## Decision 4: Use OpenAPI-first contracts for dispute endpoints

- Decision: Define core dispute endpoints in OpenAPI and align backend handlers and frontend client generation/typing to that contract.
- Rationale: Team preference is explicit in the spec; contract-first reduces integration drift.
- Alternatives considered:
  - Code-first docs generation: rejected due to weaker pre-implementation agreement on request/response shapes.

## Decision 5: Role model and authorization behavior

- Decision: `agent` can create disputes and add comments/transitions allowed by policy; `manager` can reassign disputes and override outcomes.
- Rationale: Mirrors requirement boundaries while keeping permissions auditable at action level.
- Alternatives considered:
  - Broad shared permissions: rejected because it weakens governance and can blur escalation authority.

## Decision 6: Resolve testing stack clarification

- Decision: Backend validation must include pytest unit + integration tests, plus contract tests against OpenAPI. Frontend test framework remains repository-specific but must cover list/detail/transition/assignment flows.
- Rationale: Ensures confidence in API correctness and critical UI behavior while accommodating existing frontend test tooling.
- Alternatives considered:
  - Backend-only testing: rejected due to workflow-heavy UI interactions.
  - E2E-only strategy: rejected because slower feedback and less targeted failure diagnosis.

## Decision 7: CSV export strategy for monthly outcomes

- Decision: Add a parameterized endpoint for monthly export (`month=YYYY-MM`) with server-side streaming/chunked generation where needed.
- Rationale: Handles potentially large datasets and supports operations reporting without timeout-prone payload assembly.
- Alternatives considered:
  - Client-side CSV assembly from paginated API data: rejected due to complexity and potential data inconsistency.
  - Full pre-generated monthly files only: rejected because ad hoc reruns and corrections are required.

## Unknowns Closed

All plan-blocking `NEEDS CLARIFICATION` items were resolved to implementation-ready decisions. Remaining implementation detail (exact frontend test framework command) is non-blocking and can be mapped in the target repository CI setup.
