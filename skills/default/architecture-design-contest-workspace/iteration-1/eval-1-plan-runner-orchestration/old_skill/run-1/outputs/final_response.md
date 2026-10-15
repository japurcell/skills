# Plan-runner orchestration: architecture options

## Inferred answers to the important design questions

Because this benchmark run is non-interactive, I’m making these assumptions up front:

- A “saved plan” means the existing feature workspace under `.agents/scratchpad/<feature>/`, especially `plan.md` and `tasks.md`.
- Resume state has to survive agent/session interruption.
- The current skills (`create-plan`, `create-tasks`, `implement-plan`) must remain independently runnable.
- Review checkpoints should happen after Foundational, after each User Story phase, and once more at the final Polish step.
- State should live in repo-local/workspace-local artifacts, not an external service.
- The main failure to avoid is turning `implement-plan` into a god-skill.

## Option 1 — Thin wrapper + workspace ledger

This is the lowest-friction option, and the one that fits the repo’s current shape best.

Add a new top-level skill such as `run-plan` that wraps the existing chain instead of replacing it. It would own a small execution artifact in the feature workspace, track which phase is active, persist checkpoint outcomes, and call `implement-plan` one phase at a time. `tasks.md` checkboxes would stay as compatibility state, but richer progress would live beside them.

The key repo fit is cultural as much as technical: this codebase already passes work through files like `plan.md`, `tasks.md`, `handoff-plan.md`, and review protocol docs. A wrapper skill plus feature-local state artifact keeps that model intact.

Its main weakness is brittleness if it relies only on markdown parsing. The current `create-tasks` and `implement-plan` phase models already drift a bit, so a purely textual wrapper will eventually start carrying too much parsing glue.

## Option 2 — Shared execution kernel + normalized task graph

This is the cleanest long-term architecture.

Instead of making `implement-plan` own parsing, scheduling, resume, checkpointing, and review orchestration, introduce a shared execution kernel. `create-tasks` would emit a machine-readable task graph in addition to human-readable `tasks.md`. `implement-plan` would become a thin adapter over that graph and the persisted run state.

This directly fixes the current mismatch between the phase taxonomy implied by `create-tasks` and the one assumed inside `implement-plan`. It also makes checkpoint-aware review far more precise because review scope can be derived from verified nodes completed since the last checkpoint, rather than from the whole working tree.

The downside is cost. This is more platform work up front, and if you do too much of it at once you risk building infrastructure before the repo has proven it needs it.

## Option 3 — Append-only run journal

This option treats execution as an event stream. Every important action appends an immutable event, and current progress is derived by replaying those events.

Architecturally, this is the strongest for auditability, retries, and debugging. You get excellent postmortems, deterministic replay, and a very explicit model for checkpoint review and re-entry after interruptions.

But in this repo it is probably over-ceremonious as a first move. The existing workflow is artifact-first and prompt-driven, not runtime-engine-first. Event sourcing is powerful, but it tends to introduce a lot of schema, projection, and recovery machinery before it starts paying for itself.

## Option 4 — SQLite-backed runner

This option splits execution state out of markdown and into a local SQLite database, while still projecting readable artifacts into the feature workspace.

It is the most operationally solid option short of a full workflow service. It gives you clean task state transitions, retry history, checkpoint gating, and queryable review coverage without needing any external infrastructure.

The trade-off is conceptual weight. Once SQLite becomes the source of truth, `tasks.md` becomes a projection, and that introduces a second system that contributors have to understand. It can still be a good fit, but it is a bigger architectural step than this repo seems to need right now.

## Comparison

In this repo, the real problem is not “how do we execute tasks at all?” The existing pipeline already knows how to plan, taskify, execute, validate, and review. The missing pieces are narrower: durable progress state, a stable checkpoint contract, and review orchestration that happens at the right boundaries instead of only as a final catch-all.

That makes the wrapper and kernel families the strongest fits. The wrapper approach wins on local fit because it respects the repo’s artifact-first workflow and keeps the current skills independently useful. The kernel approach wins on architectural cleanliness because it solves the phase-model mismatch structurally instead of papering over it.

The journal design is the most rigorous if you expect long-lived, heavily interrupted, or compliance-sensitive runs. I just would not pay that complexity tax first in a repo that currently communicates state mostly through markdown artifacts and prompt contracts.

The SQLite design is the best if you know you want a durable runner with rich querying and multiple retries from day one. But as a first bet it feels heavier than necessary, and it risks shifting attention from workflow seams to framework-building.

## Where I’d place the bet

I’d bet on a **hybrid that leans strongly toward Option 1, but steals one crucial idea from Option 2**.

Concretely:

- Add a new `run-plan` skill as the orchestration shell.
- Keep existing skills independently runnable.
- Have `create-tasks` emit a tiny machine-readable `task-manifest.json` alongside `tasks.md`.
- Keep canonical run state in `.agents/scratchpad/<feature>/execution/state.json`, with a human-readable `status.md` next to it.
- Teach `implement-plan` only two narrow new hooks: `stop_after_phase` and explicit `review_scope_files`.
- Freeze review scope at checkpoints from tasks verified since the last approved checkpoint.
- Keep the final all-uncommitted-files review as a backstop, not the primary coordination mechanism.

That gives you real saved-progress execution without forcing a platform rewrite. It also leaves a clean upgrade path into Option 2 later if the runner becomes central enough to deserve a true shared execution kernel.

## Why this is the best fit for this repo

It matches the repo’s current operating style: explicit artifacts, narrow skill boundaries, and reusable review protocols. It avoids the monolith by putting orchestration in a new shell instead of bloating `implement-plan`. And it addresses the one structural issue that pure wrapper designs would otherwise trip over: the need for a small machine-readable manifest so phase boundaries and task dependencies are not inferred from markdown alone.

In other words: **use a wrapper for control flow, use a manifest for truth, and keep `implement-plan` focused on execution.**

## What I would not do first

I would not start with full event sourcing.

I would not make SQLite the first dependency unless you already know concurrent or long-lived runs are common.

And I would definitely not keep piling orchestration policy into `implement-plan`; that is exactly how this turns into the monolith you want to avoid.

## Concrete first slice

First, extend `create-tasks` to write `task-manifest.json` with stable phase IDs, task IDs, dependencies, and declared file scopes.

Second, add `run-plan` to initialize and resume `.agents/scratchpad/<feature>/execution/state.json` and `status.md`.

Third, add the two narrow contracts to `implement-plan`: stop after a named phase, and accept a frozen review scope.

Fourth, extend the review protocol so checkpoint reviews can exclude ambient unrelated working-tree files while still surfacing them.

That is enough to prove the architecture without committing to a heavyweight runtime.

## Reference anchors

- GitHub reusable workflows: https://docs.github.com/en/actions/sharing-automations/reusing-workflows
- Temporal workflow execution: https://docs.temporal.io/workflow-execution
- Python `graphlib.TopologicalSorter`: https://docs.python.org/3/library/graphlib.html
- Event sourcing pattern: https://martinfowler.com/eaaDev/EventSourcing.html
- SQLite “When To Use SQLite”: https://www.sqlite.org/whentouse.html
