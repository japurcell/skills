---
type: Agent Instruction
description: Repo-wide workflow for top-level docs, install refresh, and documentation sync
---

# Repo Workflow

- Treat `.agents/instructions/` and `.agents/memory/` as canonical home for agent-facing repo guidance.
- Keep `README.md` aligned when install, validation, or hook behavior changes, and keep `AGENTS.md` aligned with the `.agents/` loading contract.
- Keep top-level docs short. Put durable rules in `.agents/instructions/` and durable repo facts in `.agents/memory/`.
- Put repository-local workflow skills under `.agents/skills/`; put publishable skills installed into user environments under `skills/`. Confirm which boundary a new skill belongs to before applying generic skill workspace or installation conventions.
- Put active research and planning artifacts that require version control under a focused `docs/<effort>/` subtree; keep transient, disposable working state under `.agents/scratchpad/` unless the user explicitly promotes it.
- For Tool Guardian work, follow the retained [execution plan](../../docs/tool-guardian-tuning/ExecPlan.md), including its security and latency gates. Use the [feature handoff](../../docs/tool-guardian-tuning/handoff.md) for current state, [repair logs](../../docs/tool-guardian-tuning/repair-logs/orchestration.md) for delegated evidence, and the [prior plan](../../docs/tool-guardian-tuning/history/2026-10-07-plan-before-reconciliation.md) and [prior handoff](../../docs/tool-guardian-tuning/history/2026-10-07-handoff-before-reconciliation.md) as historical evidence. The user owns real installation for this effort.
- When a user explicitly promotes a feature handoff into `docs/<effort>/`, keep it at `docs/<effort>/handoff.md` and limit it to current status, remaining work, and exact resume instructions.
- The planning/task skill effort uses the explicitly requested sibling paths [docs/exec-plan-tasks-improvements.md](../../docs/exec-plan-tasks-improvements.md) and [docs/handoff.md](../../docs/handoff.md). Preserve these destinations; dependency direction is defined in [skills instructions](skills.md#planning-and-task-execution).
- Keep the generated-provider-hooks architectural decision at `docs/adr/0004-generated-provider-hooks.md`.
- After changing repo source that is installed into home-directory targets, run `./scripts/install.sh` before checking live Copilot or Gemini behavior.
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.
- Treat a subagent runtime target as a required status-check point. If work exceeds the target, inspect its status and give an overrun warning; let the work continue. Do not interrupt ongoing work solely because the target elapsed.
