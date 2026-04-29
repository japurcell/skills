## Verification blocker: shared command group failed for both issues

The shared verification command group for child issues #6101 and #6102 has failed. Both issues remain open.

### Shared verification command

The controller's verification plan covers both issues with one command:
- Command: `bundle exec rspec spec/requests/admin/export_spec.rb`
- Status: `/bin/sh: bundle: command not found`
- Covered issues: #6101 "CSV export filters", #6102 "CSV export download audit log"

### Why both issues are blocked

The skill rules state:

> "Do not close any child issue covered by a shared command group unless that shared group passes."

and

> "Do not replace framework-native verification with static analysis, source inspection, or generic 'looks correct' reasoning."

The suggested workaround — closing #6101 based on diff inspection while #6102 remains open — violates the shared command group contract. When multiple issues share one verification command, the command's success or failure blocks or unblocks all covered issues collectively. Diff inspection does not substitute for the required `bundle exec rspec` invocation.

### Current state

- Child issue #6101: **remains open** — shared command group failed
- Child issue #6102: **remains open** — shared command group failed
- Parent task-graph line for #6101: **remains `[ ]`** — no checkbox update
- Parent task-graph line for #6102: **remains `[ ]`** — no checkbox update
- Wave W4: **blocked** on missing `bundle` / `bundler` CLI

### Required resolution

To unblock W4:
1. Install or enable the `bundle` CLI in the current environment and rerun `bundle exec rspec spec/requests/admin/export_spec.rb`, or
2. Update both child issues' Verification sections to list an acceptable alternative if one exists and the human approves

### Landing status

- Local changes only; no commit, push, or PR actions performed in this run.

---

PRD execution status for #6000

Completed this run:
- none

Blocked / waiting:
1. #6101 CSV export filters - shared verification command failed; missing `bundle` CLI
2. #6102 CSV export download audit log - shared verification command failed; missing `bundle` CLI

Next ready work:
- W4: both issues blocked on missing CLI

Landing status:
- Local changes only; no commit, push, or PR actions performed in this run.

Notes:
- Shared verification commands block all covered issues until the command passes. Partial closure (one issue open, one closed) is not permitted.
- Diff inspection does not substitute for the required `bundle exec rspec` invocation.
- Parent PRD issue #6000 remains open pending resolution.