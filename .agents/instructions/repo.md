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
- When a user explicitly promotes a feature handoff into `docs/<effort>/`, keep it at `docs/<effort>/handoff.md` and limit it to current status, remaining work, and exact resume instructions.
- Keep the generated-provider-hooks architectural decision at `docs/adr/0004-generated-provider-hooks.md`; use `docs/generated-provider-hooks/handoff.md` for the remaining deployed Gemini validation.
- After changing repo source that is installed into home-directory targets, run `./scripts/install.sh` before checking live Copilot or Gemini behavior.
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.
