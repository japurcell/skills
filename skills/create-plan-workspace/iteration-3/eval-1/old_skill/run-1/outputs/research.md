# Research: Audit Log Export Service

## Official docs reviewed

- OpenAPI Specification 3.0.3 — https://spec.openapis.org/oas/v3.0.3
- RFC 4180: Common Format and MIME Type for CSV Files — https://datatracker.ietf.org/doc/html/rfc4180
- RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format — https://datatracker.ietf.org/doc/html/rfc8259
- Amazon S3 presigned URL guidance (used as the reference model for time-limited object-storage downloads) — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

## Version/context checked

- OpenAPI `3.0.3` was chosen for the admin API contract because it is broadly supported by internal tooling and matches the contract-first planning workflow.
- CSV output is planned as `text/csv` with header row and quoted-field handling compatible with RFC 4180.
- JSON output is planned as UTF-8 JSON documents compatible with RFC 8259.
- Signed download links are modeled as provider-issued presigned URLs with explicit expiration metadata; the 24-hour TTL required by the spec is within common object-storage capabilities and must be enforced by the current provider SDK plus credential lifetime checks.

## Decision 1: Keep the request path synchronous only for validation + enqueue

Decision: Accept export requests only after validating filters, role, and export-window rules, then persist a job row and enqueue background work without scanning audit data on the request path.

Rationale: This is the only reliable way to meet the under-500ms initiation target while still returning a durable export identifier and immediate status.

Alternatives considered:

- Begin export processing inline before responding: rejected because large datasets would violate the initiation SLO.
- Skip durable persistence and return queue metadata only: rejected because progress/status and cancellation need stable application IDs.

## Decision 2: Store export-job state in relational metadata with explicit transitions

Decision: Persist one `ExportJob` record per request with explicit lifecycle states `queued`, `running`, `failed`, `completed`, and `cancelled`, plus monotonic progress counters and heartbeat timestamps.

Rationale: The UI, admin cancel endpoint, and operational failure-rate tracking all require durable state that survives worker restarts and can be queried efficiently.

Alternatives considered:

- Redis-only transient state: rejected because it weakens historical traceability and operational reporting.
- Object-storage metadata only: rejected because status polling and cancellation queries become awkward and slow.

## Decision 3: Enforce a PII-safe export allowlist

Decision: Serialize exports from a reviewed allowlist of permitted audit fields rather than a redact-after-read or blacklist model.

Rationale: The spec explicitly forbids exposing PII. Allowlisting is safer because newly added source fields stay excluded until intentionally approved.

Alternatives considered:

- Blacklist-based redaction: rejected because missed or newly added PII fields can leak into exports.
- User-selectable projection fields: rejected because it increases policy complexity and risk.

## Decision 4: Produce two artifacts per successful job and gate download through signed URLs

Decision: Generate one CSV artifact and one JSON artifact for every completed export job, store both in object storage, and return download URLs only for completed jobs whose `download_expires_at` is still in the future.

Rationale: This directly satisfies the dual-format requirement and keeps access time-limited and auditable.

Alternatives considered:

- Generate only one canonical artifact and transcode on demand: rejected because it increases latency and complicates expiry behavior.
- Store files permanently behind app-session auth only: rejected because signed URLs with explicit TTL better fit the storage constraint and reduce dependency on long-lived app sessions.

## Decision 5: Use chunked worker processing with heartbeats and cancellation checks

Decision: Process audit events in bounded batches, stream writes to artifact builders, update `records_processed`/`progress_pct` after each chunk, and check for cancel requests between chunks.

Rationale: Five-million-record exports require bounded memory and visible progress. Cooperative cancellation is safer than abrupt worker termination and supports the stuck-job admin flow.

Alternatives considered:

- Materialize all rows in memory before writing files: rejected due to memory pressure and failure risk.
- Force-stop workers from outside the app to cancel jobs: rejected because it risks partial writes and inconsistent state.

## Decision 6: Scope admin API around create, status, cancel, and download operations

Decision: Expose a focused admin interface with endpoints for create, get status, cancel, and fetch download URLs; enforce `compliance_admin` in server-side authorization for every operation.

Rationale: The spec names those behaviors explicitly, and server-side authorization is required even if the UI hides actions from unauthorized users.

Alternatives considered:

- UI-only role checks: rejected because client checks alone do not secure the system.
- Reuse a generic exports endpoint shared with other features: rejected because compliance exports need dedicated controls and audit semantics.

## Decision 7: Emit dedicated audit-stream events for request, download, cancel, and failure outcomes

Decision: Publish immutable events to a dedicated audit stream for accepted or denied export requests, download-link issuance, explicit cancellations, and terminal failures.

Rationale: Requirement 5 calls for a dedicated audit stream and traceability for both request and download activity. Including cancel/failure outcomes makes operator actions and incidents observable too.

Alternatives considered:

- Log only request events: rejected because download access would be invisible.
- Reuse generic application logs: rejected because that does not satisfy the dedicated-stream requirement.

## Decision 8: Keep product-repository path binding as a follow-up, not a planning blocker

Decision: Document target touchpoints without inventing concrete source directories, then require binding them in the product repository before `/create-tasks` execution.

Rationale: The benchmark workspace contains only planning inputs/outputs, not the actual application tree. The workflow explicitly forbids inventing repository structure.

Alternatives considered:

- Guess product paths from a common web-app layout: rejected because it introduces false precision.
- Stop planning entirely until the product repo is present: rejected because architecture, contracts, and operational decisions can still be made now.

## Unknowns closed

All plan-blocking unknowns were resolved to implementation-ready decisions. The remaining open item is operational, not architectural: bind the documented touchpoints and concrete repo commands in the actual product repository before task decomposition and coding.
