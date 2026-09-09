---
coverage: Repo-wide workflow for top-level docs, install refresh, and documentation sync
---

# Repo Workflow

- Treat `.agents/instructions/` and `.agents/memory/` as canonical home for agent-facing repo guidance.
- Keep `README.md` aligned when install, validation, or hook behavior changes, and keep `AGENTS.md` aligned with the `.agents/` loading contract.
- Keep top-level docs short. Put durable rules in `.agents/instructions/` and durable repo facts in `.agents/memory/`.
- Put long-lived research and planning artifacts that require version control under a focused `docs/<effort>/` subtree; keep transient, disposable working state under `.agents/scratchpad/` unless the user explicitly promotes it.
- In `docs/okf-kb-migration/`, keep current open and closed authoritative decision tickets directly under `tickets/`; move obsolete tickets to `tickets/obsolete/` and repair links when their paths change.
- After changing repo source that is installed into home-directory targets, run `./scripts/install.sh` before checking live Copilot or Gemini behavior.
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.
