# Quickstart: Audit Log Export Service

## Prerequisites

- Access to the downstream product repository that contains the real admin UI, API, worker, and storage integration code (not included in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs`).
- Access to the planning package at `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs`.
- Access to a test account with the `compliance_admin` role.
- Access to the existing Redis queue, object storage signing integration, and audit-event source store used by the product.

## 1. Implement

1. Bind the planning package to the actual product repository before creating tasks or code changes.

```bash
export TARGET_REPO=/absolute/path/to/target-product-repo
cd "$TARGET_REPO" && rg -n "compliance_admin|audit|worker|redis|presign|signed" .
```

Expected outcome: You identify the existing auth guard, admin API surface, worker entrypoint, and object-storage adapter that map to the logical implementation areas described in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/plan.md` and `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/research.md`.

2. Turn this plan package into an ordered implementation backlog.

```text
/create-tasks /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/plan.md
```

Expected outcome: A task breakdown is produced from the plan, contracts, and data model so implementation can proceed in small verified increments instead of ad hoc changes.

3. Implement against the machine-readable contracts and data model, not against free-form notes.

```bash
sed -n '1,240p' /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/contracts/audit-export-api.yaml
sed -n '1,240p' /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/data-model.md
```

Expected outcome: The downstream implementation uses the exact request/status/cancel/download contract, the export-job state machine, and the artifact/audit-event invariants defined by this plan.

## 2. Validate

1. Verify export initiation, authorization, and queued-state behavior from the API contract.

```bash
curl -sS -X POST http://localhost:8080/admin/audit-exports   -H 'Content-Type: application/json'   -H 'Authorization: Bearer <TOKEN_FOR_COMPLIANCE_ADMIN>'   -d '{"dateFrom":"2026-01-01","dateTo":"2026-03-31","actorType":"human","actionCategory":"auth"}'
```

Expected outcome: The API returns `202 Accepted` in under 500ms with a stable export ID, initial status `queued`, and no sensitive fields in the response.

2. Verify lifecycle transitions, cancellation, and signed-link generation.

```bash
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID> -H 'Authorization: Bearer <TOKEN_FOR_COMPLIANCE_ADMIN>'
curl -sS -X POST http://localhost:8080/admin/audit-exports/<EXPORT_ID>/cancel -H 'Authorization: Bearer <TOKEN_FOR_COMPLIANCE_ADMIN>'
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID>/downloads/csv -H 'Authorization: Bearer <TOKEN_FOR_COMPLIANCE_ADMIN>'
```

Expected outcome: Status responses follow the planned state machine, cancellation is accepted only for queued/running jobs, and the download response returns a format-specific signed URL that expires in 24 hours.

3. Validate artifact safety and audit-stream coverage.

```bash
sed -n '1,220p' /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/contracts/audit-export-audit-stream.schema.json
```

Expected outcome: The downstream implementation can be checked against the event schema to confirm request and download actions are emitted to the dedicated audit stream and that exported fields remain on the allowlisted safe schema.

## 3. Rollout/Operate

1. Roll out API and worker changes together so queue processing and download-link minting stay compatible.

```bash
cd "$TARGET_REPO" && git grep -n "audit_export\|failure rate\|queue depth\|downloadExpiresAt" .
```

Expected outcome: Deployment and monitoring changes cover request latency, queue depth, stuck-job detection, and failure-rate alerts aligned to the `<0.5%` target in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-1/with_skill/run-1/outputs/plan.md`.

2. Run a compliance smoke check after deployment using production-like data volume.

```bash
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID>/downloads/json -H 'Authorization: Bearer <TOKEN_FOR_COMPLIANCE_ADMIN>'
```

Expected outcome: Both CSV and JSON downloads are available for completed jobs, links expire after 24 hours, and the dedicated audit stream records request/download activity for compliance review.
