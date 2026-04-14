# Code review protocol

This document covers coverage tracking and scope conflict resolution for the code review step. Subagent dispatch (code-simplifier and code-reviewer agents) is defined in the main SKILL.md.

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
