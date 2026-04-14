# Code review protocol

This document describes how to orchestrate the code review step. The goal is comprehensive coverage with no files slipping through the cracks.

## Building review scope

Materialize a deterministic, stable-sorted `review_scope_files` list from all uncommitted changed implementation files:

```bash
git status --porcelain
```

Include staged, unstaged, and untracked files. Exclude:

- Deleted files (shown with `D` status in `git status`)
- Every `.gitignore` file

List excluded files separately so there's a clear audit trail.

## Dispatching review subagents

Pass the exact `review_scope_files` list to every review subagent. Subagents must not recompute or narrow this scope — when each reviewer works from a different file list, gaps and overlaps creep in.

If a reviewer reports a different file list than what it was given, treat it as a **scope conflict**: reconcile missing files (in scope but not reviewed) and extra files (reviewed but not in scope) against the controller list. Keep the review status INCOMPLETE until the conflict is resolved or explicitly deferred.

### Code simplifier

Launch independent [code-simplifier](../../code-simplifier/SKILL.md) subagents to identify refactoring opportunities. Scale based on the number of changed files:

- **≤5 files**: 1 agent covering all files
- **>5 files**: partition into non-overlapping groups by module, directory, or logical area — each file appears in exactly one agent's scope to prevent conflicting writes

### Code reviewers

Launch 3 review agents in parallel using [agents/code-reviewer.agent.md](../agents/code-reviewer.agent.md), each focusing on a different lens:

1. **Simplicity & DRY** — duplication, unnecessary complexity, dead code
2. **Bugs & correctness** — logic errors, null handling, race conditions, security
3. **Conventions & abstractions** — project patterns, naming, architecture alignment

## Coverage tracking

Report review coverage using this template inside the `Code Review Findings` section:

```text
Review Scope Coverage
- Total Changed (Uncommitted) Files: <count>
- Total Reviewed Files: <count>
- Missing Files: <count>
- Missing File List: <paths or none>
- Excluded Files: <paths including .gitignore and deleted files, or none>
- Completion Gate: Missing Files > 0 => INCOMPLETE (requires explicit deferment/approval)
```

If `Missing Files > 0`, code review is INCOMPLETE until the gap is reviewed or the user explicitly defers it.

## Handling scope conflicts

When a reviewer reports a file list that differs from `review_scope_files`:

1. Label it explicitly as a **scope conflict** or **reviewer file-list mismatch**
2. Reconcile: identify missing files (in scope but not reviewed) and extra files (reviewed but not in scope)
3. Keep completion status INCOMPLETE until the conflict is resolved or explicitly deferred
