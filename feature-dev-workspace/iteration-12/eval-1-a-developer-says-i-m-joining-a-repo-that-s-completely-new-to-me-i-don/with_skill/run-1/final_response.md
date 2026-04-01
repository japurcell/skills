## Understanding

You are onboarding into an unfamiliar codebase and want to ship a medium-sized feature safely. In the feature-dev workflow, this is a **Standard track** task: enough complexity to require structured discovery before coding, but not a massive multi-team rewrite.

## How The Feature-Dev Workflow Guides You

1. Discovery

- Clarify the feature goal, boundaries, and constraints (performance, compatibility, rollout expectations).
- Define what success looks like and what is explicitly out of scope.

2. Codebase exploration

- Map architecture and flow for the feature area.
- Find similar features and copy proven patterns.
- Identify integration points: APIs, domain services, state/data model, UI surfaces, background jobs, config, and migrations.
- Read real source files (not just summaries) to ground decisions.

3. Clarifying questions

- Ask only high-leverage questions that change design or behavior.
- Lock down edge cases, failure modes, backward compatibility, and ownership boundaries.

4. Architecture/design choice

- Pick the smallest approach that fits existing patterns.
- Call out trade-offs (speed vs maintainability, local fix vs shared abstraction).

5. Implementation (with TDD)

- Red: write/extend a failing test that proves the feature requirement.
- Green: implement the minimum code to pass.
- Refactor: improve readability/design while keeping tests green.

6. Quality review

- Independent simplification/refactor pass (remove duplication, improve naming/structure).
- Independent code review pass (correctness, regressions, conventions, risk).
- Run targeted validation for behavior, errors, and integration touchpoints.

7. Summary/handoff

- Document what changed, why, risks, and follow-ups so another engineer can continue without rediscovery.

## What Goes Wrong If You Skip Exploration And Jump To Implementation

1. You implement in the wrong layer

- Without architectural mapping, it is easy to add logic in controllers/UI instead of domain/service boundaries.
- Result: harder maintenance, duplicated logic, future bugs.

2. You violate hidden invariants

- Mature codebases often enforce implicit rules (transaction order, idempotency, caching contracts, auth checks).
- Result: subtle production bugs that pass happy-path local testing.

3. You choose patterns the team does not use

- New abstractions might conflict with existing conventions for error handling, dependency injection, state, or API shape.
- Result: painful review cycles and rework.

4. You miss cross-cutting impact

- Feature changes can affect telemetry, permissions, rate limits, migrations, jobs, or downstream consumers.
- Result: regressions outside the files you touched.

5. You write brittle or misaligned tests

- Without understanding the testing strategy (unit/integration/e2e boundaries, fixtures, mocking style), tests either over-mock or over-integrate.
- Result: flaky tests, poor signal, and false confidence.

6. You underestimate scope and sequence

- Unknown dependencies surface late (schema changes, API contracts, feature flags, rollout constraints).
- Result: missed estimates, rushed fixes, and risky merges.

7. You increase rollback risk

- If integration points are discovered only after merge, rollback may be non-trivial due to partial data/state changes.
- Result: longer incident windows.

## Practical Safe Rule

For a medium-sized feature in a new repo, spend early time on exploration to reduce total cycle time. A common pattern is roughly:

- 20-30% discovery + exploration
- 50-60% implementation with TDD
- 20% review/validation and handoff

That front-loaded exploration usually prevents the expensive rework that happens when coding starts from incorrect assumptions.
