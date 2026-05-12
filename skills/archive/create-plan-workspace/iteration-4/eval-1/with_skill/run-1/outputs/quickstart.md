# Quickstart: Audit Log Export Service

## Prerequisites

- Work from the actual product repository that contains the admin UI, API service, worker service, and object-storage adapter; this benchmark workspace contains only the planning artifacts.
- Have credentials for a test environment with the `compliance_admin` role plus a non-compliance user for negative checks.
- Have local or shared access to the existing Redis worker queue and object storage used by the product.
- Use these artifacts while implementing:
  - `plan.md` for scope and constraints
  - `research.md` for design decisions and cited standards
  - `data-model.md` for state and schema rules
  - `contracts/audit-export-api.yaml` for the external API contract

## 1. Implement

1. Locate the existing authorization, audit publishing, queue, and storage integration points in the product repo.
   ```bash
   git grep -nE "compliance_admin|authorize|audit|redis|signed" .
   ```
   Expected outcome: you identify the server-side role-check middleware/policies, the audit-event publisher, the worker enqueue path, and the object-storage adapter that this feature must extend.

2. Add the durable export-job model and state machine from `data-model.md`, then wire the async API endpoints defined in `contracts/audit-export-api.yaml`.
   ```bash
   git grep -nE "queued|running|failed|completed|job" .
   ```
   Expected outcome: you confirm whether an existing job-status abstraction can be reused; if not, you create a new export-job record with `cancellationRequested`, heartbeat tracking, and dual-artifact metadata.

3. Implement the worker pipeline so it reads the filtered audit-log dataset in batches, writes allowlisted rows to both CSV and JSON artifacts, updates progress/heartbeats, and emits dedicated export audit events.
   - Reuse the existing Redis-backed worker system from the spec.
   - Keep artifact generation streaming so 5-million-record exports do not require loading the full dataset into memory.
   - Mark cancellation by setting `cancellationRequested=true` and transitioning to `failed(cancelled_by_admin)` when the worker stops safely.

## 2. Validate

1. Create an export as a compliance admin.
   ```bash
   curl -sS -X POST "$BASE_URL/admin/audit-exports"      -H "Authorization: Bearer $COMPLIANCE_TOKEN"      -H "Content-Type: application/json"      -d '{"startDate":"2026-01-01","endDate":"2026-03-31","actorType":"human","actionCategory":"authentication"}'
   ```
   Expected outcome: the API returns `202 Accepted` with a job id, `status="queued"`, `cancellationRequested=false`, and no artifact URLs yet.

2. Poll for completion and verify both artifact links are present.
   ```bash
   curl -sS "$BASE_URL/admin/audit-exports/$JOB_ID"
   ```
   Expected outcome: the response eventually reaches `status="completed"` and includes exactly two artifacts (`csv`, `json`) whose `expiresAt` values are within 24 hours of issuance.

3. Confirm authorization is enforced server-side.
   ```bash
   curl -i -X POST "$BASE_URL/admin/audit-exports"      -H "Authorization: Bearer $NON_COMPLIANCE_TOKEN"      -H "Content-Type: application/json"      -d '{"startDate":"2026-01-01","endDate":"2026-03-31","actorType":"human"}'
   ```
   Expected outcome: the API rejects the request with `403 Forbidden`, and no export job is created.

4. Verify the downloaded schema excludes PII.
   ```bash
   curl -sS "$CSV_URL" | head
   ```
   Expected outcome: only allowlisted export columns appear, matching `ExportedAuditRecord` in `data-model.md`; no PII-bearing source columns are present.

## 3. Rollout/Operate

- Configure worker concurrency and batch size so the control-plane request still returns in under 500ms while workers handle large datasets.
- Monitor dedicated audit-stream events for `request_submitted`, `download_requested`, `cancel_requested`, `job_completed`, and `job_failed`.
- Establish an operational threshold for stale heartbeats so stuck jobs can be cancelled and investigated quickly.
- Exercise the admin cancellation path before production rollout.
  ```bash
  curl -sS -X POST "$BASE_URL/admin/audit-exports/$JOB_ID/cancel"     -H "Authorization: Bearer $COMPLIANCE_TOKEN"
  ```
  Expected outcome: the API acknowledges cancellation, the job record flips `cancellationRequested=true`, and the worker eventually finishes in `failed` with `failureCode="cancelled_by_admin"` if it had already started.
