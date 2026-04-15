# Implementation Plan: Release Calendar Role Controls

**Date**: March 26, 2026 | **Spec**: /home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/.agents/skills/create-plan-workspace/iteration-2/inputs/spec-release-calendar-roles.md`

## Summary

Introduce role-based permissions and approval workflow controls for release calendar windows. The implementation adds role-aware APIs and UI behavior for `viewer`, `editor`, and `release_manager`, enforces audited state transitions with required reason/actor metadata, emits notifications on approval decisions, and provides a grouped pending-approvals endpoint by product area. Delivery preserves backward compatibility for one quarter by keeping existing read behavior unchanged and adding additive fields/endpoints.

## Technical Context

**Language/Version**: Node.js 20 LTS (backend), TypeScript 5.x, Next.js 14 (frontend)
**Primary Dependencies**: Backend HTTP framework (Express/Fastify-compatible), existing auth middleware/JWT role claims, notification service client, PostgreSQL access layer (ORM/query builder)
**Storage**: PostgreSQL tables for release windows and transition audit history
**Testing**: Jest (unit/integration), Playwright (end-to-end)
**Target Platform**: Browser clients against Node API in monorepo deployment
**Project Type**: Monorepo web application (backend + frontend)
**Performance Goals**: Calendar UI interactions remain under 150ms perceived latency; pending approvals endpoint p95 < 200ms at 300 concurrent users
**Constraints**: Backward-compatible API behavior for one quarter; every state transition must include reason and actor metadata; integrate with existing notification service for approve/reject outcomes
**Scale/Scope**: 300 concurrent users during planning week; role checks across all release-window write paths

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-research gate: PASS

- No `AGENTS.md` or additional scoped instruction files were found in repository scope.
- Spec provides sufficient, actionable requirements to complete implementation-ready planning artifacts.

Post-design gate: PASS

- Plan, research decisions, data model, contracts, and quickstart are internally consistent.
- All Technical Context unknowns resolved with concrete implementation decisions.
- Artifacts are ready for `/create-tasks` decomposition.

## Project Structure

### Documentation (this feature)

```text
/home/adam/.agents/skills/create-plan-workspace/iteration-2/release-calendar-role-controls/old_skill/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── release-calendar-role-controls.openapi.yaml
├── report.md
└── output.md
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── api/release-windows/
│   │   ├── routes.ts
│   │   ├── handlers.ts
│   │   └── schemas.ts
│   ├── auth/
│   │   └── role-guards.ts
│   ├── domain/release-windows/
│   │   ├── state-machine.ts
│   │   ├── service.ts
│   │   └── repository.ts
│   └── integrations/notifications/
│       └── release-events.ts
└── tests/
    ├── integration/release-windows/
    └── unit/domain/release-windows/

frontend/
├── src/
│   ├── features/release-calendar/
│   │   ├── components/
│   │   ├── hooks/
│   │   └── state/
│   └── services/release-windows-client/
└── tests/
    └── e2e/release-calendar/
```

**Structure Decision**: Use explicit backend/frontend monorepo layout aligned to the spec constraint (Node backend + Next.js frontend), with role guards and state machine logic isolated in backend domain modules and role-aware UI controls in the release calendar feature module.

## Complexity Tracking

No policy violations requiring justification.
