---
name: prd
description: Create an implementation-ready PRD for a feature. Use for product requirements, feature specs, user stories, planning, or preparing for `/prd-to-tasks`. Do not implement or write code.
disable-model-invocation: true
---

# /prd

Create an unambiguous, implementation-ready PRD from the conversation and codebase context.

## Rules
- Do not implement or write code.
- Do not interview the user; make reasonable assumptions and document them. If unsafe/contradictory, stop and report the blocker.
- Follow existing codebase patterns. Prefer YAGNI.
- If codebase context is missing, invoke `explore`.
- Check available workspace conventions: `AGENTS.md`, scoped docs, repo docs, scripts, tests, existing modules/patterns.
- Do not invent commands, files, paths, schemas, URLs, literals, DB objects, or conventions. Use exact names only when verified or clearly inferable.
- Define each path, schema, key format, command, contract, and rollout order in one canonical place, then reference it consistently.
- Never overwrite, rename, or delete an existing PRD.
- Require named test targets when inferable: exact test file/class names and intended assertions. Avoid vague metrics such as “100% tests pass.”

## Save path

Save to `.agents/scratchpad/[feature-name]/prd.md`, where `[feature-name]` is short kebab-case. If it exists, use `[feature-name]-2`, `-3`, etc. Create directories as needed. Verify the final file exists. If saving fails, stop and report failure.

## Workflow

1. If codebase context is missing, invoke the `explore` skill.
2. Identify existing patterns, affected modules, contracts, test seams, risks, edge cases, rollout constraints, and conflicts with workspace conventions.
3. Draft the PRD using the template below.
4. Validate consistency across sections, especially requirements, acceptance criteria, technical decisions, Definition of Done, paths, schemas, commands, examples, and execution order.
5. Resolve conflicts by preferring the most specific implementation-nearest source; document assumptions. If unclear, stop and report the blocker.
6. Save to the verified unused path.
7. Final response: feature short name, PRD path, validation status `pass`/`fail`, readiness for `/prd-to-tasks`.

<prd-template>

# PRD: [Feature Name]

## Overview

Describe the problem, users, value, and proposed solution.

## Assumptions

List assumptions made because the user was not interviewed.

## Goals

- Specific measurable goal

## User Stories

List enough stories to cover user-visible capabilities, roles, states, and edge cases without turning implementation tasks into stories. Each story should describe one coherent behavior slice.

Format:

```md
### US-001: [Title]

**Story:** As a [user], I want [capability] so that [benefit].

**Acceptance Criteria:**

- [ ] Concrete, observable behavior
- [ ] Relevant edge/failure case
- [ ] Relevant build/typecheck/lint/test commands pass, using exact commands when inferable
- [ ] For UI: Verify in browser using playwright-cli skill

**Design Guidance:**

- Follow existing [pattern/module/component] because [rationale].
```

Acceptance criteria rules:

- Describe observable outcomes, not implementation steps.
- Define done using concrete inputs, outputs, states, side effects, and success/failure behavior.
- Include relevant error paths: validation, permissions, timeouts, dependency failure, partial failure, invalid/corrupted state, and recovery.
- For CLI/API/data features, specify contracts: inputs, outputs, status codes, exit codes, stdout/stderr, schemas, and side effects.
- Use measurable performance targets when performance matters.

## Functional Requirements

- FR-1: The system must... Related: US-001
- FR-2: When..., the system must... Related: US-002, US-003

Every functional requirement must have a stable `FR-*` ID and map to at least one user story, acceptance criterion, testing-plan item, or execution-sequence item.

## Technical Decisions

Document only relevant decisions: affected modules/interfaces, contracts, dependencies, migrations, rollout, compatibility, security/privacy, observability, performance, UI/accessibility, and rationale tied to discovered patterns.

Define each schema, key format, identifier, or contract in one canonical place and reference it elsewhere. For cleanup, retries, fallbacks, cancellation, or recovery, specify triggers, guarantees, limits, and non-goals. For observability, specify event conditions, severity/cardinality, and rate limits when relevant.

Do not include file paths or code unless necessary to capture a decision precisely.

## Definition of Done

- Relevant build, typecheck, lint, and test commands pass, using exact commands when inferable.
- Required behavior is covered by automated tests at the highest practical seam.
- Edge/failure cases listed in this PRD are verified.
- For UI changes, browser verification using playwright-cli skill is completed.
- Rollout, migration, cleanup, compatibility, observability, privacy/security, and accessibility requirements are satisfied where applicable.

## Execution Sequence

List user stories or requirement groups in recommended implementation order.

For each sequence item, specify:

- IDs covered, such as `US-001` or `FR-1`
- Dependencies
- Whether order is mandatory or recommended
- Parallelizable work
- Rollout, migration, cleanup, verification, or removal steps

Do not imply mandatory ordering unless required by data, API, migration, rollout, safety, or compatibility constraints.

## Testing Plan

Describe the highest practical test seam, preferring existing seams and minimizing new ones. Test external behavior, not implementation details. Reference similar existing tests/patterns.

When inferable, include exact commands/scripts, such as `npm test`, `pnpm typecheck`, `pytest path/to/test.py`, or a repo-specific verification script. Do not invent commands.

Specify named test targets when inferable:
- File/class: `[ExactTestFileOrClass]`
- Assertion: `[SpecificBehaviorOrContractAssertionName]`
- Covers: `FR-*` / `US-*`

Include a compact edge-case matrix when relevant: invalid inputs, missing dependencies, permissions/environment constraints, concurrency/races, partial failure, fallback behavior, cleanup, and recovery.

## Success Metrics

- Measurable success condition

For performance metrics, specify measurement protocol: environment, input size/dataset, warm vs. cold state, percentile/average, sample size, and threshold.

## Out of Scope

List what this PRD explicitly does not include.

</prd-template>

## Validation

- [ ] Codebase context and workspace conventions were checked when available.
- [ ] Existing PRD was not overwritten, renamed, or deleted.
- [ ] Scope and out-of-scope items are clear.
- [ ] Technical decisions include rationale and discovered-pattern references.
- [ ] Sections are internally consistent across requirements, acceptance criteria, technical decisions, Definition of Done, paths, schemas, commands, and execution order.
- [ ] Paths, schemas, commands, key formats, contracts, and rollout order are defined once and referenced consistently.
- [ ] Functional requirements use stable IDs and map to stories, acceptance criteria, testing, or execution sequence.
- [ ] Testing Plan names exact test files/classes/assertions when inferable and avoids vague pass metrics.
- [ ] Execution Sequence distinguishes mandatory dependencies from recommended order and identifies parallelizable work.
- [ ] Edge cases and negative paths are captured in acceptance criteria or Testing Plan.
- [ ] Exact verification commands are included when inferable; none are invented.
- [ ] PRD saved at `.agents/scratchpad/[feature-name]/prd.md` with `[feature-name]` suffixed with `-2`, `-3`, etc. if needed.
- [ ] No existing PRD was overwritten.
- [ ] Final response includes feature short name, PRD path, validation status, and readiness for `/prd-to-tasks`.
