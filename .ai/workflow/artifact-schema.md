# Artifact schema

Durable artifacts must be stored in:

```text
.ai/artifacts/<work-id>/
  00-intake.md
  01-worktree.md
  02-exploration-summary.md
  03-research-findings.md
  04-clarifications.md
  05-plan.md
  06-task-graph.yaml
  08-code-review.md
  08-security-review.md
  08-tech-debt.md
  09-verification.md
```

## Recommended metadata block

Add this block at the top of each markdown artifact:

```yaml
---
work_id: <work-id>
phase: "00|01|..."
status: draft|in_progress|complete
depends_on: []
updated_at: <ISO-8601 UTC>
---
```

## Task graph schema (required fields)

`06-task-graph.yaml` should include:

- `work_id`
- `tasks[]` with:
  - `id`
  - `title`
  - `stage` (`red|green|refactor`)
  - `depends_on` (list of task IDs)
  - `parallelizable` (`true|false`)
  - `verification` (test/check command or note)
