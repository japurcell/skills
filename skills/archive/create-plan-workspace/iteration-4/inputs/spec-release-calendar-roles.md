# Feature Spec: Release Calendar Role Controls

## Problem

Release coordinators and engineers share one calendar view with no role-specific permissions, causing accidental edits and unclear approvals.

## Goals

- Add role-based permissions for release planning calendar.
- Support explicit approval workflow for release windows.

## Requirements

1. Roles: `viewer`, `editor`, `release_manager`.
2. `viewer` can read only; `editor` can propose changes; `release_manager` can approve/reject.
3. Release window states: `draft`, `proposed`, `approved`, `blocked`, `cancelled`.
4. Every state transition requires a reason and actor metadata.
5. Integrate with notification service for approvals and rejections.
6. Provide endpoint to list pending approvals grouped by product area.

## Non-Functional

- Calendar UI interactions should stay under 150ms perceived latency.
- Must support 300 concurrent users during planning week.

## Constraints

- Existing app is a monorepo with Node backend and Next.js frontend.
- Tests currently use Playwright and Jest.
- Teams require backward-compatible API changes for one quarter.
