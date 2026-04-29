## Verification failure: required CLI unavailable

Child issue #5101 "Add tenant-scoped route guard" cannot proceed past verification.

**Missing tool:** `expo-router` CLI
- Required command: `pnpm exec expo-router verify`
- Error: `/bin/sh: expo-router: command not found`
- Status: Verification blocked

**Proposed workaround rejected:**
Manual code inspection + `pnpm exec tsc --noEmit` do not substitute for the required `pnpm exec expo-router verify` command. The skill rules are explicit:

> "Treat each listed verification step as the required command contract for that issue. If the issue says to use a framework or project CLI, run that CLI; do not silently swap in static analysis, code reading, lint-only checks, type-check-only checks, or some other weaker proxy just because the intended verification tool is missing or inconvenient."

### Current state

- Child issue #5101: **remains open** — verification incomplete
- Parent task-graph line for #5101: **remains `[ ]`** — no checkbox update
- Wave W2: **blocked** on this missing dependency

### Required resolution

To unblock W2, either:
1. Install or enable the `expo-router` CLI in the current environment and rerun verification, or
2. Update the child issue's Verification section to list an acceptable alternative if one exists

### Landing status

- Local changes only; no commit, push, or PR actions performed in this run.

---

PRD execution status for #5000

Completed this run:
- none

Blocked / waiting:
1. #5101 Add tenant-scoped route guard - missing `expo-router` CLI; required `pnpm exec expo-router verify` cannot run

Next ready work:
- W2: #5101 (blocked on missing CLI)

Landing status:
- Local changes only; no commit, push, or PR actions performed in this run.

Notes:
- The `pnpm exec tsc --noEmit` and code inspection proposals do not meet the required verification contract for #5101.
- Parent PRD issue #5000 remains open pending resolution of the verification blocker.