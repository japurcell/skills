# Research: Audit Log Export Service

## Decision 1: Keep the request path to authorize, validate, persist, and enqueue only

**Decision**
- Accept export requests only after validating filters and `compliance_admin` access, then persist a durable job record and enqueue background work without scanning audit data on the request path.

**Rationale**
- This is the cleanest way to meet the under-500ms initiation target while still returning a stable export identifier and immediate `queued` status.
- It also leaves heavy I/O and serialization work in the existing background-processing model instead of coupling it to the user-facing request path.

**Official docs reviewed**
- Redis `XREADGROUP` command reference — https://redis.io/docs/latest/commands/xreadgroup/
- Redis Streams overview — https://redis.io/docs/latest/develop/data-types/streams/

**Version/context checked**
- Redis documentation current as retrieved during this run; `XREADGROUP` is available since Redis Open Source 5.0.0 and documents consumer-group handoff semantics relevant to queue-backed worker processing.
- The feature spec already mandates an existing Redis + worker system, so the plan keeps request handling separate from worker execution instead of introducing a new queueing substrate.

**Alternatives considered**
- Start export processing inline before responding: rejected because large datasets would violate the 500ms initiation target.
- Fire-and-forget queue publish with no durable application record: rejected because the UI, cancellation flow, and auditability need stable job IDs and queryable state.

## Decision 2: Persist explicit export job and artifact metadata outside the queue

**Decision**
- Store one `ExportJob` row per request plus child `ExportArtifact` rows for generated CSV/JSON files, including lifecycle timestamps, progress counters, heartbeat data, and expiry metadata.

**Rationale**
- Queue state alone is not sufficient for UI status polling, stuck-job operations, or historical compliance traceability.
- Separating durable business state from transient worker-delivery mechanics keeps job reporting stable across worker restarts.

**Official docs reviewed**
- Redis Streams overview — https://redis.io/docs/latest/develop/data-types/streams/
- Amazon S3 presigned URL guidance — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

**Version/context checked**
- Redis streams documentation emphasizes delivery/acknowledgement behavior rather than long-lived business-state queries.
- Current Amazon S3 presigned-URL guidance requires explicit expiration handling and ties URL validity to the credentials used to sign the URL; the plan therefore stores expiry metadata at the application layer.

**Alternatives considered**
- Redis-only transient state: rejected because it weakens traceability and status reporting.
- Object-storage metadata only: rejected because status polling, cancellation, and operational dashboards become awkward and slow.

## Decision 3: Use a reviewed export-field allowlist and emit dual-format artifacts

**Decision**
- Serialize exports from an explicit allowlist of approved audit fields, then generate both CSV and JSON artifacts for each completed job.

**Rationale**
- The spec forbids exposing PII fields, and allowlisting is safer than blacklist-based redaction because newly added source fields stay excluded until explicitly approved.
- Generating both required formats during the worker run avoids on-demand transcoding latency later.

**Official docs reviewed**
- RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files — https://datatracker.ietf.org/doc/html/rfc4180
- RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format — https://datatracker.ietf.org/doc/html/rfc8259

**Version/context checked**
- RFC 4180 registers `text/csv` and documents interoperable header/quoting expectations for CSV output.
- RFC 8259 is the current IETF JSON standard and provides the interoperability baseline for JSON artifact generation.

**Alternatives considered**
- Blacklist-based redaction after reading all source fields: rejected because missed or newly introduced PII fields can leak.
- Generate only one canonical artifact and transcode on demand: rejected because it adds latency and more failure points to the download flow.

## Decision 4: Deliver completed artifacts through time-limited signed URLs

**Decision**
- Store completed CSV/JSON artifacts in object storage and issue signed download URLs only for completed jobs whose `download_expires_at` is still in the future.

**Rationale**
- This directly satisfies the 24-hour download-link requirement while keeping object access time-bounded and auditable.
- It also avoids forcing long-lived application sessions to proxy potentially large downloads.

**Official docs reviewed**
- Amazon S3 presigned URL guidance — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

**Version/context checked**
- Current presigned-URL guidance documents explicit expiration intervals, permission requirements, and the constraint that temporary credentials can shorten effective URL lifetime.
- The plan therefore requires application-visible expiry timestamps and provider-credential checks when issuing links.

**Alternatives considered**
- Permanent object URLs behind obscurity: rejected because they do not meet the explicit 24-hour access-control requirement.
- App-server file proxying only: rejected because it increases backend load for large exports and makes expiry enforcement less transparent.

## Decision 5: Process jobs in bounded worker batches with heartbeats and cooperative cancellation

**Decision**
- Run export generation in bounded chunks inside the existing Redis-backed worker service, update progress after each chunk, record heartbeats, and honor cancel requests between chunk boundaries.

**Rationale**
- Five-million-record exports require bounded memory usage and visible progress for operators.
- Cooperative cancellation is safer than abruptly terminating a worker because it reduces partial-write and inconsistent-state risk.

**Official docs reviewed**
- Redis `XREADGROUP` command reference — https://redis.io/docs/latest/commands/xreadgroup/
- Redis Streams overview — https://redis.io/docs/latest/develop/data-types/streams/
- Redis Streams consumer-group commands index (includes `XAUTOCLAIM`) — https://redis.io/docs/latest/develop/data-types/streams/#consumer-groups

**Version/context checked**
- Redis documentation current as retrieved during this run; consumer-group primitives document claim/acknowledgement patterns and stale-work recovery capabilities relevant to stuck-job handling.
- The plan uses those semantics only as a reference model and keeps the existing worker abstraction authoritative.

**Alternatives considered**
- Materialize all rows in memory before writing files: rejected because it creates unacceptable memory pressure.
- Force-stop worker processes to cancel jobs: rejected because it risks partial artifacts and ambiguous terminal state.

## Decision 6: Define external interfaces with OpenAPI and JSON Schema, while deferring repo-path binding

**Decision**
- Document the admin HTTP interface in OpenAPI and the dedicated audit-stream payload in JSON Schema, but keep concrete product-repository paths and native commands as a follow-up because the application source tree is not present in this benchmark workspace.

**Rationale**
- Contracts are part of feature scope and can be made implementation-ready now.
- Guessing product paths or tool commands would create false precision and violate the workflow rule against inventing repository structure.

**Official docs reviewed**
- OpenAPI Specification latest HTML (`Version 3.2.0`) — https://spec.openapis.org/oas/latest.html
- JSON Schema Draft 2020-12 — https://json-schema.org/draft/2020-12

**Version/context checked**
- The latest OpenAPI specification published in the current HTML source-of-truth is 3.2.0; the contract artifact uses an OpenAPI 3.1-compatible document format to align with widely supported tooling while staying within the current specification family.
- JSON Schema Draft 2020-12 is the current published draft line suitable for the audit-stream event schema.

**Alternatives considered**
- Skip contracts until coding starts: rejected because `/create-tasks` benefits from stable interfaces now.
- Invent backend/frontend directory paths or repo-native commands: rejected because the target product repository is not available in this workspace.

## Unknowns closed

- Technical design unknowns around async execution, durable state, export formats, signed-link behavior, worker progress/cancellation, and interface definition were resolved.
- Remaining open item: bind the documented touchpoints and concrete implementation commands in the real product repository before coding begins.
