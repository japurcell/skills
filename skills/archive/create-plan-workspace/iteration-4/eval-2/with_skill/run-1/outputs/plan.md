# Implementation Plan: Release Calendar Role Controls

**Date**: 2026-04-21 | **Spec**: /home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/with_skill/run-1/outputs/spec-release-calendar-roles.md
**Input**: Feature specification from `/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/with_skill/run-1/outputs/spec-release-calendar-roles.md`

## Summary

Add role-based controls to the release planning calendar so `viewer` users stay read-only, `editor` users can draft and propose changes, and `release_manager` users can approve, reject, block, or cancel release windows with explicit reasons and actor metadata. The implementation should preserve one-quarter backward API compatibility by adding an approval-focused transition contract, a grouped pending-approvals endpoint, and asynchronous notification hooks while keeping calendar interactions under 150ms perceived latency for 300 concurrent planning-week users.

## Technical Context

**Language/Version**: Existing monorepo Node.js backend and Next.js frontend using the versions already pinned in the product repository; no net-new runtime is introduced by this plan  
**Primary Dependencies**: Existing authentication/authorization layer, release calendar backend APIs, Next.js calendar UI, notification service integration, OpenAPI-compatible API documentation, Jest, and Playwright  
**Storage**: Existing release-window persistence plus durable transition-history and approval metadata in the current backend datastore; notification delivery continues through the existing notification service  
**Testing**: Existing Jest unit/integration coverage for permission and workflow logic plus Playwright end-to-end coverage for calendar role flows  
**Target Platform**: Internal web-based release planning application backed by Node APIs and a Next.js frontend  
**Project Type**: Monorepo web application  
**Performance Goals**: Keep calendar interactions under 150ms perceived latency and support at least 300 concurrent users during planning week  
**Constraints**: Roles are fixed to `viewer`, `editor`, and `release_manager`; release-window states are fixed to `draft`, `proposed`, `approved`, `blocked`, and `cancelled`; every transition must record reason plus actor metadata; approval and rejection decisions must notify through the existing notification service; new API behavior must be backward-compatible for one quarter; pending approvals must be listable grouped by product area  
**Scale/Scope**: Role-aware calendar reads and edits, explicit approval workflow, immutable transition history, grouped approvals inbox, and notification fan-out for approval/rejection outcomes

## AGENTS.md Check

_GATE: Must pass before Phase 0 research. Re-check after Phase 1 design._

- Reviewed `/home/adam/dev/personal/skills/AGENTS.md`, `/home/adam/dev/personal/skills/docs/agent-guides/repo-layout.md`, and `/home/adam/dev/personal/skills/docs/agent-guides/validation.md`.
- In-scope repository constraints:
  - Helper scripts use `python3`; there is no repo-wide package manifest or single test runner.
  - Repository source should be edited directly before refreshing installed copies; this benchmark run does not edit source.
  - `skills/*-workspace/**/outputs/` is normally ignored during audits, but this run is explicitly writing planning artifacts there.
- **Pre-research gate: PASS** — no AGENTS.md rule blocks generating planning artifacts in the requested output workspace.
- **Post-design gate: PASS** — artifacts remain inside the required output directory, no repository source files were modified, and no agent-context update is needed because the plan reuses the existing Node/Next.js/notification stack.
- **Net-new technology review**: none. The plan stays within the existing monorepo stack and existing notification integration, so `agents-md-refactor` is not required for this benchmark.

## Project Structure

### Documentation (this feature)

```text
/home/adam/dev/personal/skills/skills/create-plan-workspace/iteration-4/eval-2/with_skill/run-1/outputs/
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

### Source Code (repository root)

```text
/home/adam/dev/personal/skills/
├── AGENTS.md
├── docs/
│   └── agent-guides/
│       ├── repo-layout.md
│       └── validation.md
├── skills/
│   ├── create-plan/
│   │   ├── SKILL.md
│   │   └── references/
│   │       └── plan-template.md
│   └── create-plan-workspace/
│       └── iteration-4/eval-2/with_skill/run-1/outputs/
│           ├── spec-release-calendar-roles.md
│           ├── plan.md
│           ├── research.md
│           ├── data-model.md
│           ├── quickstart.md
│           └── contracts/
└── scripts/
    └── copilot-install.sh
```

**Structure Decision**: The benchmark repository only contains the planning skill and output workspace, not the actual product monorepo named in the spec. This plan therefore defines logical implementation surfaces—calendar UI, authorization layer, release-window workflow API, transition-history persistence, and notification integration—while carrying one readiness risk to map those surfaces onto the real monorepo packages during `/create-tasks`.

## Complexity Tracking

No AGENTS.md or repository-policy violations require justification for this planning-only run.
