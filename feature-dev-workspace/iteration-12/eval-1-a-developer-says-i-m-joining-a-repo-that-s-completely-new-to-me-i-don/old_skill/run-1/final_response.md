## Understanding

You are joining an unfamiliar repo and want to implement a medium-sized feature safely. This is exactly **Standard Track** in the feature-dev workflow: enough moving parts to require real discovery, but not so massive that you need a heavyweight process.

## How The Feature-Dev Workflow Guides You Safely

1. **Discovery (scope + intent first)**

- Define the feature goal, non-goals, and constraints.
- Turn vague requests into concrete acceptance criteria.
- Result: you avoid solving the wrong problem.

2. **Codebase Exploration (architecture before edits)**

- Trace existing flows related to your feature (entry points, data flow, side effects).
- Identify 5-10 key files that represent the true implementation path.
- Find existing patterns for validation, errors, permissions, logging, and tests.
- Result: your design aligns with how this repo already works.

3. **Clarifying Questions (only high-leverage unknowns)**

- Ask questions that change implementation shape: edge cases, API contracts, backward compatibility, rollout constraints.
- State assumptions explicitly when ambiguity is minor.
- Result: fewer surprises and less rework.

4. **Architecture Design (right level for medium feature)**

- Compare 1-2 realistic approaches only where trade-offs are real.
- Choose the approach that best matches existing conventions and risk tolerance.
- Result: deliberate decisions, not accidental architecture drift.

5. **Implementation (TDD, small slices)**

- Implement in ordered slices with red-green-refactor loops.
- Keep changes localized, verify each slice, and update tests continuously.
- Result: steady progress with fast feedback and controlled risk.

6. **Quality Review (independent checks)**

- Run an independent review pass for correctness, simplicity, and convention fit.
- Fix high-severity issues early.
- Result: fewer regressions and cleaner final code.

## What Goes Wrong If You Skip Exploration And Jump To Coding

1. **You optimize the wrong layer**

- You might edit a surface component while the real behavior is orchestrated elsewhere.
- Outcome: duplicated logic, broken abstractions, and fragile patches.

2. **You violate implicit architecture contracts**

- Unknown invariants (transaction boundaries, event ordering, cache rules, auth checks) get bypassed.
- Outcome: subtle production bugs that unit tests may not catch.

3. **You miss existing extension points**

- Instead of plugging into established hooks/services, you add parallel paths.
- Outcome: inconsistent behavior and long-term maintenance cost.

4. **You choose the wrong test strategy**

- Without learning the repo’s testing pyramid and fixtures, tests become flaky, slow, or low-signal.
- Outcome: false confidence and CI churn.

5. **You break cross-cutting concerns silently**

- Logging, metrics, feature flags, localization, accessibility, and permissions are often pattern-driven.
- Outcome: feature “works locally” but fails operational or compliance expectations.

6. **You underestimate blast radius**

- Medium-sized features often touch contracts used by other modules.
- Outcome: backward-compatibility regressions and integration breakage.

7. **You create avoidable rework**

- Clarifications discovered late force redesign after code is already written.
- Outcome: wasted cycles, delayed delivery, and review fatigue.

## Practical Rule Of Thumb

For a medium feature in a new repo, spend early effort roughly like this:

- 20-30% understanding and exploration
- 60-70% implementation in validated slices
- 10-20% review and hardening

That front-loaded exploration is not overhead; it is risk removal. It shortens total lead time by preventing wrong turns.

## Recommendation

Follow Standard Track explicitly:

- Do focused discovery and code exploration first.
- Ask only blocking questions.
- Pick one recommended design aligned with current patterns.
- Implement incrementally with tests.
- Run independent quality review before calling it done.

That is the safest way to move quickly in an unfamiliar codebase without accumulating hidden defects.
