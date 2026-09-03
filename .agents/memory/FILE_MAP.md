---
coverage: Top-level overview; per-layer directory detail lives in the instruction files
---

# File Map

This file is a **top-level map only**. For area detail and working rules, read the matching instruction file:

- repo docs and root workflow → `.agents/instructions/repo.md`
- hooks areas → `.agents/instructions/hooks.md`
- skills areas → `.agents/instructions/skills.md`
- custom agents → `.agents/instructions/agents.md`
- shell helper scripts → `.agents/instructions/scripts.md`
- PowerShell installer/test scripts → `.agents/instructions/powershell.md`

## Source Areas

| Path | Layer | Purpose |
| --- | --- | --- |
| `.github/hooks/` | hooks | Repo-local Copilot hook config and auto-ingest wiring. |
| `.copilot/` | hooks | Copilot instructions and local hook runtime sources. |
| `.gemini/` | hooks | Gemini instructions and local hook runtime sources. |
| `skills/` | skills | One directory per skill, centered on `SKILL.md`; may include scripts, references, assets, and evals. |
| `agents/` | agents | Standalone custom agent prompt files. |
| `docs/adr/` | repo docs | Human-facing ADRs that complement `.agents/` canonical guidance. |
| `docs/research/` | repo docs | Human-facing research notes on tooling and conversions. |
| `docs/okf-kb-migration/` | repo docs | Version-controlled OKF migration research, Wayfinder map, handoff, decision tickets, and relocation record. |
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
| `scripts/install.ps1` | PowerShell 7 port of `scripts/install.sh`; same sources, destinations, exclusions, and installed layout (run with `pwsh scripts/install.ps1`). |
| `scripts/test-install.ps1` | Fixture-repo test for `scripts/install.ps1` (run with `pwsh -NoProfile -File scripts/test-install.ps1`). |
| `scripts/common.sh` | Shared shell helper for resolving repo root in small shell tests and utilities. |
| `scripts/addy-install.sh` | Imports selected upstream addy skills, agents, and references into this repo. |
| `.agents/memory/sources/source-ingest-manifest.json` | Shared source-summary state file for Copilot and Gemini auto-ingest hooks plus pending-ingest gating. |
| `.copilot/hooks/rtk-rewrite.json` | RTK rewrite config used by hook-driven tool rewrite flows; points at `.copilot/hooks/scripts/rtk-hook-copilot.py`. |
| `docs/adr/0001-auto-ingest-runtime-shape.md` | Records why source auto-ingest uses runtime-local hook code with one committed repo manifest. |
| `docs/adr/0002-pending-ingest-gate.md` | Records why the pending-ingest gate blocks normal work until summaries resolve. |
| `docs/adr/0003-sqlite-backed-hook-observability.md` | Records why hook observability uses SQLite as source of truth with NDJSON fallback. |
| `docs/okf-kb-migration/map.md` | Active Wayfinder map for the implementation-ready OKF agent-knowledge-base migration design. |
| `.nvmrc` | Node version hint for local tooling. |
| `skills/skill-creator/scripts/quick_validate.py` | Narrow validation entry point for skill definitions. |
| `skills/skill-creator/scripts/package_skill.py` | Packages a skill directory into a distributable `.skill` archive. |
| `.agents/skills/ingest-source/SKILL.md` | The canonical repo-local `/ingest-source` recovery skill used by the pending-ingest gate. |
