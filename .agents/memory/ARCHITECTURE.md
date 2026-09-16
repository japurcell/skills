---
type: Agent Memory
description: Repo structure, install flows, and how top-level areas relate
---

# Architecture

## Top-level areas

| Path | Role | Main consumer |
| --- | --- | --- |
| `skills/` | Source of reusable task skills built around `SKILL.md` entry points. | Installed to `~/.agents/skills` by `scripts/install.sh` (PowerShell: `scripts/install.ps1`) |
| `agents/` | Source of custom agent definitions. | Installed to both `~/.copilot/agents` and `~/.gemini/agents` |
| `references/` | Optional shared reference material shipped with this repo. | Installed to `~/.agents/references` when that target exists |
| `.github/` | Repository-level Copilot config, including repo-local hooks. | Loaded directly from the workspace by Copilot |
| `.copilot/` | Copilot-specific instructions and hooks. | Installed to `~/.copilot/` |
| `.gemini/` | Gemini-specific instructions and hooks. | Installed to `~/.gemini/` |
| `.codex/` | Inactive source template and script for the user-global Codex required-skills hook. | Installed to `~/.codex/hooks/` and merged into `~/.codex/hooks.json` |
| `scripts/` | Installers, importers, and targeted validation helpers. | Run from repo checkout |
| `.agents/` | Agent knowledge base with canonical agent-facing rules and durable repo facts. | Copilot/Gemini agents working in this repo |
| `docs/` | Version-controlled ADRs plus active research and effort plans that complement `.agents/` canonical guidance. | Repo readers and agents who need current project context or human decision history |
| `README.md`, `AGENTS.md` | Top-level human entry points that summarize the repo and point into `.agents/`. | Repo readers and agents |

## Main flows

### Source authoring flow

1. Edit source under `skills/`, `agents/`, `.github/`, `.copilot/`, `.gemini/`, `.codex/`, `references/`, or `scripts/`.
2. Run narrow validation for changed area from `.agents/memory/TESTING_STRATEGY.md` and any matching `testing/<area>.md` file.
3. If installed behavior matters, run `./scripts/install.sh` (or `pwsh scripts/install.ps1`) before live checks because Codex, Copilot, and Gemini read installed copies from home-directory targets, not repository source files.

### Addy import flow

`scripts/addy-install.sh` is upstream-ingestion path. It syncs `../addy-agent-skills`, copies selected upstream agents, skills, and top-level references into this repository, prefixes imported names with `addy-`, and refreshes `.addy-skills` with source skill names that were installed.

### Documentation flow

- `README.md` and `AGENTS.md` stay as short top-level entry points.
- Durable agent-facing rules and repo facts belong in `.agents/instructions/` and `.agents/memory/`.
- Active research and planning artifacts that need version history belong under a focused `docs/<effort>/` subtree; transient working state remains in `.agents/scratchpad/`. After an effort finishes, import unique durable agent knowledge into `.agents/`, remove completed research and planning artifacts unless historical retention was requested, and retain ADRs by default.
- Keep top-level summaries aligned with `.agents/` instead of maintaining parallel long-form copies.

## Boundaries

- Treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- Treat `skills/archive/` as historical reference, not primary authoring surface.
- Treat `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` as fixtures unless task explicitly targets them.
- `.agents/sources/` and most of `.agents/skills/` are not normal edit targets; repository-maintained documentation work stays in `.agents/instructions/` and `.agents/memory/`. Exception: `.agents/skills/ingest-source/SKILL.md` is the canonical repo-local auto-ingest recovery skill and is maintained with the pending-ingest hook flow.
