---
coverage: Repo structure, install flows, and how top-level areas relate
---

# Architecture

## Top-level areas

| Path | Role | Main consumer |
| --- | --- | --- |
| `skills/` | Source of reusable task skills built around `SKILL.md` entry points. | Installed to `~/.agents/skills` by `scripts/install.sh` |
| `agents/` | Source of custom agent definitions. | Installed to both `~/.copilot/agents` and `~/.gemini/agents` |
| `references/` | Optional shared reference material shipped with this repo. | Installed to `~/.agents/references` when that target exists |
| `.copilot/` | Copilot-specific instructions and hooks. | Installed to `~/.copilot/` |
| `.gemini/` | Gemini-specific instructions and hooks. | Installed to `~/.gemini/` |
| `scripts/` | Installers, importers, and targeted validation helpers. | Run from repo checkout |
| `.agents/` | Agent knowledge base with canonical agent-facing rules and durable repo facts. | Copilot/Gemini agents working in this repo |
| `docs/` | Human-facing design notes and ADRs that complement `.agents/` canonical guidance. | Repo readers who need recorded decisions |
| `README.md`, `AGENTS.md` | Top-level human entry points that summarize the repo and point into `.agents/`. | Repo readers and agents |

## Main flows

### Source authoring flow

1. Edit source under `skills/`, `agents/`, `.copilot/`, `.gemini/`, `references/`, or `scripts/`.
2. Run narrow validation for changed area from `.agents/memory/TESTING_STRATEGY.md` and any matching `testing/<area>.md` file.
3. If installed behavior matters, run `./scripts/install.sh` before live checks because Copilot and Gemini read installed copies from home-directory targets, not repository source files.

### Addy import flow

`scripts/addy-install.sh` is upstream-ingestion path. It syncs `../addy-agent-skills`, copies selected upstream agents, skills, and top-level references into this repository, prefixes imported names with `addy-`, and refreshes `.addy-skills` with source skill names that were installed.

### Documentation flow

- `README.md` and `AGENTS.md` stay as short top-level entry points.
- Durable agent-facing rules and repo facts belong in `.agents/instructions/` and `.agents/memory/`.
- Keep top-level summaries aligned with `.agents/` instead of maintaining parallel long-form copies.

## Boundaries

- Treat `skills/*-workspace/**/outputs/` as generated benchmark artifacts, not maintained source.
- Treat `skills/archive/` as historical reference, not primary authoring surface.
- Treat `skills/**/evals/files/**/AGENTS.md` and `skills/*-workspace/**/sandbox/AGENTS.md` as fixtures unless task explicitly targets them.
- `.agents/skills/` and `.agents/sources/` are not normal edit targets; repository-maintained documentation work stays in `.agents/instructions/` and `.agents/memory/`.
