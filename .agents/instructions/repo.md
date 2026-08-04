---
coverage: Repo-wide workflow for top-level docs, install refresh, and documentation sync
---

# Repo Workflow

- Treat `.agents/instructions/` and `.agents/memory/` as canonical home for agent-facing repo guidance.
- Keep `README.md` and `AGENTS.md` aligned with `.agents/` summaries; do not let duplicate long-form guidance drift.
- Keep top-level docs short. Put durable rules in `.agents/instructions/` and durable repo facts in `.agents/memory/`.
- After changing repo source that is installed into home-directory targets, run `./scripts/install.sh` before checking live Copilot or Gemini behavior.
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- TDD applies to app code and shell scripts.
- Keep `README.md` in sync when install, validation, or hook behavior changes.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.
