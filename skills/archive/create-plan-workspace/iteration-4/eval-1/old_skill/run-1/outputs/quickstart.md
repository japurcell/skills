# Quickstart: Audit Log Export Service

## Prerequisites

- Access to the real product repository that contains the admin UI, API service, worker service, and deployment tooling.
- A test account with the `compliance_admin` role.
- Connectivity to the existing Redis-backed queue, audit-event source store, relational metadata store, and object-storage bucket used by the product.
- Object-storage signing credentials whose lifetime safely covers the required 24-hour download TTL.
- A reviewed export-field allowlist based on `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/data-model.md`.

## 1. Implement

1. Bind the planned touchpoints in the product repository before editing code.

```bash
cd /path/to/product-repo
git grep -nE 'compliance_admin|audit[-_ ]export|audit stream|signed url|redis' .
```

Expected outcome: You identify the existing admin UI, API, worker, and audit-publishing modules that will host the feature, satisfying the repo-binding follow-up from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/plan.md`.

2. Stage the API and audit-event contracts beside the feature work so implementation can follow one shared interface definition.

```bash
cd /path/to/product-repo
mkdir -p docs/contracts/audit-export
cp /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/contracts/audit-export-api.yaml docs/contracts/audit-export/
cp /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/contracts/audit-export-audit-stream.json docs/contracts/audit-export/
```

Expected outcome: Backend, UI, and worker implementers are working from the same HTTP and audit-stream contracts documented by the plan and research artifacts.

3. Implement the durable job model, allowlist serializer, and worker flow described in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/data-model.md` and `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/research.md`.

```bash
cd /path/to/product-repo
$EDITOR <identified-api-files> <identified-worker-files> <identified-ui-files>
```

Expected outcome: The product code now supports role-gated export creation, bounded-batch worker processing, dual-format artifact generation, 24-hour signed URLs, dedicated audit events, and a cancel flow for queued/running jobs.

## 2. Validate

1. Exercise the create/status/download flow against a local or staging environment.

```bash
curl -sS -X POST http://localhost:8080/admin/audit-exports \
  -H 'Content-Type: application/json' \
  -H 'X-Role: compliance_admin' \
  -d '{"dateFrom":"2026-01-01","dateTo":"2026-03-31","actorType":"human","actionCategory":"auth"}'
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID> -H 'X-Role: compliance_admin'
curl -sS http://localhost:8080/admin/audit-exports/<EXPORT_ID>/downloads -H 'X-Role: compliance_admin'
```

Expected outcome: The create request returns `202 Accepted` in under 500ms, status shows a valid lifecycle progression, and completed jobs return both CSV and JSON signed URLs with a 24-hour expiry timestamp.

2. Validate authorization, cancellation, and PII-safe export behavior.

```bash
curl -sS -X POST http://localhost:8080/admin/audit-exports/<EXPORT_ID>/cancel -H 'X-Role: compliance_admin'
curl -sS -X POST http://localhost:8080/admin/audit-exports -H 'Content-Type: application/json' -H 'X-Role: analyst' -d '{"dateFrom":"2026-01-01","dateTo":"2026-03-31"}'
```

Expected outcome: Only `queued` or `running` jobs can be cancelled, non-`compliance_admin` requests are rejected, and the resulting exported payloads contain only allowlisted non-PII fields from the policy in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-1/old_skill/run-1/outputs/data-model.md`.

## 3. Rollout/Operate

1. Deploy API and worker changes together using the product repository's normal release workflow so queue, persistence, and signed-link behavior stay in sync.
2. Monitor initiation latency, queue depth, worker failures, stuck-job count, and dedicated audit-stream coverage during rollout.
3. Run a compliance smoke check on a production-like dataset to confirm both artifact formats are generated, links expire after 24 hours, and request/download/cancel/failure events appear in the dedicated audit stream.
