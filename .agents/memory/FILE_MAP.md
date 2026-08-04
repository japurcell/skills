---
coverage: Top-level overview; per-layer directory detail lives in the instruction files
---

# File Map

This file is a **top-level map only**. For area detail and working rules, read the matching instruction file:

- repo docs and root workflow → `.agents/instructions/repo.md`
- hooks areas → `.agents/instructions/hooks.md`
- skills areas → `.agents/instructions/skills.md`
- custom agents → `.agents/instructions/agents.md`
- helper scripts → `.agents/instructions/scripts.md`

## Source Areas

| Path | Layer | Purpose |
| --- | --- | --- |
| `.copilot/` | hooks | Copilot CLI instructions plus installed hook source under `.copilot/hooks/`, Python operational entrypoints under `.copilot/hooks/scripts/` (startup, tool guard, RTK, secrets scanner, session-end, and retained lifecycle logging hooks), and shared hook helpers under `.copilot/hooks/scripts/helpers/`. |
| `.gemini/` | hooks | Gemini CLI instructions, settings, installed hook source under `.gemini/hooks/`, Python operational entrypoints under `.gemini/hooks/scripts/` (startup, passive logging, tool guard, secrets scanner, and session-end logger), and shared hook helpers under `.gemini/hooks/scripts/helpers/`. |
| `skills/` | skills | One directory per skill, centered on `SKILL.md`; may include scripts, references, assets, and evals. |
| `agents/` | agents | Standalone custom agent prompt files. |
| `scripts/` | scripts | Installers, importers, validation helpers, and shared shell utilities. |
| `references/` | references | Optional shared reference material shipped with installs. |

## Knowledge and top-level docs

| Path | Status | Purpose |
| --- | --- | --- |
| `.agents/instructions/` | canonical | Agent-facing workflow rules and area conventions. |
| `.agents/memory/` | canonical | Durable repo facts, file maps, testing routes, and known issues. |
| `README.md` | companion | Repo overview and install entry point. |
| `AGENTS.md` | companion | Quickstart, loading contract, and top-level links for agents. |

## Key files

| Path | Why it matters |
| --- | --- |
| `scripts/install.sh` | Installs repo assets into `~/.agents`, `~/.copilot`, and `~/.gemini` targets. |
| `scripts/addy-install.sh` | Imports selected upstream addy skills, agents, and references into this repo. |
| `.copilot/hooks/rtk-rewrite.json` | RTK rewrite config used by hook-driven tool rewrite flows; points at `.copilot/hooks/scripts/rtk-hook-copilot.py`. |
| `.nvmrc` | Node version hint for local tooling. |
| `skills/skill-creator/scripts/quick_validate.py` | Narrow validation entry point for skill definitions. |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill directory into a distributable `.skill` archive. |
| `skills/agent-sop-author/validate-sop.sh` | Validates `.sop.md` files against expected Agent SOP structure. |
