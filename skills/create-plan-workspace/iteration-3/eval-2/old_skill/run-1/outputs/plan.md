# Implementation Plan: Release Calendar Role Controls

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-release-calendar-roles.md`

## Summary

Add role-based control to the release planning calendar by introducing backend authorization, an audited release-window state machine, grouped pending-approval APIs, notification delivery for approval decisions, and role-aware Next.js UI affordances. Delivery stays backward-compatible for one quarter by keeping existing read flows intact and layering new write/approval capabilities through additive endpoints and fields.

## Technical Context

**Language/Version**: Node.js 20 LTS backend, TypeScript 5.x shared code, Next.js 14 frontend  
**Primary Dependencies**: Existing Node HTTP API framework, Next.js app router, authentication middleware with role claims, PostgreSQL data access layer, notification service client  
**Storage**: PostgreSQL tables for `release_windows`, immutable `release_window_transitions`, and notification outbox events  
**Testing**: Jest for backend unit/integration coverage; Playwright for role-aware calendar e2e flows  
**Target Platform**: Browser clients using a Node backend in a monorepo deployment  
**Project Type**: Monorepo web application (backend + frontend)  
**Performance Goals**: Calendar interactions remain under 150ms perceived latency; pending approvals endpoint stays under 200ms p95 while supporting 300 concurrent planning-week users  
**Constraints**: One-quarter backward-compatible API behavior; every state transition must capture reason and actor metadata; approval/rejection must integrate with notification delivery  
**Scale/Scope**: Three roles across all release-window write paths, approval dashboards grouped by product area, 300 concurrent users during planning week

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-research gate: PASS

- `/home/adam/dev/personal/skills/AGENTS.md` contains repository authoring guidance only and does not block generation of planning artifacts.
- The benchmark is scoped to writing files only under `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-2/old_skill/run-1/outputs`, which is consistent with the repository guidance to treat workspace outputs as fixtures.

Post-design gate: PASS

- No net-new technology was introduced beyond the spec's Node.js, Next.js, Jest, and Playwright stack, so no agent-context update is required.
- `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/release-calendar-role-controls.openapi.yaml` are internally consistent and ready for `/create-tasks`.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-2/old_skill/run-1/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── release-calendar-role-controls.openapi.yaml
├── report.md
└── output.md
```

### Source Code (implementation target)

```text
backend/
├── src/
│   ├── api/release-windows/
│   │   ├── routes.ts
│   │   ├── handlers.ts
│   │   ├── validators.ts
│   │   └── presenters.ts
│   ├── auth/
│   │   └── release-calendar-policy.ts
│   ├── domain/release-windows/
│   │   ├── entities/
│   │   │   ├── release-window.ts
│   │   │   └── release-window-transition.ts
│   │   ├── state-machine.ts
│   │   ├── service.ts
│   │   └── repository.ts
│   ├── integrations/notifications/
│   │   └── release-window-approvals.ts
│   └── jobs/
│       └── notification-outbox-dispatcher.ts
└── tests/
    ├── integration/release-windows/
    └── unit/domain/release-windows/

frontend/
├── src/
│   ├── app/(release-calendar)/calendar/page.tsx
│   ├── features/release-calendar/
│   │   ├── components/
│   │   │   ├── PendingApprovalsPanel.tsx
│   │   │   ├── ReleaseWindowCard.tsx
│   │   │   └── TransitionReasonDialog.tsx
│   │   ├── hooks/
│   │   │   ├── usePendingApprovals.ts
│   │   │   └── useReleaseWindows.ts
│   │   └── permissions/
│   │       └── can-transition.ts
│   └── services/release-windows-client.ts
└── tests/
    └── e2e/release-calendar/
```

**Structure Decision**: Use the spec-constrained backend/frontend monorepo split, keeping permission enforcement and workflow validation on the backend while the Next.js frontend consumes additive APIs and renders role-aware affordances. The notification outbox dispatcher is isolated from request handling so approval actions stay responsive.

## Complexity Tracking

No policy violations requiring justification.

## Implementation Slices

### Slice 1: Authorization and role exposure

- Extend backend request context so every release-calendar mutation resolves the actor's effective role (`viewer`, `editor`, `release_manager`) for the relevant product area.
- Add centralized policy helpers so route handlers and domain services share the same authorization decisions.
- Preserve existing read endpoints and add additive response metadata (`availableTransitions`, `canApprove`) instead of breaking existing consumers.

### Slice 2: Release-window workflow and audit persistence

- Implement an explicit transition state machine covering `draft`, `proposed`, `approved`, `blocked`, and `cancelled`.
- Require `reason`, `actor_id`, `actor_role`, and timestamp on every state change.
- Persist immutable transition records alongside the canonical `release_windows.state` update under optimistic locking.

### Slice 3: Approval APIs and grouped read model

- Add `POST /release-windows/{id}/transitions` for workflow actions and `GET /release-windows/approvals/pending` for grouped pending approvals.
- Return pending approvals grouped by `productArea` with stable ordering and pagination so manager dashboards stay efficient.
- Keep all API changes additive for the one-quarter compatibility window.

### Slice 4: Notification delivery

- Publish `release_window.approved` and `release_window.rejected` events only after the database transaction commits.
- Use an outbox table and dispatcher job so transient notification failures do not roll back user-visible state changes.
- Track retry count and dead-letter escalation for operational visibility.

### Slice 5: Role-aware frontend workflow

- Render read-only calendar behavior for `viewer`, proposal actions for `editor`, and approval/rejection controls for `release_manager`.
- Require a transition-reason modal before submit and show inline state badges plus transition history.
- Add a pending approvals panel grouped by product area with optimistic refresh after approval decisions.

### Slice 6: Verification and rollout safety

- Add Jest coverage for role policies, transition legality, audit persistence, grouped pending-approval queries, and notification publishing.
- Add Playwright scenarios for viewer/editor/manager flows and regression coverage for backward-compatible reads.
- Roll out backend changes before frontend activation and monitor latency plus notification retry metrics through the compatibility window.
