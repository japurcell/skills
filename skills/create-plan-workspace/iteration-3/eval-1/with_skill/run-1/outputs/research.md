# Research: Audit Log Export Service

## Decision 1: Export artifact formats stay standards-compliant and streamable

Decision: Generate exactly two artifacts per successful job: one CSV file using `text/csv` conventions from RFC 4180 and one UTF-8 JSON file that remains RFC 8259 compliant while being written incrementally by the worker.

Rationale: The spec explicitly requires CSV and JSON downloads, while the 5-million-record constraint means the worker cannot depend on full in-memory materialization. A streamed writer can preserve standards compliance and still keep memory bounded.

Official docs reviewed:

- RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files — https://www.rfc-editor.org/rfc/rfc4180.txt
- RFC 8259: The JavaScript Object Notation (JSON) Data Interchange Format — https://www.rfc-editor.org/rfc/rfc8259.txt

Version/context checked: RFC 4180 (October 2005) and RFC 8259 (December 2017) were fetched during this run and used as the authoritative format references.

Alternatives considered:

- NDJSON for the JSON artifact: rejected because the requirement says JSON, and a line-delimited format would need a separate client contract.
- Spreadsheet-native output such as XLSX: rejected because it is not required and would add a new dependency surface.

## Decision 2: Prevent PII leakage with allowlisted serialization and spreadsheet-safe CSV handling

Decision: Serialize exports from a versioned allowlist of approved audit fields and neutralize CSV cells that begin with formula-trigger characters before writing the CSV artifact.

Rationale: The spec forbids PII exposure, so blacklist-style filtering is too brittle when audit schemas evolve. CSV exports are likely to be opened in spreadsheet software, which creates an additional formula-injection risk for user-controlled text fields.

Official docs reviewed:

- OWASP: CSV Injection — https://owasp.org/www-community/attacks/CSV_Injection
- RFC 4180: Common Format and MIME Type for Comma-Separated Values (CSV) Files — https://www.rfc-editor.org/rfc/rfc4180.txt

Version/context checked: The OWASP CSV Injection guidance available on 2026-04-21 and RFC 4180 were reviewed together to set the CSV safety approach.

Alternatives considered:

- Blacklist-based redaction: rejected because newly added sensitive fields could leak before the blacklist is updated.
- Raw CSV quoting only: rejected because it does not reliably prevent spreadsheet formula execution.

## Decision 3: Store object keys, not presigned URLs, and mint 24-hour links on demand

Decision: Persist artifact object keys and metadata only; generate the signed download URL when an authorized user requests a download, with a hard 24-hour expiration and per-format authorization check.

Rationale: Presigned URLs are bearer tokens. Creating them on demand reduces leakage windows, avoids stale URL storage, and still satisfies the 24-hour requirement.

Official docs reviewed:

- Amazon S3 User Guide: Download and upload objects with presigned URLs — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html
- Amazon S3 User Guide: Sharing objects with presigned URLs — https://docs.aws.amazon.com/AmazonS3/latest/userguide/ShareObjectPreSignedURL.html

Version/context checked: Current Amazon S3 User Guide pages fetched on 2026-04-21. They confirm presigned URLs are time-limited bearer tokens and that 24 hours is comfortably inside supported expiration limits.

Alternatives considered:

- Persisting presigned URLs with the export job: rejected because revocation and rotation are harder and stale URLs are easy to mishandle.
- Streaming the artifact directly through the API on every download: rejected because large exports would add avoidable API latency and egress load.

## Decision 4: Keep authoritative job state in durable storage and use Redis only for dispatch/lease behavior

Decision: Queue only the export job identifier in the existing Redis-backed worker system, keep authoritative lifecycle/progress/heartbeat state in durable export-job storage, and use short-lived worker lease or heartbeat semantics for stuck-job detection and cooperative cancellation.

Rationale: The create request must return in under 500ms, which favors asynchronous dispatch. Durable job state is required for status polling, cancellation, download gating, and failure-rate reporting, while Redis expiry semantics are useful for worker liveness signals.

Official docs reviewed:

- Redis command reference: EXPIRE — https://redis.io/docs/latest/commands/expire/
- Redis documentation: A distributed lock pattern with Redis — https://redis.io/docs/latest/develop/clients/patterns/distributed-locks/

Version/context checked: Latest Redis documentation pages fetched on 2026-04-21. The EXPIRE documentation informed TTL-based lease semantics, and the distributed-lock guidance reinforced avoiding unsafe lock assumptions for job coordination.

Alternatives considered:

- Redis-only transient job state: rejected because status history and auditability would be fragile.
- Force-killing workers to cancel stuck jobs: rejected because it risks partial file writes and inconsistent state.

## Decision 5: Use machine-readable contracts for the admin API and dedicated audit stream

Decision: Document the admin export API in OpenAPI 3.1 and the dedicated audit stream payload in JSON Schema Draft 2020-12.

Rationale: `/create-tasks` and downstream implementation both benefit from contracts that can be traced directly to the plan, data model, and quickstart steps. Machine-readable contracts also make it easier to preserve state, security, and validation rules across API and worker implementation.

Official docs reviewed:

- OpenAPI Specification 3.1.0 — https://spec.openapis.org/oas/v3.1.0.html
- JSON Schema Draft 2020-12 overview — https://json-schema.org/draft/2020-12

Version/context checked: OpenAPI 3.1.0 and JSON Schema Draft 2020-12 materials fetched on 2026-04-21.

Alternatives considered:

- Prose-only interface notes: rejected because they are harder to validate and easier to drift from implementation.
- OpenAPI 3.0.x plus ad hoc event JSON: rejected because 3.1 aligns better with modern JSON Schema usage and keeps the contracts consistent.

## Decision 6: Treat downstream source-path binding as a prerequisite, not a blocker

Decision: Keep the planning package implementation-ready at the behavior and contract level, but defer exact file-path mapping to the downstream product repository because that repository is not part of the provided workspace.

Rationale: The skill requires real repository alignment and forbids inventing source layout. The current repository only exposes the skill source and benchmark workspace, so the correct approach is to preserve logical implementation areas here and bind them later.

Official docs reviewed:

- N/A — repository-local structure decision based on the current tree under `/home/adam/dev/personal/skills`

Version/context checked: Repository layout and instructions were read from `/home/adam/dev/personal/skills/AGENTS.md`, `/home/adam/dev/personal/skills/.copilot/copilot-instructions.md`, and `/home/adam/dev/personal/skills/docs/agent-guides/*.md` on 2026-04-21.

Alternatives considered:

- Guessing product-repo directories now: rejected because it would violate the skill rule against inventing structure.
- Blocking the plan entirely: rejected because the required behavior, data model, contracts, and operational guidance can still be specified with high confidence.
