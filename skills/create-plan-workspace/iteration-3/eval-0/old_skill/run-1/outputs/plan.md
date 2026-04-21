# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-billing-disputes.md  
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-billing-disputes.md`

## Summary

Deliver a billing-disputes workflow for the internal billing portal so agents can create and work disputes, managers can reassign or override outcomes, SLA warning/breach deadlines are enforced, every mutation is captured in an immutable activity timeline, and backend/frontend integration is governed by an OpenAPI contract plus a monthly CSV export path.

## Technical Context

**Language/Version**: Python 3.11+ (backend), TypeScript 5.x (frontend)  
**Primary Dependencies**: FastAPI, Pydantic, PostgreSQL, React 18+  
**Storage**: PostgreSQL for dispute records and append-only activity events  
**Testing**: `pytest` for backend unit/integration/contract coverage, existing React test runner for UI workflow coverage, contract validation against `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/contracts/openapi-disputes.yaml`  
**Target Platform**: Linux-hosted internal web application  
**Project Type**: Web application (FastAPI service + React frontend)  
**Performance Goals**: p95 disputes list endpoint under 250 ms at 50k disputes; monthly CSV export completes within normal operational reporting windows  
**Constraints**: Immutable audit trail; role-based authorization for `agent` and `manager`; SLA warning at 24 hours and breach at 48 hours; OpenAPI-first service contracts  
**Scale/Scope**: 50k+ disputes, timeline history per dispute, monthly outcome exports for operations/reporting

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Result: PASS
- Evidence: `/home/adam/dev/personal/skills/AGENTS.md` applies in this benchmark workspace and requires Python 3 helper scripts, notes there is no repo-wide package manifest or single test runner, and treats `skills/*-workspace/**/outputs/` as benchmark fixtures rather than maintained source.
- Action: Keep all generated files inside `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs` and use planning-only validation instead of repository build/test automation.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/old_skill/run-1/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── openapi-disputes.yaml
├── report.md
└── output.md
```

### Source Code (target implementation repository)

```text
backend/
├── src/
│   ├── api/disputes/
│   ├── services/disputes/
│   ├── models/
│   └── exports/
├── migrations/
└── tests/
    ├── unit/disputes/
    ├── integration/disputes/
    └── contract/

frontend/
├── src/
│   ├── pages/disputes/
│   ├── components/disputes/
│   └── services/disputesApi/
└── tests/disputes/
```

**Structure Decision**: Use a backend/frontend split because the spec explicitly targets an existing FastAPI + Postgres backend and React + TypeScript frontend. The benchmark workspace is planning-only, so these are the implementation repository paths the build team should map to the actual billing portal codebase.

## Complexity Tracking

No constitution or AGENTS gate violations were identified for this planning run.
