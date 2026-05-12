# Implementation Plan: Release Calendar Role Controls

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/old_skill/run-1/outputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/old_skill/run-1/outputs/spec-release-calendar-roles.md`

## Summary

Add role-based control to the release planning calendar by introducing shared role-aware permission checks, an audited release-window state machine, additive HTTP APIs for proposing and approving release windows, a grouped pending-approvals read model, and asynchronous notification delivery for approvals/rejections. The design preserves backward-compatible API behavior for one quarter while keeping interactive calendar actions responsive for 300 concurrent planning-week users.

## Technical Context

**Language/Version**: Node.js 20 LTS-compatible backend, TypeScript 5.x shared models, Next.js 15-compatible frontend patterns  
**Primary Dependencies**: Existing Node backend framework, Next.js frontend, React client components for interactive calendar controls, authentication middleware with role claims, notification service client, OpenAPI 3.1 API contract  
**Storage**: Existing relational persistence extended with `release_windows`, append-only `release_window_transitions`, and durable notification dispatch records  
**Testing**: Jest for backend/service coverage and contract assertions; Playwright for end-to-end role and approval workflows  
**Target Platform**: Browser clients using a backend + Next.js frontend monorepo deployment  
**Project Type**: Monorepo web application  
**Performance Goals**: Calendar interactions under 150ms perceived latency; pending approvals route efficient enough for 300 concurrent users during planning week  
**Constraints**: One-quarter backward-compatible API changes; every transition must capture reason and actor metadata; notification delivery required for approval/rejection outcomes  
**Scale/Scope**: Three roles (`viewer`, `editor`, `release_manager`) across release-window reads/writes, grouped approval queues by product area, planning-week concurrency of 300 users

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

PASS (pre-research and post-design): repository instructions only constrain where benchmark artifacts are written and do not block planning work. This run writes artifacts solely under `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/old_skill/run-1/outputs`, does not edit repository source, and introduces no net-new technology that would require an agent-context update.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/old_skill/run-1/outputs/
├── spec-release-calendar-roles.md
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
│       └── notification-dispatcher.ts
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

**Structure Decision**: Use the monorepo backend/frontend split stated in the spec. Backend code owns authorization, transition legality, audit persistence, compatibility guarantees, and notification dispatch; the Next.js frontend renders role-aware calendar controls and approval queues by consuming additive APIs.

## Complexity Tracking

No AGENTS.md or instruction-file violations require justification.

## Implementation Slices

### Slice 1: Role exposure and policy checks

- Resolve the actor's effective role (`viewer`, `editor`, `release_manager`) for each release-calendar request.
- Centralize permission evaluation in `release-calendar-policy.ts` so route handlers and domain services cannot drift.
- Preserve existing read flows while adding optional permission metadata (`availableTransitions`, `canApprove`) to responses.

### Slice 2: Audited workflow state machine

- Implement allowed transitions for `draft`, `proposed`, `approved`, `blocked`, and `cancelled`.
- Require `reason`, `actor_id`, and `actor_role` on every state change.
- Persist immutable transition history alongside the canonical release-window row with optimistic locking.

### Slice 3: Approval APIs and grouped read model

- Add `POST /api/release-windows/{id}/transitions` for propose/approve/reject/block/cancel actions.
- Add `GET /api/release-windows/approvals/pending` returning groups keyed by product area.
- Keep existing read endpoints backward compatible for one quarter.

### Slice 4: Notification integration

- Record approval/rejection notifications durably as part of the same transaction as the transition.
- Dispatch notifications asynchronously via a worker/job runner so request latency remains within target.
- Capture retry/error state for operator visibility.

### Slice 5: Role-aware Next.js UI

- Keep the page shell and grouped data loading server-side where possible.
- Isolate interactive editing, approval, and reason-capture flows inside client components.
- Surface permission states clearly so viewers stay read-only, editors can propose, and release managers can approve/reject.
