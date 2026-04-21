# Data Model: Audit Log Export Service

## Entity: ExportJob

Purpose: Represents one compliance-admin initiated export request and its lifecycle.

Fields:

- `id` (UUID, primary key)
- `requested_by_user_id` (string/UUID, required)
- `requested_by_role` (string/enum, must equal `compliance_admin` for accepted requests)
- `date_from` (timestamp/date, required)
- `date_to` (timestamp/date, required, must be greater than or equal to `date_from`)
- `actor_type` (string/enum, optional filter)
- `action_category` (string/enum, optional filter)
- `status` (enum: `queued`, `running`, `failed`, `completed`, `cancelled`)
- `records_processed` (integer, default `0`, monotonic)
- `records_exported` (integer, default `0`, monotonic)
- `progress_pct` (integer, range `0..100`)
- `queue_job_id` (string, nullable)
- `failure_reason` (string, nullable)
- `heartbeat_at` (timestamp, nullable)
- `cancel_requested_at` (timestamp, nullable)
- `started_at` (timestamp, nullable)
- `completed_at` (timestamp, nullable)
- `cancelled_at` (timestamp, nullable)
- `download_expires_at` (timestamp, nullable; required for completed jobs)
- `created_at` (timestamp)
- `updated_at` (timestamp)

Validation rules and invariants:

- Only `compliance_admin` users may create, cancel, or request downloads for a job.
- `date_from`/`date_to` must define a valid bounded window accepted by backend policy.
- Job creation must not expose or accept field-selection inputs that bypass the export allowlist.
- `progress_pct`, `records_processed`, and `records_exported` must never decrease.
- `download_expires_at` must equal `completed_at + 24 hours` for successful jobs.
- A job may expose download URLs only when `status == completed` and `now < download_expires_at`.

State transitions:

- `queued -> running`: worker claims job and starts batch processing.
- `running -> completed`: both CSV and JSON artifacts were generated, stored, and linked.
- `running -> failed`: unrecoverable read/serialize/store failure.
- `queued -> cancelled`: admin cancellation accepted before work begins.
- `running -> cancelled`: cooperative cancellation after chunk boundary.
- `failed -> queued` (optional manual retry policy, if product chooses to support retries).

## Entity: ExportArtifact

Purpose: Tracks one generated output file for an export job.

Fields:

- `id` (UUID, primary key)
- `export_job_id` (UUID, foreign key -> `ExportJob.id`)
- `format` (enum: `csv`, `json`)
- `storage_key` (string, required)
- `content_type` (string, expected `text/csv` or `application/json`)
- `bytes` (integer, required)
- `checksum` (string, optional but recommended)
- `created_at` (timestamp)

Relationships:

- One `ExportJob` has zero-to-many `ExportArtifact` rows while running and exactly two artifacts on successful completion.

Validation rules:

- `format` must be unique per `export_job_id`.
- Artifact rows must reference an existing `ExportJob`.
- Artifact creation is allowed only while parent job is `running` and must complete before the parent transitions to `completed`.

## Entity: ExportAuditEvent

Purpose: Dedicated audit-stream payload describing sensitive export actions and outcomes.

Fields:

- `event_id` (UUID)
- `event_type` (enum: `audit_export.requested`, `audit_export.request_denied`, `audit_export.downloaded`, `audit_export.cancelled`, `audit_export.failed`)
- `occurred_at` (timestamp)
- `actor_user_id` (string/UUID)
- `actor_role` (string)
- `export_job_id` (UUID, nullable for denied requests before job creation)
- `result` (enum: `accepted`, `denied`, `success`, `failure`)
- `request_filters` (object containing date range, actor type, and action category)
- `download_format` (enum `csv|json`, nullable)
- `client_ip` (string, nullable)
- `user_agent` (string, nullable)
- `reason` (string, nullable)

Validation rules:

- Every accepted export request emits `audit_export.requested`.
- Every denied create/cancel/download attempt emits an explicit denied event.
- Every signed download-link issuance emits `audit_export.downloaded`.
- Terminal failures and successful cancellations emit corresponding terminal events.

## Entity: ExportFieldPolicy

Purpose: Defines the approved output schema and PII exclusions for export serialization.

Fields:

- `policy_version` (string)
- `allowed_fields` (ordered list of safe source-field names)
- `source_schema_version` (string, optional)
- `reviewed_by` (string/user identifier)
- `reviewed_at` (timestamp)

Validation rules and invariants:

- Only fields in `allowed_fields` may appear in CSV or JSON exports.
- Policy changes require compliance/security review before rollout.
- CSV header order and JSON object keys must map to the same approved field set.

## Operational configuration: StuckJobPolicy

Purpose: Defines how the system recognizes and safely handles stuck jobs.

Fields:

- `heartbeat_timeout_minutes` (integer)
- `max_running_minutes` (integer)
- `cancel_grace_seconds` (integer)
- `max_retry_count` (integer)

Usage:

- UI and operators use these thresholds to identify jobs that qualify as stuck.
- Admin cancel requests should respect `cancel_grace_seconds` before marking terminal cancellation if a worker is still shutting down.
