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
1. Inspect the current change set:
   - Run `git status` and `git diff HEAD`.
2. If there is no meaningful diff, inspect recent work:
   - Run `git diff HEAD~5..HEAD`.
3. Build a shortlist of added or edited units: functions, classes, modules, handlers, tests, configs, or scripts.

## 3) Find Duplication
Spawn three `code-explorer` subagents to compare the shortlist across the codebase using patterns that fit the repository language mix:
1. Use fast textual search (`rg`) to find repeated:
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
   - shell snippets in scripts
   - test setup code

If no meaningful duplication is found, report that clearly and stop.

## 4) Classify Findings
Classify each finding before editing:
1. Exact duplicate: same behavior already exists elsewhere.
2. Near duplicate: same intent with minor variation.
3. Reimplementation: inline code duplicates an existing helper or utility.

Favor refactors that improve clarity and avoid over-abstraction.

## 5) Refactor Safely
Launch a subagent to apply fixes directly:
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

Instruct the subagent:
- Prefer existing project structure for shared code.
- Do not introduce a new top-level pattern if an equivalent one exists.
- Report:
  - what was deduplicated
  - what shared abstractions were introduced
  - what validations were run and their results
  - any deliberate non-changes and why

## 6) Validate and Report
1. Read the refactoring subagent's report and run the most relevant validation commands: tests, lint, type-check, build, or targeted checks.
2. If a validation command fails because of your changes, fix it.
3. Provide a concise summary:
   - what was deduplicated
   - what shared abstractions were introduced
   - what validations were run and their results
   - any deliberate non-changes and why