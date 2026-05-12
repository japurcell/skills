---
name: techdebt
description: Find and remove duplicated or redundant code introduced in the current session across any language or framework. Use this whenever the user asks to reduce tech debt, deduplicate logic, consolidate repeated patterns, or clean up copy-pasted code after feature work.
disable-model-invocation: true
---

# /techdebt - Remove Duplication and Repetition

You are a focused deduplication agent. Prioritize real maintainability wins over cosmetic churn.

## Goal

Reduce technical debt by removing duplicated logic and consolidating repeated patterns while preserving behavior.

## Step 1: Detect Session Scope

1. Inspect the current change set first:

- Run `git status` and `git diff HEAD`.

2. If there is no meaningful diff, inspect recent work:

- Run `git diff HEAD~5..HEAD`.

3. Build a shortlist of newly added or edited units (functions, classes, modules, handlers, tests, configs, scripts).

## Step 2: Find Duplication Across the Codebase

Spawn three code-explorer subagents to search for duplication against the shortlist, using patterns appropriate to the repository language mix.

1. Use fast textual search (`rg`) to find repeated literals, conditionals, SQL snippets, HTTP request patterns, serialization/parsing logic, validation branches, and error handling blocks.
2. Compare nearby architecture patterns by file role, not framework name:
   - domain/service/repository layers
   - controllers/handlers/routes
   - UI components/views/templates
   - CLI commands/jobs/workers
   - tests and fixtures

3. Include non-source duplication when relevant:
   - duplicated config fragments
   - repeated shell snippets in scripts
   - repeated test setup code

If no meaningful duplication is found, report that clearly and stop.

## Step 3: Classify Findings

For each finding, classify it before editing:

1. Exact duplicate: same behavior already exists elsewhere.
2. Near duplicate: same intent with minor variation.
3. Reimplementation: inline code duplicates an established utility/helper.

Favor refactors that improve long-term clarity and avoid over-abstraction.

## Step 4: Refactor Safely

Apply fixes directly.

1. Exact duplicate:
   - Remove duplicate implementation.
   - Reuse the existing source of truth.
   - Update references/imports.

2. Near duplicate:
   - Extract a shared unit with clear parameters.
   - Keep naming and location consistent with project conventions.

3. Reimplementation:
   - Replace inline logic with existing helper/utility.
   - Keep behavior and edge-case handling identical.

When deciding location for shared code, prefer existing project structure. Do not introduce a new top-level pattern if an equivalent one already exists.

## Step 5: Validate and Report

1. Run the most relevant validation commands for this repository (tests, lint, type-check, build, or targeted checks).
2. If a validation command fails because of your changes, fix it.
3. Produce a concise summary:
   - what was deduplicated
   - what shared abstractions were introduced
   - what validations were run and their outcomes
   - any deliberate non-changes and why
