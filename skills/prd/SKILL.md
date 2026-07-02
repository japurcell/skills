---
name: prd
description: Create an implementation-ready PRD for a feature. Use when user wants to create/write PRD, product requirements, plan/spec feature, requirements, user stories, prepare for /prd-to-tasks. Do not implement or write code.
disable-model-invocation: true
---

# /prd

Create an unambiguous, implementation-ready PRD from the current conversation and codebase context.

## Rules

- Do not implement the feature or include implementation code.
- Do not interview the user; make reasonable assumptions and document them.
- Follow existing codebase patterns. Prefer YAGNI: exclude unnecessary features and abstractions.
- Never overwrite, rename, or delete an existing PRD.

## Save path

Derive `[feature-name]` in short kebab-case. Save to `.agents/scratchpad/[feature-name]/prd.md`.

If it exists, use `[feature-name]-2`, `-3`, etc. Create directories as needed. Verify the final file exists at the exact path. If saving fails, stop and report failure.

## Workflow

1. **Explore**
   - If codebase context is missing, run `/explore`.

2. **Design**
   - Sketch out the seams at which you're going to test the feature. Existing seams should be preferred to new ones. Use the highest seam possible. If new seams are needed, propose them at the highest point you can. The fewer seams across the codebase, the better - the ideal number is one.

3. **Write and save PRD**
   - Write the PRD using the template below.
   - Save to the verified unused path.

4. **Final response**
   - Include:
     - feature short name
     - PRD path
     - validation status: `pass` or `fail`
     - readiness for `/prd-to-tasks`

<prd-template>

# PRD: [Feature Name]

## Overview

Describe the problem, users, value, and proposed solution.

## Assumptions

List assumptions made because the user was not interviewed.

## Goals

- Specific measurable goal

## User Stories

This list of user stories should be extremely extensive and cover all aspects of the feature. Each story must be small enough for one focused implementation session.

Format:

```md
### US-001: [Title]

**Story:** As a [user], I want [capability] so that [benefit].

**Acceptance Criteria:**

- [ ] Concrete, testable behavior
- [ ] Relevant edge/failure case
- [ ] Relevant build, typecheck, lint, and test commands pass
- [ ] For UI: Verify in browser using playwright-cli skill

**Design Guidance:**

- Follow existing [pattern/module/component] because [rationale].
```

Acceptance criteria rules:

- Describe observable outcomes, not implementation steps.
- Define done using concrete inputs, outputs, states, side effects, and success/failure behavior.
- Include relevant error paths: validation, permissions, timeouts, dependency failure, partial failure, invalid/corrupted state, and recovery.
- For CLI/API/data features, specify relevant contracts: inputs, outputs, status codes, exit codes, stdout/stderr, schemas, and side effects.
- Use measurable performance targets when performance matters.

## Functional Requirements

- FR-1: The system must...
- FR-2: When..., the system must...

## Technical Decisions

Document only relevant decisions: affected modules/interfaces, contracts, dependencies, migrations, rollout, compatibility, security/privacy, observability, performance, UI/accessibility, and rationale tied to discovered patterns.

Specify relevant data contracts, schemas, identifiers, state transitions, compatibility requirements, and migration/rollout behavior precisely. Include matrices only when they clarify compatibility, migration, or state behavior.

Do not include file paths or code unless necessary to capture a decision precisely.

## Testing Plan

Describe the highest practical test seam, preferring existing seams and minimizing new ones. Test external behavior, not implementation details. Identify test levels and reference similar existing tests/patterns.

## Success Metrics

- Measurable success conditions

## Out of Scope

List what this PRD explicitly does not include.

</prd-template>

## Validation

- [ ] Missing codebase context explored, but tokens were not wasted re-exploring the same context
- [ ] Out-of-scope items clearly define scope
- [ ] Technical decisions include rationale and references to discovered patterns
- [ ] PRD saved at `.agents/scratchpad/[feature-name]/prd.md` with `[feature-name]` suffixed with `-2`, `-3`, etc. if needed
- [ ] No existing PRD was overwritten
- [ ] Final response includes feature short name, PRD path, validation status, and readiness for `/prd-to-tasks`
