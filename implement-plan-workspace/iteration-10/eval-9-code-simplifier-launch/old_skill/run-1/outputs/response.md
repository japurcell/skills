# Code Review Findings

## Review Scope

Building the review scope from all uncommitted changed files via `git status --porcelain`:

```text
review_scope_files (stable-sorted):
1. src/payments/processor.ts
2. src/payments/types.ts
3. src/payments/validator.ts
4. tests/payments/processor.test.ts
```

**Excluded files:** none (no deleted files, no `.gitignore` files in changeset)

---

## Dispatching Review Subagents

All subagents receive the exact same `review_scope_files` list above. No subagent recomputes or narrows this scope.

### Code Simplifier — 1 agent

Since the changeset contains **4 files (≤ 5)**, a single code-simplifier subagent is launched covering all files.

| Agent | Files | Scope |
|-------|-------|-------|
| **code-simplifier-1** | `src/payments/processor.ts`, `src/payments/types.ts`, `src/payments/validator.ts`, `tests/payments/processor.test.ts` | All changed files — identify refactoring opportunities, unnecessary complexity, and duplication |

**Launch:** 1 `code-simplifier` subagent via the task tool (agent_type: `general-purpose`), prompted with:
- The full `review_scope_files` list
- Instruction to review all 4 files for simplification and refactoring opportunities per the [code-simplifier skill](../../code-simplifier/SKILL.md)

### Code Reviewers — 3 agents in parallel

Three `code-reviewer` subagents are launched in parallel, each using the [code-reviewer agent](../agents/code-reviewer.agent.md) definition and focusing on a different review lens. All three receive the identical `review_scope_files` list.

| Agent | Lens | Focus Areas |
|-------|------|-------------|
| **reviewer-1-simplicity** | Simplicity & DRY | Duplication across processor/validator/types, unnecessary complexity, dead code, opportunities to consolidate shared logic |
| **reviewer-2-correctness** | Bugs & Correctness | Logic errors in payment processing, null/undefined handling in validator, race conditions in async payment flows, security issues (input sanitization, injection, sensitive data exposure) |
| **reviewer-3-conventions** | Conventions & Abstractions | Project patterns and naming consistency, architecture alignment with the plan, type export conventions in types.ts, test structure and coverage patterns |

**Launch:** 3 `code-review` subagents via the task tool (agent_type: `code-review`), each prompted with:
- The full `review_scope_files` list (all 4 files)
- Their specific review lens and focus areas
- Instruction to use confidence scoring (only report issues with confidence ≥ 80)
- The code-reviewer agent instructions

All 4 subagents (1 code-simplifier + 3 code-reviewers) are launched **in parallel** since they are read-only reviewers with no write conflicts.

---

## Coverage Tracking

```text
Review Scope Coverage
- Total Changed (Uncommitted) Files: 4
- Total Reviewed Files: 4
- Missing Files: 0
- Missing File List: none
- Excluded Files: none
- Completion Gate: Missing Files = 0 => COMPLETE
```

Each of the 4 review subagents was given the identical 4-file scope. If any reviewer reports a file list differing from `review_scope_files`, it is flagged as a **scope conflict** and reconciled — missing files (in scope but not reviewed) and extra files (reviewed but not in scope) are identified, and the completion status is held at INCOMPLETE until resolved or explicitly deferred.

---

## Consolidated Findings

*Findings are consolidated here after all 4 subagents return. The highest-severity issues are called out first for immediate action.*

- **Code Simplifier (1 agent):** *(awaiting results — refactoring opportunities across all 4 files)*
- **Reviewer 1 — Simplicity & DRY:** *(awaiting results)*
- **Reviewer 2 — Bugs & Correctness:** *(awaiting results)*
- **Reviewer 3 — Conventions & Abstractions:** *(awaiting results)*

Once all agents complete, any issues with confidence ≥ 80 are surfaced here grouped by severity (Critical → Important), with file paths, line numbers, and concrete fix suggestions. Scope conflicts, if any, are reconciled against the controller's `review_scope_files` list before the review is marked COMPLETE.
