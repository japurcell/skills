---
name: techdebt
description: Find and remove duplicated or redundant code introduced in the current session across any language or framework. Use this whenever the user asks to reduce tech debt, deduplicate logic, consolidate repeated patterns, or clean up copy-pasted code after feature work.
disable-model-invocation: true
---

# /techdebt - Remove Duplication and Repetition

You are a focused deduplication agent. Prioritize maintainability over cosmetic churn.

## Goal

Reduce technical debt by removing duplicated logic and repeated patterns while preserving behavior.

## 1) Setup

1. Invoke `subagent-model-router`.

## 2) Detect Session Scope

Using a fast-tier subagent:

1. Inspect the current changes:
   - Run `git status` and `git diff HEAD`.
2. If there is no meaningful diff, inspect recent work:
   - Run `git diff HEAD~5..HEAD`.
3. Build a shortlist of added or edited functions, classes, modules, handlers, tests, configs, or scripts.

## 3) Find Duplication

Spawn three `code-explorer` subagents to compare the shortlist across the codebase using patterns that fit the repository language mix:

1. Use fast search (`rg`) to find repeated:
   - literals
   - conditionals
   - SQL snippets
   - HTTP request patterns
   - parsing or serialization logic
   - validation branches
   - error-handling blocks
2. Compare by file role, not framework name:
   - domain, service, repository
   - controller, handler, route
   - UI component, view, template
   - CLI command, job, worker
   - test, fixture
3. Include non-source duplication when relevant:
   - config fragments
   - shell snippets
   - test setup code
4. If no meaningful duplication is found, report that clearly and stop.
5. If meaningful duplication is found, continue and apply at least one safe refactor unless every candidate is unsafe, ambiguous, or out of scope.

## 4) Classify and Prioritize Findings

Classify each finding before editing:

1. Exact duplicate: same behavior already exists elsewhere.
2. Near duplicate: same intent with minor variation.
3. Reimplementation: inline code duplicates an existing helper or utility.

Rank findings and apply safe refactors in this order:

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
- Do not bundle unrelated refactors from different scopes unless they share the same abstraction and validation path.
- Do not wait to solve all duplication in one pass.

## 5) Refactor Safely

Launch a subagent to apply fixes directly. It must edit code, not only propose changes.
Before changing code, the subagent must invoke the `tdd` skill and follow it while implementing the refactor.

Apply the highest-priority safe candidate first:

1. Exact duplicate:
   - Remove the duplicate implementation.
   - Reuse the existing source of truth.
   - Update references and imports.
2. Near duplicate:
   - Extract a shared unit with clear parameters.
   - Keep naming and location consistent with project conventions.
3. Reimplementation:
   - Replace inline logic with the existing helper or utility.
   - Preserve behavior and edge cases exactly.

Execution rules:

- Prefer existing project structure for shared code.
- Do not introduce a new top-level pattern if an equivalent one exists.
- Keep the diff minimal and focused.
- Do not ask the user to choose if a safe, local refactor can be applied directly.
- If the first candidate is blocked or fails validation, try the next safest candidate.
- If findings span very different scopes, stop after the first validated refactor and report the remaining candidates in priority order.
- Ask the user only if the next step requires an architectural choice, public API change, visual/UI behavior risk, or a broad project-wide convention change.

Require the subagent to report:

- what was deduplicated
- what shared abstractions were introduced
- what validations were run and their results
- any deliberate non-changes and why
- why the chosen refactor was the safest available

## 6) Validate and Report

1. Read the refactoring subagent report and run the most relevant validation commands: tests, lint, type-check, build, or targeted checks.
2. If validation fails because of your changes, fix it or revert that candidate and try the next safest one.
3. If meaningful duplication was found, do not return discovery only unless every candidate was unsafe, ambiguous, or out of scope. In that case, list each blocked candidate and why.
4. Provide a concise summary:
   - what was deduplicated
   - what shared abstractions were introduced
   - what validations were run and their results
   - any remaining duplication not changed and why
   - which candidate was chosen first and why
   - remaining duplication in recommended next order
