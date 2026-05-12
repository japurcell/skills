# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/old_skill/run-1/outputs/spec-billing-disputes.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/old_skill/run-1/outputs/spec-billing-disputes.md`

## Summary

Add a disputes workflow to the internal billing portal using the existing FastAPI + PostgreSQL backend and React + TypeScript frontend. The implementation centers on a current-state `billing_disputes` record, an append-only `dispute_activity` audit log, OpenAPI-defined REST endpoints for create/list/detail/transition/assignment/export flows, SLA timestamps stored at creation (`warn_at`, `breach_at`), and a CSV monthly outcomes export documented as a first-class contract.

## Technical Context

**Language/Version**: Python 3.11+ for backend services; TypeScript 5.x on React 18 for the portal UI, while keeping exact deployed portal versions unchanged  
**Primary Dependencies**: FastAPI, Pydantic response models, PostgreSQL, React, TypeScript, OpenAPI 3.1 contract-first API design  
**Storage**: PostgreSQL tables for disputes and append-only dispute activity  
**Testing**: Backend `pytest` integration/contract coverage; frontend component/workflow coverage in the portal's existing TypeScript test harness; targeted API smoke checks for CSV export  
**Target Platform**: Internal web application on Linux-hosted services with browser clients for support agents and managers  
**Project Type**: Web application (React frontend + FastAPI backend)  
**Performance Goals**: Dispute list endpoint p95 under 250ms with 50k disputes; constant-time timeline writes per action; export path safe for monthly operational use  
**Constraints**: Immutable audit trail, SLA warn at 24h and breach at 48h, role-gated actions (`agent`, `manager`), OpenAPI-aligned service contracts, no repository source edits in this planning run  
**Scale/Scope**: 50k-dispute operational dataset, monthly outcome exports, internal support staff using create/assign/investigate/resolve workflows

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

PASS (pre-research and post-design): the repository-level instructions require output-only work in this benchmark run, helper scripts via `python3` when used, no assumption of a monorepo test runner, and no edits to maintained source. This plan writes artifacts only inside `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/old_skill/run-1/outputs`, does not introduce net-new technology that requires an agent-context update, and keeps validation scoped to artifact consistency.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-0/old_skill/run-1/outputs/
├── spec-billing-disputes.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── disputes.openapi.yaml
└── report.md
```

### Source Code (target billing portal repository)

```text
backend/
├── app/
│   ├── api/
│   │   └── disputes.py
│   ├── models/
│   │   ├── dispute.py
│   │   └── dispute_activity.py
│   ├── services/
│   │   └── disputes/
│   │       ├── policies.py
│   │       ├── queries.py
│   │       └── transitions.py
│   └── schemas/
│       └── disputes.py
├── migrations/
│   └── versions/
└── tests/
    ├── contract/
    └── integration/

frontend/
├── src/
│   ├── api/
│   │   └── disputes.ts
│   ├── features/
│   │   └── disputes/
│   │       ├── components/
│   │       ├── hooks/
│   │       ├── pages/
│   │       └── state/
│   └── routes/
└── tests/
    └── disputes/
```

**Structure Decision**: Use the web-application split implied by the spec: backend API + frontend portal feature module. The exact repository-specific module names are not visible from the provided workspace, so `/create-tasks` should keep these paths as the implementation target shape and remap filenames to the real billing-portal repo during task creation.

## Complexity Tracking

No AGENTS.md or instruction-file violations require justification for this planning run.
