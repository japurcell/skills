# Implementation Plan: Release Calendar Role Controls

**Date**: March 26, 2026 | **Spec**: /home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-release-calendar-roles.md`

## Summary

Implement role-based controls and explicit approval workflow for release planning windows in the shared calendar. The feature introduces three roles (`viewer`, `editor`, `release_manager`), enforced state transitions with required reason and actor metadata, notification events for approval outcomes, and a pending-approvals API grouped by product area. Design is backward-compatible for one quarter by versioning new write paths and preserving existing read behavior.

## Technical Context

**Language/Version**: Node.js 20 LTS (backend), Next.js 14 (frontend)
**Primary Dependencies**: Express/Fastify-compatible backend framework, existing auth middleware, notification service client, PostgreSQL driver/ORM
**Storage**: PostgreSQL for release windows, transition history, and pending-approval query indexes
**Testing**: Jest (unit/integration), Playwright (end-to-end)
**Target Platform**: Web application (Node backend + Next.js frontend)
**Project Type**: Monorepo web application
**Performance Goals**: Calendar interactions under 150ms perceived latency; pending approvals endpoint p95 under 200ms at 300 concurrent users
**Constraints**: Backward-compatible API changes for one quarter; every transition must persist reason + actor metadata
**Scale/Scope**: Up to 300 concurrent planning-week users; release windows segmented by product area

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-research gate: PASS

- No `AGENTS.md` file detected in workspace scope; no additional repository policy blockers found.
- Spec constraints are actionable and sufficient for architecture and planning.

Post-design gate: PASS

- Artifacts are internally consistent: role model, state machine, API contracts, and quickstart execution flow align.
- Quickstart depth gate passed: required headings present, includes concrete commands and expected outcomes.
- No unresolved technical unknowns that block `/create-tasks`.

## Project Structure

### Documentation (this feature)

```text
/home/adam/.agents/skills/create-plan-workspace/iteration-2/release-calendar-role-controls/with_skill/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── release-windows-api.openapi.yaml
├── report.md
└── output.md
```

### Source Code (target monorepo per spec constraints)

```text
backend/
├── src/
│   ├── api/release-windows/
│   ├── services/release-approval/
│   ├── auth/role-guards/
│   └── notifications/
└── tests/
    ├── integration/release-windows/
    └── unit/release-approval/

frontend/
├── src/
│   ├── features/release-calendar/
│   ├── components/approval-queue/
│   └── services/release-windows-client/
└── tests/
    └── e2e/release-calendar/
```

**Structure Decision**: Use the web-application split (`backend/`, `frontend/`) explicitly stated in the spec constraints (Node backend + Next.js frontend), with feature-scoped modules for release windows, role checks, and approval queue UX.

## Complexity Tracking

No policy violations requiring justification.
