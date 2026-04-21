# Research: Billing Disputes Workflow

## Decision 1: Keep the API contract OpenAPI-first and aligned to FastAPI's generated schema

- Decision: Define the disputes service contract as an OpenAPI 3.1 artifact with explicit operations for list, create, detail, transition, assignment, and monthly export, and implement JSON responses with FastAPI/Pydantic response models so the runtime schema and contract stay aligned.
- Rationale: FastAPI documents that `response_model` validates, filters, and documents returned data, and that the framework's OpenAPI generation defaults to version 3.1.0. Using the generated schema as the source of truth supports contract testing and frontend integration without hand-maintained drift.
- Official docs reviewed:
  - FastAPI, "Response Model" — https://fastapi.tiangolo.com/tutorial/response-model/
  - FastAPI, "Extending OpenAPI" — https://fastapi.tiangolo.com/how-to/extending-openapi/
  - OpenAPI Specification latest HTML — https://spec.openapis.org/oas/latest.html
- Version/context checked: FastAPI docs current as of 2026-04-21 state the default generated schema uses OpenAPI 3.1.0; the latest OAS HTML identifies version 3.2.0, so the contract artifact should remain 3.1.0 until the target FastAPI runtime formally upgrades.
- Alternatives considered:
  - Markdown-only endpoint notes: rejected because they are not machine-checkable.
  - Jumping ahead to OpenAPI 3.2.0 in the artifact: rejected because it would no longer mirror the framework's generated output.
  - GraphQL migration: rejected as out of scope.

## Decision 2: Use a mutable dispute summary row plus append-only dispute events for the audit trail

- Decision: Store current workflow state on a `disputes` table and capture every state transition, comment, assignment change, manager override, and SLA milestone in an append-only `dispute_events` table.
- Rationale: PostgreSQL constraints and foreign keys provide durable enforcement for required fields and state invariants on the current row, while an append-only event log satisfies the immutable audit-trail requirement and gives the frontend a single ordered timeline source.
- Official docs reviewed:
  - PostgreSQL, "5.5. Constraints" — https://www.postgresql.org/docs/current/ddl-constraints.html
- Version/context checked: PostgreSQL current documentation as of 2026-04-21; the design relies on named `CHECK`, `NOT NULL`, and foreign-key constraints that are stable core features.
- Alternatives considered:
  - Only storing a mutable dispute row with `updated_at`: rejected because historical actions would be lost.
  - Full event sourcing for the aggregate: rejected because it adds unnecessary reconstruction complexity for this scope.

## Decision 3: Meet the list latency target with ordered keyset pagination and targeted indexes

- Decision: Serve dispute lists in deterministic `created_at DESC, id DESC` order, expose an opaque cursor based on that pair, and index the main filters with a composite list index plus point-lookup indexes for invoice and customer IDs. Add a partial index for active disputes if explain plans show that open/in-flight statuses dominate operational traffic.
- Rationale: PostgreSQL documents that `LIMIT/OFFSET` results are unstable without a unique `ORDER BY`, and that large offsets remain inefficient because skipped rows still have to be computed. Composite and partial indexes keep common list queries predictable at the 50k-row scale.
- Official docs reviewed:
  - PostgreSQL, "11.1. Introduction" — https://www.postgresql.org/docs/current/indexes-intro.html
  - PostgreSQL, "7.6. LIMIT and OFFSET" — https://www.postgresql.org/docs/current/queries-limit.html
  - PostgreSQL, "11.8. Partial Indexes" — https://www.postgresql.org/docs/current/indexes-partial.html
  - PostgreSQL, "CREATE INDEX" — https://www.postgresql.org/docs/current/sql-createindex.html
- Version/context checked: PostgreSQL current documentation as of 2026-04-21.
- Alternatives considered:
  - Offset pagination only: rejected because deep pages degrade and ordering is less robust.
  - A materialized-view read model from day one: deferred unless profiling shows base-table queries cannot hit the p95 target.
  - Unindexed scans on 50k rows: rejected against the p95 requirement.

## Decision 4: Generate the monthly export as streamed RFC 4180 CSV with documented `text/csv`

- Decision: Implement the monthly export as a FastAPI endpoint that streams CSV rows produced by Python's `csv.DictWriter`, uses a documented CSV response class/media type, emits a header row, and keeps a fixed column set for downstream finance tooling.
- Rationale: Python's standard `csv` module already handles CSV dialect/quoting concerns, RFC 4180 defines the common CSV format and MIME type `text/csv`, and FastAPI documents that `response_class` is how response media types are surfaced in generated OpenAPI.
- Official docs reviewed:
  - Python Standard Library, `csv` — https://docs.python.org/3/library/csv.html
  - RFC 4180, "Common Format and MIME Type for Comma-Separated Values (CSV) Files" — https://www.rfc-editor.org/rfc/rfc4180.txt
  - FastAPI, "Custom Response" — https://fastapi.tiangolo.com/advanced/custom-response/
- Version/context checked: Python docs current page references CPython 3.14 docs as of 2026-04-21; RFC 4180 remains the registered CSV MIME/type reference; FastAPI custom-response docs are current as of this run.
- Alternatives considered:
  - Ad hoc string concatenation: rejected because quoting/newline behavior becomes fragile.
  - Direct database exports for agents to run manually: rejected because it bypasses application authorization and repeatability.
  - Async export jobs only: deferred unless real monthly volumes exceed acceptable synchronous streaming time.

## Decision 5: Keep the frontend pure and strongly typed with shared dispute status unions

- Decision: Build the disputes UI from pure React components and hooks, keep side effects in event handlers/effects, and model dispute statuses, SLA state, and role-sensitive actions with explicit TypeScript string-literal unions plus narrowing/type guards instead of `any`.
- Rationale: React's official rules require purity and no non-local mutation during render, and TypeScript's handbook emphasizes specific primitive/collection types and narrowing as the path to reliable type safety. This keeps agent/manager action gates and status badges consistent across list and detail screens.
- Official docs reviewed:
  - React, "Components and Hooks must be pure" — https://react.dev/reference/rules/components-and-hooks-must-be-pure
  - TypeScript Handbook, "Everyday Types" — https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
  - TypeScript Handbook, "Narrowing" — https://www.typescriptlang.org/docs/handbook/2/narrowing.html
- Version/context checked: React and TypeScript documentation current as of 2026-04-21.
- Alternatives considered:
  - Unstructured JSON and `any` types: rejected because role/action drift becomes likely.
  - Triggering API writes during render: rejected because it violates React's purity model.

## Decision 6: Persist SLA deadlines at creation and use the existing scheduler/worker platform to emit due events

- Decision: Calculate `sla_warn_at` and `sla_breach_at` when a dispute is created, store them on the dispute row, and let the existing deployment scheduler/worker platform query due disputes and append `sla_warning` / `sla_breach` events.
- Rationale: Persisted deadlines make SLA status queryable for lists, dashboards, and exports while avoiding per-request recomputation. Keeping the execution mechanism on the application's existing scheduler/worker platform prevents this plan from introducing net-new infrastructure without repository evidence.
- Official docs reviewed:
  - PostgreSQL, "5.5. Constraints" — https://www.postgresql.org/docs/current/ddl-constraints.html
  - PostgreSQL, "11.1. Introduction" — https://www.postgresql.org/docs/current/indexes-intro.html
- Version/context checked: PostgreSQL current documentation as of 2026-04-21.
- Alternatives considered:
  - Computing warning/breach state only when reading a dispute: rejected because alerts and audits would be inconsistent.
  - Creating one external timer per dispute: rejected because operational overhead is too high for initial scope.
  - Introducing a brand-new queue/cron product in the plan: rejected because the target runtime is unspecified.
