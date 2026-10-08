---
type: Agent Instruction
description: Repo-wide workflow for top-level docs, install refresh, and documentation sync
---

# Repo Workflow

- Treat `.agents/instructions/` and `.agents/memory/` as canonical home for agent-facing repo guidance under [knowledge admission](knowledge-base.md).
- Keep `README.md` aligned when install, validation, or hook behavior changes, and keep `AGENTS.md` aligned with the `.agents/` loading contract.
- Keep top-level docs short. Put established rules in `.agents/instructions/` and only admitted, evidence-backed facts in `.agents/memory/`.
- Put repository-local workflow skills under `.agents/skills/`; put publishable skills installed into user environments under `skills/`. Confirm which boundary a new skill belongs to before applying generic skill workspace or installation conventions.
- Put active research and planning artifacts that require version control under a focused `docs/<effort>/` subtree; keep transient, disposable working state under `.agents/scratchpad/` unless the user explicitly promotes it.
- Apply the OKF profile only to its canonical instruction/memory bundles. Ordinary research Markdown can link to source directories; validate those destinations as files or directories instead of imposing OKF's regular-file-only rule outside its scope.
- When a user explicitly promotes a feature handoff into `docs/<effort>/`, keep it at `docs/<effort>/handoff.md` and limit it to current status, remaining work, and exact resume instructions.
- For selected-asset installation and lifecycle work, follow [selected installer rules](agent-assets.md).
- Keep the generated-provider-hooks architectural decision at `docs/adr/0004-generated-provider-hooks.md`.
- Verify installed behavior in a disposable target through the affected selected-asset command or legacy fixture. Source edits do not refresh installed copies. A live personal refresh belongs only to an explicitly authorized user-install workflow; never run `./scripts/install.sh` against real home as an automatic validation step. For selected scopes and remaining native gates, follow [usage](../../docs/agent-asset-installer/usage.md) and [client validation](../../docs/agent-asset-installer/client-validation.md).
- Ignore `skills/*-workspace/**/outputs/` during normal edits and reviews.
- Ignore `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` unless task explicitly targets them.
- When using simplification or refactor help, state intentional path boundaries explicitly, such as `.gemini/` versus `.copilot/`.
- Treat a subagent runtime target as a required status-check point. If work exceeds the target, inspect its status and give an overrun warning; let the work continue. Do not interrupt ongoing work solely because an advisory target elapsed. Explicit user-imposed hard deadlines and stop conditions still govern.

## Documentation retention

After an effort finishes, retain unique agent knowledge only when it passes [knowledge admission](knowledge-base.md). Remove completed research and working plans unless historical retention was requested; retain ADRs by default. Current owner actions and unresolved acceptance remain in the active effort's documents. Keep retained decisions under `docs/adr/` instead of copying them into memory.
