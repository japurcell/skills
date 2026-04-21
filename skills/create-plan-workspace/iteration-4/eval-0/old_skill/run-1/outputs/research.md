# Research: Billing Disputes Workflow

## Decision 1: Use a current-state dispute table plus an append-only activity log

- **Decision**: Persist the latest dispute state in `billing_disputes` and record every create/comment/status/assignment/outcome-override event in immutable `dispute_activity` rows.
- **Rationale**: The feature needs fast list/detail reads and an immutable audit trail. PostgreSQL constraints are a good fit for row-level invariants such as required IDs, valid enums, and SLA timestamp ordering, while append-only activity rows preserve the required history without expensive event replay on every list query.
- **Official docs reviewed**:
  - PostgreSQL Documentation — DDL Constraints: https://www.postgresql.org/docs/current/ddl-constraints.html
- **Version/context checked**: PostgreSQL current documentation (`current`, now PostgreSQL 18 docs) covering named `CHECK`/`NOT NULL` constraints and the warning that `CHECK` constraints should not encode cross-row guarantees.
- **Alternatives considered**: Full event sourcing as the sole read model (rejected because list/detail latency and operational complexity are worse for a 50k-record portal); mutable dispute rows with no event ledger (rejected because it fails the immutable audit-trail requirement).

## Decision 2: Optimize hot queries with targeted B-tree indexes and partial indexes on unresolved disputes

- **Decision**: Add B-tree indexes for dispute lookup/filter keys (`status`, `assigned_agent_id`, `customer_id`, `invoice_id`, `created_at`) and partial indexes for unresolved/SLA-monitored rows used by the list view and escalation jobs.
- **Rationale**: PostgreSQL uses indexes to accelerate `WHERE` and join predicates, and partial indexes reduce index size and write overhead when only unresolved disputes are hot. This aligns with the p95 <250ms requirement for list queries at 50k disputes while keeping timeline writes cheap.
- **Official docs reviewed**:
  - PostgreSQL Documentation — Indexes Introduction: https://www.postgresql.org/docs/current/indexes-intro.html
  - PostgreSQL Documentation — Partial Indexes: https://www.postgresql.org/docs/current/indexes-partial.html
- **Version/context checked**: PostgreSQL current documentation for general B-tree index behavior and predicate-matching rules for partial indexes.
- **Alternatives considered**: Full-table scans with pagination only (rejected because they risk missing the p95 target); a separate reporting/materialized view from day one (rejected because the 50k scale does not justify extra synchronization complexity initially).

## Decision 3: Treat the disputes API as an OpenAPI-first FastAPI surface, including the CSV export

- **Decision**: Define the feature contract in OpenAPI 3.1, implement JSON endpoints with FastAPI `response_model` validation/filtering, and document the monthly export endpoint with an explicit `text/csv` response class.
- **Rationale**: FastAPI response models validate and filter output shapes while generating JSON Schema/OpenAPI automatically. FastAPI metadata docs show the framework's OpenAPI support, and the OpenAPI specification remains the team's preferred interoperable interface description. Declaring the CSV response class keeps the export visible in generated API docs instead of returning an undocumented raw response.
- **Official docs reviewed**:
  - FastAPI — Response Model: https://fastapi.tiangolo.com/tutorial/response-model/
  - FastAPI — Metadata and Docs URLs: https://fastapi.tiangolo.com/tutorial/metadata/
  - FastAPI — Custom Response / `response_class`: https://fastapi.tiangolo.com/advanced/custom-response/
  - OpenAPI Specification (latest HTML source of truth): https://spec.openapis.org/oas/latest.html
- **Version/context checked**: FastAPI current docs, including the note that OpenAPI 3.1 support is available since FastAPI 0.99.0; OpenAPI latest spec page (currently version 3.2.0 in the published HTML).
- **Alternatives considered**: Handwritten Markdown endpoint docs (rejected because they drift from implementation); undocumented CSV responses returned directly from handlers (rejected because FastAPI warns those won't be documented in OpenAPI).

## Decision 4: Centralize role enforcement with FastAPI dependencies and service-layer policy checks

- **Decision**: Use FastAPI dependency injection to resolve the current user and enforce `agent`/`manager` permissions in a dedicated disputes policy/service layer.
- **Rationale**: The spec differentiates create, reassign, and override privileges by role. FastAPI's dependency pattern cleanly injects current-user context into handlers, while policy functions in the disputes service prevent authorization logic from being duplicated across route handlers and frontend checks.
- **Official docs reviewed**:
  - FastAPI — Get Current User: https://fastapi.tiangolo.com/tutorial/security/get-current-user/
- **Version/context checked**: FastAPI current security tutorial using `Depends(...)` / `Annotated[...]` for current-user resolution.
- **Alternatives considered**: Inline role checks in each endpoint (rejected because they duplicate logic and are easier to drift); frontend-only role gating (rejected because authorization must be enforced server-side).

## Decision 5: Persist SLA deadlines at creation time and stream monthly CSV output

- **Decision**: Compute `warn_at` and `breach_at` when a dispute is created, derive `sla_state` in reads from the persisted timestamps plus terminal status, and generate monthly CSV output with Python's `csv` module while documenting the response as `text/csv`.
- **Rationale**: Persisted deadlines make SLA queries indexable and deterministic, which matters for dashboard filters and escalation sweeps. Python's standard `csv` module is purpose-built for writing rows, supports dialect control, and documents the `newline=''` requirement for file-like writers; FastAPI's response-class docs keep that export documented. For a monthly user-triggered export, streaming a generated file is simpler than introducing a new async job system in the first increment.
- **Official docs reviewed**:
  - Python 3 Standard Library — `csv`: https://docs.python.org/3/library/csv.html
  - FastAPI — Custom Response / `response_class`: https://fastapi.tiangolo.com/advanced/custom-response/
  - FastAPI — Background Tasks: https://fastapi.tiangolo.com/tutorial/background-tasks/
- **Version/context checked**: Python 3.14 docs for `csv`; FastAPI current docs describing documented response classes and the intended use of `BackgroundTasks` for after-response work.
- **Alternatives considered**: Recomputing deadlines from `created_at` on every query (rejected because it weakens indexing and complicates filtering); introducing a separate job queue for exports in the first increment (rejected because the spec only requires monthly CSV export and FastAPI can serve a documented streaming response without a new infrastructure dependency).

## Decision 6: Keep the frontend feature module typed and render-pure

- **Decision**: Implement the portal UI as a dedicated `features/disputes` React module with typed request/response models, pure render logic, and side effects isolated to hooks/event handlers.
- **Rationale**: The feature needs list/detail/forms/timeline interactions without letting UI state drift from the backend contract. React's guidance requires components and hooks to remain pure during render, and TypeScript's core type system is sufficient to model dispute payloads without falling back to `any`, which keeps the UI aligned with the OpenAPI-defined backend shapes.
- **Official docs reviewed**:
  - React — Components and Hooks must be pure: https://react.dev/reference/rules/components-and-hooks-must-be-pure
  - TypeScript Handbook — Everyday Types: https://www.typescriptlang.org/docs/handbook/2/everyday-types.html
- **Version/context checked**: Current React reference docs for component/hook purity and current TypeScript Handbook guidance for everyday structural typing.
- **Alternatives considered**: Ad hoc shared state mixed directly into page components (rejected because it encourages render-time side effects and weak reuse); broad `any`-typed API objects in the UI (rejected because they weaken contract safety for assignment/transition/export flows).
