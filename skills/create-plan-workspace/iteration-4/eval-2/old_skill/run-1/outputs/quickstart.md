# Quickstart: Release Calendar Role Controls

## Prerequisites

- Node.js 20+ and the monorepo package manager used by the release-calendar repository (`pnpm` assumed below).
- Local database and seed data for users in the `viewer`, `editor`, and `release_manager` roles.
- Notification service sandbox credentials or a local stub for approval/rejection delivery.
- Environment configured for the backend API and Next.js frontend packages.

## 1. Implement

1. **Apply the workflow and audit persistence from `plan.md` slices 2 and 4.**
   - Command: `pnpm --filter backend db:migrate && pnpm --filter backend dev`
   - Expected outcome: the backend starts with `release_windows`, `release_window_transitions`, and `notification_dispatch_records` available, plus additive transition and pending-approvals routes aligned with `contracts/release-calendar-role-controls.openapi.yaml`.

2. **Wire shared role/state types and centralized policy checks.**
   - Command: `pnpm --filter backend test -- release-windows-policy`
   - Expected outcome: role capability rules from `research.md` Decision 1 are enforced consistently and stale/illegal transitions fail before state changes are persisted.

3. **Add the role-aware Next.js calendar UI from `plan.md` slice 5.**
   - Command: `pnpm --filter frontend dev`
   - Expected outcome: viewers see read-only calendar cards, editors can open a reason dialog to propose changes, and release managers see grouped pending approvals with approve/block actions backed by the additive APIs.

## 2. Validate

1. **Run focused automated coverage for backend workflow and dispatch behavior.**
   - Command: `pnpm --filter backend test -- release-windows`
   - Expected outcome: Jest verifies permission checks, legal/illegal transitions, optimistic locking, audit-row creation, compatibility response fields, and durable notification-dispatch record creation.

2. **Run browser-level role workflow coverage.**
   - Command: `pnpm --filter frontend test:e2e -- release-calendar`
   - Expected outcome: Playwright proves viewer/editor/release-manager UX paths, reason capture, grouped approvals, and read-only protections without flaky waits.

3. **Smoke-test the manager queue contract.**
   - Command: `curl -s http://localhost:3000/api/release-windows/approvals/pending | jq '.groups'`
   - Expected outcome: the response is grouped by `productArea`, contains only `proposed` windows, and manager-only actions remain absent or forbidden for lower roles.

## 3. Rollout/Operate

- Deploy backend schema/API support before enabling the new frontend controls so legacy readers stay functional during the compatibility quarter.
- Monitor calendar route latency, pending-approval queue latency, dispatcher retry/failure counts, and authorization-denial counts by role.
- Keep approval/rejection state authoritative even if notification delivery fails; operators should replay failed records instead of asking users to resubmit transitions.
- After the one-quarter compatibility window, remove deprecated consumer assumptions only after confirming downstream clients have moved to the additive workflow fields/endpoints.
