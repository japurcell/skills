# Feature Spec: Billing Disputes Workflow

## Problem

Support agents handle payment disputes manually across email and spreadsheets, causing slow resolution and inconsistent outcomes.

## Goals

- Add a disputes workflow to the internal billing portal.
- Allow agents to create, assign, and resolve disputes with status tracking.
- Record SLA deadlines and escalation rules.

## Requirements

1. Users with role `agent` can create disputes with invoice ID, customer ID, reason code, and notes.
2. Users with role `manager` can reassign disputes and override outcome.
3. Each dispute has statuses: `open`, `investigating`, `waiting_on_customer`, `resolved`, `rejected`.
4. SLA timer starts at creation; warn at 24 hours, breach at 48 hours.
5. Activity timeline must capture state transitions and comments.
6. Add API endpoints for listing disputes, detail view, transitions, and assignment changes.
7. Export monthly dispute outcomes as CSV.

## Non-Functional

- p95 list endpoint under 250ms for 50k disputes.
- Must preserve immutable audit trail for dispute actions.

## Constraints

- Existing backend stack is Python FastAPI with Postgres.
- Frontend is React + TypeScript.
- Team prefers OpenAPI for service contracts.
