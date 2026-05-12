# Research: Billing Disputes Workflow

## 1. Backend feature layout and response modeling

Decision: Implement disputes as a dedicated FastAPI router with request/response schemas and a service/repository boundary; use explicit response models on outward-facing endpoints.

Rationale: FastAPI's larger-application guidance recommends splitting features into routers/modules instead of keeping everything in one file. Its response-model guidance also shows that declared response models validate and filter responses, which protects the API contract and prevents leaking internal fields into dispute detail/list payloads.

Official docs reviewed:
- FastAPI — "Bigger Applications - Multiple Files" — https://fastapi.tiangolo.com/tutorial/bigger-applications/
- FastAPI — "Response Model" — https://fastapi.tiangolo.com/tutorial/response-model/

Version/context checked: FastAPI official docs fetched on 2026-04-21 for the existing Python FastAPI backend named in the spec.

Alternatives considered: Keep dispute endpoints in an existing catch-all router; return ORM/dict payloads without explicit response models.

## 2. Authorization enforcement for `agent` and `manager`

Decision: Centralize role checks in shared FastAPI dependencies that resolve the current user and verify the required role before route logic executes.

Rationale: FastAPI dependencies are explicitly designed for shared logic, authentication, and role requirements. Using a dependency-based guard keeps authorization logic consistent across create, transition, assignment, and override endpoints and avoids relying on frontend gating alone.

Official docs reviewed:
- FastAPI — "Dependencies" — https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI — "Get Current User" — https://fastapi.tiangolo.com/tutorial/security/get-current-user/

Version/context checked: FastAPI official docs fetched on 2026-04-21; plan assumes the existing service already has a current-user/auth dependency that can be extended with dispute-role checks.

Alternatives considered: Inline role checks in every handler; frontend-only role restrictions; separate duplicate authorization helpers per endpoint.

## 3. Contract standard for backend/frontend coordination

Decision: Publish and review a checked-in OpenAPI 3.x contract for the dispute endpoints and keep schema names/operation IDs stable enough for frontend integration and future client generation.

Rationale: The spec explicitly says the team prefers OpenAPI. The OpenAPI Specification defines a language-agnostic HTTP API description that both humans and tooling can consume, while FastAPI response models feed directly into documented schemas.

Official docs reviewed:
- OpenAPI Initiative — "OpenAPI Specification" — https://spec.openapis.org/oas/latest.html
- FastAPI — "Response Model" — https://fastapi.tiangolo.com/tutorial/response-model/

Version/context checked: OpenAPI latest page fetched on 2026-04-21 (current document advertises OAS 3.2.0); plan keeps the contract in OpenAPI 3.x form that fits the FastAPI ecosystem.

Alternatives considered: Rely on ad hoc wiki docs; defer contract authoring until after backend code is complete.

## 4. Persistence model and list-query performance

Decision: Store current dispute state in a `disputes` table and immutable event history in an append-only `dispute_activity` table, with indexes supporting the main list filters and SLA lookups.

Rationale: The feature needs both a fast current-state list view and an immutable audit trail. PostgreSQL's indexing guidance notes that indexes are the main tool for accelerating common `WHERE` and join patterns, so the design should index the dispute status, assignee, and creation-time access paths that the portal will query repeatedly at 50k-row scale.

Official docs reviewed:
- PostgreSQL — "11.1. Introduction to Indexes" — https://www.postgresql.org/docs/current/indexes-intro.html

Version/context checked: PostgreSQL current documentation fetched on 2026-04-21 for the existing Postgres backend named in the spec.

Alternatives considered: Single mutable dispute row with no event table; JSON-only audit history embedded in the dispute row; postpone indexing until after the feature launches.

## 5. Monthly CSV export generation

Decision: Implement the monthly outcome export as a streamed CSV response generated from queried rows using Python's standard `csv` module instead of writing temp files.

Rationale: Python's `csv` module provides standard readers/writers for tabular data and handles dialect/quoting concerns. Streaming the export keeps memory usage bounded for monthly batches and avoids filesystem staging requirements that are unnecessary for a portal download endpoint.

Official docs reviewed:
- Python — "csv — CSV File Reading and Writing" — https://docs.python.org/3/library/csv.html

Version/context checked: CPython 3.14 standard-library docs fetched on 2026-04-21; applies to the Python backend constrained by the spec.

Alternatives considered: Manual string concatenation; database-side file export to server storage; generating and persisting static CSV files before download.

## 6. Frontend dispute page state management

Decision: Keep canonical dispute state on the server and manage only page-level filters, selection, and mutation status in React component state; derive SLA labels and action availability from fetched data instead of storing duplicates.

Rationale: React's state-management guidance stresses avoiding redundant or duplicate state because it leads to stale UI bugs. For disputes, server responses should stay authoritative while the UI derives badges, disable states, and timeline presentation from the returned record.

Official docs reviewed:
- React — "Managing State" — https://react.dev/learn/managing-state

Version/context checked: React learn docs fetched on 2026-04-21 for the existing React + TypeScript frontend identified in the spec.

Alternatives considered: Duplicate computed values across multiple component states; keep all list/detail state in ad hoc globals; precompute every presentation field in the client store.
