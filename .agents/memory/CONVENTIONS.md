---
type: Agent Memory
description: Repo-wide code style rules (layer-specific conventions live in the instruction files)
---

# Conventions

Authoritative formatting lives in `.editorconfig`; path-scoped rules live in `.agents/instructions/<area>.md`. This file holds only **repo-wide** conventions.

**Layer-specific conventions live in the path-scoped instruction files — read the one for your area:**

- repo docs and root workflow (`AGENTS.md`, `README.md`) → `.agents/instructions/repo.md`
- general provider hooks → `.agents/instructions/hooks.md`
- source auto-ingest hooks → `.agents/instructions/hooks-auto-ingest.md`
- hook observability and trace storage → `.agents/instructions/hooks-observability.md`
- skills (`skills/`) → `.agents/instructions/skills.md`
- custom agents (`agents/`) → `.agents/instructions/agents.md`
- shell helper scripts (`scripts/*.sh`, `scripts/*.py`) → `.agents/instructions/scripts.md`
- PowerShell installer/test scripts (`scripts/*.ps1`) → `.agents/instructions/powershell.md`

## Agent Workspace Boundaries

- **Out of bounds files:** Files under `.agents/sources/` and most of `.agents/skills/` are strictly out of bounds for automated agent documentation routines or standard modifications. Exception: `.agents/skills/ingest-source/SKILL.md` is the canonical repo-local auto-ingest recovery skill and may be edited when the pending-ingest hook workflow changes. Do not modify other `.agents/skills/` files unless explicitly instructed by the user.

## Code Style

From `.editorconfig`:

- Indentation: 2 spaces for XML/JSON/SH files. Never tabs.
- Line endings: LF for text files on every platform; `.bat` and `.cmd` remain CRLF.
- **Blank lines must contain no whitespace** (no spaces/tabs) — this is a hard lint failure.
- **No trailing whitespace.**
