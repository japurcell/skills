---
name: feature-dev
description: Use when the user asks to add, build, implement, design, plan, extend, refactor, or coordinate a feature or medium-to-large code change in an unfamiliar codebase. Trigger on phrases such as "add a feature", "implement X", "build support for X", "extend this subsystem", "design this change", "make an implementation plan", "coordinate this refactor", "update multiple files", "figure out how to add X", or "plan and implement X". Best for multi-file work requiring codebase exploration, architecture trade-offs, clarifying questions, implementation sequencing, TDD, refactoring, or review. Do not use for tiny bug fixes, isolated one-file edits, simple explanations, or fully specified straightforward changes ready for direct implementation.
argument-hint: Optional feature description
disable-model-invocation: true
---

# Feature Development

Deliver features with process scaled to scope, ambiguity, and risk.

Initial request: $ARGUMENTS

## Non-Negotiables

- Use `TodoWrite` throughout.
- Choose and state one track up front: `Light`, `Standard`, or `Deep`.
- Ask only questions that materially affect design, scope, behavior, compatibility, performance, error handling, or integration.
- If a question is not blocking, state an assumption and proceed.
- Ground decisions in source. After exploration agents return files, read those files.
- Do not create artificial approval gates. If the user requested implementation and blockers are resolved, implement.
- Implementation must be done by one dedicated implementation subagent.
- The implementation subagent must use the `tdd` skill with explicit red-green-refactor.
- After any implementation, always run `code-simplifier` and independent `code-reviewer` review.
- Implementation, simplification, fixing, and review must be done by separate agents. Reviewers must not fix their own findings, and fixing agents must not perform final review of their own changes.
- The main agent orchestrates, inspects results, updates todos, and avoids direct feature-code edits except trivial mechanical fixes.

## Tracks

### Light

Use for bounded medium changes where risk is mostly local context.

- Explore directly or launch 1 targeted `code-explorer`.
- Ask only blocking questions.
- Recommend one approach and implement once context is sufficient.

### Standard

Use for multi-file work with ambiguity or a non-trivial design choice.

- Launch 2 parallel `code-explorer` agents.
- Ask targeted questions after exploration.
- Recommend a path with key trade-offs; implement after blockers are resolved.

### Deep

Use for large, risky, cross-cutting, or highly ambiguous work.

- Launch 2–3 parallel `code-explorer` agents with distinct focuses.
- Organize blocking questions.
- Present multiple approaches only when trade-offs are meaningful.
- Confirm direction only for real product or architecture forks; otherwise proceed.

## Response Shape

Use only sections relevant to the current stage:

1. `Understanding` — interpretation and chosen track
2. `Relevant Findings` — source-grounded files, patterns, and constraints
3. `Open Questions` — only outcome-changing questions
4. `Recommendation` — proposed path and rationale
5. `Implementation Map` — files, sequence, and validation
6. `Status` — progress, blockers, or completion state

## Workflow

### Phase 0: Startup

1. Invoke `subagent-model-router` if available; otherwise choose subagent types directly from this skill.

### Phase 1: Discovery

Goal: understand what should be built.

1. Create a todo list scaled to the work.
2. Choose `Light`, `Standard`, or `Deep` based on scope, ambiguity, and risk.
3. If unclear, ask for the problem being solved, expected behavior, and constraints.
4. Summarize understanding. Seek confirmation only when uncertainty is meaningful.

### Phase 2: Codebase Exploration

Goal: understand architecture, patterns, flows, tests, data, integrations, and extension points.

1. Scale exploration and invoke the `explore` skill:
   - `Light`: direct exploration or 1 `code-explorer`
   - `Standard`: 2 parallel `code-explorer` agents
   - `Deep`: 2–3 parallel `code-explorer` agents
2. Give each agent a distinct focus, such as similar features, architecture, UX, tests, data flow, integrations, or extension points.
3. Require each agent to trace relevant code and return 5–10 key files to read.
4. Read the returned files.
5. Report only findings that affect design, questions, or implementation.

If explaining why exploration cannot be skipped, tie each gap to a downstream failure:

- Missing conventions cause Phase 5 rework.
- Missing integration points cause Phase 4 design errors.
- Unknown architecture patterns cause Phase 5 implementation gaps.

### Phase 3: Clarifying Questions

Goal: resolve design-changing ambiguity.

- Prefer 3 or fewer concrete questions.
- Tie each question to the decision it affects.
- Do not list generic concern categories.
- If no blockers remain, state assumptions and proceed.
- If the user says “whatever you think is best,” recommend a direction and request explicit confirmation only for real product or architecture forks.

### Phase 4: Architecture Design

Goal: choose an implementation approach.

1. Scale design:
   - `Light`: one concrete approach with brief rationale
   - `Standard`: compare 1–2 approaches only if there is a real decision
   - `Deep`: launch 2–3 parallel `code-architect` agents, such as minimal change, clean architecture, and pragmatic balance
2. Recommend the best path and explain why.
3. Ask the user to choose only for meaningful product or architecture forks; otherwise proceed.

### Phase 5: Implementation

Goal: build the feature through one dedicated implementation subagent.

1. Read all relevant files identified earlier.
2. Prepare a concise implementation brief containing:
   - goal and non-goals
   - chosen design and assumptions
   - files and patterns to follow
   - ordered implementation steps
   - validation commands or expected tests
   - required `tdd` red-green-refactor loop
3. Launch one dedicated implementation subagent. Prefer `code-implementer` if available; otherwise use the most appropriate coding/general subagent and assign only implementation work.
4. Require the implementation subagent to:
   - use the `tdd` skill with explicit red-green-refactor
   - follow codebase conventions strictly
   - write clean, maintainable code
   - report changed files, tests added or updated, validation run, and remaining risks
5. Do not use the implementation subagent as a reviewer.

If stopping before implementation, summarize findings, assumptions, remaining decisions, and next implementation steps. State that execution still requires:

- dedicated-subagent TDD implementation
- `code-simplifier` refactor pass
- independent `code-reviewer` review

### Phase 6: Quality Review

Goal: ensure correctness, simplicity, readability, maintainability, and minimal duplication.

1. Read the implementation summary and inspect important changed files.
2. Launch independent `code-simplifier` agents to simplify/refactor after implementation:
   - Up to 5 changed files: 1 agent covers all changed files.
   - More than 5 changed files: partition files into non-overlapping groups by module, directory, or logical area; each file appears in exactly one scope.
3. Launch independent `code-reviewer` agents:
   - `Light`: at least 1 reviewer.
   - `Standard`/`Deep`: multiple parallel reviewers with distinct focuses such as correctness, simplicity, conventions, tests, or edge cases.
4. Consolidate findings.
5. Route substantive fixes to a new dedicated fixing subagent. Reviewers must not fix their own findings, and fixing agents must not perform final review of their own changes.
6. Surface remaining risks and follow-up work.

### Phase 7: Summary

Goal: document completion.

1. Mark todos complete.
2. Summarize:
   - what was built
   - key decisions
   - files modified
   - validation performed
   - review and refactor results
   - remaining risks or next steps
