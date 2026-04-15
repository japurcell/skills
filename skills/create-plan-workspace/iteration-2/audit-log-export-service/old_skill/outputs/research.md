# Research: Audit Log Export Service

## Scope of Research

Research focused on unresolved implementation choices from the spec: async job model, file generation strategy for large datasets, security controls for role-based access and signed downloads, cancellation semantics, and PII-safe export shape.

## Decisions

### 1. Job Orchestration Strategy

**Decision**: Use BullMQ on top of existing Redis queue infrastructure with explicit job state mapping (`queued`, `running`, `failed`, `completed`).

**Rationale**:

- Aligns with the existing Redis + worker constraint.
- Supports retries, stalled job detection, progress updates, and cancellation hooks.
- Provides low-latency enqueue operations to keep initiation under 500ms.

**Alternatives considered**:

- Custom Redis list/stream consumer: more maintenance and error-prone state handling.
- External workflow engine: unnecessary operational complexity.

### 2. Export Generation for Up To 5M Rows

**Decision**: Stream records in bounded batches (for example 10k rows/batch) from the audit store and write incrementally to object storage temp objects before finalize.

**Rationale**:

- Bounded memory profile for very large exports.
- Better failure recovery and observability through progress checkpoints.
- Avoids API timeouts by fully decoupling generation from request lifecycle.

**Alternatives considered**:

- In-memory aggregation then write: high memory risk and poor failure behavior.
- Synchronous export endpoint: violates latency and resilience targets.

### 3. CSV and JSON Output Shape

**Decision**: Produce two artifacts per completed job: one CSV and one newline-delimited JSON (NDJSON) object, each with shared canonical field whitelist.

**Rationale**:

- Satisfies required CSV and JSON formats.
- NDJSON streams naturally for large result sets.
- Shared whitelist keeps parity and simplifies validation.

**Alternatives considered**:

- Standard JSON array only: harder to stream at high volume.
- CSV only: does not satisfy requirements.

### 4. PII Exclusion Strategy

**Decision**: Apply allowlist-based schema projection before serialization and enforce via contract tests.

**Rationale**:

- Strong default-deny posture for sensitive fields.
- Deterministic and auditable for compliance review.
- Prevents accidental leakage from schema drift.

**Alternatives considered**:

- Regex-based redaction: misses unknown PII forms.
- Blocklist fields: risky as new fields appear.

### 5. Signed URL and Download Security

**Decision**: Generate per-file signed URLs with 24-hour TTL and require requester ownership + role check on download link issuance.

**Rationale**:

- Meets explicit 24-hour requirement.
- Prevents link issuance to unauthorized users.
- Uses object-storage-native security model.

**Alternatives considered**:

- Long-lived static links: fails security expectations.
- App-proxy downloads only: increases backend bandwidth and latency.

### 6. Cancel Stuck Job Endpoint Behavior

**Decision**: Add admin endpoint that allows cancellation only for `queued` or `running` jobs; terminal states remain immutable.

**Rationale**:

- Clear, predictable state machine.
- Matches requirement for cancelling stuck jobs.
- Simplifies auditability and avoids conflicting transitions.

**Alternatives considered**:

- Hard delete job records: loses audit history.
- Cancel any state: invalidates completed/failed audit trail.

## Resolved Unknowns

All key technical unknowns needed for implementation planning are resolved. No blocking `NEEDS CLARIFICATION` items remain.

## Follow-ups (Non-Blocking)

- Confirm exact object storage provider naming and bucket conventions in environment config.
- Confirm existing admin UI component library to keep visual and form behavior consistent.
- Confirm retention policy for generated export objects beyond URL expiry.
