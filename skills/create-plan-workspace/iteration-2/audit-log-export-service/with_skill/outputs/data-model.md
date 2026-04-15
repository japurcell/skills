# Data Model: Audit Log Export Service

## Entity: ExportRequest

Purpose: Represents a compliance-admin initiated export job and its lifecycle.

Fields:

- `id` (UUID, primary key)
- `requested_by_user_id` (string/UUID, required)
- `requested_by_role` (enum, must be `compliance_admin`)
- `date_from` (timestamp/date, required)
- `date_to` (timestamp/date, required, must be >= `date_from`)
- `actor_type` (enum/string, optional filter)
- `action_category` (enum/string, optional filter)
- `status` (enum: `queued`, `running`, `failed`, `completed`, `cancelled`)
- `records_processed` (integer, default 0)
- `records_exported` (integer, default 0)
- `progress_pct` (integer 0-100)
- `failure_reason` (string, nullable)
- `queue_job_id` (string, nullable)
- `storage_key_csv` (string, nullable)
- `storage_key_json` (string, nullable)
- `download_expires_at` (timestamp, set when completed)
- `created_at` (timestamp)
- `updated_at` (timestamp)
- `started_at` (timestamp, nullable)
- `completed_at` (timestamp, nullable)
- `cancel_requested_at` (timestamp, nullable)
- `cancelled_at` (timestamp, nullable)

Validation rules:

- Requesting user must have `compliance_admin` role.
- `date_from` and `date_to` are mandatory and bounded to a maximum allowed window (implementation configurable).
- Export serializer must include only allowlisted fields (PII-safe output contract).
- `download_expires_at` must be exactly 24 hours from completion timestamp.

State transitions:

- `queued` -> `running`: worker claim starts processing.
- `running` -> `completed`: both CSV and JSON artifacts produced and stored.
- `running` -> `failed`: unrecoverable processing/storage failure.
- `queued` -> `cancelled`: admin cancellation before start.
- `running` -> `cancelled`: cooperative stop after cancel signal.
- `failed` -> `queued` (optional manual retry policy).

## Entity: ExportArtifact

Purpose: Captures format-specific output for a completed export request.

Fields:

- `id` (UUID)
- `export_request_id` (UUID, FK -> ExportRequest.id)
- `format` (enum: `csv`, `json`)
- `storage_key` (string, required)
- `bytes` (integer)
- `checksum` (string)
- `created_at` (timestamp)

Relationships:

- One `ExportRequest` has many `ExportArtifact` rows; expected exactly 2 on success (`csv`, `json`).

Validation rules:

- No duplicate (`export_request_id`, `format`).
- Artifact creation allowed only when parent request is `running` and transitions to `completed` after both formats are present.

## Entity: AuditExportEvent

Purpose: Dedicated audit-stream event payload for traceability.

Fields:

- `event_id` (UUID)
- `event_type` (enum: `audit_export.requested`, `audit_export.downloaded`, `audit_export.cancelled`, `audit_export.failed`)
- `occurred_at` (timestamp)
- `actor_user_id` (string/UUID)
- `actor_role` (string)
- `export_request_id` (UUID)
- `result` (enum: `accepted`, `denied`, `success`, `failure`)
- `metadata` (object: filters, format, client IP, user agent, reason)

Validation rules:

- Every accepted export request emits `audit_export.requested`.
- Every download URL retrieval emits `audit_export.downloaded`.
- Authorization failures emit denied event with reason.

## Entity: StuckJobPolicy (Configuration)

Purpose: Defines cancellation and stuck-job detection thresholds.

Fields:

- `max_running_minutes` (integer)
- `heartbeat_timeout_minutes` (integer)
- `max_retry_count` (integer)
- `cancel_grace_seconds` (integer)

Usage:

- Worker marks job as potentially stuck when heartbeat timeout exceeded.
- Admin cancel endpoint uses policy to enforce safe cancellation behavior.
