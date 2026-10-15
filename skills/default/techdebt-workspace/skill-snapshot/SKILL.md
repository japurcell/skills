---
name: techdebt
description: Find and kill duplicated code from the current session. Scans the entire codebase for duplication against what was just written, then refactors automatically.
disable-model-invocation: true
---

# /techdebt - Find and Kill Duplication

You are a ruthless deduplication agent. You do not suggest. You find duplication and you eliminate it.

## Step 1: Identify What Changed

Run `git diff HEAD` and `git status` to get the full picture of what was added or modified in this session.

Parse the diff to extract:

- New functions, components, hooks, constants, types, and utilities
- New inline logic patterns (string manipulation, fetch calls, validation, type guards, env checks, path handling)
- New API route handlers and middleware

If the diff is empty (everything is committed), run `git diff HEAD~5..HEAD` to cover recent session commits.

## Step 2: Parallel Duplication Scan

Spawn three sub-agents using the Task tool. Run them in parallel.

### Task 1: Component & Layout Duplication

Search for duplication in components and layouts:

- Glob for `**/*tsx`, `**/*.jsx` files
- For each new component from the diff, Grep the for components with similar names, similar prop debase natures, or similar JSX structure
- Check for copy-pasted layout components (`layout.tsx` files with near-identical structure)
- Check for duplicated page-level patterns (similar data fetching, similar error boundaries, similar loading states)
- Flag components that wrap the same underlying element with minor style/prop differences
- Check for duplicated `getServerSideProps` / `getStaticProps` / server action patterns across pages

## Step 3: Aggregate Findings

Collect results from all three tasks. For each finding, categorize as:

1. **Exact duplicate** - same logic exists elsewhere. Use the existing one. Delete the new one.
2. **Near duplicate** - similar logic with minor differences. Extract a shared version with parameters.
3. **Inline reimplementation** - hand-rolled logic that an existing utility already handles. Replace with the utility call.
   If no duplication is found, say so and stop. Do not invent problems.

## Step 4: Refactor

For each finding, apply the fix directly:

- **Exact duplicates**: Delete the new code, import the existing version, update all references.
- **Near duplicates**: Extract a shared function/component/ hook to the appropriate shared directory ('utils/', 'hooks/
  components/shared/,
  'lib/'). Update all call sites to
  use the shared version.
- **Inline reimplementations**: Replace inline coa
  with
  calls to the existing utility. Add imports.
  When extracting shared code:
- Place utilities in 'lib/' or 'utils/ (whichever the project uses)
- Place shared components in 'components/shared/ or
  'components/ui/ (whichever exists)
- Place shared hooks in 'hooks/"
- Do not create new directories if equivalent ones already
  exist

## Step 5: Verify

Run the project's test suite:
npm test
Run the linter:
npx next lint
If tests or lint fail, fix the issues. The codebase must be in a passing state when you're done.
