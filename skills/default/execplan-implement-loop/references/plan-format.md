# Canonical ExecPlan v1

Use UTF-8 Markdown with LF newlines and exactly one fenced block tagged `execplan-loop-v1`. The plan must be tracked at HEAD within its Git worktree before a new run. Every task and milestone begins open; completed runs require their journal and explicit resume. Static `--validate-only` does not need Git or Gemini and never executes commands.

The control object has exactly schema_version (integer 1), plan_id (stable identifier), tasks (ordered nonempty array), milestones (nonempty array), and final_task_id. Identifiers match `[A-Za-z][A-Za-z0-9_-]{0,63}`. Unknown fields, duplicate JSON keys/IDs, cycles, dangling dependencies, and ambiguous headings are errors.

Each task has id, milestone_id, kind (`implementation` or `verification`), depends_on (unique task IDs), verification (nonempty ordered command array), writable_paths, state, and evidence. writable_paths contains explicit repository-relative files or directory prefixes ending `/`; `.` and `.git` are prohibited. Traversal, backslashes, symlink escapes, and absolute paths are rejected. Verification nodes own any explicitly permitted repair within their own scope. A task's requirements and stopping boundary belong under its unique `#### Task ID: Title` heading, outside generated regions.

Each command has id, argv (nonempty string array), cwd (repository-relative directory, `.` allowed), timeout_seconds (positive finite number), expected_exit_code (0 through 255), and failure_policy (object mapping explicit other exit codes to `repair` or `blocked`). Commands execute directly, with EOF stdin and no implicit shell. A declared shell is a visible part of the authorized command. Unknown exits, missing executables, and permissions block. Use an adapter with distinct exit codes when assertion and infrastructure failures would otherwise be conflated. Command timeouts are verification failures and block without an inferred paid repair.

Each milestone has id, verification_task_id, state, and evidence. Its verification task must belong to that milestone and depend transitively on every implementation task in the milestone. The final verification task depends transitively on every other task. It reruns all milestone checks before its own commands. During that sweep, inherited check failures use the first command of the final task's failure_policy, and all repairs use the final task's writable_paths. This makes final repair authority explicit; an earlier node's policy cannot authorize new final repairs.

Use exactly one generated region for each name: `progress`, `discoveries`, `decisions`, `outcomes`, and `milestone-ID` for each milestone. Markers are standalone lines:

```text
<!-- execplan-loop:generated progress:start -->
- [ ] [M1] T1: Implement the task
<!-- execplan-loop:generated progress:end -->
```

Place progress under `## Progress`, discoveries under `## Surprises & Discoveries`, decisions under `## Decision Log`, and outcomes under `## Outcomes & Retrospective`. Milestones use unique headings `### Milestone ID: Title`. Their generated bodies contain exactly `Status: open` and `Acceptance: not met`, changing together to `Status: done` and `Acceptance: met`. Progress contains exactly one entry per task, tagged with its milestone and checked exactly when done. Generated regions contain metadata only; requirements and Markdown headings must remain outside them. Nested, duplicate, unmatched, malformed, and unknown markers are rejected.

The runner owns state/evidence and generated metadata. It preserves all other Markdown bytes. Its frozen hash includes canonical JSON without task/milestone state/evidence and Markdown with the entire raw control block replaced by a fixed sentinel and generated region contents removed. Both components are length-prefixed before hashing. Editing requirements, graph, commands, or scope blocks execution.

Evidence entries contain command_id, invocation_id, timestamp, exit_code, candidate_digest, and log_reference. Journal task phases are open, in_progress, verification_pending, commit_preparing, commit_pending, and done. Only verified committed evidence unlocks dependencies. Later edits invalidate earlier acceptance as proof of final content; the final sweep checks the final candidate again. Checks also run against the rendered completion plan before staging, so metadata-dependent failures block a commit.

See the bundled [complete example](../evals/fixtures/example.md) for a three-task graph with one milestone and final acceptance. Replace example Python executable paths and task requirements for the actual repository; do not run this demonstration as an implementation request.
