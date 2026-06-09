---
name: techdebt
description: Find and remove duplicated or redundant code introduced in the current session or a user-provided scope across any language or framework. Use this whenever the user asks to reduce tech debt, deduplicate logic, consolidate repeated patterns, clean up copy-pasted code after feature work, or provides a scope such as `scope:git diff main..HEAD`.
disable-model-invocation: true
---

# /techdebt - Remove Duplication and Repetition

Reduce technical debt by removing duplicated logic and repeated patterns while preserving behavior. Prioritize maintainability over cosmetic churn.

## 1) Setup

1. Invoke `subagent-model-router`.

## 2) Determine scope

Using a fast-tier subagent:

1. Check for a user-provided scope like `scope:git diff main..HEAD`.
2. If provided:
   - treat everything after `scope:` as the scope expression
   - inspect that scope
   - if it is invalid, empty, or yields no meaningful results, report that clearly and fall back to the default scope below
3. Otherwise inspect:
   - `git status`
   - `git diff HEAD`
4. If there is still no meaningful diff, inspect:
   - `git diff HEAD~5..HEAD`
5. Build a shortlist of added or edited functions, classes, modules, handlers, tests, configs, or scripts from the resolved scope.

## 3) Find duplication

Spawn three `code-explorer` subagents to compare the shortlist against the codebase using patterns appropriate to the repository language mix:

1. Search for repeated:
   - literals
   - conditionals
   - SQL snippets
   - HTTP request patterns
   - parsing or serialization logic
   - validation branches
   - error-handling blocks
   - config fragments
   - shell snippets
   - test setup code
2. Compare by file role rather than framework name:
   - domain, service, repository
   - controller, handler, route
   - UI component, view, template
   - CLI command, job, worker
   - test, fixture
3. If no meaningful duplication is found, report that clearly and stop.
4. Continue only with candidates that are meaningful and safe enough to attempt.

## 4) Classify and prioritize

Classify each finding as:

1. Exact duplicate: behavior already exists elsewhere.
2. Near duplicate: same intent with minor variation.
3. Reimplementation: inline code duplicates an existing helper or utility.

Prioritize in this order:

1. same file or module
2. same layer or service area
3. cross-module at the same abstraction level
4. cross-layer or architectural
5. UI/CSS or broad naming/location consolidation

Selection rules:

- Prefer exact duplicates over near duplicates.
- Prefer reusing an existing helper over creating a new one.
- Prefer the smallest behavior-preserving change with clear validation.
- Prefer backend or test refactors over UI/CSS consolidation unless the user asked for UI cleanup.
- Do not bundle unrelated refactors across different scopes.
- Do not wait to solve all duplication in one pass.

## 5) Refactor safely

Process candidates in priority order. For each candidate:

1. Launch one refactoring subagent to apply the change.
2. Before editing, that subagent must invoke the `tdd` skill and follow it during the refactor.
3. Launch a separate validation subagent to run relevant checks: tests, lint, type-check, build, interactive, or targeted checks.
4. Continue only if validation passes.
5. If validation fails, fix and revalidate, or revert before continuing.
6. Stop when:
   - all safe candidates are applied and validated, or
   - the next candidate requires an architectural choice, public API change, visual/UI behavior risk, or a broad convention change

Refactor by type:

1. Exact duplicate:
   - remove the duplicate implementation
   - reuse the existing source of truth
   - update references and imports
2. Near duplicate:
   - extract a shared unit with clear parameters
   - keep naming and location consistent with project conventions
3. Reimplementation:
   - replace inline logic with the existing helper or utility
   - preserve behavior and edge cases exactly

Execution rules:

- Prefer existing project structure for shared code.
- Do not introduce a new top-level pattern if an equivalent one exists.
- Keep each candidate diff minimal and focused.
- Do not ask the user to choose if a safe, local refactor can be applied directly.
- If findings span very different scopes, finish only the safe, local candidates.
- Ask the user only when the next candidate cannot be applied safely without a required choice or broader risk.

Require the refactoring subagent to report:

- what was deduplicated
- what shared abstractions were introduced
- any deliberate non-changes and why
- why the refactor was safe

Require the validation subagent to report:

- what commands were run
- which checks passed or failed
- whether the candidate was kept, fixed and kept, or reverted

## 6) Validate and report

1. Read the refactoring and validation reports for each candidate.
2. If meaningful duplication was found, do not return discovery only unless every candidate was unsafe, ambiguous, or out of scope. If so, list each blocked candidate and why.
3. Provide a concise summary:
   - resolved scope used
   - what was deduplicated
   - what shared abstractions were introduced
   - what validations were run and their results
   - any candidates that were reverted, skipped, or blocked and why
   - remaining duplication in recommended next order
