---
name: saga
description: Run an autonomous, spec-driven development saga for a medium-to-large feature using an orchestrator and worker subagents. Use when the user invokes /saga, asks to autonomously build a sizable feature end-to-end, wants a comprehensive milestone and task spec before parallel implementation, or asks to continue or resume a saga under the target repository's brain/sagas directory.
compatibility: Requires subagent dispatch. Local repository tasks require git worktrees. Use the host's user-input mechanism when available, or ask directly in conversation.
---

# Saga

Saga is an autonomous, spec-driven development workflow for **medium-to-large features** that should be implemented mostly without human intervention, except at a few discrete touch points. You act as the **orchestrator**: you turn a rough prompt into an airtight spec, then delegate implementation to a fleet of **worker subagents** while keeping your own context window clean.

The whole method rests on one bet: if the spec defines every task with validation criteria tight enough to form a *contract*, then workers can execute in parallel and self-verify, and the saga succeeds with almost no human babysitting. The quality of the saga is therefore decided in Phase 1, before a single line is written.

## Core principles

- **Airtight contracts over good intentions.** A task is only ready to delegate when its validation criteria are so explicit that meeting them leaves little-to-no possibility the task was done wrong. Ambiguity is the enemy; resolve it during planning, not during implementation.
- **No whitespace.** During planning, make every requirement explicit. Do not leave decisions to a worker's discretion unless the user has explicitly granted that discretion. Workers should never have to guess what "done" means.
- **Protect the orchestrator's context.** You are the long-lived coordinator. Push heavy reading, research, and implementation onto workers; receive compact reports back. Keep state on disk (in the saga directory's spec tree and `PROGRESS.md`) so your understanding survives compaction and you can re-read rather than re-hold. This maximizes time-to-compaction and keeps you coherent across the whole run.
- **Validation is first-class.** Every task and the saga as a whole carries verification criteria defined *up front*, and a concrete method for checking them (computer use, interactive CLI, or tests). See `references/validation-strategies.md`.
- **A few human touch points, not zero.** The human approves the spec (end of Phase 1), is consulted only when the spec genuinely cannot resolve a blocker (Phase 2), and does the final manual acceptance (Phase 3).

## The saga directory

Resolve the target project root independently of the current working directory and skill install location: use the project path and local project guidance supplied by the user; otherwise, from the target project, use `git rev-parse --show-toplevel`. Ask only if the target root remains genuinely ambiguous. Store each saga under `<repo-root>/brain/sagas/` so it survives across orchestrator sessions and can be resumed by a fresh agent. Create `brain/sagas/<feature-slug>-<timestamp>/` and record the resolved path as the saga's stable identity.

The directory holds a *tree* of spec files plus a progress log. Each level carries its own validation criteria, so detail scales with the size of the saga instead of bloating one file:

```
<repo-root>/brain/sagas/<saga-name>/
├── SAGA.md                      # overview, environment, saga-level exit criteria, milestone index
├── PROGRESS.md                  # live, continuously-updated execution log and current state
└── milestones/
    ├── 01-<slug>/
    │   ├── MILESTONE.md          # milestone spec + milestone-level validation criteria
    │   └── tasks/
    │       ├── 01-<slug>.md      # task spec + task-level validation criteria
    │       └── 02-<slug>.md
    └── 02-<slug>/
        ├── MILESTONE.md
        └── tasks/ ...
```

`SAGA.md` stays small. It indexes the milestones and holds only saga-wide content. Milestone and task specs hold the detail. This is what keeps your context clean: read only the spec for the milestone or task you are currently coordinating, and rely on `PROGRESS.md` for state rather than re-deriving it.

Use the templates and field definitions in `references/saga-spec-template.md` verbatim. Read it before drafting specs.

---

## Phase 1 - Planning & spec generation (orchestrator + user)

Goal: produce a comprehensive, unambiguous saga spec tree. This phase is **fully collaborative** with the user. It ends only when the user approves the spec.

When asking the user anything in this phase, use the host's structured user-input tool and **always use concrete options** (single- or multi-select) rather than open-ended questions. Provide your recommendation when there is a sensible default. Open-ended prose questions slow the user down and invite vague answers; options force crisp decisions.

### 1. Intake and frame

Restate the request as a one-paragraph problem statement and the rough shape of the feature. Identify the major unknowns you will need to close. Pick a unique saga directory under `<repo-root>/brain/sagas/` (feature slug + timestamp). Tell the user the path and create it; everything below is written there.

### 2. Establish machine & runtime capabilities

You cannot define realistic validation criteria without knowing what can actually be tested on this machine and against this program. Determine, by inspecting the repo and environment first and asking the user only for what you cannot discover:

- **What kind of program is this?** Web app, native GUI, TUI, CLI/library, backend service, etc. This dictates the validation method (see `references/validation-strategies.md`).
- **Is computer use available?** Check whether a computer-use / browser-automation capability is available to you or to cloud workers. If GUI/web validation is needed but computer use is only available remotely, plan to route that validation through remote workers.
- **What is the test/build toolchain?** Discover the test runner, build, lint, and typecheck commands (e.g. from README, CI config, package manifests, project rules). Confirm they run.
- **How is the program run/launched** for manual or interactive verification?

Record these findings in `SAGA.md` under the environment section. Workers and future orchestrators rely on them.

### 3. Close every gap of ambiguity

Iterate with the user using the host's structured input tool with concrete options when available, or concise direct questions otherwise. Provide your recommendation for each question. Close gaps in behavior, scope boundaries, edge cases, data shapes, error handling, non-goals, and acceptance bar. Batch related questions (no more than four at a time). Stop only when the remaining decisions are resolved or the user explicitly delegates them to your discretion.

### 4. Define the saga exit criteria

Before decomposing, write the saga-level **exit criteria**: the concrete, checkable conditions that mean the entire feature is done and correct. These are the contract for the whole saga and the basis for Phase 3.

### 5. Decompose into milestones and tasks

Break the work into **milestones** (coherent, independently meaningful chunks, ordered by dependency) and within each, **tasks** scoped so a *single novice worker agent* can complete one in one focused effort. For each task specify: scope, owned files/surfaces, dependencies on other tasks, and **validation criteria + validation method**. Shape the topology pragmatically around the feature's real dependencies. Maximize tasks that can run in parallel within a milestone, and sequence milestones where later work depends on earlier work.

Write this out as the spec tree in the saga directory: the milestone index and saga exit criteria in `SAGA.md`, each milestone's detail and milestone-level validation criteria in its `MILESTONE.md`, and each task's detail and validation criteria in its own task spec file. Each task's validation criteria must be airtight per `references/validation-strategies.md`. If you cannot write airtight criteria for a task, the task is under-specified. Split it or return to the user.

### 6. Get approval

Present the saga spec by walking the user through `SAGA.md` and the milestone/task specs. Ask them to approve or request changes using the host's user-input mechanism, or directly in conversation when no such tool is available. **Do not begin Phase 2 until the user approves.** This is the primary human checkpoint.

---

## Phase 2 - Implementation & validation (worker fleet, looped)

Goal: execute every task to its validation criteria, milestone by milestone, delegating to workers and keeping yourself lean. The user is involved here only if a blocker cannot be resolved from the spec.

### Orchestration mechanics

- **Delegate, don't implement.** Before dispatching workers, activate the `delegate-to-subagents` skill and follow its dispatch loop. Route each assignment with the exact model and reasoning effort it selects, define ownership and acceptance criteria, and enforce the assignment deadline and checkpoint flow it requires. You coordinate; you do not write feature code yourself. This protects your context.
- **Batch by parallelism.** Within a milestone, dispatch independent tasks together using the activated `delegate-to-subagents` workflow. Run dependent milestones in sequence. Use the task dependencies to determine the parallel groups.
- **Isolate local workers.** When workers modify the same repo, give each its own git worktree and branch. Follow the **saga branch naming convention** so every branch is traceable back to its saga directory, milestone, and task without consulting `PROGRESS.md`:
  ```
  saga/<saga-name>/m<M>t<T>-<task-slug>
  ```
  Example: `saga/dark-mode-20260609-0028/m1t2-setup-tokens`. Create with:
  ```
  git worktree add ../saga-<saga-name>-m<M>t<T> -b saga/<saga-name>/m<M>t<T>-<task-slug> <base>
  ```
  If your team or repo has a branch-prefix convention (e.g. a per-user prefix like `<username>/`, or a required prefix enforced by CI), prepend it consistently while keeping the `saga/<saga-name>/...` structure intact so branches stay filterable. Workers must never share a checkout or work on the user's current branch. Decide the merge strategy up front (typically: integrate each milestone's branches at the milestone boundary). Worker changes must be committed, pushed, or otherwise durably handed off before any worktree is removed.

  To list all branches for a saga: `git branch --list '*saga/<saga-name>/*'`
- **Remote workers for computer use.** If a task's validation needs computer use and it is only available remotely, launch that worker (or its validation step) remotely with computer use enabled, and have it return a durable artifact (pushed branch, draft PR, or a compact patch/diff) rather than leaving work only in the remote environment.

### The per-task contract given to each worker

Put shared rules in the dispatcher's shared prompt (repo path, base branch, toolchain commands, coding standards, validation method, and reporting format) and the specific task in each worker prompt. Instruct every worker to:

1. Implement only its assigned task and owned files.
2. Before editing source code, activate the `tdd` skill and follow its red-green-refactor workflow. **Self-validate in a loop** against the task's validation criteria using the prescribed method (computer use / interactive CLI / unit and integration tests). Iterate fix→validate until all criteria pass or it is genuinely blocked.
3. **Create a durable handoff before cleanup.** For local git worktree tasks, commit the validated changes to the task branch and make sure the branch is visible to the orchestrator. For remote tasks, push the branch, open a draft PR, or return a complete patch/diff; do not leave the only copy of the work in a remote checkout. If blocked with partial useful work, preserve it as a WIP commit or patch before reporting; if no partial work is worth preserving, say so explicitly.
4. **Remove the worktree only after the durable handoff exists**: `git worktree remove <worktree-path> --force`. The branch or patch persists; the worktree does not. Stale worktrees are unacceptable, but cleanup must never be allowed to discard the only copy of validated or useful partial work.
5. Report back compactly: branch name, commit hash or patch/pushed-branch artifact, changed files, validation evidence (test output, screenshots, CLI transcript), and a clear pass/blocked status. Keep findings terse to protect context.

See `references/validation-strategies.md` for choosing and applying the validation method and for what counts as sufficient evidence.

### The orchestration loop

For each milestone, in order:

1. Dispatch the milestone's parallelizable tasks as workers using the activated `delegate-to-subagents` workflow. Immediately record each worker's addressable agent/run ID in `PROGRESS.md` alongside its task, branch, and worktree. Display names are not sufficient for resume; a fresh orchestrator needs the run ID to message an in-progress worker.
2. Collect reports as they arrive (read the worker's message content; don't rely on lifecycle success alone). Update `PROGRESS.md` in the saga directory with per-task status and evidence pointers.
3. **Handle blocked tasks.** If a worker can't meet its criteria, decide: re-scope and re-delegate to the same worker (it retains context), adjust the task in its task spec file, or, only if the blocker is a genuine spec gap or external decision, escalate to the user with options. Prefer not to escalate; the spec should usually have the answer.
4. **Integrate and run milestone-level validation.** Merge the milestone's branches into the integration branch, resolve conflicts, and verify the milestone holds together (run the relevant tests/validation across the integrated result). If any worker left a worktree behind despite instructions, remove it now (`git worktree remove <path> --force`) before proceeding.
5. Move to the next milestone.

Re-read the relevant spec files and `PROGRESS.md` from disk whenever you need state instead of holding it in context. Keep `PROGRESS.md` updated as you go. It is the source of truth. A fresh orchestrator uses it to resume the saga, so a stale log means a lost saga. If you sense your context filling, write a concise progress checkpoint to `PROGRESS.md` first.

---

## Phase 3 - Final validation (orchestrator + user)

Goal: confirm the saga's exit criteria are met, then hand off to the user for manual acceptance.

1. Run the full saga-level exit criteria using the strongest available method (computer use for GUI/web, interactive CLI for TUIs, the full test/integration suite otherwise). Summarize the evidence against each exit criterion.
2. Present the user a concise completion report: what was built, how each exit criterion was validated, and exact steps for them to manually verify (how to run/launch, what to look for).
3. **Loop in the user for manual acceptance** using the host's structured input tool when available, or directly in conversation otherwise: accept, or report specific issues. If they report issues, capture them as new tasks, run a focused Phase 2 mini-loop (delegate → self-validate → integrate), and re-present. Repeat until the user accepts.

Only consider the saga complete when the user confirms acceptance.

---

## Resuming a saga

Because the saga directory and `PROGRESS.md` live in the target repository and capture full state, a saga can be picked up by a fresh orchestrator at any time (after compaction, a new session, or a handoff). When asked to continue, resume, or pick up a saga, **read `references/continuing-a-saga.md` and follow it.**

## Practical notes

- Never commit or open PRs unless the user asks; follow the repo's version-control rules when you do.
- Keep the spec tree current. If implementation forces a change to scope or criteria, update the relevant spec file rather than letting it drift.
- For very large sagas (≈10+ concurrent workers), prefer remote execution so you don't exhaust the user's machine.
- Don't expose internal worker agent IDs in user-facing summaries unless asked.

## Reference files

- `references/saga-spec-template.md` - the saga directory layout and exact templates for `SAGA.md`, `MILESTONE.md`, task specs, and `PROGRESS.md`. Read before drafting specs.
- `references/validation-strategies.md` - how to choose a validation method, write airtight criteria, and gather sufficient evidence. Read during Phase 1 (criteria) and Phase 2 (execution).
- `references/continuing-a-saga.md` - how a fresh orchestrator picks up an existing saga directory and resumes safely. Read when asked to continue/resume a saga.
