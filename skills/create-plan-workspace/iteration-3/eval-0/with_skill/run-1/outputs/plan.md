# Implementation Plan: Billing Disputes Workflow

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-billing-disputes.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-billing-disputes.md`

## Summary

Add a disputes workflow to the billing portal with role-aware creation, reassignment, outcome control, SLA tracking, immutable timeline history, API coverage, and monthly CSV export. The implementation should use the existing FastAPI + PostgreSQL backend and React + TypeScript frontend, publish an OpenAPI 3.1 contract, keep audit history append-only, and use indexed keyset list queries to hold the disputes list endpoint under the required 250 ms p95 at a 50k-dispute dataset.

## Technical Context

**Language/Version**: Python 3.10+ (FastAPI backend), TypeScript 5.x (React frontend)  
**Primary Dependencies**: FastAPI, Pydantic response models, PostgreSQL, React, TypeScript, OpenAPI 3.1 tooling, Python `csv` module  
**Storage**: PostgreSQL for dispute state and append-only dispute activity events  
**Testing**: `pytest` for backend integration/contract/performance checks; existing frontend test runner (React Testing Library or equivalent) plus TypeScript build validation  
**Target Platform**: Linux-hosted internal web application  
**Project Type**: Web application with backend API and frontend UI  
**Performance Goals**: disputes list endpoint p95 under 250 ms at 50k disputes; detail/timeline reads remain index-backed; monthly CSV export completes without long-running table scans  
**Constraints**: immutable audit trail, SLA warning at 24h and breach at 48h, manager-only reassignment/outcome override, OpenAPI-preferred service contracts, benchmark artifacts limited to /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs  
**Scale/Scope**: internal support workflow for tens of thousands of disputes and monthly operational outcome reporting

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Read /home/adam/dev/personal/skills/AGENTS.md plus linked guidance in:
  - /home/adam/dev/personal/skills/docs/agent-guides/repo-layout.md
  - /home/adam/dev/personal/skills/docs/agent-guides/authoring.md
  - /home/adam/dev/personal/skills/docs/agent-guides/validation.md
- Gate criteria from repository instructions:
  - Artifacts must live in a `*-workspace/` sibling area, not repository source. **Satisfied** by writing only to /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs.
  - Helper-script guidance prefers `python3` and narrow validation over a nonexistent monorepo test runner. **Satisfied** by using targeted artifact validation only.
  - Normal audits should ignore generated `outputs/` trees. **Satisfied**; no repository source files are modified.
- Pre-research gate: **PASS** — in-scope instructions allow this planning run and reveal no policy conflict.
- Post-design gate: **PASS** — final artifacts remain within the output directory, do not introduce net-new repository technology, and stay aligned with repo guidance.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-0/with_skill/run-1/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── disputes.openapi.yaml
├── report.md
└── output.md
```

### Source Code (target billing portal repository)

```text
backend/
├── app/
│   ├── api/disputes/
│   ├── models/
│   ├── services/disputes/
│   └── jobs/ or workers/
└── tests/
    ├── contract/
    ├── integration/
    └── performance/

frontend/
├── src/
│   └── features/disputes/
│       ├── api/
│       ├── components/
│       ├── hooks/
│       └── pages/
└── src/tests/
```

**Structure Decision**: Use a split web-application structure because the spec explicitly calls out an existing FastAPI/PostgreSQL backend and React/TypeScript frontend. This benchmark workspace does not include the billing portal source tree, so these backend/frontend paths are the implementation targets to confirm in the actual application repository before `/create-tasks` emits file-level work items.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
| --------- | ---------- | ------------------------------------ |
| None | N/A | N/A |
