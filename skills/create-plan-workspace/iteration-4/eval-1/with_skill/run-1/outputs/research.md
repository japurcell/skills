# Research: Audit Log Export Service

## Decision 1

Decision: Model export creation as an asynchronous HTTP job resource that returns immediately and is polled for status until artifacts are ready.

Rationale: The spec requires export initiation in under 500ms while supporting datasets up to 5 million records. Returning a job resource and processing the export in a worker keeps the request path fast, gives the UI a stable polling target, and aligns the API contract with asynchronous HTTP semantics.

Official docs reviewed:
- HTTP Semantics (RFC 9110), status 202 Accepted — https://httpwg.org/specs/rfc9110.html#status.202

Version/context checked: RFC 9110 (2022) reviewed on 2026-04-21; spec requires asynchronous exports plus explicit progress states.

Alternatives considered:
- Synchronous export generation in the request path — rejected because large exports would violate the 500ms initiation target.
- Long-lived streaming HTTP response — rejected because it complicates retries, cancellation, and multi-format artifact generation.

## Decision 2

Decision: Use the existing Redis-backed worker system only for dispatch and heartbeat coordination, while storing authoritative export-job metadata in persistent application storage.

Rationale: Queue transport alone is not sufficient for durable progress tracking, retries, cancellation, or admin visibility. A persistent job record supports the required `queued`, `running`, `failed`, and `completed` states, while Redis TTL-backed heartbeats provide an efficient way to detect stalled work without adding new infrastructure.

Official docs reviewed:
- Redis `EXPIRE` command documentation — https://redis.io/docs/latest/commands/expire/

Version/context checked: Redis documentation latest branch reviewed on 2026-04-21; spec states the current queue system is Redis + worker service.

Alternatives considered:
- Keeping all state only inside Redis queue payloads — rejected because it weakens auditability and makes cancellation/status lookups brittle.
- Introducing a new orchestration system — rejected because the spec explicitly constrains the solution to the existing Redis + worker setup.

## Decision 3

Decision: Persist completed artifacts in object storage and expose them through time-limited signed GET URLs that remain valid for 24 hours.

Rationale: Signed URLs satisfy the requirement for temporary download access while keeping large-file delivery out of the application servers. The design should use the product's current object-storage provider API; AWS S3 presigned URL guidance was reviewed as an official reference showing that 24-hour signed access is a supported, standard pattern.

Official docs reviewed:
- Amazon S3 presigned URL user guide — https://docs.aws.amazon.com/AmazonS3/latest/userguide/using-presigned-url.html

Version/context checked: AWS S3 user guide reviewed on 2026-04-21; spec states storage is object storage with signed URLs, but does not name the provider.

Alternatives considered:
- Permanent authenticated download endpoints served by the app — rejected because they increase application load and complicate large-file delivery.
- Emailing export attachments — rejected because file sizes can be large and attachment handling is harder to secure and audit.

## Decision 4

Decision: Generate both CSV and JSON artifacts from a single allowlisted export schema, stream-writing rows so the system never needs the full 5-million-record export in memory.

Rationale: The spec requires both CSV and JSON outputs and forbids exposing PII. RFC 4180 and RFC 8259 provide interoperable format expectations, while a fixed allowlist ensures the export contract is explicit and prevents accidental leakage of sensitive audit-log fields.

Official docs reviewed:
- Common Format and MIME Type for CSV Files (RFC 4180) — https://www.rfc-editor.org/rfc/rfc4180.txt
- The JavaScript Object Notation (JSON) Data Interchange Format (RFC 8259) — https://www.rfc-editor.org/rfc/rfc8259.txt

Version/context checked: RFC 4180 (2005) and RFC 8259 (2017) reviewed on 2026-04-21; spec requires CSV and JSON artifacts and PII exclusion.

Alternatives considered:
- NDJSON instead of standard JSON — rejected because the requirement explicitly says JSON, and consumers likely expect a conventional JSON artifact.
- Consumer-specific custom column sets — rejected because it increases ambiguity and PII leakage risk.

## Decision 5

Decision: Enforce `compliance_admin` authorization on both the UI and every server-side export endpoint, and write dedicated audit-stream events for request, download, cancel, completion, and failure actions.

Rationale: Administrative export flows are high-risk because they expose sensitive security telemetry. Central server-side role checks combined with dedicated audit events provide least-privilege enforcement, traceability, and evidence for compliance reviews.

Official docs reviewed:
- OWASP Authorization Cheat Sheet — https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html
- OWASP Broken Access Control — https://owasp.org/www-community/Broken_Access_Control

Version/context checked: OWASP guidance reviewed on 2026-04-21; spec requires `compliance_admin`-only access and dedicated audit logging for export activity.

Alternatives considered:
- UI-only gating — rejected because it would be vulnerable to direct API access.
- Reusing a broad existing admin role — rejected because the requirement names a dedicated `compliance_admin` role.

## Decision 6

Decision: Keep the public job-state contract limited to `queued`, `running`, `failed`, and `completed`, and represent cancellation as `cancellationRequested=true` followed by terminal `failed` with `failureCode=cancelled_by_admin`.

Rationale: The spec explicitly names four progress states, but it also requires an admin cancellation endpoint. Using a cancellation flag plus a terminal reason preserves the required public state model, lets workers stop safely between batches, and avoids widening the external contract unless product stakeholders explicitly approve it later.

Official docs reviewed:
- HTTP Semantics (RFC 9110), status 202 Accepted — https://httpwg.org/specs/rfc9110.html#status.202
- Redis `EXPIRE` command documentation — https://redis.io/docs/latest/commands/expire/

Version/context checked: Reviewed on 2026-04-21 against the spec's fixed state list and existing Redis worker constraint.

Alternatives considered:
- Adding new public `cancelling` and `cancelled` states — rejected because it changes the required status contract.
- Hard-killing worker processes without state coordination — rejected because it risks partial artifacts and incomplete audit trails.
