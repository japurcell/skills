# Data Model: Audit Log Export Service

## Overview

The feature centers on a durable export job that is requested from the admin UI, processed asynchronously by a worker, and traced through a dedicated audit stream. External download links are derived from artifact metadata instead of being stored directly.

## Entity: ExportJob

Purpose: Represents a single compliance-admin export request and its lifecycle.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Primary key |
| `requestedByUserId` | string/UUID | Authenticated requesting user |
| `requestedByRole` | string | Must equal `compliance_admin` for accepted jobs |
| `filters` | `ExportFilterSet` | Embedded value object |
| `status` | enum | `queued`, `running`, `failed`, `completed`, `cancelled` |
| `recordsProcessed` | integer | Monotonic counter |
| `recordsExported` | integer | Monotonic counter |
| `progressPct` | integer | 0-100, derived from worker progress |
| `queueJobId` | string nullable | Queue-level identifier if available |
| `workerLeaseKey` | string nullable | Reference to Redis lease/heartbeat entry |
| `heartbeatAt` | datetime nullable | Latest worker heartbeat |
| `failureCode` | string nullable | Stable failure classification |
| `failureReason` | string nullable | Human-readable message |
| `cancelRequestedAt` | datetime nullable | Set when admin cancellation is accepted |
| `startedAt` | datetime nullable | First worker claim time |
| `completedAt` | datetime nullable | Success terminal time |
| `cancelledAt` | datetime nullable | Cancellation terminal time |
| `downloadExpiresAt` | datetime nullable | Equals `completedAt + 24h` on success |
| `safeFieldsetVersion` | string | Version of the allowlisted export schema |
| `createdAt` | datetime | Creation timestamp |
| `updatedAt` | datetime | Last state mutation timestamp |

Validation and invariants:

- `requestedByRole` must be `compliance_admin` for any accepted request.
- `filters.dateFrom <= filters.dateTo`.
- `status = completed` requires two associated artifacts (`csv` and `json`) and a non-null `downloadExpiresAt`.
- `status = cancelled` is terminal and must have `cancelRequestedAt` or an administrative reason.
- `downloadExpiresAt` must never exceed 24 hours after `completedAt`.
- No raw signed URL is stored on the entity; only object keys and derived metadata are persisted.

## Value Object: ExportFilterSet

Purpose: Captures the request filter envelope from the UI/API.

| Field | Type | Notes |
| --- | --- | --- |
| `dateFrom` | date/datetime | Required lower bound |
| `dateTo` | date/datetime | Required upper bound |
| `actorType` | string nullable | Optional filter; constrained to existing actor taxonomy |
| `actionCategory` | string nullable | Optional filter; constrained to existing action taxonomy |

Validation and invariants:

- At least the date range must be present.
- Optional taxonomy fields must map to known application values.
- Filter values are copied into audit events for traceability.

## Entity: ExportArtifact

Purpose: Tracks a single generated file for a completed export.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID | Primary key |
| `exportJobId` | UUID | FK -> `ExportJob.id` |
| `format` | enum | `csv` or `json` |
| `objectKey` | string | Storage key/path |
| `contentType` | string | `text/csv` or `application/json` |
| `byteSize` | integer | Artifact size |
| `checksum` | string nullable | Integrity metadata if available |
| `createdAt` | datetime | Artifact creation timestamp |

Validation and invariants:

- Exactly one artifact per (`exportJobId`, `format`).
- Artifact rows are created only after the worker finishes writing the corresponding object.
- Artifact metadata must reference the same `downloadExpiresAt` window as the parent job.

## Entity: AuditExportEvent

Purpose: Dedicated audit-stream event for request, download, cancellation, and failure traceability.

| Field | Type | Notes |
| --- | --- | --- |
| `eventId` | UUID | Event primary identifier |
| `eventType` | enum | `audit_export.requested`, `audit_export.request_denied`, `audit_export.download_issued`, `audit_export.download_denied`, `audit_export.cancel_requested`, `audit_export.cancelled`, `audit_export.failed`, `audit_export.completed` |
| `occurredAt` | datetime | Event time |
| `actorUserId` | string/UUID | User or service actor |
| `actorRole` | string | Role at event time |
| `exportJobId` | UUID nullable | Required for all events after request validation |
| `result` | enum | `accepted`, `denied`, `success`, `failure` |
| `metadata` | object | Filters, format, IP/user-agent, failure detail, artifact info |

Validation and invariants:

- Every accepted request emits `audit_export.requested`.
- Every denied request emits `audit_export.request_denied` with denial reason.
- Every successful signed-link issuance emits `audit_export.download_issued`.
- Download/audit events must never include filtered-out PII fields.

## Relationships

- One `ExportJob` owns one `ExportFilterSet`.
- One `ExportJob` has many `ExportArtifact` rows; success requires exactly two.
- One `ExportJob` has many `AuditExportEvent` records across its lifecycle.

## Lifecycle / State Transitions

| From | To | Trigger | Guard rails |
| --- | --- | --- | --- |
| `queued` | `running` | Worker claims queued job | Record `startedAt`, initialize heartbeat, emit running/processing telemetry |
| `queued` | `cancelled` | Admin cancels before worker claim | Emit `audit_export.cancel_requested` then terminal cancel event |
| `running` | `completed` | Worker writes both artifacts and metadata successfully | Persist two artifacts, set `downloadExpiresAt`, emit completion event |
| `running` | `failed` | Worker hits unrecoverable extraction/storage error | Persist failure code/reason, emit failure event |
| `running` | `cancelled` | Worker observes cancel request and exits cooperatively | Ensure partial artifacts are cleaned up or ignored |

Terminal states: `completed`, `failed`, `cancelled`.

## Derived rules for implementation

- Status polling reads `ExportJob` and artifact presence only; it must not depend on Redis queue internals.
- Download endpoints validate `status = completed`, artifact existence, role access, and `downloadExpiresAt > now()` before minting a signed URL.
- CSV serialization uses the safe-field allowlist and spreadsheet-safe escaping; JSON serialization uses the same allowlist without spreadsheet-specific transformations.
