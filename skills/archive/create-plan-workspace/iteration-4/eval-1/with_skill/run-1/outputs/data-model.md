# Data Model: Audit Log Export Service

## Overview

The feature introduces a durable export-job record, per-format artifact metadata, and dedicated audit events around the export lifecycle. The source audit-log dataset already exists; this plan defines the export-facing projection and control records needed to safely package it.

## Entities

### 1. AuditExportJob

Purpose: Authoritative record for one export request from submission through completion or failure.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Stable job identifier returned by the API |
| `requestedByUserId` | string | Authenticated requester |
| `requestedByRoleSnapshot` | string | Must include `compliance_admin` at request time |
| `filters.startDate` | datetime/date | Inclusive export lower bound |
| `filters.endDate` | datetime/date | Inclusive export upper bound |
| `filters.actorType` | enum/string | Requested actor-type filter |
| `filters.actionCategory` | enum/string/null | Optional action-category filter |
| `status` | enum | `queued`, `running`, `failed`, `completed` |
| `cancellationRequested` | boolean | Set by admin cancel endpoint |
| `failureCode` | enum/string/null | Example values: `cancelled_by_admin`, `worker_timeout`, `storage_error`, `query_error` |
| `failureMessage` | string/null | Operator-readable detail |
| `progressPercent` | integer 0-100 | UI progress indicator |
| `recordsScanned` | integer | Count of source rows scanned |
| `recordsExported` | integer | Count of rows written to the allowlisted schema |
| `queuedAt` | timestamp | Creation time |
| `startedAt` | timestamp/null | First worker pickup |
| `completedAt` | timestamp/null | Successful completion time |
| `failedAt` | timestamp/null | Failure completion time |
| `lastHeartbeatAt` | timestamp/null | Updated by worker while active |
| `artifactSetReadyAt` | timestamp/null | When both export formats are available |

Validation rules:
- `endDate >= startDate`.
- `status=completed` requires `artifactSetReadyAt` and two artifacts (`csv` and `json`).
- `status=failed` requires `failureCode`.
- `cancellationRequested` may only be set by a `compliance_admin` actor.

### 2. AuditExportArtifact

Purpose: One generated file per export format.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Artifact identifier |
| `jobId` | foreign key | Parent `AuditExportJob` |
| `format` | enum | `csv` or `json` |
| `objectKey` | string | Object-storage location |
| `contentType` | string | `text/csv` or `application/json` |
| `byteSize` | integer | Size of stored artifact |
| `recordCount` | integer | Rows represented in the artifact |
| `checksum` | string/null | Integrity check value if available |
| `signedUrl` | string/null | Generated on completion/status fetch |
| `signedUrlIssuedAt` | timestamp/null | URL generation time |
| `signedUrlExpiresAt` | timestamp/null | Must be within 24 hours of issue time |

Validation rules:
- Each job must have exactly one `csv` and one `json` artifact when complete.
- `signedUrlExpiresAt - signedUrlIssuedAt <= 24 hours`.
- `objectKey` must point to immutable export output for the job/version.

### 3. AuditExportAuditEvent

Purpose: Dedicated audit-stream record for export-related actions.

| Field | Type | Notes |
| --- | --- | --- |
| `id` | UUID/string | Event id |
| `jobId` | foreign key/null | Related job, when applicable |
| `eventType` | enum | `request_submitted`, `download_requested`, `cancel_requested`, `job_started`, `job_completed`, `job_failed` |
| `actorUserId` | string | Who triggered the action |
| `actorRoleSnapshot` | string | Authorization evidence |
| `occurredAt` | timestamp | Event time |
| `metadata` | object/json | Filter summary, artifact format, failure code, etc. |

Validation rules:
- Every API request that creates, cancels, or fetches a signed artifact must emit an audit event.
- Failure events must include the terminal `failureCode`.

### 4. ExportedAuditRecord (projection)

Purpose: The allowlisted row schema written to both CSV and JSON outputs.

| Field | Type | Notes |
| --- | --- | --- |
| `occurredAt` | timestamp | Event timestamp |
| `actorType` | string | Filterable actor classification |
| `actorId` | string/hash | Use the product's non-PII representation only |
| `actionCategory` | string | Filterable grouping |
| `action` | string | Specific audit action |
| `targetType` | string | Optional subject type |
| `targetId` | string/hash/null | Non-PII identifier only |
| `outcome` | string | Success/failure result |
| `requestId` | string/null | Trace identifier |
| `metadata` | object/null | Only pre-approved non-PII metadata |

Validation rules:
- The export schema is allowlisted; fields not explicitly approved are excluded.
- PII-bearing attributes from the source audit log must never appear in this projection.

## Relationships

- `AuditExportJob 1 ── 2 AuditExportArtifact` (exactly one CSV artifact and one JSON artifact when complete).
- `AuditExportJob 1 ── many AuditExportAuditEvent`.
- `ExportedAuditRecord` rows are derived from the existing audit-log source using the job filters; they are not a new system of record.

## State Transitions

### Job lifecycle

```text
queued -> running -> completed
queued -> failed
running -> failed
```

### Cancellation behavior

```text
queued/running + cancellationRequested=false
  -> cancel endpoint sets cancellationRequested=true
  -> worker sees flag before next batch or artifact finalize step
  -> job transitions to failed(failureCode=cancelled_by_admin)
```

### Stuck-job handling

```text
running + heartbeat expires beyond operator threshold
  -> admin reviews status
  -> cancel endpoint or automated recovery marks job failed(worker_timeout)
```

## Invariants

- Only principals with the `compliance_admin` role may create, cancel, or receive download links for jobs.
- Export initiation must remain a control-plane action only; expensive reads happen in workers.
- Completed jobs must expose both formats for the same filtered record set.
- Download URLs are temporary capabilities and must never outlive the 24-hour requirement.
- Audit export events themselves must be written to a dedicated audit stream for traceability.
