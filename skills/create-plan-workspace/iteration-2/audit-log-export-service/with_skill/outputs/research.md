# Research: Audit Log Export Service

## Decision 1: Job Metadata and State Management

Decision: Persist export-job metadata in a relational table with explicit state transitions (`queued`, `running`, `failed`, `completed`, `cancelled`) and immutable timestamps.

Rationale: The spec requires asynchronous progress tracking and stuck-job cancellation. Durable metadata supports UI status polling, admin cancel operations, retry analysis, and failure-rate monitoring.

Alternatives considered:

- Redis-only transient state: rejected because state durability and historical analysis are weak.
- Object-storage metadata only: rejected because query/filter operations and status transitions are limited.

## Decision 2: Export Data Safety (PII Exclusion)

Decision: Implement export serialization from an explicit allowlist of safe audit fields instead of blacklist-based filtering.

Rationale: The requirement is strict non-exposure of PII. Allowlisting minimizes accidental leakage when new source fields are added.

Alternatives considered:

- Blacklist redaction: rejected due to regression risk when new PII fields appear.
- Free-form projection per request: rejected because it increases policy complexity and exposure risk.

## Decision 3: File Production and Download Access

Decision: Generate CSV and JSON artifacts per export job and issue signed URLs with hard 24-hour TTL, validated at request time.

Rationale: This directly satisfies dual-format requirement and 24-hour link validity while aligning with existing object storage constraints.

Alternatives considered:

- On-demand generation at download time: rejected because it increases latency and runtime cost.
- Permanent URLs with app-layer auth only: rejected because URL leakage risk is higher.

## Decision 4: API Contract and Authorization Boundaries

Decision: Expose admin-scoped endpoints for create/status/list/cancel/download with role guard `compliance_admin` enforced in middleware and endpoint-level checks.

Rationale: The spec mandates compliance-only access for export actions and a dedicated cancel endpoint for stuck jobs.

Alternatives considered:

- UI-only role checks: rejected because server-side authorization is mandatory.
- Reusing a general export endpoint: rejected because compliance scope requires stricter isolation and auditability.

## Decision 5: Audit Stream Coverage

Decision: Emit dedicated audit stream events for both export request and export download actions, each including actor identity, request context, export ID, and outcome.

Rationale: Requirement 5 demands traceable request and download events in a dedicated stream.

Alternatives considered:

- Log only request event: rejected (download access would be untracked).
- Reuse generic application log stream: rejected (does not satisfy dedicated stream requirement).

## Decision 6: Large Dataset Execution Pattern

Decision: Process source data in chunked/batched reads with streamed serialization writes and periodic heartbeat updates to job metadata.

Rationale: Up to 5 million records requires bounded memory and visible progress while minimizing worker failure risk.

Alternatives considered:

- Single in-memory materialization: rejected due to memory pressure and instability.
- Very small batches (<1k rows): rejected due to overhead and slower completion.

## Decision 7: Unknown Source Paths in Current Workspace

Decision: Keep code-path mapping as a documented pre-implementation step because this workspace contains planning artifacts but not the product source tree.

Rationale: Avoids inventing repository structure while preserving implementation readiness of behavioral and contract decisions.

Alternatives considered:

- Guessing concrete source directories: rejected by workflow rule to avoid inventing structure.
- Blocking all planning output: rejected because functional architecture and contracts can still be fully specified.
