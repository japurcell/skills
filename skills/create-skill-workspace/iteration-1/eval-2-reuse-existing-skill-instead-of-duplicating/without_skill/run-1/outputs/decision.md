# Decision

Reuse and refine **`create-plan`** instead of creating a new `plan-maker` skill.

`create-plan` already matches the requested workflow: it starts from a spec file, reads repository instructions, writes `plan.md` plus research/design artifacts, and hands off directly to `/create-tasks`. The brief explicitly says there is no new workflow or file layout requirement, so a brand-new `plan-maker` skill would duplicate existing behavior and make triggering more fragmented.

## Why `create-plan` is the right base

- It already consumes a `spec_file` and writes planning artifacts in the feature workspace.
- It already reads repo-specific planning constraints via AGENTS/instruction files.
- It already targets the exact downstream step the brief mentions: `/create-tasks`.

## What to refine

The request is mostly about **triggering** and **output specificity**, so the refinement is narrow:

1. Strengthen the description so the skill triggers on phrases like `plan.md`, `research notes`, `design artifacts`, and `task-breakdown-ready output`.
2. Tighten the instructions so `plan.md` must include explicit `Validation Strategy`, `Task Breakdown Readiness`, and `Open Questions & Risks` sections.
3. Extend the template so those sections are visible in the artifact instead of being implied.

## Revised files

- `create-plan/SKILL.md`
- `create-plan/references/plan-template.md`
