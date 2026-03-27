# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-03-26 | **Spec**: /home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-billing-disputes.md  
**Input**: Feature specification from `/home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-billing-disputes.md`

## Summary

Add an end-to-end disputes workflow to the billing portal with role-aware actions (agent and manager), state transitions, immutable audit timeline, SLA warning/breach handling, and monthly CSV export. Implement FastAPI + Postgres backend APIs and React + TypeScript frontend workflow screens to meet p95 list performance under 250ms at 50k disputes.

## Technical Context

**Language/Version**: Python 3.11 (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, SQLAlchemy/Alembic, Postgres, React, React Query, OpenAPI tooling  
**Storage**: PostgreSQL (disputes, comments, assignment changes, audit events)  
**Testing**: pytest (unit/integration/API), Playwright or RTL for UI flows  
**Target Platform**: Internal web application on Linux-hosted services  
**Project Type**: Web application (backend API + frontend UI)  
**Performance Goals**: Disputes list endpoint p95 < 250ms at dataset size 50k  
**Constraints**: Immutable audit trail; SLA warning at 24h and breach at 48h from creation; manager override permissions  
**Scale/Scope**: Operational workflow for internal support org; tens of thousands of disputes with monthly outcome exports

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- No `AGENTS.md`, `.instructions.md`, or `copilot-instructions.md` files were found under `/home/adam/.agents` workspace scope.
- Pre-research gate: **PASS** (no policy-file violations discovered).
- Post-design gate: **PASS** (artifacts remain consistent with active system/developer constraints from this run).

## Project Structure

### Documentation (this feature)

```text
/home/adam/.agents/skills/create-plan-workspace/iteration-2/billing-disputes-workflow/with_skill/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── report.md
```

### Source Code (repository root)

```text
/home/adam/.agents/
├── backend/                 # Assumed implementation location from spec stack constraints
│   ├── src/
│   │   ├── api/disputes/
│   │   ├── models/
│   │   ├── services/disputes/
│   │   └── jobs/
│   └── tests/
│       ├── integration/
│       └── contract/
└── frontend/                # Assumed implementation location from spec stack constraints
    ├── src/
    │   ├── pages/disputes/
    │   ├── components/disputes/
    │   └── services/disputes/
    └── tests/
```

**Structure Decision**: Use a web application split (`backend/` + `frontend/`) because the spec explicitly states existing FastAPI/Postgres backend and React/TypeScript frontend. This workspace snapshot does not include those app directories; creating tasks should verify exact in-repo paths before implementation.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None      | N/A        | N/A                                  |
