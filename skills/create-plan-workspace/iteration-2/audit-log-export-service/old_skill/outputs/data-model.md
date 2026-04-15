# Data Model: Audit Log Export Service

## Entity: ExportJob

Represents one export request initiated by a compliance administrator.

| Field                | Type      | Required | Notes                                         |
| -------------------- | --------- | -------- | --------------------------------------------- |
| id                   | UUID      | yes      | Primary key                                   |
| requested_by_user_id | UUID      | yes      | Must map to authenticated user                |
| requested_by_role    | string    | yes      | Must equal `compliance_admin` at request time |
| status               | enum      | yes      | `queued`, `running`, `failed`, `completed`    |
| date_from            | timestamp | yes      | Inclusive lower bound                         |
| date_to              | timestamp | yes      | Inclusive upper bound, must be >= `date_from` |
| actor_type           | string    | yes      | Filter input from UI                          |
| action_category      | string    | yes      | Filter input from UI                          |
| progress_percent     | integer   | yes      | 0-100 worker-managed progress                 |
| failure_code         | string    | no       | Present when `status=failed`                  |
| failure_message      | string    | no       | Truncated human-readable reason               |
| queued_at            | timestamp | yes      | Creation timestamp                            |
| started_at           | timestamp | no       | Set when worker begins                        |
| completed_at         | timestamp | no       | Set on terminal completion                    |
| cancelled_at         | timestamp | no       | Set when cancelled via admin endpoint         |

### Invariants

- Allowed state transitions: `queued -> running -> completed|failed`; `queued|running -> failed` when cancelled.
- Terminal states (`completed`, `failed`) are immutable.
- `progress_percent` is monotonic and must be 100 only when `completed`.
- `date_from <= date_to` and range length is bounded by configured max window.

## Entity: ExportArtifact

Represents generated downloadable output file metadata for an `ExportJob`.

| Field                 | Type      | Required | Notes                      |
| --------------------- | --------- | -------- | -------------------------- |
| id                    | UUID      | yes      | Primary key                |
| export_job_id         | UUID      | yes      | FK to `ExportJob.id`       |
| format                | enum      | yes      | `csv` or `json`            |
| object_key            | string    | yes      | Object storage key         |
| byte_size             | bigint    | yes      | File size after completion |
| checksum_sha256       | string    | yes      | Integrity tracking         |
| signed_url_expires_at | timestamp | yes      | Must be 24h from issuance  |
| created_at            | timestamp | yes      | Artifact creation time     |

### Invariants

- Exactly two artifacts expected for completed jobs: one `csv` and one `json`.
- Signed URLs are never persisted beyond expiration refresh metadata.

## Entity: ExportAuditEvent

Immutable log stream for request and download actions.

| Field         | Type      | Required | Notes                                                                                                                         |
| ------------- | --------- | -------- | ----------------------------------------------------------------------------------------------------------------------------- |
| id            | UUID      | yes      | Primary key                                                                                                                   |
| export_job_id | UUID      | yes      | FK to `ExportJob.id`                                                                                                          |
| event_type    | enum      | yes      | `export_requested`, `job_started`, `job_failed`, `job_completed`, `job_cancelled`, `download_link_issued`, `download_started` |
| actor_user_id | UUID      | yes      | User who initiated action                                                                                                     |
| actor_role    | string    | yes      | Captured at event time                                                                                                        |
| request_ip    | string    | no       | Optional network metadata                                                                                                     |
| user_agent    | string    | no       | Optional client metadata                                                                                                      |
| occurred_at   | timestamp | yes      | Event timestamp                                                                                                               |
| metadata      | jsonb     | no       | Non-PII diagnostic details                                                                                                    |

### Invariants

- Events are append-only and never updated.
- Every `ExportJob` has at least one `export_requested` event.

## Relationship Summary

- One `ExportJob` has many `ExportArtifact` records.
- One `ExportJob` has many `ExportAuditEvent` records.
- A user may initiate many `ExportJob` records, but only if role is `compliance_admin`.

## Lifecycle Summary

1. API validates role and filters, creates `ExportJob(status=queued)`, and appends `export_requested` event.
2. Worker moves job to `running`, streams records through PII allowlist projection, writes CSV and JSON artifacts.
3. On success, worker marks `completed`, writes artifact metadata, and emits `job_completed`.
4. On error or cancellation, worker/API marks `failed` with reason and emits corresponding event.
