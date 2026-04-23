# AI Workflow Starter Kit

Repo-local, deterministic workflow files for coding-task execution across different AI agents and models.

## Quick start

```bash
# 1) Create isolated worktree + scaffold artifacts
./.ai/scripts/start-work.sh my-work-id

# 2) Fill artifacts in order (see workflow)
# .ai/artifacts/my-work-id/00-intake.md ... 09-verification.md

# 3) Validate required stop gates
python3 .ai/scripts/validate-artifacts.py --work-id my-work-id
```

## Layout

- `.ai/workflow/`: policy/specification (phases, gates, hierarchy, delegation)
- `.ai/templates/`: reusable artifact templates
- `.ai/scripts/`: execution helpers
- `.ai/artifacts/<work-id>/`: durable run artifacts

See `.ai/workflow/workflow.md` for the canonical phase order.
