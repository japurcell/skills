---
name: techdebt
description: Find and safely remove duplicated or redundant code in current context or a provided scope, e.g. `scope:git diff main..HEAD`.
disable-model-invocation: true
---

# /techdebt

Remove duplicated code while preserving behavior. Prefer small, safe, validated changes over broad cleanup.

## 1. Route

Invoke `subagent-model-router`.

## 2. Scope

If candidates are already provided, use them and skip discovery.

Otherwise, use a fast-tier subagent to resolve scope:

1. If input contains `scope:...`, inspect that scope.
2. Else inspect `git status` and `git diff HEAD`.
3. If no meaningful changes are found, report that and stop.
   Do not broaden scope unless the user asks.

Build a shortlist of changed functions, classes, modules, tests, configs, scripts, handlers, or UI units.

## 3. Find duplication

Use `/explore` to spawn 1-3 `code-explorer` subagents scaled to scope size.

Search shortlist items against relevant nearby/codebase patterns for:

- exact duplicates
- near duplicates
- reimplemented helpers/utilities
- repeated validation, parsing, SQL, HTTP, error handling, config, shell, UI, or test setup logic

Classify each finding as:

- `exact`
- `near`
- `reimplementation`

If no meaningful duplication is found, report that and stop.

## 4. Prioritize

Process safe, in-scope candidates in this order:

1. same file/module
2. same layer/service area
3. same abstraction level across modules
4. broader architecture or UI/CSS only if explicitly requested

Prefer:

- exact duplicates over near duplicates
- existing helpers over new abstractions
- minimal behavior-preserving diffs
- backend/test refactors over cosmetic churn

Default to the top 1–3 safest candidates unless the user requested broader cleanup.

## 5. Refactor and validate

For each selected candidate:

1. Launch one refactoring subagent.
2. Refactoring subagent must:
   - make the smallest behavior-preserving change
   - reuse existing structure and conventions
   - avoid new top-level patterns if equivalent ones exist
   - use `tdd` only when tests must be added or changed
3. Launch one validation subagent.
4. Validation subagent runs relevant checks: tests, lint, type-check, build, or targeted commands.
5. If validation fails, fix and revalidate; otherwise revert that candidate.

Continue to the next safe candidate. Stop only when remaining candidates are unsafe, ambiguous, out of scope, or require a user choice.

Ask the user before changes involving:

- public API changes
- architectural choices
- visual/UI behavior risk
- broad convention or naming changes
- unrelated refactors

## 6. Report

Return a concise summary:

- scope used
- duplicates removed
- shared helpers/abstractions introduced
- validation commands and results
- candidates kept, fixed, reverted, skipped, or blocked
- recommended next dedupe targets, if any
