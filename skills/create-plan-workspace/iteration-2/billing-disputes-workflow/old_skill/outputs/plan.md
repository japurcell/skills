# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-03-26 | **Spec**: /home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-billing-disputes.md  
**Input**: Feature specification from `/home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-billing-disputes.md`

## Summary

Deliver a disputes workflow in the internal billing portal that supports role-based creation, assignment and resolution, enforces SLA warning/breach thresholds, records an immutable audit timeline, and exposes API endpoints plus monthly CSV exports. The implementation uses the existing FastAPI + Postgres backend and React + TypeScript frontend, with OpenAPI contracts as the service interface source of truth.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, PostgreSQL driver/ORM layer, React 18+  
**Storage**: PostgreSQL (system of record), append-only activity rows for audit trail  
**Testing**: pytest (backend API/integration), frontend test runner (NEEDS CLARIFICATION in repo), contract validation against OpenAPI  
**Target Platform**: Linux-hosted internal web application  
**Project Type**: Web application (backend API + frontend UI)  
**Performance Goals**: p95 list endpoint <250ms at 50k disputes; monthly CSV export completes in operational batch window  
**Constraints**: Immutable audit trail; role-based permissions (`agent`, `manager`); SLA warning at 24h and breach at 48h  
**Scale/Scope**: 50k+ dispute records, timeline events per state/assignment/comment action

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Result: PASS
- Evidence: No `AGENTS.md` or `*.instructions.md` files were found in this workspace scope.
- Action: Proceed with standard repository conventions and explicit assumptions in artifacts.

## Project Structure

### Documentation (this feature)

```text
/home/adam/.agents/skills/create-plan-workspace/iteration-2/billing-disputes-workflow/old_skill/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi-disputes.yaml
├── report.md
└── output.md
```

### Source Code (implementation repository)

```text
backend/
├── src/
│   ├── api/disputes/
│   ├── services/disputes/
│   ├── models/
│   └── exports/
└── tests/
    ├── integration/
    ├── contract/
    └── unit/

frontend/
├── src/
│   ├── pages/disputes/
│   ├── components/disputes/
│   └── services/disputesApi/
└── tests/
```

**Structure Decision**: Use a backend/frontend web-application split that matches the spec stack (FastAPI + Postgres and React + TypeScript). The current workspace is planning-only, so implementation paths are defined as target repository paths for the build team to map directly in the product codebase.

## Complexity Tracking

No constitution violations identified in this planning run.
