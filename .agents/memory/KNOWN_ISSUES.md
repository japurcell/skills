---
type: Known Issue
description: Repo-wide / cross-cutting quirks and workarounds; layer-specific issues live in known-issues/<area>.md
---

# Known Issues

Repo-wide and cross-cutting issues only. Layer-specific gotchas live in dedicated per-layer files (load only the one for your area):

- general provider hooks → `.agents/memory/known-issues/hooks.md`
- source auto-ingest hooks → `.agents/memory/known-issues/hooks-auto-ingest.md`
- hook observability and trace storage → `.agents/memory/known-issues/hooks-observability.md`
- skills (`skills/`) → `.agents/memory/known-issues/skills.md`
- shell scripts (`scripts/*.sh`, `scripts/*.py`) → `.agents/memory/known-issues/scripts.md`
- PowerShell scripts (`scripts/*.ps1`) → `.agents/memory/known-issues/powershell.md`

## Blank lines with whitespace fail linting

**Affected area:** all
**Description:** Blank lines containing any space or tab fail lint/format; trailing whitespace also fails.
**Workaround:** Keep blank lines completely empty.
