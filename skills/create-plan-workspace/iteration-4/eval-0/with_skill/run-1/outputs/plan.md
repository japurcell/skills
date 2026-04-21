# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/with_skill/run-1/outputs/spec-billing-disputes.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/with_skill/run-1/outputs/spec-billing-disputes.md`

## Summary

Implement billing dispute management in the internal portal with a FastAPI + PostgreSQL backend and a React + TypeScript frontend. The feature adds role-based dispute creation, assignment, transition, and resolution flows; immutable activity history; SLA warning/breach tracking; OpenAPI-described service endpoints; and a monthly CSV export while keeping the dispute list endpoint under 250ms p95 for a 50k-dispute dataset.

## Technical Context

**Language/Version**: Python 3.x backend; TypeScript 5.x + React frontend (existing stack, exact minor versions should match the billing portal repository)  
**Primary Dependencies**: FastAPI, Pydantic request/response models, PostgreSQL, React, TypeScript, OpenAPI 3.x contract artifacts  
**Storage**: PostgreSQL with normalized `disputes` and `dispute_activity` tables; CSV export generated from streamed query results instead of temp files  
**Testing**: Backend pytest API/integration tests, frontend React component/integration tests, OpenAPI contract review, targeted query-plan/performance checks  
**Target Platform**: Internal web application on Linux-hosted services and modern desktop browsers  
**Project Type**: Web application (FastAPI service + React SPA)  
**Performance Goals**: Dispute list endpoint p95 <250ms for 50k disputes; timeline/detail reads stay index-backed; monthly export streams without loading the entire file in memory  
**Constraints**: Immutable audit trail; role-based permissions (`agent`, `manager`); SLA warning at 24h and breach at 48h from creation time; team prefers OpenAPI for service contracts  
**Scale/Scope**: Up to 50k disputes in active list queries, monthly export of outcome rows, multi-user agent workflow with assignment changes and comments

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- PASS: The run writes only generated planning artifacts under `skills/create-plan-workspace/iteration-4/eval-0/with_skill/run-1/outputs`, which matches the repository rule that generated evaluation output belongs in sibling `*-workspace/` directories.
- PASS: No maintained repository source files, installer scripts, or agent definitions are modified during this benchmark run.
- PASS: AGENTS guidance states there is no single repo-wide package manifest or test runner, so targeted artifact validation is the correct verification scope for this plan-only task.
- Re-check after Phase 1: all design artifacts must remain implementation-oriented, internally consistent, and confined to the feature workspace.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/with_skill/run-1/outputs/
├── spec-billing-disputes.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── report.md
├── output.md
└── contracts/
    └── disputes-openapi.yaml
```

### Source Code (target billing portal application)

The target portal repository is not part of this benchmark workspace, so the implementation surface below is the minimum module layout implied by the spec's existing FastAPI backend and React frontend. Before coding, map these paths onto the real application repository if its naming differs.

```text
backend/
├── app/
│   ├── main.py
│   ├── routers/disputes.py
│   ├── schemas/disputes.py
│   ├── services/disputes.py
│   ├── repositories/disputes.py
│   └── models/
│       ├── dispute.py
│       └── dispute_activity.py
├── migrations/
│   └── versions/<timestamp>_billing_disputes.py
└── tests/
    ├── integration/test_disputes_api.py
    └── performance/test_disputes_list_query.py

frontend/
├── src/
│   ├── features/disputes/
│   │   ├── pages/DisputeListPage.tsx
│   │   ├── pages/DisputeDetailPage.tsx
│   │   ├── components/DisputeTimeline.tsx
│   │   ├── components/DisputeAssignmentPanel.tsx
│   │   ├── api/disputesClient.ts
│   │   └── types.ts
│   └── routes.tsx
└── src/features/disputes/__tests__/
    ├── DisputeListPage.test.tsx
    └── DisputeDetailPage.test.tsx

contracts/
└── disputes-openapi.yaml
```

**Structure Decision**: Use a feature-sliced web application layout with a dedicated FastAPI router/service/schema/model path on the backend and a `src/features/disputes` slice on the React frontend. These are the minimum concrete paths required by the spec; the first implementation step is to map them to the real portal repository paths if they differ.

## Complexity Tracking

No AGENTS.md or workflow violations require justification for this planning run.
