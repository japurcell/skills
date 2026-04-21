# Implementation Plan: Release Calendar Role Controls

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/inputs/spec-release-calendar-roles.md`

## Summary

Introduce role-based authorization and an audited approval workflow for the release planning calendar. The implementation keeps existing read behavior backward-compatible for one quarter while adding additive workflow endpoints, immutable transition history, notification delivery for approval outcomes, and a release-manager approvals queue grouped by product area. The backend remains the source of truth for permissions and state transitions; the Next.js frontend adds role-aware affordances and low-latency interaction patterns on top of those additive APIs.

## Technical Context

**Language/Version**: Node.js 20 LTS backend, TypeScript 5.x shared application code, Next.js 14 App Router frontend  
**Primary Dependencies**: Existing Node HTTP API framework, authentication middleware with role claims, PostgreSQL data access layer, notification service client, Next.js App Router, Jest, Playwright  
**Storage**: PostgreSQL tables for `release_windows`, `release_window_transitions`, role assignments (or equivalent authorization mapping), and a `notification_outbox_events` queue  
**Testing**: Jest for backend unit/integration coverage; Playwright for role-aware calendar end-to-end coverage  
**Target Platform**: Browser clients backed by a Node API in a monorepo deployment  
**Project Type**: Monorepo web application (Node backend + Next.js frontend)  
**Performance Goals**: Keep calendar interactions under 150ms perceived latency; keep pending approvals read latency under 200ms p95 while supporting 300 concurrent users during planning week  
**Constraints**: Backward-compatible API changes for one quarter; every transition requires `reason` and actor metadata; approval/rejection must trigger notification delivery; permission checks must be authoritative on the backend  
**Scale/Scope**: Three roles (`viewer`, `editor`, `release_manager`) across release-window write paths, grouped approval dashboards by product area, 300 concurrent users during planning week

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

Pre-research gate: PASS

- `/home/adam/dev/personal/skills/AGENTS.md` only constrains how this benchmark repository is edited; it does not block generation of planning artifacts in `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-2/with_skill/run-1/outputs`.
- Repository guidance explicitly treats `skills/*-workspace/**/outputs/` as benchmark fixtures, so writing the plan package under the run output directory is compliant.
- No repository instruction requires source-code edits or agent-context changes for this execution.

Post-design gate: PASS

- No net-new technology was introduced beyond the spec's Node backend, Next.js frontend, Jest, Playwright, PostgreSQL, and OpenAPI-compatible HTTP interface documentation.
- `plan.md`, `research.md`, `data-model.md`, `quickstart.md`, and `contracts/release-calendar-role-controls.openapi.yaml` are internally consistent on roles, states, contract shapes, rollout order, and validation scope.
- `quickstart.md` satisfies the required heading order and includes concrete commands with expected results in both Implement and Validate sections.
- `report.md` conforms to the required 5-section output contract.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-3/eval-2/with_skill/run-1/outputs/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
│   └── release-calendar-role-controls.openapi.yaml
├── report.md
└── output.md
```

### Source Code (implementation target per spec constraints)

```text
backend/
├── src/
│   ├── api/release-windows/
│   │   ├── routes.ts
│   │   ├── handlers.ts
│   │   ├── validators.ts
│   │   └── presenters.ts
│   ├── auth/
│   │   ├── role-claims.ts
│   │   └── release-calendar-policy.ts
│   ├── domain/release-windows/
│   │   ├── release-window.ts
│   │   ├── transition-service.ts
│   │   ├── state-machine.ts
│   │   └── repository.ts
│   ├── integrations/notifications/
│   │   └── release-window-events.ts
│   ├── jobs/
│   │   └── notification-outbox-dispatcher.ts
│   └── db/migrations/
└── tests/
    ├── integration/release-windows/
    └── unit/release-windows/

frontend/
├── src/
│   ├── app/release-calendar/page.tsx
│   ├── features/release-calendar/
│   │   ├── components/
│   │   │   ├── CalendarToolbar.tsx
│   │   │   ├── PendingApprovalsPanel.tsx
│   │   │   ├── ReleaseWindowCard.tsx
│   │   │   └── TransitionReasonDialog.tsx
│   │   ├── hooks/
│   │   │   ├── usePendingApprovals.ts
│   │   │   └── useReleaseWindowMutations.ts
│   │   ├── permissions/
│   │   │   └── can-transition.ts
│   │   └── types/
│   │       └── release-window.ts
│   └── services/release-windows-client.ts
└── tests/
    └── e2e/release-calendar/
```

**Structure Decision**: Use the spec-defined backend/frontend monorepo split. Keep authorization, state-transition validation, grouped approval queries, and notification side effects on the backend. Keep the Next.js frontend focused on role-aware rendering, mutation UX, and approval queue presentation so `/create-tasks` can sequence work cleanly across backend-first and frontend-second slices.

## Complexity Tracking

No policy violations requiring justification.

## Implementation Slices

### Slice 1: Role resolution and authorization boundary

- Normalize effective calendar role lookup for each authenticated actor, with optional product-area scoping.
- Centralize capability checks in a shared `release-calendar-policy` module so route handlers, domain services, and background paths cannot drift.
- Add additive read metadata (`availableTransitions`, `canApprove`, `canEdit`) without breaking legacy consumers.
- Exit criteria: `viewer` is always read-only; `editor` can propose/cancel within allowed states; `release_manager` can approve/reject/block.

### Slice 2: Audited workflow persistence

- Create or extend the `release_windows` persistence model with optimistic locking (`version`).
- Add append-only `release_window_transitions` records that capture `from_state`, `to_state`, `reason`, `actor_id`, `actor_role`, and timestamps for every successful transition.
- Encode the allowed state machine in a single service so illegal transitions fail before persistence.
- Exit criteria: every state change produces one immutable transition row and one updated canonical release-window row.

### Slice 3: Additive HTTP contracts and compatibility window

- Add `POST /api/release-windows/{releaseWindowId}/transitions` as the single write surface for proposals, approvals, rejections/blocks, and cancellations.
- Add `GET /api/release-windows/approvals/pending` to return grouped pending approvals by product area with stable ordering and pagination.
- Preserve existing read routes and response fields for at least one quarter; new fields must be additive and optional for old clients.
- Exit criteria: manager queue and transition flows work without forcing existing calendar readers to migrate immediately.

### Slice 4: Notification delivery after commit

- Emit approval and rejection notifications only after the corresponding state transition commits.
- Use a durable outbox table plus dispatcher job so notification failures do not roll back release-window state.
- Expose operational metrics for retry count, dead-lettering, and last dispatch error.
- Exit criteria: committed approval outcomes always enqueue a deliverable event; retries are observable and idempotent.

### Slice 5: Role-aware Next.js experience

- Render the calendar page with Server Components for initial data fetch and narrowly scoped Client Components for interactive transition controls.
- Show read-only interactions for `viewer`, proposal controls for `editor`, and approval/rejection controls plus grouped queue visibility for `release_manager`.
- Require a reason dialog for every workflow action and refetch queue/calendar data after successful mutations.
- Exit criteria: users only see controls allowed by their role and every transition submission includes a reason before the request is sent.

### Slice 6: Validation, rollout, and observability

- Add Jest coverage for role policy decisions, state-machine legality, optimistic-lock conflicts, grouped pending-approval queries, and outbox creation.
- Add Playwright coverage for viewer/editor/manager paths using distinct authenticated states because these tests mutate server-side workflow state.
- Roll out backend schema/API support before enabling frontend controls; monitor p95 latency, authorization denials, and notification retries throughout the compatibility window.
- Exit criteria: automated coverage proves the workflow end to end and rollout sequencing preserves backward compatibility.
