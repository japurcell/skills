---
type: Agent Instruction
description: Repo-wide workflow for docs, install refresh, documentation sync, and subagent checkpoints
---

# Repo Workflow

- Treat `.agents/instructions/` and `.agents/memory/` as canonical home for agent-facing repo guidance.
- Keep `README.md` aligned when install, validation, or hook behavior changes, and keep `AGENTS.md` aligned with the `.agents/` loading contract.
- Keep top-level docs short. Put durable rules in `.agents/instructions/` and durable repo facts in `.agents/memory/`.
- Put repository-local workflow skills under `.agents/skills/`; put publishable skills installed into user environments under `skills/`. Confirm which boundary a new skill belongs to before applying generic skill workspace or installation conventions.
- Put active research and planning artifacts under a focused `docs/<effort>/` subtree. Keep Wayfinder maps, tickets, research, and planning handoffs there, overriding the skill's scratchpad default. Reserve `.agents/scratchpad/` for transient, disposable working state.
- For Tool Guardian false-positive repair, follow the active [execution plan](../../docs/tool-guardian-tuning/ExecPlan.md), including its security and latency gates. The user owns real installation for this effort.
- When a user explicitly promotes a feature handoff into `docs/<effort>/`, keep it at `docs/<effort>/handoff.md` and limit it to current status, remaining work, and exact resume instructions.
- Keep the generated-provider-hooks architectural decision at `docs/adr/0004-generated-provider-hooks.md`.
- After changing repo source that is installed into home-directory targets, run `./scripts/install.sh` before checking live Copilot or Gemini behavior.
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.

## Subagent Checkpoints

- For comparable fact-gathering tasks, start with an explicit 20-minute runtime limit and require usable saved checkpoints every five minutes. Size assignments around complete, independently useful outputs.
- A missed checkpoint triggers a status check, not an interruption. Inspect progress, tools, and blockers; elapsed time or an unfinished report alone does not establish agent failure.
- At the declared runtime limit, check status before deciding whether to stop or record a justified extension. Keep the limit and enforcement mechanism explicit. Honor user stop requests and safety constraints.
